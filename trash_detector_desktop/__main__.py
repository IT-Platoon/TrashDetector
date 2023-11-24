import sys

from PyQt6 import QtWidgets

from trash_detector_desktop.constants import MAIN_WINDOW_TITLE
from trash_detector_desktop.windows import MainWindow


if __name__ == "__main__":
    application = QtWidgets.QApplication(sys.argv)
    application_window = MainWindow()
    application_window.setMinimumSize(900, 650)
    application_window.show()
    application_window.setWindowTitle(MAIN_WINDOW_TITLE)
    application.exec()
