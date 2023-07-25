import sys
from PyQt5.QtWidgets import QTabWidget, QTabBar, QLineEdit, QToolButton, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QEvent

from cesiumEIT.ui.pyplot_widget import PyPlotWidget

import logging

class GraphTabWidget(QTabWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger(__name__)
        self.logger.info("Initiate GraphTabWidget")

        tabBar = GraphTabBar(self)
        self.setTabBar(tabBar)

        self.currentChanged.connect(lambda: self.window().plot_tab_changed.emit(self.currentIndex()))

        ## Add standart widgets
        self.logger.info("Adding default tabs Frequency")
        self.addTab(name="Frequency", labels={"bottom":("Frequency", "Hz"), "left":"Transmission"})
        self.logger.info("Adding default tabs Time")
        self.addTab(name="Time", labels={"bottom":("Time", "s"), "left":("Intensity", "a.u.")})
        self.logger.info("Adding default tabs Space")
        self.addTab(name="Space", labels={"bottom":("Distance", "m"), "left":("Rabi-Frequncy", "Hz")})


    def addTab(self, item: PyPlotWidget = None, name: str = None, labels: dict = {}):
        if not item:
            item = PyPlotWidget(name=name, labels=labels)
        super().addTab(item, name)


    def setTabText(self, index, name):
        self.logger.info("Change name of tag %d to %s", index, name)
        self.widget(index).name = name
        super().setTabText(index, name)


class GraphTabBar(QTabBar):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tabWidget = parent

        ## Editing Tab Text
        self.editor = QLineEdit(self)
        self.editor.setWindowFlags(Qt.Popup)
        self.editor.setFocusProxy(self)
        self.editor.editingFinished.connect(self.handleEditingFinished)
        self.editor.installEventFilter(self)


    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.mouse_pos = event.pos()
        else:
            super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            index = self.tabAt(event.pos())
            if index >= 0:
                result = QMessageBox.question(self,
                              "Confirm Plot Close...",
                              "Are you sure you want to close with Plot?",
                              QMessageBox.Yes| QMessageBox.No)

                if result == QMessageBox.Yes:
                    self.removeTab(index)
            return
        elif event.button() == Qt.RightButton:
            self.tabWidget.addTab(PyPlotWidget(), "New")
        else:
            super().mouseReleaseEvent(event)


    def eventFilter(self, widget, event):
        if ((event.type() == QEvent.MouseButtonPress and
             not self.editor.geometry().contains(event.globalPos())) or
            (event.type() == QEvent.KeyPress and
             event.key() == Qt.Key_Escape)):
            self.editor.hide()
            return True
        return super().eventFilter(widget, event)


    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.editTab(index)


    def editTab(self, index):
        rect = self.tabRect(index)
        self.editor.setFixedSize(rect.size())
        self.editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self.editor.setText(self.tabText(index))
        if not self.editor.isVisible():
            self.editor.show()


    def handleEditingFinished(self):
        index = self.currentIndex()
        if index >= 0:
            self.editor.hide()
            self.setTabText(index, self.editor.text())
