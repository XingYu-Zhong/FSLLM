import pytest
from data.RL_data.data_factory import DataSourceFactory
from data.RL_data.tushare_data import TushareDataFetcher
from data.RL_data.baostock_data import BaostockDataFetcher
from data.RL_data.yfinance_data import YFinanceDataFetcher

class TestDataSourceFactory:
    @pytest.fixture(autouse=True)
    def setup(self, date_range, zh_stock_codes, us_stock_codes):
        self.factory = DataSourceFactory()
        self.params = {
            'start_date': date_range['start_date'],
            'end_date': date_range['end_date']
        }
        self.zh_codes = zh_stock_codes
        self.us_codes = us_stock_codes
        
    def test_create_tushare_source(self):
        data_source = self.factory.create_data_source(
            'tushare',
            'zh',
            self.params['start_date'],
            self.params['end_date'],
            self.zh_codes
        )
        assert isinstance(data_source, TushareDataFetcher)
        
    def test_create_baostock_source(self):
        data_source = self.factory.create_data_source(
            'baostock',
            'zh',
            self.params['start_date'],
            self.params['end_date'],
            self.zh_codes
        )
        assert isinstance(data_source, BaostockDataFetcher)
        
    def test_create_yfinance_source(self):
        data_source = self.factory.create_data_source(
            'yfinance',
            'us',
            self.params['start_date'],
            self.params['end_date'],
            self.us_codes
        )
        assert isinstance(data_source, YFinanceDataFetcher)
        
    def test_invalid_source(self):
        with pytest.raises(ValueError):
            self.factory.create_data_source(
                'invalid_source',
                'zh',
                self.params['start_date'],
                self.params['end_date'],
                self.zh_codes
            ) 