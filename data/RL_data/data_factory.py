from .tushare_data import TushareDataFetcher
from .baostock_data import BaostockDataFetcher
from .yfinance_data import YFinanceDataFetcher

class DataSourceFactory:
    @staticmethod
    def create_data_source(source_name, country, start_date, end_date, code_list):
        sources = {
            'tushare': TushareDataFetcher,
            'baostock': BaostockDataFetcher,
            'yfinance': YFinanceDataFetcher
        }
        
        if source_name not in sources:
            raise ValueError(f"Unsupported data source: {source_name}")
            
        return sources[source_name](country, start_date, end_date, code_list) 