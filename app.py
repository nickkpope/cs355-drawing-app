import sys
from PySide.QtGui import *
from PySide.QtCore import *
from app_ui import Ui_App_form
from controller import Controller
from model import Model


class AppMainWindow(QMainWindow):
    update_progress = Signal(int)
    process_finished = Signal(bool)
    update_track_progress = Signal(str, int)
    mw_exiting = Signal()

    def __init__(self, parent=None):
        super(AppMainWindow, self).__init__(parent=parent)
        self.cwidg = AppCentralWidget()
        self.setCentralWidget(self.cwidg)

        self.file_menu = QMenu('File')
        self.file_menu.addAction('Load', self.load_image)
        self.file_menu.addAction('Save', self.do_nothing)

        self.edit_menu = QMenu('Edit')
        self.edit_menu.addAction('Brightness', self.get_brightness)
        self.edit_menu.addAction('Contrast', self.get_contrast)
        self.edit_menu.addAction('Blur (Uniform)', self.cwidg.controller.do_uniform_blur)
        self.edit_menu.addAction('Blur (Median)', self.cwidg.controller.do_median_blur)
        self.edit_menu.addAction('Sharpen', self.cwidg.controller.do_sharpen)
        self.edit_menu.addAction('Edge Detection', self.cwidg.controller.do_edge_detection)

        self.menu_bar = QMenuBar()
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.edit_menu)
        self.setMenuBar(self.menu_bar)
        self.cwidg.controller.do_load_image(QImage("/Users/nick.pope/Downloads/Hue_Manatee_by_Bobert_Rob_face.jpg"))

        self.progress = QWidget()
        playout = QHBoxLayout()
        self.progressLabel = QLabel()
        self.progressBar = QProgressBar()
        playout.addWidget(self.progressLabel)
        playout.addWidget(self.progressBar)
        self.progress.setLayout(playout)

        self.update_progress.connect(self.progressBar.setValue)
        self.process_finished.connect(self.finish_track_progress)
        self.update_track_progress.connect(self.do_track_progress_update)

        self.statusBar = QStatusBar()
        self.statusBar.addWidget(self.progress)
        self.setStatusBar(self.statusBar)
        self.statusBar.hide()

    def closeEvent(self, e):
        self.cwidg.controller.close_down()
        e.accept()

    def track_progress(self, name, length):
        self.update_track_progress.emit(name, length)

    def do_track_progress_update(self, name, length):
        self.statusBar.show()
        self.progressLabel.setText(name)
        self.progressBar.setRange(0, length)

    def finish_track_progress(self, success):
        if success:
            self.statusBar.hide()
        else:
            self.progressLabel.setText('Process Failed')

    def load_image(self):
        fileName = QFileDialog.getOpenFileName(self,
                                               "Open Image",
                                               "",
                                               "Image Files (*.png *.jpg *.bmp)")[0]
        if (fileName):
            self.cwidg.controller.do_load_image(QImage(fileName))

    def get_brightness(self):
        amount, success = QInputDialog.getInt(self, "Adjust Brightness", "Please input the desired brightness amount.")
        if success:
            self.cwidg.controller.do_change_brightness(amount)

    def get_contrast(self):
        amount, success = QInputDialog.getInt(self, "Adjust Contrast", "Please input the desired contrast amount.")
        if success:
            self.cwidg.controller.do_change_contrast(amount)

    def do_nothing(self):
        pass

    def keyPressEvent(self, event):
        self.cwidg.keyPressEvent(event)


class AppCentralWidget(QWidget):
    def __init__(self, parent=None):
        super(AppCentralWidget, self).__init__(parent=parent)
        self.ui = Ui_App_form()
        self.ui.setupUi(self)
        self.ui.verticalScrollBar.setMinimum(0)
        self.ui.verticalScrollBar.setMaximum(2048)
        self.ui.horizontalScrollBar.setMinimum(0)
        self.ui.horizontalScrollBar.setMaximum(2048)
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
        self.ui.pb_home.clicked.connect(self.controller.toggle_3D_model_display)
        self.ui.pb_camera.clicked.connect(self.controller.toggle_background_display)
        self.ui.verticalScrollBar.sliderMoved.connect(self.controller.v_scrollbar_changed)
        self.ui.verticalScrollBar.setInvertedAppearance(True)
        self.ui.horizontalScrollBar.sliderMoved.connect(self.controller.h_scrollbar_changed)

    def change_alpha(self, v):
        self.alpha = float(v)/1000
        self.controller.alpha_slider_changed(self.alpha)

    def pick_color(self):
        picker = QColorDialog()
        picker.setOption(QColorDialog.ShowAlphaChannel, on=True)
        color = picker.getColor(options=[QColorDialog.ShowAlphaChannel, QColorDialog.DontUseNativeDialog])
        color.setAlphaF(self.alpha)
        self.controller.color_button_hit(color.redF(), color.greenF(), color.blueF(), self.alpha)

    def keyPressEvent(self, event):
        self.controller.key_pressed(event)


def main():
    app = QApplication(sys.argv)
    mw = AppMainWindow()
    mw.show()
    mw.raise_()
    app.exec_()


if __name__ == "__main__":
    main()
