# coding=utf-8
import pyautogui
import ddddocr
import time
from pynput import keyboard  # , mouse
# from schedule import every, repeat, run_pending
# import schedule
# import _thread

#########################################################################################################################
# # 鼠标监听
# def on_click(x, y, button, pressed):
#     global data, listener
#     if pressed and data.running == True:
#         data.pressed_position = (x, y)
#         print(f'Mouse pressed at {data.pressed_position}')
#     elif not pressed and data.running == True:
#         data.released_position = (x, y)
#         print(f'Mouse released at {data.released_position}')

# # 键盘监听
# def on_press(key):
#     global data, listener

#     try:
#         if key.char == 'q' and data.running == True:
#             print('键盘监听确认: q')
#             data.running = False
#             return True # 保持监听状态
#         if key.char == 'i' and data.running == False:
#             print('键盘监听确认: i')
#             listener.mouse_listener = mouse.Listener(on_click=on_click)
#             data.running = True
#             return True # 保持监听状态
#         if key.char == 'd':
#             print('键盘监听确认: d, 两秒后清除所有信息')
#             data.running = False

#             time.sleep(2)
#             data.main_running = False

#             return False # 挂起监听状态
#     except AttributeError:
#         pass

#########################################################################################################################


class DataStorage():
    # 数据存储类
    def __init__(self):
        # OCR 模型文件
        self.model = ddddocr.DdddOcr(show_ad=False)

        # 全局文件
        self.pressed_position, self.released_position = None, None
        self.running, self.status = False, False  # 这两个量只负责监听鼠标事件
        self.main_running = True

        print("DataStorage 构造函数执行完毕")

    def clear(self):
        self.pressed_position, self.released_position = None, None

#########################################################################################################################


class UsbDeviceListener():
    # USB 设备监听类
    def __init__(self, storage: DataStorage, keyboard_callback=None):
        # 所有参数都在数据存储类里
        self.storage = storage

        # 所有监听器都在这个监听类里
        self.mouse_listener = None
        if keyboard_callback is not None:
            self.keyboard_listener = keyboard.Listener(
                on_press=keyboard_callback)
            self.keyboard_listener.start()
        else:
            self.keyboard_listener = None
        print("UsbDeviceListener 构造函数执行完毕")

    def __del__(self):
        self.remove_keyboard_listener()
        print("析构函数执行完毕")

    def remove_keyboard_listener(self):
        # 手动退出键盘监听
        if self.keyboard_listener is not None and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            print("键盘监听事件挂起")


#########################################################################################################################


class OCR():
    # OCR 主识别逻辑和动作函数类
    def __init__(self, storage: DataStorage):
        self.storage = storage
        print("OCR 构造函数执行完毕")

    # 连点器屏幕绘制, 加入异常处理
    def draw(self, condition: str):
        counter = 0
        while True:
            try:
                if counter > 10:
                    print("Counter 达到次数上限, Drop")
                    break

                if condition == '<':
                    pyautogui.press('f2')
                    print('按键F2被按下')
                elif condition == '>':
                    pyautogui.press('f4')
                    print('按键F4被按下')
                elif condition == '=':
                    pyautogui.press('f3')
                    print('按键F3被按下')
                else:
                    raise RuntimeError("未识别到有效字符")

                break
            except:
                print("不是正确的识别字符, 0.1s后重试")

    # pyautogui 屏幕绘制, pos 表示起始坐标, t 表示这个符号
    def write(self, pos, t: str, length: int = 10):
        start_x, start_y = pos
        pyautogui.moveTo(start_x, start_y)
        k = 1

        if t == '<':
            pyautogui.mouseDown()
            pyautogui.moveRel(-length*k, length)
            pyautogui.mouseUp()
            pyautogui.mouseDown()
            pyautogui.moveRel(length*k, length)
            pyautogui.mouseUp()
        elif t == '>':
            pyautogui.mouseDown()
            pyautogui.moveRel(length*k, length)
            pyautogui.mouseUp()
            pyautogui.mouseDown()
            pyautogui.moveRel(-length*k, length)
            pyautogui.mouseUp()
        elif t == '=':
            pyautogui.mouseDown()
            pyautogui.moveRel(length, 0)
            pyautogui.mouseUp()
            pyautogui.moveRel(0, 20)
            pyautogui.mouseDown()
            pyautogui.moveRel(-length, 0)
            pyautogui.mouseUp()
        else:
            print("Params (t) invalid")

    # OCR 识别
    def ocr(self, img):
        # st = time.time()
        res = self.storage.model.classification(img)
        # print("OCR 用时 {:.6f}s".format(time.time() - st))
        return res


# data = DataStorage()
# listener = UsbDeviceListener(data, on_click)
# ocr = OCR(data)

#########################################################################################################################
# 测试例程
# if __name__ == "__main__":
#     # 定时器任务
#     @repeat(every().second)
#     def schedule_task():
#         global data, listener
#         try:
#             if data.running == False and data.status == True:
#                 if listener.mouse_listener is not None and listener.mouse_listener.is_alive():
#                     listener.mouse_listener.stop()
#                     listener.mouse_listener = None
#                     print("鼠标监听事件挂起")
#                 data.status = False
#             elif data.running == True and data.status == False:
#                 if listener.mouse_listener is not None:
#                     listener.mouse_listener.start()
#                 data.status = True
#                 print("鼠标监听事件启动")
#         except Exception as e:
#             print("捕获到", e)
#         except:
#             print("schedule_task 意外捕获事件")

#     # 线程任务
#     def thread_task_schedule(time_check):
#         print("线程 thread_task_schedule 启动, 轮训时间: {:.2f}".format(time_check))
#         while True:
#             run_pending()
#             time.sleep(time_check)

#     # 注册轮训服务
#     def register_service():
#         schedule.every(1).seconds.do(schedule_task)

#     # 开始运行
#     register_service()
#     _thread.start_new_thread(thread_task_schedule, ((0.5,)))

#     while data.main_running:
#         time.sleep(1)

#     print("退出主程序, 开始回收内存")

#     del listener
#     del ocr
#     del data
