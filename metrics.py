import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_metrics(portfolio_values, initial_capital, benchmark_prices=None):
    """
    Calculate comprehensive performance metrics
    
    Args:
        portfolio_values: Series of portfolio values over time
        initial_capital: Initial investment amount
        benchmark_prices: Series of benchmark prices (optional)
        
    Returns:
        dict: Dictionary of calculated metrics
    """
    try:
        if len(portfolio_values) == 0:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'calmar_ratio': 0
            }
        
        # Calculate returns
        returns = portfolio_values.pct_change().dropna()
        
        # Total return
        total_return = ((portfolio_values.iloc[-1] - initial_capital) / initial_capital) * 100
        
        # Annualized return
        trading_days = len(portfolio_values)
        years = trading_days / 252  # Approximate trading days per year
        if years > 0:
            annualized_return = (((portfolio_values.iloc[-1] / initial_capital) ** (1/years)) - 1) * 100
        else:
            annualized_return = 0
        
        # Volatility (annualized)
        if len(returns) > 1:
            volatility = returns.std() * np.sqrt(252) * 100
        else:
            volatility = 0
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        if volatility > 0:
            excess_return = (annualized_return / 100) - risk_free_rate
            sharpe_ratio = excess_return / (volatility / 100)
        else:
            sharpe_ratio = 0
        
        # Maximum drawdown
        max_drawdown = calculate_max_drawdown(portfolio_values)
        
        # Calmar ratio
        if max_drawdown != 0:
            calmar_ratio = (annualized_return / 100) / abs(max_drawdown / 100)
        else:
            calmar_ratio = 0
        
        # Win rate (if we have benchmark)
        win_rate = 0
        if benchmark_prices is not None and len(benchmark_prices) == len(portfolio_values):
            benchmark_returns = benchmark_prices.pct_change().dropna()
            if len(returns) == len(benchmark_returns):
                outperform_days = (returns > benchmark_returns).sum()
                win_rate = (outperform_days / len(returns)) * 100
        
        # Beta (if we have benchmark)
        beta = 0
        if benchmark_prices is not None and len(benchmark_prices) == len(portfolio_values):
            benchmark_returns = benchmark_prices.pct_change().dropna()
            if len(returns) == len(benchmark_returns) and len(returns) > 1:
                covariance = np.cov(returns, benchmark_returns)[0][1]
                benchmark_variance = np.var(benchmark_returns)
                if benchmark_variance > 0:
                    beta = covariance / benchmark_variance
        
        metrics = {
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'volatility': round(volatility, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'calmar_ratio': round(calmar_ratio, 2),
            'win_rate': round(win_rate, 2),
            'beta': round(beta, 2)
        }
        
        logger.info(f"Calculated metrics: Sharpe={sharpe_ratio:.2f}, MaxDD={max_drawdown:.2f}%")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            'total_return': 0,
            'annualized_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'calmar_ratio': 0,
            'win_rate': 0,
            'beta': 0
        }

def calculate_max_drawdown(portfolio_values):
    """
    Calculate maximum drawdown
    
    Args:
        portfolio_values: Series of portfolio values
        
    Returns:
        float: Maximum drawdown percentage
    """
    try:
        if len(portfolio_values) == 0:
            return 0
        
        # Calculate running maximum (peak)
        peak = portfolio_values.expanding().max()
        
        # Calculate drawdown
        drawdown = (portfolio_values - peak) / peak * 100
        
        # Return maximum drawdown (most negative value)
        max_dd = drawdown.min()
        
        return max_dd if not np.isnan(max_dd) else 0
        
    except Exception as e:
        logger.error(f"Error calculating max drawdown: {e}")
        return 0

def calculate_var(returns, confidence_level=0.05):
    """
    Calculate Value at Risk (VaR)
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level (default 5%)
        
    Returns:
        float: VaR value
    """
    try:
        if len(returns) == 0:
            return 0
        
        return np.percentile(returns, confidence_level * 100)
        
    except Exception as e:
        logger.error(f"Error calculating VaR: {e}")
        return 0

def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    """
    Calculate Sortino ratio (using downside deviation instead of total volatility)
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (annual)
        
    Returns:
        float: Sortino ratio
    """
    try:
        if len(returns) == 0:
            return 0
        
        # Convert to daily risk-free rate
        daily_rf = risk_free_rate / 252
        
        # Calculate excess returns
        excess_returns = returns - daily_rf
        
        # Calculate mean excess return
        mean_excess = excess_returns.mean()
        
        # Calculate downside deviation (only negative returns)
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) > 0:
            downside_deviation = downside_returns.std()
            if downside_deviation > 0:
                sortino = (mean_excess * np.sqrt(252)) / (downside_deviation * np.sqrt(252))
                return sortino
        
        return 0
        
    except Exception as e:
        logger.error(f"Error calculating Sortino ratio: {e}")
        return 0

def calculate_information_ratio(portfolio_returns, benchmark_returns):
    """
    Calculate Information Ratio
    
    Args:
        portfolio_returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns
        
    Returns:
        float: Information ratio
    """
    try:
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) == 0:
            return 0
        
        # Calculate tracking error (active returns)
        active_returns = portfolio_returns - benchmark_returns
        
        # Calculate mean active return and tracking error
        mean_active_return = active_returns.mean()
        tracking_error = active_returns.std()
        
        if tracking_error > 0:
            information_ratio = (mean_active_return * np.sqrt(252)) / (tracking_error * np.sqrt(252))
            return information_ratio
        
        return 0
        
    except Exception as e:
        logger.error(f"Error calculating Information Ratio: {e}")
        return 0
