# coding=utf-8
import time
import pyautogui
import json
import socket
from storage import DataStorage, OCR
import matplotlib.pyplot as plt


class req():
    # 普通消息
    COMMON_REQUEST = 0
    # 首次访问消息
    FIRST_REQUEST = 1
    # 最后一次请求消息
    LAST_REQUEST = 2
    # 重新读取当前题目消息
    RETRY_REQUEST = 3

# 规定我们的接收消息体, 本质就是一个消息队列
# {
#     "code": req.FIRST_REQUEST,
#     "count": 10,
#     "pos": [[1,2],[2,3],[1,2],[2,3],[1,2],[2,3],[1,2],[2,3]]
# }
# {
#     "code": req.COMMON_REQUEST, # 表示这是中间发送次数, 需要返回下一次的计算数据
# }
# {
#     "code": req.LAST_REQUEST, # 表示这是最后一次发送数据, Server 应自行关闭
# }

# 规定我们的发送消息体, 这个需要用到 Json 作为处理, 标准化格式输出
# {
#     "code": req.FIRST_REQUEST,
#     "length": 4,
#     "data": [6, 8, 5, 5]
# }
# {
#     "code": req.COMMON_REQUEST,
#     "length": 2,
#     "data": [5, 4],
#     "plus": 0
# }
# {
#     "code": req.LAST_REQUEST,
#     "length": 0,
#     "data": []
# }


# 我们要预先存储好我们下一步需要返回的内容, 存储字符串
pre_data = ""

# 这边只处理单个识别任务
data = DataStorage()
ocr = OCR(data)

counter = 0
pos = []


def tcp_server(host='127.0.0.1', port=11451):
    # 介于我们只有一个应用访问, 怎么写无所谓了
    global counter, pos, pre_data
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((host, port))
        server_socket.listen()
        print('TCP 服务启动: IP:PORT {}:{}'.format(host, port))

        while True:
            client_socket, addr = server_socket.accept()
            print("Addr:", addr)

            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                data = data.decode()
                print('接收到数据: {}'.format(data))  # 调试时使用

                # 从这里开始正式解释 Json 文件
                json_data = json.loads(data)

                code = json_data["code"]
                if code == req.FIRST_REQUEST:
                    # 记录我们的次数和坐标
                    counter = json_data["count"]
                    pos = json_data["pos"]
                    print("Counter: {}, Pos: {}".format(counter, pos))

                    # 截图并保存结果
                    while True:
                        imgs = [pyautogui.screenshot(region=(int(pos[2*i][0]), int(pos[2*i][1]),
                                                             int(pos[2*i+1][0]), int(pos[2*i+1][1]))) for i in range(2)]
                        res = [ocr.ocr(img) for img in imgs]

                        if res[0].isdigit() and res[1].isdigit():
                            res = [int(r) for r in res]
                            break
                        else:
                            print("首次识别未识别到有效数字")
                            time.sleep(0.5)

                    # 最速拼接字符串
                    jstr = "{" + \
                        '"code":{}, "length":2,"data":{}'.format(
                            code, res) + '}'
                    # 这里有一个假设，那就是你的题目数必须大于等于 2
                    counter -= 1
                    client_socket.sendall(jstr.encode())

                    # 开始解析下一步过程, 第一步不需要延时
                    timeout = 10
                    if counter < 1:
                        print("次数已终止")
                        raise RuntimeError("正常退出")
                    while counter > 0:
                        imgs = [pyautogui.screenshot(region=(int(pos[2*i][0]), int(pos[2*i][1]),
                                                             int(pos[2*i+1][0]), int(pos[2*i+1][1]))) for i in range(2, 4)]
                        res = [ocr.ocr(img) for img in imgs]

                        # 准备下一步内容
                        if res[0].isdigit() and res[1].isdigit():
                            res = [int(r) for r in res]

                            pre_data = "{" + \
                                '"code":{}, "length":2,"data":{}'.format(
                                    code, res) + '}'
                            print("更新 PreData:", pre_data)
                            break
                        else:
                            pre_data = ""
                            timeout -= 1
                            if timeout == 0:
                                print("超出重试限制时间")
                                break

                            print("识别下一步数字失败, 重试中")

                elif code == req.COMMON_REQUEST:
                    # 如果存在上一步数据就直接发回去
                    if pre_data != "":
                        print("PreData:", pre_data)
                        print("成功读取上一步数据")
                    else:
                        print("没有上一步数据！重新采样")

                        while True:
                            imgs = [pyautogui.screenshot(region=(int(pos[2*i][0]), int(pos[2*i][1]),
                                                                 int(pos[2*i+1][0]), int(pos[2*i+1][1]))) for i in range(2)]
                            res = [ocr.ocr(img) for img in imgs]

                            if res[0].isdigit() and res[1].isdigit():
                                res = [int(r) for r in res]

                                pre_data = "{" + \
                                    '"code":{}, "length":2,"data":{}'.format(
                                        code, res) + '}'
                                break
                            else:
                                print("识别下一步数字失败, 重试中")
                                pre_data = ""

                    client_socket.sendall(pre_data.encode())
                    counter -= 1


                    timeout = 10
                    if counter < 1:
                        print("次数已终止")
                        raise RuntimeError("正常退出")
                    while counter > 0:
                        imgs = [pyautogui.screenshot(region=(int(pos[2*i][0]), int(pos[2*i][1]),
                                                             int(pos[2*i+1][0]), int(pos[2*i+1][1]))) for i in range(2, 4)]
                        res = [ocr.ocr(img) for img in imgs]

                        # 准备下一步内容
                        if res[0].isdigit() and res[1].isdigit():
                            res = [int(r) for r in res]

                            pre_data = "{" + \
                                '"code":{}, "length":2,"data":{}'.format(
                                    code, res) + '}'
                            break
                        else:
                            print("识别下一步数字失败, 重试中")
                            pre_data = ""
                            timeout -= 1
                            if timeout <= 0:
                                print("超出重试限制时间")
                                break
                            time.sleep(0.1)

                elif code == req.LAST_REQUEST:
                    print("接收到退出信号")

                    resp = "{" + \
                        '"code":{}, "length":0,"data":[]'.format(code) + '}'
                    client_socket.sendall(resp.encode())

                    time.sleep(1)
                    raise KeyboardInterrupt()

            print('处理完一个事件')

    # 最后要请求一下端口, 让端口解除阻塞状态才行
    except KeyboardInterrupt:
        print("接收到 KeyboardInterrupt, 程序退出")
    except RuntimeError as e:
        print("接收到 RuntimeError:", e)
    except:
        print("捕获到未知异常, 程序退出")
    finally:
        server_socket.close()
        print("解除端口绑定")


if __name__ == '__main__':
    tcp_server()
