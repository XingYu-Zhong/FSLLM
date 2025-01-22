import torch
import numpy as np
from elegantrl.agents import AgentPPO
from elegantrl.train.config import Arguments
from elegantrl.train.run import train_and_evaluate
from rl_model.env.trend_predict_env import TrendPredictEnv
from logger.logging_config import logger

class ActorCritic(torch.nn.Module):
    """Actor-Critic网络"""
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(state_dim, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 32),
            torch.nn.ReLU(),
        )
        self.actor = torch.nn.Sequential(
            torch.nn.Linear(32, action_dim),
            torch.nn.Softmax(dim=-1),
        )
        self.critic = torch.nn.Sequential(
            torch.nn.Linear(32, 1),
        )

    def forward(self, state):
        feature = self.net(state)
        action_prob = self.actor(feature)
        value = self.critic(feature)
        return action_prob, value

def main():
    # 创建环境
    train_env = TrendPredictEnv(
        market='zh',
        source='baostock',
        codes=['000001'],
        start_date='20200101',
        end_date='20240101',
        is_train=True
    )
    
    # 创建评估环境
    eval_env = TrendPredictEnv(
        market='zh',
        source='baostock',
        codes=['000001'],
        start_date='20240101',
        end_date='20250101',
        is_train=False
    )
    
    # 设置训练参数
    args = Arguments(
        env=train_env,
        eval_env=eval_env,
        agent=AgentPPO,
        agent_class=ActorCritic,
        net_dim=128,
        batch_size=256,
        learning_rate=1e-4,
        gamma=0.99,
        target_step=2048,
        eval_gap=1000,
        eval_times=20,
    )
    
    # 开始训练
    logger.info('开始训练...')
    train_and_evaluate(args)
    logger.info('训练完成')

if __name__ == '__main__':
    main()