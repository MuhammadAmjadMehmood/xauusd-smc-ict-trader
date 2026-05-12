import logging
from typing import Tuple
from config import (
    ACCOUNT_BALANCE,
    RISK_PERCENT_PER_TRADE,
    MIN_POSITION_SIZE,
    MAX_POSITION_SIZE,
    MIN_RISK_REWARD
)

logger = logging.getLogger(__name__)

class RiskManager:
    """Professional Risk Management System"""
    
    def __init__(self, account_balance: float = ACCOUNT_BALANCE, risk_percent: float = RISK_PERCENT_PER_TRADE):
        self.account_balance = account_balance
        self.risk_percent_per_trade = risk_percent
        self.risk_per_trade = account_balance * (risk_percent / 100)
        self.open_trades = 0
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        min_size: float = MIN_POSITION_SIZE,
        max_size: float = MAX_POSITION_SIZE
    ) -> float:
        """
        Calculate position size based on risk
        
        Formula:
        Risk Amount = Account Balance × Risk % per Trade
        Risk Distance = Entry - Stop Loss
        Position Size = Risk Amount / (Risk Distance × Contract Multiplier)
        
        For XAUUSD: 1 lot = 100 troy ounces
        Price move of $1 = $100 profit/loss per lot
        """
        risk_distance = abs(entry_price - stop_loss_price)
        
        if risk_distance == 0:
            return min_size
        
        contract_multiplier = 100  # XAUUSD: 1 lot = 100 oz
        
        position_size = self.risk_per_trade / (risk_distance * contract_multiplier)
        
        # Clamp between min and max
        position_size = max(min_size, min(position_size, max_size))
        
        logger.info(f"Position Size Calculated: {position_size:.3f} lots | Risk Distance: ${risk_distance:.2f} | Risk Amount: ${self.risk_per_trade:.2f}")
        
        return position_size
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_reward_ratio: float = 2.0,
        round_to: int = 2
    ) -> Tuple[float, float]:
        """
        Calculate take profit based on risk-reward ratio
        
        Formula:
        RR Ratio = Profit / Loss
        TP = Entry ± (Entry - SL) × RR Ratio
        
        Returns: (take_profit, actual_rr_ratio)
        """
        risk_distance = abs(entry_price - stop_loss_price)
        
        if entry_price > stop_loss_price:  # Long trade
            take_profit = entry_price + (risk_distance * risk_reward_ratio)
        else:  # Short trade
            take_profit = entry_price - (risk_distance * risk_reward_ratio)
        
        take_profit = round(take_profit, round_to)
        
        # Calculate actual RR ratio
        profit = abs(take_profit - entry_price)
        actual_rr = profit / risk_distance if risk_distance > 0 else 0
        
        logger.info(f"Take Profit Calculated: ${take_profit:.2f} | Target RR: 1:{risk_reward_ratio:.2f}")
        
        return take_profit, actual_rr
    
    def validate_setup(
        self,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        position_size: float
    ) -> Tuple[bool, str]:
        """
        Validate trade setup against risk rules
        
        Returns: (is_valid, message)
        """
        # Check position size limits
        if position_size < MIN_POSITION_SIZE:
            return False, f"Position size {position_size:.3f} is below minimum {MIN_POSITION_SIZE}"
        
        if position_size > MAX_POSITION_SIZE:
            return False, f"Position size {position_size:.3f} exceeds maximum {MAX_POSITION_SIZE}"
        
        # Check stop loss is set and different from entry
        if stop_loss_price == entry_price:
            return False, "Stop loss cannot equal entry price"
        
        # Check take profit is set and on correct side
        if entry_price > stop_loss_price:  # Long
            if take_profit_price <= entry_price:
                return False, "Take profit must be above entry for long trades"
        else:  # Short
            if take_profit_price >= entry_price:
                return False, "Take profit must be below entry for short trades"
        
        # Check risk-reward ratio
        risk_distance = abs(entry_price - stop_loss_price)
        profit_distance = abs(take_profit_price - entry_price)
        rr_ratio = profit_distance / risk_distance if risk_distance > 0 else 0
        
        if rr_ratio < MIN_RISK_REWARD:
            return False, f"Risk/Reward ratio {rr_ratio:.2f} is below minimum {MIN_RISK_REWARD}"
        
        return True, "Setup is valid"
    
    def calculate_account_impact(self, position_size: float) -> float:
        """
        Calculate what % of account this position risks
        """
        return (position_size * 100) / self.account_balance
    
    def update_account_balance(self, pnl: float):
        """
        Update account balance after trade close
        """
        self.account_balance += pnl
        self.risk_per_trade = self.account_balance * (self.risk_percent_per_trade / 100)
        logger.info(f"Account updated: ${self.account_balance:.2f} | New risk per trade: ${self.risk_per_trade:.2f}")
