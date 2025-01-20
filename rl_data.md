# RL 数据获取模块使用指南

本模块提供了统一的股票数据获取接口，支持多个数据源，可以获取国内外市场的股票数据。

## 支持的数据源

### 国内市场
1. Tushare
   - 需要注册并获取 token
   - 支持 A 股市场数据
   - 数据更新及时，质量可靠

2. Baostock
   - 免费使用，无需注册
   - 支持 A 股市场数据
   - 适合测试和学习使用

### 国外市场
1. YFinance
   - 支持全球主要市场
   - 免费使用，无需注册
   - 适合获取美股等海外市场数据

## 快速开始

### 1. 环境配置

首先安装必要的依赖：
```bash
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

### 4. 命令行使用

本模块提供了命令行工具，可以直接通过命令行获取股票数据：

```bash
python get_stock_data.py --source <数据源> --market <市场> --codes <股票代码> --start-date <开始日期> --end-date <结束日期>
```

参数说明：
- `--source`: 数据源，可选值：tushare、baostock、yfinance
- `--market`: 市场，可选值：zh（中国市场）、us（美国市场）
- `--codes`: 股票代码列表，多个代码用逗号分隔
- `--start-date`: 开始日期，格式：YYYYMMDD
- `--end-date`: 结束日期，格式：YYYYMMDD

使用示例：
```bash
# 获取 A 股数据（使用 Tushare）
python get_stock_data.py --source tushare --market zh --codes 000001,600000 --start-date 20240101 --end-date 20240131

# 获取美股数据（使用 YFinance）
python get_stock_data.py --source yfinance --market us --codes AAPL,GOOGL --start-date 20240101 --end-date 20240131
```

数据将以 CSV 格式保存在 data/cachedata 目录下，文件命名规则同上述说明。

## 数据集构建

本模块提供了数据集构建器（DatasetBuilder），可以将获取的股票数据转换为机器学习训练所需的数据集格式。

### 1. 基本使用

```python
from data.RL_data.build_dataset import DatasetBuilder

# 创建数据集构建器
builder = DatasetBuilder(
    market='zh',           # 市场，'zh' 或 'us'
    source='baostock',     # 数据源
    codes=['000001'],      # 股票代码列表
    start_date='20240101', # 开始日期
    end_date='20240131',   # 结束日期
    input_window=60,       # 输入窗口大小
    output_window=20,      # 输出窗口大小
    train_ratio=0.7        # 训练集比例
)

# 构建数据集
dataset = builder.build()
```

### 2. 参数说明

- `market`: 市场代码，'zh'（中国市场）或 'us'（美国市场）
- `source`: 数据源，可选 'baostock'/'tushare'/'yfinance'
- `codes`: 股票代码列表
- `start_date`: 开始日期，格式 YYYYMMDD，默认为3年前
- `end_date`: 结束日期，格式 YYYYMMDD，默认为今天
- `input_window`: 输入窗口大小，默认60天
- `output_window`: 输出窗口大小，默认20天
- `train_ratio`: 训练集比例，默认0.7

### 3. 数据集格式

构建的数据集包含以下内容：

1. 训练集和验证集
   - 按照 train_ratio 比例划分
   - 随机打乱数据顺序

2. 数据格式（.npz文件）
   - train_X: 训练集特征
   - train_y: 训练集标签
   - val_X: 验证集特征
   - val_y: 验证集标签
   - metadata: 数据集元信息

3. 标签说明
   - 0: 下跌趋势
   - 1: 震荡趋势
   - 2: 上涨趋势

### 4. 输出文件

1. NPZ格式数据集
   - 文件名格式：dataset_{market}_{source}_{codes}_in{input_window}_out{output_window}.npz
   - 包含训练集、验证集数据和元信息

2. CSV格式数据集（方便查看）
   - 文件名同上，扩展名为.csv
   - 包含以下字段：
     * sample_id: 样本ID
     * label: 数值标签（0/1/2）
     * label_name: 标签名称（下跌/震荡/上涨趋势）
     * input_list: 输入窗口的收盘价序列
     * output_list: 输出窗口的收盘价序列

### 5. 使用示例

```python
from data.RL_data.build_dataset import DatasetBuilder

# 创建数据集构建器
builder = DatasetBuilder(
    market='zh',
    source='baostock',
    codes=['000001', '600000'],
    input_window=60,
    output_window=20
)

# 构建数据集
dataset = builder.build()

# 查看数据集信息
if dataset:
    print(f"训练集样本数: {len(dataset['train']['X'])}")
    print(f"验证集样本数: {len(dataset['val']['X'])}")
```

数据集将被保存在 cachedata 目录下，可以直接加载使用：

```python
import numpy as np

# 加载数据集
data = np.load('cachedata/dataset_zh_baostock_000001_600000_in60_out20.npz')

# 获取训练数据
train_X = data['train_X']
train_y = data['train_y']

# 获取验证数据
val_X = data['val_X']
val_y = data['val_y']

# 获取元信息
metadata = data['metadata'].item()
```