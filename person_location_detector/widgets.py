import services
from dependency_injector.wiring import Provide
from dependency_injection import DependencyInjectionContainer
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import os
import time
import helpers
import constants


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window class.
    """

    MENU_WIDGET_MIN_AND_MAX_WIDTHS = (38, 255)

    def __init__(self,
                 camera_service: services.CameraService = Provide[
                     DependencyInjectionContainer.camera_service_provider]):
        """
        Initializes widgets, layouts and styles on the main window.
        """
        super(MainWindow, self).__init__()

        self.__camera_service = camera_service

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
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setFixedSize(QtWidgets.QApplication.primaryScreen().availableGeometry().size())

        self.setWindowIcon(QtGui.QIcon(":/icons/person_detection"))
        self.setWindowTitle(constants.APPLICATION_NAME)

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
                outline: 0px;
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

    def closeEvent(self, event):
        """
        Asks user for exit and cleans up application resources.

        :param event: close event
        """
        exit_question_result = QtWidgets.QMessageBox.question(self, constants.APPLICATION_NAME,
                                                              "Are you sure you want to exit?",
                                                              QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                                                              QtWidgets.QMessageBox.No)
        if exit_question_result == QtWidgets.QMessageBox.Yes:
            if self.__camera_service.is_camera_stream_reading_active():
                self.__camera_service.stop_camera_stream_reading()
            event.accept()
        else:
            event.ignore()


class ProjectionAreaWidget(QtWidgets.QWidget):
    PROJECTION_AREA_POINTS_MAX_COUNT = 4
    projection_area_set = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ProjectionAreaWidget, self).__init__(parent=parent)

        self.__is_setting_projection_area = False
        self.__is_clearing_projection_area = False
        self.__projection_area_points = QtGui.QPolygon()

    def mousePressEvent(self, event):
        if self.__is_setting_projection_area:
            if self.__projection_area_points.count() < self.PROJECTION_AREA_POINTS_MAX_COUNT:
                self.__projection_area_points << event.pos()
                self.update()

                if self.__projection_area_points.count() == self.PROJECTION_AREA_POINTS_MAX_COUNT:
                    self.__is_setting_projection_area = False
                    self.projection_area_set.emit()

    def paintEvent(self, event):
        if self.__is_clearing_projection_area:
            QtGui.QPainter(self).eraseRect(event.rect())
            return

        projection_area_points_count = self.__projection_area_points.count()
        if projection_area_points_count == 0:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0), 5))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 0)))

        current_projection_area_point = self.__projection_area_points.point(0)
        painter.drawEllipse(current_projection_area_point, 5, 5)

        if projection_area_points_count > 1:
            for i in range(1, projection_area_points_count):
                next_projection_area_point = self.__projection_area_points.point(i)
                painter.drawEllipse(next_projection_area_point, 5, 5)
                painter.drawLine(current_projection_area_point, next_projection_area_point)
                current_projection_area_point = next_projection_area_point

            if projection_area_points_count == self.PROJECTION_AREA_POINTS_MAX_COUNT:
                painter.drawLine(current_projection_area_point, self.__projection_area_points.point(0))

    def set_projection_area(self):
        self.__is_setting_projection_area = True

    def clear_projection_area(self):
        self.__is_setting_projection_area = False
        self.__is_clearing_projection_area = True
        self.__projection_area_points.clear()
        self.update()
        self.__is_clearing_projection_area = False


class DetectionWidget(QtWidgets.QWidget):
    PROJECTION_AREA_RESOLUTIONS = {
        "1920×1080": (1920, 1080),
        "1280×720": (1280, 720),
        "640×480": (640, 480)
    }

    CAMERA_RESOLUTIONS = {
        "1920×1080": (1920, 1080),
        "1280×720": (1280, 720),
        "640×480": (640, 480)
    }

    def __init__(self,
                 camera_service: services.CameraService = Provide[DependencyInjectionContainer.camera_service_provider],
                 detection_service: services.DetectionService = Provide[
                     DependencyInjectionContainer.detection_service_provider]):
        super(DetectionWidget, self).__init__()

        self.__camera_service = camera_service
        self.__detection_service = detection_service

        self.detection_widget_layout = QtWidgets.QGridLayout(self)
        self.detection_widget_layout.setRowStretch(0, 1)
        self.detection_widget_layout.setRowStretch(1, 1)
        self.detection_widget_layout.setColumnStretch(0, 7)
        self.detection_widget_layout.setColumnStretch(1, 3)

        # Camera stream widgets
        self.camera_stream_widgets_layout = QtWidgets.QGridLayout(self)
        self.camera_stream_widgets_layout.setRowStretch(0, 0)
        self.camera_stream_widgets_layout.setRowStretch(1, 1)

        self.camera_stream_label = QtWidgets.QLabel("Camera stream", self)
        self.camera_stream_widgets_layout.addWidget(self.camera_stream_label, 0, 0)

        self.projection_area_camera_stream_label = QtWidgets.QLabel(self)
        self.projection_area_camera_stream_label.setFont(QtGui.QFont("Roboto", 28))
        self.projection_area_camera_stream_label.setAlignment(QtCore.Qt.AlignCenter)
        self.projection_area_camera_stream_label.hide()
        self.camera_stream_widgets_layout.addWidget(self.projection_area_camera_stream_label, 1, 0)

        self.projection_area_widget = None

        self.detection_widget_layout.addLayout(self.camera_stream_widgets_layout, 0, 0, 1, 1)

        # Detection settings widgets
        self.settings_layout = QtWidgets.QVBoxLayout(self)
        self.settings_layout.setSpacing(35)
        self.detection_widget_layout.addLayout(self.settings_layout, 0, 1, 2, 1)

        # Camera
        self.camera_settings_group_box = QtWidgets.QGroupBox("Camera settings", self)
        self.settings_layout.addWidget(self.camera_settings_group_box)
        self.camera_settings_group_box_layout = QtWidgets.QFormLayout(self.camera_settings_group_box)
        self.camera_settings_group_box_layout.setSpacing(15)

        self.camera_indexes_combo_box = QtWidgets.QComboBox(self.camera_settings_group_box)
        self.camera_indexes_combo_box.addItems(["0", "1", "2", "3", "4"])
        self.camera_settings_group_box_layout.addRow("Camera index", self.camera_indexes_combo_box)

        self.camera_resolutions_combo_box = QtWidgets.QComboBox(self.camera_settings_group_box)
        camera_resolutions_list = list(self.CAMERA_RESOLUTIONS.keys())
        camera_resolutions_list.append("Other")
        self.camera_resolutions_combo_box.addItems(camera_resolutions_list)
        self.camera_resolutions_combo_box.currentTextChanged.connect(self.resolutions_combo_box_selection_changed)
        self.camera_settings_group_box_layout.addRow("Camera resolution", self.camera_resolutions_combo_box)

        self.other_camera_resolution_layout = QtWidgets.QGridLayout(self.camera_settings_group_box)

        self.camera_width_spin_box = QtWidgets.QSpinBox(self.camera_settings_group_box)
        self.camera_width_spin_box.setMinimum(640)
        self.camera_width_spin_box.setMaximum(3840)
        self.camera_width_spin_box.setValue(1280)
        self.camera_width_spin_box.setEnabled(False)
        self.other_camera_resolution_layout.addWidget(self.camera_width_spin_box, 0, 0)

        self.camera_height_spin_box = QtWidgets.QSpinBox(self.camera_settings_group_box)
        self.camera_height_spin_box.setMinimum(480)
        self.camera_height_spin_box.setMaximum(2160)
        self.camera_height_spin_box.setValue(720)
        self.camera_height_spin_box.setEnabled(False)
        self.other_camera_resolution_layout.addWidget(self.camera_height_spin_box, 0, 1)

        self.camera_settings_group_box_layout.addRow(self.other_camera_resolution_layout)

        self.start_and_stop_camera_stream_push_buttons_layout = QtWidgets.QGridLayout(self.camera_settings_group_box)

        self.start_camera_stream_push_button = QtWidgets.QPushButton("Start camera stream",
                                                                     self.camera_settings_group_box)
        self.start_camera_stream_push_button.clicked.connect(self.start_or_stop_camera_stream)
        self.start_and_stop_camera_stream_push_buttons_layout.addWidget(self.start_camera_stream_push_button, 0, 0)

        self.stop_camera_stream_push_button = QtWidgets.QPushButton("Stop camera stream",
                                                                    self.camera_settings_group_box)
        self.stop_camera_stream_push_button.setEnabled(False)
        self.stop_camera_stream_push_button.clicked.connect(self.start_or_stop_camera_stream)
        self.start_and_stop_camera_stream_push_buttons_layout.addWidget(self.stop_camera_stream_push_button, 0, 1)

        self.camera_settings_group_box_layout.addRow(self.start_and_stop_camera_stream_push_buttons_layout)

        # Projection area
        self.projection_area_settings_group_box = QtWidgets.QGroupBox("Projection area settings", self)
        self.projection_area_settings_group_box_layout = QtWidgets.QFormLayout(self.projection_area_settings_group_box)
        self.projection_area_settings_group_box_layout.setSpacing(15)
        self.settings_layout.addWidget(self.projection_area_settings_group_box)

        self.set_and_clear_projection_area_push_buttons_layout = QtWidgets.QGridLayout(
            self.projection_area_settings_group_box)

        self.set_projection_area_push_button = QtWidgets.QPushButton("Set projection area",
                                                                     self.projection_area_settings_group_box)
        self.set_projection_area_push_button.clicked.connect(self.set_or_clear_projection_area)
        self.set_and_clear_projection_area_push_buttons_layout.addWidget(self.set_projection_area_push_button, 0, 0)

        self.clear_projection_area_push_button = QtWidgets.QPushButton("Clear projection area",
                                                                       self.projection_area_settings_group_box)
        self.clear_projection_area_push_button.clicked.connect(self.set_or_clear_projection_area)
        self.set_and_clear_projection_area_push_buttons_layout.addWidget(self.clear_projection_area_push_button, 0, 1)

        self.projection_area_settings_group_box_layout.addRow(self.set_and_clear_projection_area_push_buttons_layout)

        self.projection_area_resolutions_combo_box = QtWidgets.QComboBox(self.projection_area_settings_group_box)
        projection_resolutions_list = list(self.PROJECTION_AREA_RESOLUTIONS.keys())
        projection_resolutions_list.append("Other")
        self.projection_area_resolutions_combo_box.addItems(projection_resolutions_list)
        self.projection_area_resolutions_combo_box.currentTextChanged.connect(
            self.resolutions_combo_box_selection_changed)
        self.projection_area_settings_group_box_layout.addRow("Projection area resolution",
                                                              self.projection_area_resolutions_combo_box)

        self.other_projection_area_resolution_layout = QtWidgets.QGridLayout(self.projection_area_settings_group_box)

        self.projection_area_width_spin_box = QtWidgets.QSpinBox(self.projection_area_settings_group_box)
        self.projection_area_width_spin_box.setMinimum(640)
        self.projection_area_width_spin_box.setMaximum(3840)
        self.projection_area_width_spin_box.setValue(1280)
        self.projection_area_width_spin_box.setEnabled(False)
        self.other_projection_area_resolution_layout.addWidget(self.projection_area_width_spin_box, 0, 0)

        self.projection_area_height_spin_box = QtWidgets.QSpinBox(self.projection_area_settings_group_box)
        self.projection_area_height_spin_box.setMinimum(480)
        self.projection_area_height_spin_box.setMaximum(2160)
        self.projection_area_height_spin_box.setValue(720)
        self.projection_area_height_spin_box.setEnabled(False)
        self.other_projection_area_resolution_layout.addWidget(self.projection_area_height_spin_box, 0, 1)

        self.projection_area_settings_group_box_layout.addRow(self.other_projection_area_resolution_layout)
        self.change_projection_area_settings_widgets_state(False)

        # Detection
        self.detection_settings_group_box = QtWidgets.QGroupBox("Detection settings", self)
        self.settings_layout.addWidget(self.detection_settings_group_box)
        self.detection_settings_group_box_layout = QtWidgets.QFormLayout(self.detection_settings_group_box)
        self.detection_settings_group_box_layout.setSpacing(15)

        self.detection_models_combo_box = QtWidgets.QComboBox(self.detection_settings_group_box)
        self.detection_models_combo_box.addItems(["YOLOv4"])
        self.detection_settings_group_box_layout.addRow("Detection model", self.detection_models_combo_box)

        self.confidence_threshold_slider_layout = QtWidgets.QHBoxLayout(self.detection_settings_group_box)

        self.confidence_threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.detection_settings_group_box)
        self.confidence_threshold_slider.setMinimum(0)
        self.confidence_threshold_slider.setMaximum(100)
        self.confidence_threshold_slider.setValue(50)
        self.confidence_threshold_slider.valueChanged.connect(self.slider_value_changed)
        self.confidence_threshold_slider_layout.addWidget(self.confidence_threshold_slider)

        self.confidence_threshold_label = QtWidgets.QLabel("0.5", self.detection_settings_group_box)
        self.confidence_threshold_label.setFixedWidth(40)
        self.confidence_threshold_slider_layout.addWidget(self.confidence_threshold_label)

        self.detection_settings_group_box_layout.addRow("Confidence threshold", self.confidence_threshold_slider_layout)

        self.nms_threshold_slider_layout = QtWidgets.QHBoxLayout(self.detection_settings_group_box)

        self.nms_threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.detection_settings_group_box)
        self.nms_threshold_slider.setMinimum(0)
        self.nms_threshold_slider.setMaximum(100)
        self.nms_threshold_slider.setValue(40)
        self.nms_threshold_slider.valueChanged.connect(self.slider_value_changed)
        self.nms_threshold_slider_layout.addWidget(self.nms_threshold_slider)

        self.nms_threshold_label = QtWidgets.QLabel("0.4", self.detection_settings_group_box)
        self.nms_threshold_label.setFixedWidth(40)
        self.nms_threshold_slider_layout.addWidget(self.nms_threshold_label)

        self.detection_settings_group_box_layout.addRow("NMS threshold", self.nms_threshold_slider_layout)

        self.start_and_stop_detection_push_buttons_layout = QtWidgets.QGridLayout(self)

        self.start_detection_push_button = QtWidgets.QPushButton("Start detection",
                                                                 self.detection_settings_group_box)
        self.start_detection_push_button.clicked.connect(self.start_detection)
        self.start_and_stop_detection_push_buttons_layout.addWidget(self.start_detection_push_button, 0, 0)

        self.stop_detection_push_button = QtWidgets.QPushButton("Stop detection",
                                                                self.detection_settings_group_box)
        self.stop_detection_push_button.clicked.connect(self.stop_detection)
        self.start_and_stop_detection_push_buttons_layout.addWidget(self.stop_detection_push_button, 0, 1)

        self.detection_settings_group_box_layout.addRow(self.start_and_stop_detection_push_buttons_layout)
        self.change_detection_settings_widgets_state(False)

        self.settings_layout.addStretch()

    @QtCore.pyqtSlot()
    def start_or_stop_camera_stream(self):
        if self.sender() == self.start_camera_stream_push_button:
            self.camera_indexes_combo_box.setEnabled(False)
            self.camera_resolutions_combo_box.setEnabled(False)
            self.camera_width_spin_box.setEnabled(False)
            self.camera_height_spin_box.setEnabled(False)
            self.start_camera_stream_push_button.setEnabled(False)
            self.projection_area_camera_stream_label.setText("Camera is initializing...")
            self.projection_area_camera_stream_label.show()

            camera_index = self.camera_indexes_combo_box.currentIndex()
            if self.camera_resolutions_combo_box.currentText() in self.CAMERA_RESOLUTIONS:
                camera_resolution = self.CAMERA_RESOLUTIONS[self.camera_resolutions_combo_box.currentText()]
            else:
                camera_resolution = (self.camera_width_spin_box.value(), self.camera_height_spin_box.value())
            self.__camera_service.start_camera_stream_reading(camera_index, camera_resolution, self.camera_initialized,
                                                              self.update_first_frame)
        else:
            self.camera_settings_and_stream_initial_state()
            self.change_projection_area_settings_widgets_state(False)
            self.change_detection_settings_widgets_state(False)
            self.projection_area_widget.clear_projection_area()

            self.__camera_service.stop_camera_stream_reading()

    @QtCore.pyqtSlot(bool)
    def camera_initialized(self, is_successful):
        if is_successful:
            self.stop_camera_stream_push_button.setEnabled(True)
            self.change_projection_area_settings_widgets_state(True)
        else:
            self.__camera_service.stop_camera_stream_reading()
            self.camera_settings_and_stream_initial_state()
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "An error occurred during camera initialization!"
                                           "Probably there is no connected camera with such index.")

    def camera_settings_and_stream_initial_state(self):
        self.camera_indexes_combo_box.setEnabled(True)
        self.camera_resolutions_combo_box.setEnabled(True)
        if self.camera_resolutions_combo_box.currentText() not in self.CAMERA_RESOLUTIONS:
            self.camera_width_spin_box.setEnabled(True)
            self.camera_height_spin_box.setEnabled(True)
        self.start_camera_stream_push_button.setEnabled(True)
        self.stop_camera_stream_push_button.setEnabled(False)
        self.projection_area_camera_stream_label.hide()

    @QtCore.pyqtSlot(np.ndarray)
    def update_first_frame(self, camera_frame):
        self.projection_area_camera_stream_label.setPixmap(
            helpers.convert_opencv_image_to_pixmap(camera_frame).scaled(self.projection_area_camera_stream_label.size(),
                                                                        QtCore.Qt.KeepAspectRatio))

        # Create projection area widget
        self.projection_area_widget = ProjectionAreaWidget(self)
        self.projection_area_widget.setFixedSize(self.projection_area_camera_stream_label.pixmap().size())
        self.projection_area_widget.projection_area_set.connect(self.projection_area_set)
        self.camera_stream_widgets_layout.addWidget(self.projection_area_widget, 1, 0, alignment=QtCore.Qt.AlignHCenter)

        self.__camera_service.update_camera_frame_read_slot(self.camera_frame_read)

    def change_projection_area_settings_widgets_state(self, is_enabled):
        self.set_projection_area_push_button.setEnabled(is_enabled)
        self.clear_projection_area_push_button.setEnabled(is_enabled)
        self.projection_area_resolutions_combo_box.setEnabled(is_enabled)

        if self.projection_area_resolutions_combo_box.currentText() not in self.PROJECTION_AREA_RESOLUTIONS:
            self.projection_area_width_spin_box.setEnabled(is_enabled)
            self.projection_area_height_spin_box.setEnabled(is_enabled)

    @QtCore.pyqtSlot()
    def set_or_clear_projection_area(self):
        if self.sender() == self.set_projection_area_push_button:
            self.set_projection_area_push_button.setEnabled(False)
            self.projection_area_widget.set_projection_area()
        else:
            self.set_projection_area_push_button.setEnabled(True)
            self.change_detection_settings_widgets_state(False)
            self.projection_area_widget.clear_projection_area()

    @QtCore.pyqtSlot(str)
    def resolutions_combo_box_selection_changed(self, current_text):
        if self.sender() == self.projection_area_resolutions_combo_box:
            if current_text in self.PROJECTION_AREA_RESOLUTIONS:
                self.projection_area_width_spin_box.setEnabled(False)
                self.projection_area_height_spin_box.setEnabled(False)
            else:
                self.projection_area_width_spin_box.setEnabled(True)
                self.projection_area_height_spin_box.setEnabled(True)
        else:
            if current_text in self.CAMERA_RESOLUTIONS:
                self.camera_width_spin_box.setEnabled(False)
                self.camera_height_spin_box.setEnabled(False)
            else:
                self.camera_width_spin_box.setEnabled(True)
                self.camera_height_spin_box.setEnabled(True)

    def change_detection_settings_widgets_state(self, is_enabled):
        self.detection_models_combo_box.setEnabled(is_enabled)
        self.confidence_threshold_slider.setEnabled(is_enabled)
        self.confidence_threshold_label.setEnabled(is_enabled)
        self.nms_threshold_slider.setEnabled(is_enabled)
        self.nms_threshold_label.setEnabled(is_enabled)
        self.start_detection_push_button.setEnabled(is_enabled)
        self.stop_detection_push_button.setEnabled(is_enabled)

    @QtCore.pyqtSlot()
    def projection_area_set(self):
        self.change_detection_settings_widgets_state(True)
        self.stop_detection_push_button.setEnabled(False)

    @QtCore.pyqtSlot(np.ndarray)
    def camera_frame_read(self, camera_frame):
        self.projection_area_camera_stream_label.setPixmap(
            helpers.convert_opencv_image_to_pixmap(camera_frame).scaled(self.projection_area_camera_stream_label.size(),
                                                                        QtCore.Qt.KeepAspectRatio))

    @QtCore.pyqtSlot(int)
    def slider_value_changed(self, value):
        if self.sender() == self.confidence_threshold_slider:
            self.confidence_threshold_label.setText(str(round(value * 0.01, 2)))
        else:
            self.nms_threshold_label.setText(str(round(value * 0.01, 2)))

    @QtCore.pyqtSlot()
    def start_detection(self):
        self.__detection_service.initialize_detection_model(os.path.join("detection_models", "yolov4-tiny.weights"),
                                                            os.path.join("detection_models", "yolov4-tiny.cfg"),
                                                            1.0 / 255, (416, 416))
        self.__camera_service.update_camera_frame_read_slot(self.camera_frame_read_extended)
        self.start_detection_push_button.setEnabled(False)
        self.stop_detection_push_button.setEnabled(True)
        self.change_camera_and_projection_area_settings_group_boxes_state(False)

    @QtCore.pyqtSlot()
    def stop_detection(self):
        self.__camera_service.update_camera_frame_read_slot(self.camera_frame_read)
        self.stop_detection_push_button.setEnabled(False)
        self.start_detection_push_button.setEnabled(True)
        self.change_camera_and_projection_area_settings_group_boxes_state(True)

    def change_camera_and_projection_area_settings_group_boxes_state(self, is_enabled):
        self.camera_settings_group_box.setEnabled(is_enabled)
        self.projection_area_settings_group_box.setEnabled(is_enabled)
        self.detection_models_combo_box.setEnabled(is_enabled)

    @QtCore.pyqtSlot(np.ndarray)
    def camera_frame_read_extended(self, camera_frame):
        start_detection_time = time.time()

        class_ids, confidences, boxes = self.__detection_service.detect_objects(camera_frame,
                                                                                self.confidence_threshold_slider.value() * 0.01,
                                                                                self.nms_threshold_slider.value() * 0.01)
        end_detection_time = time.time()

        pixmap = helpers.convert_opencv_image_to_pixmap(camera_frame)

        painter = QtGui.QPainter()
        painter.begin(pixmap)
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

        self.projection_area_camera_stream_label.setPixmap(
            pixmap.scaled(self.projection_area_camera_stream_label.size(),
                          QtCore.Qt.KeepAspectRatio))


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
