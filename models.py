from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)  # 0x + 40 hex chars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_contributed = db.Column(db.Float, default=0.0)
    total_burned = db.Column(db.Float, default=0.0)
    campaigns_supported = db.Column(db.Integer, default=0)
    campaigns_created = db.Column(db.Integer, default=0)

    # Relationships
    campaigns = db.relationship('Campaign', backref='creator', lazy=True, foreign_keys='Campaign.creator_id')
    contributions = db.relationship('Contribution', backref='contributor', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)

    def display_address(self):
        """Returns formatted address: 0x742d...8B4e"""
        if len(self.wallet_address) >= 10:
            return f"{self.wallet_address[:6]}...{self.wallet_address[-4:]}"
        return self.wallet_address

    def calculate_rank_score(self):
        """Calculate ranking score: volume + 20% burn bonus + 10% frequency bonus"""
        volume_score = self.total_contributed
        burn_bonus = self.total_burned * 0.20
        frequency_bonus = self.campaigns_supported * 0.10
        return volume_score + burn_bonus + frequency_bonus


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.String(12), unique=True, nullable=False)  # Random ID
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Basic Info
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    goal_usd = db.Column(db.Float, nullable=False)
    goal_pls = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    beneficiary_address = db.Column(db.String(42), nullable=False)

    # Staged Funding
    num_milestones = db.Column(db.Integer, default=1)
    creator_deposit_per_stage = db.Column(db.Float, default=0.0)
    total_creator_deposit = db.Column(db.Float, default=0.0)

    # Status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ends_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    # Financials
    total_raised_pls = db.Column(db.Float, default=0.0)
    total_raised_usd = db.Column(db.Float, default=0.0)
    total_burned_pls = db.Column(db.Float, default=0.0)
    creation_fee_burned = db.Column(db.Float, default=0.0)
    supporter_count = db.Column(db.Integer, default=0)
    contribution_velocity = db.Column(db.Float, default=0.0)  # PLS per hour

    # Media
    image_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))

    # Relationships
    contributions = db.relationship('Contribution', backref='campaign', lazy=True)
    milestones = db.relationship('Milestone', backref='campaign', lazy=True)
    updates = db.relationship('CampaignUpdate', backref='campaign', lazy=True)
    comments = db.relationship('Comment', backref='campaign', lazy=True)

    def progress_percentage(self):
        """Calculate funding progress"""
        if self.goal_pls > 0:
            return min((self.total_raised_pls / self.goal_pls) * 100, 100)
        return 0

    def days_remaining(self):
        """Calculate days remaining"""
        if self.ends_at > datetime.utcnow():
            delta = self.ends_at - datetime.utcnow()
            return delta.days
        return 0

    def is_successful(self):
        """Check if campaign reached goal"""
        return self.total_raised_pls >= self.goal_pls

    def is_ended(self):
        """Check if campaign has ended"""
        return datetime.utcnow() >= self.ends_at

    def current_milestone_stage(self):
        """Determine current milestone stage based on funding"""
        progress = self.progress_percentage()
        if progress >= 100:
            return 100
        elif progress >= 75:
            return 75
        elif progress >= 50:
            return 50
        elif progress >= 25:
            return 25
        return 0


class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    amount_pls = db.Column(db.Float, nullable=False)
    amount_usd = db.Column(db.Float, nullable=False)
    burned_pls = db.Column(db.Float, nullable=False)  # 1% of amount
    to_campaign_pls = db.Column(db.Float, nullable=False)  # 99% of amount

    transaction_hash = db.Column(db.String(66))  # 0x + 64 hex chars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.Text)


class Milestone(db.Model):
    __tablename__ = 'milestones'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)

    stage_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    required_amount_pls = db.Column(db.Float, nullable=False)
    creator_deposit_pls = db.Column(db.Float, nullable=False)

    is_completed = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    verified_at = db.Column(db.DateTime)

    proof_submitted = db.Column(db.Text)
    proof_url = db.Column(db.String(500))

    funds_released = db.Column(db.Boolean, default=False)
    funds_released_at = db.Column(db.DateTime)


class CampaignUpdate(db.Model):
    __tablename__ = 'campaign_updates'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(500))


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    achievement_type = db.Column(db.String(50), nullable=False)
    # Types: fire_starter, flame_fanatic, inferno_king, burn_legend,
    #        first_contribution, big_spender, consistent_giver, top_10, top_100, etc.

    achievement_name = db.Column(db.String(100), nullable=False)
    achievement_description = db.Column(db.String(200))
    badge_tier = db.Column(db.String(20))  # bronze, silver, gold, platinum

    earned_at = db.Column(db.DateTime, default=datetime.utcnow)


class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pls_usd_price = db.Column(db.Float, nullable=False)
    volume_24h = db.Column(db.Float, default=0.0)


class BurnStats(db.Model):
    __tablename__ = 'burn_stats'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)

    daily_contribution_burn = db.Column(db.Float, default=0.0)
    daily_creation_burn = db.Column(db.Float, default=0.0)
    daily_total_burn = db.Column(db.Float, default=0.0)

    campaigns_created = db.Column(db.Integer, default=0)
    contributions_made = db.Column(db.Integer, default=0)

    total_burn_to_date = db.Column(db.Float, default=0.0)


def generate_campaign_id():
    """Generate random 12-character campaign ID"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))


def generate_transaction_hash():
    """Generate fake transaction hash for demo"""
    return '0x' + ''.join(random.choices('0123456789abcdef', k=64))


def generate_wallet_address():
    """Generate fake wallet address for demo"""
    return '0x' + ''.join(random.choices('0123456789abcdef', k=40))
