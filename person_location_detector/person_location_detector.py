import sys
import application_resources
import widgets
from PyQt5 import QtWidgets, QtGui


def main():
    """
    Application entry point: initializes and starts application.
    """
    application = QtWidgets.QApplication(sys.argv)

    QtGui.QFontDatabase.addApplicationFont(":/fonts/roboto_regular")
    application.setFont(QtGui.QFont("Roboto", 14))

    main_window = widgets.MainWindow()
    main_window.show()

    sys.exit(application.exec_())


if __name__ == "__main__":
    main()
