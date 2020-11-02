import sys
from dependency_injection import DependencyInjectionContainer
from PyQt5 import QtWidgets, QtGui
from widgets import MainWindow
import application_resources
import widgets


def create_and_configure_dependency_injection_container():
    """
    Creates and configures dependency injection container.
    """
    container = DependencyInjectionContainer()
    container.configuration_provider.from_ini("configuration.ini")
    container.wire(modules=[sys.modules[widgets.__name__]])


def initialize_and_start_application():
    """
    Creates application, applies global styles, creates main window, shows it and starts application event loop.
    """
    application = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont(":/fonts/roboto_light")
    QtGui.QFontDatabase.addApplicationFont(":/fonts/roboto_regular")
    application.setFont(QtGui.QFont("Roboto Light", 14))

    main_window = MainWindow()
    main_window.show()

    sys.exit(application.exec_())


def main():
    """
    Application entry point. Creates and configures dependency injection container, initializes and starts application.
    """
    create_and_configure_dependency_injection_container()
    initialize_and_start_application()


if __name__ == "__main__":
    main()
