import logging

logger = logging.getLogger(__name__)

class Portfolio:
    """Portfolio management class for tracking positions and cash"""
    
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.shares = 0
        self.total_bought = 0
        self.total_sold = 0
        self.transactions = []
        
    def buy(self, shares, total_cost):
        """
        Execute a buy order
        
        Args:
            shares: Number of shares to buy
            total_cost: Total cost including commissions
        """
        if total_cost > self.cash:
            raise ValueError(f"Insufficient cash: need ${total_cost:.2f}, have ${self.cash:.2f}")
        
        self.cash -= total_cost
        self.shares += shares
        self.total_bought += total_cost
        
        self.transactions.append({
            'action': 'BUY',
            'shares': shares,
            'cost': total_cost,
            'price_per_share': total_cost / shares if shares > 0 else 0
        })
        
        logger.debug(f"Bought {shares} shares for ${total_cost:.2f}. "
                    f"Cash: ${self.cash:.2f}, Shares: {self.shares}")
    
    def sell(self, shares, total_revenue):
        """
        Execute a sell order
        
        Args:
            shares: Number of shares to sell
            total_revenue: Total revenue after commissions
        """
        if shares > self.shares:
            raise ValueError(f"Insufficient shares: trying to sell {shares}, have {self.shares}")
        
        self.cash += total_revenue
        self.shares -= shares
        self.total_sold += total_revenue
        
        self.transactions.append({
            'action': 'SELL',
            'shares': shares,
            'revenue': total_revenue,
            'price_per_share': total_revenue / shares if shares > 0 else 0
        })
        
        logger.debug(f"Sold {shares} shares for ${total_revenue:.2f}. "
                    f"Cash: ${self.cash:.2f}, Shares: {self.shares}")
    
    def get_current_value(self, current_price):
        """
        Calculate current portfolio value
        
        Args:
            current_price: Current stock price
            
        Returns:
            float: Total portfolio value
        """
        return self.cash + (self.shares * current_price)
    
    def get_total_return(self, current_price):
        """
        Calculate total return percentage
        
        Args:
            current_price: Current stock price
            
        Returns:
            float: Total return percentage
        """
        current_value = self.get_current_value(current_price)
        return ((current_value - self.initial_capital) / self.initial_capital) * 100
    
    def get_realized_pnl(self):
        """
        Calculate realized profit/loss from closed positions
        
        Returns:
            float: Realized P&L
        """
        return self.total_sold - self.total_bought
    
    def get_unrealized_pnl(self, current_price):
        """
        Calculate unrealized profit/loss from open positions
        
        Args:
            current_price: Current stock price
            
        Returns:
            float: Unrealized P&L
        """
        if self.shares == 0:
            return 0
        
        current_value = self.shares * current_price
        # Calculate average cost basis
        if len(self.transactions) > 0:
            buy_transactions = [t for t in self.transactions if t['action'] == 'BUY']
            if buy_transactions:
                total_cost = sum(t['cost'] for t in buy_transactions)
                total_shares = sum(t['shares'] for t in buy_transactions)
                avg_cost = total_cost / total_shares if total_shares > 0 else 0
                cost_basis = self.shares * avg_cost
                return current_value - cost_basis
        
        return 0
    
    def get_summary(self, current_price):
        """
        Get portfolio summary
        
        Args:
            current_price: Current stock price
            
        Returns:
            dict: Portfolio summary
        """
        current_value = self.get_current_value(current_price)
        total_return = self.get_total_return(current_price)
        realized_pnl = self.get_realized_pnl()
        unrealized_pnl = self.get_unrealized_pnl(current_price)
        
        return {
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'shares': self.shares,
            'current_value': current_value,
            'total_return_pct': total_return,
            'total_return_dollar': current_value - self.initial_capital,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': realized_pnl + unrealized_pnl,
            'total_transactions': len(self.transactions)
        }
