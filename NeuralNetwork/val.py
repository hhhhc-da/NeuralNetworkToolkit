# coding=utf-8
import torch
from torch import nn
from torchvision.models import resnet18
import numpy as np
import cv2
import os
import random
import matplotlib.pyplot as plt


class Net():
    def __init__(self):
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        self.save_path = os.path.join('savedata', 'resnet18.pth')

        self.model = resnet18()
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


if __name__ == "__main__":
    model = Net()

    label_filename = [i for i in os.listdir(
        os.path.join("traindata", "image", "test")) if i != "placeholder"]
    if len(label_filename) == 0:
        raise RuntimeError("没有要测试的数据, 请确认数据集完好")

    pack = random.sample(label_filename, 4)
    org, img_data = [], []

    for i in range(4):
        image = cv2.imread(os.path.join("traindata", "image", "test", pack[i]))
        org.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        image = cv2.resize(image, (128, 128))
        image = image.transpose(2, 0, 1)

        img_data.append(image)

    images = np.array(img_data, dtype=np.float32)/255.0

    result = model.predict(images)

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    for i in range(4):
        ax[i//2][i % 2].imshow(org[i])
        ax[i//2][i % 2].set_title("Pred: {}".format(result[i]))
        ax[i//2][i % 2].axis('off')
    plt.tight_layout()
    plt.show()
