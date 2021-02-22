from pyqtgraph.Qt import QtCore

from model.model import Model


class Controller(QtCore.QObject):
    updated_pandas_model = QtCore.Signal()
    updated_active_data = QtCore.Signal()
    updated_active_slice = QtCore.Signal()

    def __init__(self, client):
        super(Controller, self).__init__()
        self.client = client
        self.model = Model(self)

    def update_pandas_model(self):
        self.updated_pandas_model.emit()

    def update_progress_bar(self, value):
        self.client.progressBar.setValue(value)

    def update_active_data(self):
        self.updated_active_data.emit()

    def update_active_slice(self):
        self.updated_active_slice.emit()
