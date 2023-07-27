import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import QListWidgetItem
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QColor

from spectralEIT.bin.default_config import DefaultClass, COLOUR_MAP

import spectralEIT.bin.string_manipulation as stringManipu


class AxisItem(pg.AxisItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        black_pen_axis = pg.mkPen(0,0,0, width=2)
        black_pen_text = pg.mkPen(0,0,0, width=3)
        # black_pen_tick = pg.mkPen(0,0,0, width=2)
        self.setPen(black_pen_axis)
        self.setTextPen(black_pen_text)
        # self.setTickPen(black_pen_tick)

        tick_font = QFont("Helvetica", 10, QFont.Bold)
        self.setStyle(tickTextOffset=10, tickFont=tick_font)


class PyPlotWidget(pg.PlotWidget, DefaultClass):

    updatePlotItem = pyqtSignal(object)

    def __init__(self, *args, **kwargs):#name: str = None,

        if "name" in kwargs:
            self.name = kwargs["name"]

        pg.PlotWidget.__init__(self,
            *args,
            axisItems={
                "bottom": AxisItem(orientation="bottom"),
                # "top": AxisItem(orientation="top"),
                "left": AxisItem(orientation="left")
                # "right": AxisItem(orientation="right")
            },
            **kwargs
        )
        DefaultClass.__init__(self, __name__)

        if "labels" in kwargs:
            labels = kwargs["labels"]
            for ax in labels.keys():
                self.setLabel(ax, *labels[ax])

        ## list of plotted items
        self.plotted = {}

        ## add legend
        self.addLegend(offset=(350, 600),labelTextColor=(0, 0, 0))

        ## redraw data if changed
        # self.updatePlotItem.connect(self.update_data)

        ## Booleans for measurement selection
        self.enable_area_selection = False
        self.enable_point_selection = False
        self.area_zoom = False

        ## Point selection helpers
        self.line_count = 0
        self.point_list = []

        self.lines_peaks_count = 0
        self.lines_experimental_count = 0
        self.lines_theoretical_count = 0

        self.selection = None
        self.tab = None

        ## start coordinate for mouse press
        self.mouse_press_start = None

        ## widget backgroundcolor
        self.setBackground("w")

        ## initiate selection overlay
        self.init_overlays()


    def init_overlays(self):
        self.overlay = pg.LinearRegionItem(
                values=(0, 0),
                movable=False,
                pen=pg.mkPen(QColor(0,0,0),width=2,style=Qt.DashLine),
                brush=pg.mkBrush(0.85)
            )
        self.overlay.setVisible(False)
        self.addItem(self.overlay)


    def remove_selection_lines(self):
        for i in range(4):
            if hasattr(self,  "line_selection_" + str(i)):
                self.removeItem(getattr(self, "line_selection_" + str(i)))


    def remove_peak_lines(self, name="peaks"):
        for i in range(getattr(self, "lines_{}_count".format(name))):
            if hasattr(self,  "lines_{}_".format(name) + str(i)):
                self.removeItem(getattr(self, "lines_{}_".format(name) + str(i)))


    def remove_lines(self):
        self.remove_peak_lines("experimental")
        self.remove_peak_lines("theoretical")
        self.remove_selection_lines()


    def add_peak_line(self, x, number=None, name="peaks"):
        setattr(self, "lines_{}_count".format(name), getattr(self, "lines_{}_count".format(name))+1)
        setattr(self, "lines_{}_{}".format(name, number), pg.InfiniteLine(x, pen=pg.mkPen(QColor(0,0,0), style=Qt.DashLine)))
        self.addItem(getattr(self, "lines_{}_{}".format(name, number)))


    def already_plotted(self, name):
        if name in self.plotted.keys():
            return True
        else:
            return False


    def get_color_num(self):
        plotted_color = [ item.color_num for item in self.plotted.values()]
        for i in range(9):
            # plotted_color = [color for item.color_num in self.plotted]
            if i not in plotted_color:
                return i


    def add_item(self, item):
        item_name = item.name()
        if self.already_plotted(item_name):
            return
        color_num = self.get_color_num()
        item.sigClicked.connect(self.window().graph_tab.set_current_plot_item)
        item.sigPlotChanged.connect(self.update)
        item.setPen(pg.mkPen(
                        COLOUR_MAP[color_num],
                        width = 3
                        )
                    )
        item.color_num = color_num
        self.plotted[item_name] = item
        self.addItem(item)

        self.window().plotted_list.add_item(item)


    def del_item(self, plot: pg.PlotDataItem, item: QListWidgetItem):
        self.removeItem(plot)
        self.plotted.pop(plot.name())

        index  = self.window().plotted_list.row(item)
        self.window().plotted_list.takeItem(index)


    def clear(self):
        for name in self.plotted.keys():
            self.del_item(name)


    def mousePressEvent(self, event):

        if self.enable_area_selection:
            if event.button() == Qt.RightButton:
                self.overlay.setVisible(False)
                self.mouse_press_start = None
                self.enable_area_selection = False
                return

            x, y = self.point_to_coords(event.pos())

            self.mouse_press_start = x, y
            self.overlay_draw(x, 0)
            self.overlay.setVisible(True)
            return
        elif self.enable_point_selection:
            x, y = self.point_to_coords(event.pos())
            self.new_x = x
        else:
            super().mousePressEvent(event)


    def mouseMoveEvent(self, event):

        x, y = self.point_to_coords(event.pos())
        if x:
            self.window().label_graph_pos_x.setText("x={}".format(stringManipu.format_float_to_scale(x, custom_precision=6, plain=True)))
            self.window().label_graph_pos_y.setText("y={}".format(stringManipu.format_float_to_scale(y, custom_precision=6, plain=True)))
        if self.enable_area_selection:
            if self.mouse_press_start is None:
                return

            x0, y0 = self.mouse_press_start

            x, y = self.point_to_coords(event.pos())
            # x = self._within_boundaries(x)
            self.overlay_draw(x0, x - x0)
            return

        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self.enable_area_selection:
            x0, y0 = self.mouse_press_start
            x1, y1 = self.point_to_coords(event.pos())

            # response = getattr(self.window().meas_tab, self.selection, None)
            # response.emit([x0, x1])
            self.tab.sigSetPoints.emit(self.selection, [x0, x1])

            self.overlay.setVisible(False)
            self.mouse_press_start = None
            self.enable_area_selection = False
            return
        if self.enable_point_selection:
            self.point_list.append(self.new_x)

            setattr(
                    self,
                    "line_selection_"+str(self.line_count),
                    pg.InfiniteLine(self.new_x, pen=pg.mkPen(QColor(0,0,0), style=Qt.DashLine))
                )
            self.addItem(getattr(self, "line_selection_"+str(self.line_count)))
            self.line_count += 1

            if len(self.point_list) >= 4:
                # response = getattr(self.window().meas_tab, self.selection, None)
                # response.emit(self.point_list)
                self.tab.sigSetPoints.emit(self.selection, self.point_list)
                self.line_count = 0
                self.point_list = []
                self.enable_point_selection = False
            return


    def overlay_draw(self, x_start, width):
        self.overlay.setRegion((x_start, x_start + width))


    def point_to_coords(self, point_frame):
        if not point_frame:
            return None, None
        point_coordinate = self.plotItem.vb.mapSceneToView(point_frame)
        return point_coordinate.x(), point_coordinate.y()


    def setLabel(self, axis, text, units=None, labelStyle={}):

        if not labelStyle:
            labelStyle = {"color": "#000000", "font-weight": "600", "font-size": "10pt"}

        self.plotItem.setLabel(axis, text=text, units=units, **labelStyle)
