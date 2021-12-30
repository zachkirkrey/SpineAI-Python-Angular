import csv
import logging
import os
import pathlib
import pprint
import queue
import subprocess
import sys
import threading
import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

from PIL import Image
import SimpleITK

import classifier_lib
import dicom_lib
import img_lib
import report_lib
import segmentation_lib
import study_lib
from models import bilwaj_lib

DRY_RUN = False
INPUT_FILE = 'input.csv'
INPUT_STUDIES_DIR = 'input_studies'
OUTPUT_FILE = 'output.csv'

style = ttk.Style()
style.map("C.TButton",
          foreground=[('pressed', 'red'), ('active', 'blue')],
          background=[('pressed', '!disabled', 'black'),
                      ('active', 'white')]
          )

class QueueDone(object):
    """Signifies all processing on the queue is complete."""
    pass

class IORedirector(object):
    def __init__(self, master, text_area):
        self.text_area = text_area
        self.master = master

    def write(self, s):
        self.text_area.insert(tk.INSERT, s)

    def flush(self):
        self.master.update_idletasks()


class Application(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self.counters = {
            'duplicate_mrn': 0,
            'missing_image_dir': 0,
            'missing_mrn': 0,
            'processed_patients': 0,
            'resumed_patients': 0,
        }

        self.patients = {}

        self.pack()
        self.create_widgets()

        self.read_inputs()
        self.read_outputs()
        if DRY_RUN:
            self.set_status('Ready (WARNING: dry run mode)')
        else:
            self.set_status('Ready')

    def increment_counter(self, counter_id, increment):
        if counter_id not in self.counters:
            raise KeyError('%s is not a valid counter.' % counter_id)

        self.counters[counter_id] += increment
        if counter_id == 'processed_patients':
            self.patients_processed['text'] = 'Patients processed: %d' % (
                    self.counters['processed_patients'])

    def set_counter(self, counter_id, value):
        if counter_id not in self.counters:
            raise KeyError('%s is not a valid counter.' % counter_id)

        self.counters[counter_id] = value
        if counter_id == 'processed_patients':
            self.patients_processed['text'] = 'Patients processed: %d' % (
                    self.counters['processed_patients'])

    def read_inputs(self):
        # Read image directories.
        dir_path = os.path.dirname(os.path.realpath(__file__))
        studies_dir = os.path.join(dir_path, INPUT_STUDIES_DIR)
        image_dirs = [f.name for f in os.scandir(studies_dir) if f.is_dir()] 

        with open(INPUT_FILE, encoding="ISO-8859-1") as csvfile:
            reader = csv.reader(csvfile)

            # Skip header row.
            next(reader)
            
            for i, row in enumerate(reader):
                mrn = row[300]
                if not mrn:
                    logging.warning(
                            "No MRN in column 300 for row %d. Skipping..." % i)
                    self.increment_counter('missing_mrn', 1)
                elif mrn in self.patients:
                    logging.warning(
                            "Duplicate MRN ('%s') in row %d. Skipping..." % (
                                mrn, i))
                    self.increment_counter('duplicate_mrn', 1)
                elif mrn not in image_dirs:
                    logging.warning(
                            "MRN '%s' in input sheet but not in image "
                            "directory %s. Skipping..." % (
                                mrn, studies_dir))
                    self.increment_counter('missing_image_dir', 1)
                else:
                    image_dirs.remove(mrn)

                    self.patients[mrn] = {}
                    if len(row) > 308:
                        # We allow for an extra "surgery recommendation" column.
                        self.patients[mrn]['surgery_recommendation'] = row[307]
                    else:
                        self.patients[mrn]['surgery_recommendation'] = ''
                    self.patients[mrn]['consult_datetime'] = len(row) > 1 ? row[1] : ''
                    self.patients[mrn]['had_surgery'] = len(row) > 14 ? row[14] : ''  # "Yes" or "No"
                    self.patients[mrn]['surgery_date'] = len(row) > 15 ? row[15] : ''
                    self.patients[mrn]['vas_score'] = len(row) > 85 ? row[85] : '' # 1 - 10

        self.mrns = sorted(self.patients.keys())
        self.patient_count['text'] = "Total new patients: %d" % len(self.patients)
        self.missing_mrns['text'] = "Rows missing MRNs: %d" % self.counters['missing_mrn']
        self.duplicate_rows['text'] = "Rows with duplicate MRNs: %d" % self.counters['duplicate_mrn']
        self.missing_images['text'] = "MRNs missing images: %d" % self.counters['missing_image_dir']
        self.extra_images['text'] = "Extra image directories: %d" % len(image_dirs)

    def read_outputs(self):
        """If an output file exists, read it to resume already completed work.
        
        Intended to be called after read_inputs()"""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.isfile(os.path.join(dir_path, OUTPUT_FILE)):
            with open(OUTPUT_FILE, encoding="ISO-8859-1") as csvfile:
                reader = csv.reader(csvfile)

                # Skip header row
                next(reader)

                for i, row in enumerate(reader):
                    mrn = row[0]
                    if not mrn:
                        logging.warning(
                                "No MRN in column 300 for row %d. Skipping..." % i)
                        return

                    if mrn not in self.patients:
                        logging.warning("MRN #%s not seen in inputs.")

                    patient = {}
                    patient['resumed'] = True
                    patient['surgery_recommendation'] = row[1]
                    patient['consult_datetime'] = row[2]
                    patient['had_surgery'] = row[3]
                    patient['surgery_date'] = row[4]
                    patient['vas_score'] = row[5]
                    patient['age'] = row[6]
                    patient['sex'] = row[7]
                    patient['weight'] = row[8]
                    patient['size'] = row[9]
                    patient['foramen_segmentation'] = {}
                    patient['foramen_segmentation']['segmentation_sizes'] = {}
                    patient['foramen_segmentation']['segmentation_sizes']['left'] = []
                    patient['foramen_segmentation']['segmentation_sizes']['right'] = []
                    patient['foramen_segmentation']['segmentation_sizes']['left'].append(float(row[10]))
                    patient['foramen_segmentation']['segmentation_sizes']['left'].append(float(row[11]))
                    patient['foramen_segmentation']['segmentation_sizes']['left'].append(float(row[12]))
                    patient['foramen_segmentation']['segmentation_sizes']['left'].append(float(row[13]))
                    patient['foramen_segmentation']['segmentation_sizes']['left'].append(float(row[14]))
                    patient['foramen_segmentation']['segmentation_sizes']['right'].append(float(row[15]))
                    patient['foramen_segmentation']['segmentation_sizes']['right'].append(float(row[16]))
                    patient['foramen_segmentation']['segmentation_sizes']['right'].append(float(row[17]))
                    patient['foramen_segmentation']['segmentation_sizes']['right'].append(float(row[18]))
                    patient['foramen_segmentation']['segmentation_sizes']['right'].append(float(row[19]))
                    patient['canal_areas'] = []
                    patient['canal_areas'].append(float(row[20]))
                    patient['canal_areas'].append(float(row[21]))
                    patient['canal_areas'].append(float(row[22]))
                    patient['canal_areas'].append(float(row[23]))
                    patient['canal_areas'].append(float(row[24]))
                    patient['canal_relative_areas'] = []
                    patient['canal_relative_areas'].append(float(row[25]) / 100)
                    patient['canal_relative_areas'].append(float(row[26]) / 100)
                    patient['canal_relative_areas'].append(float(row[27]) / 100)
                    patient['canal_relative_areas'].append(float(row[28]) / 100)
                    patient['canal_relative_areas'].append(float(row[29]) / 100)

                    if mrn in self.patients:
                        old_patient = self.patients[mrn]
                        self.patients[mrn] = {**old_patient, **patient}
                    else:
                        self.patients[mrn] = patient

                    self.increment_counter('resumed_patients', 1)

        self.patient_count['text'] = "Total new patients: %d" % (len(self.patients) - self.counters['resumed_patients'])
        self.seen_patient_count['text'] = "Total existing patients: %d" % self.counters['resumed_patients']
    
    def set_status(self, status_txt):
        self.info['text'] = 'Status: %s' % str(status_txt)
    
    def create_widgets(self):
        # Header Frame
        header_frame = tk.Frame(self)
        header_frame.pack(side="top", padx=10, pady=15)

        self.patient_count = tk.Label(header_frame, text="Total new patients: 0")
        self.patient_count.pack(side="top")

        self.seen_patient_count = tk.Label(header_frame, text="Total existing patients: 0")
        self.seen_patient_count.pack(side="top")

        self.missing_mrns = tk.Label(header_frame, text="Rows missing MRNs: N/A")
        self.missing_mrns.pack(side="top")

        self.duplicate_rows = tk.Label(header_frame, text="Rows with duplicate MRNs: N/A")
        self.duplicate_rows.pack(side="top")

        self.missing_images = tk.Label(header_frame, text="MRNs missing images: N/A")
        self.missing_images.pack(side="top")

        self.extra_images = tk.Label(header_frame, text="Extra image directories: N/A")
        self.extra_images.pack(side="top")

        self.patients_processed = tk.Label(header_frame, text="Patients processed: 0")
        self.patients_processed.pack(side="top", fill=tk.X, pady=10)

        self.info = tk.Label(header_frame, text="")
        self.info.pack(side="top", fill=tk.X, pady=10)

        # # Info Frame
        # info_frame = tk.Frame(self, height=50)
        # info_frame.pack(side="top", padx=10, pady=15)

        # self.notes = tkst.ScrolledText(info_frame, width=90, height=30)
        # self.notes.pack(side="top")

        # Notes message.
        self.msg= tk.Label(
                self, text="Instructions:\n\n"
                           "1. Move input spreadsheet to this folder and rename 'input.csv'.\n"
                           "2. Move images into input_studies/<patient number>.\n"
                           "3. Start app, verify 'Total New Patients' > 0.\n"
                           "4. Press 'Execute'. 'output.csv' is written every time a patient \n"
                           "evaluation completes.")
        self.msg.pack(side="bottom")

        # Bottom buttons
        bottom_buttons = tk.Frame(self, height=10)
        bottom_buttons.pack(side="bottom", pady=5)

        self.execute = ttk.Button(bottom_buttons, width=10, style="C.TButton")
        self.execute["text"] = "Execute"
        self.execute["command"] = self.process_patients
        self.execute.pack(side="left")

        # self.export_button = ttk.Button(bottom_buttons, width=10, style="C.TButton")
        # self.export_button["text"] = "Export CSV"
        # self.export_button["command"] = self.export_csv
        # self.export_button.pack(side="left")

    @staticmethod
    def export_csv(patients):
        headers = [
                "Acension",
                "Surgery Recommendation",
                "Consult Date",
                "Had Surgery",
                "Surgery Date",
                "VAS Score (1-10)",
                "Age",
                "Sex",
                "Weight",
                "Size (m)",
                "L5 Left Foramen Area (mm²)",
                "L4 Left Foramen Area (mm²)",
                "L3 Left Foramen Area (mm²)",
                "L2 Left Foramen Area (mm²)",
                "L1 Left Foramen Area (mm²)",
                "L5 Right Foramen Area (mm²)",
                "L4 Right Foramen Area (mm²)",
                "L3 Right Foramen Area (mm²)",
                "L2 Right Foramen Area (mm²)",
                "L1 Right Foramen Area (mm²)",
                "L5 Canal Area (mm²)",
                "L4 Canal Area (mm²)",
                "L3 Canal Area (mm²)",
                "L2 Canal Area (mm²)",
                "L1 Canal Area (mm²)",
                "L5 Canal Relative to neighboring slices (%)",
                "L4 Canal Relative to neighboring slices (%)",
                "L3 Canal Relative to neighboring slices (%)",
                "L2 Canal Relative to neighboring slices (%)",
                "L1 Canal Relative to neighboring slices (%)"]

        with open(OUTPUT_FILE, 'w+') as f:
            f.write(','.join(headers))
            f.write('\n')
            for patient_id in patients:
                patient = patients[patient_id]
                # TODO(billy): Make segmentation areas robust to failures (missing area)
                row = [
                        patient_id,
                        patient['surgery_recommendation'],
                        patient['consult_datetime'],
                        patient['had_surgery'],
                        patient['surgery_date'],
                        patient['vas_score'],
                        patient['age'],
                        patient['sex'],
                        patient['weight'],
                        patient['size'],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['left'][0],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['left'][1],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['left'][2],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['left'][3],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['left'][4],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['right'][0],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['right'][1],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['right'][2],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['right'][3],
                        '%0.2f' % patient['foramen_segmentation']['segmentation_sizes']['right'][4],
                        '%0.2f' % patient['canal_areas'][0],
                        '%0.2f' % patient['canal_areas'][1],
                        '%0.2f' % patient['canal_areas'][2],
                        '%0.2f' % patient['canal_areas'][3],
                        '%0.2f' % patient['canal_areas'][4],
                        '%0.2f' % (patient['canal_relative_areas'][0] * 100),
                        '%0.2f' % (patient['canal_relative_areas'][1] * 100),
                        '%0.2f' % (patient['canal_relative_areas'][2] * 100),
                        '%0.2f' % (patient['canal_relative_areas'][3] * 100),
                        '%0.2f' % (patient['canal_relative_areas'][4] * 100),
                ]
                row = [str(elem) for elem in row]
                f.write(','.join(row))
                f.write('\n')

    def process_patients(self):
        self.set_counter('processed_patients', 0)
        thread = threading.Thread(target=self.process_patients_thread)
        thread.start()

    def process_patients_thread(self):
        input_queue = queue.Queue()
        output_queue = queue.Queue()

        # TODO(billy): Consider processing multiple patients in a single thread
        # here.
        thread = threading.Thread(target=self.process_patient_thread, args=(
            input_queue, output_queue, self))
        thread.daemon = True
        thread.start()

        for patient_id in self.patients:
            patient = self.patients[patient_id]
            if 'resumed' in patient and patient['resumed']:
                pass
            else:
                input_queue.put((patient_id, patient))
        input_queue.put(QueueDone())

        output_patients = {}
        while True:
            output = output_queue.get()
            if isinstance(output, QueueDone):
                break
            else:
                patient_id, patient = output
                output_patients[patient_id] = patient
                self.increment_counter('processed_patients', 1)
            
            self.export_csv(output_patients)
        
        self.set_status('Done. Results written to "%s".' % OUTPUT_FILE)
           
    @staticmethod
    def process_patient_thread(input_queue, output_queue, app):
        if DRY_RUN:
            logging.warning('DRY_RUN == True, not performing real data')

        while True:
            input_obj = input_queue.get()
            if isinstance(input_obj, QueueDone):
                output_queue.put(QueueDone())
                return
            else:
                patient_id, patient = input_obj
                app.set_status('Processing MRN #%s' % patient_id)

                if DRY_RUN:
                    logging.warning('DRY_RUN == True, not performing real data')
                    fake_patient = {'surgery_recommendation': 'N/A', 'consult_datetime': '', 'age': None, 'weight': None, 'sex': None, 'size': None, 'foramen_segmentation': {'max_area_slice': {'left': 4, 'right': 11}, 'segmentation_sizes': {'left': [114.0, 131.0, 158.0, 92.0, 110.0, 90.0, 70.0], 'right': [81.0, 215.0, 172.0, 114.0, 143.0, 106.0]}, 'segmentation_areas': {'left': [{'size': 114, 'height': 18, 'width': 11, 'center': (203, 141)}, {'size': 131, 'height': 12, 'width': 17, 'center': (186, 150)}, {'size': 158, 'height': 19, 'width': 13, 'center': (159, 143)}, {'size': 92, 'height': 12, 'width': 10, 'center': (121, 145)}, {'size': 110, 'height': 21, 'width': 9, 'center': (92, 154)}, {'size': 90, 'height': 15, 'width': 7, 'center': (56, 165)}, {'size': 70, 'height': 13, 'width': 7, 'center': (22, 173)}], 'right': [{'size': 81, 'height': 13, 'width': 10, 'center': (203, 141)}, {'size': 215, 'height': 20, 'width': 21, 'center': (189, 150)}, {'size': 172, 'height': 19, 'width': 12, 'center': (156, 142)}, {'size': 114, 'height': 13, 'width': 11, 'center': (121, 146)}, {'size': 143, 'height': 21, 'width': 9, 'center': (92, 155)}, {'size': 106, 'height': 20, 'width': 9, 'center': (59, 166)}]}}, 'canal_areas': [415.692138671875, 346.58203125, 292.9443359375, 315.63720703125, 326.983642578125, 363.0859375], 'canal_relative_areas': [.9]*6}
                    patient = {**patient, **fake_patient}
                else:
                    dir_path = os.path.dirname(os.path.realpath(__file__))
                    studies_dir = os.path.join(dir_path, INPUT_STUDIES_DIR)

                    src_filepattern = os.path.join(studies_dir, patient_id, '**', '*')
                    study = study_lib.Study.from_files(src_filepattern)

                    # TODO(billy): Consider using GPU to optimize classification.
                    ##########
                    # BEGIN FORAMEN SEGMENTATION
                    #########

                    model = bilwaj_lib.get_foramen_model()
                    model_file = os.path.join(os.environ['PYTHONPATH'], 'testdata/models/foramen/UNet.hdf5')
                    model.load_weights(model_file)

                    classifier = classifier_lib.ForamenKerasClassifier()
                    classifier.preprocess_settings['n4_bias_correction'] = False
                    classifier.model = model
                    classifier.preprocess(study)
                    classifier.classify_study(study)

                    study.get_segmentation(study_lib.SegmentationType.FORAMEN).postprocess_settings['min_area_filter'] = 51
                    study.get_segmentation(study_lib.SegmentationType.FORAMEN).postprocess()

                    ##########
                    # END FORAMEN SEGMENTATION
                    ##########

                    ##########
                    # BEGIN DISK SEGMENTATION
                    ##########

                    model = bilwaj_lib.get_disk_model()
                    model_file = os.path.join(os.environ['PYTHONPATH'], 'testdata/models/disk/UNet.hdf5')
                    model.load_weights(model_file)

                    classifier = classifier_lib.DiskKerasClassifier()
                    classifier.model = model
                    classifier.preprocess(study)
                    classifier.classify_study(study)
                    
                    study.get_segmentation(study_lib.SegmentationType.DISK).postprocess_settings['min_area_filter'] = 120
                    study.get_segmentation(study_lib.SegmentationType.DISK).postprocess()

                    ##########
                    # END DISK SEGMENTATION
                    ##########

                    ##########
                    # BEGIN CANAL SEGMENTATION
                    ##########

                    model = bilwaj_lib.get_canal_model()
                    model_file = os.path.join(os.environ['PYTHONPATH'], 'testdata/models/canal/UNet.hdf5')
                    model.load_weights(model_file)

                    classifier = classifier_lib.CanalKerasClassifier()
                    classifier.model = model
                    classifier.preprocess(study)
                    classifier.classify_study(study)

                    ##########
                    # END CANAL SEGMENTATION
                    ##########

                    dicom_patient = dicom_lib.get_patient(study.get_series(study_lib.SeriesType.SAGGITAL_ORIGINAL))
                    patient['age'] = dicom_patient['age']
                    patient['weight'] = dicom_patient['weight']
                    patient['sex'] = dicom_patient['sex']
                    patient['size'] = dicom_patient['size']

                    patient['foramen_segmentation'] = study.get_segmentation(study_lib.SegmentationType.FORAMEN)._data()

                    canal_locations_mm = study.get_segmentation(study_lib.SegmentationType.DISK).get_disk_locations_mm()
                    canal_spacing = study.get_series(study_lib.SeriesType.AXIAL_PREPROCESSED).image.GetSpacing()
                    canal_areas = study.get_segmentation(study_lib.SegmentationType.CANAL).get_canal_areas_for_Z_mm(canal_locations_mm, canal_spacing)
                    patient['canal_areas'] = canal_areas

                    # TODO(billy): Move the logic for this "relative area" 
                    # calculation to CanalSegmentation.
                    canal_slices = [study.get_segmentation(study_lib.SegmentationType.CANAL).get_nearest_index_from_mm(l) for l in canal_locations_mm]
                    relative_areas = []
                    for i, index in enumerate(canal_slices):
                        neighbor_slices = []
                        if index > 0:
                            neighbor_slices.append(index - 1)
                        if index < study.get_segmentation(study_lib.SegmentationType.CANAL).series.image.GetDepth() - 1:
                            neighbor_slices.append(index + 1)

                        canal_area = canal_areas[i]
                        neighbor_areas = study.get_segmentation(study_lib.SegmentationType.CANAL).get_canal_areas_for_indicies(neighbor_slices, canal_spacing)

                        relative_areas.append(
                                canal_area / (
                                    sum(neighbor_areas) / len(neighbor_areas)))
                    patient['canal_relative_areas'] = relative_areas

                output_queue.put((patient_id, patient))


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
