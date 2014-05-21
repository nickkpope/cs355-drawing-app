from model import Color


class Controller():
    def __init__(self, view):
        self.view = view
        self.draw_mode = 'select'
        self.selected_shape = None
        self.draw_color = Color(0.0, 0.0, 0.0, 1.0)
        self.selected_draw_color = Color(0.0, 0.0, 0.0, 1.0)
        self.view.update_color_indicator(*self.draw_color.rgba())

    def draw(self):
        self.view.draw(self.draw_mode)

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
        pass

    def zoomOut_button_hit(self):
        pass

    def h_scrollbar_changed(self, value):
        pass

    def v_scrollbar_changed(self, value):
        pass

    def toggle_3D_model_display(self):
        pass

    def key_pressed(self, iterator):
        pass

    def do_edge_detection(self):
        pass

    def do_sharpen(self):
        pass

    def do_median_blur(self):
        pass

    def do_uniform_blur(self):
        pass

    def do_change_contrast(self, contrast_amount_num):
        pass

    def do_change_brightness(self, brightness_amount_num):
        pass

    def do_load_image(self, open_image):
        pass

    def toggle_background_display(self):
        pass
