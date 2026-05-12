import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime
from smc_ict_analyzer import TradeSetup, TrendDirection

logger = logging.getLogger(__name__)

class TradingBot(commands.Cog):
    """Discord Bot for Real-Time Trading Signals"""
    
    def __init__(self, bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id
        self.active_trades = []
        self.trade_history = []
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"✅ Bot logged in as {self.bot.user}")
    
    async def send_trade_signal(self, setup: TradeSetup):
        """Send trade signal to Discord with rich embed"""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                logger.error(f"Channel {self.channel_id} not found")
                return
            
            # Determine direction
            is_long = setup.entry_price > setup.stop_loss
            direction = "🟢 LONG" if is_long else "🔴 SHORT"
            
            # Calculate risk amount
            risk_distance = abs(setup.entry_price - setup.stop_loss)
            profit_distance = abs(setup.take_profit - setup.entry_price)
            
            # Create embed
            embed = discord.Embed(
                title=f"⚡ {direction} SIGNAL - {setup.setup_type}",
                description=f"XAUUSD SMC/ICT Trading Setup",
                color=discord.Color.green() if is_long else discord.Color.red(),
                timestamp=setup.timestamp
            )
            
            # Add fields
            embed.add_field(
                name="📍 Entry Price",
                value=f"${setup.entry_price:.2f}",
                inline=True
            )
            embed.add_field(
                name="🛑 Stop Loss",
                value=f"${setup.stop_loss:.2f}",
                inline=True
            )
            embed.add_field(
                name="🎯 Take Profit",
                value=f"${setup.take_profit:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="💰 Risk per Trade",
                value=f"${risk_distance:.2f}",
                inline=True
            )
            embed.add_field(
                name="📈 Potential Profit",
                value=f"${profit_distance:.2f}",
                inline=True
            )
            embed.add_field(
                name="📊 Risk/Reward Ratio",
                value=f"1:{setup.risk_reward_ratio:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="📦 Position Size",
                value=f"{setup.position_size:.3f} lots",
                inline=True
            )
            embed.add_field(
                name="🎲 Confidence",
                value=f"{setup.confidence:.1f}%",
                inline=True
            )
            embed.add_field(
                name="🔄 Setup Type",
                value=setup.setup_type,
                inline=True
            )
            
            # Add footer
            embed.set_footer(
                text="XAUUSD SMC/ICT Bot | Trade Responsibly ⚠️"
            )
            
            # Send embed
            message = await channel.send(embed=embed)
            
            # Add reaction buttons for tracking
            await message.add_reaction('✅')  # Accepted
            await message.add_reaction('❌')  # Rejected
            await message.add_reaction('📊')  # View stats
            
            logger.info(f"✅ Signal sent to Discord: {setup.setup_type}")
            
        except Exception as e:
            logger.error(f"Error sending signal to Discord: {e}")
    
    async def send_status_update(self, status: str):
        """Send status update to Discord"""
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                return
            
            embed = discord.Embed(
                title="📊 Bot Status Update",
                description=status,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            await channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error sending status update: {e}")
    
    @commands.command()
    async def signal(self, ctx):
        """Get latest signal info"""
        if not self.active_trades:
            await ctx.send("❌ No active trades at the moment.")
            return
        
        latest = self.active_trades[-1]
        
        embed = discord.Embed(
            title="📊 Latest Signal",
            color=discord.Color.gold()
        )
        embed.add_field(name="Entry", value=f"${latest.entry_price:.2f}")
        embed.add_field(name="Stop Loss", value=f"${latest.stop_loss:.2f}")
        embed.add_field(name="Take Profit", value=f"${latest.take_profit:.2f}")
        embed.add_field(name="Position Size", value=f"{latest.position_size:.3f} lots")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def status(self, ctx):
        """Get bot status"""
        embed = discord.Embed(
            title="🤖 Bot Status",
            color=discord.Color.green()
        )
        embed.add_field(name="Active Trades", value=len(self.active_trades))
        embed.add_field(name="Total Trades", value=len(self.trade_history))
        embed.add_field(name="Status", value="🟢 Running")
        
        await ctx.send(embed=embed)

async def setup(bot, channel_id: int):
    """Setup bot cog"""
    await bot.add_cog(TradingBot(bot, channel_id))
