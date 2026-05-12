import asyncio
import logging
from datetime import datetime
import discord
from discord.ext import commands

from config import (
    DISCORD_TOKEN,
    DISCORD_CHANNEL_ID,
    ACCOUNT_BALANCE,
    RISK_PERCENT_PER_TRADE
)
from data_fetcher import BinanceDataFetcher
from smc_ict_analyzer import SMCICTAnalyzer, Candle
from risk_manager import RiskManager
from discord_bot import TradingBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XAUUSDTradingSystem:
    """Main Trading System with Real-Time Data & Discord Signals"""
    
    def __init__(self):
        self.data_fetcher = BinanceDataFetcher(symbol="XAUUSDT", interval="1h")
        self.analyzer = SMCICTAnalyzer(lookback_periods=100)
        self.risk_manager = RiskManager(ACCOUNT_BALANCE, RISK_PERCENT_PER_TRADE)
        
        # Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        
        self.trading_bot = None
        self.last_signal_time = None
    
    async def on_candle_close(self, candle: Candle):
        """Called when a candle closes - ZERO DELAY"""
        logger.info(f"\n🕯️  CANDLE CLOSED: {candle.timestamp}")
        logger.info(f"   OHLCV: {candle.open:.2f} | {candle.high:.2f} | {candle.low:.2f} | {candle.close:.2f} | {candle.volume:.0f}")
        
        # Add to analyzer
        self.analyzer.add_candle(candle)
        
        # Analyze
        await self.analyze_and_signal(candle)
    
    async def analyze_and_signal(self, candle: Candle):
        """Perform SMC/ICT analysis and generate signals"""
        try:
            # Identify swings
            self.analyzer.identify_swings()
            
            # Detect signals
            bos = self.analyzer.detect_break_of_structure()
            sweeps = self.analyzer.detect_liquidity_sweeps()
            order_blocks = self.analyzer.identify_order_blocks()
            structure = self.analyzer.get_market_structure()
            
            logger.info(f"📊 Market Structure: {structure.value}")
            logger.info(f"   Break of Structure: {'YES' if bos else 'NO'}")
            logger.info(f"   Liquidity Sweeps: {len(sweeps)}")
            logger.info(f"   Order Blocks: {len(order_blocks)}")
            
            # Generate setup
            setup = self.generate_trade_setup(candle)
            
            if setup:
                logger.info(f"\n✅ TRADE SETUP GENERATED!")
                logger.info(f"   Type: {setup.setup_type}")
                logger.info(f"   Entry: ${setup.entry_price:.2f}")
                logger.info(f"   SL: ${setup.stop_loss:.2f}")
                logger.info(f"   TP: ${setup.take_profit:.2f}")
                logger.info(f"   RR: 1:{setup.risk_reward_ratio:.2f}")
                logger.info(f"   Size: {setup.position_size:.3f} lots")
                logger.info(f"   Confidence: {setup.confidence:.1f}%\n")
                
                # Send to Discord
                if self.trading_bot:
                    await self.trading_bot.send_trade_signal(setup)
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}", exc_info=True)
    
    def generate_trade_setup(self, candle: Candle):
        """Generate trade setup based on SMC/ICT signals"""
        try:
            bos = self.analyzer.detect_break_of_structure()
            sweeps = self.analyzer.detect_liquidity_sweeps()
            order_blocks = self.analyzer.identify_order_blocks()
            
            if not (bos and (sweeps or order_blocks)):
                return None
            
            trend, bos_price = bos
            
            # Signal 1: Sweep + Retest
            if sweeps and bos:
                last_sweep = sweeps[-1]
                
                if trend.value == "UP" and candle.close > bos_price:
                    stop_loss = last_sweep.price - 50
                    
                    tp, actual_rr = self.risk_manager.calculate_take_profit(
                        candle.close, stop_loss, risk_reward_ratio=2.0
                    )
                    
                    position_size = self.risk_manager.calculate_position_size(
                        candle.close, stop_loss
                    )
                    
                    is_valid, msg = self.risk_manager.validate_setup(
                        candle.close, stop_loss, tp, position_size
                    )
                    
                    if is_valid:
                        from smc_ict_analyzer import TradeSetup
                        return TradeSetup(
                            entry_price=candle.close,
                            stop_loss=stop_loss,
                            take_profit=tp,
                            risk_reward_ratio=actual_rr,
                            position_size=position_size,
                            setup_type="SWEEP_RETEST_UP",
                            confidence=75.0,
                            timestamp=datetime.now()
                        )
                
                elif trend.value == "DOWN" and candle.close < bos_price:
                    stop_loss = last_sweep.price + 50
                    
                    tp, actual_rr = self.risk_manager.calculate_take_profit(
                        candle.close, stop_loss, risk_reward_ratio=2.0
                    )
                    
                    position_size = self.risk_manager.calculate_position_size(
                        candle.close, stop_loss
                    )
                    
                    is_valid, msg = self.risk_manager.validate_setup(
                        candle.close, stop_loss, tp, position_size
                    )
                    
                    if is_valid:
                        from smc_ict_analyzer import TradeSetup
                        return TradeSetup(
                            entry_price=candle.close,
                            stop_loss=stop_loss,
                            take_profit=tp,
                            risk_reward_ratio=actual_rr,
                            position_size=position_size,
                            setup_type="SWEEP_RETEST_DOWN",
                            confidence=75.0,
                            timestamp=datetime.now()
                        )
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating trade setup: {e}")
            return None
    
    async def initialize_bot(self):
        """Initialize Discord bot"""
        @self.bot.event
        async def on_ready():
            logger.info(f"\n{'='*60}")
            logger.info(f"🤖 XAUUSD SMC/ICT Trading Bot Online")
            logger.info(f"📊 Account Balance: ${ACCOUNT_BALANCE:,.2f}")
            logger.info(f"📈 Risk per Trade: {RISK_PERCENT_PER_TRADE}%")
            logger.info(f"🔗 Discord Channel: {DISCORD_CHANNEL_ID}")
            logger.info(f"{'='*60}\n")
            
            # Create trading bot cog
            self.trading_bot = TradingBot(self.bot, DISCORD_CHANNEL_ID)
        
        await self.bot.add_cog(TradingBot(self.bot, DISCORD_CHANNEL_ID))
    
    async def start_trading(self):
        """Start the trading system"""
        try:
            logger.info("🚀 Starting XAUUSD Trading System...")
            
            # Set candle callback
            self.data_fetcher.set_candle_close_callback(self.on_candle_close)
            
            # Load historical data
            logger.info("📊 Loading historical data...")
            await self.data_fetcher.fetch_historical_data(limit=100)
            
            # Initialize with historical candles
            for candle in self.data_fetcher.candles:
                self.analyzer.add_candle(candle)
            
            logger.info(f"✅ Loaded {len(self.analyzer.candles)} candles for analysis")
            
            # Start bot and data stream concurrently
            logger.info("🔌 Starting real-time WebSocket stream...")
            
            bot_task = asyncio.create_task(self.bot.start(DISCORD_TOKEN))
            stream_task = asyncio.create_task(self.data_fetcher.start_stream())
            
            await asyncio.gather(bot_task, stream_task)
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)

async def main():
    """Main entry point"""
    system = XAUUSDTradingSystem()
    await system.initialize_bot()
    await system.start_trading()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 XAUUSD SMC/ICT TRADING AI")
    print("📊 Real-Time Data | Discord Signals | Professional Risk Management")
    print("="*70 + "\n")
    
    asyncio.run(main())
