# coding=utf-8
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import confusion_matrix, classification_report, f1_score, make_scorer
import pandas as pd
from torchvision.models import resnet18, ResNet18_Weights
import numpy as np
from dataloader import MyDataset


# scikit-learn 适配器
class AdaptedClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, learning_rate=0.001, batch_size=15, test_batch_size=3, episode=20):
        super(AdaptedClassifier, self).__init__()

        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.test_batch_size = test_batch_size
        self.episode = episode

        self.model = resnet18(weights=ResNet18_Weights.DEFAULT)
        self.model.fc = nn.Linear(self.model.fc.in_features, 2, bias=False)
        self.model = self.model.to(self.device)
        self.critirion = nn.CrossEntropyLoss()

        # 默认 betas=(0.9, 0.999)
        self.optimizer = optim.Adam(
            self.model.parameters(), lr=self.learning_rate)

    def fit(self, x, y):
        self.model.train()
        x_input = torch.tensor(x, dtype=torch.float32).to(self.device)
        y_input = torch.tensor(y, dtype=torch.long).to(self.device)

        # 确定分类总数
        self.classes_ = np.unique(y)

        for _ in range(self.episode):
            self.optimizer.zero_grad()

            output = self.model(x_input)
            loss = self.critirion(output, y_input)
            loss.backward()
            self.optimizer.step()

        return self

    def predict(self, x):
        self.model.eval()
        x_input = torch.tensor(x, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            outputs = self.model(x_input)

            if torch.cuda.is_available():
                predicted = torch.argmax(outputs, 1).cpu()
            else:
                predicted = torch.argmax(outputs, 1)

            return predicted.numpy()


# 设置超参数网格
param_grid = {
    'learning_rate': [0.05, 0.01, 0.005, 0.001],
    'batch_size': [2, 5, 10, 15, 20],
    'episode': [5, 10, 15, 20, 30]  # 可以根据需要调整
}

# 创建 GridSearchCV 对象, 宏平均 F1-score 评价方式
grid_search = GridSearchCV(estimator=AdaptedClassifier(
), param_grid=param_grid, cv=2, scoring=make_scorer(f1_score, average='macro'))

train_dataset = MyDataset(mode='train')
x_train, y_train = train_dataset.data()
print("x_train.shape: {}, y_train.shape: {}".format(x_train.shape, y_train.shape))

grid_search.fit(x_train, y_train)

# 输出最佳参数和评分
print("最佳参数:", grid_search.best_params_)
print("最佳得分:", grid_search.best_score_)

results = pd.DataFrame(grid_search.cv_results_)
print("\n所有参数组合的得分:\n{}".format(
    results[['params', 'mean_test_score', 'std_test_score', 'rank_test_score']]))

# 测试数据
test_dataset = MyDataset(mode='test')
x_test, y_test = test_dataset.data()
print("x_test.shape: {}, y_test.shape: {}".format(x_test.shape, y_test.shape))

# 处理后的预测数据
best_model = grid_search.best_estimator_
y_pred = best_model.predict(x_test)

print("\n混淆矩阵:")
print(confusion_matrix(y_test, y_pred))

print("\n分类报告:")
print(classification_report(y_test, y_pred))
