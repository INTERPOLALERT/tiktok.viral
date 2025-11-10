from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timedelta, date
from config import Config
from models import (
    db, User, Campaign, Contribution, Milestone, CampaignUpdate, Comment,
    Achievement, PriceHistory, BurnStats, generate_campaign_id,
    generate_transaction_hash, generate_wallet_address
)
import random
import json

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# Mock PLS price (in real app, would fetch from PulseX)
MOCK_PLS_PRICE = 0.00015  # $0.00015 USD per PLS


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_or_create_user(wallet_address):
    """Get or create user by wallet address"""
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        user = User(wallet_address=wallet_address)
        db.session.add(user)
        db.session.commit()
    return user


def get_current_pls_price():
    """Get current PLS price (mocked for demo)"""
    # In production, fetch from PulseX DEX
    return MOCK_PLS_PRICE


def calculate_burn(amount_pls):
    """Calculate 1% burn amount"""
    return amount_pls * Config.CONTRIBUTION_BURN_RATE


def update_burn_stats(contribution_burn=0.0, creation_burn=0.0):
    """Update daily burn statistics"""
    today = date.today()
    stats = BurnStats.query.filter_by(date=today).first()

    if not stats:
        # Get total burn to date
        previous_stats = BurnStats.query.order_by(BurnStats.date.desc()).first()
        total_to_date = previous_stats.total_burn_to_date if previous_stats else 0.0

        stats = BurnStats(
            date=today,
            daily_contribution_burn=0.0,
            daily_creation_burn=0.0,
            daily_total_burn=0.0,
            campaigns_created=0,
            contributions_made=0,
            total_burn_to_date=total_to_date
        )
        db.session.add(stats)

    stats.daily_contribution_burn += contribution_burn
    stats.daily_creation_burn += creation_burn
    stats.daily_total_burn += (contribution_burn + creation_burn)
    stats.total_burn_to_date += (contribution_burn + creation_burn)

    if contribution_burn > 0:
        stats.contributions_made += 1
    if creation_burn > 0:
        stats.campaigns_created += 1

    db.session.commit()


def check_and_award_achievements(user):
    """Check if user earned new achievements"""
    new_achievements = []

    # Burn achievements
    if user.total_burned >= Config.ACHIEVEMENTS['fire_starter']:
        if not Achievement.query.filter_by(user_id=user.id, achievement_type='fire_starter').first():
            ach = Achievement(
                user_id=user.id,
                achievement_type='fire_starter',
                achievement_name='Fire Starter',
                achievement_description='Burned 100 PLS total',
                badge_tier='bronze'
            )
            db.session.add(ach)
            new_achievements.append(ach)

    if user.total_burned >= Config.ACHIEVEMENTS['flame_fanatic']:
        if not Achievement.query.filter_by(user_id=user.id, achievement_type='flame_fanatic').first():
            ach = Achievement(
                user_id=user.id,
                achievement_type='flame_fanatic',
                achievement_name='Flame Fanatic',
                achievement_description='Burned 1,000 PLS total',
                badge_tier='silver'
            )
            db.session.add(ach)
            new_achievements.append(ach)

    if user.total_burned >= Config.ACHIEVEMENTS['inferno_king']:
        if not Achievement.query.filter_by(user_id=user.id, achievement_type='inferno_king').first():
            ach = Achievement(
                user_id=user.id,
                achievement_type='inferno_king',
                achievement_name='Inferno King',
                achievement_description='Burned 10,000 PLS total',
                badge_tier='gold'
            )
            db.session.add(ach)
            new_achievements.append(ach)

    # Contribution achievements
    if user.total_contributed >= 100:
        if not Achievement.query.filter_by(user_id=user.id, achievement_type='first_contribution').first():
            ach = Achievement(
                user_id=user.id,
                achievement_type='first_contribution',
                achievement_name='First Contribution',
                achievement_description='Made your first contribution',
                badge_tier='bronze'
            )
            db.session.add(ach)
            new_achievements.append(ach)

    if user.total_contributed >= 10000:
        if not Achievement.query.filter_by(user_id=user.id, achievement_type='big_spender').first():
            ach = Achievement(
                user_id=user.id,
                achievement_type='big_spender',
                achievement_name='Big Spender',
                achievement_description='Contributed 10,000+ PLS total',
                badge_tier='gold'
            )
            db.session.add(ach)
            new_achievements.append(ach)

    # Campaign support achievements
    if user.campaigns_supported >= 10:
        if not Achievement.query.filter_by(user_id=user.id, achievement_type='support_10').first():
            ach = Achievement(
                user_id=user.id,
                achievement_type='support_10',
                achievement_name='Community Champion',
                achievement_description='Supported 10 campaigns',
                badge_tier='silver'
            )
            db.session.add(ach)
            new_achievements.append(ach)

    db.session.commit()
    return new_achievements


def get_top_contributors(time_period='all_time', limit=100):
    """Get top contributors by ranking algorithm"""
    users = User.query.all()

    # Apply time filtering if needed
    if time_period != 'all_time':
        # For demo, return all users sorted by score
        # In production, filter contributions by time period
        pass

    # Calculate scores
    user_scores = []
    for user in users:
        if user.total_contributed > 0:
            score = user.calculate_rank_score()
            user_scores.append({
                'user': user,
                'score': score,
                'rank': 0  # Will be calculated after sorting
            })

    # Sort by score descending
    user_scores.sort(key=lambda x: x['score'], reverse=True)

    # Assign ranks
    for i, item in enumerate(user_scores, 1):
        item['rank'] = i

    return user_scores[:limit]


def calculate_campaign_velocity(campaign):
    """Calculate contribution velocity (PLS per hour)"""
    if campaign.total_raised_pls == 0:
        return 0.0

    time_elapsed = datetime.utcnow() - campaign.created_at
    hours_elapsed = max(time_elapsed.total_seconds() / 3600, 1)  # At least 1 hour

    velocity = campaign.total_raised_pls / hours_elapsed
    return velocity


# ============================================================================
# ROUTES - Home & Discovery
# ============================================================================

@app.route('/')
def index():
    """Homepage with viral discovery feed"""
    wallet_address = session.get('wallet_address')
    user = None
    if wallet_address:
        user = User.query.filter_by(wallet_address=wallet_address).first()

    # Get campaigns for different sections
    all_campaigns = Campaign.query.filter_by(is_active=True).all()

    # Update velocities
    for campaign in all_campaigns:
        campaign.contribution_velocity = calculate_campaign_velocity(campaign)

    db.session.commit()

    # Trending (by velocity)
    trending_campaigns = sorted(
        [c for c in all_campaigns if c.contribution_velocity > 0],
        key=lambda x: x.contribution_velocity,
        reverse=True
    )[:12]

    # New (by creation date)
    new_campaigns = sorted(
        all_campaigns,
        key=lambda x: x.created_at,
        reverse=True
    )[:12]

    # Ending Soon (by days remaining)
    ending_soon_campaigns = sorted(
        [c for c in all_campaigns if c.days_remaining() <= 7 and c.days_remaining() > 0],
        key=lambda x: x.days_remaining()
    )[:12]

    # Get global burn stats
    latest_burn_stats = BurnStats.query.order_by(BurnStats.date.desc()).first()
    total_burned = latest_burn_stats.total_burn_to_date if latest_burn_stats else 0.0

    # Get current PLS price
    pls_price = get_current_pls_price()

    return render_template(
        'index.html',
        user=user,
        trending_campaigns=trending_campaigns,
        new_campaigns=new_campaigns,
        ending_soon_campaigns=ending_soon_campaigns,
        total_burned=total_burned,
        pls_price=pls_price
    )


@app.route('/discover')
def discover():
    """Discovery page with filters"""
    wallet_address = session.get('wallet_address')
    user = None
    if wallet_address:
        user = User.query.filter_by(wallet_address=wallet_address).first()

    # Get filter parameters
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'trending')
    search_query = request.args.get('q', '')

    # Base query
    query = Campaign.query.filter_by(is_active=True)

    # Filter by category
    if category != 'all':
        query = query.filter_by(category=category)

    # Search
    if search_query:
        query = query.filter(Campaign.title.ilike(f'%{search_query}%'))

    campaigns = query.all()

    # Update velocities
    for campaign in campaigns:
        campaign.contribution_velocity = calculate_campaign_velocity(campaign)

    # Sort
    if sort_by == 'trending':
        campaigns.sort(key=lambda x: x.contribution_velocity, reverse=True)
    elif sort_by == 'new':
        campaigns.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == 'ending':
        campaigns.sort(key=lambda x: x.days_remaining())
    elif sort_by == 'popular':
        campaigns.sort(key=lambda x: x.supporter_count, reverse=True)

    pls_price = get_current_pls_price()

    return render_template(
        'discover.html',
        user=user,
        campaigns=campaigns,
        category=category,
        sort_by=sort_by,
        search_query=search_query,
        pls_price=pls_price
    )


# ============================================================================
# ROUTES - Wallet Connection
# ============================================================================

@app.route('/connect_wallet', methods=['POST'])
def connect_wallet():
    """Simulate wallet connection"""
    # In production, this would verify signature from MetaMask
    # For demo, generate or use provided address

    data = request.json
    wallet_address = data.get('wallet_address')

    if not wallet_address:
        # Generate demo wallet
        wallet_address = generate_wallet_address()

    # Create or get user
    user = get_or_create_user(wallet_address)

    # Store in session
    session['wallet_address'] = wallet_address

    return jsonify({
        'success': True,
        'wallet_address': wallet_address,
        'display_address': user.display_address()
    })


@app.route('/disconnect_wallet', methods=['POST'])
def disconnect_wallet():
    """Disconnect wallet"""
    session.pop('wallet_address', None)
    return jsonify({'success': True})


# ============================================================================
# ROUTES - Campaign Creation
# ============================================================================

@app.route('/create')
def create_campaign_page():
    """Campaign creation page"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        return redirect(url_for('index'))

    user = User.query.filter_by(wallet_address=wallet_address).first()
    pls_price = get_current_pls_price()

    return render_template('create_campaign.html', user=user, pls_price=pls_price, creation_fees=Config.CREATION_FEES)


@app.route('/api/create_campaign', methods=['POST'])
def create_campaign():
    """Create new campaign (30-second flow)"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        return jsonify({'success': False, 'error': 'Not connected'}), 401

    user = get_or_create_user(wallet_address)

    data = request.json

    # Extract campaign data
    title = data.get('title')
    category = data.get('category')
    description = data.get('description', '')
    goal_usd = float(data.get('goal_usd', 0))
    duration_days = int(data.get('duration_days', 30))
    beneficiary_address = data.get('beneficiary_address', wallet_address)
    num_milestones = int(data.get('num_milestones', 1))
    image_url = data.get('image_url', '')
    video_url = data.get('video_url', '')

    # Validate
    if not title or not category or goal_usd <= 0:
        return jsonify({'success': False, 'error': 'Invalid campaign data'}), 400

    # Calculate PLS amounts
    pls_price = get_current_pls_price()
    goal_pls = goal_usd / pls_price

    # Get creation fee
    creation_fee = Config.CREATION_FEES.get(category, 25)

    # Calculate creator deposit per stage
    deposit_per_stage = goal_pls / num_milestones
    total_creator_deposit = deposit_per_stage * num_milestones

    # Create campaign
    campaign_id = generate_campaign_id()
    ends_at = datetime.utcnow() + timedelta(days=duration_days)

    campaign = Campaign(
        campaign_id=campaign_id,
        creator_id=user.id,
        title=title,
        category=category,
        description=description,
        goal_usd=goal_usd,
        goal_pls=goal_pls,
        duration_days=duration_days,
        beneficiary_address=beneficiary_address,
        num_milestones=num_milestones,
        creator_deposit_per_stage=deposit_per_stage,
        total_creator_deposit=total_creator_deposit,
        ends_at=ends_at,
        creation_fee_burned=creation_fee,
        image_url=image_url,
        video_url=video_url
    )

    db.session.add(campaign)

    # Create milestones
    amount_per_milestone = goal_pls / num_milestones
    for i in range(num_milestones):
        milestone = Milestone(
            campaign_id=campaign.id,
            stage_number=i + 1,
            title=f'Milestone {i + 1}',
            description='',
            required_amount_pls=amount_per_milestone * (i + 1),
            creator_deposit_pls=deposit_per_stage
        )
        db.session.add(milestone)

    # Update user stats
    user.campaigns_created += 1

    # Update burn stats (creation fee burned)
    update_burn_stats(creation_burn=creation_fee)

    db.session.commit()

    return jsonify({
        'success': True,
        'campaign_id': campaign_id,
        'creation_fee_burned': creation_fee,
        'total_deposit_required': total_creator_deposit,
        'transaction_hash': generate_transaction_hash()
    })


# ============================================================================
# ROUTES - Campaign View
# ============================================================================

@app.route('/campaign/<campaign_id>')
def view_campaign(campaign_id):
    """View individual campaign"""
    wallet_address = session.get('wallet_address')
    user = None
    if wallet_address:
        user = User.query.filter_by(wallet_address=wallet_address).first()

    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    if not campaign:
        return "Campaign not found", 404

    # Get campaign data
    creator = User.query.get(campaign.creator_id)
    contributions = Contribution.query.filter_by(campaign_id=campaign.id).order_by(Contribution.created_at.desc()).limit(50).all()
    milestones = Milestone.query.filter_by(campaign_id=campaign.id).order_by(Milestone.stage_number).all()
    updates = CampaignUpdate.query.filter_by(campaign_id=campaign.id).order_by(CampaignUpdate.created_at.desc()).all()
    comments = Comment.query.filter_by(campaign_id=campaign.id).order_by(Comment.created_at.desc()).all()

    # Calculate velocity
    campaign.contribution_velocity = calculate_campaign_velocity(campaign)

    pls_price = get_current_pls_price()

    return render_template(
        'campaign.html',
        user=user,
        campaign=campaign,
        creator=creator,
        contributions=contributions,
        milestones=milestones,
        updates=updates,
        comments=comments,
        pls_price=pls_price
    )


# ============================================================================
# ROUTES - Contributions
# ============================================================================

@app.route('/api/contribute', methods=['POST'])
def contribute():
    """Make contribution to campaign"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        return jsonify({'success': False, 'error': 'Not connected'}), 401

    user = get_or_create_user(wallet_address)

    data = request.json
    campaign_id = data.get('campaign_id')
    amount_pls = float(data.get('amount_pls', 0))
    comment_text = data.get('comment', '')

    if amount_pls <= 0:
        return jsonify({'success': False, 'error': 'Invalid amount'}), 400

    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    if not campaign or not campaign.is_active:
        return jsonify({'success': False, 'error': 'Campaign not found'}), 404

    # Calculate burn (1%)
    burned_pls = calculate_burn(amount_pls)
    to_campaign_pls = amount_pls - burned_pls

    # Calculate USD
    pls_price = get_current_pls_price()
    amount_usd = amount_pls * pls_price

    # Create contribution
    contribution = Contribution(
        campaign_id=campaign.id,
        contributor_id=user.id,
        amount_pls=amount_pls,
        amount_usd=amount_usd,
        burned_pls=burned_pls,
        to_campaign_pls=to_campaign_pls,
        transaction_hash=generate_transaction_hash(),
        comment=comment_text
    )

    db.session.add(contribution)

    # Update campaign stats
    campaign.total_raised_pls += to_campaign_pls
    campaign.total_raised_usd += amount_usd
    campaign.total_burned_pls += burned_pls

    # Update supporter count if first contribution from this user
    existing_contributions = Contribution.query.filter_by(campaign_id=campaign.id, contributor_id=user.id).count()
    if existing_contributions == 0:
        campaign.supporter_count += 1
        user.campaigns_supported += 1

    # Update user stats
    user.total_contributed += amount_pls
    user.total_burned += burned_pls

    # Update burn stats
    update_burn_stats(contribution_burn=burned_pls)

    # Check achievements
    new_achievements = check_and_award_achievements(user)

    db.session.commit()

    return jsonify({
        'success': True,
        'transaction_hash': contribution.transaction_hash,
        'burned_pls': burned_pls,
        'to_campaign_pls': to_campaign_pls,
        'new_achievements': [{'name': a.achievement_name, 'tier': a.badge_tier} for a in new_achievements]
    })


# ============================================================================
# ROUTES - Top Contributors
# ============================================================================

@app.route('/leaderboard')
def leaderboard():
    """Top contributors leaderboard"""
    wallet_address = session.get('wallet_address')
    user = None
    if wallet_address:
        user = User.query.filter_by(wallet_address=wallet_address).first()

    time_period = request.args.get('period', 'all_time')

    # Get top contributors
    top_contributors = get_top_contributors(time_period=time_period, limit=100)

    pls_price = get_current_pls_price()

    return render_template(
        'leaderboard.html',
        user=user,
        top_contributors=top_contributors,
        time_period=time_period,
        pls_price=pls_price
    )


@app.route('/profile/<wallet_address>')
def profile(wallet_address):
    """User profile page"""
    current_wallet = session.get('wallet_address')
    current_user = None
    if current_wallet:
        current_user = User.query.filter_by(wallet_address=current_wallet).first()

    profile_user = User.query.filter_by(wallet_address=wallet_address).first()
    if not profile_user:
        return "User not found", 404

    # Get user's campaigns
    created_campaigns = Campaign.query.filter_by(creator_id=profile_user.id).order_by(Campaign.created_at.desc()).all()

    # Get user's contributions
    contributions = Contribution.query.filter_by(contributor_id=profile_user.id).order_by(Contribution.created_at.desc()).limit(50).all()

    # Get achievements
    achievements = Achievement.query.filter_by(user_id=profile_user.id).order_by(Achievement.earned_at.desc()).all()

    # Get rank
    top_contributors = get_top_contributors('all_time', 1000)
    user_rank = None
    for item in top_contributors:
        if item['user'].id == profile_user.id:
            user_rank = item['rank']
            break

    pls_price = get_current_pls_price()

    return render_template(
        'profile.html',
        current_user=current_user,
        profile_user=profile_user,
        created_campaigns=created_campaigns,
        contributions=contributions,
        achievements=achievements,
        user_rank=user_rank,
        pls_price=pls_price
    )


# ============================================================================
# ROUTES - Burn Stats & Price Chart
# ============================================================================

@app.route('/burns')
def burn_stats_page():
    """Burn statistics and projections"""
    wallet_address = session.get('wallet_address')
    user = None
    if wallet_address:
        user = User.query.filter_by(wallet_address=wallet_address).first()

    # Get burn stats history
    burn_stats = BurnStats.query.order_by(BurnStats.date.desc()).limit(30).all()
    burn_stats.reverse()  # Oldest to newest for chart

    # Get latest stats
    latest_stats = BurnStats.query.order_by(BurnStats.date.desc()).first()
    total_burned = latest_stats.total_burn_to_date if latest_stats else 0.0

    # Get price history (mocked)
    pls_price = get_current_pls_price()

    return render_template(
        'burn_stats.html',
        user=user,
        burn_stats=burn_stats,
        total_burned=total_burned,
        pls_price=pls_price
    )


@app.route('/api/burn_projections', methods=['POST'])
def burn_projections():
    """Calculate burn projections"""
    data = request.json

    # Input variables
    daily_volume_pls = float(data.get('daily_volume_pls', 0))
    campaigns_per_day = int(data.get('campaigns_per_day', 0))
    avg_creation_fee = float(data.get('avg_creation_fee', 25))
    projection_days = int(data.get('projection_days', 365))

    # Calculate daily burn
    daily_contribution_burn = daily_volume_pls * 0.01
    daily_creation_burn = campaigns_per_day * avg_creation_fee
    daily_total_burn = daily_contribution_burn + daily_creation_burn

    # Calculate projections
    projections = {
        'daily': daily_total_burn,
        'weekly': daily_total_burn * 7,
        'monthly': daily_total_burn * 30,
        'yearly': daily_total_burn * 365,
        'custom': daily_total_burn * projection_days
    }

    # Get current PLS price for USD values
    pls_price = get_current_pls_price()

    projections_usd = {
        'daily': projections['daily'] * pls_price,
        'weekly': projections['weekly'] * pls_price,
        'monthly': projections['monthly'] * pls_price,
        'yearly': projections['yearly'] * pls_price,
        'custom': projections['custom'] * pls_price
    }

    return jsonify({
        'success': True,
        'projections_pls': projections,
        'projections_usd': projections_usd,
        'daily_contribution_burn': daily_contribution_burn,
        'daily_creation_burn': daily_creation_burn,
        'daily_total_burn': daily_total_burn
    })


@app.route('/api/price_history')
def price_history():
    """Get PLS price history"""
    # In production, fetch from PulseX DEX
    # For demo, return mock data

    days = int(request.args.get('days', 30))

    history = []
    base_price = get_current_pls_price()

    for i in range(days):
        timestamp = datetime.utcnow() - timedelta(days=days - i)
        # Random price variation for demo
        price = base_price * (1 + random.uniform(-0.1, 0.1))
        volume = random.uniform(100000, 500000)

        history.append({
            'timestamp': timestamp.isoformat(),
            'price': price,
            'volume': volume
        })

    return jsonify({
        'success': True,
        'history': history,
        'current_price': base_price
    })


# ============================================================================
# ROUTES - Campaign Management
# ============================================================================

@app.route('/api/post_update', methods=['POST'])
def post_update():
    """Post campaign update"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        return jsonify({'success': False, 'error': 'Not connected'}), 401

    user = User.query.filter_by(wallet_address=wallet_address).first()

    data = request.json
    campaign_id = data.get('campaign_id')
    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url', '')

    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    if not campaign or campaign.creator_id != user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    update = CampaignUpdate(
        campaign_id=campaign.id,
        title=title,
        content=content,
        image_url=image_url
    )

    db.session.add(update)
    db.session.commit()

    return jsonify({
        'success': True,
        'update_id': update.id
    })


@app.route('/api/post_comment', methods=['POST'])
def post_comment():
    """Post comment on campaign"""
    wallet_address = session.get('wallet_address')
    if not wallet_address:
        return jsonify({'success': False, 'error': 'Not connected'}), 401

    user = User.query.filter_by(wallet_address=wallet_address).first()

    data = request.json
    campaign_id = data.get('campaign_id')
    content = data.get('content')

    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    if not campaign:
        return jsonify({'success': False, 'error': 'Campaign not found'}), 404

    comment = Comment(
        campaign_id=campaign.id,
        user_id=user.id,
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'success': True,
        'comment_id': comment.id
    })


# ============================================================================
# ROUTES - Activity Feed
# ============================================================================

@app.route('/api/activity_feed')
def activity_feed():
    """Get live activity feed"""
    limit = int(request.args.get('limit', 50))

    # Get recent contributions
    recent_contributions = Contribution.query.order_by(Contribution.created_at.desc()).limit(limit).all()

    activities = []
    for contrib in recent_contributions:
        campaign = Campaign.query.get(contrib.campaign_id)
        contributor = User.query.get(contrib.contributor_id)

        activities.append({
            'type': 'contribution',
            'contributor_address': contributor.display_address(),
            'amount_pls': contrib.amount_pls,
            'burned_pls': contrib.burned_pls,
            'campaign_title': campaign.title,
            'campaign_id': campaign.campaign_id,
            'timestamp': contrib.created_at.isoformat()
        })

    return jsonify({
        'success': True,
        'activities': activities
    })


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()

        # Check if already initialized
        if User.query.count() > 0:
            return

        print("Initializing database with sample data...")

        # Create sample users
        sample_users = []
        for i in range(20):
            wallet = generate_wallet_address()
            user = User(
                wallet_address=wallet,
                total_contributed=random.uniform(100, 5000),
                total_burned=random.uniform(1, 50),
                campaigns_supported=random.randint(1, 10),
                campaigns_created=random.randint(0, 3)
            )
            sample_users.append(user)
            db.session.add(user)

        db.session.commit()

        # Create sample campaigns
        categories = ['personal', 'business', 'charity', 'emergency', 'creative', 'education', 'medical', 'community']
        pls_price = get_current_pls_price()

        for i in range(30):
            creator = random.choice(sample_users)
            category = random.choice(categories)
            goal_usd = random.uniform(1000, 50000)
            goal_pls = goal_usd / pls_price

            campaign = Campaign(
                campaign_id=generate_campaign_id(),
                creator_id=creator.id,
                title=f'Sample Campaign {i+1}: Help Fund {category.capitalize()} Project',
                category=category,
                description=f'This is a sample {category} campaign to demonstrate Fund.tires platform features.',
                goal_usd=goal_usd,
                goal_pls=goal_pls,
                duration_days=random.randint(30, 90),
                beneficiary_address=creator.wallet_address,
                num_milestones=random.randint(4, 10),
                creator_deposit_per_stage=goal_pls / 10,
                total_creator_deposit=goal_pls,
                ends_at=datetime.utcnow() + timedelta(days=random.randint(1, 90)),
                creation_fee_burned=Config.CREATION_FEES.get(category, 25),
                total_raised_pls=goal_pls * random.uniform(0.1, 0.9),
                total_burned_pls=goal_pls * random.uniform(0.001, 0.009),
                supporter_count=random.randint(5, 50)
            )

            db.session.add(campaign)

        db.session.commit()

        # Create initial burn stats
        today = date.today()
        burn_stat = BurnStats(
            date=today,
            daily_contribution_burn=100.0,
            daily_creation_burn=500.0,
            daily_total_burn=600.0,
            campaigns_created=20,
            contributions_made=150,
            total_burn_to_date=50000.0
        )
        db.session.add(burn_stat)
        db.session.commit()

        print("Database initialized successfully!")


if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("FUND.TIRES - GoFundMe × Pump.tires Hybrid on PulseChain")
    print("="*60)
    print("\nStarting server on http://127.0.0.1:5000")
    print("\nPress CTRL+C to stop the server\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
