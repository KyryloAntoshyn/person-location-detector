from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from views.detection_widget import DetectionWidget
from views.detection_models_widget import DetectionModelsWidget
from views.settings_widget import SettingsWidget
from views.about_widget import AboutWidget

STYLE_SHEET = """

QListWidget {
    background-color: #E5E5E5;
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
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(":/icons/person-detection"))

        self.central_widget = QtWidgets.QWidget(self)

        self.horizontal_layout_menu_and_pages = QtWidgets.QHBoxLayout(self.central_widget)

        self.list_widget_menu = QtWidgets.QListWidget(self.central_widget)
        self.stacked_widget_pages = QtWidgets.QStackedWidget(self.central_widget)

        self.init_ui()
        self.setStyleSheet(STYLE_SHEET)

    def init_ui(self):
        self.setObjectName("main_window")
        self.resize(800, 600)

        self.setWindowTitle("Person Location Detector")

        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame_geometry.topLeft())

        self.central_widget.setObjectName("central_widget")

        self.horizontal_layout_menu_and_pages.setObjectName("horizontal_layout_menu_and_pages")
        self.horizontal_layout_menu_and_pages.setSpacing(0)
        self.horizontal_layout_menu_and_pages.setContentsMargins(0, 0, 0, 0)

        self.list_widget_menu.setObjectName("list_widget_menu")
        self.list_widget_menu.currentRowChanged.connect(self.stacked_widget_pages.setCurrentIndex)
        self.list_widget_menu.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.list_widget_menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget_menu.setMinimumWidth(255)
        self.list_widget_menu.setMaximumWidth(255)

        self.list_widget_menu.setFont(QFont("Roboto", 14))
        self.list_widget_menu.setIconSize(QSize(32, 32))

        list_items = [("Detection", DetectionWidget(), ":/icons/camera"),
                      ("Detection models", DetectionModelsWidget(), ":/icons/neural-network"),
                      ("Settings", SettingsWidget(), ":/icons/settings"),
                      ("About", AboutWidget(), ":/icons/information")]
        for menu_item_name, widget, icon in list_items:
            item = QtWidgets.QListWidgetItem(QIcon(icon), menu_item_name)
            item.setSizeHint(QSize(16777215, 45))
            self.list_widget_menu.addItem(item)

            self.stacked_widget_pages.addWidget(widget)

        self.list_widget_menu.setCurrentRow(0)

        self.horizontal_layout_menu_and_pages.addWidget(self.list_widget_menu)

        self.stacked_widget_pages.setObjectName("stacked_widget_pages")
        # ADD PAGES

        self.horizontal_layout_menu_and_pages.addWidget(self.stacked_widget_pages)

        self.setCentralWidget(self.central_widget)
