# Algo Tester Overview

This is an algorithmic trading backtester web application built with Flask that allows users to test trading strategies against historical stock data. The system fetches real-time market data from Yahoo Finance, executes various trading strategies (Moving Average Crossover and Mean Reversion), and provides comprehensive performance analytics with interactive visualizations.

The application enables traders and analysts to validate their trading strategies before deploying them in live markets, offering detailed metrics like Sharpe ratio, maximum drawdown, total returns, and trade-by-trade analysis.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask**: Core web framework handling HTTP requests and responses
- **SQLAlchemy**: ORM for database operations with declarative models
- **Jinja2 Templates**: Server-side templating for dynamic HTML generation
- **Werkzeug ProxyFix**: Middleware for proper handling of proxy headers in production

## Frontend Architecture
- **Tailwind CSS + Bootstrap**: Hybrid CSS framework approach for responsive design
- **Plotly.js**: Interactive charting library for financial data visualization
- **Vanilla JavaScript**: Custom client-side logic for form validation and UI interactions
- **Font Awesome**: Icon library for consistent UI elements

## Backend Architecture
- **Modular Strategy Pattern**: Base strategy class with concrete implementations (MovingAverageCrossover, MeanReversion)
- **Portfolio Management**: Dedicated Portfolio class for tracking positions, cash, and transactions
- **Backtesting Engine**: Core BacktestEngine class orchestrating strategy execution and performance calculation
- **Data Handler**: Centralized DataHandler class with caching for efficient market data retrieval

## Database Design
- **SQLAlchemy Models**: 
  - BacktestResult: Stores backtest metadata and key performance metrics
  - Trade: Stores individual trade records with foreign key relationship
- **JSON Parameter Storage**: Strategy parameters serialized as JSON for flexibility
- **Automatic Schema Creation**: Database tables created automatically on app startup

## Data Processing Pipeline
- **Yahoo Finance Integration**: Real-time historical data fetching via yfinance library
- **Pandas DataFrames**: Core data structure for time series analysis and manipulation
- **NumPy**: Numerical computations for performance metrics calculations
- **In-Memory Caching**: Simple dictionary-based cache to reduce API calls

## Performance Metrics System
- **Comprehensive Analytics**: Total return, annualized return, Sharpe ratio, maximum drawdown, Calmar ratio
- **Risk-Free Rate**: Configurable assumption (default 2%) for Sharpe ratio calculations
- **Benchmark Comparison**: Optional benchmark performance comparison capabilities

# External Dependencies

## Market Data Services
- **Yahoo Finance API**: Primary data source via yfinance Python library for historical OHLCV data
- **Multiple Timeframes**: Support for daily, weekly, and monthly intervals

## Python Libraries
- **Flask Ecosystem**: flask, flask-sqlalchemy for web framework and database ORM
- **Data Science Stack**: pandas, numpy for data manipulation and numerical computations
- **Financial Data**: yfinance for market data retrieval with built-in error handling

## Frontend Dependencies
- **CDN-Based Assets**: 
  - Tailwind CSS for utility-first styling
  - Bootstrap 5 for additional UI components
  - Plotly.js for interactive financial charts
  - Font Awesome for iconography

## Database
- **SQLite**: Default database for development with support for PostgreSQL via DATABASE_URL environment variable
- **Connection Pooling**: Configured with pool recycling and pre-ping for production reliability

## Environment Configuration
- **Environment Variables**: DATABASE_URL for database connection, SESSION_SECRET for Flask sessions
- **Development Defaults**: Fallback configurations for local development environment

## Some Images of the Application
(images/my-image.png)
