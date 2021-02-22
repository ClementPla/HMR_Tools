import os
import warnings
import xml.dom.minidom
from zeiss_reader import ZeissDecoder
import tqdm


class ZeissExporter:
    def __init__(self, data_folder, xml_folder):
        self.data_root = data_folder
        self.xml_root = xml_folder
        self.xml_files = os.listdir(xml_folder)
        self.data_folders = os.listdir(data_folder)

    def extract_visit_date(self, folder):
        str_date = folder[-8:]
        year = str_date[:4]
        month = str_date[4:6]
        day = str_date[6:]
        return year+'-'+month+'-'+day

    def extract_patient_id(self, folder):
        id_patient = folder.split(' ')[0][1:]
        return id_patient

    def find_xml_per_id(self, id):
        for xml_f in self.xml_files:
            if id in xml_f:
                return xml_f
        warnings.warn('XML not found for user with id '+id, UserWarning)
    def refine_patient_id(self, patient_id):
        if patient_id[0].isdigit():
            return patient_id
        else:
            return patient_id[0]+'-'+patient_id[3:]

    def export(self, out_folder):
        for folder in tqdm.tqdm(self.data_folders):
            visit_date = self.extract_visit_date(folder)
            id_patient = self.extract_patient_id(folder)
            xml_filename = self.find_xml_per_id(id_patient)
            xml_filepath = os.path.join(self.xml_root, xml_filename)
            doc = xml.dom.minidom.parse(xml_filepath)
            patient_last_name = doc.getElementsByTagName('LAST_NAME')[0].firstChild.nodeValue
            patient_first_name = doc.getElementsByTagName('FIRST_NAME')[0].firstChild.nodeValue
            patient_id = doc.getElementsByTagName('PATIENT_ID')[0].firstChild.nodeValue
            patient_id = self.refine_patient_id(patient_id)
            folder_name = patient_id.upper()+' '+patient_last_name.upper()+', '+patient_first_name.upper()
            zeiss_decoder = ZeissDecoder(os.path.join(self.data_root, folder))
            zeiss_decoder.decode()
            # print(os.path.join(out_folder, folder_name, visit_date))
            zeiss_decoder.save(os.path.join(out_folder, folder_name, visit_date))


if __name__ == '__main__':
    xml_folder = '/media/clement/SAMSUNG/AMD/ZeissExport/December/XML/'
    data_folder = '/media/clement/SAMSUNG/AMD/ZeissExport/December/data/'
    output = '/media/clement/SAMSUNG/AMD/ZeissExport/December/patients/'
    zeiss_exporter = ZeissExporter(data_folder, xml_folder)
    zeiss_exporter.export(output)









