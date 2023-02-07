from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QIcon, QPixmap, QImage
from pathlib import Path
import assets

SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640


class StartLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("kami2")
        background = QPixmap().fromImage(QImage(":/assets/welcome.png")).scaled(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.setPixmap(background)

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon(":/assets/app_icon.ico"))
    window = StartLabel()
    window.show()

    app.exec()