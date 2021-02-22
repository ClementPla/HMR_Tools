import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.Qt import QtWidgets as QtW


class Panel(QtW.QFrame):
    def __init__(self, parent_splitter):
        super(Panel, self).__init__()
        self.parent = parent_splitter
        self.clickable_margin_size = 50
        self.menu_bar = QtW.QComboBox()
        vbox = QtW.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        vbox.setContentsMargins(0, 0, 0, 0)
        hbox = QtW.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        hbox.addWidget(self.menu_bar)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        vbox.addLayout(hbox)
        self.stacked_layout = QtW.QStackedLayout()
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(self.stacked_layout)

        self.menu_bar.currentIndexChanged.connect(self.stacked_layout.setCurrentIndex)

        self.setLayout(vbox)

    def add_component(self, widget, icon, name):
        self.stacked_layout.addWidget(widget)
        self.menu_bar.addItem(icon, name)

    def set_current_index(self, index):
        self.menu_bar.setCurrentIndex(index)

    def current_index(self):
        return self.menu_bar.currentIndex()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == QtCore.Qt.MiddleButton or e.button() == QtCore.Qt.RightButton:
            localPos = e.localPos()
            size = QtCore.QPoint(self.size().width(), self.size().height())
            relative_pos = size - localPos
            if localPos.x() < self.clickable_margin_size:
                self.parent.insert_in_horizontal_splitter(0, localPos.y())
            elif relative_pos.x() < self.clickable_margin_size:
                self.parent.insert_in_horizontal_splitter(self.parent.horizontalSplitter.count() - 1, localPos.y())
            elif localPos.y() < self.clickable_margin_size:
                self.parent.insert_in_vertical_splitter(0, localPos.x())
            elif relative_pos.y() < self.clickable_margin_size:
                self.parent.insert_in_vertical_splitter(self.parent.verticalSplitter.count() - 1, localPos.x())
        super(Panel, self).mousePressEvent(e)


class ImageProperties(QtW.QFrame):
    def __init__(self, controller):
        self.c = controller
        super(ImageProperties, self).__init__()

        layout = QtW.QGridLayout()
        text1 = QtW.QLabel('Width')
        text2 = QtW.QLabel('Height')

        text1.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        text2.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)

        self.widthEdit = QtW.QSpinBox()
        self.widthEdit.setMinimum(0)
        self.widthEdit.setMaximum(5000)

        self.heightEdit = QtW.QSpinBox()
        self.heightEdit.setMinimum(0)
        self.heightEdit.setMaximum(5000)

        layout.setSpacing(0)
        text1.setAlignment(QtCore.Qt.AlignCenter)
        text2.setAlignment(QtCore.Qt.AlignCenter)
        # text1.setMaximumHeight(10)
        layout.addWidget(text1, 0, 0)
        layout.addWidget(self.widthEdit, 1, 0)
        layout.addWidget(text2, 0, 1)
        layout.addWidget(self.heightEdit, 1, 1)
        self.c.updated_active_data.connect(self.update_data_shape)
        self.widthEdit.editingFinished.connect(self.set_data_shape)
        self.heightEdit.editingFinished.connect(self.set_data_shape)
        self.update_data_shape()

        self.setLayout(layout)

        self.setMinimumHeight(10)

    def update_data_shape(self):
        data = self.c.model.active_data
        if data is not None:
            z, h, w, c = data.shape
            self.widthEdit.blockSignals(True)
            self.heightEdit.blockSignals(True)
            self.widthEdit.setValue(h)
            self.heightEdit.setValue(w)
            self.widthEdit.blockSignals(False)
            self.heightEdit.blockSignals(False)

    def set_data_shape(self):
        h, w = self.widthEdit.value(), self.heightEdit.value()
        if self.c.model.active_data is not None:
            self.c.model.reshape_active_data(h, w)


class ElementsPanel(Panel):
    def __init__(self, parent_splitter):
        super(ElementsPanel, self).__init__(parent_splitter)
        self.c = parent_splitter.c
        self.tableView = QtW.QTableView()
        self.glView = gl.GLViewWidget()
        self.glView.opts['azimuth'] = 90
        self.glView.opts['elevation'] = 90
        self.glView.pan(0, 0, -5)
        self.regularView = pg.ImageView()
        self.regularView.playRate = 25
        self.sliceView = pg.ImageView()

        self.add_component(self.tableView, QtGui.QIcon('ui/icons/database.png'), 'Database')
        self.add_component(self.glView, QtGui.QIcon('ui/icons/3d_view.png'), '3D view')
        self.add_component(self.regularView, QtGui.QIcon('ui/icons/2d_view.png'), '2D view')
        self.add_component(self.sliceView, QtGui.QIcon('ui/icons/slicer.png'), 'Slice view')
        self.add_component(ImageProperties(self.c), QtGui.QIcon('ui/icons/properties.png'), 'Data properties')


        self.v = gl.GLVolumeItem(None)
        self.glView.addItem(self.v)
        self.roi = pg.LineSegmentROI([[10, 64], [120, 64]], pen='r')
        self.roi.sigRegionChanged.connect(self.update_roi)

        self.regularView.addItem(self.roi)
        self.regularView.setHistogramRange(0, 255)
        self.regularView.setLevels(0, 255)

        self.sliceView.setHistogramRange(0, 255)
        self.sliceView.setLevels(0, 255)

        self.tableView.doubleClicked.connect(self.request_loading_data)
        self.c.updated_pandas_model.connect(self.set_table_model)
        self.c.updated_active_data.connect(self.set_data)
        self.c.updated_active_slice.connect(self.set_slice)
        self.set_table_model()
        self.set_data()
        self.set_slice()
        self.menu_bar.currentIndexChanged.connect(self.is_3d_data)

    def is_3d_data(self):
        if self.current_index() == 1:
            self.set_3d_data()

    def update_roi(self):
        data = self.c.model.active_data
        if data is not None:
            self.c.model.active_slice = self.roi.getArrayRegion(data, self.regularView.imageItem, axes=(1, 2))
            self.c.update_active_slice()

    def set_slice(self):
        data = self.c.model.active_slice
        if data is not None:
            self.sliceView.setImage(data)

    def set_table_model(self):
        if self.c.model.pandas_model is not None:
            self.tableView.setModel(self.c.model.pandas_model)

    def request_loading_data(self, item):
        self.c.model.load_data(self.c.model.pandas_model.get_path_data(item.row()))

    def set_data(self):

        data = self.c.model.active_data
        if data is not None:
            self.regularView.setImage(data)  # Format is column-major for some reason
            if self.current_index() == 1:
                self.set_3d_data()
            self.update_roi()

    def set_3d_data(self):
        data = self.c.model.active_data
        if data is not None:
            self.v.resetTransform()
            # data = np.transpose(data, (1, 2, 0, 3))
            data[:, :, :, 3] = data[:, :, :, 0]
            self.v.setData(data)
            max_size = max(data.shape[:2])
            self.v.scale(5 / max_size, 5 / max_size, -5 / data.shape[2])
            self.v.translate(-2.5, -2.5, -5)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super(ElementsPanel, self).mousePressEvent(e)


class SplitterHandle(QtW.QSplitterHandle):
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super(SplitterHandle, self).mousePressEvent(e)


class Splitter(QtW.QSplitter):
    def createHandle(self) -> 'QSplitterHandle':
        return SplitterHandle(self.orientation(), self)


class SplittableWidget(QtW.QFrame):
    def __init__(self, controller):
        super(SplittableWidget, self).__init__()
        self.c = controller
        self.center = ElementsPanel(self)
        self.horizontalSplitter = Splitter()
        self.verticalSplitter = Splitter()

        self.verticalSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSplitter.addWidget(self.verticalSplitter)
        self.horizontalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.verticalSplitter.addWidget(self.center)
        layout = QtW.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self.horizontalSplitter)

    def insert_in_vertical_splitter(self, index, pos):
        splittable_widget = SplittableWidget(self.c)
        self.verticalSplitter.insertWidget(index + 1, splittable_widget)
        self.verticalSplitter.moveSplitter(pos, index + 1)
        return splittable_widget

    def insert_in_horizontal_splitter(self, index, pos):
        splittable_widget = SplittableWidget(self.c)
        self.horizontalSplitter.insertWidget(index + 1, splittable_widget)
        self.horizontalSplitter.moveSplitter(pos, index + 1)
        return splittable_widget


class MainWindow(QtW.QMainWindow):
    def __init__(self, size=(1980 * .9, 1020 * .9), title='HMR Data Viewer'):
        super(MainWindow, self).__init__()
        self.resize(*size)
        self.setWindowTitle(title)
        self.status = self.statusBar()
        self.status.showMessage("App successfully launched")
        self.progressBar = QtW.QProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.status.addPermanentWidget(self.progressBar)
        self.create_menu()

        cw = SplittableWidget()
        self.setCentralWidget(cw)

        cw.setVisible(True)

    def create_menu(self):
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        # Exit QAction
        exit_action = QtW.QAction("Exit", self)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication([])
    stylesheet = open('stylesheet.sc', 'r').read()
    app.setStyleSheet(stylesheet)
    win = MainWindow()
    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
