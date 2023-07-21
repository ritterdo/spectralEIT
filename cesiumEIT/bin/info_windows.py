from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from traceback import format_exception

import cesiumEIT.bin.log as log

logger = log.get_logger("MessageBox")

def showCriticalMessageBox(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)

    # setting message for Message Box
    msg.setText(message)

    # setting Message box window title
    msg.setWindowTitle("Critical Error")

    # log event
    logger.error("Critical Error: " + message)

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok)

    # start the app
    retval = msg.exec_()

def showCriticalErrorBox(e, message=""):
    exc_type, exc_val, tb = e
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    error_msg = "Critical Error: " + message + "\n".join(format_exception(exc_type, exc_val, tb)) + "\n"

    # setting message for Message Box
    msg.setText(error_msg)

    # setting Message box window title
    msg.setWindowTitle(type(e).__name__)

    # log event
    logger.error(error_msg)

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok)

    # start the app
    retval = msg.exec_()

def showInfoBox(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    # setting message for Message Box
    msg.setText("Info: "+message)

    # setting Message box window title
    msg.setWindowTitle("Info Box")

    # log event
    logger.info(message)

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok)

    # start the app
    retval = msg.exec_()

def showQuestionBox(title = "QuestionBox", message = "Do you want tot proceed?"):

    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
    msg.setWindowFlags(msg.windowFlags() | Qt.FramelessWindowHint)

    return msg.exec_()
