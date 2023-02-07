def cross_product(point1, point2):
    return point1[0] * point2[1] - point1[1] * point2[0]


def point_in_triangle(point, triangle):
    (x1, y1), (x2, y2), (x3, y3) = triangle
    if cross_product((x3-x1, y3-y1), (x2-x1, y2-y1)) >= 0:
        x2, y2, x3, y3 = x3, y3, x2, y2
    if cross_product( (x2-x1, y2-y1), (point[0]-x1, point[1]-y1) ) < 0:
        return False
    if cross_product( (x1-x3, y1-y3), (point[0]-x3, point[1]-y3) ) < 0:
        return False
    if cross_product( (x3-x2, y3-y2), (point[0]-x2, point[1]-y2) ) < 0:
        return False
    return True

def test_pit():
    point = (192, 793)
    triangle = [(144, 787), (144, 869), (214, 829)]
    print(point_in_triangle(point, triangle))

if __name__ == "__main__":
    test_pit()