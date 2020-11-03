import services
from dependency_injector.wiring import Provide
from dependency_injection import DependencyInjectionContainer
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import cv2 as cv


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


class VideoThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self):
        super(VideoThread, self).__init__()
        self._run_flag = True

    def run(self):
        cap = cv.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class DetectionWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DetectionWidget, self).__init__()

        self.detection_widget_layout = QtWidgets.QGridLayout(self)
        self.detection_widget_layout.setColumnStretch(0, 7)
        self.detection_widget_layout.setColumnStretch(1, 3)

        self.detected_persons_label = QtWidgets.QLabel(self)
        self.detection_widget_layout.addWidget(self.detected_persons_label, 0, 0, 2, 1)

        self.detection_settings_layout = QtWidgets.QVBoxLayout(self)
        self.detection_widget_layout.addLayout(self.detection_settings_layout, 0, 1, 2, 1)
        self.detection_settings_layout.addWidget(QtWidgets.QLabel("Detection settings"))

        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.detected_persons_label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.display_width, self.display_height, QtCore.Qt.KeepAspectRatio)
        p = convert_to_Qt_format.scaled(self.detected_persons_label.width(), self.detected_persons_label.height(),
                                        QtCore.Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)


class DetectionModelsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DetectionModelsWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("Detection models widget", self)


class SettingsWidget(QtWidgets.QWidget):
    def __init__(self,
                 service: services.SettingsService = Provide[DependencyInjectionContainer.settings_service_provider]):
        super(SettingsWidget, self).__init__()
        self.init_ui()

        service.hello()

    def init_ui(self):
        lbl = QtWidgets.QLabel("Settings widget", self)


class AboutWidget(QtWidgets.QWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("About widget", self)
