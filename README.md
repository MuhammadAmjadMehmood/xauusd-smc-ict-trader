# 🚀 XAUUSD SMC/ICT Trading AI

**Real-Time Trading System with Zero Delay Discord Signals**

## ⚡ Features

### ✅ Real-Time Data (ZERO DELAY)
- **WebSocket Integration** - Direct connection to Binance
- **Sub-second Signals** - Trade alerts sent to Discord instantly on candle close
- **Auto Reconnection** - Never misses a signal
- **1-Hour Timeframe** - Ideal for swing trading

### ✅ SMC/ICT Trading Concepts
- **Break of Structure (BoS)** - Identifies swing high/low breaks
- **Liquidity Sweeps** - Detects smart money taking out stops
- **Order Blocks** - Consolidation zones + retest setups
- **Market Structure** - Uptrend/Downtrend/Ranging confirmation

### ✅ Professional Risk Management
- **Position Sizing** - Based on account % risk (default 1% per trade)
- **Risk/Reward Ratio** - Minimum 1.5:1, enforced validation
- **Stop Loss** - Always calculated and validated
- **Take Profit** - Auto-calculated based on RR multiple
- **Account Protection** - Max 3 open trades

### ✅ Discord Integration
- **Rich Signal Embeds** - All trade details in one message
- **Real-Time Alerts** - Instant notification when signals generated
- **Command Support** - Check status, view signals
- **Reaction Buttons** - Track trade acceptance/rejection

---

## 🎯 Trade Setups

### Setup 1: Sweep + Retest
```
1. Liquidity sweep takes out previous level (high/low)
2. Price retests that swept level
3. Confirmation candle breaks above/below retest
4. Entry on break with SL beyond retest + buffer
```

### Setup 2: Order Block Break
```
1. Identify order block in consolidation area
2. Price breaks above/below OB
3. Retest of OB line
4. Entry on second break with SL beyond OB
```

---

## 🔧 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/MuhammadAmjadMehmood/xauusd-smc-ict-trader
cd xauusd-smc-ict-trader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Configure:**
- `DISCORD_TOKEN` - Your Discord bot token
- `DISCORD_CHANNEL_ID` - Channel ID to send signals
- `BINANCE_API_KEY` - Binance API credentials
- `BINANCE_API_SECRET` - Binance API secret
- `ACCOUNT_BALANCE` - Your trading account size
- `RISK_PERCENT_PER_TRADE` - Risk % per trade (default 1%)

### 4. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section → "Add Bot"
4. Copy the token → paste in `.env`
5. Enable "Message Content Intent" under Privileged Gateway Intents
6. Go to OAuth2 → URL Generator
7. Select scopes: `bot`
8. Select permissions: `Send Messages`, `Embed Links`, `Add Reactions`
9. Copy generated URL → open in browser → authorize

### 5. Get Channel ID
1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click channel → Copy ID
3. Paste in `.env`

### 6. Run the Bot
```bash
python main.py
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│         BINANCE WEBSOCKET (Real-Time Klines)           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   Data Fetcher             │
        │   - WebSocket Manager      │
        │   - Candle Parser          │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   SMC/ICT Analyzer         │
        │   - Swing Detection        │
        │   - BoS Detection          │
        │   - Liquidity Sweeps       │
        │   - Order Blocks           │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   Risk Manager             │
        │   - Position Sizing        │
        │   - RR Calculation         │
        │   - Setup Validation       │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   Discord Bot              │
        │   - Signal Embeds          │
        │   - Command Handling       │
        └────────────────────────────┘
```

---

## 💻 Commands

### `!signal`
Get latest trade signal details

### `!status`
Check bot status and trade stats

---

## 📈 Risk Management Formula

### Position Sizing
```
Risk Amount = Account Balance × Risk % per Trade
Risk Distance = Entry - Stop Loss
Position Size = Risk Amount / (Risk Distance × 100)

* For XAUUSD: 1 lot = 100 troy ounces
* $1 price move = $100 profit/loss per lot
```

### Take Profit Calculation
```
TP = Entry ± (Entry - SL) × Risk/Reward Ratio

Example (Long Trade):
- Entry: $2500
- SL: $2490 (risk = $10)
- RR: 2.0
- TP = 2500 + (10 × 2.0) = $2520
```

---

## 🔍 Signal Example

```
⚡ 🟢 LONG SIGNAL - SWEEP_RETEST_UP
XAUUSD SMC/ICT Trading Setup

📍 Entry Price: $2485.50
🛑 Stop Loss: $2475.00
🎯 Take Profit: $2506.00

💰 Risk per Trade: $10.50
📈 Potential Profit: $20.50
📊 Risk/Reward Ratio: 1:2.0

📦 Position Size: 1.000 lots
🎲 Confidence: 75.0%
🔄 Setup Type: SWEEP_RETEST_UP

Trade Responsibly ⚠️
```

---

## ⚠️ Disclaimer

**This is an EDUCATIONAL trading system for learning purposes.**

- Always paper trade first
- Never risk more than you can afford to lose
- Test thoroughly before live trading
- Past performance ≠ future results
- Trading forex/commodities carries high risk

---

## 📝 License

MIT License - Feel free to use and modify

---

## 🤝 Support

Having issues? 
1. Check your `.env` configuration
2. Verify Discord bot permissions
3. Check API credentials
4. Review logs for errors

---

## 🚀 Next Steps

- [ ] Add more timeframes (15m, 4h, 1d)
- [ ] Implement trade execution API
- [ ] Add performance analytics
- [ ] Create web dashboard
- [ ] Add more SMC patterns
- [ ] Implement machine learning confirmation

---

**Happy Trading! 🎯📊**
