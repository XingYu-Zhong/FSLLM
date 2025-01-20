import os
import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime
from .base_data import BaseDataFetcher, prue_num_code
from logger.logging_config import logger

class BaostockDataFetcher(BaseDataFetcher):
    def __init__(self, country, start_date, end_date, code_list):
        super().__init__(country, start_date, end_date, code_list)
        lg = bs.login()
        if lg.error_code != '0':
            raise ConnectionError(f"Baostock login failed: {lg.error_msg}")

    def __del__(self):
        """析构函数，确保退出时登出"""
        bs.logout()

    def _format_stock_code(self, code):
        """格式化股票代码"""
        if code[0] == '6' or code[0] == '5' or code[0] == 'h':
            return 'sh.' + code[-6:]
        return 'sz.' + code[-6:]

    def _format_date(self, date_str):
        """将YYYYMMDD格式转换为YYYY-MM-DD格式"""
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    def _process_result(self, df):
        """处理返回的数据"""
        if df.empty:
            return df

        # 处理日期和代码
        df['date'] = df['date'].apply(lambda x: x.replace('-', ''))
        df['code'] = df['code'].apply(prue_num_code)
        
        # 确保数值列的类型正确
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_columns:
            # 先移除可能的逗号和空格
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '').str.strip()
            # 转换为float类型
            df[col] = df[col].astype(np.float64)
        
        # 过滤掉无效数据
        df = df.dropna(subset=numeric_columns)
        
        return df[['date', 'code', 'open', 'high', 'low', 'close', 'volume', 'amount']]

    def _handle_cached_data(self, cache_path):
        """处理缓存数据"""
        df = pd.read_csv(cache_path, dtype={
            'date': str,
            'code': str,
            'open': np.float64,
            'high': np.float64,
            'low': np.float64,
            'close': np.float64,
            'volume': np.float64,
            'amount': np.float64
        })
        return df[df['code'].isin(self.code_list)]

    def get_day_trade_data(self):
        cache_path = self.get_cache_path("trade_data")
        if os.path.exists(cache_path):
            return self._handle_cached_data(cache_path)
            
        data_list = []
        formatted_start_date = self._format_date(self.start_date)
        formatted_end_date = self._format_date(self.end_date)
        
        for bs_code in self.code_list:
            formatted_code = self._format_stock_code(bs_code)
            rs = bs.query_history_k_data_plus(
                formatted_code,
                "date,code,open,high,low,close,volume,amount",
                start_date=formatted_start_date,
                end_date=formatted_end_date,
                frequency='d',
                adjustflag="3"
            )
            
            if rs is None or rs.error_code != '0':
                raise ValueError(f"Failed to get data for {bs_code}: {rs.error_msg if rs else 'No response'}")
                
            while rs.next():
                data_list.append(rs.get_row_data())
                
        if not data_list:
            logger.warning(f"No data found for period {formatted_start_date} to {formatted_end_date}")
            return pd.DataFrame(columns=["date", "code", "open", "high", "low", "close", "volume", "amount"])
            
        result = pd.DataFrame(data_list, columns=["date", "code", "open", "high", "low", "close", "volume", "amount"])
        result = self._process_result(result)
        
        # 保存前再次确认数据类型
        result = result.astype({
            'date': str,
            'code': str,
            'open': np.float64,
            'high': np.float64,
            'low': np.float64,
            'close': np.float64,
            'volume': np.float64,
            'amount': np.float64
        })
        
        result.to_csv(cache_path, index=False)
        return result 