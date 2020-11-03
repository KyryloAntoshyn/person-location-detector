from PyQt5 import QtCore
import numpy as np
import cv2 as cv


class VideoThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, camera_resolution):
        super(VideoThread, self).__init__()
        self.__camera_resolution = camera_resolution
        self._run_flag = True

    def run(self):
        cap = cv.VideoCapture(0)

        cap.set(cv.CAP_PROP_FRAME_WIDTH, self.__camera_resolution[0])
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.__camera_resolution[1])

        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class CameraService:
    def __init__(self):
        self.__video_thread = None

    def start_video_thread(self, callback):
        camera_resolution = (1280, 720)

        self.__video_thread = VideoThread(camera_resolution)
        self.__video_thread.change_pixmap_signal.connect(callback)
        self.__video_thread.start()

    def stop_video_thread(self):
        self.__video_thread.stop()
        self.__video_thread = None

    def update_video_callback(self, new_callback):
        self.__video_thread.change_pixmap_signal.disconnect()
        self.__video_thread.change_pixmap_signal.connect(new_callback)


class DetectionService:
    def __init__(self):
        self.__detection_model = None

    def initialize_detection_model(self, weights_file_path, configuration_file_path, scale, size):
        self.__detection_model = cv.dnn_DetectionModel(weights_file_path, configuration_file_path)
        self.__detection_model.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.__detection_model.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        self.__detection_model.setInputParams(scale, size)

    def detect_objects(self, frame, conf_threshold, nms_threshold):
        return self.__detection_model.detect(frame, conf_threshold, nms_threshold)
