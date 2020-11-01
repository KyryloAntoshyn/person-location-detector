from PyQt5 import QtWidgets


class AboutWidget(QtWidgets.QWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("About widget", self)
