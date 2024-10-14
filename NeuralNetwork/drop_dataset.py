# coding=utf-8
import os

image_path = os.path.join("traindata", "unform", "image")
label_path = os.path.join("traindata", "unform", "label")

images = os.listdir(image_path)
labels = os.listdir(label_path)

# 推倒删除
[os.remove(os.path.join(image_path, i)) for i in images]
[os.remove(os.path.join(label_path, i)) for i in labels]

with open(os.path.join(image_path, "placeholder"), 'w+') as file:
    file.write('Hello, World!')
    file.close()

with open(os.path.join(label_path, "placeholder"), 'w+') as file:
    file.write('Hello, World!')
    file.close()

print("开始执行回收任务\n{}\n{}".format(image_path, label_path))

for mode in ["train", "test"]:
    image_path = os.path.join("traindata", "image", mode)
    label_path = os.path.join("traindata", "label", mode)

    images = os.listdir(image_path)
    labels = os.listdir(label_path)

    [os.remove(os.path.join(image_path, i)) for i in images]
    [os.remove(os.path.join(label_path, i)) for i in labels]

    with open(os.path.join(image_path, "placeholder"), 'w+') as file:
        file.write('Hello, World!')
        file.close()

    with open(os.path.join(label_path, "placeholder"), 'w+') as file:
        file.write('Hello, World!')
        file.close()

    print("{}\n{}".format(image_path, label_path))

print("Done.")
