import sys, os

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path += ["../",os.path.join("..", ".."), "."]

from spectralEIT.bin.default_config import *

sys.path += [ui_path]

os.environ["QT_MAC_WANTS_LAYER"] = "1"

from spectralEIT.ui.main_window import MainWindow

import spectralEIT.bin.log as log

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream

import platform

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def main():
    
    logger = log.get_logger()
    logger.info("Application Starts")

    # QApplication.setGraphicsSystem("raster")
    app = QApplication(sys.argv)

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

    window = MainWindow()
    window.show()

    # Start the event loop.
    sys.exit(app.exec())
    # app.exec_()

if __name__ == "__main__":
    main()
