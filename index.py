"""
首页，在此选择进入旅程或隐藏模块
"""
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QApplication, QPushButton, QLabel
from PySide6.QtGui import QIcon, QPixmap, QImage
from pathlib import Path
import assets


SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'kami2'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class Index(QLabel):
    # 首页，选择旅程或隐藏模块
    redirect_travel = Signal(int)
    redirect_hidden = Signal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("kami2")
        background = QPixmap().fromImage(QImage(":/assets/background.png")).scaled(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.setPixmap(background)
        self.setBaseSize(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.travel_button = QPushButton("", self)
        self.hidden_button = QPushButton("", self)
        self.styled_buttons()
        self.travel_button.clicked.connect(self.open_travel)
        self.hidden_button.clicked.connect(self.open_hidden)

    def styled_buttons(self):
        # 修饰按钮
        width = 200
        height = 200
        x = 80
        y1 = 50 + 20
        y2 = y1 + height + 40
        self.travel_button.setGeometry(x, y1, width, height)
        self.hidden_button.setGeometry(x, y2, width, height)
        self.travel_button.setIcon(QIcon(':/assets/travel.png'))
        self.hidden_button.setIcon(QIcon(':/assets/hidden.png'))
        self.travel_button.setIconSize(QSize(200, 200))
        self.hidden_button.setIconSize(QSize(200, 200))
        self.travel_button.setStyleSheet("background-color: rgba(0, 0, 0, 0%);")
        self.hidden_button.setStyleSheet("background-color: rgba(0, 0, 0, 0%);")

    def open_travel(self):
        # 打开旅程关卡选择页面
        self.redirect_travel.emit(-1)

    def open_hidden(self):
        # 打开隐藏关卡选择页面
        self.redirect_hidden.emit(-1)

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(":/assets/app_icon.ico"))
    window = Index()
    window.show()

    app.exec_()