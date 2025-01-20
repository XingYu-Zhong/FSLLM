import numpy as np
import pandas as pd
from data.RL_data.trend_analysis import TrendAnalyzer

def test_trend_analyzer():
    """测试函数"""
    # 生成测试数据
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    base_price = np.linspace(100, 120, 100)  # 上升趋势
    noise = np.random.normal(0, 2, 100)
    close_prices = base_price + noise
    
    df_test = pd.DataFrame({
        "date": dates,
        "close": close_prices
    })
    
    # 分析趋势
    analyzer = TrendAnalyzer()
    trend, pivots = analyzer.analyze_stock_trend(df_test)
    
    print("趋势分析结果:")
    print(f"当前趋势: {trend}")
    print("\n关键枢纽点:")
    for p in pivots:
        print(f"位置: {p['index']}, 价格: {p['price']:.2f}, 类型: {p['type']}")


if __name__ == "__main__":
    test_trend_analyzer() 