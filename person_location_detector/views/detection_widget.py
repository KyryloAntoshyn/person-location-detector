from PyQt5 import QtWidgets


class DetectionWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DetectionWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("Detection widget", self)
