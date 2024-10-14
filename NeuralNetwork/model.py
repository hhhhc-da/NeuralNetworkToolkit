# coding=utf-8
import torch
from torch import nn
import torch.nn.functional as F


class LeNet(nn.Module):
    def __init__(self):
        nn.Module.__init__(self)
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=12, kernel_size=4)
        self.fc1 = nn.Linear(in_features=12*35*35, out_features=120)
        self.fc2 = nn.Linear(in_features=120, out_features=84)
        self.fc3 = nn.Linear(in_features=84, out_features=2)  # 二分类

    def forward(self, x):
        x = F.relu(self.conv1(x))           # 第一层卷积 + ReLU
        x = F.max_pool2d(x, 2)              # 最大池化
        x = F.relu(self.conv2(x))           # 第二层卷积 + ReLU
        x = F.max_pool2d(x, 2)              # 最大池化
        x = x.view(x.size(0), -1)           # 展平
        x = F.relu(self.fc1(x))             # 全连接层 + ReLU
        x = F.relu(self.fc2(x))             # 全连接层 + ReLU
        x = self.fc3(x)                     # 输出层
        return F.softmax(x, dim=1)          # Softmax 激活

    @torch.no_grad
    def predict(self, x):
        return self.forward(x)
