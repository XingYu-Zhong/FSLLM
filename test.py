import numpy as np
import pandas as pd
from data.RL_data.build_dataset import DatasetBuilder
from logger.logging_config import logger
def main():
    # 示例用法
    builder = DatasetBuilder(
        market='zh',
        source='baostock',
        codes=['000001'],  # 示例股票代码
        input_window=60,
        output_window=20,
        train_ratio=1,
        start_date='20050101',
        end_date='20200101'
    )
    
    dataset = builder.build()
    if dataset:
        logger.info('\n数据集示例:')
        # 打印训练集信息
        logger.info(f'训练集特征形状: {dataset["train"]["X"].shape}')
        logger.info(f'训练集标签形状: {dataset["train"]["y"].shape}')

        
        # 打印训练集标签分布
        train_label_dist = np.bincount(dataset["train"]["y"])
        logger.info('\n训练集标签分布:')
        logger.info(f'- 下跌趋势 (0): {train_label_dist[0]} 个样本')
        logger.info(f'- 震荡趋势 (1): {train_label_dist[1]} 个样本')
        logger.info(f'- 上涨趋势 (2): {train_label_dist[2]} 个样本')
        
        # 打印验证集信息
        logger.info(f'\n验证集特征形状: {dataset["val"]["X"].shape}')
        logger.info(f'验证集标签形状: {dataset["val"]["y"].shape}')

        
      
    
    builder = DatasetBuilder(
        market='zh',
        source='baostock',
        codes=['000001'],  # 示例股票代码
        input_window=60,
        output_window=20,
        train_ratio=1,
        start_date='20200101',
        end_date='20250101'
    )
    
    dataset = builder.build()
    if dataset:
        logger.info('\n数据集示例:')
        # 打印训练集信息
        logger.info(f'训练集特征形状: {dataset["train"]["X"].shape}')
        logger.info(f'训练集标签形状: {dataset["train"]["y"].shape}')

        
        # 打印训练集标签分布
        train_label_dist = np.bincount(dataset["train"]["y"])
        logger.info('\n训练集标签分布:')
        logger.info(f'- 下跌趋势 (0): {train_label_dist[0]} 个样本')
        logger.info(f'- 震荡趋势 (1): {train_label_dist[1]} 个样本')
        logger.info(f'- 上涨趋势 (2): {train_label_dist[2]} 个样本')
        
        # 打印验证集信息
        logger.info(f'\n验证集特征形状: {dataset["val"]["X"].shape}')
        logger.info(f'验证集标签形状: {dataset["val"]["y"].shape}')

        

if __name__ == '__main__':
    main()