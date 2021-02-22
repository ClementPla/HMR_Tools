from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtWidgets


class LabelToolbar(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(LabelToolbar, self).__init__(*args, *kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        add_button = QtWidgets.QPushButton('Add')
        delete_button = QtWidgets.QPushButton('Delete')
        self.layout.addWidget(add_button)
        self.layout.addWidget(delete_button)
        self.setLayout(self.layout)


class LabelListWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(LabelListWidget, self).__init__(*args, *kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.listLabels = QtGui.QListView()
        self.layout.addWidget(self.listLabels)
        self.toolBar = LabelToolbar()
        self.layout.addWidget(self.toolBar)
