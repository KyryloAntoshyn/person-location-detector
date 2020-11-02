import sys
import widgets
import application_resources
from dependency_injection import DependencyInjectionContainer
from PyQt5 import QtWidgets, QtGui


class ApplicationInitializer:
    """
    Class that is responsible for application initialization.
    """

    @staticmethod
    def create_and_configure_dependency_injection_container():
        """
        Creates and configures dependency injection container.
        """
        container = DependencyInjectionContainer()
        container.configuration_provider.from_ini("configuration.ini")
        container.wire(modules=[sys.modules[widgets.__name__]])

    @staticmethod
    def initialize_and_start_application():
        """
        Creates application, applies global styles, creates main window, shows it and starts application event loop.
        """
        application = QtWidgets.QApplication(sys.argv)
        QtGui.QFontDatabase.addApplicationFont(":/fonts/roboto_light")
        QtGui.QFontDatabase.addApplicationFont(":/fonts/roboto_regular")
        application.setFont(QtGui.QFont("Roboto Light", 14))

        main_window = widgets.MainWindow()
        main_window.show()

        sys.exit(application.exec_())


def main():
    """
    Application entry point. Creates and configures dependency injection container, initializes and starts application.
    """
    ApplicationInitializer.create_and_configure_dependency_injection_container()
    ApplicationInitializer.initialize_and_start_application()


if __name__ == "__main__":
    main()
