import sys

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow


def set_app_resources(app):
    from resources import app_resources
    QFontDatabase.addApplicationFont(':/fonts/roboto-light')
    QFontDatabase.addApplicationFont(':/fonts/roboto-regular')
    font = QFont("Roboto Light", 14)
    app.setFont(font)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    set_app_resources(app)

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
