from PyQt5 import QtWidgets


class DetectionModelsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DetectionModelsWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        lbl = QtWidgets.QLabel("Detection models widget", self)
