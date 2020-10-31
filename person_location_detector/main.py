import sys

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow


def set_app_resources(application):
    from resources import application_resources
    QFontDatabase.addApplicationFont(':/fonts/roboto_light')
    QFontDatabase.addApplicationFont(':/fonts/roboto_regular')
    font = QFont("Roboto Light", 14)
    application.setFont(font)


if __name__ == "__main__":
    application = QApplication(sys.argv)

    set_app_resources(application)

    main_window = MainWindow()
    main_window.show()
    sys.exit(application.exec_())
