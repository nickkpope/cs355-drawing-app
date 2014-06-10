import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
from OpenGL.GLU import *
from OpenGL.GL import *
from math import *

houses = [(0, 0, 0)]
for i in range(-100, 100, 10):
    for j in range(0, 100, 10):
        houses.append((i, 0, j))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)
        self.glwidg = GLWidget(self)
        self.resize(512, 512)
        self.camera = Camera(512, 512)
        self.setCentralWidget(self.glwidg)

    def keyPressEvent(self, event):
        key = event.key()
        move_amount = .5
        if key == Qt.Key_A:
            self.camera.move_left(move_amount)
        elif key == Qt.Key_D:
            self.camera.move_right(move_amount)
        elif key == Qt.Key_W:
            self.camera.move_forward(move_amount)
        elif key == Qt.Key_S:
            self.camera.move_backward(move_amount)
        elif key == Qt.Key_Q:
            self.camera.turn_left(move_amount+2)
        elif key == Qt.Key_E:
            self.camera.turn_right(move_amount+2)
        elif key == Qt.Key_R:
            self.camera.move_up(move_amount)
        elif key == Qt.Key_F:
            self.camera.move_down(move_amount)
        elif key == Qt.Key_O:
            self.camera.view_ortho()
        elif key == Qt.Key_P:
            self.camera.view_persp()
        elif key == Qt.Key_H:
            self.camera.reset()

        self.camera.set_camera()
        self.glwidg.updateGL()


class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.parent = parent
        self.setFocus(Qt.OtherFocusReason)

    def initializeGL(self):
        self.qglClearColor(QColor(0, 0, 0))
        self.qglColor(QColor(0, 0, 0))
        self.parent.camera.set_camera()

    def paintGL(self):
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for i in houses:
            draw_house(offset=i)
        glFlush()


class Camera():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.fovy = 0
        self.reset()

    def reset(self):
        self.persp = True
        self.x = 0
        self.y = 0
        self.z = 10.0
        self.roty = 0.0

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
        glViewport(0, 0, self.w, self.h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.persp:
            gluPerspective(45.0, self.w/self.h, .01, 100.0)
        else:
            # glOrtho(0, self.w, 0, self.h, -1.0, 1.0)
            # gluLookAt( eyeX , eyeY , eyeZ , centerX , centerY , centerZ , upX , upY , upZ )
            # glOrtho(-3.7, 3.7, -3.7, 3.7, .01, 100.0)
            # glOrtho(-3.7, 3.7, -3.7, 3.7, .01, 100.0)
            try:
                glOrtho(self.z*-.1, self.z*.1, self.z*-.1, self.z*.1, .01, 100.0)
            except:
                glOrtho(-.1, .1, -.1, .1, .01, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotate(self.roty, 0, 1, 0)
        glTranslate(-self.x, -self.y, -self.z)
        if not self.persp:
            glMultMatrixf([[1, 0,  0, 0],
                           [0, 1,  0, 0],
                           [0, 0, -1, 0],
                           [0, 0,  0, 1]])


def draw_house(offset=(0, 0, 0)):
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glTranslate(*offset)
    glBegin(GL_LINES)
    glColor4f(0, 1, 1, 0)

    for l in house_lines():
        glVertex3f(*l[0])
        glVertex3f(*l[1])

    glEnd()
    glPopMatrix()


def house_lines():
    lines = []

    def add_line_point(x, y, z):
        if len(lines) == 0:
            lines.append([(x*1.5, y, z)])
        else:
            if len(lines[-1]) == 2:
                lines.append([(x*1.5, y, z)])
            else:
                lines[-1].append((x*1.5, y, z))

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


def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    mw.raise_()
    app.exec_()


if __name__ == '__main__':
    main()
