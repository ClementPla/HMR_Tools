import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.Qt import QtWidgets as qtw

from controller import Controller
from core.view import DrawableImage
from model import pandas_model as pm
from model.images import *
from ui.components import SplittableWidget
from ui.label_viewer import LabelListWidget


class MainWindow(qtw.QMainWindow):
    def __init__(self, size=(1200, 1200), title='HMR Data Viewer'):
        super(MainWindow, self).__init__()
        controller = Controller(self)
        self.c = controller
        self.resize(*size)
        self.setWindowTitle(title)
        self.load_thread = QtCore.QThread()

        self.status = self.statusBar()
        self.status.showMessage("App successfully launched")
        self.progressBar = qtw.QProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.status.addPermanentWidget(self.progressBar)
        self.create_menu()
        mainWidget = SplittableWidget(self.c)
        self.setCentralWidget(mainWidget)

        sp1 = mainWidget.insert_in_vertical_splitter(0, 500.0)
        # sp2 = sp1.insert_in_horizontal_splitter(0, 500)
        # sp3 = sp2.insert_in_horizontal_splitter(0, 100)
        #
        # sp2 = mainWidget.insert_in_vertical_splitter(0, 300)
        # sp3 = sp1.insert_in_horizontal_splitter(0, 400)

        sp1.center.set_current_index(2)
        # sp2.center.set_current_index(3)
        # sp3.center.set_current_index(4)

    def create_menu(self):
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")


        pkl_open_action = self.file_menu.addAction("Open pandas file (pkl, csv)")
        read_folder_action = self.file_menu.addAction("Read folders")
        exit_action = self.file_menu.addAction("Exit")

        # Exit QAction
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # Open pkl action
        pkl_open_action.setShortcut(QtGui.QKeySequence.Open)
        pkl_open_action.triggered.connect(self.open_file)

        # Read folder action
        read_folder_action.triggered.connect(self.read_folder)

    def open_file(self):
        filepath, filter_param = qtw.QFileDialog.getOpenFileName(self, "Open pandas file", "../", filter='*.pkl;; *.csv')
        self.c.model.load_pandas_model(filepath)

    def read_folder(self):
        folderpath = qtw.QFileDialog.getExistingDirectory(self, "Open pandas file", "../")
        self.c.model.read_folder(folderpath)


class WindowApp(qtw.QMainWindow):
    def __init__(self, size=(1200, 1200), title='HMR Data Viewer'):
        super(WindowApp, self).__init__()
        self.resize(*size)
        self.setWindowTitle(title)
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = qtw.QAction("Exit", self)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # Open action
        open_action = qtw.QAction("Open", self)
        open_action.setShortcut(QtGui.QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        self.status = self.statusBar()
        self.status.showMessage("App successfully launched")
        self.progressBar = qtw.QProgressBar(self)
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)

        self.status.addPermanentWidget(self.progressBar)
        self.file_menu.addAction(open_action)
        self.file_menu.addAction(exit_action)

        cw = qtw.QWidget(self)
        grid_layout = QtGui.QGridLayout()

        self.setCentralWidget(cw)
        cw.setLayout(grid_layout)
        self.horizontalQSplitter = qtw.QSplitter()
        grid_layout.addWidget(self.horizontalQSplitter, 0, 0)
        self.horizontalQSplitter.setOrientation(QtCore.Qt.Vertical)
        self.horizontalQSplitter.setSizes([sys.maxsize, sys.maxsize])

        top_splitter = qtw.QSplitter(self.horizontalQSplitter)
        down_splitter = qtw.QSplitter(self.horizontalQSplitter)
        down_splitter.setSizes([sys.maxsize, sys.maxsize])
        top_splitter.setSizes([sys.maxsize, sys.maxsize])

        self.pandasTableView = qtw.QTableView()
        self.w = gl.GLViewWidget()
        self.imv1 = DrawableImage()
        self.imv2 = pg.ImageView()

        down_splitter.addWidget(self.imv1)
        down_splitter.addWidget(self.imv2)
        top_splitter.addWidget(self.pandasTableView)
        top_splitter.addWidget(self.w)
        top_splitter.addWidget(LabelListWidget())

        self.root_folder = '/media/clement/SAMSUNG/AMD/data/patients/'
        g = gl.GLGridItem()
        g.scale(1, 1, 1)
        self.w.addItem(g)

        self.roi = pg.LineSegmentROI([[10, 64], [120, 64]], pen='r')
        self.imv1.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.update_roi)

        self.imv1.setHistogramRange(0, 1)
        self.imv1.setLevels(0, 1)
        self.v = None
        # w.addItem(self.v)
        ax = gl.GLAxisItem()
        self.w.addItem(ax)
        # self.update_roi()
        self.pandasTableView.doubleClicked.connect(self.request_loading_data)
        # self.load_data('trash/')

    def update_roi(self):
        d2 = self.roi.getArrayRegion(self.data, self.imv1.imageItem, axes=(1, 2))
        self.imv2.setImage(d2)

    def set_data(self, data):
        if data.ndim == 3:
            # data = data.transpose((0, 1, 1))
            data = np.expand_dims(data, 3)
            data = np.repeat(data, 4, axis=3)
        self.data = data.transpose((0, 2, 1, 3))
        self.imv1.setImage((self.data / 255.))  # Format is column-major for some reason
        if self.v is None:
            self.v = gl.GLVolumeItem(data)
            self.v.translate(-50, -250, -1536 // 2)
            self.w.addItem(self.v)
            self.v.setData(data)
        else:
            self.v.setData(data)

    def open_file(self):
        fileName, filter_param = qtw.QFileDialog.getOpenFileName(self, "Open pandas file", "../../", filter='*.pkl')

        if os.path.exists(fileName):
            self.load_pandas_file(fileName)

    def load_pandas_file(self, filepath):
        dataframe = pm.read_pandas_from_pickle(filepath)
        self.model = pm.PandasModel(dataframe)
        self.pandasTableView.setModel(self.model)

    def update_progress_bar(self, value):
        self.progressBar.setValue(value)

    def request_loading_data(self, item):

        self.load_data(self.model.get_path_data(item.row()))

    def load_data(self, path):
        self.status.showMessage("Loading data")
        self.progressBar.setVisible(True)

        full_path = os.path.join(self.root_folder, path)

        data = read_images_to_np(full_path, progress_function=self.update_progress_bar)
        self.status.showMessage("Data loaded")
        self.progressBar.setVisible(False)

        self.set_data(data)
        self.update_roi()
        self.status.showMessage("Done!")


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    app = QtGui.QApplication([])
    win = WindowApp()
    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
