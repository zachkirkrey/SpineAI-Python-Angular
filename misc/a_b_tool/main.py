import argparse
import csv
import functools
import logging
import pathlib
import pprint
import tkinter as tk
import tkinter.font as tkfont
import tkinter.scrolledtext as tkst
import tkinter.simpledialog as tksd
from tkinter import ttk
import yaml

# FIND_STRINGS = [
#         'lami', 'Lami',
#         'laminectomy', 'Laminectomy',
#         'discectomy', 'Discectomy',
#         'diskectomy', 'Diskectomy',
#         'fusion', 'Fusion',
#         'lumbar laminectomy', 'Lumbar Laminectomy', 'Lumbar laminectomy', 'lumbar Laminectomy']


style = ttk.Style()
style.map("C.TButton",
          foreground=[('pressed', 'red'), ('active', 'blue')],
          background=[('pressed', '!disabled', 'black'),
                      ('active', 'white')]
          )

class Application(ttk.Frame):

    # TODO(billy): Document settings config.
    def __init__(self, settings, master=None):
        super().__init__(master)

        self.settings = settings
        self._validate_settings()

        with open(settings['settings_file'], 'r') as f:
            self.yaml_settings = yaml.load(f, Loader=yaml.BaseLoader)

        self.pack()
        self.create_widgets()

        self.read_csv()
        self.load_patient(0)

    def _validate_settings(self):
        valid = True
        if 'input_file' not in self.settings:
            logging.error('input_file not defined.')
            valid = False
        if 'output_file' not in self.settings:
            logging.error('output_file not defined.')
            valid = False
        if 'settings_file' not in self.settings:
            logging.error('settings_file not defined.')
            valid = False

        if not valid:
            logging.fatal('invalid settings')

    def read_csv(self):
        self.patients = {}

        with open(self.settings['input_file'], encoding="ISO-8859-1") as csvfile:
            reader = csv.reader(csvfile)

            # Skip header row.
            if self.yaml_settings['input_ignore_first_row']:
                next(reader)
           
            col_locations = self.yaml_settings['input_column_indicies']
            # Convert from 1-indexed to 0-indexed
            for key in col_locations:
                col_locations[key] = int(col_locations[key]) - 1

            for row in reader:
                mrn = row[col_locations['mri_no']]
                if not mrn in self.patients:
                    self.patients[mrn] = {}
                    for key in col_locations:
                        if len(row) > col_locations[key]:
                            self.patients[mrn][key] = row[col_locations[key]]
                        else:
                            self.patients[mrn][key] = ''

        self.mrns = list(self.patients.keys())

    def save_current_patient(self):
        if not hasattr(self, 'current_mrn'):
            return

        self.patients[self.current_mrn]['subject_referral'] = self.response_var_referral.get()
        self.patients[self.current_mrn]['subject_urgency'] = self.response_var_urgent.get()
        self.patients[self.current_mrn]['subject_confidence'] = self.response_var_confidence.get()
        self.patients[self.current_mrn]['subject_notes'] = self.notes_text.get('1.0', 'end-1c')

    def get_spine_ai_report(self, patient):
       
        def get_bar_for_value(value):
            """Renders an ASCII bar for use in a horizontal bar graph."""
            num_bars, num_remainder = divmod(value, 4)
            
            bar = '█' * num_bars

            fourth_bars = ['', '▎', '▌', '▊']
            if num_remainder > 0:
                bar += fourth_bars[num_remainder]

            if not bar:
                bar = '▎'

            return bar

        def get_row_for_percentile(percentile):
            try:
                percentile_num = int(percentile)
                if percentile_num < 100:
                    percentile += ' '
                if percentile_num < 10:
                    percentile += ' '
                return "{}  {}".format(
                        percentile, get_bar_for_value(percentile_num))
            except ValueError:
                return percentile.upper()

        template = """
CANAL    | NARROWING (%)
-----------------------------------------
L1/L2    | {stenosis_percentile_l1_l2}
-----------------------------------------
L2/L3    | {stenosis_percentile_l2_l3}
-----------------------------------------
L3/L4    | {stenosis_percentile_l3_l4}
-----------------------------------------
L4/L5    | {stenosis_percentile_l4_l5}
-----------------------------------------
L5/S1    | {stenosis_percentile_l5_s1}
-----------------------------------------
                Minimal            Severe
"""

        format_vars = {
                'stenosis_percentile_l1_l2': get_row_for_percentile(patient['stenosis_percentile_l1_l2']),
                'stenosis_percentile_l2_l3': get_row_for_percentile(patient['stenosis_percentile_l2_l3']),
                'stenosis_percentile_l3_l4': get_row_for_percentile(patient['stenosis_percentile_l3_l4']),
                'stenosis_percentile_l4_l5': get_row_for_percentile(patient['stenosis_percentile_l4_l5']),
                'stenosis_percentile_l5_s1': get_row_for_percentile(patient['stenosis_percentile_l5_s1']),
        }

        return template.format(**format_vars)

    def load_patient(self, index):
        if index < 0:
            return
        if index >= len(self.mrns):
            return

        self.save_current_patient()
        
        # Load new state.
        self.current_index = index
        mrn = self.mrns[index]
        self.current_mrn = mrn
        patient = self.patients[mrn]

        self.patient_num['text'] = "Patient number: " + str(index)
        self.mrn['text'] = "MRN: #" + str(mrn)
        # self.op_desc['text'] = patient['procedure_desc']

        self.notes.delete('1.0', tk.END)
        if patient['render_type'] == 'RAD':
            self.notes.insert(tk.INSERT, patient['classic_mri_report_text'])
        elif patient['render_type'] == 'SPINE':
            self.notes.insert(tk.INSERT, self.get_spine_ai_report(patient))
        else:
            self.notes.insert(tk.INSERT, "Invalid '{}' Value. (Expected: 'RAD' or 'SPINE'. Got: '{}'".format(
                self.yaml_settings['input_column_labels']['render_type'],
                patient['render_type']))

        # Highlight FIND_STRINGS.
        # for string in FIND_STRINGS:
        #     self.find_string(string)

        if patient['subject_referral']:
            self.response_var_referral.set(patient['subject_referral'])
        else:
            self.response_var_referral.set(None)
        if patient['subject_urgency']:
            self.response_var_urgent.set(patient['subject_urgency'])
        else:
            self.response_var_urgent.set(None)
        if patient['subject_confidence']:
            self.response_var_confidence.set(patient['subject_confidence'])
        else:
            self.response_var_confidence.set(None)


        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert(tk.INSERT, patient['subject_notes'])

    def find_string(self, string, tag='find'):
        if not string:
            return

        count_var = tk.IntVar()
        search_index = '1.0'
        while True:
            search_index = self.notes.search(string, search_index, "end", count=count_var)
            if not search_index: break

            end = self.notes.index('%s + %s c' % (search_index, count_var.get()))
            self.notes.tag_add(tag, search_index, end)
            search_index = end

    def ask_find(self, tag='find_2'):
        find_string = tksd.askstring('Find', 'String to find:')
        self.find_string(find_string, tag)

    def create_widgets(self):
        header_frame = tk.Frame(self)
        header_frame.pack(side="top", padx=10, pady=15)

        info_frame = tk.Frame(self, height=50)
        info_frame.pack(side="top", padx=10, pady=15)

        self.patient_num = tk.Label(header_frame, text="Patient number: 0")
        self.patient_num.pack(side="top")

        self.mrn = tk.Label(header_frame, text="MRN")
        self.mrn.pack(side="top")

        self.op_desc= tk.Label(header_frame)
        self.op_desc.pack(side="top")

        customfont = tkfont.Font(
                family=self.yaml_settings['report_font_family'],
                size=self.yaml_settings['report_font_size'])

        self.notes = tkst.ScrolledText(info_frame, width=110, height=30, font=customfont)
        self.notes.pack(side="top")
        self.notes.insert(tk.INSERT, "notes")
        self.notes.tag_configure("find", background="yellow")
        self.notes.tag_configure("find_2", background="cyan")

        after_notes = tk.Frame(self)
        after_notes.pack(side="top")

        self.next_patient = ttk.Button(after_notes, width=10, style="C.TButton")
        self.next_patient["text"] = "Find in Notes"
        self.next_patient["command"] = self.ask_find
        self.next_patient.pack(side="top")

        user_responses = tk.Frame(self, height=10)
        user_responses.pack(side="top", pady=5)

        notes_inputs = tk.Frame(self)
        notes_inputs.pack(side="top", pady=3)

        self.notes_label= tk.Label(notes_inputs, text="Notes")
        self.notes_label.pack(side="left", padx=5)
        self.notes_text = tk.Text(notes_inputs, height=1)
        self.notes_text.pack(side="left", padx=5)

        bottom_buttons = tk.Frame(self, height=10)
        bottom_buttons.pack(side="top", pady=12)

        self.msg= tk.Label(self, text="Your progress is saved when you click 'Export CSV'.\nThis app loads saved state so you can safely quit and re-open after exporting.")
        self.msg.pack(side="bottom")

        def select_button(button, event):
            button.select()

        column_1 = tk.Frame(user_responses)
        column_1.pack(side="left", padx=10)

        column_1_label = tk.Label(column_1, text="Referral to:")
        column_1_label.pack(side="left", anchor="n")

        column_1_buttons = tk.Frame(column_1)
        column_1_buttons.pack(side="left")

        self.response_var_referral = tk.StringVar()

        column_1_row_1 = tk.Frame(column_1_buttons)
        column_1_row_1.pack(side="top")
        column_1_button_1 = tk.Radiobutton(column_1_row_1, variable=self.response_var_referral, value="Pain / PT")
        column_1_button_1.pack(side="left")
        column_1_button_1_label = tk.Label(column_1_row_1, text="Pain / PT")
        column_1_button_1_label.pack(side="left")
        column_1_button_1_label.bind("<Button-1>", functools.partial(select_button, column_1_button_1))

        column_1_row_2 = tk.Frame(column_1_buttons)
        column_1_row_2.pack(side="top")
        column_1_button_2 = tk.Radiobutton(column_1_row_2, variable=self.response_var_referral, value="Surgeon")
        column_1_button_2.pack(side="left")
        column_1_button_2_label = tk.Label(column_1_row_2, text="Surgeon")
        column_1_button_2_label.pack(side="left")
        column_1_button_2_label.bind("<Button-1>", functools.partial(select_button, column_1_button_2))

        column_2 = tk.Frame(user_responses)
        column_2.pack(side="left", padx=30)

        column_2_label = tk.Label(column_2, text="Urgent:")
        column_2_label.pack(side="left", anchor="n")

        column_2_buttons = tk.Frame(column_2)
        column_2_buttons.pack(side="left")

        self.response_var_urgent = tk.StringVar()

        column_2_row_1 = tk.Frame(column_2_buttons)
        column_2_row_1.pack(side="top")
        column_2_button_1 = tk.Radiobutton(column_2_row_1, variable=self.response_var_urgent, value="Yes")
        column_2_button_1.pack(side="left")
        column_2_button_1_label = tk.Label(column_2_row_1, text="Yes")
        column_2_button_1_label.pack(side="left")
        column_2_button_1_label.bind("<Button-1>", functools.partial(select_button, column_2_button_1))

        column_2_row_2 = tk.Frame(column_2_buttons)
        column_2_row_2.pack(side="top")
        column_2_button_2 = tk.Radiobutton(column_2_row_2, variable=self.response_var_urgent, value="No")
        column_2_button_2.pack(side="left")
        column_2_button_2_label = tk.Label(column_2_row_2, text="No")
        column_2_button_2_label.pack(side="left")
        column_2_button_2_label.bind("<Button-1>", functools.partial(select_button, column_2_button_2))

        column_3 = tk.Frame(user_responses)
        column_3.pack(side="left", padx=10)

        column_3_label = tk.Label(column_3, text="Confidence in your decision:", wraplength=100)
        column_3_label.pack(side="left", anchor="n")

        column_3_buttons = tk.Frame(column_3)
        column_3_buttons.pack(side="left")

        self.response_var_confidence = tk.StringVar()

        column_3_row_1 = tk.Frame(column_3_buttons)
        column_3_row_1.pack(side="top")
        column_3_button_1 = tk.Radiobutton(column_3_row_1, variable=self.response_var_confidence, value="1")
        column_3_button_1.pack(side="left")
        column_3_button_1_label = tk.Label(column_3_row_1, text="1 Low")
        column_3_button_1_label.pack(side="left")
        column_3_button_1_label.bind("<Button-1>", functools.partial(select_button, column_3_button_1))

        column_3_button_2 = tk.Radiobutton(column_3_row_1, variable=self.response_var_confidence, value="2")
        column_3_button_2.pack(side="left")
        column_3_button_2_label = tk.Label(column_3_row_1, text="2")
        column_3_button_2_label.pack(side="left")
        column_3_button_2_label.bind("<Button-1>", functools.partial(select_button, column_3_button_2))

        column_3_button_3 = tk.Radiobutton(column_3_row_1, variable=self.response_var_confidence, value="3")
        column_3_button_3.pack(side="left")
        column_3_button_3_label = tk.Label(column_3_row_1, text="3")
        column_3_button_3_label.pack(side="left")
        column_3_button_3_label.bind("<Button-1>", functools.partial(select_button, column_3_button_3))

        column_3_button_4 = tk.Radiobutton(column_3_row_1, variable=self.response_var_confidence, value="4")
        column_3_button_4.pack(side="left")
        column_3_button_4_label = tk.Label(column_3_row_1, text="4 High")
        column_3_button_4_label.pack(side="left")
        column_3_button_4_label.bind("<Button-1>", functools.partial(select_button, column_3_button_4))

        self.last_patient = ttk.Button(bottom_buttons, width=10, style="C.TButton")
        self.last_patient["text"] = "Last MRN"
        self.last_patient["command"] = self.go_last_patient
        self.last_patient.pack(side="left")

        self.export_patient = ttk.Button(bottom_buttons, width=10, style="C.TButton")
        self.export_patient["text"] = "Export CSV"
        self.export_patient["command"] = self.export_csv
        self.export_patient.pack(side="left")

        self.next_patient = ttk.Button(bottom_buttons, width=10, style="C.TButton")
        self.next_patient["text"] = "Next MRN"
        self.next_patient["command"] = self.go_next_patient
        self.next_patient.pack(side="left")

    def go_last_patient(self):
        self.load_patient(self.current_index - 1)

    def go_next_patient(self):
        self.load_patient(self.current_index + 1)

    def export_csv(self):
        self.save_current_patient()

        keys = self.yaml_settings['input_column_indicies'].keys()
        headers = [self.yaml_settings['input_column_labels'][key] for key in keys]
        with open(self.settings['output_file'], 'w', newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(headers)
            for mrn in self.mrns:
                patient = self.patients[mrn]
                row = [patient[key] for key in keys]
                csvwriter.writerow(row)


def main():
    parser = argparse.ArgumentParser(
            description='\x1b[34mSpineAI Research Tool\x1b[0m: Study decision making with SpineAI report.\n',
            formatter_class=argparse.RawTextHelpFormatter)

    # TODO(billy): Add an example CSV.
    parser.add_argument(
            '--input_file',
            default='input.csv',
            help='Input file CSV to read. (default="input.csv")')
    parser.add_argument(
            '--output_file',
            help='(optional) If specified, write output to this file. Otherwise, write directly over --input_file.')
    parser.add_argument(
            '--settings_file',
            default='settings.yml',
            help='YAML file containing settings to load. (default="settings.yml")')
    args = parser.parse_args()

    settings = {
            'input_file': args.input_file,
            'settings_file': args.settings_file,
            'output_file': '',
    }
    if args.output_file is not None:
        settings['output_file'] = args.output_file
    else:
        settings['output_file'] = args.input_file

    app = Application(settings)
    app.mainloop()


if __name__ == "__main__":
    main()
