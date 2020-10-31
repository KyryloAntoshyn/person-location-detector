import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
from views.main_window import MainWindow


def initialize_application_resources_and_styles(application):
    """
    Initializes application resources and styles (fonts, etc.).

    :param application: application object
    """
    from resources import application_resources
    QFontDatabase.addApplicationFont(":/fonts/roboto_light")
    QFontDatabase.addApplicationFont(":/fonts/roboto_regular")
    application.setFont(QFont("Roboto Light", 14))


def main():
    """
    Initializes application and its resources. Creates and shows main window. Starts application event loop.

    :return: None
    """
    application = QApplication(sys.argv)
    initialize_application_resources_and_styles(application)

    main_window = MainWindow()
    main_window.show()

    sys.exit(application.exec_())


if __name__ == "__main__":
    main()
