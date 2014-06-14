from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
from OpenGL.GLU import *
from OpenGL.GL import *
from model import Transform2d, Color, Point, Shape, Line, Rectangle, Square, Ellipse, Circle, Triangle
import numpy as np
import copy


class ColorIndicator(QWidget):
    def __init__(self, parent=None):
        super(ColorIndicator, self).__init__(parent=parent)
        self.color = None

    def update_color(self, r, g, b, a):
        self.color = QColor()
        self.color.setRgbF(r, g, b, a)
        self.update()

    def paintEvent(self, event):
        if self.color:
            painter = QPainter(self)
            cx = self.size().width()
            cy = self.size().height()
            painter.setBackgroundMode(Qt.OpaqueMode)
            bg = QColor(0, 0, 0)
            fg = QColor(255, 255, 255)
            painter.fillRect(0, 0, cx, cy, bg)
            painter.fillRect(cx/4, cy/4, cx/2, cy/2, fg)
            painter.fillRect(0, 0, cx, cy, self.color)


class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.parent = parent
        self.setFocus(Qt.OtherFocusReason)
        self.clear_color = (1, 1, 1, 1)
        self.texture_id = None

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
        glClearColor(*self.clear_color)
        glClear(GL_COLOR_BUFFER_BIT)
        self.parent.draw()

        if not self.texture_id is None:
            self.draw_image()
        glFlush()

    def set_image(self, image):
        print 'setting image'
        image.convertToFormat(QImage.Format_ARGB32)
        data = QGLWidget.convertToGLFormat(image)
        data.convertToFormat(QImage.Format_ARGB32)
        self.iwidth = image.width()
        self.iheight = image.height()

        # generate a texture id, make it current
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # texture mode and parameters controlling wrapping and scaling
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        # glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.iwidth, self.iheight, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, str(data.bits()))

        glDisable(GL_TEXTURE_2D)

    def draw_image(self):
        glPushAttrib(GL_TEXTURE_BIT | GL_ENABLE_BIT | GL_TRANSFORM_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)

        # map the image data to the texture. note that if the input
        # type is GL_FLOAT, the values must be in the range [0..1]
        # glDepthMask(False)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glColor3f(1, 1, 1)

        glBegin(GL_QUADS)
        # glVertex2f(-self.iwidth, self.iheight)
        # glTexCoord2f(-self.iwidth, self.iheight)
        # glVertex2f(self.iwidth, self.iheight)
        # glTexCoord2f(self.iwidth, self.iheight)
        # glVertex2f(self.iwidth, -self.iheight)
        # glTexCoord2f(self.iwidth, -self.iheight)
        # glVertex2f(-self.iwidth, -self.iheight)
        # glTexCoord2f(-self.iwidth, -self.iheight)

        glVertex2f(0, 0)
        glTexCoord2f(0, 0)
        glVertex2f(0, self.iheight)
        glTexCoord2f(0, self.iheight)
        glVertex2f(self.iwidth, self.iheight)
        glTexCoord2f(self.iwidth, self.iheight)
        glVertex2f(self.iwidth, 0)
        glTexCoord2f(self.iwidth, 0)

        glEnd()
        glDisable(GL_TEXTURE_2D)

        glPopAttrib()


class DrawWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawWidget, self).__init__(parent=parent)
        self.setFixedSize(512, 512)
        self.canvas = GLWidget(self)
        self.canvas.setFixedSize(512, 512)
        self.canvas.move(self.pos())
        self.controller = None
        self.model = None
        self.setCursor(Qt.CrossCursor)
        self.clear_state()
        self.viewport = Viewport(2048, 2048)

        self.draw_map = {}
        self.reshape_map = {}
        self.shape_types_map = {}
        shape_descs = [
            ('line', self.draw_line, self.reshape_line, Line),
            ('rectangle', self.draw_rectangle, self.reshape_rectangle, Rectangle),
            ('square', self.draw_square, self.reshape_square, Square),
            ('ellipse', self.draw_ellipse, self.reshape_ellipse, Ellipse),
            ('circle', self.draw_circle, self.reshape_circle, Circle),
            ('triangle', self.draw_triangle, self.reshape_triangle, Triangle),
            ('select', self.draw_nothing, self.draw_nothing, Shape)
        ]
        for tn, d, u, t in shape_descs:
            self.draw_map[tn] = d
            self.reshape_map[tn] = u
            self.shape_types_map[tn] = t

    def update_color_indicator(self, r, g, b, a):
        self.parent().ui.w_color_indicator.update_color(r, g, b, a)

    def clear_state(self):
        self.press_pos = Point(0, 0)
        self.draw_shape = None
        self.tri_shape = None
        self.rotating = False
        self.rot_handle = None
        self.selected_handle_index = -1
        self.active_handles = []
        self.shape_orig_center = None
        self.opress_pos = None
        self.selected_line_endpoint = None
        self.d_vec = Point(0, 0)
        self.move_pos = None

    def clear(self):
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        # glEnable(GL_POINT_SMOOTH)

    def to_screen(self, x, y):
        return Point(x, self.size().height()-y)  # not sure why widgets are missaligned like this but whatever.

    def set_controller(self, controller):
        self.controller = controller

    def set_model(self, model):
        self.model = model

    def mousePressEvent(self, event):
        self.press_pos = self.viewport.to_world(self.to_screen(event.pos().x(), event.pos().y()))
        print 'press', self.press_pos
        if self.controller.draw_mode == 'select':
            handle_clicked = False
            if self.rot_handle:
                if self.rot_handle.is_inside(self.press_pos):
                    self.rotating = True
                    handle_clicked = True

            # check active handles for click event
            for i, h in enumerate(self.active_handles):
                if h.is_inside(self.press_pos):
                    self.selected_handle_index = i
                    handle_clicked = True
                    self.hd_vec = self.press_pos - h.center
                    break

            found_shape = False
            if not handle_clicked:
                for s in reversed(self.model.shapes):
                    if s.type == 'line':
                        print 'tolerance', 4/self.controller.zoom_amount()
                        is_inside = s.is_inside(self.press_pos, tolerance=4/self.controller.zoom_amount())
                    else:
                        is_inside = s.is_inside(self.press_pos)

                    if is_inside:
                        self.controller.selected_shape = s
                        print 'found selected shape', self.controller.selected_shape.color
                        found_shape = True
                        break

            if found_shape:
                self.controller.selected_draw_color = self.controller.selected_shape.color
                self.d_vec = self.press_pos - self.controller.selected_shape.center
                self.update_color_indicator(*self.controller.selected_shape.color.rgba())
            else:
                self.update_color_indicator(*self.controller.draw_color.rgba())

            if not found_shape and not handle_clicked:
                self.controller.selected_shape = None
        else:
            self.draw_shape = self.shape_types_map[self.controller.draw_mode](
                copy.deepcopy(self.controller.draw_color),
                self.press_pos)
            print 'drawing', self.draw_shape

    def mouseMoveEvent(self, event):
        self.move_pos = self.viewport.to_world(self.to_screen(event.pos().x(), event.pos().y()))
        # print ' move', self.move_pos
        if self.controller.selected_shape and self.controller.draw_mode == 'select':
            if self.rotating:
                theta = (self.move_pos - self.controller.selected_shape.center).angle_between(Point(1, 0))
                if self.move_pos.y < self.controller.selected_shape.center.y:
                    theta *= -1
                self.controller.selected_shape.rotation = theta
            elif self.selected_handle_index >= 0:
                self.reshape_map[self.controller.selected_shape.type]()
            else:
                self.controller.selected_shape.center = self.move_pos - self.d_vec
        self.canvas.updateGL()

    def mouseReleaseEvent(self, event):
        self.move_pos = None
        self.active_handles = []
        self.selected_handle_index = None
        self.rotating = False
        if self.controller.selected_shape:
            if self.controller.selected_shape.type == 'rectangle' or self.controller.draw_mode == 'ellipse':
                self.controller.selected_shape.w = abs(self.controller.selected_shape.w)
                self.controller.selected_shape.h = abs(self.controller.selected_shape.h)
        self.finish(self.to_screen(event.pos().x(), event.pos().y()))

    def draw(self):
        for shape in self.model.shapes:
            self.draw_map[shape.type](shape)

        if self.move_pos:
            self.draw_map[self.controller.draw_mode](self.draw_shape, pos=self.move_pos)

        if self.controller.threeD_mode:
            self.draw_house(self.controller.house_lines())

        if self.controller.selected_shape:

            # Draw outline shape
            outline = copy.deepcopy(self.controller.selected_shape)
            outline.color = Color(1, 0, 0)
            self.draw_map[outline.type](outline, fill=False)

            # Draw object handles
            self.active_handles = []
            for p in self.controller.selected_shape.handle_positions():
                c = Circle(Color(1, 0, 0), self.controller.selected_shape.to_world(p), 5)
                self.active_handles.append(c)
                self.draw_circle(c, fill=False, fixed_size=True)

            # Draw rotation handle if needed
            if self.controller.selected_shape.type != 'line':
                obb = shape.bounding_box()
                rot_handle_x = max(obb.tl().x, obb.tr().x)
                rot_handle_y = (obb.tr().y + obb.br().y)/2
                rot_handle_point = outline.to_world(Point(rot_handle_x, rot_handle_y)) + Point(15, 0)
                self.rot_handle = Circle(Color(1, 0, 0), rot_handle_point, 5)
                self.draw_circle(self.rot_handle, fixed_size=True)

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
            draw_line(shape.color, self.viewport.to_view(shape.p1).vec(), self.viewport.to_view(shape.p2).vec())

    def reshape_line(self):
        if self.active_handles[self.selected_handle_index].center == self.controller.selected_shape.p1:
            self.controller.selected_shape.p1 = self.move_pos - self.hd_vec
        elif self.active_handles[self.selected_handle_index].center == self.controller.selected_shape.p2:
            self.controller.selected_shape.p2 = self.move_pos - self.hd_vec

    def draw_rectangle(self, shape, pos=None, fill=True):
        if pos:
            w = abs(pos.x - self.press_pos.x)/2
            h = abs(pos.y - self.press_pos.y)/2
            top_left = Point(0, 0)

            if pos.x < self.press_pos.x:  # hovering left of initial click
                top_left.x = pos.x
            else:
                top_left.x = self.press_pos.x

            if pos.y > self.press_pos.y:  # hovering above initial click
                top_left.y = pos.y
            else:
                top_left.y = self.press_pos.y

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
            self.viewport.to_view(shape.to_world(Point(-shape.w, +shape.h))).xy(),
            self.viewport.to_view(shape.to_world(Point(+shape.w, +shape.h))).xy(),
            self.viewport.to_view(shape.to_world(Point(+shape.w, -shape.h))).xy(),
            self.viewport.to_view(shape.to_world(Point(-shape.w, -shape.h))).xy(),
            fill=fill)

    def reshape_rectangle(self):
        self.bounding_box_reshape(self.controller.selected_shape)

    def draw_square(self, shape, pos=None, fill=True):
        if pos:
            dx = abs(pos.x - self.press_pos.x)/2
            dy = abs(pos.y - self.press_pos.y)/2
            shape.size = min(dx, dy)
            top_left = Point(0, 0)
            if pos.x < self.press_pos.x:  # hovering left of initial click
                top_left.x = self.press_pos.x - shape.size*2
            else:
                top_left.x = self.press_pos.x

            if pos.y > self.press_pos.y:  # hovering above initial click
                top_left.y = self.press_pos.y + shape.size*2
            else:
                top_left.y = self.press_pos.y

            shape.center = Point(top_left.x + shape.size, top_left.y - shape.size)

        if not (shape.center and shape.size):
            return

        draw_quad(
            shape.color,
            self.viewport.to_view(shape.to_world(Point(-shape.size, +shape.size))).xy(),  # top left corner
            self.viewport.to_view(shape.to_world(Point(+shape.size, +shape.size))).xy(),  # top right corner
            self.viewport.to_view(shape.to_world(Point(+shape.size, -shape.size))).xy(),  # bottom right corner
            self.viewport.to_view(shape.to_world(Point(-shape.size, -shape.size))).xy(),  # bottom left corner
            fill=fill
        )

    def reshape_square(self):
        move_pos = self.controller.selected_shape.to_object(self.move_pos)
        self.controller.selected_shape.size = min(abs(move_pos.x), abs(move_pos.y))
        # self.square_bbox_reshape(self.controller.selected_shape)

    def draw_ellipse(self, shape, pos=None, fill=True):
        if pos:
            w = abs(pos.x - self.press_pos.x)
            h = abs(pos.y - self.press_pos.y)
            if pos.x < self.press_pos.x:  # hovering left of initial click
                tlx = pos.x
                trx = self.press_pos.x
            else:
                tlx = self.press_pos.x
                trx = pos.x

            if pos.y > self.press_pos.y:  # hovering above initial click
                tly = pos.y
                try_ = self.press_pos.y
            else:
                tly = self.press_pos.y
                try_ = pos.y
            shape.center = self.viewport.to_world(Point((tlx + trx)/2, (tly + try_)/2))

            shape.w = w/2
            shape.h = h/2

        if not (shape.center and shape.w and shape.h):
            return

        center = self.viewport.to_view(shape.center)
        rot = {'angle': shape.rotation, 'x': center.x, 'y': center.y}
        draw_ellipse(shape.color,
                     center.x,
                     center.y,
                     abs(shape.w)*self.controller.zoom_amount(),
                     abs(shape.h)*self.controller.zoom_amount(),
                     fill=fill,
                     rot=rot)

    def reshape_ellipse(self):
        self.bounding_box_reshape(self.controller.selected_shape)

    def draw_circle(self, shape, pos=None, fill=True, fixed_size=False):
        if pos:
            dw = abs(pos.x - self.press_pos.x)/2
            dh = abs(pos.y - self.press_pos.y)/2
            shape.radius = min(dw, dh)
            if pos.x < self.press_pos.x:  # hovering left of initial click
                tlx = self.press_pos.x - shape.radius*2
                trx = self.press_pos.x
            else:
                tlx = self.press_pos.x
                trx = self.press_pos.x + shape.radius*2

            if pos.y > self.press_pos.y:  # hovering above initial click
                tly = self.press_pos.y + shape.radius*2
                try_ = self.press_pos.y
            else:
                tly = self.press_pos.y
                try_ = self.press_pos.y - shape.radius*2
            shape.center = self.viewport.to_view(Point((tlx + trx)/2, (tly + try_)/2))
            shape.radius = shape.radius*self.controller.zoom_amount()

        if not (shape.center and shape.radius):
            return
        center = self.viewport.to_view(shape.center)

        if fixed_size:
            radius = shape.radius
        else:
            radius = shape.radius*self.controller.zoom_amount()

        draw_ellipse(shape.color,
                     center.x,
                     center.y,
                     radius,
                     radius,
                     fill=fill)

    def reshape_circle(self):
        move_pos = self.controller.selected_shape.to_object(self.move_pos)
        self.controller.selected_shape.radius = min(abs(move_pos.x), abs(move_pos.y))

    def draw_triangle(self, shape, pos=None, fill=True):
        # convert back to world
        draw_triangle(shape.color,
                      self.viewport.to_view(shape.to_world(shape.p1)).xy(),
                      self.viewport.to_view(shape.to_world(shape.p2)).xy(),
                      self.viewport.to_view(shape.to_world(shape.p3)).xy(),
                      fill=fill)

    def reshape_triangle(self):
        p1 = self.controller.selected_shape.to_world(self.controller.selected_shape.p1)
        p2 = self.controller.selected_shape.to_world(self.controller.selected_shape.p2)
        p3 = self.controller.selected_shape.to_world(self.controller.selected_shape.p3)
        move_pos = self.controller.selected_shape.to_object(self.move_pos - self.hd_vec)

        if self.active_handles[self.selected_handle_index].center == p1:
            self.controller.selected_shape.p1 = move_pos
        elif self.active_handles[self.selected_handle_index].center == p2:
            self.controller.selected_shape.p2 = move_pos
        elif self.active_handles[self.selected_handle_index].center == p3:
            self.controller.selected_shape.p3 = move_pos
        else:
            print 'could not find triangle point on update'

    def draw_house(self, houses):
        for lines in houses:
            # print 'drawing house, yay!'
            for l in lines:
                # perform clip test
                p1 = l[0]
                p2 = l[1]

                p1x_out = p1[0] < -p1[3] or p1[0] > p1[3]
                p1y_out = p1[1] < -p1[3] or p1[1] > p1[3]
                p1z_out = p1[2] < -p1[3] or p1[2] > p1[3]

                p1_out = p1x_out or p1y_out or p1z_out

                p2x_out = p2[0] < -p2[3] or p2[0] > p2[3]
                p2y_out = p2[1] < -p2[3] or p2[1] > p2[3]
                p2z_out = p2[2] < -p2[3] or p2[2] > p2[3]

                p2_out = p2x_out or p2y_out or p2z_out

                if p1_out or p2_out:
                    continue

                # divide by w
                p1 = [i/l[0][3] for i in l[0][:2]]
                p2 = [i/l[1][3] for i in l[1][:2]]

                # apply viewport transformation
                p1 = [1080+i*2048 for i in p1]
                p2 = [1080+i*2048 for i in p2]

                # draw line
                vl = Line(Color(0, 1, 1), Point(*p1), Point(*p2))
                self.draw_line(vl)  # applies viewing transformation

    def draw_image(self, image):
        self.canvas.set_image(image)
        self.canvas.updateGL()

    def square_bbox_reshape(self, shape):
            # determine which corner was picked
            hc = shape.to_object(self.active_handles[self.selected_handle_index].center)
            w = h = shape.size
            # put new position in object space
            move_pos = shape.to_object(self.move_pos - self.hd_vec)

            # update shape
            dp = (move_pos - hc)/2.0
            if int(hc.x) == int(shape.bounding_box().tl().x) and int(hc.y) == int(shape.bounding_box().tl().y):
                w -= dp.x
                h += dp.y
            elif int(hc.x) == int(shape.bounding_box().tr().x) and int(hc.y) == int(shape.bounding_box().tr().y):
                w += dp.x
                h += dp.y
            elif int(hc.x) == int(shape.bounding_box().br().x) and int(hc.y) == int(shape.bounding_box().br().y):
                w += dp.x
                h -= dp.y
            elif int(hc.x) == int(shape.bounding_box().bl().x) and int(hc.y) == int(shape.bounding_box().bl().y):
                w -= dp.x
                h -= dp.y
            else:
                print 'could not determine picked handle'

            shape.size = min(abs(w), abs(h))
            if (dp.x == 0 and dp.y < 0) or (dp.x == 0 and dp.y > 0):  # down or up
                if move_pos.x < 0:
                    dp.x = -dp.y
                else:
                    dp.x = dp.y
            elif (dp.x < 0 and dp.y == 0) or (dp.x > 0 and dp.y == 0):  # left or right
                if move_pos.y < shape.center.y:
                    dp.y = -dp.x
                else:
                    dp.y = dp.x

            shape.center += shape.to_world(dp, trans=False)

    def bounding_box_reshape(self, shape):
            # determine which corner was picked
            hc = shape.to_object(self.active_handles[self.selected_handle_index].center)

            # put new position in object space
            move_pos = shape.to_object(self.move_pos - self.hd_vec)

            # update shape
            dp = (move_pos - hc)/2.0
            if int(hc.x) == int(shape.bounding_box().tl().x) and int(hc.y) == int(shape.bounding_box().tl().y):
                shape.w -= dp.x
                shape.h += dp.y
            elif int(hc.x) == int(shape.bounding_box().tr().x) and int(hc.y) == int(shape.bounding_box().tr().y):
                shape.w += dp.x
                shape.h += dp.y
            elif int(hc.x) == int(shape.bounding_box().br().x) and int(hc.y) == int(shape.bounding_box().br().y):
                shape.w += dp.x
                shape.h -= dp.y
            elif int(hc.x) == int(shape.bounding_box().bl().x) and int(hc.y) == int(shape.bounding_box().bl().y):
                shape.w -= dp.x
                shape.h -= dp.y
            else:
                print 'could not determine picked handle'

            shape.center += shape.to_world(dp, trans=False)


class Viewport():
    def __init__(self, world_w, world_h):
        self.world_w = world_w
        self.world_h = world_h
        self.set_offset(0, 0)
        self.set_scale(1)

    def set_offset(self, x, y):
        self.x = x
        self.y = y

    def set_scale(self, s):
        self.s = s

    def to_view(self, p):
        t = Transform2d()
        t.scale(self.s, self.s)
        t.translate(Point(-self.x, -self.y))
        return t.transform(p)

    def to_world(self, p):
        t = Transform2d()
        t.translate(Point(self.x, self.y))
        t.scale(1/self.s, 1/self.s)
        return t.transform(p)


def draw_line(color, p1, p2):
    glBegin(GL_LINES)
    glColor4f(*color.rgba())
    glVertex2i(*[int(i) for i in p1])
    glVertex2i(*[int(i) for i in p2])
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
    # if fill:
    #     for i in range(xc-x, xc+x):
    #         glVertex2i(i, yc+y)
    #         glVertex2i(i, yc-y)


def draw_quad(color, tl, tr, br, bl, fill=True):
    if not fill:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(2)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1)
    glBegin(GL_POLYGON)
    glColor4f(*color.rgba())
    glVertex2f(*[int(i) for i in tl])
    glVertex2f(*[int(i) for i in tr])
    glVertex2f(*[int(i) for i in br])
    glVertex2f(*[int(i) for i in bl])
    glEnd()
