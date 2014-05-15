import sys
from PySide.QtGui import *
from PySide.QtCore import *
from app_ui import Ui_App_form
from controller import Controller
from model import Model


class AppMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(AppMainWindow, self).__init__(parent=parent)
        self.cwidg = AppCentralWidget()
        self.setCentralWidget(self.cwidg)


class AppCentralWidget(QWidget):
    def __init__(self, parent=None):
        super(AppCentralWidget, self).__init__(parent=parent)
        self.ui = Ui_App_form()
        self.ui.setupUi(self)
        self.controller = Controller(self.ui.w_drawWidg)
        self.model = Model(self.ui.w_drawWidg, self.controller)
        self.ui.w_drawWidg.set_controller(self.controller)
        self.ui.w_drawWidg.set_model(self.model)
        self.ui.pb_color.clicked.connect(self.pick_color)
        self.ui.pb_line.clicked.connect(self.controller.line_button_hit)
        self.ui.pb_square.clicked.connect(self.controller.square_button_hit)
        self.ui.pb_rectangle.clicked.connect(self.controller.rectangle_button_hit)
        self.ui.pb_circle.clicked.connect(self.controller.circle_button_hit)
        self.ui.pb_ellipse.clicked.connect(self.controller.ellipse_button_hit)
        self.ui.pb_triangle.clicked.connect(self.controller.triangle_button_hit)
        self.ui.pb_select.clicked.connect(self.controller.select_button_hit)
        self.ui.pb_zoom_in.clicked.connect(self.controller.zoomIn_button_hit)
        self.ui.pb_zoom_out.clicked.connect(self.controller.zoomOut_button_hit)
        self.ui.sl_alpha.valueChanged.connect(self.change_alpha)
        self.change_alpha(1000)
        # self.ui.pb_home.clicked.connect(self.controller.)
        # self.ui.pb_camera.clicked.connect(self.controller.)

    def change_alpha(self, v):
        self.alpha = float(v)/1000
        self.controller.alpha_slider_changed(self.alpha)

    def pick_color(self):
        picker = QColorDialog()
        picker.setOption(QColorDialog.ShowAlphaChannel, on=True)
        color = picker.getColor(options=[QColorDialog.ShowAlphaChannel, QColorDialog.DontUseNativeDialog])
        color.setAlphaF(self.alpha)
        self.controller.color_button_hit(color.redF(), color.greenF(), color.blueF(), self.alpha)


def main():
    app = QApplication(sys.argv)
    mw = AppMainWindow()
    mw.show()
    mw.raise_()
    app.exec_()


if __name__ == "__main__":
    main()
