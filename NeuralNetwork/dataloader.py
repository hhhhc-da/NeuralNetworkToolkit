# coding=utf-8
import os
import torch
from torch.utils.data import Dataset
import cv2
import numpy as np


class MyDataset(Dataset):
    def __init__(self, root_dir="traindata", mode="train"):
        Dataset.__init__(self)

        self.mode = mode
        self.root_dir = root_dir
        self.image_dir = os.path.join(self.root_dir, "image", self.mode)
        self.label_dir = os.path.join(self.root_dir, "label", self.mode)

        self.image_file = os.listdir(self.image_dir)
        self.length = len(self.image_file)

        # 检查, 如果 analyze 过了可以省略
        if len(self.image_dir) != len(self.label_dir) and len(self.image_dir) > 0:
            raise RuntimeError("Fatal Error: 文件个数不匹配")

        # 将所有图片数据加载, 因为有黑白两种照片, 不适合标准化
        # 我们使用 Min-Max 归一化

        self.images = []
        self.labels = []

        for image_path in self.image_file:
            image = cv2.imread(os.path.join(self.image_dir, image_path))
            image = cv2.resize(image, (128, 128))
            image = image.transpose(2, 0, 1)

            self.images.append(np.array(image, dtype=np.float32)/255.0)

            with open(os.path.join(self.label_dir, image_path[:-4] + ".txt"), "r") as f:
                l = int(f.read())
                f.close()

                self.labels.append(l)

                # if l == 0:
                #     self.labels.append(np.array([1,0], dtype=np.float32))
                # elif l == 1:
                #     self.labels.append(np.array([0,1], dtype=np.float32))
                # else:
                #     raise RuntimeError("Unknown label")

        # 转换为 torch.FloatTensor
        self.images = torch.tensor(self.images, dtype=torch.float32)
        self.labels = torch.tensor(self.labels, dtype=torch.long)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        return self.images[idx], self.labels[idx]

    def data(self):
        return np.array(self.images, dtype=np.float32), np.array(self.labels, dtype=np.long)
