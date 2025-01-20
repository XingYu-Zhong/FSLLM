import pytest
import pandas as pd
from datetime import datetime
from data.RL_data.data_factory import DataSourceFactory

class TestBaostockDataFetcher:
    @pytest.fixture(autouse=True)
    def setup(self, date_range, zh_stock_codes):
        self.factory = DataSourceFactory()
        self.data_source = self.factory.create_data_source(
            'baostock',
            'zh',
            date_range['start_date'],
            date_range['end_date'],
            zh_stock_codes
        )
        self.date_range = date_range
    
    def test_format_date(self):
        """测试日期格式转换"""
        formatted_start = self.data_source._format_date('20240101')
        assert formatted_start == '2024-01-01'
    
    @pytest.mark.baostock    
    def test_get_day_trade_data(self):
        df = self.data_source.get_day_trade_data()
        
        # 检查数据框架是否正确
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        
        # 检查必要的列是否存在
        required_columns = ['date', 'code', 'open', 'high', 'low', 'close', 'volume', 'amount']
        assert all(col in df.columns for col in required_columns)
        
        # 检查数据类型
        assert df['date'].dtype == 'object'
        assert df['code'].dtype == 'object'
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_columns:
            print(df[col].dtype)
            assert df[col].dtype == 'float64', f"{col} 应该是 float64 类型"
        
        # 检查数据值是否合理
        assert df['open'].min() > 0, "开盘价应该大于0"
        assert df['close'].min() > 0, "收盘价应该大于0"
        assert df['volume'].min() >= 0, "成交量应该大于等于0"
        assert df['amount'].min() >= 0, "成交额应该大于等于0"
        assert (df['high'] >= df['low']).all(), "最高价应该大于等于最低价"
        
        # 检查是否有重复数据
        assert not df.duplicated(['date', 'code']).any(), "数据中不应该有重复记录"
        
        # 检查日期范围
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        min_date = df['date'].min()
        max_date = df['date'].max()
        start_date = datetime.strptime(self.date_range['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.date_range['end_date'], '%Y%m%d')
        
        assert min_date >= start_date, f"最早数据日期 {min_date} 应该不早于开始日期 {start_date}"
        assert max_date <= end_date, f"最新数据日期 {max_date} 应该不晚于结束日期 {end_date}"
        
        # 检查股票代码
        assert set(df['code']) == set(self.data_source.code_list), "返回的股票代码与请求的不匹配" 
    
    @pytest.mark.baostock    
    def test_get_day_trade_data_empty(self):
        """测试无数据时的情况"""
        # 使用一个不可能有数据的日期范围
        self.data_source.start_date = '19000101'
        self.data_source.end_date = '19000102'
        df = self.data_source.get_day_trade_data()
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == ["date", "code", "open", "high", "low", "close", "volume", "amount"] 