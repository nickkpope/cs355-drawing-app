# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'app.ui'
#
# Created: Tue May  6 08:40:51 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_App_form(object):
    def setupUi(self, App_form):
        App_form.setObjectName("App_form")
        App_form.resize(828, 773)
        self.horizontalLayout = QtGui.QHBoxLayout(App_form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pb_color = QtGui.QPushButton(App_form)
        self.pb_color.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/Colors.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_color.setIcon(icon)
        self.pb_color.setIconSize(QtCore.QSize(32, 32))
        self.pb_color.setObjectName("pb_color")
        self.verticalLayout_2.addWidget(self.pb_color)
        self.pb_line = QtGui.QPushButton(App_form)
        self.pb_line.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("res/Line.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_line.setIcon(icon1)
        self.pb_line.setIconSize(QtCore.QSize(32, 32))
        self.pb_line.setObjectName("pb_line")
        self.verticalLayout_2.addWidget(self.pb_line)
        self.pb_square = QtGui.QPushButton(App_form)
        self.pb_square.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("res/Square.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_square.setIcon(icon2)
        self.pb_square.setIconSize(QtCore.QSize(32, 32))
        self.pb_square.setObjectName("pb_square")
        self.verticalLayout_2.addWidget(self.pb_square)
        self.pb_rectangle = QtGui.QPushButton(App_form)
        self.pb_rectangle.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("res/Rectangle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_rectangle.setIcon(icon3)
        self.pb_rectangle.setIconSize(QtCore.QSize(32, 32))
        self.pb_rectangle.setObjectName("pb_rectangle")
        self.verticalLayout_2.addWidget(self.pb_rectangle)
        self.pb_circle = QtGui.QPushButton(App_form)
        self.pb_circle.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("res/Circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_circle.setIcon(icon4)
        self.pb_circle.setIconSize(QtCore.QSize(32, 32))
        self.pb_circle.setObjectName("pb_circle")
        self.verticalLayout_2.addWidget(self.pb_circle)
        self.pb_ellipse = QtGui.QPushButton(App_form)
        self.pb_ellipse.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("res/Ellipse.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_ellipse.setIcon(icon5)
        self.pb_ellipse.setIconSize(QtCore.QSize(32, 32))
        self.pb_ellipse.setObjectName("pb_ellipse")
        self.verticalLayout_2.addWidget(self.pb_ellipse)
        self.pb_triangle = QtGui.QPushButton(App_form)
        self.pb_triangle.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("res/Triangle.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_triangle.setIcon(icon6)
        self.pb_triangle.setIconSize(QtCore.QSize(32, 32))
        self.pb_triangle.setObjectName("pb_triangle")
        self.verticalLayout_2.addWidget(self.pb_triangle)
        self.pb_select = QtGui.QPushButton(App_form)
        self.pb_select.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("res/Select.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_select.setIcon(icon7)
        self.pb_select.setIconSize(QtCore.QSize(32, 32))
        self.pb_select.setObjectName("pb_select")
        self.verticalLayout_2.addWidget(self.pb_select)
        self.pb_zoom_in = QtGui.QPushButton(App_form)
        self.pb_zoom_in.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("res/ZoomIn.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_zoom_in.setIcon(icon8)
        self.pb_zoom_in.setIconSize(QtCore.QSize(32, 32))
        self.pb_zoom_in.setObjectName("pb_zoom_in")
        self.verticalLayout_2.addWidget(self.pb_zoom_in)
        self.pb_zoom_out = QtGui.QPushButton(App_form)
        self.pb_zoom_out.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("res/ZoomOut.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_zoom_out.setIcon(icon9)
        self.pb_zoom_out.setIconSize(QtCore.QSize(32, 32))
        self.pb_zoom_out.setObjectName("pb_zoom_out")
        self.verticalLayout_2.addWidget(self.pb_zoom_out)
        self.pb_home = QtGui.QPushButton(App_form)
        self.pb_home.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("res/House.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_home.setIcon(icon10)
        self.pb_home.setIconSize(QtCore.QSize(32, 32))
        self.pb_home.setObjectName("pb_home")
        self.verticalLayout_2.addWidget(self.pb_home)
        self.pb_camera = QtGui.QPushButton(App_form)
        self.pb_camera.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("res/Camera.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_camera.setIcon(icon11)
        self.pb_camera.setIconSize(QtCore.QSize(32, 32))
        self.pb_camera.setObjectName("pb_camera")
        self.verticalLayout_2.addWidget(self.pb_camera)
        spacerItem = QtGui.QSpacerItem(20, 739, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.w_drawWidg = DrawWidget(App_form)
        self.w_drawWidg.setMinimumSize(QtCore.QSize(512, 512))
        self.w_drawWidg.setObjectName("w_drawWidg")
        self.horizontalLayout.addWidget(self.w_drawWidg)

        self.retranslateUi(App_form)
        QtCore.QMetaObject.connectSlotsByName(App_form)

    def retranslateUi(self, App_form):
        App_form.setWindowTitle(QtGui.QApplication.translate("App_form", "Form", None, QtGui.QApplication.UnicodeUTF8))

from view import DrawWidget
