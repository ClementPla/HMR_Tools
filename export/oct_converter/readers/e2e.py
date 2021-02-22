import numpy as np
from construct import PaddedString, Int16un, Struct, Int32sn, Int32un, Array, Int8un
from ..image_types import OCTVolumeWithMetaData, FundusImageWithMetaData
import datetime


class E2E(object):
    """ Class for extracting data from Heidelberg's .e2e file format.

        Notes:
            Mostly based on description of .e2e file format here:
            https://bitbucket.org/uocte/uocte/wiki/Heidelberg%20File%20Format.

        Attributes:
            filepath (str): Path to .img file for reading.
            header_structure (obj:Struct): Defines structure of volume's header.
            main_directory_structure (obj:Struct): Defines structure of volume's main directory.
            sub_directory_structure (obj:Struct): Defines structure of each sub directory in the volume.
            chunk_structure (obj:Struct): Defines structure of each data chunk.
            image_structure (obj:Struct): Defines structure of image header.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.header_structure = Struct(
            'magic' / PaddedString(12, 'ascii'),
            'version' / Int32un,
            'unknown' / Array(10, Int16un)
        )
        self.main_directory_structure = Struct(
            'magic' / PaddedString(12, 'ascii'),
            'version' / Int32un,
            'unknown' / Array(10, Int16un),
            'num_entries' / Int32un,
            'current' / Int32un,
            'prev' / Int32un,
            'unknown3' / Int32un,
        )
        self.sub_directory_structure = Struct(
            'pos' / Int32un,
            'start' / Int32un,
            'size' / Int32un,
            'unknown' / Int32un,
            'patient_id' / Int32un,
            'study_id' / Int32un,
            'series_id' / Int32un,
            'slice_id' / Int32sn,
            'unknown2' / Int16un,
            'unknown3' / Int16un,
            'type' / Int32un,
            'unknown4' / Int32un,
        )
        self.chunk_structure = Struct(
            'magic' / PaddedString(12, 'ascii'),
            'unknown' / Int32un,
            'unknown2' / Int32un,
            'pos' / Int32un,
            'size' / Int32un,
            'unknown3' / Int32un,
            'patient_id' / Int32un,
            'study_id' / Int32un,
            'series_id' / Int32un,
            'slice_id' / Int32sn,
            'ind' / Int16un,
            'unknown4' / Int16un,
            'type' / Int32un,
            'unknown5' / Int32un,
        )
        self.image_structure = Struct(
            'size' / Int32un,
            'type' / Int32un,
            'unknown' / Int32un,
            'width' / Int32un,
            'height' / Int32un,
        )
        self.patient_structure = Struct(
            'name' / PaddedString(31, 'ascii'),
            'surname' / PaddedString(66, 'ascii'),
            'birthdate' / Int32un,
            'sex' / PaddedString(1, 'ascii')
        )
        self.laterality_structure = Struct(
            'unknown' / Array(14, Int8un),
            'laterality' / PaddedString(1, 'ascii')
        )

    def read_oct_volume(self):
        """ Reads OCT data.

            Returns:
                obj:OCTVolumeWithMetaData
        """
        with open(self.filepath, 'rb') as f:
            raw = f.read(36)
            header = self.header_structure.parse(raw)

            raw = f.read(52)
            main_directory = self.main_directory_structure.parse(raw)

            # traverse list of main directories in first pass
            directory_stack = []

            current = main_directory.current
            while current != 0:
                directory_stack.append(current)
                f.seek(current)
                raw = f.read(52)
                directory_chunk = self.main_directory_structure.parse(raw)
                current = directory_chunk.prev

            # traverse in second pass and  get all subdirectories
            chunk_stack = []
            volume_dict = {}
            for position in directory_stack:
                f.seek(position)
                raw = f.read(52)
                directory_chunk = self.main_directory_structure.parse(raw)

                for ii in range(directory_chunk.num_entries):
                    raw = f.read(44)
                    chunk = self.sub_directory_structure.parse(raw)
                    volume_string = '{}_{}_{}'.format(chunk.patient_id, chunk.study_id, chunk.series_id)
                    if volume_string not in volume_dict.keys():
                        volume_dict[volume_string] = chunk.slice_id / 2
                    elif chunk.slice_id / 2 > volume_dict[volume_string]:
                        volume_dict[volume_string] = chunk.slice_id / 2

                    if chunk.start > chunk.pos:
                        chunk_stack.append([chunk.start, chunk.size])

            # initalise dict to hold all the image volumes
            volume_array_dict = {}
            laterality_array_dict = {}
            image_array_dict = {}
            patient_array_data = {}
            for volume, num_slices in volume_dict.items():
                if num_slices > 0:
                    volume_array_dict[volume] = [0] * int(num_slices)

            # traverse all chunks and extract slices
            for start, pos in chunk_stack:
                f.seek(start)
                raw = f.read(60)
                chunk = self.chunk_structure.parse(raw)
                volume_string = '{}_{}_{}'.format(chunk.patient_id, chunk.study_id, chunk.series_id)
                patient_array_data[volume_string] = {'name':'', 'surname':'','birthdate':''}
                if chunk.type == 9:
                    """
                    Patient data
                
                    Birthdate conversion is not working
                    """
                    raw = f.read(102)
                    patient_data = self.patient_structure.parse(raw)
                    julian_date = str((patient_data.birthdate//64)-14558805)
                    # centuryArray = ['19', '20', '21']
                    # d = centuryArray[int(julian_date[:1])] + julian_date[1:]
                    d = julian_date
                    patient_array_data[volume_string] = {'name':patient_data.name,
                                                         'surname':patient_data.surname,
                                                         'birthdate': d}
                if chunk.type == 11:
                    '''
                    Laterality
                    '''
                    if volume_string not in laterality_array_dict:
                        raw = f.read(15)
                        laterality = self.laterality_structure.parse(raw)
                        laterality_array_dict[volume_string] = laterality.laterality

                if chunk.type == 1073741824:  # image data
                    '''
                    2D data
                    '''
                    raw = f.read(20)
                    image_data = self.image_structure.parse(raw)

                    if chunk.ind == 0:  # fundus data
                        if volume_string not in image_array_dict:
                            all_bits = f.read(image_data.height * image_data.width)
                            img = np.frombuffer(all_bits, dtype=np.uint8)
                            img = img.reshape(image_data.height, image_data.width)
                            image_array_dict[volume_string] = img

                    elif chunk.ind == 1:  # oct
                        '''
                        B-scan data
                        '''
                        all_bits = [np.frombuffer(f.read(2), dtype=np.uint8) for i in range(image_data.height * image_data.width)]
                        raw_volume = numpy_read_custom_float(np.asarray(all_bits))
                        image = np.array(raw_volume).reshape(image_data.width, image_data.height)
                        image = 256 * pow(image, 1.0 / 2.4)

                        if volume_string in volume_array_dict.keys():
                            volume_array_dict[volume_string][int(chunk.slice_id / 2) - 1] = image
                        else:
                            print('Failed to save image data for volume {}'.format(volume_string))

            oct_data = []
            for key, volume in volume_array_dict.items():
                oct_data.append(OCTVolumeWithMetaData(volume=volume,
                                                      patient_id=key,
                                                      laterality=laterality_array_dict[key],
                                                      patient_name=patient_array_data[key]['name'],
                                                      patient_surname=patient_array_data[key]['surname']))

            for key, img in image_array_dict.items():
                oct_data.append(FundusImageWithMetaData(image=img, patient_id=key,
                                                        laterality=laterality_array_dict[key]))

        return oct_data

    def read_custom_float(self, bytes):
        """ Implementation of bespoke float type used in .e2e files.

        Notes:
            Custom float is a floating point type with no sign, 6-bit exponent, and 10-bit mantissa.

        Args:
            bytes (str): The two bytes.

        Returns:
            float
        """
        power = pow(2, 10)
        # convert two bytes to 16-bit binary representation
        print(bytes[0])
        bits = bin(bytes[0])[2:].zfill(8)[::-1] + bin(bytes[1])[2:].zfill(8)[::-1]

        # get mantissa and exponent
        mantissa = bits[:10]
        exponent = bits[10:]

        # convert to decimal representations
        mantissa_sum = 1 + int(mantissa, 2) / power
        exponent_sum = int(exponent[::-1], 2) - 63
        decimal_value = mantissa_sum * pow(2, exponent_sum)
        return decimal_value


def read_custom_float(bytes):
    """ Implementation of bespoke float type used in .e2e files.

    Notes:
        Custom float is a floating point type with no sign, 6-bit exponent, and 10-bit mantissa.

    Args:
        bytes (str): The two bytes.

    Returns:
        float
    """
    power = pow(2, 10)
    # convert two bytes to 16-bit binary representation
    bits = bin(bytes[0])[2:].zfill(8)[::-1] + bin(bytes[1])[2:].zfill(8)[::-1]
    # get mantissa and exponent
    mantissa = bits[:10]
    exponent = bits[10:]
    # convert to decimal representations
    mantissa_sum = 1 + int(mantissa, 2) / power
    exponent_sum = int(exponent[::-1], 2) - 63
    decimal_value = mantissa_sum * pow(2, exponent_sum)
    return decimal_value


def numpy_read_custom_float(bytes_array):
    bits_f, bits_s = np.unpackbits(bytes_array[:, 0]).astype(bool), np.unpackbits(bytes_array[:, 1]).astype(bool)
    bits_f, bits_s = bits_f.reshape((bytes_array.shape[0], 8))[:, ::-1], bits_s.reshape((bytes_array.shape[0], 8))[:, ::-1]

    bits = np.hstack((bits_f, bits_s))
    mantissa = bits[:, :10]
    exponent = bits[:, 10:][:, ::-1]
    exponent = np.hstack((np.zeros((exponent.shape[0], 2), dtype=np.bool), exponent))
    power = pow(2, 10)
    mantissa = np.hstack((np.zeros((mantissa.shape[0], 6), dtype=np.bool), mantissa))
    mantissa_sum = 1 + np.packbits(mantissa.reshape(-1, 2, 8)[:, ::-1]).view(np.uint16) / power
    exponent_sum = (np.packbits(exponent, -1).astype(np.float) - 63).squeeze()
    return mantissa_sum.astype(np.float) * np.power(2, exponent_sum)
