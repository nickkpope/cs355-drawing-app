from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
from OpenGL.GLU import *
from OpenGL.GL import *
from model import Point, Line, Rectangle, Square, Ellipse, Circle, Triangle


class DrawWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawWidget, self).__init__(parent=parent)
        self.setFixedSize(512, 512)
        self.canvas = GLWidget(self)
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.canvas)
        self.setLayout(self.vlayout)
        self.click_pos = (0, 0)
        self.controller = None
        self.model = None
        self.draw_shape = None
        self.tri_shape = None

        self.draw_map = {}
        self.shape_types_map = {}
        shape_descs = [
            ('line', self.draw_line, Line),
            ('rectangle', self.draw_rectangle, Rectangle),
            ('square', self.draw_square, Square),
            ('ellipse', self.draw_ellipse, Ellipse),
            ('circle', self.draw_circle, Circle),
            ('triangle', self.draw_triangle, Triangle)
        ]
        for tn, d, t in shape_descs:
            self.draw_map[tn] = d
            self.shape_types_map[tn] = t

    def set_controller(self, controller):
        self.controller = controller

    def set_model(self, model):
        self.model = model

    def mousePressEvent(self, event):
        print 'mousePressEvent', event.pos()
        self.click_pos = self.to_screen(event.pos().x(), event.pos().y())
        self.draw_shape = self.shape_types_map[self.controller.draw_mode](
            self.controller.draw_color,
            self.to_screen(event.pos().x(), event.pos().y()))

    def mouseMoveEvent(self, event):
        self.clear()
        self.draw_map[self.controller.draw_mode](self.draw_shape, pos=self.to_screen(event.pos().x(), event.pos().y()))
        self.draw()
        # print 'mouseMoveEvent', event

    def mouseReleaseEvent(self, event):
        print 'mouseReleaseEvent', event.pos()
        self.finish(self.to_screen(event.pos().x(), event.pos().y()))

    def draw(self):
        # call drawing function here
        for shape in self.model.shapes:
            self.draw_map[shape.type](shape)
        glFlush()
        self.canvas.updateGL()

    def clear(self):
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        # glEnable(GL_POINT_SMOOTH)

    def to_screen(self, x, y):
        return Point(x, self.size().height()-y)

    def finish(self, pos):
        if self.draw_shape:
            save_shape = False
            if self.draw_shape.type == 'triangle':
                print self.tri_shape
                if self.tri_shape:
                    if self.tri_shape.p2:
                        self.tri_shape.p3 = pos
                        save_shape = True
                        self.draw_shape = self.tri_shape
                        self.tri_shape = None
                    else:
                        self.tri_shape.p2 = pos
                else:
                    self.tri_shape = Triangle(self.draw_shape.color, self.draw_shape.p1)

            else:
                save_shape = True
            if save_shape:
                self.clear()
                self.model.save_shape(self.draw_shape)
                print 'saving', self.draw_shape, self.draw_shape.color, len(self.model.shapes)
                self.draw_shape = None
            self.draw()

    def draw_line(self, shape, pos=None):
        if pos:
            shape.p2 = pos
        glBegin(GL_LINES)
        glColor4f(*shape.color.rgba())
        glVertex2i(*shape.p1.xy())
        glVertex2i(*shape.p2.xy())
        glEnd()

    def draw_rectangle(self, shape, pos=None):
        if pos:
            w = abs(pos.x - self.click_pos.x)
            h = abs(pos.y - self.click_pos.y)

            if pos.x < self.click_pos.x:  # hovering left of initial click
                shape.top_left.x = pos.x
            else:
                shape.top_left.x = self.click_pos.x

            if pos.y > self.click_pos.y:  # hovering above initial click
                shape.top_left.y = pos.y
            else:
                shape.top_left.y = self.click_pos.y

            shape.w = w
            shape.h = h

        else:
            w = shape.w
            h = shape.h

        draw_quad(
            shape.color,
            shape.top_left.xy(),
            (shape.top_left.x + w, shape.top_left.y),
            (shape.top_left.x + w, shape.top_left.y - h),
            (shape.top_left.x, shape.top_left.y - h)
        )

    def draw_square(self, shape, pos=None):
        if pos:
            dx = abs(pos.x - self.click_pos.x)
            dy = abs(pos.y - self.click_pos.y)
            shape.size = min(dx, dy)
            if pos.x < self.click_pos.x:  # hovering left of initial click
                shape.top_left.x = self.click_pos.x - shape.size
            else:
                shape.top_left.x = self.click_pos.x

            if pos.y > self.click_pos.y:  # hovering above initial click
                shape.top_left.y = self.click_pos.y + shape.size
            else:
                shape.top_left.y = self.click_pos.y

        draw_quad(
            shape.color,
            shape.top_left.xy(),  # top left corner
            (shape.top_left.x + shape.size, shape.top_left.y),  # top right corner
            (shape.top_left.x + shape.size, shape.top_left.y - shape.size),  # bottom right corner
            (shape.top_left.x, shape.top_left.y - shape.size)  # bottom left corner
        )

    def draw_ellipse(self, shape, pos=None, circle=False):
        if pos:
            w = abs(pos.x - self.click_pos.x)
            h = abs(pos.y - self.click_pos.y)
            if pos.x < self.click_pos.x:  # hovering left of initial click
                tlx = pos.x
                trx = self.click_pos.x
            else:
                tlx = self.click_pos.x
                trx = pos.x

            if pos.y > self.click_pos.y:  # hovering above initial click
                tly = pos.y
                try_ = self.click_pos.y
            else:
                tly = self.click_pos.y
                try_ = pos.y

            shape.center.x = (tlx + trx)/2
            shape.center.y = (tly + try_)/2
            shape.w = w
            shape.h = h

        draw_ellipse(shape.color, shape.center.x, shape.center.y, shape.w/2, shape.h/2)

    def draw_circle(self, shape, pos=None):
        if pos:
            dw = abs(pos.x - self.click_pos.x)
            dh = abs(pos.y - self.click_pos.y)
            shape.radius = min(dw, dh)
            if pos.x < self.click_pos.x:  # hovering left of initial click
                tlx = self.click_pos.x - shape.radius
                trx = self.click_pos.x
            else:
                tlx = self.click_pos.x
                trx = self.click_pos.x + shape.radius

            if pos.y > self.click_pos.y:  # hovering above initial click
                tly = self.click_pos.y + shape.radius
                try_ = self.click_pos.y
            else:
                tly = self.click_pos.y
                try_ = self.click_pos.y - shape.radius

            shape.center.x = (tlx + trx)/2
            shape.center.y = (tly + try_)/2

        draw_ellipse(shape.color, shape.center.x, shape.center.y, shape.radius/2, shape.radius/2)

    def draw_triangle(self, shape, pos=None):
        draw_triangle(shape.color, shape.p1.xy(), shape.p2.xy(), shape.p3.xy())


class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.parent = parent
        self.setFocus(Qt.OtherFocusReason)
        self.setFixedSize(512, 512)

    def initializeGL(self):
        self.qglClearColor(QColor(0, 0, 0))
        self.qglColor(QColor(0, 0, 0))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        print self.size().width(), 0, self.size().height()
        glOrtho(0, self.size().width(), 0, self.size().height(), -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


def draw_triangle(color, p1, p2, p3):
    glBegin(GL_TRIANGLES)
    glColor4f(*color.rgba())
    glVertex2i(*p1)
    glVertex2i(*p2)
    glVertex2i(*p3)
    glEnd()


def draw_ellipse(color, xc, yc, rx, ry):
    glBegin(GL_POINTS)
    glColor4f(*color.rgba())
    rxSq = rx * rx
    rySq = ry * ry
    x = 0
    y = ry
    p = 0
    px = 0
    py = 2 * rxSq * y
    draw_ellipse_points(xc, yc, x, y)

    p = rySq - (rxSq * ry) + (0.25 * rxSq)
    while px < py:
        x += 1
        px = px + 2 * rySq
        if p < 0:
            p = p + rySq + px
        else:
            y -= 1
            py = py - 2 * rxSq
            p = p + rySq + px - py

        draw_ellipse_points(xc, yc, x, y)

    p = rySq*(x+0.5)*(x+0.5) + rxSq*(y-1)*(y-1) - rxSq*rySq
    while (y > 0):
        y -= 1
        py = py - 2 * rxSq
        if (p > 0):
            p = p + rxSq - py
        else:
            x += 1
            px = px + 2 * rySq
            p = p + rxSq - py + px

        draw_ellipse_points(xc, yc, x, y)
    # draws center point
    # glVertex2i(xc, yc)
    glEnd()


def draw_ellipse_points(xc, yc, x, y):
    glVertex2i(xc+x, yc+y)
    glVertex2i(xc-x, yc+y)
    glVertex2i(xc+x, yc-y)
    glVertex2i(xc-x, yc-y)


def draw_quad(color, tl, tr, br, bl):
    glBegin(GL_QUADS)
    glColor4f(*color.rgba())
    glVertex2i(*tl)
    glVertex2i(*tr)
    glVertex2i(*br)
    glVertex2i(*bl)
    glEnd()


def draw_lines():
        print 'drawing lines'
        glBegin(GL_LINES)
        for i in range(9):
            glColor3f(1, 0, 0)
            glVertex2i(200, 200)
            glVertex2i(200 + 10*i, 280)
            glColor3f(0, 1, 0)
            glVertex2i(200, 200)
            glColor3f(0, 1, 1)
            glVertex2i(200 - 10*i, 280)
            glVertex2i(200, 200)
            glVertex2i(280, 200 + 10*i)
            glVertex2i(200, 200)
            glVertex2i(280, 200 - 10*i)

        glEnd()
