import sys
import application_resources
import constants
import widgets
from PyQt5 import QtWidgets, QtGui


def main():
    """
    Application entry point: initializes and starts application.
    """
    application = QtWidgets.QApplication(sys.argv)

    QtGui.QFontDatabase.addApplicationFont(constants.APPLICATION_FONT_RESOURCE)
    application.setFont(QtGui.QFont(constants.APPLICATION_FONT_FAMILY_NAME, constants.APPLICATION_FONT_SIZE))

    main_window = widgets.MainWindow()
    main_window.show()

    sys.exit(application.exec_())


if __name__ == "__main__":
    main()
