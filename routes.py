from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import BacktestResult, Trade
from backtester import BacktestEngine
from strategies import MovingAverageCrossover, MeanReversion
from data_handler import DataHandler
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard showing recent backtest results"""
    recent_results = BacktestResult.query.order_by(BacktestResult.created_at.desc()).limit(5).all()
    return render_template('index.html', results=recent_results)

@app.route('/strategy_config')
def strategy_config():
    """Strategy configuration page"""
    return render_template('strategy_config.html')

@app.route('/run_backtest', methods=['POST'])
def run_backtest():
    """Execute a backtest with given parameters"""
    try:
        # Get form data
        strategy_type = request.form.get('strategy_type')
        symbol = request.form.get('symbol', 'AAPL').upper()
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        initial_capital = float(request.form.get('initial_capital', 10000))
        
        # Strategy-specific parameters
        if strategy_type == 'ma_crossover':
            short_window = int(request.form.get('short_window', 10))
            long_window = int(request.form.get('long_window', 30))
            strategy = MovingAverageCrossover(short_window=short_window, long_window=long_window)
            strategy_name = f"MA Crossover ({short_window}/{long_window})"
            parameters = {'short_window': short_window, 'long_window': long_window}
        elif strategy_type == 'mean_reversion':
            window = int(request.form.get('window', 20))
            std_dev = float(request.form.get('std_dev', 2.0))
            strategy = MeanReversion(window=window, std_dev=std_dev)
            strategy_name = f"Mean Reversion ({window}, {std_dev})"
            parameters = {'window': window, 'std_dev': std_dev}
        else:
            flash('Invalid strategy type selected', 'error')
            return redirect(url_for('strategy_config'))
        
        # Get data
        data_handler = DataHandler()
        try:
            data = data_handler.get_data(symbol, start_date, end_date)
            if data.empty:
                flash(f'No data available for {symbol} in the specified date range', 'error')
                return redirect(url_for('strategy_config'))
        except Exception as e:
            logger.error(f"Data fetch error: {e}")
            flash(f'Error fetching data for {symbol}: {str(e)}', 'error')
            return redirect(url_for('strategy_config'))
        
        # Run backtest
        engine = BacktestEngine(initial_capital=initial_capital)
        result = engine.run_backtest(data, strategy)
        
        # Save result to database
        backtest_result = BacktestResult(
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            final_value=result['final_value'],
            total_return=result['total_return'],
            sharpe_ratio=result['sharpe_ratio'],
            max_drawdown=result['max_drawdown'],
            total_trades=len(result['trades'])
        )
        backtest_result.set_parameters(parameters)
        
        db.session.add(backtest_result)
        db.session.commit()
        
        # Save trades
        for trade_data in result['trades']:
            trade = Trade(
                backtest_id=backtest_result.id,
                date=trade_data['date'],
                action=trade_data['action'],
                price=trade_data['price'],
                quantity=trade_data['quantity'],
                value=trade_data['value']
            )
            db.session.add(trade)
        
        db.session.commit()
        
        flash('Backtest completed successfully!', 'success')
        return redirect(url_for('results', backtest_id=backtest_result.id))
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        flash(f'Error running backtest: {str(e)}', 'error')
        return redirect(url_for('strategy_config'))

@app.route('/results/<int:backtest_id>')
def results(backtest_id):
    """Display backtest results"""
    result = BacktestResult.query.get_or_404(backtest_id)
    trades = Trade.query.filter_by(backtest_id=backtest_id).order_by(Trade.date).all()
    
    # Get the original data for charting
    data_handler = DataHandler()
    try:
        data = data_handler.get_data(result.symbol, result.start_date, result.end_date)
        
        # Create price chart
        price_chart = create_price_chart(data, trades, result.symbol)
        price_chart_json = json.dumps(price_chart, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Create portfolio value chart
        portfolio_chart = create_portfolio_chart(trades, result.initial_capital)
        portfolio_chart_json = json.dumps(portfolio_chart, cls=plotly.utils.PlotlyJSONEncoder)
        
    except Exception as e:
        logger.error(f"Chart creation error: {e}")
        price_chart_json = None
        portfolio_chart_json = None
    
    return render_template('results.html', 
                         result=result, 
                         trades=trades,
                         price_chart=price_chart_json,
                         portfolio_chart=portfolio_chart_json)

def create_price_chart(data, trades, symbol):
    """Create price chart with buy/sell signals"""
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=f'{symbol} Price',
        line=dict(color='blue')
    ))
    
    # Add buy signals
    buy_trades = [t for t in trades if t.action == 'BUY']
    if buy_trades:
        buy_dates = [t.date for t in buy_trades]
        buy_prices = [t.price for t in buy_trades]
        fig.add_trace(go.Scatter(
            x=buy_dates,
            y=buy_prices,
            mode='markers',
            name='Buy Signals',
            marker=dict(color='green', size=10, symbol='triangle-up')
        ))
    
    # Add sell signals
    sell_trades = [t for t in trades if t.action == 'SELL']
    if sell_trades:
        sell_dates = [t.date for t in sell_trades]
        sell_prices = [t.price for t in sell_trades]
        fig.add_trace(go.Scatter(
            x=sell_dates,
            y=sell_prices,
            mode='markers',
            name='Sell Signals',
            marker=dict(color='red', size=10, symbol='triangle-down')
        ))
    
    fig.update_layout(
        title=f'{symbol} Price with Trading Signals',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        hovermode='x unified'
    )
    
    return fig

def create_portfolio_chart(trades, initial_capital):
    """Create portfolio value chart over time"""
    if not trades:
        return go.Figure()
    
    portfolio_values = []
    cash = initial_capital
    shares = 0
    dates = []
    
    for trade in trades:
        if trade.action == 'BUY':
            shares += trade.quantity
            cash -= trade.value
        else:  # SELL
            shares -= trade.quantity
            cash += trade.value
        
        portfolio_value = cash + (shares * trade.price)
        portfolio_values.append(portfolio_value)
        dates.append(trade.date)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='purple')
    ))
    
    # Add initial capital line
    fig.add_hline(y=initial_capital, line_dash="dash", line_color="gray", 
                  annotation_text="Initial Capital")
    
    fig.update_layout(
        title='Portfolio Value Over Time',
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)',
        hovermode='x unified'
    )
    
    return fig

@app.route('/api/validate_symbol/<symbol>')
def validate_symbol(symbol):
    """API endpoint to validate if a symbol exists"""
    try:
        data_handler = DataHandler()
        # Try to get just one day of data to validate
        test_data = data_handler.get_data(symbol.upper(), date.today(), date.today())
        return jsonify({'valid': not test_data.empty})
    except:
        return jsonify({'valid': False})
