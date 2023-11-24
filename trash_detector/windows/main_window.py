import os

import cv2
from PyQt6 import QtCore, QtGui, QtWidgets

from trash_detector.constants import (
    ClassesLabels,
    FUNCTIONS,
    ML_MODEL,
    REFERENCE,
    RESULT_DIRECTORY,
    RESULT_MESSAGE,
    SELECT_FILES_FAILED,
    SELECT_MODEL_FAILED,
    MethodsLoad,
    Mode,
)
from trash_detector.forms import Ui_DetectionWindow
from trash_detector.ml import InferenceAPI, load_model
from trash_detector.palettes import main_window_styles
from trash_detector.thread import VideoThread


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DetectionWindow()
        self.ui.setupUi(self)
        self.ui.reference.setPlainText(REFERENCE)
        self.ui.reference.setReadOnly(True)
        self.setStyleSheet(main_window_styles)
        self.ui.select_files.currentTextChanged.connect(self.add_combo_box_webcam)
        self.init_variable()

    def add_combo_box_webcam(self, text):
        if text == MethodsLoad.WEBCAM:
            cameras = self.get_available_cameras()
            if cameras:
                self.cameras = cameras
                self.available_cameras = QtWidgets.QComboBox(self)
                self.available_cameras.addItems(camera[-1] for camera in cameras)
                self.ui.verticalLayout_2.insertWidget(1, self.available_cameras)

                self.classes = QtWidgets.QComboBox(self)
                self.classes.addItems(label.value for label in ClassesLabels)
                self.ui.verticalLayout_2.insertWidget(2, self.classes)
            else:
                self.get_warning_window(
                    "Внимание!",
                    "Камер на данном устройстве не найдено!",
                )
                self.ui.select_files.setCurrentIndex(0)
        else:
            if self.available_cameras is not None:
                self.available_cameras.close()
                self.available_cameras = None

    def init_variable(self):
        self.mode = Mode.EMPTY
        self.result_model = None
        self.result_func = FUNCTIONS[self.mode]
        self.model_path = ""
        self.view_result = None
        self.directory_to_save = ""
        self.files = []
        self.video_thread = None
        self.list_labels = []
        self.cameras = None

        if hasattr(self, "classes"):
            if self.classes is not None:
                self.classes.close()
        self.classes = None

        if hasattr(self, "available_cameras"):
            if self.available_cameras is not None:
                self.available_cameras.close()
        self.available_cameras = None

        if hasattr(self, "progress_bar"):
            if self.progress_bar is not None:
                self.progress_bar.close()
        self.progress_bar = None

        if hasattr(self, "stop_detection"):
            if self.stop_detection is not None:
                self.stop_detection.close()
        self.stop_detection = None
        self.ui.select_files.setCurrentIndex(0)
        self.show_result = False
    
    def get_available_cameras(self) -> list[tuple[int, str]]:
        is_working = True
        dev_port = 0
        cameras = []
        while is_working:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                is_working = False
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    item = (dev_port, f"Камера {dev_port} работает и читает в разрешении ({w} x {h})")
                    cameras.append(item)
                else:
                    item = (dev_port, f"Камера {dev_port} существует, но не читает. Разрешение ({w} x {h})")
                    cameras.append(item)
            dev_port += 1
        return cameras

    def get_warning_window(self, title, text):
        QtWidgets.QMessageBox.warning(self, title, text)

    def get_critical_window(self, title, text):
        QtWidgets.QMessageBox.critical(self, title, text)

    def get_information_window(self, title, text):
        QtWidgets.QMessageBox.information(self, title, text)

    def get_files(self, method_load, extensions_images, extensions_videos):
        media_type, media, extensions, self.mode = (
            ("изображения", "Images", extensions_images, Mode.IMAGE)
            if method_load == MethodsLoad.GET_FILES_IMAGES else
            ("видео файлы", "Videos", extensions_videos, Mode.VIDEO)
        )
        self.files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            f"Выберите {media_type}",
            "/",
            f"{media} ({extensions})",
        )

    def get_directory(self, method_load, extensions_images, extensions_videos):
        try:
            media_type, extensions, self.mode = (
                ("изображений", extensions_images,  Mode.IMAGE)
                if method_load == MethodsLoad.GET_DIRECTORY_IMAGES else
                ("видео файлов", extensions_videos, Mode.VIDEO)
            )
            directory_to_load = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                f"Выберите директорию для загрузки {media_type}",
                "/",
            )
            files = os.listdir(directory_to_load)
            self.files = [
                os.path.join(directory_to_load, file)
                for file in files
                if file.endswith(extensions)
            ]
        except FileNotFoundError:
            pass

    @QtCore.pyqtSlot()
    def on_load_button_clicked(self) -> None:
        self.ui.load_button.setEnabled(False)
        conf, iou = self.ui.conf.value(), self.ui.iou.value()
        right_extensions_images = " ".join(["*.jpeg", "*.jpg", "*.png"])
        right_extensions_videos = " ".join(["*.mp4"])
        method_load = self.ui.select_files.currentText()
        if method_load in (MethodsLoad.GET_FILES_IMAGES, MethodsLoad.GET_FILES_VIDEOS):
            self.get_files(method_load, right_extensions_images, right_extensions_videos)
        elif method_load in (MethodsLoad.GET_DIRECTORY_IMAGES, MethodsLoad.GET_DIRECTORY_VIDEOS):
            self.get_directory(method_load, right_extensions_images, right_extensions_videos)
        elif method_load == MethodsLoad.WEBCAM:
            self.files = str(self.cameras[self.available_cameras.currentIndex()][0])
            self.mode = Mode.WEBCAM
        self.directory_to_save = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            RESULT_DIRECTORY,
            "/",
        )
        if self.files and self.directory_to_save:
            self.model_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                ML_MODEL,
                "/",
                "PyTorch (*.pt)",
            )
            if self.model_path:
                model = load_model(self.model_path)
                self.result_model = InferenceAPI(model, conf=conf, iou=iou)
                self.result_func = getattr(self.result_model, FUNCTIONS[self.mode])
                self.compute_result()
            else:
                self.get_critical_window("Ошибка!", SELECT_MODEL_FAILED)
        else:
            self.get_critical_window("Ошибка!", SELECT_FILES_FAILED)
        self.ui.load_button.setEnabled(True)

    @QtCore.pyqtSlot(int, QtWidgets.QWidget, QtGui.QImage)
    def setNewMediaImageVideo(self, progress, obj, image):
        is_new = False
        if self.progress_bar:
            prev_progress = self.progress_bar.value()
            if prev_progress != progress:
                is_new = True
                label = QtWidgets.QLabel(parent=self)
                self.list_labels.append(label)
                self.progress_bar.setValue(progress)
        last_label = self.list_labels[-1]
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap_resized = pixmap.scaled(
            512,
            512,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
        )
        last_label.setPixmap(pixmap_resized)
        last_label.setScaledContents(True)
        if self.mode != Mode.WEBCAM and is_new:
            obj.addWidget(last_label)
            obj.addStretch()

    @QtCore.pyqtSlot(QtWidgets.QWidget, QtGui.QImage)
    def setNewMediaWebCam(self, obj, image):
        print(self.classes.currentText())
        if not self.list_labels:
            label = QtWidgets.QLabel(parent=self)
            self.list_labels.append(label)
            obj.addWidget(self.list_labels[-1])
            obj.addStretch()
        last_label = self.list_labels[-1]
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap_resized = pixmap.scaled(
            512,
            512,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
        )
        last_label.setPixmap(pixmap_resized)
        last_label.setScaledContents(True)
    
    def clicked_stop_detection(self):
        self.video_thread.requestInterruption()
        while not self.video_thread.isFinished():
            self.video_thread.requestInterruption()
        args = (False, )
        if self.mode == Mode.WEBCAM:
            args = (True, )
        self.finish_detecting(*args)

    def compute_result(self):
        self.ui.tabWidget.setCurrentIndex(1)
        if self.ui.label is not None:
            self.ui.label.close()
            self.ui.label = None
        if self.progress_bar is not None:
            self.progress_bar.close()
            self.progress_bar = None
        list_detections = QtWidgets.QWidget()
        self.ui.scrollArea.setWidget(list_detections)
        self.stop_detection = QtWidgets.QPushButton("Остановить детекцию")
        self.stop_detection.clicked.connect(self.clicked_stop_detection)
        self.ui.verticalLayout_5.addWidget(self.stop_detection)
        if self.mode != Mode.WEBCAM:
            self.progress_bar = QtWidgets.QProgressBar(self)
            self.ui.verticalLayout_5.addWidget(self.progress_bar)
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        list_detections.setLayout(vbox)
        args = (self.files, self.directory_to_save)
        kwargs = {}
        if self.mode == Mode.WEBCAM:
            kwargs.update({"flag_save_imgs": True})
        self.video_thread = VideoThread(
            self,
            self.result_func,
            args,
            kwargs,
            vbox,
            self.mode,
        )
        self.video_thread.changePixmapImageVideo.connect(self.setNewMediaImageVideo)
        self.video_thread.changePixmapWebCam.connect(self.setNewMediaWebCam)
        self.video_thread.finished.connect(self.finish_detecting)
        self.video_thread.start()

    @QtCore.pyqtSlot(bool, str)
    def finish_detecting(
        self,
        is_success: bool = False,
        message: str = "Вы прервали детекцию",
    ) -> None:
        self.video_thread.quit()
        if not is_success:
            self.get_warning_window("Детекция прервана!", message)
        else:
            if self.mode != Mode.WEBCAM:
                self.progress_bar.setValue(100)
            self.get_information_window("Детекция завершена!", RESULT_MESSAGE)
        self.init_variable()
