import pandas as pd
import os
import tqdm


def extract_patient_info(folder_name):
    id = folder_name.split(' ')[0]
    names = folder_name.split(id+' ')[-1]
    last_name = names.split(',')[0].lower()
    surname = names.split(', ')[1].lower()
    return {'id':id, 'last_name':last_name[0].upper()+last_name[1:], 'surname':surname[0].upper()+surname[1:]}


def build_dataframe(root_to_patients_folders):
    df = pd.DataFrame(columns=['id', 'surname', 'last_name', 'visit_date', 'eye', 'modality', 'nb_imgs', 'relative_path'])
    list_folder_patients = os.listdir(root_to_patients_folders)

    for patient in tqdm.tqdm(list_folder_patients):
        patient_info = extract_patient_info(patient)
        patient_folder = os.path.join(root_to_patients_folders, patient)
        for visits in os.listdir(patient_folder):
            eye_folders = os.path.join(patient_folder, visits)
            for eye in os.listdir(eye_folders):
                modality_folders = os.path.join(eye_folders, eye)
                for modality in os.listdir(modality_folders):
                    data_folder = os.path.join(modality_folders, modality, 'data/')
                    if not os.path.exists(data_folder):
                        data_folder = os.path.join(modality_folders, modality)
                    nb_img = len(os.listdir(data_folder))
                    relative_folder = data_folder.split(root_to_patients_folders)[-1]
                    patient_dict = {}
                    patient_dict.update(patient_info)
                    patient_dict['visit_date'] = visits
                    patient_dict['eye'] = eye
                    patient_dict['modality'] = modality
                    patient_dict['nb_imgs'] = nb_img
                    patient_dict['relative_path'] = relative_folder
                    df = df.append(patient_dict, ignore_index=True)

    return df




