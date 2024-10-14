# coding=utf-8
from sklearn.model_selection import train_test_split
import os
import glob
import shutil
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Data sample project")
parser.add_argument('-p', type=float, default=0.2,
                    help='Percentage of TEST data')
args = parser.parse_args()

try:
    root_dir = 'traindata'
    split_folder = ['train', 'test']

    for t in ["image", "label"]:
        for f in split_folder:
            if not os.path.exists(os.path.join(root_dir, t, f)):
                os.mkdir(os.path.join(root_dir, t, f))

    unformed_path = os.path.join(root_dir, "unform")
    print('解析文件夹: {}'.format(unformed_path))

    image_files = [f for f in glob.glob(os.path.join(
        unformed_path, "image", "*")) if os.path.isfile(f)]

    if len(image_files) == 0:
        raise RuntimeError("没有要归类的数据")

    label_files = [f for f in glob.glob(os.path.join(
        unformed_path, "label", "*")) if os.path.isfile(f)]

    image_type = set([os.path.splitext(f)[-1] for f in image_files])
    label_type = set([os.path.splitext(f)[-1] for f in label_files])

    print("数据类型: {}, 标签类型: {}".format(list(image_type), list(label_type)))
    for i in list(label_type):
        if i not in ['.txt']:
            raise RuntimeError("出现非 .txt 类型的 Label")

    # 排查数据问题
    if len(image_files) != len(label_files):
        raise RuntimeError("数据不匹配, 请排查问题")

    # 排查完毕，接下来检查是否匹配数量
    pf = pd.DataFrame({
        "image": [i for i in image_files],
        "label": [i for i in label_files]
    })
    print(pf)

    image_name = pf['image'].apply(lambda x: x.split("\\")[-1])
    label_name = pf['label'].apply(lambda x: x.split("\\")[-1])

    if (image_name.apply(lambda x: os.path.splitext(x)[0]) != label_name.apply(lambda x: os.path.splitext(x)[0])).any():
        raise RuntimeError("Image 和 Label 名称不匹配")
    else:
        print("名称完全匹配, 开始切分数据集")

    x_train, x_test, y_train, y_test = train_test_split(
        image_name.to_list(), label_name.to_list(), test_size=args.p, random_state=42)
    print("训练集 Length: {} & {}, 测试集 Length: {} & {}, 测试集比例: {}".format(
        len(x_train), len(y_train), len(x_test), len(y_test), args.p))

    # 将训练集放入对应位置
    for name in x_train:
        origin_filename = os.path.join(unformed_path, "image", name)
        target_filename = os.path.join(root_dir, "image", "train", name)
        if os.path.exists(target_filename):
            print("发现重名文件: {}, 已覆盖".format(target_filename))
            os.remove(target_filename)

        shutil.move(origin_filename, target_filename)

    for name in y_train:
        origin_filename = os.path.join(unformed_path, "label", name)
        target_filename = os.path.join(root_dir, "label", "train", name)
        if os.path.exists(target_filename):
            print("发现重名文件: {}, 已覆盖".format(target_filename))
            os.remove(target_filename)

        shutil.move(origin_filename, target_filename)

    for name in x_test:
        origin_filename = os.path.join(unformed_path, "image", name)
        target_filename = os.path.join(root_dir, "image", "test", name)
        if os.path.exists(target_filename):
            print("发现重名文件: {}, 已覆盖".format(target_filename))
            os.remove(target_filename)

        shutil.move(origin_filename, target_filename)

    for name in y_test:
        origin_filename = os.path.join(unformed_path, "label", name)
        target_filename = os.path.join(root_dir, "label", "test", name)
        if os.path.exists(target_filename):
            print("发现重名文件: {}, 已覆盖".format(target_filename))
            os.remove(target_filename)

        shutil.move(origin_filename, target_filename)

    image_path = os.path.join("traindata", "unform", "image")
    label_path = os.path.join("traindata", "unform", "label")

    with open(os.path.join(image_path, "placeholder"), 'w+') as file:
        file.write('Hello, World!')
        file.close()

    with open(os.path.join(label_path, "placeholder"), 'w+') as file:
        file.write('Hello, World!')
        file.close()

    for mode in ["train", "test"]:
        image_path = os.path.join("traindata", "image", mode)
        label_path = os.path.join("traindata", "label", mode)

        if os.path.exists(os.path.join(image_path, "placeholder")):
            os.remove(os.path.join(image_path, "placeholder"))
        if os.path.exists(os.path.join(label_path, "placeholder")):
            os.remove(os.path.join(label_path, "placeholder"))

except RuntimeError as r:
    print("截获 RuntimeError:", r)
except Exception as e:
    print("截获 Exception:", e)
except:
    raise RuntimeError("Fatal Error: 截获到未预料的异常")

print("Done.")
