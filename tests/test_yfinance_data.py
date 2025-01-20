import pytest
import pandas as pd
from data.RL_data.data_factory import DataSourceFactory

class TestYFinanceDataFetcher:
    @pytest.fixture(autouse=True)
    def setup(self, date_range, us_stock_codes):
        self.factory = DataSourceFactory()
        self.data_source = self.factory.create_data_source(
            'yfinance',
            'us',
            date_range['start_date'],
            date_range['end_date'],
            us_stock_codes
        )
        
    def test_get_day_trade_data(self):
        df = self.data_source.get_day_trade_data()
        
        # 检查数据框架是否正确
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        
        # 检查必要的列是否存在
        required_columns = ['date', 'code', 'open', 'high', 'low', 'close', 'volume']
        assert all(col in df.columns for col in required_columns)
        
        # 检查数据类型
        assert df['date'].dtype == 'object'
        assert df['code'].dtype == 'object'
        assert df['open'].dtype == 'float64'
        assert df['volume'].dtype == 'float64'
        
        # 检查数据值是否合理
        assert df['open'].min() > 0
        assert df['close'].min() > 0
        assert df['volume'].min() >= 0 