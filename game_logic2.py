"""
旅程关卡游戏内部逻辑
"""
import random
from collections import deque
import copy
from pathlib import Path

class Env:
    # 搭建游戏环境
    def load_config_file(self, file):
        self.state = []
        with open(file, 'r') as f:
            lines = f.readlines()
            self.colors = int(lines[0])
            self.min_steps = int(lines[1])
            self.rest_of_colors = [i for i in range(0, self.colors)]
            for i in range(self.colors):
                self.color_rgbs.append(eval(lines[i+2]))
            for line in lines[self.colors+2:]:
                self.state.append(eval(line))
        return self.state, self.min_steps, self.colors, self.color_rgbs

    def __init__(self):
        self.colors = 0
        self.rest_of_colors = []
        self.state = []
        self.color_rgbs = []
        self.init_state = []

    def init_game(self, part=1):
        # 初始化游戏
        if not self.init_state:
            self.load_config_file(Path.cwd().joinpath("config/" + str(part)))
            self.init_state = copy.deepcopy(self.state)
            self.init_colors = copy.deepcopy(self.colors)
            self.init_rest_of_colors = copy.deepcopy(self.rest_of_colors)
            self.init_color_rgbs = copy.deepcopy(self.color_rgbs)
        else:
            self.state = copy.deepcopy(self.init_state)
            self.colors = copy.deepcopy(self.init_colors)
            self.rest_of_colors = copy.deepcopy(self.init_rest_of_colors)
            self.color_rgbs = copy.deepcopy(self.init_color_rgbs)
        return self.state, self.min_steps, self.colors, self.color_rgbs

        

    def get_game_state(self):
        # 获取游戏状态
        return self.state, self.colors, self.init_color_rgbs
        

    def tran_state(self):
        # 转换游戏状态
        state = []
        for color_index in range(5):
            if color_index >= self.colors:
                state.append([[-1 for _ in range(15)] for _ in range(20)])
                continue
            types = []
            for column_index in range(20):
                column = [0 for _ in range(15)]
                if column_index % 4 == 1 or column_index % 4 == 2: 
                    column[14] = -1
                types.append(column)
            state.append(types)
        for i in range(20):
            for j in range(len(self.state[i])):
                color = self.state[i][j]
                state[color][i][j] = 1
        return state

    def random(self):
        # 产生随机游戏内容
        self.colors = random.randint(2, 5)
        self.rest_of_colors = [i for i in range(0, self.colors)]
        self.state = []

        for i in range(20):
            max_index = 14 if i % 4 == 1 or i % 4 == 2 else 15
            column = []
            for j in range(max_index):
                column.append(random.randint(0, self.colors-1))
            self.state.append(column)
        over, _ = self.game_over()
        if over:
            self.state[0][0] = (self.state[0][0] + 1) % self.colors
        return self.state, self.colors

    def game_over(self):
        # 判断游戏是否结束
        reward = -1
        for color in range(self.colors):
            if not any(color in column for column in self.state):
                if color in self.rest_of_colors:
                    self.rest_of_colors.remove(color)
                    reward = 3
            else:
                if color not in self.rest_of_colors:
                    index = len(self.rest_of_colors)
                    for i in range(len(self.rest_of_colors)):
                        if self.rest_of_colors[i] > color:
                            index = i 
                            break
                    self.rest_of_colors.insert(index, color)
        if len(self.rest_of_colors) == 1:
            return True, 10
        return False, reward

    def deque_util(self, deq, x, y, color):
        if (x, y) not in deq:
            deq.append((x, y))
            self.state[x][y] = color

    def valid(self, action):
        color = action // 300
        index = action - color * 300
        x = index // 15
        y = index % 15
        if (y == 14 and (x % 4 == 1 or x % 4 == 2)) or (color >= self.colors) or (self.state[x][y] == color):
            return False
        return True

    def change_color(self, x, y, color):
        # 使用一种不同颜色点击三角块带来的影响
        change_triangles = []
        before_color = self.state[x][y]
        if before_color == color:
            return self.state, 0, False
        deq = deque()
        deq.append((x, y))
        change_triangles.append((x, y))
        self.state[x][y] = color

        while len(deq) != 0:
            x, y = deq.pop()
            if x-1 >= 0 and len(self.state[x-1]) > y and self.state[x - 1][y] == before_color:
                self.deque_util(deq, x-1, y, color)
                if ((x-1), y) not in change_triangles:
                    change_triangles.append(((x-1), y))
            if x+1 < 20 and len(self.state[x+1]) > y and self.state[x + 1][y] == before_color:
                self.deque_util(deq, x+1, y, color)
                if ((x+1), y) not in change_triangles:
                    change_triangles.append(((x + 1), y))
            if x % 4 == 0:
                if x + 1 < 20 and y - 1 >= 0 and self.state[x+1][y-1] == before_color:
                    self.deque_util(deq, x+1, y-1, color)
            elif x % 4 == 1:
                if x - 1 >= 0 and len(self.state[x-1]) > y + 1 and self.state[x-1][y+1] == before_color:
                    self.deque_util(deq, x-1, y+1, color)
            elif x % 4 == 2:
                if x + 1 < 20 and len(self.state[x+1]) > y + 1 and self.state[x+1][y+1] == before_color:
                    self.deque_util(deq, x+1, y+1, color)
            else:
                if x - 1 >=0 and y - 1 >= 0 and self.state[x-1][y-1] == before_color:
                    self.deque_util(deq, x-1, y-1, color)
            if deq and deq[len(deq) - 1] not in change_triangles:
                change_triangles.append(deq[len(deq) - 1])
        
        done, reward = self.game_over()
        if not change_triangles:
            reward = 0
        return self.state, reward, done

    def tran_action(self, action):
        # 将action值转为可以直接使用的三角块索引和颜色
        color = action // 290
        index = action - color * 290
        four_columns = index // (29 * 2)
        index = index - four_columns * 29 * 2
        if index < 15:
            y = index
            x = four_columns * 4
        elif index < 15 + 14:
            y = index - 15
            x = four_columns * 4 + 1
        elif index < 15 + 14 + 14:
            y = index - 29
            x = four_columns * 4 + 2
        else:
            y = index - 43
            x = four_columns * 4 + 3
        
        rest_colors = self.rest_of_colors[:]
        rest_colors.remove(self.state[x][y])
        color = rest_colors[color % len(rest_colors)]
        return x, y, color

    def step(self, action):
        x, y, color = self.tran_action(action)
        return self.change_color(x, y, color)
        
