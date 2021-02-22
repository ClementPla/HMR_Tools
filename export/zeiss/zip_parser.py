import zipfile
import os
import tqdm


def extract_file_folder(file, folder):
    if os.path.exists(folder):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            count_file = len([_ for _ in zip_ref.infolist() if not _.is_dir()])
        if count_file == os.listdir(folder):
            return
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(folder)


def recursive_unzip(root_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    xml_folder = os.path.join(destination_folder, 'XML/')
    data_folder = os.path.join(destination_folder, 'data/')

    if not os.path.exists(xml_folder):
        os.makedirs(xml_folder)

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    for root, dirs, files in tqdm.tqdm(os.walk(root_folder, topdown=False)):
        for name in files:
            file = os.path.join(root, name)
            if name == 'XMLExportFiles.zip':
                extract_file_folder(file, xml_folder)
            elif name == 'IMGExportFiles.zip':
                extract_file_folder(file, data_folder)


if __name__ == '__main__':
    root = '/media/clement/SAMSUNG/AMD/Zeiss/December/'
    destination = '/media/clement/SAMSUNG/AMD/ZeissExport/December/'
    recursive_unzip(root, destination)


