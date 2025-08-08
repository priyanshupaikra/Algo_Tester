import pandas as pd
import numpy as np
from portfolio import Portfolio
from metrics import calculate_metrics
import logging

logger = logging.getLogger(__name__)

class BacktestEngine:
    """Core backtesting engine"""
    
    def __init__(self, initial_capital=10000, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission  # 0.1% commission per trade
        
    def run_backtest(self, data, strategy):
        """
        Run backtest on given data with specified strategy
        
        Args:
            data: DataFrame with OHLCV data
            strategy: Strategy object with generate_signals method
            
        Returns:
            dict: Backtest results including metrics and trades
        """
        try:
            # Generate trading signals
            signals = strategy.generate_signals(data)
            
            # Initialize portfolio
            portfolio = Portfolio(self.initial_capital)
            
            # Track trades and portfolio values
            trades = []
            portfolio_values = []
            
            position = 0  # 0 = no position, 1 = long position
            
            for i in range(len(signals)):
                date = signals.index[i]
                signal = signals.iloc[i]['signal']
                price = data.loc[date, 'Close']
                
                # Execute trades based on signals
                if signal == 1 and position == 0:  # Buy signal and no position
                    # Calculate shares to buy (use all available cash)
                    shares = int(portfolio.cash / (price * (1 + self.commission)))
                    if shares > 0:
                        cost = shares * price * (1 + self.commission)
                        portfolio.buy(shares, cost)
                        
                        trades.append({
                            'date': date.date(),
                            'action': 'BUY',
                            'price': price,
                            'quantity': shares,
                            'value': cost
                        })
                        position = 1
                        
                elif signal == -1 and position == 1:  # Sell signal and have position
                    # Sell all shares
                    shares = portfolio.shares
                    if shares > 0:
                        revenue = shares * price * (1 - self.commission)
                        portfolio.sell(shares, revenue)
                        
                        trades.append({
                            'date': date.date(),
                            'action': 'SELL',
                            'price': price,
                            'quantity': shares,
                            'value': revenue
                        })
                        position = 0
                
                # Calculate current portfolio value
                current_value = portfolio.cash + (portfolio.shares * price)
                portfolio_values.append({
                    'date': date,
                    'value': current_value
                })
            
            # Final portfolio value
            final_price = data['Close'].iloc[-1]
            final_value = portfolio.cash + (portfolio.shares * final_price)
            
            # Calculate metrics
            portfolio_df = pd.DataFrame(portfolio_values)
            portfolio_df.set_index('date', inplace=True)
            
            metrics = calculate_metrics(
                portfolio_df['value'], 
                self.initial_capital,
                data['Close']
            )
            
            # Compile results
            result = {
                'initial_capital': self.initial_capital,
                'final_value': final_value,
                'total_return': ((final_value - self.initial_capital) / self.initial_capital) * 100,
                'trades': trades,
                'portfolio_values': portfolio_values,
                **metrics
            }
            
            logger.info(f"Backtest completed: {len(trades)} trades, "
                       f"{result['total_return']:.2f}% return")
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest execution error: {e}")
            raise

class Order:
    """Represents a trading order"""
    
    def __init__(self, action, quantity, price, date):
        self.action = action  # 'BUY' or 'SELL'
        self.quantity = quantity
        self.price = price
        self.date = date
        self.executed = False
        
    def execute(self):
        """Mark order as executed"""
        self.executed = True
        return {
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'date': self.date,
            'value': self.quantity * self.price
        }
