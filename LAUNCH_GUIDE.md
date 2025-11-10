# FUND.TIRES - Windows 11 Launch Guide

## Quick Start (3 Steps)

### Step 1: Install Python
1. Download Python 3.8+ from: https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Complete the installation

### Step 2: Install Dependencies
1. Open File Explorer and navigate to the `tiktok.viral` folder
2. Double-click `install.bat`
3. Wait for installation to complete

### Step 3: Launch Application
1. Double-click `run.bat`
2. Open your browser to: http://127.0.0.1:5000
3. Start using Fund.tires!

## What to Expect

When you run the application:
- A command window will open showing server logs
- The database will be automatically created with sample data
- Your browser should navigate to http://127.0.0.1:5000

## First Time Setup

The first time you run the application:
1. **Sample Data**: 20 sample users, 30 sample campaigns will be created
2. **Wallet Connection**: Click "Connect Wallet" to create a demo wallet
3. **Create Campaign**: Click "Create Campaign in 30 Seconds" to launch your first fundraiser

## Using the Application

### Connect a Wallet
- Click "Connect Wallet" button in the top right
- A random PulseChain address will be generated (demo mode)
- Format: 0x742d...8B4e

### Create a Campaign
1. Click "Create Campaign"
2. Fill in:
   - Title
   - Category (determines creation fee: 10-50 PLS)
   - Description
   - Funding goal (in USD)
   - Duration (7-90 days)
   - Number of milestones (for staged funding)
3. Click "Launch Campaign in 30 Seconds"
4. Your campaign is live!

### Contribute to Campaigns
1. Browse campaigns on the homepage or Discover page
2. Click on a campaign to view details
3. Enter PLS amount to contribute
4. See the breakdown:
   - 99% goes to campaign
   - 1% is permanently burned
5. Click "Contribute Now"

### Explore Features
- **Leaderboard**: View top contributors ranked by activity
- **Burns**: Track total PLS burned and calculate projections
- **Profile**: View your contribution history and achievements
- **Discover**: Filter and search all campaigns

## Key Features

### 1% Burn on Every Contribution
- Automatic on all contributions
- Permanently removes PLS from circulation
- Visible in burn statistics

### Staged Funding Safety Mechanism
- Campaigns divided into milestones
- Creator deposits PLS as security
- Funds released as milestones are verified
- Automatic refunds if milestones fail

### Address-Only Identity
- Your wallet address is your identity
- No usernames, emails, or passwords
- Privacy-first approach
- Format: 0x742d...8B4e

### Achievement System
- Fire Starter: Burn 100 PLS
- Flame Fanatic: Burn 1,000 PLS
- Inferno King: Burn 10,000 PLS
- Many more achievements to unlock!

### Real-Time Features
- Live activity feed
- Contribution velocity tracking
- Trending campaigns
- Burn statistics

## Troubleshooting

### Python Not Found
- Make sure Python is installed
- Verify "Add Python to PATH" was checked during installation
- Restart your computer after installing Python

### Port Already in Use
- Close any other applications using port 5000
- Or edit `app.py` and change the port number

### Dependencies Failed to Install
- Make sure you have internet connection
- Try running as Administrator
- Check Windows Firewall settings

### Database Errors
- Delete `fundtires.db` file and restart
- Database will be recreated automatically

## Demo vs Production Mode

This is a **DEMO APPLICATION** with simulated blockchain features:

### Demo Features:
- Simulated wallet connections
- Mock PLS price ($0.00015)
- Fake transaction hashes
- Local SQLite database

### For Production:
You would need to integrate:
- Real Web3/MetaMask wallet connection
- Actual PulseChain smart contracts
- Real PLS price oracle from PulseX DEX
- Blockchain transaction signing

## Stopping the Server

To stop the server:
1. Focus on the command window
2. Press `CTRL+C`
3. Type `Y` when prompted
4. Or simply close the command window

## File Structure

```
tiktok.viral/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── install.bat            # Windows installation script
├── run.bat                # Windows run script
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── campaign.html
│   ├── create_campaign.html
│   ├── discover.html
│   ├── leaderboard.html
│   ├── profile.html
│   └── burn_stats.html
└── static/
    └── css/
        └── style.css      # PulseChain gradient styles
```

## Support

For issues or questions:
- Check this guide for common solutions
- Review the main README.md for detailed information
- Ensure Python 3.8+ is installed correctly

## Next Steps

1. Explore the sample campaigns
2. Create your own test campaign
3. Make some contributions
4. Check the leaderboard rankings
5. View burn projections
6. Unlock achievements!

Enjoy using Fund.tires! 🔥
