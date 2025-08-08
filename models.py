from app import db
from datetime import datetime
import json

class BacktestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy_name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    initial_capital = db.Column(db.Float, nullable=False)
    final_value = db.Column(db.Float, nullable=False)
    total_return = db.Column(db.Float, nullable=False)
    sharpe_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    total_trades = db.Column(db.Integer)
    parameters = db.Column(db.Text)  # JSON string of strategy parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_parameters(self, params_dict):
        self.parameters = json.dumps(params_dict)
    
    def get_parameters(self):
        if self.parameters:
            return json.loads(self.parameters)
        return {}

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    backtest_id = db.Column(db.Integer, db.ForeignKey('backtest_result.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'BUY' or 'SELL'
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)
    
    backtest = db.relationship('BacktestResult', backref=db.backref('trades', lazy=True))
