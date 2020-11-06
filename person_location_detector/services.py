from PyQt5 import QtCore
import numpy as np
import cv2 as cv


class CameraStreamReaderThread(QtCore.QThread):
    """
    Thread that initializes connected camera and captures its frames.
    """

    camera_initialized = QtCore.pyqtSignal(bool)
    camera_frame_read = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, camera_index, camera_resolution):
        """
        Initializes thread: sets camera index, resolution and "active" thread flag.

        :param camera_index: index of the connected camera
        :param camera_resolution: resolution of the connected camera
        """
        super(CameraStreamReaderThread, self).__init__()

        self.__camera_index = camera_index
        self.__camera_resolution = camera_resolution
        self.__is_active = True

    def run(self):
        """
        Runs thread: initializes connected camera, emits initialization status signal, captures camera frames and emits
        signals with current read frame.
        """
        video_capture = cv.VideoCapture(self.__camera_index)
        if not video_capture.isOpened():
            self.camera_initialized.emit(False)
            self.__is_active = False
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
        """
        Stops thread: releases connected camera and waits for thread exit.
        """
        self.__is_active = False
        self.wait()


class CameraService:
    """
    Service that initializes connected camera and captures its frames.
    """

    def __init__(self):
        """
        Initializes service: sets camera stream reader thread.
        """
        self.__camera_stream_reader_thread = None

    def start_camera_stream_reading(self, camera_index, camera_resolution, camera_initialized_slot,
                                    camera_frame_read_slot):
        """
        Creates camera stream reader thread, connects slots with signals and starts thread execution.

        :param camera_index: index of the connected camera
        :param camera_resolution: resolution of the connected camera
        :param camera_initialized_slot: slot that is called when the camera has been initialized
        :param camera_frame_read_slot: slot that is called when the camera frame has been read
        """
        if self.is_camera_stream_reading_active():
            raise Exception("You need to stop camera stream reading first!")

        self.__camera_stream_reader_thread = CameraStreamReaderThread(camera_index, camera_resolution)
        self.__camera_stream_reader_thread.camera_initialized.connect(camera_initialized_slot)
        self.__camera_stream_reader_thread.camera_frame_read.connect(camera_frame_read_slot)
        self.__camera_stream_reader_thread.start()

    def update_camera_frame_read_slot(self, camera_frame_read_slot):
        """
        Updates "camera frame read" slot.

        :param camera_frame_read_slot: slot that is called when the camera frame has been read
        """
        if not self.is_camera_stream_reading_active():
            raise Exception("You need to start camera stream reading first!")

        self.__camera_stream_reader_thread.camera_frame_read.disconnect()
        self.__camera_stream_reader_thread.camera_frame_read.connect(camera_frame_read_slot)

    def stop_camera_stream_reading(self):
        """
        Stops camera stream reader thread execution.
        """
        if not self.is_camera_stream_reading_active():
            raise Exception("You need to start camera stream reading first!")

        self.__camera_stream_reader_thread.stop()
        self.__camera_stream_reader_thread = None

    def is_camera_stream_reading_active(self):
        """
        Returns whether camera stream reading is active (whether camera stream reader thread has been started).

        :return: whether camera stream reading is active
        """
        return self.__camera_stream_reader_thread is not None


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
