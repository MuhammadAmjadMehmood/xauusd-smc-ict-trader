import os
from dotenv import load_dotenv

load_dotenv()

# Discord Settings
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 0))

# Binance API
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# OANDA Forex
OANDA_API_KEY = os.getenv('OANDA_API_KEY')
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID')

# Account Settings
ACCOUNT_BALANCE = float(os.getenv('ACCOUNT_BALANCE', 50000))
RISK_PERCENT_PER_TRADE = float(os.getenv('RISK_PERCENT_PER_TRADE', 1.0))
MAX_OPEN_TRADES = int(os.getenv('MAX_OPEN_TRADES', 3))

# SMC/ICT Parameters
SWING_LOOKBACK = 2
ORDER_BLOCK_DEPTH = 4
LIQUIDITY_SWEEP_AGG = 4

# Risk Management
DEFAULT_RISK_REWARD_RATIO = float(os.getenv('DEFAULT_RISK_REWARD_RATIO', 2.0))
MIN_POSITION_SIZE = 0.01
MAX_POSITION_SIZE = 10.0
MIN_RISK_REWARD = 1.5

# Data
DATA_SOURCE = os.getenv('DATA_SOURCE', 'binance')
TIMEFRAME = os.getenv('TIMEFRAME', '1h')
KLINE_INTERVAL = 3600  # 1 hour in seconds

# Logging
LOG_FILE = 'xauusd_trader.log'
LOG_LEVEL = 'INFO'

# Trading Symbols
XAUUSD_SYMBOL = 'XAUUSD'
BINANCE_SYMBOL = 'XAUUSDT'
