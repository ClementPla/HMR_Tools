import os
from pyqtgraph.Qt import QtCore, QtGui
import model.pandas_model as pm
from model.images import read_images_to_np, resize_images


class Model(QtCore.QObject):
    def __init__(self, controller):
        super(Model, self).__init__()
        self.c = controller
        self.pandas_model = None
        self.active_data = None
        self.active_slice = None
        self.root_folder = '/media/clement/SAMSUNG/AMD/data/patients'


    def load_pandas_model(self, filepath):
        if os.path.exists(filepath):
            if filepath.endswith('.pkl'):
                dataframe = pm.read_pandas_from_pickle(filepath)
            elif filepath.endswith('.csv'):
                dataframe = pm.read_pandas_from_csv(filepath)
            self.pandas_model = pm.PandasModel(dataframe)
            self.c.update_pandas_model()

    def reshape_active_data(self, new_h, new_w):
        data = self.active_data
        z, h, w, c = data.shape
        if new_h != h or new_w != w:
            self.c.client.status.showMessage("Reshaping data")
            self.c.client.progressBar.setVisible(True)
            data = resize_images(data, new_h, new_w, progress_function=self.c.update_progress_bar)
            self.active_data = data
            self.c.client.status.showMessage("Data resized")
            self.c.client.progressBar.setVisible(False)
            self.c.update_active_data()

    def read_folder(self, folderpath):
        pass

    def load_data(self, filepath):
        self.c.client.status.showMessage("Loading data")
        filepath = os.path.join(self.root_folder, filepath)
        if os.path.exists(filepath):
            self.c.client.progressBar.setVisible(True)
            data = read_images_to_np(filepath, progress_function=self.c.update_progress_bar)
            self.active_data = data
            self.c.client.status.showMessage("Data loaded")
            self.c.client.progressBar.setVisible(False)
            self.c.update_active_data()

        else:
            self.c.client.status.showMessage("Could not find the file. Is your datapoint mounted?")
