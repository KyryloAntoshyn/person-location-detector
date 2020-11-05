from PyQt5 import QtCore
import numpy as np
import cv2 as cv


class VideoThread(QtCore.QThread):
    camera_initialized = QtCore.pyqtSignal(bool)
    camera_frame_read = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, camera_index, camera_resolution):
        super(VideoThread, self).__init__()

        self.__camera_index = camera_index
        self.__camera_resolution = camera_resolution
        self.__is_active = True

    def run(self):
        video_capture = cv.VideoCapture(self.__camera_index)

        if not video_capture.isOpened():
            self.camera_initialized.emit(False)
            self.stop()
            return

        video_capture.set(cv.CAP_PROP_FRAME_WIDTH, self.__camera_resolution[0])
        video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.__camera_resolution[1])

        self.camera_initialized.emit(True)

        while self.__is_active:
            is_success_frame_read, frame = video_capture.read()

            if is_success_frame_read:
                self.camera_frame_read.emit(frame)

        video_capture.release()

    def stop(self):
        self.__is_active = False
        self.wait()


class CameraService:
    def __init__(self):
        self.__video_thread = None

    def start_camera_stream(self, camera_index, camera_resolution, camera_initialized_callback,
                            camera_frame_read_callback):
        self.__video_thread = VideoThread(camera_index, camera_resolution)
        self.__video_thread.camera_initialized.connect(camera_initialized_callback)
        self.__video_thread.camera_frame_read.connect(camera_frame_read_callback)
        self.__video_thread.start()

    def stop_camera_stream(self):
        self.__video_thread.stop()
        self.__video_thread = None

    def update_camera_frame_read_callback(self, camera_frame_read_callback):
        self.__video_thread.camera_frame_read.disconnect()
        self.__video_thread.camera_frame_read.connect(camera_frame_read_callback)


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
