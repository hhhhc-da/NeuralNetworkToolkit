from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
from PySide6.QtCore import Qt
from numpy import copy
import time
import sys
import os
import schedule
import _thread
import pyautogui
import subprocess
import socket
import json
import numpy as np
from pynput import mouse
from schedule import every, repeat, run_pending
from storage import DataStorage, UsbDeviceListener, OCR
import matplotlib.pyplot as plt
from server import req
from net import Net
import cv2

THREAD_FLAG = 1

#########################################################################################################################


def on_click(x, y, button, pressed):
    # 鼠标监听
    global data, listener
    if pressed and data.running == True:
        data.pressed_position = (x, y)
        print(f'Mouse pressed at {data.pressed_position}')
    elif not pressed and data.running == True:
        data.released_position = (x, y)
        print(f'Mouse released at {data.released_position}')
        data.running = False


#########################################################################################################################
# 全局操作量
data = DataStorage()
listener = UsbDeviceListener(data)
ocr = OCR(data)
model = Net()


#########################################################################################################################
# 按钮组总控制类
class DataGroup():
    def __init__(self, load_path='data'):
        # Button 信息存储
        self.btn_label = ['确定 Pos{} 坐标'.format(
            i) for i in ['A', 'B', 'C', 'D', 'E']]
        # [X, Y, W, H] 基础计算点位坐标信息
        self.btn_data = np.zeros((9, 2), dtype=np.uint32)
        # 识别进度条位置
        self.process_bar = np.zeros((2, 2), dtype=np.uint32)

        # 文件名
        self.file_name = "_p.npy"
        self.process_name = "_s.npy"
        self.load_path = load_path

        self.load_process(self.load_path, self.file_name, self.process_name)

    def load_process(self, load_path, file_name, process_bar):
        # 后加的, 不想重构了, 分两次存取
        print('Load path: {}, file name: {}, process_bar: {}'.format(
            load_path, file_name, process_bar))
        if os.path.exists(os.path.join(load_path, file_name)):
            self.btn_data = np.load(os.path.join(load_path, file_name))
        else:
            print('未识别到有效数据, 跳过数据装载'.format(os.path.join(load_path, file_name)))

        if os.path.exists(os.path.join(load_path, process_bar)):
            self.process_bar = np.load(os.path.join(load_path, process_bar))
        else:
            print('未识别到有效数据, 跳过进度条装载'.format(
                os.path.join(load_path, process_bar)))


#########################################################################################################################
# 主窗口控制类
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("小猿口算辅助")
        self.data = DataGroup(load_path='data')

        # 创建一个中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 更新 QLabel 用
        self.labels = []

        # 创建垂直布局
        layout = QVBoxLayout()
        for i in range(4):
            label = QLabel("{}: {}".format(self.data.btn_label[i][3:7], (str(
                self.data.btn_data[i*2]) + ',' + str(self.data.btn_data[2*i+1]))))
            self.labels.append(label)
            layout.addWidget(label, alignment=Qt.AlignCenter)

        # PosE 起始坐标 (使用 pyautogui 时绘图起点)
        # label = QLabel("{}: {}".format(self.data.btn_label[4][3:7], str(self.data.btn_data[8])))
        # self.labels.append(label)
        # layout.addWidget(label, alignment=Qt.AlignCenter)

        label = QLabel("PosP: {}".format(
            (str(self.data.process_bar[0]) + ',' + str(self.data.process_bar[1]))))
        self.labels.append(label)
        layout.addWidget(label, alignment=Qt.AlignCenter)

        # 创建四个按钮
        for i in range(8):
            if i < 5:
                button = QPushButton(str(self.data.btn_label[i]))
                button.clicked.connect(
                    lambda checked, button_index=i: self.on_button_clicked(button_index))
                layout.addWidget(button)
            elif i == 5:
                self.save_btn = QPushButton("保存配置文件")
                self.save_btn.clicked.connect(self.save_profile)
                layout.addWidget(self.save_btn)
            elif i == 6:
                self.config_btn = QPushButton("获取框选矩形")
                self.config_btn.clicked.connect(
                    lambda checked, button_index=i: self.on_button_clicked(button_index))
                layout.addWidget(self.config_btn)
            elif i == 7:
                self.process_btn = QPushButton("获取进度条坐标")
                self.process_btn.clicked.connect(
                    lambda checked, button_index=i: self.on_button_clicked(button_index))
                layout.addWidget(self.process_btn)

        self.val_btn = QPushButton("采集测试")
        self.val_btn.clicked.connect(self.valication)
        layout.addWidget(self.val_btn)

        self.shoot_btn = QPushButton("开始运行程序")
        self.shoot_btn.clicked.connect(self.screen_ocr_section)
        layout.addWidget(self.shoot_btn)

        # 设置布局
        central_widget.setLayout(layout)
        
    def process_detect(self, old_pro:int):
        if old_pro >= 10:
            print("任务已完成, 不需要再阻塞")
            return 
        st = time.time()
        while True:
            # 获取进度条
            img = pyautogui.screenshot(region=(int(self.data.process_bar[0][0]), int(self.data.process_bar[0][1]),
                                                    int(self.data.process_bar[1][0]), int(self.data.process_bar[1][1])))
            result = ocr.ocr(img)
            
            if len(result.split('/')) > 1:
                data = result.split('/')
            elif len(result.split('|')) > 1:
                data = result.split('|')
            else:
                print("OCR 返回了错误信息")
                if time.time() - st > 0.4:
                    print("超时自动退出 OCR 识别模式")
                    break
                continue
            
            try:
                pro = int(data[0])
            except:
                print("捕获到转换时的错误, 错误未知")
                
            if time.time() - st > 0.4:
                print("超时自动退出 OCR 识别模式")
                break
            if pro >= old_pro + 1:
                print("任务已完成转换")
                return
        
    def mode_detect(self):
        # 超过 6 帧就开始运行模型, 一开始会有 4 帧左右的错误识别时间
        N = 6
        counter = N
        st = time.time()
        while True:
            # 训练的模型效果还可以我就懒得重新找超参数了, 牺牲一点速度
            img = np.array(pyautogui.screenshot(region=(0, 0, 1642, 932)), dtype=np.float32)
            # 编码变换
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # 形态变换
            img = cv2.resize(img, (128, 128))
            # 格式转换
            img = img.transpose(2, 0, 1)
            
            ret = model.predict(np.expand_dims(np.array(img, dtype=np.float32), axis=0)/255.0)[0]
            print("界面分类结果: {}".format(ret))
            if ret == 1:
                counter -= 1
                if counter <= 0:
                    print("多次检测到的开始信号")
                    return
            else:
                counter = N
                if time.time() - st > 600:
                    print("十分钟没有检测到信号, 退出阻塞状态")
                    return
            

    def valication(self):
        imgs = [pyautogui.screenshot(region=(int(self.data.btn_data[2*i][0]), int(self.data.btn_data[2*i][1]),
                                             int(self.data.btn_data[2*i+1][0]), int(self.data.btn_data[2*i+1][1]))) for i in range(4)]
        imgs.append(pyautogui.screenshot(region=(int(self.data.process_bar[0][0]), int(self.data.process_bar[0][1]),
                                                 int(self.data.process_bar[1][0]), int(self.data.process_bar[1][1]))))

        res = [ocr.ocr(img) for img in imgs]

        fig, ax = plt.subplots(1, 5, figsize=(10, 2))
        for i in range(len(imgs)):
            ax[i].imshow(imgs[i])
            ax[i].set_title('OCR: "{}"'.format(res[i]))
            ax[i].axis('off')
        plt.tight_layout()
        plt.show()

    def one_thread_processor(self):
        # 单线程处理函数
        counter = 0
        timeout = 10
        while counter < 20:
            imgs = [pyautogui.screenshot(region=(int(self.data.btn_data[2*i][0]), int(self.data.btn_data[2*i][1]),
                                                 int(self.data.btn_data[2*i+1][0]), int(self.data.btn_data[2*i+1][1]))) for i in range(4)]

            res = [ocr.ocr(img) for img in imgs]

            try:
                if int(res[0]) < int(res[1]):
                    # ocr.write(self.data.btn_data[8], '<')
                    ocr.draw("<")
                    timeout = 10

                elif int(res[0]) > int(res[1]):
                    # ocr.write(self.data.btn_data[8], '>')
                    ocr.draw(">")
                    timeout = 10

                elif int(res[0]) == int(res[1]):
                    # ocr.write(self.data.btn_data[8], '=')
                    ocr.draw("=")
                    timeout = 10

                else:
                    print("出现了程序跳转错误")
                    timeout -= 1
                    if timeout <= 0:
                        break

                counter += 1
                time.sleep(0.2)

            except Exception as e:
                print("捕捉到错误:", e)
                timeout -= 1
                if timeout <= 0:
                    break
            except:
                print("捕捉到未识别的错误")
                timeout -= 1
                if timeout <= 0:
                    break

    def multi_thread_processor(self):
        # 多线程模式, 首先我们先开启服务器, 这个需要提前点击
        counter = 0
        max_count = 20
        timeout = 2

        try:
            while counter < max_count:
                print("Counter: {}".format(counter))
                data = []

                if counter == 0:
                    print("进入块 A")
                    data = self.notify_process(req.FIRST_REQUEST)
                elif counter != 0 and counter < max_count - 1:
                    print("进入块 B")
                    data = self.notify_process(req.COMMON_REQUEST)
                elif counter > max_count - 1:
                    print("进入块 C")
                    data = self.notify_process(req.LAST_REQUEST)
                else:
                    print("进入块 D, 产生不可预测的结果")

                # output, error = server_handler.communicate()
                # print("服务线程返回: {}".format(output.decode()))

                if len(data) != 0:
                    if int(data[0]) < int(data[1]):
                        # ocr.write(self.data.btn_data[8], '<')
                        ocr.draw("<")
                        timeout = 2

                    elif int(data[0]) > int(data[1]):
                        # ocr.write(self.data.btn_data[8], '>')
                        ocr.draw(">")
                        timeout = 2

                    elif int(data[0]) == int(data[1]):
                        # ocr.write(self.data.btn_data[8], '=')
                        ocr.draw("=")
                        timeout = 2

                    else:
                        print("出现了程序跳转错误")
                        timeout -= 1
                        if timeout <= 0:
                            break

                else:
                    print("len(data) == 0, 返回数据无效")
                    timeout -= 1
                    if timeout <= 0:
                        break

                # 延时需要卡在绘制时间附近
                counter += 1
                
                
                # 阻塞到绘图任务结束
                self.process_detect(counter)
                
        except json.decoder.JSONDecodeError as e:
            print("Json 解析错误:", e)
        except Exception as e:
            print("捕捉到普通错误:", e)
        except:
            print("捕捉到未知错误")
        finally:
            print("进程被杀死")

    def screen_ocr_section(self):
        # 上一次的进程数
        self.laat_data = 0
        if THREAD_FLAG == 0:
            # 移动光标
            pyautogui.moveTo(837, 706, duration=0.01)
            pyautogui.click()
        
            self.one_thread_processor()
        else:
            # 开启服务器进程
            server_handler = subprocess.Popen(
                ['python', 'server.py']
            )

            # 阻塞式检测
            self.mode_detect()
            # 移动光标
            pyautogui.moveTo(837, 706, duration=0.01)
            pyautogui.click()
            self.multi_thread_processor()

            # # 最后不需要回收进程, 因为进程自动退出, 不放心可以再加一个
            # # server_handler.terminate()

        print("Done")

    def notify_process(self, mode: int = req.COMMON_REQUEST):
        # 请求我们需要的内容
        data = []
        if mode == req.COMMON_REQUEST:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            message = '{"code": 0}'
            print('发送字符串:', message)

            client_socket.connect(("127.0.0.1", 11451))
            client_socket.sendall(message.encode())

            response = client_socket.recv(1024).decode()
            print("接收字符串: {}".format(response))

            data = json.loads(response)["data"]

        elif mode == req.FIRST_REQUEST:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            message = '{' + '"code": 1,"count": 10,"pos": {}'.format(
                self.data.btn_data[0:9, :].tolist()) + '}'
            print('发送字符串:', message)

            client_socket.connect(("127.0.0.1", 11451))
            client_socket.sendall(message.encode())

            response = client_socket.recv(1024).decode()
            print("接收字符串: {}".format(response))

            data = json.loads(response)["data"]

        elif mode == req.LAST_REQUEST:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            message = '{"code": 2}'
            print('发送字符串:', message)

            client_socket.connect(("127.0.0.1", 11451))
            client_socket.sendall(message.encode())

            response = client_socket.recv(1024).decode()
            print("接收字符串: {}".format(response))

            data = json.loads(response)["data"]

        elif mode == req.RETRY_REQUEST:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            message = '{"code": 3}'
            print('发送字符串:', message)

            client_socket.connect(("127.0.0.1", 11451))
            client_socket.sendall(message.encode())

            response = client_socket.recv(1024).decode()
            print("接收字符串: {}".format(response))

            data = json.loads(response)["data"]

        else:
            print("错误的请求码")
            return []

        return data

    def save_profile(self):
        np.save(os.path.join(self.data.load_path,
                self.data.file_name), self.data.btn_data)
        np.save(os.path.join(self.data.load_path,
                self.data.process_name), self.data.process_bar)
        print('配置文件保存完毕')

    def on_button_clicked(self, index):
        print(f'按钮 {index + 1} 被点击!')

        listener.mouse_listener = mouse.Listener(on_click=on_click)
        data.running = True

        # 阻塞式监听鼠标
        while (data.pressed_position is None or data.released_position is None):
            if data.released_position is not None:
                print('鼠标按下事件记录失败')
                data.clear()

                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("记录失败")
                msg.setIcon(QMessageBox.Critical)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return
            time.sleep(0.1)

        if index < 4:
            self.data.btn_data[index*2] = np.array(
                [min(data.pressed_position[i], data.released_position[i]) for i in range(2)], dtype=np.uint32)
            self.data.btn_data[index*2+1] = np.array(
                [abs(data.pressed_position[i] - data.released_position[i]) for i in range(2)], dtype=np.uint32)
            self.labels[index].setText("{}: {}".format(self.data.btn_label[index][3:7], (str(
                self.data.btn_data[index*2]) + ',' + str(self.data.btn_data[index*2+1]))))
        # elif index == 4:
        #     self.data.btn_data[8] = np.array((copy(data.pressed_position) + copy(data.released_position))/2, dtype=np.uint16).tolist()
        #     self.labels[index].setText("{}: {}".format(self.data.btn_label[index][3:7], (str(self.data.btn_data[8]))))
        elif index == 6:
            msg = QMessageBox()
            msg.setWindowTitle("框选结果")
            msg.setText("起点: {}\n终点: {}".format(
                data.pressed_position, data.released_position))
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        elif index == 7:
            self.data.process_bar[0] = np.array(
                [min(data.pressed_position[i], data.released_position[i]) for i in range(2)], dtype=np.uint32)
            self.data.process_bar[1] = np.array(
                [abs(data.pressed_position[i] - data.released_position[i]) for i in range(2)], dtype=np.uint32)
            self.labels[4].setText("PosP: {}".format(
                (str(self.data.process_bar[0]) + ',' + str(self.data.process_bar[1]))))

        data.clear()


#########################################################################################################################
# 主程序入口
if __name__ == "__main__":
    # 定时器任务
    @repeat(every().second)
    def schedule_task():
        global data, listener
        try:
            if data.running == False and data.status == True:
                if listener.mouse_listener is not None and listener.mouse_listener.is_alive():
                    listener.mouse_listener.stop()
                    listener.mouse_listener = None
                    print("鼠标监听事件挂起")
                data.status = False
            elif data.running == True and data.status == False:
                if listener.mouse_listener is not None:
                    listener.mouse_listener.start()
                data.status = True
                print("鼠标监听事件启动")
        except Exception as e:
            print("捕获到", e)
        except:
            print("schedule_task 意外捕获事件")

    # 线程任务
    def thread_task_schedule(time_check):
        print("线程 thread_task_schedule 启动, 轮训时间: {:.2f}".format(time_check))
        while True:
            run_pending()
            time.sleep(time_check)

    # 注册轮训服务
    def register_service():
        schedule.every(1).seconds.do(schedule_task)

    # 开始运行
    register_service()
    _thread.start_new_thread(thread_task_schedule, ((0.5,)))

    print('开始渲染 UI 界面')
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()

    code = app.exec()
    print("退出主程序, 开始回收内存")

    del listener
    del ocr
    del data

    sys.exit(code)
