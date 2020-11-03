import services
from dependency_injector.wiring import Provide
from dependency_injection import DependencyInjectionContainer
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import cv2 as cv
import os
import time


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window class.
    """

    MENU_WIDGET_MIN_AND_MAX_WIDTHS = (38, 255)

    def __init__(self):
        """
        Initializes widgets, layouts and styles on the main window.
        """
        super(MainWindow, self).__init__()

        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.menu_widget = QtWidgets.QWidget(self.central_widget)
        self.menu_widget_layout = QtWidgets.QVBoxLayout(self.menu_widget)
        self.menu_push_button = QtWidgets.QPushButton(self.menu_widget)
        self.menu_list_widget = QtWidgets.QListWidget(self.menu_widget)
        self.menu_property_animation = QtCore.QPropertyAnimation(self.menu_widget, b"maximumWidth", self.menu_widget)
        self.widgets_stacked_widget = QtWidgets.QStackedWidget(self.central_widget)

        self.__initialize_window()
        self.__initialize_central_widget()
        self.__initialize_menu_widget()
        self.__initialize_widgets_stacked_widget()

    def __initialize_window(self):
        """
        Sets window parameters and centers it.
        """
        self.setMinimumSize(1280, 720)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowIcon(QtGui.QIcon(":/icons/person_detection"))
        self.setWindowTitle("Person Location Detector")

        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())
        self.move(frame_geometry.topLeft())

    def __initialize_central_widget(self):
        """
        Sets central widget and changes its layout styles.
        """
        self.setCentralWidget(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)

    def __initialize_menu_widget(self):
        """
        Sets menu widget styles, adds it to the central widget layout and adds styled menu items.
        """
        self.menu_widget.setStyleSheet("""
            QWidget {
                background-color: #E5E5E5;
            }""")
        self.menu_widget.setMaximumWidth(self.MENU_WIDGET_MIN_AND_MAX_WIDTHS[0])
        self.central_widget_layout.addWidget(self.menu_widget)

        self.menu_widget_layout.setSpacing(0)
        self.menu_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.menu_push_button.setStyleSheet("""
            QPushButton {
                border: none;
            }
            QPushButton:pressed {
                background-color: #C5C5C5;
            }
            QPushButton:hover:!pressed {
                background-color: #D5D5D5;
            }""")
        self.menu_push_button.setFixedWidth(38)
        self.menu_push_button.setFixedHeight(38)
        self.menu_push_button.setIcon(QtGui.QIcon(":/icons/menu"))
        self.menu_push_button.setIconSize(QtCore.QSize(26, 26))
        self.menu_push_button.setCheckable(True)
        self.menu_push_button.toggled.connect(self.__menu_push_button_on_toggled)
        self.menu_widget_layout.addWidget(self.menu_push_button)

        self.menu_list_widget.setStyleSheet("""
            QListWidget {
                outline: 0px;
            }
            QListWidget::item:selected:active, QListWidget::item:selected:!active {
                background-color: #C5C5C5;
                color: #193852;
            }
            QListWidget::item:hover {
                background-color: #D5D5D5;
            }""")
        self.menu_list_widget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.menu_list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.menu_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.menu_list_widget.setIconSize(QtCore.QSize(32, 32))
        self.menu_list_widget.setFont(QtGui.QFont("Roboto", 14))

        menu_items = [(":/icons/camera", "Detection", DetectionWidget()),
                      (":/icons/neural_network", "Detection models", DetectionModelsWidget()),
                      (":/icons/settings", "Settings", SettingsWidget()),
                      (":/icons/information", "About", AboutWidget())]
        for menu_item_icon, menu_item_name, menu_item_widget in menu_items:
            menu_item = QtWidgets.QListWidgetItem(QtGui.QIcon(menu_item_icon), menu_item_name, self.menu_list_widget)
            menu_item.setSizeHint(QtCore.QSize(16777215, 45))
            self.widgets_stacked_widget.addWidget(menu_item_widget)

        self.menu_list_widget.setCurrentRow(0)
        self.menu_list_widget.currentRowChanged.connect(self.widgets_stacked_widget.setCurrentIndex)
        self.menu_widget_layout.addWidget(self.menu_list_widget)

    def __menu_push_button_on_toggled(self, is_checked):
        """
        Starts expanding or collapsing menu widget animation.

        :param is_checked: whether button is checked
        """
        animation_start_value, animation_end_value = self.MENU_WIDGET_MIN_AND_MAX_WIDTHS if is_checked else reversed(
            self.MENU_WIDGET_MIN_AND_MAX_WIDTHS)

        self.menu_property_animation.setDuration(300)
        self.menu_property_animation.setStartValue(animation_start_value)
        self.menu_property_animation.setEndValue(animation_end_value)
        self.menu_property_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.menu_property_animation.start()

    def __initialize_widgets_stacked_widget(self):
        """
        Adds widgets stacked widget to the central widget layout.
        """
        self.central_widget_layout.addWidget(self.widgets_stacked_widget)


class DetectionWidget(QtWidgets.QWidget):
    def __init__(self,
                 camera_service: services.CameraService = Provide[DependencyInjectionContainer.camera_service_provider],
                 detection_service: services.DetectionService = Provide[
                     DependencyInjectionContainer.detection_service_provider]):
        super(DetectionWidget, self).__init__()

        self.detection_widget_layout = QtWidgets.QGridLayout(self)
        self.detection_widget_layout.setColumnStretch(0, 6)
        self.detection_widget_layout.setColumnStretch(1, 4)

        self.detected_persons_label = QtWidgets.QLabel("Camera is initializing...", self)
        self.detected_persons_label.setFont(QtGui.QFont("Roboto Light", 32))
        self.detected_persons_label.setAlignment(QtCore.Qt.AlignCenter)
        self.detection_widget_layout.addWidget(self.detected_persons_label, 0, 0, 2, 1)

        self.detection_settings_layout = QtWidgets.QVBoxLayout(self)
        self.detection_widget_layout.addLayout(self.detection_settings_layout, 0, 1, 2, 1)
        self.detection_settings_layout.addWidget(QtWidgets.QLabel("Detection settings"))

        self.start_detection_button = QtWidgets.QPushButton("Start detection", self)
        self.start_detection_button.clicked.connect(self.start_detection)
        self.detection_settings_layout.addWidget(self.start_detection_button)

        self.__camera_service = camera_service
        self.__camera_service.start_video_thread(self.update_image)

        self.__detection_service = detection_service

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.detected_persons_label.setPixmap(qt_img.scaled(self.detected_persons_label.width(),
                                                            self.detected_persons_label.height(), QtCore.Qt.KeepAspectRatio))

    @QtCore.pyqtSlot()
    def start_detection(self):
        self.__detection_service.initialize_detection_model(os.path.join("detection_models", "yolov4-tiny.weights"),
                                                            os.path.join("detection_models", "yolov4-tiny.cfg"),
                                                            1.0 / 255, (416, 416))
        self.__camera_service.update_video_callback(self.update_image_with_detected_objects)

    @QtCore.pyqtSlot(np.ndarray)
    def update_image_with_detected_objects(self, cv_img):
        start_detection_time = time.time()
        class_ids, confidences, boxes = self.__detection_service.detect_objects(cv_img, 0.2, 0.4)
        end_detection_time = time.time()

        qt_img = self.convert_cv_qt(cv_img)

        painter = QtGui.QPainter()
        painter.begin(qt_img)
        bounding_box_pen = QtGui.QPen()
        bounding_box_pen.setColor(QtGui.QColor(0, 255, 0))
        bounding_box_pen.setWidth(3)
        painter.setPen(bounding_box_pen)
        location_brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        location_pen = QtGui.QPen()
        location_pen.setColor(QtGui.QColor(0, 0, 255))
        for (class_id, confidence, box) in zip(class_ids, confidences, boxes):
            if class_id == 0:
                painter.setPen(bounding_box_pen)
                painter.drawRect(box[0], box[1], box[2], box[3])
                painter.setBrush(location_brush)
                painter.drawEllipse(QtCore.QPoint((box[0] + box[2]) / 2 + (box[0] / 2), box[1] + box[3]), 5, 5)

                painter.drawText(box[0], box[1] - 10, "Person: %.2f" % confidence)

        painter.drawText(0, 15, "FPS: %.2f" % (1 / (end_detection_time - start_detection_time)))
        painter.end()

        self.detected_persons_label.setPixmap(
            qt_img.scaled(self.detected_persons_label.width(), self.detected_persons_label.height(), QtCore.Qt.KeepAspectRatio))

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QtGui.QPixmap.fromImage(convert_to_Qt_format)


class DetectionModelsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DetectionModelsWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("Detection models widget", self)


class SettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(SettingsWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("Settings widget", self)


class AboutWidget(QtWidgets.QWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("About widget", self)
