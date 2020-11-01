import sys
from PyQt5 import QtWidgets, QtGui
from views.main_window import MainWindow
from resources import application_resources


class ApplicationInitializer:
    """
    Class that is responsible for application initialization.
    """

    def __init__(self):
        """
        Creates application and main window.
        """
        self.application = QtWidgets.QApplication(sys.argv)
        self.main_window = MainWindow()

    def initialize_and_start_application(self):
        """
        Initializes application styles, shows main window and starts application event loop.
        """
        self.__initialize_application_styles()
        self.main_window.show()
        sys.exit(self.application.exec_())

    def __initialize_application_styles(self):
        """
        Initializes application styles (fonts, etc.).
        """
        QtGui.QFontDatabase.addApplicationFont(":/fonts/roboto_light")
        QtGui.QFontDatabase.addApplicationFont(":/fonts/roboto_regular")
        self.application.setFont(QtGui.QFont("Roboto Light", 14))


def main():
    """
    Application entry point.
    """
    ApplicationInitializer().initialize_and_start_application()


if __name__ == "__main__":
    main()
