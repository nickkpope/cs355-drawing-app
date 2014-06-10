import numpy as np
from math import *


class Shape():
    def __init__(self, color):
        self.color = color
        self.center = Point(0, 0)
        self.rotation = 0

    def bounding_box(self):
        return BoundingBox()

    def is_inside(self, q):
        return False

    def to_world(self, p, trans=True):
        t = Transform2d()
        if trans:
            t.translate(self.center)
        t.rotate(self.rotation)
        return t.transform(p)

    def to_object(self, q, trans=True):
        t = Transform2d()
        t.rotate(-self.rotation)
        if trans:
            t.translate(-self.center)
        return t.transform(q)


class Line(Shape):
    def __init__(self, color, p1, p2=None):
        Shape.__init__(self, color)
        self.type = 'line'
        self.p1 = p1
        self.p2 = p2

    def to_world(self, p):
        return p

    def to_object(self, q):
        return q

    def is_inside(self, q, tolerance=4):
        if not (self.p1 and self.p2):
            return False
        point_dist = (self.p2 - self.p1).length()
        d_hat = (self.p2 - self.p1)/point_dist
        t = (q - self.p1).dot(d_hat)
        q_prime = self.p1 + d_hat*t
        dist_from_line = (q - q_prime).length()
        return dist_from_line < tolerance and t > 0 and t < point_dist  # represents a buffer area of 8 around the line

    def handle_positions(self):
        return self.p1, self.p2

    def __repr__(self):
        return 'ln(p1=%s p2=%s)' % (self.p1, self.p2)


class Rectangle(Shape):
    def __init__(self, color, top_left, w=None, h=None):
        Shape.__init__(self, color)
        self.type = 'rectangle'
        self.w = w
        self.h = h

    def handle_positions(self):
        return self.bounding_box().corners()

    def bounding_box(self):
        return BoundingBox(self.center, self.w, self.h)

    def is_inside(self, q):
        return self.bounding_box().is_inside(self.to_object(q))

    def __repr__(self):
        return 'rect(center=%s, w=%s, h=%s)' % (self.center, self.w, self.h)


class Square(Shape):
    def __init__(self, color, top_left, size=None):
        Shape.__init__(self, color)
        self.type = 'square'
        self.size = size

    def handle_positions(self):
        return self.bounding_box().corners()

    def bounding_box(self):
        return BoundingBox(center=self.center, w=self.size, h=self.size)

    def is_inside(self, q):
        return self.bounding_box().is_inside(self.to_object(q))

    def __repr__(self):
        return 'sq(center=%s size=%s)' % (self.center, self.size)


class Ellipse(Shape):
    def __init__(self, color, center, w=None, h=None):
        Shape.__init__(self, color)
        self.type = 'ellipse'
        self.center = center
        self.h = h
        self.w = h

    def bounding_box(self):
        return BoundingBox(center=self.center, w=self.w, h=self.h)

    def handle_positions(self):
        return self.bounding_box().corners()

    def is_inside(self, q):
        tq = self.to_object(q)
        if self.bounding_box().is_inside(tq):
            print 'inside bbox'
            return ((tq.x)/(self.w))**2 + ((tq.y)/(self.h))**2 <= 1
        else:
            return False

    def __repr__(self):
        return 'elli(center=%s, w=%s, h=%s)' % (self.center, self.w, self.h)


class Circle(Shape):
    def __init__(self, color, center, radius=None):
        Shape.__init__(self, color)
        self.type = 'circle'
        self.center = center
        self.radius = radius

    def handle_positions(self):
        return self.bounding_box().corners()

    def bounding_box(self):
        return BoundingBox(center=self.center, w=self.radius, h=self.radius)

    def is_inside(self, q):
        return (q - self.center).length() < self.radius

    def __repr__(self):
        return 'cir(center=%s radius=%s)' % (self.center, self.radius)


class Triangle(Shape):
    def __init__(self, color, p1, p2=None, p3=None):
        Shape.__init__(self, color)
        self.type = 'triangle'
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def points(self):
        return (self.p1, self.p2, self.p3)

    def handle_positions(self):
        return self.points()

    def bounding_box(self):
        minx = min(i.x for i in self.points())
        maxx = max(i.x for i in self.points())
        miny = min(i.y for i in self.points())
        maxy = max(i.y for i in self.points())
        return BoundingBox(Point((minx+maxx)/2, (miny+maxy)/2), (maxx-minx)/2, (maxy-miny)/2)

    def is_inside(self, q):
        q = self.to_object(q)
        if self.bounding_box().is_inside(q):
            print (q-self.p1).dot((self.p2-self.p1).perp())
            print (q-self.p2).dot((self.p3-self.p2).perp())
            print (q-self.p3).dot((self.p1-self.p3).perp())
            print
            t1 = (q-self.p1).dot((self.p2-self.p1).perp())
            t2 = (q-self.p2).dot((self.p3-self.p2).perp())
            t3 = (q-self.p3).dot((self.p1-self.p3).perp())
            all_pos = t1 > 0
            all_pos = all_pos and t2 > 0
            all_pos = all_pos and t3 > 0
            all_neg = t1 < 0
            all_neg = all_neg and t2 < 0
            all_neg = all_neg and t3 < 0
            return all_pos or all_neg
        else:
            return False

    def __repr__(self):
        return 'tri(p1=%s p2=%s p3=%s)' % (self.p1, self.p2, self.p3)


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
            return np.array(self.vec()).dot(np.array(other.vec()))
        else:
            print 'Cannot do dot product on type %s' % other.__class__
            return None

    def length(self):
        return np.linalg.norm(np.array(self.vec()))

    def angle_between(a, b):
        return np.arccos(a.dot(b)/(a.length() * b.length()))

    def __neg__(self):
        return self.__class__(*[-a for a in self.vec()])

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
        if isinstance(other, self.__class__):
            return self.__class__(*[a * b for a, b in zip(self.vec(), other.vec())])
        else:
            return self.__class__(*[a * other for a in self.vec()])

    def __div__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(*[a / b for a, b in zip(self.vec(), other.vec())])
        else:
            return self.__class__(*[a / other for a in self.vec()])

    def __repr__(self):
        return self.__class__.__name__ + '(' + ', '.join([str(i) for i in self.vec()]) + ')'


class Point(Vector):
    def __init__(self, x, y, w=1):
        self.x = float(x)
        self.y = float(y)
        self.w = float(w)

    def xy(self):
        return (self.x, self.y)

    def vec(self):
        return self.xy()

    def perp(self):
        return Point(self.y*-1, self.x)


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
    assert Point(0, 1).length() == 1
    assert Point(0, 1).angle_between(Point(1, 0)) == np.pi/2
    assert Point(0, 1).angle_between(Point(1/np.sqrt(2), 1/np.sqrt(2))) == np.pi/4
    assert Point(0, 1).angle_between(Point(0, -1)) == np.pi
    # assert Point(1/np.sqrt(2), 1/np.sqrt(2)).length() == np.sqrt


class BoundingBox(Shape):
    def __init__(self, center=None, w=None, h=None):
        self.center = center or Point(0, 0)
        self.w = w or 0
        self.h = h or 0

    def tl(self):
        return Point(-self.w, +self.h)

    def tr(self):
        return Point(+self.w, +self.h)

    def br(self):
        return Point(+self.w, -self.h)

    def bl(self):
        return Point(-self.w, -self.h)

    def corners(self):
        return (self.tl(), self.tr(), self.br(), self.bl())

    def is_inside(self, q):
        within_x = -self.w < q.x and q.x < self.w
        within_y = self.h > q.y and q.y > -self.h
        return within_x and within_y

    def __repr__(self):
        return 'BB(%s %s %s %s)' % self.corners()


class Transform2d():
    def __init__(self):
        self.load_identity()

    def load_identity(self):
        self.M = np.identity(3, dtype=float)

    def rotate(self, theta):
        '''theta must be in radians'''
        self.M = self.M.dot(np.array([[np.cos(theta), -np.sin(theta), 0],
                                      [np.sin(theta),  np.cos(theta), 0],
                                      [0,                0,           1]],
                                     dtype=float))

    def translate(self, p):
        self.M = self.M.dot(np.array([[1, 0, p.x],
                                      [0, 1, p.y],
                                      [0, 0, p.w]],
                                     dtype=float))

    def scale(self, sx, sy):
        self.M = self.M.dot(np.array([[sx, 0, 0],
                                      [0, sy, 0],
                                      [0,  0, 1]],
                                     dtype=float))

    def transform(self, p):
        ret = self.M.dot(np.array([[p.x], [p.y], [p.w]], dtype=float)).reshape(-1)
        return Point(ret[0], ret[1], ret[2])


def test_Transform2d():
    t = Transform2d()
    t.translate(Point(1.0, 1.0))
    assert t.transform(Point(0, 0)) == Point(1.0, 1.0)
    t.load_identity()
    t.translate(Point(1.0, 1.0))
    assert t.transform(Point(1.0, 1.0)) == Point(2.0, 2.0)
    t.load_identity()
    t.translate(Point(-1.0, -1.0))
    assert t.transform(Point(1.0, 1.0)) == Point(0.0, 0.0)

    t.load_identity()
    t.rotate(np.pi/2)
    assert t.transform(Point(1.0, 0.0)) == Point(0.0, 1.0)


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

    def __repr__(self):
        return 'Color(%s %s %s %s)' % self.rgba()


class Camera():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.fovy = 45.0
        self.reset()
        self.set_camera()

    def load_identity(self):
        self.M = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]],
                          dtype=float)

    def reset(self):
        self.persp = True
        self.x = 0
        self.y = 0
        self.z = 10.0
        self.roty = 0.0
        self.load_identity()

    def move_forward(self, amount):
        self.z -= sin(radians(self.roty)+pi/2)*amount
        self.x -= cos(radians(self.roty)+pi/2)*amount

    def move_backward(self, amount):
        self.z += sin(radians(self.roty)+pi/2)*amount
        self.x += cos(radians(self.roty)+pi/2)*amount

    def move_up(self, amount):
        self.y += amount

    def move_down(self, amount):
        self.y -= amount

    def move_left(self, amount):
        self.z -= sin(radians(self.roty))*amount
        self.x -= cos(radians(self.roty))*amount

    def move_right(self, amount):
        self.z += sin(radians(self.roty))*amount
        self.x += cos(radians(self.roty))*amount

    def turn_left(self, amount):
        self.turn_y(-abs(amount))

    def turn_right(self, amount):
        self.turn_y(abs(amount))

    def turn_y(self, amount):
        '''IN DEGREES'''
        self.roty += amount

    def view_ortho(self):
        self.persp = False

    def view_persp(self):
        self.persp = True

    def set_camera(self):
        self.load_identity()
        theta = radians(self.roty)

        # apply perspective clip matrix
        aspect = float(self.w)/float(self.h)
        zy = 1/tan(radians(self.fovy/2))
        zx = zy/aspect
        n = .1
        f = 50
        a = (f + n)/(f - n)
        b = (2*n*f)/(f - n)

        self.M = self.M.dot(np.array([[zx, 0,  0, 0],
                                      [0,  zy, 0, 0],
                                      [0,  0,  a, b],
                                      [0,  0,  -1, 0]],
                                     dtype=float))

        # apply rotation
        self.M = self.M.dot(np.array([[+cos(theta), 0, sin(theta), 0],
                                      [0,           1, 0,          0],
                                      [-sin(theta), 0, cos(theta), 0],
                                      [0,           0, 0,          1]],
                                     dtype=float))

        # apply translation
        self.M = self.M.dot(np.array([[1, 0, 0, -self.x],
                                      [0, 1, 0, -self.y],
                                      [0, 0, 1, -self.z],
                                      [0, 0, 0,       1]],
                                     dtype=float))

    def to_camera(self, x, y, z, w=1.0):
        # reshape back to a regular list again, and convert to floats
        return [float(i) for i in self.M.dot(np.array([[x], [y], [z], [w]], dtype=float)).reshape(-1)]


def house_lines(offset=None):
    lines = []
    if offset:
        offset = offset[0]

    def add_line_point(x, y, z):
        if len(lines) == 0:
            lines.append([(x*1.5+offset, y, z)])
        else:
            if len(lines[-1]) == 2:
                lines.append([(x*1.5+offset, y, z)])
            else:
                lines[-1].append((x*1.5+offset, y, z))

   # Bottom Face
    # rear bottom line
    add_line_point(-1, -1, -1)
    add_line_point(+1, -1, -1)
    # front bottom line
    add_line_point(-1, -1, +1)
    add_line_point(+1, -1, +1)
    # left bottom line
    add_line_point(-1, -1, -1)
    add_line_point(-1, -1, +1)
    # right bottom line
    add_line_point(+1, -1, -1)
    add_line_point(+1, -1, +1)

    # Top Face
    # rear top line
    add_line_point(-1, +1, -1)
    add_line_point(+1, +1, -1)
    # front top line
    add_line_point(-1, +1, +1)
    add_line_point(+1, +1, +1)
    # left top line
    add_line_point(-1, +1, -1)
    add_line_point(-1, +1, +1)
    # right top line
    add_line_point(+1, +1, -1)
    add_line_point(+1, +1, +1)

    # Left Face
    # left back line
    add_line_point(-1, -1, -1)
    add_line_point(-1, +1, -1)
    # left front line
    add_line_point(-1, -1, +1)
    add_line_point(-1, +1, +1)
    # left top line
    add_line_point(-1, +1, -1)
    add_line_point(-1, +1, +1)

    # Right Face
    # right back line
    add_line_point(+1, -1, -1)
    add_line_point(+1, +1, -1)
    # right front line
    add_line_point(+1, -1, +1)
    add_line_point(+1, +1, +1)
    # right top line
    add_line_point(+1, +1, -1)
    add_line_point(+1, +1, +1)

    # Front Door
    # left side
    add_line_point(-.25, -1, +1)
    add_line_point(-.25, .5, +1)
    # right side
    add_line_point(+.25, -1.0, +1)
    add_line_point(+.25, +0.5, +1)
    # top side
    add_line_point(-.25, +0.5, +1)
    add_line_point(+.25, +0.5, +1)

    # Roof
    add_line_point(0, 1.5, +1)
    add_line_point(0, 1.5, -1)

    add_line_point(-1, 1.0, +1)
    add_line_point(+0, 1.5, +1)

    add_line_point(+0, 1.5, +1)
    add_line_point(+1, 1.0, +1)

    add_line_point(-1, 1.0, -1)
    add_line_point(+0, 1.5, -1)
    add_line_point(+0, 1.5, -1)
    add_line_point(+1, 1.0, -1)

    return lines
