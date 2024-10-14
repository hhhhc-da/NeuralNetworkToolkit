# coding=utf-8
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

scale = (800, 600)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("可视化标签工具")
        self.setGeometry(100, 100, 400, 300)

        # 创建中心部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.data_dir = os.path.join('traindata', 'unform', 'image')
        self.label_dir = os.path.join('traindata', 'unform', 'label')
        self.image_filename = os.listdir(self.data_dir)

        if os.path.exists(os.path.join(self.label_dir, "placeholder")):
            os.remove(os.path.join(self.label_dir, "placeholder"))

        self.now_image = 0
        self.total_length = len(self.image_filename)
        if self.total_length == 0:
            print("没有未分类数据")

        if self.total_length > 0:
            self.process = QLabel(
                "进度: {}/{}".format(self.now_image+1, self.total_length))
        else:
            self.process = QLabel(
                "进度: {}/{}".format(self.now_image, self.total_length))
        layout.addWidget(self.process, alignment=Qt.AlignCenter)

        # 图片组
        self.image_label = QLabel()

        if len(self.image_filename) > 0:
            pixmap = QPixmap(os.path.join(
                self.data_dir, self.image_filename[0]))
            pixmap = pixmap.scaled(scale[0], scale[1])
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setPixmap(QPixmap())

        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # 按钮组
        self.button1 = QPushButton("是其他图片")
        self.button1.clicked.connect(lambda: self.button_clicked(0))
        self.button2 = QPushButton("是目标图片")
        self.button2.clicked.connect(lambda: self.button_clicked(1))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)

        layout.addLayout(button_layout)

        central_widget.setLayout(layout)

    def button_clicked(self, index):
        # 图片路径 self.data_dir, 标签路径 self.label_dir
        txt_filename = self.image_filename[self.now_image][:-4] + ".txt"
        with open(os.path.join(self.label_dir, txt_filename), 'w+') as f:
            f.write(str(index))
            f.close()
        print('保存文件 {}, 标签: {}'.format(os.path.join(
            self.label_dir, txt_filename), index))

        if self.now_image < self.total_length - 1:
            self.now_image += 1

            # 显示新的图片
            png_filename = self.image_filename[self.now_image]
            pixmap = QPixmap(os.path.join(self.data_dir, png_filename))
            pixmap = pixmap.scaled(scale[0], scale[1])
            self.image_label.setPixmap(pixmap)

            # 更新进度显示
            self.process.setText(
                "进度: {}/{}".format(self.now_image+1, self.total_length))
        else:
            self.process.setText("已完成".format(
                self.now_image+1, self.total_length))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
