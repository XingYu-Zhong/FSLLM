# RL 数据获取模块使用指南

本模块提供了统一的股票数据获取接口，支持多个数据源，可以获取国内外市场的股票数据。

## 支持的数据源

### 国内市场 (A股)
1. Tushare (推荐)
   - 需要注册获取 token
   - 数据质量好，更新及时
   - 支持更多的数据类型

2. Baostock
   - 免费使用，无需注册
   - 数据延迟较小
   - 适合学习和测试

### 国外市场
1. YFinance
   - 支持全球主要市场
   - 免费使用，无需注册
   - 适合获取美股等海外市场数据

## 快速开始

### 1. 环境配置

首先安装必要的依赖：
```python
pip install -r requirements.txt
```

### 2. 配置数据源

创建 .env 文件并配置相关 token：
```env
TUSHARE_TOKEN=你的tushare_token
MJS_TOKEN=你的mjs_token  # 可选
```

### 3. 基本使用

```python
from data.RL_data.data_factory import DataSourceFactory

# 创建数据源工厂
factory = DataSourceFactory()

# 配置参数
start_date = '20240101'
end_date = '20240131'
zh_codes = ['000001', '600000']  # A股代码
us_codes = ['AAPL', 'GOOGL']     # 美股代码

# 获取A股数据（使用 Tushare）
zh_data_source = factory.create_data_source(
    'tushare',    # 或 'baostock'
    'zh',         # 国家/地区代码
    start_date,
    end_date,
    zh_codes
)
zh_data = zh_data_source.get_day_trade_data()

# 获取美股数据
us_data_source = factory.create_data_source(
    'yfinance',
    'us',
    start_date,
    end_date,
    us_codes
)
us_data = us_data_source.get_day_trade_data()
```

### 4. 数据格式

所有数据源返回的数据格式统一为 pandas DataFrame，包含以下字段：
- date: 交易日期 (格式：YYYYMMDD)
- code: 股票代码
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- volume: 成交量

示例数据：
```csv
date,code,open,high,low,close,volume
20240101,000001,11.59,11.64,11.54,11.59,69737904
20240101,600000,9.51,9.56,9.42,9.53,42987772
```

### 5. 数据缓存

- 数据会自动缓存在 data/cachedata 目录下
- 缓存文件命名格式：
  - A股：zh_trade_data_000001_600000_20240101to20240131.csv
  - 美股：us_trade_data_AAPL_GOOGL_20240101to20240131.csv
- 再次请求相同的数据会直接从缓存读取，提高效率

## 高级特性

### 1. 股票代码格式

- A股：支持带后缀和不带后缀的代码（如 '000001' 或 '000001.SZ'）
- 美股：直接使用股票代码（如 'AAPL', 'GOOGL'）

### 2. 错误处理

- 数据获取失败会返回空的 DataFrame
- 通过日志记录详细的错误信息
- 支持优雅的异常处理

### 3. 数据验证

所有返回的数据都会进行以下验证：
- 数据类型检查（如 float64 类型的价格数据）
- 数值范围验证（如价格 > 0）
- 日期连续性检查
- 重复数据检查

## 注意事项

1. Tushare 使用提示：
   - 需要注册并获取 token
   - 不同的会员等级有不同的访问限制
   - 建议使用 MJS_TOKEN 以获得更好的访问体验

2. Baostock 使用提示：
   - 无需注册，但需要网络连接
   - 数据可能有延迟
   - 适合用于测试和学习

3. YFinance 使用提示：
   - 免费使用，但有访问频率限制
   - 建议合理控制请求频率
   - 数据精度可能略低于付费数据源



