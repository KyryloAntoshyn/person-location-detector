from PyQt5 import QtCore
import numpy as np
import cv2 as cv
import time
from shapely.geometry import Point, Polygon
import queue


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
        self.__is_detection_active = False

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

            if self.__is_detection_active:
                is_success_frame_read, frame = video_capture.read()
                if is_success_frame_read:
                    self.tasks.put(frame)
            else:
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

    def detection_state_changed(self, is_detection_active):
        self.__is_detection_active = is_detection_active


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

    def detection_started(self, tasks):
        self.__camera_stream_reader_thread.tasks = tasks
        self.__camera_stream_reader_thread.detection_state_changed(True)


class PersonLocationDetectionThread(QtCore.QThread):
    camera_frame_processed = QtCore.pyqtSignal(tuple)

    def __init__(self, detection_model_weights_file_path, detection_model_configuration_file_path,
                 detection_model_scale, detection_model_size, person_class_id, confidence_threshold, nms_threshold,
                 projection_area_coordinates, projection_area_resolution):
        super(PersonLocationDetectionThread, self).__init__()

        self.__detection_model_weights_file_path = detection_model_weights_file_path
        self.__detection_model_configuration_file_path = detection_model_configuration_file_path
        self.__detection_model_scale = detection_model_scale
        self.__detection_model_size = detection_model_size
        self.__person_class_id = person_class_id
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.__projection_area_coordinates = projection_area_coordinates
        self.__projection_area_resolution = projection_area_resolution

        self.location_detection_tasks = queue.Queue(maxsize=1)

    def run(self):
        detection_model = cv.dnn_DetectionModel(self.__detection_model_weights_file_path,
                                                self.__detection_model_configuration_file_path)
        detection_model.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        detection_model.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        detection_model.setInputParams(self.__detection_model_scale, self.__detection_model_size)

        while True:
            camera_frame = self.location_detection_tasks.get()

            start_detection_time = time.time()
            class_ids, confidences, boxes = detection_model.detect(camera_frame, self.confidence_threshold,
                                                                   self.nms_threshold)
            end_detection_time = time.time()

            result_class_ids = []
            result_confidences = []
            result_boxes = []
            result_center_points = []
            result_points_ext = []

            # Get warp matrix
            pts1 = np.float32(self.__projection_area_coordinates)
            pts2 = np.float32([[self.__projection_area_resolution[0], 0], self.__projection_area_resolution,
                               [0, self.__projection_area_resolution[1]], [0, 0]])
            matrix = cv.getPerspectiveTransform(pts1, pts2)

            poly = Polygon(self.__projection_area_coordinates)
            for (class_id, confidence, box) in zip(class_ids, confidences, boxes):
                if class_id[0] != self.__person_class_id:
                    continue

                box_bottom_edge_center = (box[0] + box[2] / 2, box[1] + box[3])
                point = Point(box_bottom_edge_center)
                if point.within(poly):
                    result_class_ids.append(class_id)
                    result_confidences.append(confidence)
                    result_boxes.append(box)
                    result_center_points.append(box_bottom_edge_center)
                    px = (matrix[0][0] * box_bottom_edge_center[0] + matrix[0][1] * box_bottom_edge_center[1] +
                          matrix[0][2]) / (
                             (matrix[2][0] * box_bottom_edge_center[0] + matrix[2][1] * box_bottom_edge_center[1] +
                              matrix[2][2]))
                    py = (matrix[1][0] * box_bottom_edge_center[0] + matrix[1][1] * box_bottom_edge_center[1] +
                          matrix[1][2]) / (
                             (matrix[2][0] * box_bottom_edge_center[0] + matrix[2][1] * box_bottom_edge_center[1] +
                              matrix[2][2]))
                    result_points_ext.append((px, py))

            camera_frame_warped = cv.warpPerspective(camera_frame, matrix, self.__projection_area_resolution)
            self.camera_frame_processed.emit(
                (camera_frame, camera_frame_warped, result_confidences, result_boxes, matrix, result_center_points, result_points_ext))

            self.location_detection_tasks.task_done()


class PersonLocationDetectionService:

    def __init__(self):
        self.location_detection_thread = None

    def start_person_location_detection(self, weights_file_path, configuration_file_path, scale, size, person_class_id,
                                        confidence_threshold,
                                        nms_threshold, projection_area_coordinates, projection_area_resolution,
                                        camera_frame_processed_slot,
                                        camera_service):
        self.location_detection_thread = PersonLocationDetectionThread(weights_file_path, configuration_file_path,
                                                                       scale,
                                                                       size, person_class_id, confidence_threshold,
                                                                       nms_threshold,
                                                                       projection_area_coordinates,
                                                                       projection_area_resolution)
        camera_service.detection_started(self.location_detection_thread.location_detection_tasks)
        self.location_detection_thread.camera_frame_processed.connect(camera_frame_processed_slot)

        self.location_detection_thread.start()

    def update_confidence_threshold(self, updated_confidence_threshold):
        if self.location_detection_thread is not None:
            self.location_detection_thread.confidence_threshold = updated_confidence_threshold

    def update_nms_threshold(self, updated_nms_threshold):
        if self.location_detection_thread is not None:
            self.location_detection_thread.nms_threshold = updated_nms_threshold
