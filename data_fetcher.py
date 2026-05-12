import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import aiohttp
from binance.websocket.spot.websocket_client import SpotWebsocketClient
from smc_ict_analyzer import Candle
import json

logger = logging.getLogger(__name__)

class BinanceDataFetcher:
    """Real-time data fetching from Binance with ZERO DELAY"""
    
    def __init__(self, symbol: str = "XAUUSDT", interval: str = "1h"):
        self.symbol = symbol
        self.interval = interval
        self.candles: List[Candle] = []
        self.current_candle: Optional[dict] = None
        self.websocket_client = None
        self.on_candle_close_callback = None
    
    def set_candle_close_callback(self, callback):
        """Set callback for when candle closes"""
        self.on_candle_close_callback = callback
    
    async def message_handler(self, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            
            if 'k' in data:  # Kline data
                kline = data['k']
                
                candle_data = {
                    'timestamp': datetime.fromtimestamp(kline['t'] / 1000),
                    'open': float(kline['o']),
                    'high': float(kline['h']),
                    'low': float(kline['l']),
                    'close': float(kline['c']),
                    'volume': float(kline['v']),
                    'is_closed': kline['x']
                }
                
                self.current_candle = candle_data
                
                # If candle is closed, trigger callback
                if kline['x'] and self.on_candle_close_callback:
                    candle = Candle(
                        timestamp=candle_data['timestamp'],
                        open=candle_data['open'],
                        high=candle_data['high'],
                        low=candle_data['low'],
                        close=candle_data['close'],
                        volume=candle_data['volume']
                    )
                    self.candles.append(candle)
                    
                    # Call callback immediately
                    await self.on_candle_close_callback(candle)
                    
                    logger.info(f"📊 Candle Closed: {candle.timestamp} O:{candle.open:.2f} H:{candle.high:.2f} L:{candle.low:.2f} C:{candle.close:.2f}")
        
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def start_stream(self):
        """Start real-time WebSocket stream"""
        try:
            # Map interval to Binance format
            interval_map = {
                '1h': '1h',
                '4h': '4h',
                '1d': '1d',
                '15m': '15m',
                '1m': '1m'
            }
            
            binance_interval = interval_map.get(self.interval, '1h')
            stream = f"{self.symbol.lower()}@kline_{binance_interval}"
            
            url = f"wss://stream.binance.com:9443/ws/{stream}"
            
            logger.info(f"🔌 Connecting to Binance WebSocket: {stream}")
            
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url) as ws:
                    logger.info("✅ WebSocket Connected - Listening for XAUUSD signals...")
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self.message_handler(msg.data)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WebSocket error: {ws.exception()}")
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            logger.warning("WebSocket closed, attempting to reconnect...")
                            await asyncio.sleep(5)
                            await self.start_stream()  # Reconnect
        
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            await asyncio.sleep(5)
            await self.start_stream()  # Reconnect
    
    async def fetch_historical_data(self, limit: int = 100) -> List[Candle]:
        """Fetch historical candles for initialization"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            
            interval_map = {
                '1h': '1h',
                '4h': '4h',
                '1d': '1d',
                '15m': '15m',
                '1m': '1m'
            }
            
            params = {
                'symbol': self.symbol,
                'interval': interval_map.get(self.interval, '1h'),
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        for kline in data:
                            candle = Candle(
                                timestamp=datetime.fromtimestamp(kline[0] / 1000),
                                open=float(kline[1]),
                                high=float(kline[2]),
                                low=float(kline[3]),
                                close=float(kline[4]),
                                volume=float(kline[7])
                            )
                            self.candles.append(candle)
                        
                        logger.info(f"✅ Loaded {len(self.candles)} historical candles")
                        return self.candles
                    else:
                        logger.error(f"Failed to fetch data: {resp.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return []
    
    def get_current_price(self) -> Optional[float]:
        """Get current price from latest candle"""
        if self.current_candle:
            return self.current_candle['close']
        return None
    
    def get_latest_candles(self, count: int = 20) -> List[Candle]:
        """Get latest N candles"""
        return self.candles[-count:] if len(self.candles) >= count else self.candles
