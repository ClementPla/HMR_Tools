import sys

from pyqtgraph.Qt import QtCore, QtGui

from ui.window import MainWindow


class Launcher(QtCore.QObject):
    def launch(self):
        app = QtGui.QApplication([])
        stylesheet = open('ui/stylesheet.sc', 'r').read()
        app.setStyleSheet(stylesheet)
        win = MainWindow()

        win.show()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
