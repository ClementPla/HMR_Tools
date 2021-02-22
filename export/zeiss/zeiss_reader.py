import os
import numpy as np
import cv2


class ZeissDecoder:
    def __init__(self, folder):
        self.folder = folder
        self.data = {'fundus_zeiss': None,
                     'structural_oct_3mmx3mm': None,
                     'structural_oct_6mmx6mm': None,
                     'angio_oct_3mmx3mm': None,
                     'angio_oct_6mmx6mm': None,
                     'iris': None}

        self.list_files = os.listdir(folder)
        self.eye = 'OS/' if '_OS_' in self.list_files[0] else 'OD/'

    def read_file(self, file, reshape):
        return np.fromfile(file, dtype=np.uint8).reshape(reshape)

    def decode(self):
        for f in self.list_files:
            file = os.path.join(self.folder, f)
            if f.endswith('_cube_z.img'):
                if '3mmx3mm' in f:
                    self.data['structural_oct_3mmx3mm'] = self.read_file(file, (-1, 1536, 300))[:, ::-1, :]
                if '6mmx6mm' in f:
                    self.data['structural_oct_6mmx6mm'] = self.read_file(file, (-1, 1536, 500))[:, ::-1, :]

            if f.endswith('_FlowCube_z.img'):
                if '3mmx3mm' in f:
                    self.data['angio_oct_3mmx3mm'] = self.read_file(file, (-1, 1536, 300))[:, ::-1, :]
                if '6mmx6mm' in f:
                    self.data['angio_oct_6mmx6mm'] = self.read_file(file, (-1, 1536, 500))[:, ::-1, :]

            if f.endswith('_iris.bin'):
                self.data['iris'] = self.read_file(file, (480, 640))

            if f.endswith('_lslo.bin'):
                self.data['fundus_zeiss'] = self.read_file(file, (512, 664))

    def write_array(self, folder, array):
        array = np.squeeze(array)
        if not os.path.exists(folder):
            os.makedirs(folder)
        if array.ndim == 2:
            cv2.imwrite(os.path.join(folder, 'data.png'), array)
        else:
            for i, bscan in enumerate(array):
                cv2.imwrite(os.path.join(folder, 'data_%i.png' % i), bscan)

    def save(self, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for key in self.data:
            array = self.data[key]
            if array is not None:
                self.write_array(os.path.join(output_folder, self.eye, key), array)
