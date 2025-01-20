import datetime
import os
import pandas as pd
from config.config import ConfigJson
from logger.logging_config import logger

def timestampchange(x):
    return datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%Y%m%d')

def prue_num_code(x):
    return ''.join(e for e in x if e.isdigit())

class BaseDataFetcher:
    def __init__(self, country, start_date, end_date, code_list):
        self.country = country.lower()
        self.start_date = start_date
        self.end_date = end_date
        self.code_list = code_list
        
    def get_cache_path(self, data_type):
        """获取缓存文件路径，如果缓存目录不存在则创建"""
        root_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cachedata')
        # 确保缓存目录存在
        os.makedirs(root_path, exist_ok=True)
        
        # 根据国家类型处理代码
        if self.country == 'zh':
            # 中国股票只保留数字部分
            codes_str = '_'.join(sorted([prue_num_code(code) for code in self.code_list]))
        else:
            # 其他市场（如美股）保留原始代码
            codes_str = '_'.join(sorted(self.code_list))
        
        file_name = f"{self.country}_{data_type}_{codes_str}_{self.start_date}to{self.end_date}.csv"
        return os.path.join(root_path, file_name)
        
    def get_trade_cal(self):
        raise NotImplementedError
        
    def get_day_trade_data(self):
        raise NotImplementedError 