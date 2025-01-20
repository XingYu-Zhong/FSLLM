#!/usr/bin/env python3

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data.RL_data.data_factory import DataSourceFactory
from data.RL_data.trend_analysis import TrendAnalyzer
from logger.logging_config import logger
import os

class DatasetBuilder:
    def __init__(self, market='zh', source='baostock', codes=None, 
                 start_date=None, end_date=None,
                 input_window=60, output_window=20,
                 train_ratio=0.7):
        """
        初始化数据集构建器
        
        参数:
            market (str): 市场，'zh' 或 'us'
            source (str): 数据源，'baostock'/'tushare'/'yfinance'
            codes (list): 股票代码列表
            start_date (str): 开始日期，格式YYYYMMDD，默认为3年前
            end_date (str): 结束日期，格式YYYYMMDD，默认为今天
            input_window (int): 输入窗口大小，默认60天
            output_window (int): 输出窗口大小，默认20天
            train_ratio (float): 训练集比例，默认0.7
        """
        self.market = market
        self.source = source
        self.codes = codes if codes else []
        self.input_window = input_window
        self.output_window = output_window
        self.train_ratio = train_ratio
        
        # 设置默认日期范围（如果未指定）
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y%m%d')
            
        self.start_date = start_date
        self.end_date = end_date
        
        # 初始化数据源
        self.factory = DataSourceFactory()
        self.data_source = None
        
    def fetch_data(self):
        """获取股票数据"""
        try:
            self.data_source = self.factory.create_data_source(
                self.source,
                self.market,
                self.start_date,
                self.end_date,
                self.codes
            )
            return self.data_source.get_day_trade_data()
        except Exception as e:
            logger.error(f'获取数据失败: {str(e)}')
            return pd.DataFrame()
    
    def build_samples(self, data):
        """构建样本数据集"""
        samples = []
        labels = []
        input_windows = []  # 存储输入窗口的原始数据
        output_windows = []  # 存储输出窗口的原始数据
        
        # 按股票代码分组处理
        for code in self.codes:
            stock_data = data[data['code'] == code].sort_values('date')
            if len(stock_data) < self.input_window + self.output_window:
                continue
                
            # 使用滑动窗口构建样本
            for i in range(0, len(stock_data) - self.input_window - self.output_window + 1, 5):
                # 输入特征窗口
                input_data = stock_data.iloc[i:i+self.input_window]
                # 输出标签窗口
                output_data = stock_data.iloc[i+self.input_window:i+self.input_window+self.output_window]
                
                # 检查output_data是否有足够的数据
                if len(output_data) < self.output_window:
                    continue
                
                # 使用趋势分析器判断趋势
                trend, _ = TrendAnalyzer.analyze_stock_trend(output_data)
                
                # 将趋势转换为数值标签
                trend_label = {
                    'Uptrend': 2,
                    'Sideways': 1,
                    'Downtrend': 0
                }[trend]
                
                # 将所有数据存入字典
                sample_dict = {
                    'features': input_data['close'].values,
                    'label': trend_label,
                    'input_window': input_data['close'].values.tolist(),
                    'output_window': output_data['close'].values.tolist()
                }
                samples.append(sample_dict)

        return samples
    
    def split_dataset(self, samples):
        """划分训练集和验证集"""
        # 随机打乱数据
        indices = np.random.permutation(len(samples))
        train_size = int(len(samples) * self.train_ratio)
        
        train_indices = indices[:train_size]
    
    def split_dataset(self, X, y):
        """划分训练集和验证集"""
        # 随机打乱数据
        indices = np.random.permutation(len(X))
        train_size = int(len(X) * self.train_ratio)
        
        train_indices = indices[:train_size]
        val_indices = indices[train_size:]
        
        return {
            'train': {
                'X': X[train_indices],
                'y': y[train_indices]
            },
            'val': {
                'X': X[val_indices],
                'y': y[val_indices]
            }
        }
    
    def build(self):
        """构建完整的数据集"""
        # 1. 获取数据
        logger.info('正在获取股票数据...')
        data = self.fetch_data()
        if data.empty:
            logger.warning('获取的数据为空')
            return None
            
        # 2. 构建样本
        logger.info('正在构建样本...')
        samples = self.build_samples(data)
        if len(samples) == 0:
            logger.warning('没有足够的数据构建样本')
            return None
            
        # 一次性提取所有特征和标签
        data_arrays = [(sample['features'], sample['label'], sample['input_window'], sample['output_window']) for sample in samples]
        X, y, input_windows, output_windows = map(list, zip(*data_arrays))
        X = np.array(X)
        y = np.array(y)
            
        # 3. 划分数据集
        logger.info('正在划分训练集和验证集...')
        dataset = self.split_dataset(X, y)
        
        logger.info('数据集构建完成:')
        logger.info(f'- 训练集: {len(dataset["train"]["X"])} 个样本')
        logger.info(f'- 验证集: {len(dataset["val"]["X"])} 个样本')
        
        # 4. 保存数据集
        cache_dir = 'cachedataset'
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        # 构造文件名
        codes_str = '_'.join(self.codes) if len(self.codes) <= 3 else f'{self.codes[0]}_{len(self.codes)}stocks'
        filename = f'dataset_{self.market}_{self.source}_{codes_str}_in{self.input_window}_out{self.output_window}.npz'
        filepath = os.path.join(cache_dir, filename)
        
        # 保存数据集
        np.savez(filepath,
                 train_X=dataset['train']['X'],
                 train_y=dataset['train']['y'],
                 val_X=dataset['val']['X'],
                 val_y=dataset['val']['y'],
                 metadata={
                     'market': self.market,
                     'source': self.source,
                     'codes': self.codes,
                     'start_date': self.start_date,
                     'end_date': self.end_date,
                     'input_window': self.input_window,
                     'output_window': self.output_window,
                     'train_ratio': self.train_ratio
                 })
        logger.info(f'数据集已保存到: {filepath}')
        
        # 保存CSV格式的数据集，方便直接查看
        csv_filename = filepath.replace('.npz', '.csv')
        all_samples = np.concatenate([dataset['train']['X'], dataset['val']['X']], axis=0)
        all_labels = np.concatenate([dataset['train']['y'], dataset['val']['y']], axis=0)
        
        # 创建DataFrame，只保留必要的列并重命名
        df_data = {
            'sample_id': range(len(all_samples)),
            'label': all_labels,
            'label_name': ['下跌趋势' if l == 0 else '震荡趋势' if l == 1 else '上涨趋势' for l in all_labels],
            'input_list': input_windows,
            'output_list': output_windows
        }
            
        df = pd.DataFrame(df_data)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        logger.info(f'CSV格式数据集已保存到: {csv_filename}')
        
        # 打印数据分布统计
        label_dist = np.bincount(all_labels)
        total_samples = len(all_labels)
        logger.info('\n完整数据集的标签分布:')
        logger.info(f'- 下跌趋势 (0): {label_dist[0]} 个样本 ({label_dist[0]/total_samples*100:.2f}%)')
        logger.info(f'- 震荡趋势 (1): {label_dist[1]} 个样本 ({label_dist[1]/total_samples*100:.2f}%)')
        logger.info(f'- 上涨趋势 (2): {label_dist[2]} 个样本 ({label_dist[2]/total_samples*100:.2f}%)')
        
        return dataset
