import argparse
import os
from oct_converter.readers import E2E
from tqdm import tqdm
from oct_converter.image_types import FundusImageWithMetaData


class LogProcessor:
    def __init__(self, filepath):
        self.use_log = filepath is not None
        if self.use_log:
            assert os.path.exists(filepath)
            with open(filepath) as fp:
                self.log = fp.readlines()

    def get_log_index(self, key):
        for i, line in enumerate(self.log):
            if key.lower() in line.lower():
                return i

    def extract_patient_name(self, index):
        line = self.log[index]
        return line.split(', ')[:2]

    def extract_visit_date(self, index):
        line = self.log[index]
        if 'OCT' in line:
            return line.split('OCT ')[1][:10]
        elif 'HRA' in line:
            return line.split('HRA ')[1][:10]

    def patient_from_filename(self, filename):
        if self.use_log:
            return self.extract_patient_name(self.get_log_index(filename))
        else:
            return ['', '']

    def visit_date_from_filename(self, filename):
        if self.use_log:
            return self.extract_visit_date(self.get_log_index(filename))
        else:
            return ''

    def extract_patient_id(self, index):
        line = self.log[index]
        id = (line.split(':')[0].split(' ')[-1])
        return id

    def id_from_filename(self, filename):
        if self.use_log:
            return self.extract_patient_id(self.get_log_index(filename))
        else:
            return ''


class E2EExporter:
    def __init__(self, config):

        e2e_dirpath = os.path.split(config['input']['spectralis'])
        log_filepath = config['input']['spectralis_log_filename']

        if log_filepath is not None:
            log_filepath = os.path.split()
            if not log_filepath[0]:
                log_filepath = os.path.join(e2e_dirpath[0], log_filepath[1])
            else:
                log_filepath = config['input']['spectralis_log_filename']

        self.log = LogProcessor(log_filepath)
        self.dirpath = e2e_dirpath[0]
        self.output = config['export']['output_folder']
        self.overwrite = config['export']['overwrite']
        self.format = config['export']['format']
        if not self.format[0] == '.':
            self.format = '.'+self.format
        if e2e_dirpath[1]:
            self.files = [e2e_dirpath[1]]
        else:
            self.files = [f for f in os.listdir(self.dirpath)
                          if os.path.isfile(os.path.join(self.dirpath, f)) and f.lower().endswith('.e2e')]
        if config['options']['verbose']:
            print('Found %i .e2e file(s)' % len(self.files))

    def export(self):
        for i, f in tqdm(enumerate(self.files)):
            if f.lower().endswith('.e2e'):
                patient = self.log.patient_from_filename(f)
                patient_id = self.log.id_from_filename(f)
                visit_date = self.log.visit_date_from_filename(f).replace('/', '-')
                if self.log.use_log:
                    folder = os.path.join(self.output, str(patient_id)+' '+patient[0]+', '+patient[1]+'/'+visit_date+'/')
                else:
                    base = os.path.basename(f)
                    file, ext = os.path.splitext(base)
                    folder = os.path.join(self.output, file)
                if os.path.exists(folder) and not self.overwrite:
                    print('Skipping folder %s'%folder)
                    continue
                file = E2E(os.path.join(self.dirpath, f))
                oct_volumes = file.read_oct_volume()  # returns an OCT volume with additional metadata if available
                for o in oct_volumes:
                    laterality = 'OD' if o.laterality == 'R' else 'OS'

                    f_save = os.path.join(folder, laterality, o.type)
                    f_save_data = os.path.join(f_save, 'data/')
                    if not os.path.exists(f_save):
                        os.makedirs(f_save)

                    if not os.path.exists(f_save_data):
                        os.makedirs(f_save_data)
                    o.save(os.path.join(f_save_data, 'data'+self.format))
                    img_type = 'fundus' if isinstance(o, FundusImageWithMetaData) else 'OCT'

                    meta = {'visit_date': visit_date, 'laterality': laterality,
                           'patient': patient, 'image_type':img_type}
                    with open(os.path.join(f_save,'metadata.csv'), 'w') as f:
                        for key in meta.keys():
                            f.write("%s,%s\n" % (key, meta[key]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="Folder containing the .E2E files OR specific file path")
    parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="store_true", default=True)
    parser.add_argument("-o", "--output", help="output folder path", default="export/")
    parser.add_argument("-ow", "--overwrite", help="Overwrite existing file", default=False, action='store_true')
    parser.add_argument("-nl", "--no_log", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-eo", "--export_in_origin_folder", help="Export in the origin folder", action="store_true",
                        default=False)

    parser.add_argument("-l", "--log",
                        help="Path of the log file used to reconstruct the patient forder. \
                        By default, I'll look in DIRPATH/BatchLog.txt", default="BatchLog.txt")

    parser.add_argument("-f", "--format", help="export format", default=".png")


    args = parser.parse_args()
    no_log = args.no_log
    export_origin_folder = args.export_in_origin_folder
    e2e_dirpath = os.path.split(args.dir)
    log_filepath = os.path.split(args.log)
    if no_log:
        log_filepath = None
    else:
        if not log_filepath[0]:
            log_filepath = os.path.join(e2e_dirpath[0], log_filepath[1])
        else:
            log_filepath = args.log

    config = {}
    config['input'] = {}
    config['export'] = {}
    config['options'] = {}

    config['input']['spectralis'] = args.dir
    config['input']['spectralis_log_filename'] = log_filepath
    config['export']['format'] = args.format
    if export_origin_folder:
        config['export']['output_folder'] = os.path.split(args.dir)[0]
    else:
        config['export']['output_folder'] = args.output
    config['export']['overwrite'] = args.overwrite
    config['options']['verbose'] = args.verbosity

    e = E2EExporter(config)

    e.export()
