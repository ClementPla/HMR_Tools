import os


class Dicom(object):
    def __init__(self, filepath):
        """
        :param filepath: Should either be a folder containing multiples sub-volume or a single DCOM
        """
        self.filepath = filepath

    def read_oct_volume(self):
        lstFilesDCM = []  # create an empty list
        for dirName, subdirList, fileList in os.walk(PathDicom):
            for filename in fileList:
                if ".dcm" in filename.lower():  # check whether the file's DICOM
                    lstFilesDCM.append(os.path.join(dirName, filename))

