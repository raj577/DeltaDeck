# Option spreads analysis engine
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from enum import Enum
import asyncio
from logzero import logger

class OptionType(str, Enum):
    CALL = "CE"
    PUT = "PE"

class SpreadType(str, Enum):
    BULL_CALL = "Bull Call Spread"
    BEAR_PUT = "Bear Put Spread"

class OptionContract(BaseModel):
    """Data model for individual option contracts"""
    strike: float
    premium: float
    delta: float
    gamma: float
    theta: float
    vega: float
    implied_volatility: float
    volume: int
    option_type: OptionType
    expiry: str
    symbol: str

class SpreadRecommendation(BaseModel):
    """Data model for spread recommendations"""
    type: SpreadType
    symbol: str
    expiry: str
    
    # Buy leg details
    buy_strike: float
    buy_premium: float
    buy_delta: float
    
    # Sell leg details  
    sell_strike: float
    sell_premium: float
    sell_delta: float
    
    # Spread metrics
    delta_difference: float  # buy_delta - sell_delta
    net_premium: float       # buy_premium - sell_premium (debit)
    max_profit: float        # (strike_diff - net_premium) * lot_size
    max_loss: float          # net_premium * lot_size
    breakeven: float         # buy_strike + net_premium (for calls)
    
    # P&L per 100 points movement
    profit_per_100_up: float    # If underlying moves up 100 points
    profit_per_100_down: float  # If underlying moves down 100 points
    
    # Risk metrics
    risk_reward_ratio: float    # max_profit / max_loss
    probability_profit: float   # Estimated based on delta
    
    # Liquidity
    total_volume: int          # buy_volume + sell_volume

class SpreadAnalyzer:
    """Main analysis engine for option spreads"""
    
    def __init__(self):
        # Lot sizes for different symbols
        self.lot_sizes = {
            "NIFTY": 75,
            "BANKNIFTY": 35
        }
        
        # Delta difference range for spreads
        self.min_delta_diff = 0.15
        self.max_delta_diff = 0.26
    
    def parse_angel_option_data(self, angel_data: List[Dict], symbol: str) -> List[OptionContract]:
        """Convert Angel One API data to OptionContract objects"""
        options = []
        
        for opt in angel_data:
            try:
                option = OptionContract(
                    strike=float(opt['strikePrice']),
                    premium=0.0,  # Angel One doesn't provide premium in Greeks API
                    delta=abs(float(opt['delta'])),  # Use absolute value for comparison
                    gamma=float(opt['gamma']),
                    theta=float(opt['theta']),
                    vega=float(opt['vega']),
                    implied_volatility=float(opt['impliedVolatility']),
                    volume=int(float(opt['tradeVolume'])),
                    option_type=OptionType.CALL if opt['optionType'] == 'CE' else OptionType.PUT,
                    expiry=opt['expiry'],
                    symbol=symbol
                )
                options.append(option)
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid option data: {e}")
                continue
        
        return options
    
    def find_atm_strike(self, options: List[OptionContract], current_price: float) -> float:
        """Find the ATM (At The Money) strike closest to current price"""
        if not options:
            return current_price
        
        # Find the strike closest to current price
        closest_strike = min(options, key=lambda x: abs(x.strike - current_price))
        return closest_strike.strike
    
    def calculate_bull_call_spreads(self, calls: List[OptionContract], current_price: float) -> List[SpreadRecommendation]:
        """Calculate Bull Call Spread recommendations"""
        spreads = []
        atm_strike = self.find_atm_strike(calls, current_price)
        lot_size = self.lot_sizes.get(calls[0].symbol, 50)
        
        # Find ATM call as buy leg
        atm_calls = [c for c in calls if c.strike == atm_strike]
        if not atm_calls:
            return spreads
        
        buy_call = atm_calls[0]
        
        # Find OTM calls as sell leg with proper delta difference
        for sell_call in calls:
            if (sell_call.strike > buy_call.strike and  # OTM
                sell_call.option_type == OptionType.CALL):
                
                delta_diff = buy_call.delta - sell_call.delta
                
                # Check if delta difference is in our target range
                if self.min_delta_diff <= delta_diff <= self.max_delta_diff:
                    
                    # Calculate spread metrics
                    strike_diff = sell_call.strike - buy_call.strike
                    net_premium = 50.0  # Estimated net debit (would need LTP data)
                    
                    max_profit = (strike_diff - net_premium) * lot_size
                    max_loss = net_premium * lot_size
                    breakeven = buy_call.strike + net_premium
                    
                    # P&L per 100 points movement (based on delta)
                    profit_per_100_up = (buy_call.delta - sell_call.delta) * 100 * lot_size
                    profit_per_100_down = -(buy_call.delta - sell_call.delta) * 100 * lot_size
                    
                    spread = SpreadRecommendation(
                        type=SpreadType.BULL_CALL,
                        symbol=buy_call.symbol,
                        expiry=buy_call.expiry,
                        
                        buy_strike=buy_call.strike,
                        buy_premium=net_premium,  # Estimated
                        buy_delta=buy_call.delta,
                        
                        sell_strike=sell_call.strike,
                        sell_premium=net_premium * 0.6,  # Estimated
                        sell_delta=sell_call.delta,
                        
                        delta_difference=delta_diff,
                        net_premium=net_premium,
                        max_profit=max_profit,
                        max_loss=max_loss,
                        breakeven=breakeven,
                        
                        profit_per_100_up=profit_per_100_up,
                        profit_per_100_down=profit_per_100_down,
                        
                        risk_reward_ratio=max_profit / max_loss if max_loss > 0 else 0,
                        probability_profit=buy_call.delta * 100,  # Rough estimate
                        
                        total_volume=buy_call.volume + sell_call.volume
                    )
                    
                    spreads.append(spread)
        
        return spreads
    
    def calculate_bear_put_spreads(self, puts: List[OptionContract], current_price: float) -> List[SpreadRecommendation]:
        """Calculate Bear Put Spread recommendations"""
        spreads = []
        atm_strike = self.find_atm_strike(puts, current_price)
        lot_size = self.lot_sizes.get(puts[0].symbol, 50)
        
        # Find ATM put as buy leg
        atm_puts = [p for p in puts if p.strike == atm_strike]
        if not atm_puts:
            return spreads
        
        buy_put = atm_puts[0]
        
        # Find OTM puts as sell leg with proper delta difference
        for sell_put in puts:
            if (sell_put.strike < buy_put.strike and  # OTM
                sell_put.option_type == OptionType.PUT):
                
                # For puts, both deltas are negative, so we need absolute difference
                delta_diff = abs(buy_put.delta) - abs(sell_put.delta)
                
                # Check if delta difference is in our target range
                if self.min_delta_diff <= delta_diff <= self.max_delta_diff:
                    
                    # Calculate spread metrics
                    strike_diff = buy_put.strike - sell_put.strike
                    net_premium = 50.0  # Estimated net debit
                    
                    max_profit = (strike_diff - net_premium) * lot_size
                    max_loss = net_premium * lot_size
                    breakeven = buy_put.strike - net_premium
                    
                    # P&L per 100 points movement (based on delta)
                    profit_per_100_up = -(buy_put.delta - sell_put.delta) * 100 * lot_size
                    profit_per_100_down = (buy_put.delta - sell_put.delta) * 100 * lot_size
                    
                    spread = SpreadRecommendation(
                        type=SpreadType.BEAR_PUT,
                        symbol=buy_put.symbol,
                        expiry=buy_put.expiry,
                        
                        buy_strike=buy_put.strike,
                        buy_premium=net_premium,
                        buy_delta=buy_put.delta,
                        
                        sell_strike=sell_put.strike,
                        sell_premium=net_premium * 0.6,
                        sell_delta=sell_put.delta,
                        
                        delta_difference=delta_diff,
                        net_premium=net_premium,
                        max_profit=max_profit,
                        max_loss=max_loss,
                        breakeven=breakeven,
                        
                        profit_per_100_up=profit_per_100_up,
                        profit_per_100_down=profit_per_100_down,
                        
                        risk_reward_ratio=max_profit / max_loss if max_loss > 0 else 0,
                        probability_profit=abs(buy_put.delta) * 100,
                        
                        total_volume=buy_put.volume + sell_put.volume
                    )
                    
                    spreads.append(spread)
        
        return spreads
    
    def analyze_spreads(self, angel_data: List[Dict], symbol: str, current_price: float) -> List[SpreadRecommendation]:
        """Main method to analyze and return spread recommendations"""
        
        # Parse Angel One data
        options = self.parse_angel_option_data(angel_data, symbol)
        
        if not options:
            logger.warning(f"No valid options data for {symbol}")
            return []
        
        # Separate calls and puts
        calls = [opt for opt in options if opt.option_type == OptionType.CALL]
        puts = [opt for opt in options if opt.option_type == OptionType.PUT]
        
        logger.info(f"Analyzing {len(calls)} calls and {len(puts)} puts for {symbol}")
        
        # Debug: Print some delta values to understand the data
        if calls:
            logger.info(f"Sample call deltas for {symbol}: {[f'{c.strike}:{c.delta:.4f}' for c in calls[:5]]}")
        if puts:
            logger.info(f"Sample put deltas for {symbol}: {[f'{p.strike}:{p.delta:.4f}' for p in puts[:5]]}")
        
        # Calculate spreads
        all_spreads = []
        
        # Bull Call Spreads
        bull_call_spreads = self.calculate_bull_call_spreads(calls, current_price)
        all_spreads.extend(bull_call_spreads)
        
        # Bear Put Spreads  
        bear_put_spreads = self.calculate_bear_put_spreads(puts, current_price)
        all_spreads.extend(bear_put_spreads)
        
        # Sort by risk-reward ratio (best first)
        all_spreads.sort(key=lambda x: x.risk_reward_ratio, reverse=True)
        
        logger.info(f"Found {len(all_spreads)} spread opportunities for {symbol}")
        return all_spreads[:10]  # Return top 10 spreads