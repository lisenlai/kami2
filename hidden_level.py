"""
隐藏关卡选择
"""
import json
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QApplication, QPushButton, QLabel
from PySide6.QtGui import QIcon, QPixmap, QImage
import functools
from pathlib import Path
import assets, hidden_imgs

SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640


class HLevel(QLabel):
    # 隐藏关卡模块
    redirect_home = Signal(int)
    redirect_hidden_game = Signal(int)
    def __init__(self, type="旅程"):
        super().__init__()

        self.setWindowTitle("kami2")
        background = QPixmap().fromImage(QImage(":assets/background.png")).scaled(SCREEN_WIDTH,SCREEN_HEIGHT)
        # canvas.fill(Qt.green)
        self.setPixmap(background)
        self.setBaseSize(SCREEN_WIDTH,SCREEN_HEIGHT)
        with open(Path.cwd().joinpath("kami_state.json"), 'r') as f:
            self.global_state = json.load(f)

        self.home_button = QPushButton("", self)
        self.styled_button()
        self.count_level = 42
        self.current_level_imgs = [QPushButton("", self) for _ in range(5)]
        self.current_levels = [QPushButton("", self) for _ in range(5)]
        self.current_level_nums = [QLabel("", self.current_levels[i]) for i in range(5)]
        self.styled_level()
        self.bind_level()
        self.hidden_rose()


    def styled_button(self):
        # 修饰按钮
        self.home_button.clicked.connect(self.return_home)
        x, y, width, height = 20, 20, 40, 40
        self.home_button.setGeometry(x, y, width, height)
        self.home_button.setIcon(QIcon(":assets/home.png"))
        self.home_button.setIconSize(QSize(27, 27))
        self.home_button.setStyleSheet("background-color: #9cb8b5; border-radius: 20;")



    def styled_level(self):
        # 修饰关卡选择
        for i in range(5):
            x, y, width, height = (i % 3) * 115 + 16, (i // 3) * (160 + 100) + 80, 99, 160
            self.current_level_imgs[i].setGeometry(x, y, width, height)
            self.current_level_imgs[i].setIconSize(QSize(99, 160))
            x, y, width, height = (i % 3) * 115 + 16 + 20, (i // 3) * (160 + 100) + 80 + 170, 60, 60
            self.current_levels[i].setGeometry(x, y, width, height)
            self.current_levels[i].setIconSize(QSize(60, 60))
            self.current_levels[i].setStyleSheet("background-color: rgba(0, 0, 0, 0%);")
            x, y ,width, height = 0, 0, 60, 60
            
            self.current_level_nums[i].setGeometry(x, y, width, height)
            self.current_level_nums[i].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.current_level_nums[i].setStyleSheet("font-size: 18px; color: #475c53;")

    def reload_config(self, lv):
        # 导入关卡是否通过配置
        with open(Path.cwd().joinpath("kami_state.json"), 'r') as f:
            self.global_state = json.load(f)
        if self.global_state['hidden_level'][lv -1] == 2:
            self.current_levels[lv - 1].setIcon(QIcon(":assets/perfect.png"))
            self.current_level_nums[lv - 1].setText("")
        elif self.global_state['hidden_level'][lv - 1] == 1:
            self.current_levels[lv - 1].setIcon(QIcon(":assets/ok.png"))
            self.current_level_nums[lv - 1].setText("")
        else:
            self.current_levels[lv - 1].setIcon(QIcon(":assets/level.png"))
            self.current_level_nums[lv - 1].setText(str(lv))
        self.hidden_rose()

    def bind_level(self):
        # 关卡绑定数据
        for i in range(5):
            lv = i + 1
            self.current_level_imgs[i].setIcon(QIcon(":hidden_img/" + str(lv) + ".png"))
            self.current_levels[i].setIcon(QIcon(":assets/level.png"))
            self.current_level_nums[i].setText(str(lv))
            if self.global_state['hidden_level'][lv - 1] == 2:
                self.current_levels[i].setIcon(QIcon(":assets/perfect.png"))
                self.current_level_nums[i].setText("")
            elif self.global_state['hidden_level'][lv - 1] == 1:
                self.current_levels[i].setIcon(QIcon(":assets/ok.png"))
                self.current_level_nums[i].setText("")
            else:
                self.current_levels[i].setIcon(QIcon(":assets/level.png"))
                self.current_level_nums[i].setText(str(lv))
            self.current_level_imgs[i].clicked.connect(functools.partial(self.open_game, lv))
            self.current_levels[i].clicked.connect(functools.partial(self.open_game, lv))

    def return_home(self):
        # 返回首页
        self.redirect_home.emit(1)

    def open_game(self, lv=1):
        # 打开关卡对应的游戏
        self.redirect_hidden_game.emit(lv)

    def hidden_rose(self):
        # 隐藏的玫瑰关卡
        hidden = False
        for level in self.global_state['hidden_level'][:4]:
            if level == 0:
                hidden = True
                break
        if hidden:
            self.current_level_imgs[4].hide()
            self.current_levels[4].hide()
            self.current_level_nums[4].hide()
        else:
            self.current_level_imgs[4].setHidden(False)
            self.current_levels[4].setHidden(False)
            self.current_level_nums[4].setHidden(False)

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(":/assets/app_icon.ico"))
    window = HLevel()
    window.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
    window.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.show()

    app.exec_()