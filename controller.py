from model import Color, Point, Camera, house_lines
from PySide.QtCore import *
from PySide.QtGui import *


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
        pass

    def do_sharpen(self):
        pass

    def do_median_blur(self):
        pass

    def do_uniform_blur(self):
        pass

    def do_change_contrast(self, contrast_amount_num):
        print 'changing contrast by', contrast_amount_num

    def do_change_brightness(self, brightness_amount_num):
        print 'changing brightness by', brightness_amount_num

    def do_load_image(self, open_image):
        self.view.draw_image(open_image)

    def toggle_background_display(self):
        pass

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
