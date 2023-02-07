def get_triangles():
    triangles = []
    for i in range(20):
        column = []
        if i % 4 == 1 or i % 4 == 2:
            for j in range(14):
                point1 = (72 + 72 * 2 * ((i - 1) // 4), 82 * j)
                point2 = (72 + 72 * 2 * ((i - 1) // 4), 82 * j + 82)
                point3 = (((i+2) // 4) * 144, 82 * j + 41)
                points = [point1, point2, point3]
                column.append(points)
        else:
            for j in range(15):
                if j != 0 and j != 14:
                    point1 = (144 * ((i+1) // 4), 82 * (j-1) + 41)
                    point2 = (144 * ((i+1) // 4), 82 * j + 41)
                    point3 = (72 + 144 * (i // 4), 82 * j)
                elif j == 0:
                    point1 = (144 * ((i+1) // 4), 0)
                    point2 = (144 * ((i+1) // 4), 41)
                    point3 = (72 + 144 * (i // 4), 0)
                else:
                    point1 = (144 * ((i+1) // 4), 14 * 82 - 41)
                    point2 = (144 * ((i+1) // 4), 14 * 82)
                    point3 = (72 + 144 * (i // 4), 14 * 82)
                points = [point1, point2, point3]
                column.append(points)
        triangles.append(column)
    for i, column in enumerate(triangles):
        for j, triangle in enumerate(column):
            for k, point in enumerate(triangle):
                triangles[i][j][k] = point[0]//2, point[1] //2
    return triangles

def whichTriangle(x, y, triangles):
    from point_triangle import point_in_triangle
    columns_index = (x // 36) * 2, (x // 36) * 2 + 1
    for index in columns_index:
        for j in range(len(triangles[index])):
            if point_in_triangle((x,y), triangles[index][j]):
                return index, j

def get_rectangles():
    rectangles = []
    for i in range(116):
        row = []
        x = i * 5
        for j in range(72):
            y = j * 5
            row.append((x, y))
        rectangles.append(row)
    return rectangles

def which_rectangle(x, y):
    return y // 5, x // 5

def tran_state(state, color_nums):
        trans_state = []
        for color_index in range(5):
            if color_index >= color_nums:
                trans_state.append([[-1 for _ in range(15)] for _ in range(20)])
                continue
            types = []
            for column_index in range(20):
                column = [0 for _ in range(15)]
                if column_index % 4 == 1 or column_index % 4 == 2: 
                    column[14] = -1
                types.append(column)
            trans_state.append(types)
        for i in range(20):
            for j in range(len(state[i])):
                color = state[i][j]
                trans_state[color][i][j] = 1
        return trans_state

def get_center_pos(x, y):
    # x 列数， y行数
    if x % 4 == 1 or x % 4 == 2:
        pos_x, pos_y = 36 + 72 * (x // 2),  41 + (1160 * y) // 14
    else:
        if y == 0:
            if x % 4 == 0:
                pos_x, pos_y = 18 + 144 * (x // 4), 21
            else:
                pos_x, pos_y = 144 - 18 + 144 * (x//4), 21
        elif y == 14:
            if x % 4 == 0:
                pos_x, pos_y = 18 + 144 * (x // 4), 1160 - 21
            else:
                pos_x, pos_y = 144 - 18 + 144 * (x//4), 1160 - 21
        else:
            pos_x, pos_y = 36 + 72 * (x//2),  (1160 * y) // 14
    return pos_x // 2, pos_y // 2