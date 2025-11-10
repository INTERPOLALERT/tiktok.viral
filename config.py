import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fund-tires-secret-key-pulsechain-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fundtires.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PulseChain Configuration
    PLS_ADDRESS = '0x0000000000000000000000000000000000000000'
    WPLS_ADDRESS = '0xA1077a294dDE1B09bB078844df40758a5D0f9a27'

    # Burn Rates
    CONTRIBUTION_BURN_RATE = 0.01  # 1%

    # Creation Fees (in PLS) - 100% burned
    CREATION_FEES = {
        'personal': 25,
        'business': 50,
        'charity': 15,
        'emergency': 10,
        'creative': 25,
        'education': 25,
        'medical': 15,
        'community': 25,
        'technology': 50,
        'environment': 25,
        'animal': 20,
        'other': 25
    }

    # Achievement Thresholds (in PLS)
    ACHIEVEMENTS = {
        'fire_starter': 100,
        'flame_fanatic': 1000,
        'inferno_king': 10000,
        'burn_legend_percentile': 1  # Top 1%
    }

    # Milestone Release Percentages
    MILESTONE_RELEASES = {
        25: 20,   # 25% funded -> withdraw 20%
        50: 40,   # 50% funded -> withdraw 40%
        75: 60,   # 75% funded -> withdraw 60%
        100: 100  # 100% funded -> withdraw 100%
    }
