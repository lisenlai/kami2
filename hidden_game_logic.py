"""
隐藏关卡游戏内部逻辑
"""
from collections import deque
import copy
from pathlib import Path

class Env:
    # 搭建游戏环境
    def __init__(self):
        self.color_nums = 0
        self.state = []
        self.color_rgbs = []
        self.init_state = []

    def init_game(self, part=1):
        if not self.init_state:
            self.load_config_file(Path.cwd().joinpath("hidden_config/" + str(part)))
            self.init_state = copy.deepcopy(self.state)
        else:
            self.state = copy.deepcopy(self.init_state)
        return self.state, self.min_steps, self.color_nums, self.color_rgbs

    def load_config_file(self, file):
        # 导入游戏状态文件
        self.state = []
        with open(file, 'r') as f:
            lines = f.readlines()
            self.color_nums = int(lines[0])
            self.min_steps = int(lines[1])
            # color_rgbs = []
            for i in range(self.color_nums):
                self.color_rgbs.append(eval(lines[i+2]))
            for line in lines[self.color_nums+2:]:
                self.state.append(eval(line))
        return self.state, self.min_steps, self.color_nums, self.color_rgbs

    def get_game_state(self):
        # 获取游戏状态
        return self.state, self.color_nums, self.color_rgbs

    def game_over(self):
        # 判断游戏是否结束
        color = self.state[0][0]
        for row in self.state:
            for item in row:
                if item != color: 
                    return False
        return True

    def append_deq(self, deq, row, column, color):
        if (row, column) not in deq:
            deq.append((row, column))
            self.state[row][column] = color
            
    def change_color(self, row, column, color):
        # 使用一种不同颜色点击矩形块带来的影响
        if self.state[row][column] == color:
            return self.state, False, False
        before_color = self.state[row][column]
        deq = deque()
        deq.append((row, column))
        self.state[row][column] = color
        while len(deq) != 0:
            row, column = deq.pop()
            if row - 1 >= 0 and self.state[row - 1][column] == before_color:
                self.append_deq(deq, row - 1, column, color)
            if row + 1 < 116 and self.state[row + 1][column] == before_color:
                self.append_deq(deq, row + 1, column, color)
            if column - 1 >= 0 and self.state[row][column - 1] == before_color:
                self.append_deq(deq, row, column - 1, color)
            if column + 1 < 72 and self.state[row][column + 1] == before_color:
                self.append_deq(deq, row, column + 1, color)
        if self.game_over():
            return self.state, True, True
        else:
            return self.state, True, False