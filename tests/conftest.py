import pytest
import logging
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def setup_logging():
    logger.info("Setting up test environment")
    yield
    logger.info("Tearing down test environment")

@pytest.fixture
def date_range():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 获取过去30天的数据
    # 确保日期格式正确且是过去的日期
    dates = {
        'start_date': (end_date - timedelta(days=30)).strftime('%Y%m%d'),
        'end_date': (end_date - timedelta(days=1)).strftime('%Y%m%d')  # 使用昨天作为结束日期
    }
    logger.debug(f"Date range: {dates}")
    return dates

@pytest.fixture
def zh_stock_codes():
    return ['000001', '600000']  # 平安银行、浦发银行

@pytest.fixture
def us_stock_codes():
    return ['AAPL', 'GOOGL']  # 苹果、谷歌 