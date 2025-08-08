import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataHandler:
    """Handles data fetching and processing from Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        
    def get_data(self, symbol, start_date, end_date, interval='1d'):
        """
        Fetch stock data from Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval ('1d', '1wk', '1mo')
            
        Returns:
            DataFrame: OHLCV data
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"
        
        # Check cache first
        if cache_key in self.cache:
            logger.info(f"Returning cached data for {symbol}")
            return self.cache[cache_key].copy()
        
        try:
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch data
            data = ticker.history(
                start=start_date,
                end=end_date + timedelta(days=1),  # Add one day to include end_date
                interval=interval,
                auto_adjust=True,
                prepost=False
            )
            
            if data.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()
            
            # Clean data
            data = self._clean_data(data)
            
            # Cache the data
            self.cache[cache_key] = data.copy()
            
            logger.info(f"Successfully fetched {len(data)} rows for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
    
    def _clean_data(self, data):
        """
        Clean and validate the fetched data
        
        Args:
            data: Raw DataFrame from yfinance
            
        Returns:
            DataFrame: Cleaned data
        """
        try:
            # Remove any rows with NaN values
            data = data.dropna()
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Remove any rows where OHLC values are zero or negative
            data = data[
                (data['Open'] > 0) & 
                (data['High'] > 0) & 
                (data['Low'] > 0) & 
                (data['Close'] > 0)
            ]
            
            # Ensure High >= Low and High >= Open, Close and Low <= Open, Close
            data = data[
                (data['High'] >= data['Low']) &
                (data['High'] >= data['Open']) &
                (data['High'] >= data['Close']) &
                (data['Low'] <= data['Open']) &
                (data['Low'] <= data['Close'])
            ]
            
            # Sort by date
            data = data.sort_index()
            
            logger.info(f"Data cleaned: {len(data)} valid rows remaining")
            return data
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            raise
    
    def get_symbol_info(self, symbol):
        """
        Get basic information about a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            dict: Symbol information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'longName': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'marketCap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD')
            }
            
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return {
                'symbol': symbol,
                'longName': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'marketCap': 0,
                'currency': 'USD'
            }
    
    def validate_symbol(self, symbol):
        """
        Validate if a symbol exists and has data
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            bool: True if symbol is valid
        """
        try:
            ticker = yf.Ticker(symbol)
            # Try to get recent data (last 5 days)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=5)
            
            data = ticker.history(start=start_date, end=end_date, period="5d")
            return not data.empty
            
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False
    
    def get_available_symbols(self):
        """
        Get a list of popular/available symbols for testing
        
        Returns:
            list: List of symbol dictionaries
        """
        popular_symbols = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
            {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.'},
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson'},
            {'symbol': 'V', 'name': 'Visa Inc.'},
            {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF'},
            {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust'}
        ]
        
        return popular_symbols
