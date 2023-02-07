"""
旅程关卡中的游戏部分
"""
import json
from utils import get_center_pos, get_triangles, whichTriangle
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QPoint, Signal, QThread
from PySide6.QtWidgets import QApplication, QPushButton, QLabel
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPolygon, QColor, QBrush, QPen
from game_logic2 import Env
import functools
from utils import tran_state
import onnxruntime as ort
import numpy as np
import assets

colors = [Qt.red, Qt.blue, Qt.green]
SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640

class Thread(QThread):
    load_model_complete = Signal(int)
    def __int__(self):
        # 初始化函数
        super(Thread, self).__init__()

class Game(QLabel):
    # 旅程关卡游戏内容
    redirect_travel = Signal(int)
    def __init__(self, lv):
        super().__init__()
        self.lv = lv
        self.setWindowTitle("kami2")
        canvas = QPixmap(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.setPixmap(canvas)
        self.env = Env()
        
        self.triangle_colors, self.min_steps, self.colors, self.color_rgbs = self.env.init_game(self.lv)
        self.current_step = self.min_steps
        self.qcolors = [QColor(*rgb) for rgb in self.color_rgbs]
        self.current_color_index = 0
        self.triangles = get_triangles()
        self.draw_triangles(self.triangles)
        self.draw_handle_buttons()
        self.draw_color_buttons()
        self.tip_circle1 = QPushButton("", self)
        self.tip_circle1.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.tip_circle1.hide()
        self.tip_circle2 = QPushButton("", self)
        self.tip_circle2.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.tip_circle2.hide()
        self.tip_line1 = QPushButton("", self) # 横线
        self.tip_line1.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.tip_line1.hide()
        self.tip_line2 = QPushButton("", self)  # 竖线
        self.tip_line2.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.tip_line2.hide()
        self.mousePressEvent = self.pressEvent
        with open(Path.cwd().joinpath("kami_state.json"), 'r') as f:
            self.global_state = json.load(f)
        # self.setMenuWidget(button2)
        self.tip_thread = Thread()
        self.tip_thread.run = self.load_model
        self.tip_thread.load_model_complete.connect(self.predict)
        

        # Set the central widget of the Window.
    def pressEvent(self, QMouseEvent):
        # 鼠标点击事件
        if QMouseEvent.buttons() != Qt.LeftButton:   ##判断是否鼠标左键点击
            return
        self.hidden_tip()
        pos = QMouseEvent.pos()
        x, y = whichTriangle(pos.x(), pos.y(), self.triangles)
        color_index = self.current_color_index
        self.triangle_colors, reward, done = self.env.change_color(x, y, color_index)
        if reward == 0:
            return 
        self.current_step -= 1
        self.step_button.setText(str(self.current_step))
        self.draw_triangles(self.triangles)
        if done:
            reload_config = -1
            if self.current_step >= 0:
                if self.global_state["travel_level"][self.lv - 1] < 2:
                    self.global_state["travel_level"][self.lv - 1] = 2
                    with open(Path.cwd().joinpath("kami_state.json"), 'w') as f:
                        json.dump(self.global_state, f)
                    reload_config = self.lv
            else:
                if self.global_state["travel_level"][self.lv - 1] == 0:
                    self.global_state["travel_level"][self.lv - 1] = 1
                    with open(Path.cwd().joinpath("kami_state.json"), 'w') as f:
                        json.dump(self.global_state, f)
                    reload_config = self.lv
            self.back(reload_config)
        
        
    def draw_one_color(self, triangles_index, color):
        # 将三角块颜色变为指定颜色
        canvas = self.pixmap()
        painter = QPainter(canvas)
        for xy_index in triangles_index:
            x, y = xy_index
            triangle = self.triangles[x][y]
            points = QPolygon([
                    QPoint(*triangle[0]),
                    QPoint(*triangle[1]),
                    QPoint(*triangle[2])
                ])
            brush = QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.Dense7Pattern)
            painter.setBrush(brush)
            pen = QPen()
            pen.setWidth(0)
            pen.setStyle(Qt.PenStyle.SolidLine)
            pen.setColor(color)
            painter.setPen(pen)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.drawPolygon(points,Qt.WindingFill)
        painter.end()
        self.setPixmap(canvas)

    def draw_triangles(self, triangles):
        # 绘制三角块
        canvas = self.pixmap()
        painter = QPainter(canvas)
        for i, column in enumerate(triangles):
            for j, triangle in enumerate(column):
                points = QPolygon([
                    QPoint(*triangle[0]),
                    QPoint(*triangle[1]),
                    QPoint(*triangle[2])
                ])
                brush = QBrush()
                color = self.qcolors[self.triangle_colors[i][j]]
                brush.setColor(color)
                brush.setStyle(Qt.SolidPattern)
                painter.setBrush(brush)
                pen = QPen()
                pen.setStyle(Qt.PenStyle.SolidLine)
                pen.setWidth(0)
                pen.setColor(color)
                painter.setPen(pen)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.drawPolygon(points,Qt.WindingFill)
        painter.end()
        self.setPixmap(canvas)

    def selectColor(self, index):
        # 选择颜色
        self.current_color_index = index
        width = (SCREEN_WIDTH - 144) // self.colors
        x, y = 144 + width * (index + 1) - 20,  82 * 14 // 2
        if index == self.colors - 1:
            x = SCREEN_WIDTH - 20
        self.selected_color_button.setGeometry(x, y, 20, 20)


    def draw_handle_buttons(self):
        # 绘制操作按钮
        width = 144 // 4
        height = SCREEN_HEIGHT - 82 * 14 // 2
        icons = [":/assets/back.png", "", ":/assets/refresh.png", ":/assets/tip.png"]
        funcs = [functools.partial(self.back, -1), None, self.refresh, self.tip]
        self.handle_buttons = [QPushButton("", self) for _ in range(4)]
        for i in range(4):
            x = i * width
            y = 82 * 14 // 2
            self.handle_buttons[i].setStyleSheet("border: 0; background-color: #241b0d; color: white;")
            self.handle_buttons[i].setIcon(QIcon(icons[i]))
            self.handle_buttons[i].setIconSize(QSize(60, 60))
            self.handle_buttons[i].setGeometry(x, y, width, height)
            if i < 3:
                self.handle_buttons[i].setStyleSheet("border: 0; background-color: #241b0d; border-right: 1px solid white; color: white; font-size: 22px;")
            if i == 1:
                self.handle_buttons[i].setText(str(self.current_step))
                self.step_button = self.handle_buttons[i]
            self.handle_buttons[i].clicked.connect(funcs[i])
    
    def draw_color_buttons(self):
        # 画颜色按钮，并添加监听器
        # canvas = self.pixmap()
        width = (SCREEN_WIDTH - 144) // self.colors
        height = SCREEN_HEIGHT - 82 * 14 // 2
        for i in range(self.colors):
            x = 144 + i * width
            y = 82 * 14 // 2
            button = QPushButton("", self)
            button.setStyleSheet("border: 0; background-color: rgb" + str(self.color_rgbs[i])+"; border-top: 1px dotted #241b0d;")
            button.setGeometry(x, y, width, height)
            button.clicked.connect(functools.partial(self.selectColor, i))
        self.selected_color_button = QPushButton("", self)
        self.selected_color_button.setIcon(QIcon(':/assets/selected.png'))
        self.selected_color_button.setIconSize(QSize(30, 30))
        self.selectColor(0)

    def back(self, reload_config):
        self.redirect_travel.emit(reload_config)

    def refresh(self):
        # 重新开始游戏
        self.hidden_tip()
        self.triangle_colors, self.min_steps, self.colors, self.color_rgbs = self.env.init_game(self.lv)
        self.current_step = self.min_steps
        self.current_color_index = 0
        self.step_button.setText(str(self.current_step))
        self.draw_triangles(self.triangles)

    def predict(self):
        # 给出提示
        state = tran_state(self.triangle_colors, self.colors)
        input = np.asarray([state]).astype(np.float16)
            
        outputs = self.ort_sess.run(['output'], {'input': input})
        action = np.asarray(outputs).argmax()

        x, y, color = self.env.tran_action(action.item())
        self.handle_buttons[3].setIcon(QIcon(":./assets/tip.png"))
        self.handle_buttons[3].setText("")
        self.show_tip(x, y, color)

    def load_model(self):
        if not hasattr(self, 'ort_sess'):
            self.ort_sess = ort.InferenceSession('model/kami.onnx')
            
        self.tip_thread.load_model_complete.emit(1)
            
    def show_tip(self, x, y, color):
        # x是列数， y是行数
        width = (SCREEN_WIDTH - 144) // self.colors
        x1, y1 = 144 + width // 2 + width * color - 20, 587
        self.tip_circle1.setGeometry(x1, y1, 40, 40)
        self.tip_circle1.setStyleSheet("border-radius: 20; background: none; border: 3 solid white;")
        self.tip_circle1.setHidden(False)
        # self.tip_circle2, self.tip_line1, self.line2
        x2, y2 = get_center_pos(x, y)
        x2, y2 = x2 - 5, y2 - 5
        self.tip_circle2.setGeometry(x2, y2, 10, 10)
        self.tip_circle2.setStyleSheet("border-radius: 5; background: white;")
        self.tip_circle2.setHidden(False)

        self.tip_line2.setGeometry(x1 + 20, y2 + 5, 3, y1 - y2 - 5 )
        self.tip_line2.setStyleSheet("background: white;")
        self.tip_line2.setHidden(False)
        if x2 + 5 >= x1 + 20:
            line_x = x1 + 20
            line_width = x2 - line_x
        else:
            line_x = x2 + 10
            line_width = x1 + 20 - line_x
        self.tip_line1.setGeometry(line_x, y2 + 5, line_width, 3)
        self.tip_line1.setStyleSheet("background: white;")
        self.tip_line1.setHidden(False)


    def hidden_tip(self):
        self.tip_circle1.hide()
        self.tip_circle2.hide()
        self.tip_line1.hide()
        self.tip_line2.hide()
        

    def tip(self):
        self.handle_buttons[3].setIcon(QIcon())
        self.handle_buttons[3].setText("load")
        self.tip_thread.start()
        

    def clickTriangles(self):
        # 点击三角块
        x, y, color = 0, 0, 0
        xy_indexs, _, _ = self.env.change_color(x, y, color)
        if not xy_indexs:
            return
        canvas = self.pixmap()
        painter = QPainter(canvas)
        for xy_index in xy_indexs:
            x, y = xy_index
            triangle = self.triangles[x][y]
            points = QPolygon([
                    QPoint(*triangle[0]),
                    QPoint(*triangle[1]),
                    QPoint(*triangle[2])
                ])
            brush = QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.SolidPattern)
            painter.setBrush(brush)
            pen = QPen()
            pen.setWidthF(0)
            pen.setColor(color)
            painter.setPen(pen)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.drawPolygon(points,Qt.WindingFill)
        painter.end()
        self.setPixmap(canvas)

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(":/assets/app_icon.ico"))
    window = Game(3)
    window.show()

    app.exec_()
