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


def convert_polygon_points_to_coordinates_list(polygon):
    """
    Converts polygon points to list of coordinates – (x, y) tuples.

    :param polygon: polygon
    :return: list of coordinates
    """
    polygon_point_coordinates = []
    for i in range(0, polygon.count()):
        polygon_point = polygon.point(i)
        polygon_point_coordinates.append((polygon_point.x(), polygon_point.y()))
    return polygon_point_coordinates


def convert_points_to_another_resolution(points, current_resolution, result_resolution):
    converted_points = []
    for point in points:
        converted_points.append((result_resolution[0] * point[0] / current_resolution[0],
                                 result_resolution[1] * point[1] / current_resolution[1]))

    return converted_points
