import sys
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path += ["../",os.path.join("..", ".."), "."]

from spectralEIT.bin.default_config import *

sys.path += [ui_path]

os.environ["QT_MAC_WANTS_LAYER"] = "1"

from spectralEIT.ui.main_window import MainWindow
from spectralEIT.bin.info_windows import showQuestionBox

import spectralEIT.bin.log as log

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtGui import QFont

import platform

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def main():

    # QApplication.setGraphicsSystem("raster")
    app = QApplication(sys.argv)

    check_logs_dir()
    check_logs_dir_size()
    
    logger = log.get_logger()
    logger.info("Application Starts")

    f = QFile("bin/style_Dark.qss")
    if not f.exists():
        # print("stylesheet: in if not")
        f = QFile("bin/style_Dark.css")
    else:
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
        if platform.system().lower() == 'darwin':
            mac_fix = '''
            QDockWidget::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }
            '''
            stylesheet += mac_fix

        app.setStyleSheet(stylesheet)
    # app.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_Dark"))

    system = platform.system()
    if system == "Linux":
        custom_font = QFont("Noto Sans")
        custom_font.setPointSize(9)
        app.setFont(custom_font)
    elif system == "Darwin":
        custom_font = QFont("Helvetica Neue")
        custom_font.setPointSize(9)
        app.setFont(custom_font)
    elif system == "Windows":
        custom_font = QFont("Segoe UI")
        custom_font.setPointSize(9)
        app.setFont(custom_font)

    window = MainWindow()
    window.show()

    # Start the event loop.
    sys.exit(app.exec())
    # app.exec_()

def check_logs_dir():
    if not os.path.exists("logs"):
        os.mkdir("logs")

def check_logs_dir_size():
    total_size = 0
    total_files = 0
    for dirpath, dirnames, filenames in os.walk("logs"):
        for f in filenames:
            total_files += 1
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    if total_size > 100000000:
        result = showQuestionBox("Warning", "Log folder size is over 100MB. Do you want to delete all old logs?.")
        if result == QMessageBox.Yes:
            for dirpath, dirnames, filenames in os.walk("logs"):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    os.remove(fp)
    if total_files > 20:
        result = showQuestionBox("Warning", "Log folder contains more than 20 files. Do you want to delete all old logs?.")
        if result == QMessageBox.Yes:
            for dirpath, dirnames, filenames in os.walk("logs"):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    os.remove(fp)
        

if __name__ == "__main__":
    main()
