import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QWidget

from trash_detector.constants import Mode


class VideoThread(QThread):
    changePixmapImageVideo = pyqtSignal(int, QWidget, QImage)
    changePixmapWebCam = pyqtSignal(list, QWidget, QImage)
    finished = pyqtSignal(bool, str)

    def __init__(self, parent, func, args, kwargs, widget, mode) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.widget = widget
        self.mode = mode
        super().__init__(parent)
    
    def get_frame(self, frame: np.ndarray) -> QImage:
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        return QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)

    def run(self):
        detection = self.func(
            *self.args,
            **self.kwargs,
        )
        self.is_interruption_requested = False
        try:
            yielded = next(detection)
            
            while not self.isInterruptionRequested():
                if self.mode != Mode.WEBCAM:
                    progress, image = yielded
                    frame = self.get_frame(image)
                    self.changePixmapImageVideo.emit(int(progress), self.widget, frame)
                else:
                    image, classes = yielded
                    frame = self.get_frame(image)
                    self.changePixmapWebCam.emit(classes, self.widget, frame)
                yielded = detection.send(True)
            else:
                self.is_interruption_requested = True
                detection.send(False)
        except StopIteration as exception:
            if not self.is_interruption_requested and self.mode != Mode.WEBCAM:
                self.finished.emit(True, "")
        except Exception as exception:
            self.finished.emit(False, str(exception))
