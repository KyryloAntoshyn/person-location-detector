import numpy as np
import cv2 as cv
import queue
import time
from PyQt5 import QtCore
from shapely.geometry import Point, Polygon


class CameraStreamReaderThread(QtCore.QThread):
    """
    Thread that initializes connected camera and captures its frames.
    """

    camera_initialized = QtCore.pyqtSignal(bool)
    camera_frame_read = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, camera_index, camera_resolution):
        """
        Initializes thread.

        :param camera_index: index of the connected camera
        :param camera_resolution: resolution of the connected camera
        """
        super(CameraStreamReaderThread, self).__init__()

        self.camera_index = camera_index
        self.camera_resolution = camera_resolution
        self.is_running = False
        self.video_capture = None
        self.is_person_location_detection_running = False
        self.camera_frames_to_process = None

    def run(self):
        """
        Runs thread: initializes connected camera and captures its frames. Thread can switch its state and start putting
        camera frames into the queue in order for person location detection thread to process them.
        """
        self.is_running = True

        if not self.__initialize_camera():
            self.camera_initialized.emit(False)
            self.is_running = False
            self.video_capture = None
            return

        self.camera_initialized.emit(True)

        while self.is_running:
            is_successful_camera_frame_read, camera_frame = self.video_capture.read()
            if is_successful_camera_frame_read:
                self.camera_frame_read.emit(camera_frame)

                if self.is_person_location_detection_running:
                    self.camera_frames_to_process.put(camera_frame)
                    self.camera_frames_to_process.join()

        self.video_capture.release()

    def __initialize_camera(self):
        """
        Initializes camera.

        :return: whether camera has been initialized successfully
        """
        self.video_capture = cv.VideoCapture(self.camera_index)
        if not self.video_capture.isOpened():
            return False

        self.video_capture.set(cv.CAP_PROP_FRAME_WIDTH, self.camera_resolution[0])
        self.video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.camera_resolution[1])

        return True

    def stop(self):
        """
        Stops thread: returns thread to the initial state (before running).
        """
        self.is_running = False
        self.is_person_location_detection_running = False
        self.wait()
        self.video_capture = None


class CameraService:
    """
    Service that initializes connected camera and captures its frames.
    """

    def __init__(self):
        """
        Initializes service.
        """
        self.__camera_stream_reader_thread = None

    def is_camera_stream_reading_running(self):
        """
        Returns whether camera stream reading is running (whether camera stream reader thread has been started).

        :return: whether camera stream reading is running
        """
        return self.__camera_stream_reader_thread is not None and self.__camera_stream_reader_thread.is_running

    def start_camera_stream_reading(self, camera_index, camera_resolution, camera_initialized_slot,
                                    camera_frame_read_slot):
        """
        Creates camera stream reader thread, connects signals with slots and starts thread execution.

        :param camera_index: index of the connected camera
        :param camera_resolution: resolution of the connected camera
        :param camera_initialized_slot: slot that is called when the camera has been initialized
        :param camera_frame_read_slot: slot that is called when the camera frame has been read
        """
        if self.is_camera_stream_reading_running():
            raise Exception("You need to stop camera stream reading first!")

        self.__camera_stream_reader_thread = CameraStreamReaderThread(camera_index, camera_resolution)
        self.__camera_stream_reader_thread.camera_initialized.connect(camera_initialized_slot)
        self.__camera_stream_reader_thread.camera_frame_read.connect(camera_frame_read_slot)
        self.__camera_stream_reader_thread.start()

    def update_camera_frame_read_slot(self, current_camera_frame_read_slot, updated_camera_frame_read_slot):
        """
        Updates "camera frame read" slot.

        :param current_camera_frame_read_slot: current slot that is called when the camera frame has been read
        :param updated_camera_frame_read_slot: updated slot that is called when the camera frame has been read
        """
        if not self.is_camera_stream_reading_running():
            raise Exception("You need to start camera stream reading first!")

        self.__camera_stream_reader_thread.camera_frame_read.disconnect(current_camera_frame_read_slot)
        self.__camera_stream_reader_thread.camera_frame_read.connect(updated_camera_frame_read_slot)

    def disconnect_camera_frame_read_slot(self, camera_frame_read_slot):
        """
        Disconnects "camera frame read" slot.

        :param camera_frame_read_slot: slot that is called when the camera frame has been read
        """
        if not self.is_camera_stream_reading_running():
            raise Exception("You need to start camera stream reading first!")

        self.__camera_stream_reader_thread.camera_frame_read.disconnect(camera_frame_read_slot)

    def connect_camera_frame_read_slot(self, camera_frame_read_slot):
        """
        Connects "camera frame read" slot.

        :param camera_frame_read_slot: slot that is called when the camera frame has been read
        """
        if not self.is_camera_stream_reading_running():
            raise Exception("You need to start camera stream reading first!")

        self.__camera_stream_reader_thread.camera_frame_read.connect(camera_frame_read_slot)

    def clean_camera_stream_reading_resources(self):
        """
        Cleans camera stream reader thread resources.
        """
        if self.__camera_stream_reader_thread is None:
            raise Exception("You need to start camera stream reading first!")

        self.__camera_stream_reader_thread = None

    def stop_camera_stream_reading(self):
        """
        Stops camera stream reader thread execution and cleans its resources.
        """
        if not self.is_camera_stream_reading_running():
            raise Exception("You need to start camera stream reading first!")

        self.__camera_stream_reader_thread.stop()
        self.clean_camera_stream_reading_resources()

    def switch_camera_stream_reading_state(self, is_person_location_detection, camera_frames_to_process=None):
        """
        Switches camera stream reading state from plain reading to reading camera frames and putting them into the
        queue in order for person location detection thread to process them and vice versa.

        :param is_person_location_detection: whether person location detection is running
        :param camera_frames_to_process: camera frames to process queue
        """
        if not self.is_camera_stream_reading_running():
            raise Exception("You need to start camera stream reading first!")

        if is_person_location_detection:
            if camera_frames_to_process is None:
                raise Exception("Camera frames to process queue should be initialized!")

            self.__camera_stream_reader_thread.camera_frames_to_process = camera_frames_to_process
            self.__camera_stream_reader_thread.is_person_location_detection_running = True
        else:
            self.__camera_stream_reader_thread.is_person_location_detection_running = False


class PersonLocationDetectionThread(QtCore.QThread):
    """
    Thread that detects locations of persons within the projection area.
    """

    camera_frame_processed = QtCore.pyqtSignal(tuple)

    def __init__(self, detection_model_weights_file_path, detection_model_configuration_file_path,
                 detection_model_input_scale, detection_model_input_size, detection_model_person_class_id,
                 detection_model_confidence_threshold, detection_model_nms_threshold, projection_area_coordinates,
                 projection_area_resolution):
        """
        Initializes thread.

        :param detection_model_weights_file_path: detection model weights file path
        :param detection_model_configuration_file_path: detection model configuration file path
        :param detection_model_input_scale: detection model scale factor for input frames
        :param detection_model_input_size: detection model input size
        :param detection_model_person_class_id: detection model person class ID
        :param detection_model_confidence_threshold: detection model confidence threshold
        :param detection_model_nms_threshold: detection model non-maximum suppression threshold
        :param projection_area_coordinates: projection area coordinates
        :param projection_area_resolution: projection area resolution
        """
        super(PersonLocationDetectionThread, self).__init__()

        self.detection_model_weights_file_path = detection_model_weights_file_path
        self.detection_model_configuration_file_path = detection_model_configuration_file_path
        self.detection_model_input_scale = detection_model_input_scale
        self.detection_model_input_size = detection_model_input_size
        self.detection_model_person_class_id = detection_model_person_class_id
        self.detection_model_confidence_threshold = detection_model_confidence_threshold
        self.detection_model_nms_threshold = detection_model_nms_threshold
        self.projection_area_coordinates = projection_area_coordinates
        self.projection_area_resolution = projection_area_resolution
        self.is_running = False
        self.camera_frames_to_process = queue.Queue(1)
        self.detection_model = None
        self.perspective_transformation_matrix = None
        self.projection_area_polygon = None

    def run(self):
        """
        Runs thread: initializes detection model, perspective transformation matrix, projection area polygon and
        processes camera frames.
        """
        self.is_running = True

        self.__initialize_detection_model()
        self.__initialize_perspective_transformation_matrix()
        self.projection_area_polygon = Polygon(self.projection_area_coordinates)

        while self.is_running:
            try:
                camera_frame_to_process = self.camera_frames_to_process.get_nowait()
            except queue.Empty:
                continue

            class_ids, confidences, bounding_boxes, fps_number = self.__detect_camera_frame_objects_and_measure_fps(
                camera_frame_to_process)

            result_confidences = []
            result_bounding_boxes = []
            result_persons_locations = []
            for (class_id, confidence, bounding_box) in zip(class_ids, confidences, bounding_boxes):
                if class_id[0] != self.detection_model_person_class_id:
                    continue

                bounding_box_bottom_edge_center_point, is_within_projection_area = \
                    self.__is_bounding_box_bottom_edge_center_point_within_projection_area(bounding_box)
                if not is_within_projection_area:
                    continue

                result_confidences.append(confidence[0])
                result_bounding_boxes.append(bounding_box)
                result_persons_locations.append(self.__calculate_person_location(bounding_box_bottom_edge_center_point))

            camera_frame_to_process_warped = self.__warp_camera_frame_to_process(camera_frame_to_process)
            self.camera_frame_processed.emit((camera_frame_to_process, camera_frame_to_process_warped, fps_number,
                                              result_confidences, result_bounding_boxes, result_persons_locations))

            self.camera_frames_to_process.task_done()

    def __initialize_detection_model(self):
        """
        Initializes detection model.
        """
        self.detection_model = cv.dnn_DetectionModel(self.detection_model_weights_file_path,
                                                     self.detection_model_configuration_file_path)
        self.detection_model.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.detection_model.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        self.detection_model.setInputParams(self.detection_model_input_scale, self.detection_model_input_size)

    def __initialize_perspective_transformation_matrix(self):
        """
        Initializes perspective transformation matrix.
        """
        source_points = np.float32(self.projection_area_coordinates)
        destination_points = np.float32([[self.projection_area_resolution[0], 0], self.projection_area_resolution,
                                         [0, self.projection_area_resolution[1]], [0, 0]])
        self.perspective_transformation_matrix = cv.getPerspectiveTransform(source_points, destination_points)

    def __detect_camera_frame_objects_and_measure_fps(self, camera_frame_to_process):
        """
        Detects objects on the camera frame and measures FPS.

        :param camera_frame_to_process: camera frame to process
        :return: tuple with class id's, confidences, bounding boxes and FPS number
        """
        start_detection_time = time.time()
        class_ids, confidences, bounding_boxes = self.detection_model.detect(
            camera_frame_to_process, self.detection_model_confidence_threshold, self.detection_model_nms_threshold)
        end_detection_time = time.time()
        fps_number = 1 / (end_detection_time - start_detection_time)

        return class_ids, confidences, bounding_boxes, fps_number

    def __is_bounding_box_bottom_edge_center_point_within_projection_area(self, bounding_box):
        """
        Calculates bounding box bottom edge center point and checks whether it is within the projection area.

        :param bounding_box: bounding box
        :return: calculated bounding box bottom edge center point and indication whether it is within the projection
        area
        """
        bounding_box_bottom_edge_center_point = Point((bounding_box[0] + bounding_box[2] / 2,
                                                       bounding_box[1] + bounding_box[3]))

        return (bounding_box_bottom_edge_center_point,
                bounding_box_bottom_edge_center_point.within(self.projection_area_polygon))

    def __calculate_person_location(self, bounding_box_bottom_edge_center_point):
        """
        Calculates person location by transforming it in perspective.

        :param bounding_box_bottom_edge_center_point: bounding box bottom edge center point
        :return: transformed bounding box bottom edge center point
        """
        return ((self.perspective_transformation_matrix[0][0] * bounding_box_bottom_edge_center_point.x +
                 self.perspective_transformation_matrix[0][1] * bounding_box_bottom_edge_center_point.y +
                 self.perspective_transformation_matrix[0][2]) /
                (self.perspective_transformation_matrix[2][0] * bounding_box_bottom_edge_center_point.x +
                 self.perspective_transformation_matrix[2][1] * bounding_box_bottom_edge_center_point.y +
                 self.perspective_transformation_matrix[2][2]),
                (self.perspective_transformation_matrix[1][0] * bounding_box_bottom_edge_center_point.x +
                 self.perspective_transformation_matrix[1][1] * bounding_box_bottom_edge_center_point.y +
                 self.perspective_transformation_matrix[1][2]) /
                (self.perspective_transformation_matrix[2][0] * bounding_box_bottom_edge_center_point.x +
                 self.perspective_transformation_matrix[2][1] * bounding_box_bottom_edge_center_point.y +
                 self.perspective_transformation_matrix[2][2]))

    def __warp_camera_frame_to_process(self, camera_frame_to_process):
        """
        Warps camera frame to process.

        :param camera_frame_to_process: camera frame to process
        :return: warped camera frame to process
        """
        return cv.warpPerspective(camera_frame_to_process, self.perspective_transformation_matrix,
                                  self.projection_area_resolution)

    def stop(self):
        """
        Stops thread: returns thread to the initial state (before running).
        """
        self.is_running = False
        self.wait()
        self.camera_frames_to_process.queue.clear()
        self.detection_model = None
        self.perspective_transformation_matrix = None
        self.projection_area_polygon = None


class PersonLocationDetectionService:
    """
    Service that detects locations of persons within the projection area.
    """

    def __init__(self):
        """
        Initializes service.
        """
        self.__person_location_detection_thread = None

    def is_person_location_detection_running(self):
        """
        Returns whether person location detection is running (whether person location detection thread has been
        started).

        :return: whether person location detection is running
        """
        return self.__person_location_detection_thread is not None and self.__person_location_detection_thread.is_running

    def start_person_location_detection(self, detection_model_weights_file_path,
                                        detection_model_configuration_file_path, detection_model_input_scale,
                                        detection_model_input_size, detection_model_person_class_id,
                                        detection_model_confidence_threshold, detection_model_nms_threshold,
                                        projection_area_coordinates, projection_area_resolution,
                                        camera_frame_processed_slot):
        """
        Creates person location detection thread, connects signal with slot and starts thread execution.

        :param detection_model_weights_file_path: detection model weights file path
        :param detection_model_configuration_file_path: detection model configuration file path
        :param detection_model_input_scale: detection model scale factor for input frames
        :param detection_model_input_size: detection model input size
        :param detection_model_person_class_id: detection model person class ID
        :param detection_model_confidence_threshold: detection model confidence threshold
        :param detection_model_nms_threshold: detection model non-maximum suppression threshold
        :param projection_area_coordinates: projection area coordinates
        :param projection_area_resolution: projection area resolution
        :param camera_frame_processed_slot: slot that is called when the camera frame has been processed
        """
        if self.is_person_location_detection_running():
            raise Exception("You need to stop person location detection first!")

        self.__person_location_detection_thread = PersonLocationDetectionThread(detection_model_weights_file_path,
                                                                                detection_model_configuration_file_path,
                                                                                detection_model_input_scale,
                                                                                detection_model_input_size,
                                                                                detection_model_person_class_id,
                                                                                detection_model_confidence_threshold,
                                                                                detection_model_nms_threshold,
                                                                                projection_area_coordinates,
                                                                                projection_area_resolution)
        self.__person_location_detection_thread.camera_frame_processed.connect(camera_frame_processed_slot)
        self.__person_location_detection_thread.start()

    @property
    def camera_frames_to_process(self):
        """
        Gets camera frames to process queue.

        :return: camera frames to process queue
        """
        return self.__person_location_detection_thread.camera_frames_to_process

    def update_detection_model_confidence_threshold(self, updated_detection_model_confidence_threshold):
        """
        Updates detection model confidence threshold.

        :param updated_detection_model_confidence_threshold: updated detection model confidence threshold
        """
        if not self.is_person_location_detection_running():
            raise Exception("You need to start person location detection first!")

        self.__person_location_detection_thread.detection_model_confidence_threshold = \
            updated_detection_model_confidence_threshold

    def update_detection_model_nms_threshold(self, updated_detection_model_nms_threshold):
        """
        Updates detection model non-maximum suppression threshold.

        :param updated_detection_model_nms_threshold: updated detection model non-maximum suppression threshold
        """
        if not self.is_person_location_detection_running():
            raise Exception("You need to start person location detection first!")

        self.__person_location_detection_thread.detection_model_nms_threshold = updated_detection_model_nms_threshold

    def stop_person_location_detection(self):
        """
        Stops person location detection thread execution and cleans its resources.
        """
        if not self.is_person_location_detection_running():
            raise Exception("You need to start person location detection first!")

        self.__person_location_detection_thread.stop()
        self.__person_location_detection_thread = None
