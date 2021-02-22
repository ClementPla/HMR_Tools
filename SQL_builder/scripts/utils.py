import os

class SQL_builder:
    def __init__(self, root):
        self.list_folder = os.listdir(root)
        self.visits_dict = []

    def get_list_patients(self):
        return [f.split(' ')[1] for f in self.list_folder]

    def get_list_id(self):
        return [f.split(' ')[0] for f in self.list_folder]

    def get_id_from_folder_name(self, folder):
        return folder.split(' ')[0]

    def build_visits_list(self):
        for p in self.list_folder:
            id_patient = self.get_id_from_folder_name(p)



