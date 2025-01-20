#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime
from data.RL_data.data_factory import DataSourceFactory

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f'无效的日期格式: {date_str}，请使用YYYYMMDD格式')

def validate_stock_codes(codes_str):
    codes = codes_str.split(',')
    if not codes:
        raise argparse.ArgumentTypeError('股票代码不能为空')
    return codes

def main():
    parser = argparse.ArgumentParser(description='股票数据下载工具')
    parser.add_argument('--source', type=str, required=True,
                      choices=['tushare', 'baostock', 'yfinance'],
                      help='数据源: tushare/baostock/yfinance')
    parser.add_argument('--market', type=str, required=True,
                      choices=['zh', 'us'],
                      help='市场: zh(中国)/us(美国)')
    parser.add_argument('--codes', type=validate_stock_codes, required=True,
                      help='股票代码列表，用逗号分隔，如: 000001,600000')
    parser.add_argument('--start-date', type=validate_date, required=True,
                      help='开始日期，格式: YYYYMMDD')
    parser.add_argument('--end-date', type=validate_date, required=True,
                      help='结束日期，格式: YYYYMMDD')

    args = parser.parse_args()

    try:
        # 创建数据源工厂
        factory = DataSourceFactory()

        # 创建数据源
        data_source = factory.create_data_source(
            args.source,
            args.market,
            args.start_date,
            args.end_date,
            args.codes
        )

        # 获取数据
        print(f'正在从 {args.source} 获取数据...')
        data = data_source.get_day_trade_data()

        if data.empty:
            print('未获取到数据')
            sys.exit(1)

        print(f'数据获取成功，共 {len(data)} 条记录')
        print(f'数据已保存到 cachedata 目录')

    except Exception as e:
        print(f'错误: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()