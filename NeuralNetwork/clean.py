# coding=utf-8
import os
import argparse

# 本文件用于清理多余的 txt 文件
parser = argparse.ArgumentParser(description="Data sample project")
parser.add_argument('-m', type=str, default='ALL', help='ALL, UNFORM, FORM')
args = parser.parse_args()

if args.m == "ALL" or args.m == "UNFORM":
    print("开始清理未归类的数据")
    image_path = os.path.join("traindata", "unform", "image")
    label_path = os.path.join("traindata", "unform", "label")

    try:
        if len(os.listdir(image_path)) == 0:
            raise RuntimeError("没有未加入数据包的数据")

        if len(os.listdir(image_path)) >= len(os.listdir(label_path)):
            raise RuntimeError("本情景不适合清理 UNFORM LABEL")

        image_filename = [os.path.splitext(name)[0]
                          for name in os.listdir(image_path)]

        for name in os.listdir(label_path):
            if os.path.splitext(name)[0] not in image_filename:
                os.remove(os.path.join(label_path, name))
                print("已删除 {}".format(os.path.join(label_path, name)))

        print("未归类 Label 清理完毕")
    except RuntimeError as r:
        print("截获 RuntimeError:", r)
    except Exception as e:
        print("截获 Exception:", e)
    except:
        raise RuntimeError("Fatal Error: 截获到未预料的异常")

if args.m == "ALL" or args.m == "FORM":
    print("开始清理已归类的数据")

    for mode in ["train", "test"]:
        image_path = os.path.join("traindata", "image", mode)
        label_path = os.path.join("traindata", "label", mode)

        try:
            if len(os.listdir(image_path)) == 0:
                raise RuntimeError("没有加入数据包的数据")

            if len(os.listdir(image_path)) >= len(os.listdir(label_path)):
                print("IMAGE 个数: {}, LABEL 个数: {}".format(
                    len(os.listdir(image_path)), len(os.listdir(label_path))))
                raise RuntimeError("本情景不适合清理 FORM LABEL")

            image_filename = [os.path.splitext(
                name)[0] for name in os.listdir(image_path)]

            for name in os.listdir(label_path):
                if os.path.splitext(name)[0] not in image_filename:
                    os.remove(os.path.join(label_path, name))
                    print("已删除 {}".format(os.path.join(label_path, name)))

            print("LABEL (Mode: {}) 清理完毕".format(mode))
        except RuntimeError as r:
            print("截获 RuntimeError:", r)
        except Exception as e:
            print("截获 Exception:", e)
        except:
            raise RuntimeError("Fatal Error: 截获到未预料的异常")

print("Done.")
