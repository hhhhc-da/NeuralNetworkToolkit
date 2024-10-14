# coding=utf-8
import time
import os
from pynput import keyboard
import pyautogui

# 我们要训练一个 Convolution neural network 用来判断是否结束
running, main_running = False, True
counter = 0

folder_path = os.path.join("traindata", "unform", "image")


def on_press(key):
    global running, main_running

    try:
        if key.char == 'q' and running == True:
            print('键盘监听确认: q, 暂停操作')
            running = False
            return True  # 保持监听状态
        if key.char == 'i' and running == False:
            print('键盘监听确认: i, 开始保存信息')
            running = True
            return True  # 保持监听状态
        if key.char == 'd':
            print('键盘监听确认: d, 退出')
            running = False
            main_running = False
            return False  # 挂起监听状态
    except AttributeError:
        pass


key = keyboard.Listener(on_press=on_press)
try:
    print("开始监听")
    key.start()
    while main_running:
        if running:
            if os.path.exists(os.path.join(folder_path, "placeholder")):
                os.remove(os.path.join(folder_path, "placeholder"))

            img = pyautogui.screenshot(region=(0, 0, 1642, 932))
            img.save(os.path.join(folder_path, "{}.png".format(counter)))
            counter += 1

        time.sleep(0.1)

finally:
    key.stop()
