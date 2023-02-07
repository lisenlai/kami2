"""
隐藏关卡中的游戏部分
"""
import json
from utils import get_rectangles, which_rectangle

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from hidden_game_logic import Env
import functools
from pathlib import Path
import assets


colors = [Qt.red, Qt.blue, Qt.green]
SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640

class HGame(QLabel):
    # 隐藏关卡游戏内容
    redirect_hidden = Signal(int)
    def __init__(self, lv=1):
        super().__init__()
        self.lv = lv
        self.setWindowTitle("kami2")
        canvas = QPixmap(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.setPixmap(canvas)
        self.env = Env()
        
        self.rectangle_colors, self.min_steps, self.colors, self.color_rgbs = self.env.init_game(self.lv)
        self.current_step = self.min_steps
        self.qcolors = [QColor(*rgb) for rgb in self.color_rgbs]
        self.current_color_index = 0
        self.rectangles = get_rectangles()
        self.draw_rectangles()
        self.draw_handle_buttons()
        self.draw_color_buttons()
        self.mousePressEvent = self.pressEvent
        with open(Path.cwd().joinpath("kami_state.json"), 'r') as f:
            self.global_state = json.load(f)

    def pressEvent(self, QMouseEvent):
        # 鼠标点击事件
        if QMouseEvent.buttons() != Qt.LeftButton:   ##判断是否鼠标左键点击
            return
        pos = QMouseEvent.pos()
        row, column = which_rectangle(pos.x(), pos.y())
        color_index = self.current_color_index
        self.rectangle_colors, valid, done = self.env.change_color(row, column, color_index)
        if not valid:
            return 
        self.current_step -= 1
        self.step_button.setText(str(self.current_step))
        self.draw_rectangles()
        if done:
            reload_config = -1
            if self.current_step >= 0:
                if self.global_state["hidden_level"][self.lv - 1] < 2:
                    self.global_state["hidden_level"][self.lv - 1] = 2
                    with open(Path.cwd().joinpath("kami_state.json"), 'w') as f:
                        json.dump(self.global_state, f)
                    reload_config = self.lv
            else:
                if self.global_state["hidden_level"][self.lv - 1] == 0:
                    self.global_state["hidden_level"][self.lv - 1] = 1
                    with open(Path.cwd().joinpath("kami_state.json"), 'w') as f:
                        json.dump(self.global_state, f)
                    reload_config = self.lv
            self.back(reload_config)
        
    def draw_rectangles(self):
        # 绘制矩形块
        canvas = self.pixmap()
        painter = QPainter(canvas)
        width, height = 5, 5
        for i, row in enumerate(self.rectangle_colors):
            y = i * 5
            for j, rectangle in enumerate(row):
                brush = QBrush()
                color = self.qcolors[self.rectangle_colors[i][j]]
                brush.setColor(color)
                brush.setStyle(Qt.SolidPattern)
                painter.setBrush(brush)
                pen = QPen()
                pen.setStyle(Qt.PenStyle.SolidLine)
                pen.setWidth(0)
                pen.setColor(color)
                painter.setPen(pen)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                x = j * 5
                painter.drawRect(x, y, width, height)
        painter.end()
        self.setPixmap(canvas)

    def selectColor(self, index):
        # 选择一种颜色
        self.current_color_index = index
        width = (SCREEN_WIDTH - 108) // self.colors
        x, y = 108 + width * (index + 1) - 20,  580
        if index == self.colors - 1:
            x = SCREEN_WIDTH - 20
        self.selected_color_button.setGeometry(x, y, 20, 20)

    def draw_handle_buttons(self):
        # 绘制各个操作按钮
        width = 36
        height = SCREEN_HEIGHT - 580
        icons = [":/assets/back.png", "", ":/assets/refresh.png"]
        funcs = [functools.partial(self.back, -1), None, self.refresh, self.tip]
        for i in range(3):
            x = i * width
            y = 580
            button = QPushButton("", self)
            button.setStyleSheet("border: 0; background-color: #241b0d;")
            button.setIcon(QIcon(icons[i]))
            button.setIconSize(QSize(60, 60))
            button.setGeometry(x, y, width, height)
            if i < 2:
                button.setStyleSheet("border: 0; background-color: #241b0d; border-right: 1px solid white; color: white; font-size: 22px;")
            if i == 1:
                button.setText(str(self.current_step))
                self.step_button = button
            button.clicked.connect(funcs[i])
    
    def draw_color_buttons(self):
        # 画颜色按钮，并添加监听器
        # canvas = self.pixmap()
        width = (SCREEN_WIDTH - 108) // self.colors
        height = SCREEN_HEIGHT - 580
        for i in range(self.colors):
            x = 108 + i * width
            y = 580
            button = QPushButton("", self)
            button.setStyleSheet("border: 0; background-color: rgb" + str(self.color_rgbs[i])+"; border-top: 1px dotted #241b0d;")
            if i == self.colors - 1:
                colors_width = SCREEN_WIDTH - 108
                width = colors_width - (colors_width // self.colors) * i
            button.setGeometry(x, y, width, height)
            button.clicked.connect(functools.partial(self.selectColor, i))
        self.selected_color_button = QPushButton("", self)
        self.selected_color_button.setIcon(QIcon(':/assets/selected.png'))
        self.selected_color_button.setIconSize(QSize(30, 30))
        self.selectColor(0)

    def back(self, reload_config):
        self.redirect_hidden.emit(reload_config)

    def refresh(self):
        # 重新开始该游戏
        self.rectangle_colors, self.min_steps, self.colors, self.color_rgbs = self.env.init_game(self.lv)
        self.current_step = self.min_steps
        self.current_color_index = 0
        self.step_button.setText(str(self.current_step))
        self.draw_rectangles()
        

    def tip(self):
        print("tip")
        pass

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(":/assets/app_icon.ico"))
    gameLabel = HGame(3)
    mainWindow = QMainWindow()
    mainWindow.setCentralWidget(gameLabel)
    mainWindow.show()

    app.exec_()
