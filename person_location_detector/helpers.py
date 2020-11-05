import cv2 as cv
from PyQt5 import QtGui


def convert_opencv_image_to_pixmap(opencv_image):
    """
    Converts OpenCV image to pixmap.

    :param opencv_image: OpenCV image
    :return: pixmap
    """
    opencv_rgb_image = cv.cvtColor(opencv_image, cv.COLOR_BGR2RGB)
    opencv_image_height, opencv_image_width, opencv_image_channels_number = opencv_rgb_image.shape
    return QtGui.QPixmap.fromImage(
        QtGui.QImage(opencv_rgb_image.data, opencv_image_width, opencv_image_height,
                     opencv_image_channels_number * opencv_image_width, QtGui.QImage.Format_RGB888))
