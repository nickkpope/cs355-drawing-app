from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
from OpenGL.GLU import *
from OpenGL.GL import *
from model import Point, Line, Rectangle, Square, Ellipse, Circle


class DrawWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawWidget, self).__init__(parent=parent)
        self.setFixedSize(512, 512)
        self.canvas = GLWidget(self)
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.canvas)
        self.setLayout(self.vlayout)
        self.draw_map = {}
        self.shape_types_map = {}
        shape_descs = [
            ('line', self.draw_line, Line),
            ('rectangle', self.draw_rectangle, Rectangle),
            ('square', self.draw_square, Square),
            ('ellipse', self.draw_ellipse, Ellipse),
            ('circle', self.draw_circle, Circle)
        ]
        for tn, d, t in shape_descs:
            self.draw_map[tn] = d
            self.shape_types_map[tn] = t
        self.controller = None
        self.model = None
        self.draw_shape = None

    def set_controller(self, controller):
        self.controller = controller

    def set_model(self, model):
        self.model = model

    def mousePressEvent(self, event):
        print 'mousePressEvent', event.pos()
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
                if self.draw_shape.p3:
                    save_shape = True
            else:
                save_shape = True
            if save_shape:
                self.clear()
                self.model.save_shape(self.draw_shape)
                print 'saving', self.draw_shape, len(self.model.shapes)
                self.draw_shape = None
            self.draw()

    def draw_line(self, shape, pos=None):
        if pos:
            shape.p2 = pos
        glBegin(GL_LINES)
        glColor3f(*shape.color.rgb())
        glVertex2i(*shape.p1.xy())
        glVertex2i(*shape.p2.xy())
        glEnd()

    def draw_rectangle(self, shape, pos=None, square=True):
        if pos:
            w = pos.x - shape.top_left.x
            h = pos.y - shape.top_left.y
            if square:
                if abs(w) > abs(h):

                    # preserve direction but change magnitude
                    if h < 0:
                        h = abs(w) * -1
                    else:
                        h = abs(w)
                    shape.size = w
                else:
                    if w < 0:
                        w = abs(h) * -1
                    else:
                        w = abs(h)
                    shape.size = h
            else:

                # rectangles are easier
                shape.w = w
                shape.h = h
        else:

            # retrieve stored information from shape for finalizing data
            if square:
                w = shape.size
                h = shape.size
            else:
                w = shape.w
                h = shape.h

        glBegin(GL_QUADS)
        glColor3f(*shape.color.rgb())
        glVertex2i(*shape.top_left.xy())
        glVertex2i(shape.top_left.x + w, shape.top_left.y)
        glVertex2i(shape.top_left.x + w, shape.top_left.y + h)
        glVertex2i(shape.top_left.x, shape.top_left.y + h)
        glEnd()

        # prep rectangle for storage
        if not pos:
            if square:
                tlx = shape.top_left.x + shape.size
                tly = shape.top_left.y + shape.size
            else:
                tlx = shape.top_left.x + shape.w
                tly = shape.top_left.y + shape.y
            shape.top_left = Point(tlx, tly)
            if square:
                shape.size = w
            else:
                shape.w = abs(shape.w)
                shape.h = abs(shape.h)

    def draw_square(self, shape, pos=None):
        self.draw_rectangle(shape, pos=pos, square=True)

    def draw_ellipse(self, shape, pos=None, circle=False):
        if pos:
            rx = (shape.center.x - pos.x)/2
            ry = (shape.center.y - pos.y)/2
            if circle:
                if abs(rx) < abs(ry):
                    if rx < 0:
                        ry = abs(rx) * -1
                    else:
                        ry = abs(rx)
                else:
                    if ry < 0:
                        rx = abs(ry) * -1
                    else:
                        rx = abs(ry)
                shape.radius = abs(rx)
            else:
                shape.w = rx
                shape.h = ry

            cx = (shape.center.x + pos.x)/2
            cy = (shape.center.y + pos.y)/2
        else:
            if circle:
                posx = posy = shape.center.x - 2*shape.radius
            else:
                posx = shape.center.x - 2*shape.w
                posy = shape.center.y - 2*shape.h
            cx = (shape.center.x + posx)/2
            cy = (shape.center.y + posy)/2
            if circle:
                rx = ry = shape.radius
            else:
                rx = shape.w
                ry = shape.h

        ellipseMidpoint(cx, cy, rx, abs(ry))

    def draw_circle(self, shape, pos=None):
        self.draw_ellipse(shape, pos=pos, circle=True)


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


def ellipseMidpoint(xc, yc, rx, ry):
    glBegin(GL_POINTS)
    rxSq = rx * rx
    rySq = ry * ry
    x = 0
    y = ry
    p = 0
    px = 0
    py = 2 * rxSq * y
    drawEllipse(xc, yc, x, y)

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

        drawEllipse(xc, yc, x, y)

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

        drawEllipse(xc, yc, x, y)
    # draws center point
    # glVertex2i(xc, yc)
    glEnd()


def drawEllipse(xc, yc, x, y):
    glVertex2i(xc+x, yc+y)
    glVertex2i(xc-x, yc+y)
    glVertex2i(xc+x, yc-y)
    glVertex2i(xc-x, yc-y)


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
