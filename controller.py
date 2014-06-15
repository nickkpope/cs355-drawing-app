from model import Color, Point, Camera, house_lines, Image, Pixel
from PySide.QtCore import *
from PySide.QtGui import *
import cProfile
import sys
import traceback
from math import sqrt
import numpy as np
import time


class Controller():
    def __init__(self, view):
        self.view = view
        self.draw_mode = 'select'
        self.viewable_size = 512
        self.selected_shape = None
        self.draw_color = Color(0.0, 0.0, 0.0, 1.0)
        self.selected_draw_color = Color(0.0, 0.0, 0.0, 1.0)
        self.view.update_color_indicator(*self.draw_color.rgba())
        self.zoom_list = [.25, .5, 1.0, 2.0, 4.0]
        self.zoom_list.sort(reverse=True)
        self.zoom_level = 2
        self.set_v_scrollbar_size(512)
        self.set_h_scrollbar_size(512)
        self.camera = Camera(2048, 2048)
        self.threeD_mode = False
        self.img_mode = False
        self.t = None
        self.waiters = []
        self.current_image = None

        for w in QApplication.topLevelWidgets():
            if isinstance(w, QMainWindow):
                self.main_window = w
                break

    def close_down(self):
        if self.t:
            self.t.quit()

        for w in self.waiters:
            w.quit()
        return True

    def update_progress(self, v):
        self.main_window.update_progress.emit(v)

    def process_finished(self, img):
        if img:
            self.main_window.process_finished.emit(True)
            self.view.draw_image(img)
        else:
            self.main_window.process_finished.emit(False)
            self.view.draw_image()

    def color_button_hit(self, r, g, b, a):
        color = color = Color(r, g, b, a)
        if self.selected_shape:
            self.view.clear()
            self.selected_draw_color = color
            self.selected_shape.color = color
            self.view.update_color_indicator(*self.selected_shape.color.rgba())
            print 'selected color', self.selected_shape.color, id(self.selected_shape)
            self.view.canvas.updateGL()
        else:
            self.draw_color = color
            self.view.update_color_indicator(*self.draw_color.rgba())
            print 'draw color', self.draw_color

    def alpha_slider_changed(self, alpha):
        if self.selected_shape:
            self.selected_draw_color.a = alpha
            self.color_button_hit(*self.selected_draw_color.rgba())
        else:
            self.draw_color.a = alpha
            self.color_button_hit(*self.draw_color.rgba())

    def triangle_button_hit(self):
        self.view.clear_state()
        self.draw_mode = 'triangle'

    def square_button_hit(self):
        self.view.clear_state()
        self.draw_mode = 'square'

    def rectangle_button_hit(self):
        self.view.clear_state()
        self.draw_mode = 'rectangle'

    def circle_button_hit(self):
        self.view.clear_state()
        self.draw_mode = 'circle'

    def ellipse_button_hit(self):
        self.view.clear_state()
        self.draw_mode = 'ellipse'

    def line_button_hit(self):
        self.view.clear_state()
        self.draw_mode = 'line'

    def select_button_hit(self):
        self.view.clear_state()
        self.draw_mode = 'select'

    def zoomIn_button_hit(self):
        if self.zoom_in():
            self.update_zoom()
            zoom_width = (512/self.zoom_amount())/2
            newPos = min(self.h_scrollbar_position()+zoom_width, 2048)
            self.set_h_scrollbar_position(newPos)
            self.set_v_scrollbar_position(newPos)

    def zoomOut_button_hit(self):
        if self.zoom_out():
            self.update_zoom()
            zoom_width = (512/self.zoom_amount())/4
            newPos = max(self.h_scrollbar_position()-zoom_width, 0)
            self.set_h_scrollbar_position(newPos)
            self.set_v_scrollbar_position(newPos)

    def update_zoom(self):
        self.view.viewport.set_scale(self.zoom_amount())
        view_zoom = 512*1/self.zoom_amount()
        self.set_h_maximum(2048-view_zoom)
        self.set_v_maximum(2048-view_zoom)
        self.set_v_scrollbar_size(view_zoom)
        self.set_h_scrollbar_size(view_zoom)

    def set_h_maximum(self, m):
        self.view.parent().ui.horizontalScrollBar.setMaximum(m)

    def set_v_maximum(self, m):
        self.view.parent().ui.verticalScrollBar.setMaximum(m)

    def h_scrollbar_changed(self, value):
        self.view.viewport.set_offset(value, self.view.viewport.y)
        self.view.draw()
        self.view.canvas.updateGL()

    def v_scrollbar_changed(self, value):
        if self.img_mode:
            self.view.viewport.set_offset(self.view.viewport.x,
                                          self.view.parent().ui.horizontalScrollBar.maximum()-value)
        else:
            self.view.viewport.set_offset(self.view.viewport.x, value)
        self.view.draw()
        self.view.canvas.updateGL()

    def toggle_3D_model_display(self):
        self.threeD_mode = self.threeD_mode is False
        if self.threeD_mode:
            self.view.canvas.clear_color = (0, 0, 0, 0)
        else:
            self.view.canvas.clear_color = (1, 1, 1, 1)
        self.view.draw()
        self.view.canvas.updateGL()

    def key_pressed(self, event):
        if not self.threeD_mode:
            return

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
        elif key == Qt.Key_H:
            self.camera.reset()

        self.camera.set_camera()
        self.view.canvas.updateGL()

    def do_edge_detection(self):
        img = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        img_hor = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        img_ver = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        args = (img_hor, img_ver)
        limg = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)

        # make luminence
        self.apply_filter('Applying luminence for edge detect',
                          limg, self.luminance_filter)

        self.apply_filter('Doing edge detect', img, self.edge_detect_filter,
                          args=args, read_image=limg)

    def edge_detect_filter(self, read_image, x, y, img_hor, img_ver):
        xconstants = [-1, 0, 1,
                      -2, 0, 1,
                      -1, 0, 1]

        xr, xg, xb = self.spacial_filter(read_image, x, y, xconstants)

        yconstants = [-1, -2, -1,
                      0,  0,  0,
                      1,  2,  1]

        yr, yg, yb = self.spacial_filter(read_image, x, y, yconstants)
        v = sqrt(xr**2 + yr**2)
        return self.clip(v, v, v)

    def luminance_filter(self, read_image, x, y):
        c = self.pixel_at(read_image, x, y)
        v = (c.red() + c.green() + c.blue())/3
        return v, v, v

    def do_sharpen(self):
        constants = (0, -1, 0,
                     -1, 6, -1,
                     0, -1, 0)
        args = (constants,)
        kwargs = {'scale': 2}
        img = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        self.main_window.track_progress('Doing sharpen', img.height())
        self.apply_filter('Doing sharpen', img, self.spacial_filter, args=args, kwargs=kwargs)

    def do_median_blur(self):
        img = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        self.apply_filter('Doing median blur', img, self.median_filter)

    def do_uniform_blur(self):
        constants = (1, 1, 1,
                     1, 1, 1,
                     1, 1, 1)
        args = (constants,)
        kwargs = {'scale': 9}
        img = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        self.apply_filter('Doing uniform blur', img, self.spacial_filter, args, kwargs)

    def do_change_contrast(self, contrast_amount_num):
        print 'changing contrast by', contrast_amount_num
        img = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        args = (float(contrast_amount_num),)
        self.apply_filter('Doing contrast change', img, self.contrast_operation, args, {})

    def do_change_brightness(self, brightness_amount_num):
        print 'changing brightness by', brightness_amount_num
        constants = [0, 0, 0,
                     0, 1, 0,
                     0, 0, 0]
        img = QImage(self.view.image.qimage.width(), self.view.image.qimage.height(), QImage.Format_ARGB32)
        args = (constants,)
        kwargs = {'offset': brightness_amount_num}
        self.apply_filter('Doing change brightness', img, self.spacial_filter, args, kwargs)

    def do_load_image(self, open_image):
        self.view.image = Image(None, open_image, Point(1080, 1080), open_image.width(), open_image.height())
        if self.img_mode:
            self.view.draw_image(open_image)

    def apply_filter(self, label, write_img, func, args=(), kwargs={}, read_image=None):
        read_image = read_image or self.view.image.qimage
        # print write_img, self.view.image.qimage, write_img == self.view.image.qimage
        t = Filter_Thread(self, label, range(write_img.height()),
                          read_image, write_img, func, args, kwargs)
        startnew = False
        if self.t:
            if self.t.isRunning():
                w = Waiter(self, t)
                self.main_window.process_finished.connect(w.wake_up)
                self.waiters.append(w)
            else:
                startnew = True
        else:
            startnew = True

        if startnew:
            self.t = t
            self.t.start()
        return write_img

    def spacial_filter(self, read_image, x, y, constants, scale=1, offset=0):
        rtot = 0
        gtot = 0
        btot = 0
        for i, e in enumerate(self.neighbors(read_image, x, y)):
            if e:
                rtot += e.red()*constants[i]
                gtot += e.green()*constants[i]
                btot += e.blue()*constants[i]

        rtot = rtot/scale+offset
        gtot = gtot/scale+offset
        btot = btot/scale+offset
        return self.clip(rtot, gtot, btot)

    def median_filter(self, read_image, x, y):
        r = []
        g = []
        b = []
        for n in self.neighbors(read_image, x, y):
            if n:
                r.append(n.red())
                g.append(n.green())
                b.append(n.blue())
        r.sort()
        g.sort()
        b.sort()
        return r[len(r)/2], g[len(g)/2], b[len(b)/2]

    def clip(self, rtot, gtot, btot):
        rtot = max(0,   rtot)
        rtot = min(255, rtot)
        gtot = max(0,   gtot)
        gtot = min(255, gtot)
        btot = max(0,   btot)
        btot = min(255, btot)
        return rtot, gtot, btot

    def contrast_operation(self, read_image, x, y, c):
        p = self.pixel_at(read_image, x, y)
        r = ((c+100.0)/100.0)**4*(p.red()-128)+128
        g = ((c+100.0)/100.0)**4*(p.green()-128)+128
        b = ((c+100.0)/100.0)**4*(p.blue()-128)+128
        return self.clip(r, g, b)

    def neighbors(self, read_image, x, y):
        nw = self.pixel_at(read_image, x-1, y+1)
        nn = self.pixel_at(read_image, x,   y+1)
        ne = self.pixel_at(read_image, x+1, y+1)
        ww = self.pixel_at(read_image, x-1, y)
        cc = self.pixel_at(read_image, x,   y)
        ee = self.pixel_at(read_image, x+1, y)
        sw = self.pixel_at(read_image, x-1, y-1)
        ss = self.pixel_at(read_image, x,   y-1)
        se = self.pixel_at(read_image, x+1, y-1)
        return nw, nn, ne, ww, cc, ee, sw, ss, se

    def pixel_at(self, read_image, x, y):
        # if self.view.image.qimage.valid(x, y):
        if (x >= 0) and (x < self.view.image.fullw) and (y >= 0) and (y < self.view.image.fullh):
            return QColor(read_image.pixel(x, y))
        else:
            return None

    def toggle_background_display(self):
        self.img_mode = self.img_mode is False
        if self.img_mode:
            self.view.canvas.hide()
            self.view.draw_image()
        else:
            self.view.canvas.show()
            self.view.canvas.updateGL()

    # scroll bar interaction

    def v_scrollbar_size(self):
        return self.view.parent().ui.verticalScrollBar.pageStep()

    def h_scrollbar_size(self):
        return self.view.parent().ui.horizontalScrollBar.pageStep()

    def v_scrollbar_position(self):
        return self.view.parent().ui.verticalScrollBar.sliderPosition()

    def h_scrollbar_position(self):
        return self.view.parent().ui.horizontalScrollBar.sliderPosition()

    def set_v_scrollbar_size(self, size):
        self.view.parent().ui.verticalScrollBar.setPageStep(size)

    def set_h_scrollbar_size(self, size):
            self.view.parent().ui.horizontalScrollBar.setPageStep(size)

    def set_v_scrollbar_position(self, position):
        self.view.parent().ui.verticalScrollBar.setSliderPosition(position)
        self.v_scrollbar_changed(position)

    def set_h_scrollbar_position(self, position):
        self.view.parent().ui.horizontalScrollBar.setSliderPosition(position)
        self.h_scrollbar_changed(position)

    def zoom_amount(self):
        return self.zoom_list[self.zoom_level]

    def zoom_in(self):
        if self.zoom_level > 0:
            self.zoom_level -= 1
            return True
        else:
            return False

    def zoom_out(self):
        if self.zoom_level < len(self.zoom_list)-1:
            self.zoom_level += 1
            return True
        else:
            return False

    def house_lines(self):
        ret = []
        for i in range(-64, 64, 8):
            lines = house_lines(offset=(i, 0, 0))
            ret_lines = []
            for l in lines:
                ret_lines.append([self.camera.to_camera(*l[0]), self.camera.to_camera(*l[1])])
            ret.append(ret_lines)
        return ret


class Filter_Thread(QThread):
    def __init__(self, parent, label, yrange, read_image, write_image, func, args, kwargs):
        QThread.__init__(self)
        self.label = label
        self.parent = parent
        self.yrange = yrange
        self.read_image = read_image
        self.write_image = write_image
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.parent.main_window.track_progress(self.label, self.read_image.height())
            print self.label
            start = time.time()
            height = self.yrange[-1]
            # rangex = range(self.read_image.width())
            width = self.read_image.width()
            y = 0
            while y < height:
                self.parent.update_progress(y)
                x = 0
                while x < width:
                    fargs = (self.read_image, x, y) + self.args
                    r, g, b = self.func(*fargs, **self.kwargs)
                    self.write_image.setPixel(x, y, QColor(r, g, b).rgb())
                    x += 1
                y += 1
            print 'finished'
            end = time.time()
            print 'took', end - start
            self.parent.process_finished(self.write_image)
        except:
            etype, evalue, trace = sys.exc_info()
            print 'ERROR:', evalue
            traceback.print_tb(trace)
            self.parent.process_finished(None)


class Waiter(QThread):
    def __init__(self, parent, next):
        QThread.__init__(self)
        self.next = next
        self.parent = parent

    def run(self):
        while True:
            pass

    def wake_up(self, success):
        print 'waking up'
        if success:
            self.next.start()
            self.parent.t = self.next
        self.quit()
        self.parent.waiters.remove(self)


def test_image_access():
    q = QImage('/Users/nick.pope/Downloads/Grumpy_Cat_1k.jpg')
    rangex = range(q.width())
    for y in range(q.height()):
        for x in rangex:
            q.pixel(x, y)


def test_numpy_access():
    q = np.zeros((1080, 1337), dtype=np.int)
    rangex = range(1080)
    for y in range(1337):
        for x in rangex:
            get_pixel(q, x, y)


def get_pixel(q, x, y):
    return q[x][y]


def main():
    cProfile.run('test_image_access()', 'img_test')
    cProfile.run('test_numpy_access()', 'np_test')


if __name__ == '__main__':
    main()
