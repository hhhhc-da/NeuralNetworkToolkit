# coding=utf-8
import torch
from torch import nn
from torchvision.models import resnet18, ResNet18_Weights
import numpy as np
import os


class Net():
    def __init__(self):
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        self.save_path = os.path.join('model', 'resnet18.pth')

        self.model = resnet18(weights=ResNet18_Weights.DEFAULT)
        self.model.fc = nn.Linear(self.model.fc.in_features, 2, bias=False)
        self.model = self.model.to(self.device)

        self.model.load_state_dict(torch.load(
            self.save_path, map_location=self.device))

    @torch.no_grad
    def predict(self, x):
        self.model.eval()
        x_input = torch.tensor(x, dtype=torch.float32).to(self.device)

        outputs = self.model(x_input)
        if torch.cuda.is_available():
            predicted = torch.argmax(outputs, 1).cpu()
        else:
            predicted = torch.argmax(outputs, 1)

        return predicted.numpy().tolist()
