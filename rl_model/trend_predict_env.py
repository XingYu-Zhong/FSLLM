import gym
import numpy as np
from gym import spaces
from data.RL_data.build_dataset import DatasetBuilder
from logger.logging_config import logger

class TrendPredictEnv(gym.Env):
    """
    股票趋势预测环境
    观察空间：60天的历史收盘价数据
    动作空间：0(下跌)、1(震荡)、2(上涨)
    """
    def __init__(self, market='zh', source='baostock', codes=None, 
                 start_date=None, end_date=None, is_train=True):
        super(TrendPredictEnv, self).__init__()
        
        # 初始化数据集构建器
        self.builder = DatasetBuilder(
            market=market,
            source=source,
            codes=codes if codes else ['000001'],
            start_date=start_date,
            end_date=end_date,
            input_window=60,    # 输入窗口固定为60天
            output_window=20,   # 输出窗口固定为20天
            train_ratio=0.8     # 训练集比例
        )
        
        # 构建数据集
        self.dataset = self.builder.build()
        if not self.dataset:
            raise ValueError('数据集构建失败')
            
        # 设置是否为训练模式
        self.is_train = is_train
        self.data = self.dataset['train'] if is_train else self.dataset['val']
        
        # 设置当前样本索引
        self.current_index = 0
        self.max_index = len(self.data['X']) - 1
        
        # 定义动作空间：0(下跌)、1(震荡)、2(上涨)
        self.action_space = spaces.Discrete(3)
        
        # 定义观察空间：60天的历史数据，值域在[0,1]之间
        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(60,),
            dtype=np.float32
        )
        
    def reset(self):
        """重置环境"""
        self.current_index = 0
        return self.data['X'][self.current_index]
        
    def step(self, action):
        """执行一步交互"""
        # 获取当前真实标签
        true_label = self.data['y'][self.current_index]
        
        # 计算奖励：预测正确得1分，预测错误得-1分
        reward = 1.0 if action == true_label else -1.0
        
        # 更新索引
        self.current_index += 1
        done = self.current_index >= self.max_index
        
        # 获取下一个观察值
        next_observation = self.data['X'][self.current_index] if not done else None
        
        return next_observation, reward, done, {}
        
    def render(self, mode='human'):
        """渲染环境"""
        if mode == 'human':
            current_data = self.data['X'][self.current_index]
            true_label = self.data['y'][self.current_index]
            label_map = {0: '下跌', 1: '震荡', 2: '上涨'}
            
            logger.info(f'当前索引: {self.current_index}')
            logger.info(f'当前数据形状: {current_data.shape}')
            logger.info(f'真实趋势: {label_map[true_label]}')