import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BaseStrategy:
    """Base class for all trading strategies"""
    
    def __init__(self, name="Base Strategy"):
        self.name = name
    
    def generate_signals(self, data):
        """
        Generate trading signals based on strategy logic
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame: DataFrame with signal column (1=buy, -1=sell, 0=hold)
        """
        raise NotImplementedError("Subclasses must implement generate_signals method")

class MovingAverageCrossover(BaseStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, short_window=10, long_window=30):
        super().__init__(f"MA Crossover ({short_window}/{long_window})")
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signals(self, data):
        """
        Generate signals based on moving average crossover
        Buy when short MA crosses above long MA
        Sell when short MA crosses below long MA
        """
        try:
            signals = pd.DataFrame(index=data.index)
            signals['price'] = data['Close']
            
            # Calculate moving averages
            signals['short_ma'] = data['Close'].rolling(window=self.short_window).mean()
            signals['long_ma'] = data['Close'].rolling(window=self.long_window).mean()
            
            # Generate signals
            signals['signal'] = 0
            
            # Buy signal: short MA crosses above long MA
            signals['signal'][self.short_window:] = np.where(
                signals['short_ma'][self.short_window:] > signals['long_ma'][self.short_window:], 1, 0
            )
            
            # Generate trading positions (difference to get crossover points)
            signals['positions'] = signals['signal'].diff()
            
            # Convert positions to buy/sell signals
            signals['signal'] = 0
            signals.loc[signals['positions'] == 1, 'signal'] = 1   # Buy
            signals.loc[signals['positions'] == -1, 'signal'] = -1 # Sell
            
            logger.info(f"Generated {(signals['signal'] != 0).sum()} signals for MA Crossover strategy")
            
            return signals[['signal']]
            
        except Exception as e:
            logger.error(f"Error generating MA crossover signals: {e}")
            raise

class MeanReversion(BaseStrategy):
    """Mean Reversion Strategy using Bollinger Bands"""
    
    def __init__(self, window=20, std_dev=2.0):
        super().__init__(f"Mean Reversion ({window}, {std_dev})")
        self.window = window
        self.std_dev = std_dev
        
    def generate_signals(self, data):
        """
        Generate signals based on mean reversion using Bollinger Bands
        Buy when price touches lower band
        Sell when price touches upper band
        """
        try:
            signals = pd.DataFrame(index=data.index)
            signals['price'] = data['Close']
            
            # Calculate Bollinger Bands
            signals['sma'] = data['Close'].rolling(window=self.window).mean()
            signals['std'] = data['Close'].rolling(window=self.window).std()
            signals['upper_band'] = signals['sma'] + (signals['std'] * self.std_dev)
            signals['lower_band'] = signals['sma'] - (signals['std'] * self.std_dev)
            
            # Generate signals
            signals['signal'] = 0
            
            # Buy when price touches or goes below lower band
            buy_condition = signals['price'] <= signals['lower_band']
            
            # Sell when price touches or goes above upper band
            sell_condition = signals['price'] >= signals['upper_band']
            
            signals.loc[buy_condition, 'signal'] = 1
            signals.loc[sell_condition, 'signal'] = -1
            
            # Remove consecutive duplicate signals
            signals['prev_signal'] = signals['signal'].shift(1)
            signals.loc[(signals['signal'] == signals['prev_signal']) & (signals['signal'] != 0), 'signal'] = 0
            
            logger.info(f"Generated {(signals['signal'] != 0).sum()} signals for Mean Reversion strategy")
            
            return signals[['signal']]
            
        except Exception as e:
            logger.error(f"Error generating mean reversion signals: {e}")
            raise

class BuyAndHold(BaseStrategy):
    """Simple Buy and Hold Strategy"""
    
    def __init__(self):
        super().__init__("Buy and Hold")
        
    def generate_signals(self, data):
        """
        Generate buy signal on first day, hold until end
        """
        try:
            signals = pd.DataFrame(index=data.index)
            signals['signal'] = 0
            
            # Buy on first available day
            signals.iloc[0, signals.columns.get_loc('signal')] = 1
            
            logger.info("Generated Buy and Hold signals")
            
            return signals[['signal']]
            
        except Exception as e:
            logger.error(f"Error generating buy and hold signals: {e}")
            raise

class MomentumStrategy(BaseStrategy):
    """Momentum Strategy based on price momentum"""
    
    def __init__(self, lookback=10, threshold=0.02):
        super().__init__(f"Momentum ({lookback}, {threshold})")
        self.lookback = lookback
        self.threshold = threshold
        
    def generate_signals(self, data):
        """
        Generate signals based on price momentum
        Buy when momentum is positive above threshold
        Sell when momentum turns negative
        """
        try:
            signals = pd.DataFrame(index=data.index)
            signals['price'] = data['Close']
            
            # Calculate momentum (percentage change over lookback period)
            signals['momentum'] = signals['price'].pct_change(self.lookback)
            
            # Generate signals
            signals['signal'] = 0
            
            # Buy when momentum is above threshold
            buy_condition = signals['momentum'] > self.threshold
            
            # Sell when momentum turns negative
            sell_condition = signals['momentum'] < 0
            
            signals.loc[buy_condition, 'signal'] = 1
            signals.loc[sell_condition, 'signal'] = -1
            
            # Remove consecutive duplicate signals
            signals['prev_signal'] = signals['signal'].shift(1)
            signals.loc[(signals['signal'] == signals['prev_signal']) & (signals['signal'] != 0), 'signal'] = 0
            
            logger.info(f"Generated {(signals['signal'] != 0).sum()} signals for Momentum strategy")
            
            return signals[['signal']]
            
        except Exception as e:
            logger.error(f"Error generating momentum signals: {e}")
            raise
