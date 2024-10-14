# coding=utf-8
import matplotlib.pyplot as plt
import os

# 全局存储柱形图
bar_data = {
    "UNFORM 0": 0,
    "UNFORM 1": 0,
    "FORM 0 (train)": 0,
    "FORM 1 (train)": 0,
    "FORM 0 (test)": 0,
    "FORM 1 (test)": 0,
}

# 首先，我们先分析一下未归类的数据
print("开始分析未归类数据")
image_path = os.path.join("traindata", "unform", "image")
label_path = os.path.join("traindata", "unform", "label")

try:
    paths = [i for i in os.listdir(image_path) if i != "placeholder"]
    if len(paths) == 0:
        raise RuntimeError("没有未加入数据包的数据")

    label_filename = [i for i in os.listdir(label_path) if i != "placeholder"]
    if len(label_filename) == 0:
        raise RuntimeError("未加入数据包的数据未打标签")

    for txt in label_filename:
        with open(os.path.join(label_path, txt), "r") as f:
            x = int(f.read())

            if x == 0:
                bar_data["UNFORM 0"] += 1
            elif x == 1:
                bar_data["UNFORM 1"] += 1
            else:
                print("意外读取到 x:", x)
                raise RuntimeError("读取 LABEL 存储的数据格式不符")

except RuntimeError as r:
    print("截获 RuntimeError:", r)
except Exception as e:
    print("截获 Exception:", e)
except:
    raise RuntimeError("Fatal Error: 截获到未预料的异常")


print("开始分析已归类数据")
image_path = os.path.join("traindata", "image")
label_path = os.path.join("traindata", "label")
modes = ['train', 'test']


for i in range(len(modes)):
    try:
        paths = [i for i in os.listdir(os.path.join(
            image_path, modes[i])) if i != "placeholder"]

        if len(paths) == 0:
            raise RuntimeError("没有已加入 {} 数据包的数据".format(modes[i]))

        label_filename = [i for i in os.listdir(
            os.path.join(label_path, modes[i])) if i != "placeholder"]
        for txt in label_filename:
            with open(os.path.join(label_path, modes[i], txt), "r") as f:
                x = int(f.read())

                if x == 0:
                    bar_data["FORM 0 ({})".format(modes[i])] += 1
                elif x == 1:
                    bar_data["FORM 1 ({})".format(modes[i])] += 1
                else:
                    print("读取: {}".format(
                        os.path.join(label_path, modes[i], txt)))
                    raise RuntimeError("读取 LABEL 存储的数据格式不符")

    except RuntimeError as r:
        print("截获 RuntimeError:", r)
    except Exception as e:
        print("截获 Exception:", e)
    except:
        raise RuntimeError("Fatal Error: 截获到未预料的异常")

plt.figure(figsize=(10, 5))
plt.bar(bar_data.keys(), bar_data.values(), color='skyblue')

plt.title('Data Analyzation Bar Image')
plt.xlabel('Type')
plt.ylabel('Count')
plt.tight_layout()

print("Done.")
plt.show()
