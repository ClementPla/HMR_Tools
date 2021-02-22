import os
import imageio
import cv2
import matplotlib.pyplot as plt
import numpy as np

VIDEO_TYPES = ['.avi', '.mp4', ]
IMAGE_TYPES = ['.png', '.bmp', '.tiff', '.jpg', '.jpeg']


class FundusImageWithMetaData(object):
    """ Class to hold the fundus image and any related metadata, and enable saving.

    Attributes:
        image (np.array): Fundus image.
        laterality (str): Left or right eye.
        patient_id (str): Patient ID.
        DOB (str): Patient date of birth.
    """

    def __init__(self, image, laterality=None, patient_id=None, patient_dob=None,
                 patient_name='', patient_surname=''):
        self.image = image
        self.laterality = laterality
        self.patient_id = patient_id
        self.DOB = patient_dob
        self.patient_name = patient_name
        self.patient_surname = patient_surname
        self.type = 'fundus'

    def save(self, filepath):
        """Saves fundus image.

        Args:
            filepath (str): Location to save volume to. Extension must be in IMAGE_TYPES.
        """
        extension = os.path.splitext(filepath)[1]
        if extension.lower() in IMAGE_TYPES:
            cv2.imwrite(filepath, self.image)
        elif extension.lower() == '.npy':
            np.save(filepath, self.image)
        else:
            raise NotImplementedError('Saving with file extension {} not supported'.format(extension))

    def peek(self, filepath=None):
        """ Plots a montage of the OCT volume. Optionally saves the plot if a filepath is provided.

        Args:
            rows (int) : Number of rows in the plot.
            cols (int) : Number of columns in the plot.
            filepath (str): Location to save montage to.
        """
        images = 1
        x_size = self.image.shape[0]
        y_size = self.image.shape[1]
        ratio = y_size / x_size
        plt.figure(figsize=(12*ratio,12))
        for i in range(images):
            plt.imshow(self.image, cmap='gray')
            plt.axis('off')
            plt.title('Patient '+self.patient_name.upper()+' '+self.patient_surname)

        if filepath is not None:
            plt.savefig(filepath)
        else:
            plt.show()
