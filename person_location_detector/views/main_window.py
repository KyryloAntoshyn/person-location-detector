from PyQt5.QtWidgets import QMainWindow, QDesktopWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(800, 600)

        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(frame_geometry.topLeft())

        self.setWindowTitle("Person Location Detector")
