from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from traceback import format_exception

def showCriticalMessageBox(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)

    # setting message for Message Box
    msg.setText(message)

    # setting Message box window title
    msg.setWindowTitle("Critical Error")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # start the app
    retval = msg.exec_()

def showCriticalErrorBox(e, message=""):
    exc_type, exc_val, tb = e
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)

    # setting message for Message Box
    msg.setText("Critical Error: " + message + "\n" + "".join(format_exception(exc_type, exc_val, tb)))#str(e.args))

    # setting Message box window title
    msg.setWindowTitle(type(e).__name__)

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # start the app
    retval = msg.exec_()

def showInfoBox(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    # setting message for Message Box
    msg.setText("Info: "+message)

    # setting Message box window title
    msg.setWindowTitle("Info Box")

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
