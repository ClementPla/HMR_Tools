import pandas as pd
# from PySide2.QtCore import QAbstractTableModel, Qt

from pyqtgraph.Qt import QtCore


def read_pandas_from_pickle(filepath):
    return pd.read_pickle(filepath)


def read_pandas_from_csv(filepath):
    return pd.read_csv(filepath)


class PandasModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def get_path_data(self, index):
        return self._data.iloc[index, -1]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None
