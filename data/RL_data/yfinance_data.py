import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from .base_data import BaseDataFetcher, timestampchange
from logger.logging_config import logger

class YFinanceDataFetcher(BaseDataFetcher):
    def __init__(self, country, start_date, end_date, code_list):
        super().__init__(country, start_date, end_date, code_list)
        yf.pdr_override()

    def _format_date(self, date_str):
        """将YYYYMMDD格式转换为YYYY-MM-DD格式"""
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    def _process_result(self, data):
        """处理返回的数据"""
        if data.empty:
            return data
            
        # 重置索引并添加代码列
        processed_data = []
        for code in self.code_list:
            if code in data:
                df = data[code].reset_index()
                df['Date'] = df['Date'].dt.strftime('%Y%m%d')
                df['code'] = code
                df = df.rename(columns={
                    'Date': 'date',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                processed_data.append(df[['date', 'code', 'open', 'high', 'low', 'close', 'volume']])
        
        if not processed_data:
            return pd.DataFrame(columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume'])
            
        return pd.concat(processed_data, ignore_index=True)

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
            
        try:
            # 使用yfinance的批量下载功能
            data = yf.download(
                self.code_list,
                start=self._format_date(self.start_date),
                end=self._format_date(self.end_date),
                progress=False,
                group_by='ticker'
            )
            
            if isinstance(data, pd.DataFrame) and not data.empty:
                # 如果只有一个股票，需要特殊处理
                if len(self.code_list) == 1:
                    data = pd.concat({self.code_list[0]: data}, axis=1)
            
            if data.empty:
                logger.warning(f"No data found for period {self.start_date} to {self.end_date}")
                return pd.DataFrame(columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume'])
                
            result = self._process_result(data)
            
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
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame(columns=['date', 'code', 'open', 'high', 'low', 'close', 'volume']) 