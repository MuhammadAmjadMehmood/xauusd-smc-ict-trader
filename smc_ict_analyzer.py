import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    UP = "UP"
    DOWN = "DOWN"
    RANGING = "RANGING"

class LiquidityLevel(Enum):
    SUPPORT = "SUPPORT"
    RESISTANCE = "RESISTANCE"
    ORDER_BLOCK = "ORDER_BLOCK"

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class LiquidityZone:
    level_type: LiquidityLevel
    price: float
    strength: int
    timestamp: datetime
    swept: bool = False

@dataclass
class OrderBlock:
    high: float
    low: float
    timestamp: datetime
    trend_direction: TrendDirection
    is_mitigated: bool = False

@dataclass
class TradeSetup:
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    position_size: float
    setup_type: str
    confidence: float
    timestamp: datetime

class SMCICTAnalyzer:
    """Smart Money Concepts + Inner Circle Trader Analysis"""
    
    def __init__(self, lookback_periods: int = 100):
        self.lookback_periods = lookback_periods
        self.swing_highs: List[Tuple[int, float]] = []
        self.swing_lows: List[Tuple[int, float]] = []
        self.liquidity_zones: List[LiquidityZone] = []
        self.order_blocks: List[OrderBlock] = []
        self.candles: List[Candle] = []
    
    def add_candle(self, candle: Candle):
        """Add candle and update analysis"""
        self.candles.append(candle)
        if len(self.candles) > self.lookback_periods:
            self.candles.pop(0)
    
    def identify_swings(self) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """Identify swing highs and swing lows"""
        if len(self.candles) < 3:
            return [], []
        
        swing_highs = []
        swing_lows = []
        
        for i in range(1, len(self.candles) - 1):
            prev_high = self.candles[i-1].high
            curr_high = self.candles[i].high
            next_high = self.candles[i+1].high
            
            prev_low = self.candles[i-1].low
            curr_low = self.candles[i].low
            next_low = self.candles[i+1].low
            
            if curr_high > prev_high and curr_high > next_high:
                swing_highs.append((i, curr_high))
            
            if curr_low < prev_low and curr_low < next_low:
                swing_lows.append((i, curr_low))
        
        self.swing_highs = swing_highs[-5:]
        self.swing_lows = swing_lows[-5:]
        
        return swing_highs, swing_lows
    
    def detect_break_of_structure(self) -> Optional[Tuple[TrendDirection, float]]:
        """Break of Structure (BoS)"""
        if len(self.candles) < 2 or not self.swing_highs or not self.swing_lows:
            return None
        
        current_price = self.candles[-1].close
        current_high = self.candles[-1].high
        current_low = self.candles[-1].low
        
        last_swing_high = max(self.swing_highs, key=lambda x: x[0])[1]
        last_swing_low = min(self.swing_lows, key=lambda x: x[0])[1]
        
        if current_high > last_swing_high:
            return (TrendDirection.UP, last_swing_high)
        
        if current_low < last_swing_low:
            return (TrendDirection.DOWN, last_swing_low)
        
        return None
    
    def detect_liquidity_sweeps(self) -> List[LiquidityZone]:
        """Detect Liquidity Sweeps - Smart money taking out stops"""
        sweeps = []
        
        if len(self.candles) < 3:
            return sweeps
        
        for i in range(1, len(self.candles)):
            if i > 0:
                prev_candle = self.candles[i-1]
                curr_candle = self.candles[i]
                
                # Upside Sweep (takes out resistance, reverses down)
                if (curr_candle.high > prev_candle.high and 
                    curr_candle.close < curr_candle.open):
                    
                    sweep = LiquidityZone(
                        level_type=LiquidityLevel.RESISTANCE,
                        price=curr_candle.high,
                        strength=1,
                        timestamp=curr_candle.timestamp,
                        swept=True
                    )
                    sweeps.append(sweep)
                
                # Downside Sweep (takes out support, reverses up)
                if (curr_candle.low < prev_candle.low and 
                    curr_candle.close > curr_candle.open):
                    
                    sweep = LiquidityZone(
                        level_type=LiquidityLevel.SUPPORT,
                        price=curr_candle.low,
                        strength=1,
                        timestamp=curr_candle.timestamp,
                        swept=True
                    )
                    sweeps.append(sweep)
        
        self.liquidity_zones = sweeps
        return sweeps
    
    def identify_order_blocks(self) -> List[OrderBlock]:
        """Identify Order Blocks - Consolidation zones"""
        order_blocks = []
        
        if len(self.candles) < 5:
            return order_blocks
        
        bos_result = self.detect_break_of_structure()
        if not bos_result:
            return order_blocks
        
        trend, bos_price = bos_result
        
        for i in range(len(self.candles) - 1, max(0, len(self.candles) - 10), -1):
            ob = OrderBlock(
                high=max(c.high for c in self.candles[max(0, i-4):i+1]),
                low=min(c.low for c in self.candles[max(0, i-4):i+1]),
                timestamp=self.candles[i].timestamp,
                trend_direction=trend
            )
            order_blocks.append(ob)
        
        self.order_blocks = order_blocks[-3:]
        return order_blocks
    
    def get_market_structure(self) -> TrendDirection:
        """Determine current market structure"""
        if len(self.candles) < 5 or not self.swing_highs or not self.swing_lows:
            return TrendDirection.RANGING
        
        uptrend_count = 0
        downtrend_count = 0
        
        for i in range(1, len(self.swing_highs)):
            if self.swing_highs[i][1] > self.swing_highs[i-1][1]:
                uptrend_count += 1
            else:
                downtrend_count += 1
        
        for i in range(1, len(self.swing_lows)):
            if self.swing_lows[i][1] > self.swing_lows[i-1][1]:
                uptrend_count += 1
            else:
                downtrend_count += 1
        
        if uptrend_count > downtrend_count:
            return TrendDirection.UP
        elif downtrend_count > uptrend_count:
            return TrendDirection.DOWN
        else:
            return TrendDirection.RANGING
