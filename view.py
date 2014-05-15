from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
from OpenGL.GLU import *
from OpenGL.GL import *
from model import Color, Point, Shape, Line, Rectangle, Square, Ellipse, Circle, Triangle
import numpy as np
import copy


class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.parent = parent
        self.setFocus(Qt.OtherFocusReason)

    def initializeGL(self):
        self.qglClearColor(QColor(0, 0, 0))
        self.qglColor(QColor(0, 0, 0))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.size().width(), 0, self.size().height(), -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def paintGL(self):
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        self.parent.draw()
        glFlush()

class DrawWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawWidget, self).__init__(parent=parent)
        self.setFixedSize(512, 512)
        self.canvas = GLWidget(self)
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.canvas)
        self.setLayout(self.vlayout)
        self.controller = None
        self.model = None
        self.setCursor(Qt.CrossCursor)
        self.clear_state()

        self.draw_map = {}
        self.shape_types_map = {}
        shape_descs = [
            ('line', self.draw_line, Line),
            ('rectangle', self.draw_rectangle, Rectangle),
            ('square', self.draw_square, Square),
            ('ellipse', self.draw_ellipse, Ellipse),
            ('circle', self.draw_circle, Circle),
            ('triangle', self.draw_triangle, Triangle),
            ('select', self.draw_nothing, Shape)
        ]
        for tn, d, t in shape_descs:
            self.draw_map[tn] = d
            self.shape_types_map[tn] = t

    def clear_state(self):
        self.click_pos = Point(0, 0)
        self.draw_shape = None
        self.tri_shape = None
        self.rotating = False
        self.rot_handle = None
        self.line_p1_handle = None
        self.line_p2_handle = None
        self.selected_line_endpoint = None
        self.d_vec = Point(0, 0)
        self.cur_point = None

    def clear(self):
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        # glEnable(GL_POINT_SMOOTH)

    def to_screen(self, x, y):
        return Point(x-12, self.size().height()-y-12)  # not sure why widgets are missaligned like this but whatever.

    def set_controller(self, controller):
        self.controller = controller

    def set_model(self, model):
        self.model = model

    def mousePressEvent(self, event):
        # print 'mousePressEvent', event.pos()
        self.click_pos = self.to_screen(event.pos().x(), event.pos().y())
        if self.controller.draw_mode == 'select':
            handle_clicked = False
            if self.rot_handle:
                if self.rot_handle.is_inside(self.click_pos):
                    self.rotating = True
                    handle_clicked = True
            elif self.line_p1_handle and self.line_p2_handle:
                if self.line_p1_handle.is_inside(self.click_pos):
                    self.selected_line_endpoint = self.controller.selected_shape.p1
                    handle_clicked = True
                if self.line_p2_handle.is_inside(self.click_pos):
                    self.selected_line_endpoint = self.controller.selected_shape.p2
                    handle_clicked = True

            if not handle_clicked:
                found_shape = False
                for s in reversed(self.model.shapes):
                    if s.is_inside(self.click_pos):
                        self.controller.selected_shape = s
                        print 'found selected shape', self.controller.selected_shape.color
                        found_shape = True
                        break
            else:
                found_shape = False
            if found_shape:
                self.controller.selected_draw_color = self.controller.selected_shape.color
                self.d_vec = self.click_pos - self.controller.selected_shape.center

            if not found_shape and not handle_clicked:
                self.controller.selected_shape = None
        else:
            self.draw_shape = self.shape_types_map[self.controller.draw_mode](
                copy.deepcopy(self.controller.draw_color),
                self.to_screen(event.pos().x(), event.pos().y()))
            print 'drawing', self.draw_shape

    def mouseMoveEvent(self, event):
        self.clear()
        self.cur_point = self.to_screen(event.pos().x(), event.pos().y())
        if self.controller.selected_shape and self.controller.draw_mode == 'select':
            if self.rotating:
                theta = (self.cur_point - self.controller.selected_shape.center).angle_between(Point(1, 0))
                if self.cur_point.y < self.controller.selected_shape.center.y:
                    theta *= -1
                self.controller.selected_shape.rotation = theta
            elif self.selected_line_endpoint:
                self.selected_line_endpoint.x = self.cur_point.x
                self.selected_line_endpoint.y = self.cur_point.y
            else:
                self.controller.selected_shape.center = self.cur_point - self.d_vec

        self.canvas.updateGL()
        # print 'mouseMoveEvent', event

    def mouseReleaseEvent(self, event):
        # self.clear()
        self.cur_point = None
        # print 'mouseReleaseEvent', event.pos()
        self.rotating = False
        self.finish(self.to_screen(event.pos().x(), event.pos().y()))

    def draw(self):
        if self.cur_point:
            self.draw_map[self.controller.draw_mode](self.draw_shape, pos=self.cur_point)
        for shape in self.model.shapes:
            self.draw_map[shape.type](shape)

        if self.controller.selected_shape:
            outline = copy.deepcopy(self.controller.selected_shape)
            outline.color = Color(1, 0, 0)
            self.draw_map[outline.type](outline, fill=False)
            for c in outline.handle_positions():
                p = outline.to_world(c)
                draw_ellipse(Color(1, 0, 0), p.x, p.y, 4, 4)

            if self.controller.selected_shape.type == 'line':
                self.line_p1_handle = Circle(Color(1, 0, 0), outline.p1, 4)
                self.line_p2_handle = Circle(Color(1, 0, 0), outline.p2, 4)
            else:
                obb = outline.bounding_box()
                rot_handle_point = outline.to_world((obb.tr() + obb.br())/2 + Point(15, 0))
                self.rot_handle = Circle(Color(1, 0, 0), rot_handle_point, 4)
                self.draw_circle(self.rot_handle)

    def finish(self, pos):
        if self.draw_shape:
            save_shape = False
            if self.draw_shape.type == 'triangle':
                print self.tri_shape
                if self.tri_shape:
                    if self.tri_shape.p2:
                        self.tri_shape.p3 = pos
                        self.tri_shape.center = self.tri_shape.bounding_box().center
                        self.tri_shape.p1 = self.tri_shape.to_object(self.tri_shape.p1)
                        self.tri_shape.p2 = self.tri_shape.to_object(self.tri_shape.p2)
                        self.tri_shape.p3 = self.tri_shape.to_object(self.tri_shape.p3)
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
        self.canvas.updateGL()

    def draw_nothing(self, shape, pos, fill=False):
        pass

    def draw_line(self, shape, pos=None, fill=None):
        if pos:
            shape.p2 = pos

        if shape.p1 and shape.p2:
            draw_line(shape.color, shape.p1.vec(), shape.p2.vec())

    def draw_rectangle(self, shape, pos=None, fill=True):
        if pos:
            w = abs(pos.x - self.click_pos.x)/2
            h = abs(pos.y - self.click_pos.y)/2
            top_left = Point(0, 0)

            if pos.x < self.click_pos.x:  # hovering left of initial click
                top_left.x = pos.x
            else:
                top_left.x = self.click_pos.x

            if pos.y > self.click_pos.y:  # hovering above initial click
                top_left.y = pos.y
            else:
                top_left.y = self.click_pos.y

            shape.w = w
            shape.h = h
            shape.center = Point(top_left.x + shape.w, top_left.y - shape.h)
        else:
            w = shape.w
            h = shape.h

        if not (shape.center and shape.w and shape.h):
            return

        draw_quad(
            shape.color,
            shape.to_world(Point(-shape.w, +shape.h)).xy(),
            shape.to_world(Point(+shape.w, +shape.h)).xy(),
            shape.to_world(Point(+shape.w, -shape.h)).xy(),
            shape.to_world(Point(-shape.w, -shape.h)).xy(),
            fill=fill
        )

    def draw_square(self, shape, pos=None, fill=True):
        if pos:
            dx = abs(pos.x - self.click_pos.x)/2
            dy = abs(pos.y - self.click_pos.y)/2
            shape.size = min(dx, dy)
            top_left = Point(0, 0)
            if pos.x < self.click_pos.x:  # hovering left of initial click
                top_left.x = self.click_pos.x - shape.size*2
            else:
                top_left.x = self.click_pos.x

            if pos.y > self.click_pos.y:  # hovering above initial click
                top_left.y = self.click_pos.y + shape.size*2
            else:
                top_left.y = self.click_pos.y

            shape.center = Point(top_left.x + shape.size, top_left.y - shape.size)

        if not (shape.center and shape.size):
            return

        draw_quad(
            shape.color,
            shape.to_world(Point(-shape.size, +shape.size)).xy(),  # top left corner
            shape.to_world(Point(+shape.size, +shape.size)).xy(),  # top right corner
            shape.to_world(Point(+shape.size, -shape.size)).xy(),  # bottom right corner
            shape.to_world(Point(-shape.size, -shape.size)).xy(),  # bottom left corner
            fill=fill
        )

    def draw_ellipse(self, shape, pos=None, fill=True):
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
            shape.w = w/2
            shape.h = h/2

        if not (shape.center and shape.w and shape.h):
            return

        rot = {'angle': shape.rotation, 'x': shape.center.x, 'y': shape.center.y}
        draw_ellipse(shape.color, shape.center.x, shape.center.y, shape.w, shape.h, fill=fill, rot=rot)

    def draw_circle(self, shape, pos=None, fill=True):
        if pos:
            dw = abs(pos.x - self.click_pos.x)/2
            dh = abs(pos.y - self.click_pos.y)/2
            shape.radius = min(dw, dh)
            if pos.x < self.click_pos.x:  # hovering left of initial click
                tlx = self.click_pos.x - shape.radius*2
                trx = self.click_pos.x
            else:
                tlx = self.click_pos.x
                trx = self.click_pos.x + shape.radius*2

            if pos.y > self.click_pos.y:  # hovering above initial click
                tly = self.click_pos.y + shape.radius*2
                try_ = self.click_pos.y
            else:
                tly = self.click_pos.y
                try_ = self.click_pos.y - shape.radius*2

            shape.center.x = (tlx + trx)/2
            shape.center.y = (tly + try_)/2
        if not (shape.center and shape.radius):
            return

        draw_ellipse(shape.color, shape.center.x, shape.center.y, shape.radius, shape.radius, fill=fill)

    def draw_triangle(self, shape, pos=None, fill=True):
        # convert back to world

        draw_triangle(shape.color,
                      shape.to_world(shape.p1).xy(),
                      shape.to_world(shape.p2).xy(),
                      shape.to_world(shape.p3).xy(),
                      fill=fill)


def draw_line(color, p1, p2):
    glBegin(GL_LINES)
    glColor4f(*color.rgba())
    glVertex2i(*p1)
    glVertex2i(*p2)
    glEnd()


def draw_triangle(color, p1, p2, p3, fill=True):
    if not fill:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(2)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1)
    glBegin(GL_TRIANGLES)
    glColor4f(*color.rgba())
    glVertex2i(*[int(i) for i in p1])
    glVertex2i(*[int(i) for i in p2])
    glVertex2i(*[int(i) for i in p3])
    glEnd()


def draw_ellipse(color, xc, yc, rx, ry, fill=False, rot=None):
    if rot:
        glPushMatrix()
        glTranslate(rot['x'], rot['y'], 0)
        glRotatef(rot['angle']*180/np.pi, 0, 0, 1)
        glTranslate(-rot['x'], -rot['y'], 0)
    glBegin(GL_POINTS)
    glColor4f(*color.rgba())
    rxSq = rx * rx
    rySq = ry * ry
    x = 0
    y = ry
    p = 0
    px = 0
    py = 2 * rxSq * y
    draw_ellipse_points(xc, yc, x, y, fill=fill)

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

        draw_ellipse_points(xc, yc, x, y, fill=fill)

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

        draw_ellipse_points(xc, yc, x, y, fill=fill)
    # draws center point
    # glVertex2i(xc, yc)
    glEnd()
    if rot:
        glPopMatrix()


def draw_ellipse_points(xc, yc, x, y, fill=False):
    xc, yc, x, y = int(xc), int(yc), int(x), int(y)
    glVertex2i(xc+x, yc+y)
    glVertex2i(xc-x, yc+y)
    glVertex2i(xc+x, yc-y)
    glVertex2i(xc-x, yc-y)
    if fill:
        for i in range(xc-x, xc+x):
            glVertex2i(i, yc+y)
            glVertex2i(i, yc-y)


def draw_quad(color, tl, tr, br, bl, fill=True):
    if not fill:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(2)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1)
    glBegin(GL_POLYGON)
    glColor4f(*color.rgba())
    glVertex2f(*tl)
    glVertex2f(*tr)
    glVertex2f(*br)
    glVertex2f(*bl)
    glEnd()
