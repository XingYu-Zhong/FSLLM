import pandas as pd
import numpy as np
from logger.logging_config import logger

class TrendAnalyzer:
    """趋势分析工具类"""
    
    @staticmethod
    def zigzag_pivots(df, price_col='close', pct_threshold=2.0):
        """
        基于百分比阈值的 ZigZag 算法，识别主要枢纽点(Pivot)。
        
        参数:
            df (DataFrame): 包含价格数据的DataFrame
            price_col (str): 用于识别枢纽点的价格列名
            pct_threshold (float): 反转阈值(%)，价格反向波动超过该百分比时确认新Pivot
            
        返回:
            list[dict]: 枢纽点列表，每个元素包含 index(位置)、price(价格)和type(类型H/L)
        """
        try:
            arr = df[price_col].values
            n = len(arr)
            if n == 0:
                return []
            
            # 结果Pivot列表
            pivots = []
            
            # 初始化
            first_price = arr[0]
            first_index = df.index[0]  # 保留原始索引
            last_pivot_index = first_index
            last_pivot_price = first_price
            
            # 默认从波谷开始
            pivot_type = 'L'
            
            # 记录第一个点
            pivots.append({
                "index": last_pivot_index, 
                "price": last_pivot_price, 
                "type": pivot_type
            })
            
            for i in range(1, n):
                current_index = df.index[i]
                current_price = arr[i]
                price_change = ((current_price - last_pivot_price) / last_pivot_price) * 100
                
                if pivot_type == 'L':
                    # 从波谷向上超过阈值，确认新的波峰
                    if price_change >= pct_threshold:
                        pivot_type = 'H'
                        last_pivot_price = current_price
                        last_pivot_index = current_index
                        pivots.append({
                            "index": current_index, 
                            "price": current_price, 
                            "type": 'H'
                        })
                    # 继续创新低，更新波谷
                    elif current_price < last_pivot_price:
                        last_pivot_price = current_price
                        last_pivot_index = current_index
                        pivots[-1] = {
                            "index": current_index, 
                            "price": current_price, 
                            "type": 'L'
                        }
                
                elif pivot_type == 'H':
                    # 从波峰向下超过阈值，确认新的波谷
                    if price_change <= -pct_threshold:
                        pivot_type = 'L'
                        last_pivot_price = current_price
                        last_pivot_index = current_index
                        pivots.append({
                            "index": current_index, 
                            "price": current_price, 
                            "type": 'L'
                        })
                    # 继续创新高，更新波峰
                    elif current_price > last_pivot_price:
                        last_pivot_price = current_price
                        last_pivot_index = current_index
                        pivots[-1] = {
                            "index": current_index, 
                            "price": current_price, 
                            "type": 'H'
                        }
            
            return pivots
            
        except Exception as e:
            logger.error(f"ZigZag分析失败: {str(e)}")
            return []

    @staticmethod
    def judge_trend(pivots, tolerance=0.5):
        """
        基于ZigZag枢纽点判断趋势。
        
        参数:
            pivots (list[dict]): ZigZag枢纽点列表
            tolerance (float): 在比较高点或低点时的小幅波动容忍度(同价格单位)
            
        返回:
            str: "Uptrend"(上升) / "Downtrend"(下降) / "Sideways"(横盘)
        """
        try:
            if len(pivots) < 4:
                return "Sideways"
            
            highs = [p for p in pivots if p["type"] == 'H']
            lows = [p for p in pivots if p["type"] == 'L']
            
            if len(highs) < 2 or len(lows) < 2:
                return "Sideways"
            
            # 按时间或index排序
            highs_sorted = sorted(highs, key=lambda x: x["index"])
            lows_sorted = sorted(lows, key=lambda x: x["index"])
            
            last_two_highs = highs_sorted[-2:]
            last_two_lows = lows_sorted[-2:]
            
            h1, h2 = last_two_highs[0]["price"], last_two_highs[1]["price"]
            l1, l2 = last_two_lows[0]["price"], last_two_lows[1]["price"]
            
            # 上升趋势（考虑一定的容忍度）
            if (h2 >= h1 - tolerance) and (l2 > l1 + tolerance):
                return "Uptrend"
            # 下降趋势
            elif (h1 > h2 + tolerance) and (l1 > l2 + tolerance):
                return "Downtrend"
            else:
                return "Sideways"
                
        except Exception as e:
            logger.error(f"趋势判断失败: {str(e)}")
            return "Sideways"

    @classmethod
    def analyze_stock_trend(cls, df, price_col='close'):
        """
        分析股票趋势，自动根据价格波动设置 pct_threshold 和 tolerance。
        
        参数:
            df (DataFrame): 股票数据
            price_col (str): 价格列名
            
        返回:
            tuple: (趋势, 枢纽点列表)
        """
        try:
            # ========== 1. 如果数据太少，直接返回 "Sideways" ==========
            if df.shape[0] < 2:
                return "Sideways", []
            
            # ========== 2. 计算日收益率的平均波动(%) ==========
            daily_returns = df[price_col].pct_change().dropna()
            if len(daily_returns) < 1:
                return "Sideways", []
            
            # 日均涨跌幅(绝对值)
            avg_abs_return_percent = daily_returns.abs().mean() * 100  # 转成百分比
            
            # ========== 3. 自动设置 pct_threshold ==========
            # 简单做一个倍数放大，比如2倍日均波动，并限制在[1, 5]之间
            auto_pct_threshold = avg_abs_return_percent * 2.0
            pct_threshold = min(max(auto_pct_threshold, 1.0), 5.0)
            
            # ========== 4. 自动设置 tolerance ==========
            # 根据最近价格区间做一个2%范围 (可根据需求调整)
            price_min = df[price_col].min()
            price_max = df[price_col].max()
            price_range = price_max - price_min
            
            # 如果整个数据价格区间没变化(比如所有价格都一样), 给个缺省值
            if price_range == 0:
                tolerance = 0.1
            else:
                tolerance = price_range * 0.02  # 2%的区间
            
            logger.info(f"Auto-calculated pct_threshold={pct_threshold:.2f}, tolerance={tolerance:.2f}")
            
            # ========== 5. 获取ZigZag枢纽点 ==========
            pivots = cls.zigzag_pivots(df, price_col=price_col, pct_threshold=pct_threshold)
            
            # ========== 6. 判断趋势 ==========
            trend = cls.judge_trend(pivots, tolerance=tolerance)
            
            return trend, pivots
            
        except Exception as e:
            logger.error(f"趋势分析失败: {str(e)}")
            return "Sideways", []