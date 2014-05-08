from model import Color


class Controller():
    def __init__(self, view):
        self.view = view
        self.draw_mode = 'ellipse'
        self.draw_color = Color(0.0, 0.0, 0.0, 1.0)

    def draw(self):
        self.view.draw(self.draw_mode)

    def color_button_hit(self, c):
        self.draw_color = Color(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def triangle_button_hit(self):
        self.draw_mode = 'triangle'

    def square_button_hit(self):
        self.draw_mode = 'square'

    def rectangle_button_hit(self):
        self.draw_mode = 'rectangle'

    def circle_button_hit(self):
        self.draw_mode = 'circle'

    def ellipse_button_hit(self):
        self.draw_mode = 'ellipse'

    def line_button_hit(self):
        self.draw_mode = 'line'

    def select_button_hit(self):
        pass

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
