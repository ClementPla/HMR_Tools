import os

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.Qt import QtWidgets as qtw


class CenteredWidget(qtw.QFrame):
    def __init__(self, parent):
        super(CenteredWidget, self).__init__()
        self.parent = parent
        self.clickable_margin_size = 25

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == QtCore.Qt.MiddleButton:
            localPos = e.localPos()
            size = QtCore.QPoint(self.size().width(), self.size().height())
            relative_pos = size - localPos

            if localPos.x() < self.clickable_margin_size:
                self.parent.insert_in_vertical_splitter(0, localPos.x())
            elif relative_pos.x() < self.clickable_margin_size:
                self.parent.insert_in_vertical_splitter(self.parent.verticalSplitter.count() - 1, localPos.x())
            elif localPos.y() < self.clickable_margin_size:
                self.parent.insert_in_horizontal_splitter(0, localPos.y())
            elif relative_pos.y() < self.clickable_margin_size:
                self.parent.insert_in_horizontal_splitter(self.parent.horizontalSplitter.count() - 1, localPos.y())


class SplitterHandle(qtw.QSplitterHandle):
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super(SplitterHandle, self).mousePressEvent(e)


class Splitter(qtw.QSplitter):
    def createHandle(self) -> 'QSplitterHandle':
        return SplitterHandle(self.orientation(), self)


class SplittableWidget(qtw.QFrame):
    def __init__(self):
        super(SplittableWidget, self).__init__()
        self.center = CenteredWidget(self)
        self.horizontalSplitter = Splitter()
        self.verticalSplitter = Splitter()
        self.verticalSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.in_destruct_mode = False
        self.horizontalSplitter.addWidget(self.verticalSplitter)
        self.horizontalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.verticalSplitter.addWidget(self.center)
        layout = qtw.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self.horizontalSplitter)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == QtCore.Qt.LeftButton:
            pass
        self.in_destruct_mode = False
        super(SplittableWidget, self).mousePressEvent(e)

    def insert_in_vertical_splitter(self, index, pos):
        self.verticalSplitter.insertWidget(index + 1, SplittableWidget())
        self.verticalSplitter.moveSplitter(pos, index + 1)

    def insert_in_horizontal_splitter(self, index, pos):
        self.horizontalSplitter.insertWidget(index + 1, SplittableWidget())
        self.horizontalSplitter.moveSplitter(pos, index + 1)


class MainWindow(qtw.QMainWindow):
    def __init__(self, size=(1980 * .9, 1020 * .9), title='HMR Data Viewer'):
        super(MainWindow, self).__init__()
        self.resize(*size)
        self.setWindowTitle(title)

        self.status = self.statusBar()
        self.status.showMessage("App successfully launched")
        self.progressBar = qtw.QProgressBar(self)
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
        exit_action = qtw.QAction("Exit", self)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        open_action = qtw.QAction("Open", self)
        open_action.setShortcut(QtGui.QKeySequence.Open)
        open_action.triggered.connect(self.open_file)

        self.file_menu.addAction(open_action)
        self.file_menu.addAction(exit_action)

    def open_file(self):
        fileName, filter_param = qtw.QFileDialog.getOpenFileName(self, "Open pandas file", "../../", filter='*.pkl')
        if os.path.exists(fileName):
            self.load_pandas_file(fileName)


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication([])
    stylesheet = open('../ui/stylesheet.sc', 'r').read()
    app.setStyleSheet(stylesheet)
    win = MainWindow()
    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
