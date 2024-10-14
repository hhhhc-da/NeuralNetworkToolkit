# coding=utf-8
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from dataloader import MyDataset
from torchvision.models import resnet18, ResNet18_Weights
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
import numpy as np

# 最佳参数: {'batch_size': 2, 'episode': 30, 'learning_rate': 0.01}
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
batch_size = 5
test_batch_size = 5
episode = 20
lr = 0.001
save_path = 'resnet18.pth'

model = resnet18(weights=ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 2, bias=False)
model = model.to(device)
# print('param:', list(model.parameters()))

optimizer = optim.Adam(model.parameters(), lr=lr, betas=(0.9, 0.999))
critirion = nn.CrossEntropyLoss()

if __name__ == "__main__":
    train_dataset = MyDataset(mode='train')
    train_dataloader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    test_dataset = MyDataset(mode='test')
    test_dataloader = DataLoader(
        test_dataset, batch_size=test_batch_size, shuffle=True, num_workers=0)

    losses = []
    for epoch in range(episode):
        optimizer.zero_grad()

        buf = []
        model.train()
        with tqdm(train_dataloader, desc="EPOCH {}".format(epoch)) as tbar:
            for step, (x, y) in enumerate(tbar):
                # 迁移到 CUDA
                x = x.to(device)
                y = y.to(device)

                # print("X-shape: {}, Y-shape: {}".format(x.shape, y.shape))
                output = model(x)

                # print("o:",output, ",y:", y)
                loss = critirion(output, y)

                loss.backward()

                if device == "cuda:0":
                    loss_item = loss.cpu().item()
                else:
                    loss_item = loss.item()

                buf.append(loss_item)
                losses.append(loss_item)
                tbar.set_postfix(loss=np.average(buf))

                optimizer.step()

        if (epoch + 1) % 10 == 0 or epoch == episode - 1:
            model.eval()
            buf = []
            with torch.no_grad():
                with tqdm(test_dataloader, desc="TEST") as tbar2:
                    for step, (x, y) in enumerate(tbar2):
                        # 迁移到 CUDA
                        x = x.to(device)
                        y = y.to(device)

                        # print("X-shape: {}, Y-shape: {}".format(x.shape, y.shape))
                        output = model(x)
                        # print("o:",output, ",y:", y)

                        loss = critirion(output, y)

                        if device == "cuda:0":
                            loss_item = loss.cpu().item()
                        else:
                            loss_item = loss.item()

                        buf.append(loss_item)
                        tbar2.set_postfix(loss=np.average(buf))

    torch.save(model.state_dict(), os.path.join("savedata", save_path))
    print("模型文件已保存到: {}".format(os.path.join("savedata", save_path)))

    plt.figure()
    plt.plot(losses)
    plt.show()
    print("Done.")
