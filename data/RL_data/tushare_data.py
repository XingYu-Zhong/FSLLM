import os
import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime
from .base_data import BaseDataFetcher, timestampchange
from config.config import ConfigJson
from logger.logging_config import logger

class TushareDataFetcher(BaseDataFetcher):
    def __init__(self, country, start_date, end_date, code_list):
        super().__init__(country, start_date, end_date, code_list)
        config = ConfigJson()
        config.get_account()
        ts.set_token(config.tushare_token)
        if config.mjs_token:
            self.api = ts.pro_api(config.mjs_token)
            self.api._DataApi__http_url = 'http://tsapi.majors.ltd:7000'
        else:
            self.api = ts.pro_api()

    def _format_stock_code(self, code):
        """格式化股票代码，自动添加市场后缀"""
        # 如果已经有后缀，直接返回
        if code.endswith(('.SH', '.SZ')):
            return code
            
        # 根据股票代码规则添加后缀
        if code.startswith(('6', '5', '9')):
            return f"{code}.SH"
        elif code.startswith(('0', '3')):
            return f"{code}.SZ"
        else:
            logger.warning(f"Unknown stock code format: {code}")
            return code

    def _process_result(self, data):
        """处理返回的数据"""
        if data.empty:
            return data
            
        data['date'] = pd.to_datetime(data['trade_date']).dt.strftime('%Y%m%d')
        data = data.rename(columns={
            'ts_code': 'code',
            'vol': 'volume'
        })
        # 移除代码后缀
        data['code'] = data['code'].str.replace('.S[HZ]$', '', regex=True)
        return data[['date', 'code', 'open', 'high', 'low', 'close', 'volume']]

    def _handle_cached_data(self, cache_path):
        """处理缓存数据"""
        df = pd.read_csv(cache_path, dtype={
            'date': str,
            'code': str,
            'open': np.float64,
            'high': np.float64,
            'low': np.float64,
            'close': np.float64,
            'volume': np.float64
        })
        return df[df['code'].isin(self.code_list)]

    def get_day_trade_data(self):
        cache_path = self.get_cache_path("trade_data")
        if os.path.exists(cache_path):
            return self._handle_cached_data(cache_path)
            
        result = pd.DataFrame()
        for code in self.code_list:
            formatted_code = self._format_stock_code(code)
            try:
                data = self.api.daily(ts_code=formatted_code, 
                                    start_date=self.start_date, 
                                    end_date=self.end_date)
                if data is not None and not data.empty:
                    result = pd.concat([result, data])
                else:
                    logger.warning(f"No data returned for {formatted_code}")
            except Exception as e:
                logger.error(f"Error fetching data for {formatted_code}: {str(e)}")
                
        if result.empty:
            logger.warning(f"No data found for period {self.start_date} to {self.end_date}")
            return pd.DataFrame(columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume'])
            
        result = self._process_result(result)
        
        # 保存前确保数据类型正确
        result = result.astype({
            'date': str,
            'code': str,
            'open': np.float64,
            'high': np.float64,
            'low': np.float64,
            'close': np.float64,
            'volume': np.float64
        })
        
        result.to_csv(cache_path, index=False)
        return result 