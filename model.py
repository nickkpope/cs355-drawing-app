class Shape():
    def __init__(self, color):
        self.color = color


class Line(Shape):
    def __init__(self, color, p1, p2=None):
        Shape.__init__(self, color)
        self.type = 'line'
        self.p1 = p1
        self.p2 = p2


class Rectangle(Shape):
    def __init__(self, color, top_left, w=None, h=None):
        Shape.__init__(self, color)
        self.type = 'rectangle'
        self.top_left = top_left
        self.w = w
        self.h = h

    def __repr__(self):
        return 'rect(tl=%s, w=%s, h=%s)' % (self.top_left, self.w, self.h)


class Square(Shape):
    def __init__(self, color, top_left, size=None):
        Shape.__init__(self, color)
        self.type = 'square'
        self.top_left = top_left
        self.size = size


class Ellipse(Shape):
    def __init__(self, color, center, h=None, w=None):
        Shape.__init__(self, color)
        self.type = 'ellipse'
        self.center = center
        self.h = h
        self.w = w

    def __repr__(self):
        return 'elli(center=%s, w=%s, h=%s)' % (self.center, self.w, self.h)


class Circle(Shape):
    def __init__(self, color, center, radius=None):
        Shape.__init__(self, color)
        self.type = 'circle'
        self.center = center
        self.radius = radius


class Triangle(Shape):
    def __init__(self, color, p1, p2=None, p3=None):
        Shape.__init__(self, color)
        self.type = 'triangle'
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3


class Model():
    def __init__(self, view, controller):
        self.shapes = []
        self.view = view
        self.controller = controller

    def save_shape(self, shape):
        self.shapes.append(shape)


class Vector():
    def __init__(self):
        pass

    def vec(self):
        return tuple()

    def dot(self, other):
        if isinstance(other, self.__class__):
            return sum((self * other).vec())
        else:
            print 'Cannot do dot product on type %s' % other.__class__
            return None

    def __eq__(self, other):
        return [a == b for a, b in zip(self.vec(), other.vec())].count(False) == 0

    def __lt__(self, other):
        return [a < b for a, b in zip(self.vec(), other.vec())].count(False) == 0

    def __gt__(self, other):
        return [a > b for a, b in zip(self.vec(), other.vec())].count(False) == 0

    def __sub__(self, other):
        return self.__class__(*[a - b for a, b in zip(self.vec(), other.vec())])

    def __add__(self, other):
        return self.__class__(*[a + b for a, b in zip(self.vec(), other.vec())])

    def __mul__(self, other):
        return self.__class__(*[a * b for a, b in zip(self.vec(), other.vec())])

    def __div__(self, other):
        return self.__class__(*[a / b for a, b in zip(self.vec(), other.vec())])

    def __repr__(self):
        return self.__class__.__name__ + '(' + ', '.join([str(i) for i in self.vec()]) + ')'


class Point(Vector):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def xy(self):
        return (self.x, self.y)

    def vec(self):
        return self.xy()


def test_Point():
    assert Point(1, 2) == Point(1, 2)
    assert Point(1, 2) < Point(3, 4)
    assert Point(3, 4) > Point(1, 2)
    assert (Point(1, 2) - Point(1, 2)) == Point(0, 0)
    assert (Point(1, 2) + Point(1, 2)) == Point(2, 4)
    assert (Point(1, 2) * Point(1, 2)) == Point(1, 4)
    assert (Point(1, 2) / Point(1, 2)) == Point(1, 1)
    assert Point(1, 2).dot(Point(3, 4)) == 11
    assert not Point(1, 2).dot(Shape(Color(0, 0, 0)))


class Color(Vector):
    def __init__(self, r, g, b, a=1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def rgb(self):
        return (self.r, self.g, self.b)

    def rgba(self):
        return (self.r, self.g, self.b, self.a)

    def vec(self):
        return self.rgba()
