import services
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import os
import helpers
import constants


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

        self.__camera_service = services.CameraService()
        self.__person_location_detection_service = services.PersonLocationDetectionService()

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

        self.setWindowIcon(QtGui.QIcon(":/icons/application_logo"))
        self.setWindowTitle(constants.APPLICATION_NAME)

        self.setStyleSheet("QMainWindow { background-color: #EEEEEE; }")

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

        menu_items = [(":/icons/camera", "Detection",
                       DetectionWidget(self.__camera_service, self.__person_location_detection_service)),
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

        self.menu_property_animation.stop()
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
            if self.__camera_service.is_camera_stream_reading_running():
                self.__camera_service.stop_camera_stream_reading()
            if self.__person_location_detection_service.is_person_location_detection_running():
                self.__person_location_detection_service.stop_person_location_detection()
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
        self.__projection_area_polygon = QtGui.QPolygon()

    def get_projection_area_polygon(self):
        return self.__projection_area_polygon

    def mousePressEvent(self, event):
        if self.__is_setting_projection_area:
            if self.__projection_area_polygon.count() < self.PROJECTION_AREA_POINTS_MAX_COUNT:
                self.__projection_area_polygon << event.pos()
                self.update()

                if self.__projection_area_polygon.count() == self.PROJECTION_AREA_POINTS_MAX_COUNT:
                    self.__is_setting_projection_area = False
                    self.projection_area_set.emit()

    def paintEvent(self, event):
        if self.__is_clearing_projection_area:
            QtGui.QPainter(self).eraseRect(event.rect())
            return

        projection_area_points_count = self.__projection_area_polygon.count()
        if projection_area_points_count == 0:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 229, 255), 5))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 229, 255)))

        current_projection_area_point = self.__projection_area_polygon.point(0)
        painter.drawEllipse(current_projection_area_point, 5, 5)

        if projection_area_points_count > 1:
            for i in range(1, projection_area_points_count):
                next_projection_area_point = self.__projection_area_polygon.point(i)
                painter.drawEllipse(next_projection_area_point, 5, 5)
                painter.drawLine(current_projection_area_point, next_projection_area_point)
                current_projection_area_point = next_projection_area_point

            if projection_area_points_count == self.PROJECTION_AREA_POINTS_MAX_COUNT:
                painter.drawLine(current_projection_area_point, self.__projection_area_polygon.point(0))

    def set_projection_area(self):
        self.__is_setting_projection_area = True

    def clear_projection_area(self):
        self.__is_setting_projection_area = False
        self.__is_clearing_projection_area = True
        self.__projection_area_polygon.clear()
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

    def __init__(self, camera_service, person_location_detection_service):
        super(DetectionWidget, self).__init__()

        self.__camera_service = camera_service
        self.__person_location_detection_service = person_location_detection_service

        self.detection_widget_layout = QtWidgets.QGridLayout(self)
        self.detection_widget_layout.setRowStretch(0, 1)
        self.detection_widget_layout.setRowStretch(1, 1)
        self.detection_widget_layout.setColumnStretch(0, 6)
        self.detection_widget_layout.setColumnStretch(1, 4)

        # Camera stream widgets
        self.camera_stream_widgets_layout = QtWidgets.QGridLayout(self)
        self.camera_stream_widgets_layout.setSpacing(0)
        self.camera_stream_widgets_layout.setRowStretch(0, 0)
        self.camera_stream_widgets_layout.setRowStretch(1, 1)

        self.camera_stream_label = QtWidgets.QLabel("Camera stream", self)
        self.camera_stream_widgets_layout.addWidget(self.camera_stream_label, 0, 0, alignment=QtCore.Qt.AlignHCenter)

        self.projection_area_camera_stream_label = QtWidgets.QLabel(self)
        self.projection_area_camera_stream_label.setFont(QtGui.QFont("Roboto", 28))
        self.projection_area_camera_stream_label.setAlignment(QtCore.Qt.AlignCenter)
        self.projection_area_camera_stream_label.hide()
        self.camera_stream_widgets_layout.addWidget(self.projection_area_camera_stream_label, 1, 0)

        self.projection_area_widget = ProjectionAreaWidget(self)
        self.projection_area_widget.hide()
        self.projection_area_widget.projection_area_set.connect(self.projection_area_set)
        self.camera_stream_widgets_layout.addWidget(self.projection_area_widget, 1, 0, alignment=QtCore.Qt.AlignHCenter)

        self.detection_widget_layout.addLayout(self.camera_stream_widgets_layout, 0, 0, 1, 1)

        # Location of detected persons widgets
        self.location_of_detected_persons_widgets_layout = QtWidgets.QVBoxLayout(self)
        self.location_of_detected_persons_widgets_layout.setSpacing(0)
        self.detection_widget_layout.addLayout(self.location_of_detected_persons_widgets_layout, 1, 0, 1, 1)

        self.location_of_detected_persons_text_label = QtWidgets.QLabel("Location of detected persons", self)
        self.location_of_detected_persons_widgets_layout.addWidget(self.location_of_detected_persons_text_label,
                                                                   alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        self.location_of_detected_persons_label = QtWidgets.QLabel(self)
        self.location_of_detected_persons_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.location_of_detected_persons_widgets_layout.addWidget(self.location_of_detected_persons_label, stretch=1)

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

        self.detection_model_weights_widgets_layout = QtWidgets.QHBoxLayout(self.detection_settings_group_box)
        self.select_detection_model_weights_file_line_edit = QtWidgets.QLineEdit(self.detection_settings_group_box)
        self.select_detection_model_weights_file_line_edit.setReadOnly(True)
        self.detection_model_weights_widgets_layout.addWidget(self.select_detection_model_weights_file_line_edit)

        self.select_detection_model_weights_file_push_button = QtWidgets.QPushButton("Select",
                                                                                     self.detection_settings_group_box)
        self.select_detection_model_weights_file_push_button.setFixedWidth(100)
        self.select_detection_model_weights_file_push_button.clicked.connect(
            self.select_detection_model_weights_or_configuration)
        self.detection_model_weights_widgets_layout.addWidget(self.select_detection_model_weights_file_push_button)

        self.detection_settings_group_box_layout.addRow("Detection model weights",
                                                        self.detection_model_weights_widgets_layout)

        self.detection_model_configuration_widgets_layout = QtWidgets.QHBoxLayout(self.detection_settings_group_box)
        self.select_detection_model_configuration_file_line_edit = QtWidgets.QLineEdit(
            self.detection_settings_group_box)
        self.select_detection_model_configuration_file_line_edit.setReadOnly(True)
        self.detection_model_configuration_widgets_layout.addWidget(
            self.select_detection_model_configuration_file_line_edit)

        self.select_detection_model_configuration_file_push_button = QtWidgets.QPushButton("Select",
                                                                                           self.detection_settings_group_box)
        self.select_detection_model_configuration_file_push_button.setFixedWidth(100)
        self.select_detection_model_configuration_file_push_button.clicked.connect(
            self.select_detection_model_weights_or_configuration)
        self.detection_model_configuration_widgets_layout.addWidget(
            self.select_detection_model_configuration_file_push_button)

        self.detection_settings_group_box_layout.addRow("Detection model configuration",
                                                        self.detection_model_configuration_widgets_layout)

        # Person class ID
        self.person_class_id_spin_box = QtWidgets.QSpinBox(self.detection_settings_group_box)
        self.person_class_id_spin_box.setMinimum(0)
        self.person_class_id_spin_box.setMaximum(99)
        self.detection_settings_group_box_layout.addRow("Person class ID", self.person_class_id_spin_box)

        self.confidence_threshold_slider_layout = QtWidgets.QHBoxLayout(self.detection_settings_group_box)

        self.confidence_threshold_label = QtWidgets.QLabel("0.5", self.detection_settings_group_box)
        self.confidence_threshold_label.setFixedWidth(40)
        self.confidence_threshold_slider_layout.addWidget(self.confidence_threshold_label)

        self.confidence_threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.detection_settings_group_box)
        self.confidence_threshold_slider.setMinimum(10)
        self.confidence_threshold_slider.setMaximum(90)
        self.confidence_threshold_slider.setValue(50)
        self.confidence_threshold_slider.valueChanged.connect(self.slider_value_changed)
        self.confidence_threshold_slider_layout.addWidget(self.confidence_threshold_slider)

        self.detection_settings_group_box_layout.addRow("Confidence threshold", self.confidence_threshold_slider_layout)

        self.nms_threshold_slider_layout = QtWidgets.QHBoxLayout(self.detection_settings_group_box)

        self.nms_threshold_label = QtWidgets.QLabel("0.4", self.detection_settings_group_box)
        self.nms_threshold_label.setFixedWidth(40)
        self.nms_threshold_slider_layout.addWidget(self.nms_threshold_label)

        self.nms_threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.detection_settings_group_box)
        self.nms_threshold_slider.setMinimum(10)
        self.nms_threshold_slider.setMaximum(90)
        self.nms_threshold_slider.setValue(40)
        self.nms_threshold_slider.valueChanged.connect(self.slider_value_changed)
        self.nms_threshold_slider_layout.addWidget(self.nms_threshold_slider)

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

        self.camera_frame_resolution = None
        self.selected_projection_area_resolution = None

        # Detected persons painter
        self.detected_persons_painter = QtGui.QPainter()
        self.detected_persons_pen = QtGui.QPen(QtGui.QColor(118, 255, 3), 10)
        self.detected_persons_painter_fps_font = QtGui.QFont("Roboto", 54)
        self.detected_persons_painter_font = QtGui.QFont("Roboto", 32)

        # Detected persons locations
        self.detected_persons_locations_painter = QtGui.QPainter()
        self.detected_persons_locations_brush = QtGui.QBrush(QtGui.QColor(118, 255, 3))
        self.detected_persons_locations_ellipse_size = 50

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

            # Start camera stream reading
            camera_index = self.camera_indexes_combo_box.currentIndex()
            camera_resolution = self.CAMERA_RESOLUTIONS.get(self.camera_resolutions_combo_box.currentText(), None)
            if camera_resolution is None:
                camera_resolution = (self.camera_width_spin_box.value(), self.camera_height_spin_box.value())
            self.__camera_service.start_camera_stream_reading(camera_index, camera_resolution, self.camera_initialized,
                                                              self.update_first_frame)
        else:
            self.camera_settings_and_stream_initial_state()
            self.change_projection_area_settings_widgets_state(False)
            self.change_detection_settings_widgets_state(False)
            self.projection_area_widget.clear_projection_area()
            self.projection_area_widget.hide()

            # Stop camera stream reading
            self.__camera_service.stop_camera_stream_reading()

    @QtCore.pyqtSlot(bool)
    def camera_initialized(self, is_successful):
        if is_successful:
            self.stop_camera_stream_push_button.setEnabled(True)
            self.change_projection_area_settings_widgets_state(True)
        else:
            # Cleans camera stream reading resources
            self.__camera_service.clean_camera_stream_reading_resources()

            self.camera_settings_and_stream_initial_state()
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "An error occurred during camera initialization!"
                                           "Probably there is no connected camera with such index.")

    @QtCore.pyqtSlot(np.ndarray)
    def update_first_frame(self, camera_frame):
        self.projection_area_camera_stream_label.setPixmap(
            helpers.convert_opencv_image_to_pixmap(camera_frame).scaled(self.projection_area_camera_stream_label.size(),
                                                                        QtCore.Qt.KeepAspectRatio))

        # Change projection area widget size
        self.projection_area_widget.setFixedSize(self.projection_area_camera_stream_label.pixmap().size())
        self.projection_area_widget.show()

        self.camera_frame_resolution = (camera_frame.shape[1], camera_frame.shape[0])  # Save actual camera resolution

        self.__camera_service.update_camera_frame_read_slot(self.update_first_frame,
                                                            self.camera_frame_read)  # Change camera stream reading slot

    @QtCore.pyqtSlot(np.ndarray)
    def camera_frame_read(self, camera_frame):
        self.projection_area_camera_stream_label.setPixmap(
            helpers.convert_opencv_image_to_pixmap(camera_frame).scaled(self.projection_area_camera_stream_label.size(),
                                                                        QtCore.Qt.KeepAspectRatio))

    def camera_settings_and_stream_initial_state(self):
        self.camera_indexes_combo_box.setEnabled(True)
        self.camera_resolutions_combo_box.setEnabled(True)
        if self.camera_resolutions_combo_box.currentText() not in self.CAMERA_RESOLUTIONS:
            self.camera_width_spin_box.setEnabled(True)
            self.camera_height_spin_box.setEnabled(True)
        self.start_camera_stream_push_button.setEnabled(True)
        self.stop_camera_stream_push_button.setEnabled(False)
        self.projection_area_camera_stream_label.hide()

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

    @QtCore.pyqtSlot()
    def projection_area_set(self):
        self.change_detection_settings_widgets_state(True)

        if self.select_detection_model_weights_file_line_edit.text() == "" or \
                self.select_detection_model_configuration_file_line_edit.text() == "":
            self.start_detection_push_button.setEnabled(False)

        self.stop_detection_push_button.setEnabled(False)

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
        self.select_detection_model_weights_file_push_button.setEnabled(is_enabled)
        self.select_detection_model_weights_file_line_edit.setEnabled(is_enabled)
        self.select_detection_model_configuration_file_push_button.setEnabled(is_enabled)
        self.select_detection_model_configuration_file_line_edit.setEnabled(is_enabled)
        self.person_class_id_spin_box.setEnabled(is_enabled)
        self.confidence_threshold_slider.setEnabled(is_enabled)
        self.confidence_threshold_label.setEnabled(is_enabled)
        self.nms_threshold_slider.setEnabled(is_enabled)
        self.nms_threshold_label.setEnabled(is_enabled)
        self.start_detection_push_button.setEnabled(is_enabled)
        self.stop_detection_push_button.setEnabled(is_enabled)

    @QtCore.pyqtSlot()
    def select_detection_model_weights_or_configuration(self):
        if self.sender() == self.select_detection_model_weights_file_push_button:
            weights_file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select detection model weights file",
                                                                      os.path.join(
                                                                          os.path.dirname(os.path.abspath(__file__)),
                                                                          "detection_models"), "Weights (*.weights)")[0]
            if weights_file_path != "":
                self.select_detection_model_weights_file_line_edit.setText(weights_file_path)

                if self.select_detection_model_configuration_file_line_edit.text() != "":
                    self.start_detection_push_button.setEnabled(True)
        else:
            configuration_file_path = \
                QtWidgets.QFileDialog.getOpenFileName(self, "Select detection model configuration file",
                                                      os.path.join(
                                                          os.path.dirname(os.path.abspath(__file__)),
                                                          "detection_models"), "Configuration (*.cfg)")[0]
            if configuration_file_path != "":
                self.select_detection_model_configuration_file_line_edit.setText(configuration_file_path)

                if self.select_detection_model_weights_file_line_edit.text() != "":
                    self.start_detection_push_button.setEnabled(True)

    @QtCore.pyqtSlot(int)
    def slider_value_changed(self, value):
        if self.sender() == self.confidence_threshold_slider:
            updated_confidence_threshold = value * 0.01
            if self.__person_location_detection_service.is_person_location_detection_running():
                self.__person_location_detection_service.update_detection_model_confidence_threshold(
                    updated_confidence_threshold)
            self.confidence_threshold_label.setText(str(round(updated_confidence_threshold, 2)))
        else:
            updated_nms_threshold = value * 0.01
            if self.__person_location_detection_service.is_person_location_detection_running():
                self.__person_location_detection_service.update_detection_model_nms_threshold(updated_nms_threshold)
            self.nms_threshold_label.setText(str(round(updated_nms_threshold, 2)))

    @QtCore.pyqtSlot()
    def start_detection(self):
        # Get projection area resolution
        self.selected_projection_area_resolution = self.PROJECTION_AREA_RESOLUTIONS.get(
            self.projection_area_resolutions_combo_box.currentText(), None)
        if self.selected_projection_area_resolution is None:
            self.selected_projection_area_resolution = self.projection_area_width_spin_box.value(), \
                                                       self.projection_area_height_spin_box.value()

        # Set detections drawing parameters based on camera and projection area resolutions
        self.set_detections_drawing_parameters()

        # Get projection area coordinates
        projection_area_polygon_coordinates = helpers.convert_polygon_points_to_coordinates_list(
            self.projection_area_widget.get_projection_area_polygon())
        current_resolution = self.projection_area_camera_stream_label.pixmap().width(), self.projection_area_camera_stream_label.pixmap().height()
        projection_area_coordinates = helpers.convert_points_to_another_resolution(projection_area_polygon_coordinates,
                                                                                   current_resolution,
                                                                                   self.camera_frame_resolution)

        # Start person location detection
        self.__camera_service.disconnect_camera_frame_read_slot(self.camera_frame_read)
        self.__person_location_detection_service.start_person_location_detection(
            self.select_detection_model_weights_file_line_edit.text(),
            self.select_detection_model_configuration_file_line_edit.text(),
            1.0 / 255, (416, 416),  # Hardcoded for now
            self.person_class_id_spin_box.value(),
            self.confidence_threshold_slider.value() * 0.01,
            self.nms_threshold_slider.value() * 0.01,
            projection_area_coordinates,
            self.selected_projection_area_resolution,
            self.camera_frame_processed)
        self.__camera_service.switch_camera_stream_reading_state(
            True, self.__person_location_detection_service.camera_frames_to_process)

        # Update UI
        self.start_detection_push_button.setEnabled(False)
        self.stop_detection_push_button.setEnabled(True)
        self.change_camera_and_projection_area_settings_group_boxes_state(False)
        self.location_of_detected_persons_label.show()

    def set_detections_drawing_parameters(self):
        self.detected_persons_pen.setWidth(self.camera_frame_resolution[0] * 10 / 1920)
        self.detected_persons_painter_fps_font.setPointSize(self.camera_frame_resolution[0] * 54 / 1920)
        self.detected_persons_painter_font.setPointSize(self.camera_frame_resolution[0] * 32 / 1920)
        self.detected_persons_locations_ellipse_size = self.selected_projection_area_resolution[0] * 50 / 1920

    @QtCore.pyqtSlot(tuple)
    def camera_frame_processed(self, results):
        camera_frame, camera_frame_warped, fps_number, confidences, bounding_boxes, persons_locations = results

        # Draw detected persons
        camera_frame_pixmap = helpers.convert_opencv_image_to_pixmap(camera_frame)

        self.detected_persons_painter.begin(camera_frame_pixmap)
        self.detected_persons_painter.setPen(self.detected_persons_pen)
        self.detected_persons_painter.setFont(self.detected_persons_painter_fps_font)
        self.detected_persons_painter.drawText(0, self.detected_persons_painter_fps_font.pointSize(),
                                               "FPS: %d" % fps_number)
        self.detected_persons_painter.setFont(self.detected_persons_painter_font)
        for (confidence, bounding_box) in zip(confidences, bounding_boxes):
            self.detected_persons_painter.drawText(bounding_box[0],
                                                   bounding_box[1] - self.detected_persons_painter_font.pointSize(),
                                                   "Person: %.2f" % confidence)
            self.detected_persons_painter.drawRect(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])
        self.detected_persons_painter.end()

        self.projection_area_camera_stream_label.setPixmap(
            camera_frame_pixmap.scaled(
                self.projection_area_camera_stream_label.size(), QtCore.Qt.KeepAspectRatio))

        # Draw location of detected persons
        camera_frame_warped_pixmap = helpers.convert_opencv_image_to_pixmap(camera_frame_warped)

        self.detected_persons_locations_painter.begin(camera_frame_warped_pixmap)
        self.detected_persons_locations_painter.setBrush(self.detected_persons_locations_brush)
        for person_location in persons_locations:
            self.detected_persons_locations_painter.drawEllipse(person_location[0],
                                                                person_location[1],
                                                                self.detected_persons_locations_ellipse_size,
                                                                self.detected_persons_locations_ellipse_size)
        self.detected_persons_locations_painter.end()

        self.location_of_detected_persons_label.setPixmap(
            camera_frame_warped_pixmap.scaled(
                self.location_of_detected_persons_label.size(), QtCore.Qt.KeepAspectRatio))

    @QtCore.pyqtSlot()
    def stop_detection(self):
        # Stop person location detection
        self.__camera_service.switch_camera_stream_reading_state(False)
        self.__person_location_detection_service.stop_person_location_detection()
        self.__camera_service.connect_camera_frame_read_slot(self.camera_frame_read)

        self.stop_detection_push_button.setEnabled(False)
        self.start_detection_push_button.setEnabled(True)
        self.change_camera_and_projection_area_settings_group_boxes_state(True)
        self.location_of_detected_persons_label.hide()

    def change_camera_and_projection_area_settings_group_boxes_state(self, is_enabled):
        self.camera_settings_group_box.setEnabled(is_enabled)
        self.projection_area_settings_group_box.setEnabled(is_enabled)
        self.select_detection_model_weights_file_push_button.setEnabled(is_enabled)
        self.select_detection_model_weights_file_line_edit.setEnabled(is_enabled)
        self.select_detection_model_configuration_file_push_button.setEnabled(is_enabled)
        self.select_detection_model_configuration_file_line_edit.setEnabled(is_enabled)
        self.person_class_id_spin_box.setEnabled(is_enabled)


class AboutWidget(QtWidgets.QWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()

        self.about_widget_layout = QtWidgets.QVBoxLayout(self)
        self.about_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.about_widget_layout.setSpacing(0)

        self.application_logo_label = QtWidgets.QLabel(self)
        self.application_logo_label.setPixmap(QtGui.QPixmap(":/icons/application_logo"))
        self.about_widget_layout.addWidget(self.application_logo_label, alignment=QtCore.Qt.AlignHCenter)

        self.person_location_detector_label = QtWidgets.QLabel("<strong>Person Location Detector</strong>", self)
        self.person_location_detector_label.setFont(QtGui.QFont("Roboto", 24))
        self.about_widget_layout.addWidget(self.person_location_detector_label, alignment=QtCore.Qt.AlignHCenter)

        self.developed_by_label = QtWidgets.QLabel("Developed by", self)
        self.developed_by_label.setFont(QtGui.QFont("Roboto", 18))
        self.developed_by_label.setStyleSheet("margin-top: 30px;")
        self.about_widget_layout.addWidget(self.developed_by_label, alignment=QtCore.Qt.AlignHCenter)

        self.kyrylo_antoshyn_label = QtWidgets.QLabel("<strong>Kyrylo Antoshyn</strong>", self)
        self.kyrylo_antoshyn_label.setFont(QtGui.QFont("Roboto", 18))

        self.about_widget_layout.addWidget(self.kyrylo_antoshyn_label, alignment=QtCore.Qt.AlignHCenter)
