from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from views.detection_widget import DetectionWidget
from views.detection_models_widget import DetectionModelsWidget
from views.settings_widget import SettingsWidget
from views.about_widget import AboutWidget

STYLE_SHEET = """
QListWidget {
    outline: 0px;
}

QListWidget::item:selected:active, QListWidget::item:selected:!active {
    background-color: #C5C5C5;
    color: #193852;
}

QListWidget::item:hover {
    background-color: #D5D5D5;
}
"""


class MainWindow(QMainWindow):
    SIDE_MENU_TOGGLED_WIDTH = 255
    SIDE_MENU_DEFAULT_WIDTH = 38

    def __init__(self):
        super().__init__()

        self.frame_side_menu = QtWidgets.QFrame()
        self.animation = QPropertyAnimation(self.frame_side_menu, b"maximumWidth")
        self.push_button_hamburger = QtWidgets.QPushButton()
        self.vertical_layout_side_menu = QtWidgets.QVBoxLayout()
        self.setWindowIcon(QIcon(":/icons/person_detection"))
        self.setWindowState(Qt.WindowMaximized)

        self.central_widget = QtWidgets.QWidget(self)

        self.horizontal_layout_menu_and_pages = QtWidgets.QHBoxLayout(self.central_widget)

        self.list_widget_menu = QtWidgets.QListWidget(self.central_widget)
        self.stacked_widget_pages = QtWidgets.QStackedWidget(self.central_widget)

        self.init_ui()
        self.setStyleSheet(STYLE_SHEET)

    def init_ui(self):
        self.setObjectName("main_window")
        self.setMinimumSize(1280, 720)

        self.setWindowTitle("Person Location Detector")

        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame_geometry.topLeft())

        self.central_widget.setObjectName("central_widget")

        self.horizontal_layout_menu_and_pages.setObjectName("horizontal_layout_menu_and_pages")
        self.horizontal_layout_menu_and_pages.setSpacing(0)
        self.horizontal_layout_menu_and_pages.setContentsMargins(0, 0, 0, 0)

        self.vertical_layout_side_menu.setSpacing(0)
        self.vertical_layout_side_menu.setContentsMargins(0, 0, 0, 0)

        self.push_button_hamburger.setFixedWidth(38)
        self.push_button_hamburger.setFixedHeight(38)
        self.push_button_hamburger.setIcon(QIcon(":/icons/hamburger"))
        self.push_button_hamburger.setIconSize(QSize(32, 32))
        self.push_button_hamburger.setCheckable(True)
        self.push_button_hamburger.setChecked(True)
        self.push_button_hamburger.toggled.connect(self.toggle_side_menu)
        self.push_button_hamburger.setStyleSheet("""
        QPushButton {
            border: none;
        }
        
        QPushButton:pressed {
            background-color: #C5C5C5;
        }
        
        QPushButton:hover:!pressed {
        background-color: #D5D5D5;
        } 
        """)

        self.vertical_layout_side_menu.addWidget(self.push_button_hamburger)

        self.list_widget_menu.setObjectName("list_widget_menu")
        self.list_widget_menu.currentRowChanged.connect(self.stacked_widget_pages.setCurrentIndex)
        self.list_widget_menu.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.list_widget_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.list_widget_menu.setFont(QFont("Roboto", 14))
        self.list_widget_menu.setIconSize(QSize(32, 32))

        menu_items = [("Detection", ":/icons/camera", DetectionWidget()),
                      ("Detection models", ":/icons/neural_network", DetectionModelsWidget()),
                      ("Settings", ":/icons/settings", SettingsWidget()),
                      ("About", ":/icons/information", AboutWidget())]
        for menu_item_name, menu_item_icon, menu_item_widget in menu_items:
            item = QtWidgets.QListWidgetItem(QIcon(menu_item_icon), menu_item_name)
            item.setSizeHint(QSize(16777215, 45))
            self.list_widget_menu.addItem(item)
            self.stacked_widget_pages.addWidget(menu_item_widget)

        self.list_widget_menu.setCurrentRow(0)

        self.vertical_layout_side_menu.addWidget(self.list_widget_menu)

        self.frame_side_menu.setMaximumWidth(self.SIDE_MENU_TOGGLED_WIDTH)
        self.frame_side_menu.setStyleSheet("background-color: #E5E5E5;")
        self.frame_side_menu.setLayout(self.vertical_layout_side_menu)

        self.horizontal_layout_menu_and_pages.addWidget(self.frame_side_menu)

        self.stacked_widget_pages.setObjectName("stacked_widget_pages")

        self.horizontal_layout_menu_and_pages.addWidget(self.stacked_widget_pages)

        self.setCentralWidget(self.central_widget)

    def toggle_side_menu(self, is_checked):
        (animation_start_value, animation_end_value) = (
            self.SIDE_MENU_DEFAULT_WIDTH, self.SIDE_MENU_TOGGLED_WIDTH) if is_checked else (
            self.SIDE_MENU_TOGGLED_WIDTH, self.SIDE_MENU_DEFAULT_WIDTH)

        self.animation.setDuration(300)
        self.animation.setStartValue(animation_start_value)
        self.animation.setEndValue(animation_end_value)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
