import csv
import functools
import pathlib
import pprint
import tkinter as tk
import tkinter.scrolledtext as tkst
import tkinter.simpledialog as tksd
from tkinter import ttk

CSV_FILE = 'heap_template.csv'
OUTPUT_FILE = 'output.csv'
FIND_STRINGS = [
        'lami', 'Lami',
        'laminectomy', 'Laminectomy',
        'discectomy', 'Discectomy',
        'diskectomy', 'Diskectomy',
        'fusion', 'Fusion',
        'lumbar laminectomy', 'Lumbar Laminectomy', 'Lumbar laminectomy', 'lumbar Laminectomy']


style = ttk.Style()
style.map("C.TButton",
          foreground=[('pressed', 'red'), ('active', 'blue')],
          background=[('pressed', '!disabled', 'black'),
                      ('active', 'white')]
          )

class Application(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self.pack()
        self.create_widgets()

        self.read_csv()
        self.load_patient(0)

    def read_csv(self):
        self.patients = {}

        with open(CSV_FILE, encoding="ISO-8859-1") as csvfile:
            reader = csv.reader(csvfile)

            # Skip header row.
            next(reader)
            
            for row in reader:
                mrn = row[3]
                if not mrn in self.patients:
                    self.patients[mrn] = {}
                    self.patients[mrn]['procedure_name'] = row[11]
                    self.patients[mrn]['procedure_desc'] = row[6]
                    self.patients[mrn]['notes'] = []

                    self.patients[mrn]['l1'] = tk.BooleanVar()
                    self.patients[mrn]['l2'] = tk.BooleanVar()
                    self.patients[mrn]['l3'] = tk.BooleanVar()
                    self.patients[mrn]['l4'] = tk.BooleanVar()
                    self.patients[mrn]['l5'] = tk.BooleanVar()
                    self.patients[mrn]['other'] = tk.BooleanVar()
                    self.patients[mrn]['outcome'] = tk.StringVar()
                    self.patients[mrn]['user_notes'] = tk.StringVar()

                self.patients[mrn]['notes'].append(row[17])

        self.mrns = sorted(self.patients.keys())
    
        # If output CSV exists, load in the state.
        if pathlib.Path(OUTPUT_FILE).is_file():
            with open(OUTPUT_FILE, 'r') as f:
                reader = csv.reader(f)

                # Skip the headers.
                next(reader)

                for row in reader:
                    mrn = row[0]
                    self.patients[mrn]['l1'].set(row[1] if len(row) > 1 else 0)
                    self.patients[mrn]['l2'].set(row[2] if len(row) > 2 else 0)
                    self.patients[mrn]['l3'].set(row[3] if len(row) > 3 else 0)
                    self.patients[mrn]['l4'].set(row[4] if len(row) > 4 else 0)
                    self.patients[mrn]['l5'].set(row[5] if len(row) > 5 else 0)
                    self.patients[mrn]['other'].set(row[6] if len(row) > 6 else 0)
                    self.patients[mrn]['outcome'].set(row[7] if len(row) > 7 else '')
                    self.patients[mrn]['user_notes'].set(row[8] if len(row) > 8 else '')

    def load_patient(self, index):
        if index < 0:
            return
        if index >= len(self.mrns):
            return

        # Store state for previous MRN.
        if hasattr(self, 'current_mrn'):
            self.patients[self.current_mrn]['outcome'].set(self.outcome_text.get('1.0', 'end-1c'))
            self.patients[self.current_mrn]['user_notes'].set(self.notes_text.get('1.0', 'end-1c'))
        
        # Load new state.
        self.current_index = index
        mrn = self.mrns[index]
        self.current_mrn = mrn
        patient = self.patients[mrn]

        self.patient_num['text'] = "Patient number: " + str(index)
        self.mrn['text'] = "MRN: #" + str(mrn)
        self.op_desc['text'] = patient['procedure_desc']

        self.notes.delete('1.0', tk.END)
        self.notes.insert(tk.INSERT, '\n\n'.join(patient['notes']))

        # Highlight FIND_STRINGS.
        for string in FIND_STRINGS:
            self.find_string(string)

        self.l1_button['variable'] = self.patients[mrn]['l1']
        self.l2_button['variable'] = self.patients[mrn]['l2']
        self.l3_button['variable'] = self.patients[mrn]['l3']
        self.l4_button['variable'] = self.patients[mrn]['l4']
        self.l5_button['variable'] = self.patients[mrn]['l5']
        self.other_button['variable'] = self.patients[mrn]['other']

        self.outcome_text.delete('1.0', tk.END)
        self.outcome_text.insert(tk.INSERT, self.patients[mrn]['outcome'].get())
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert(tk.INSERT, self.patients[mrn]['user_notes'].get())

    def find_string(self, string, tag='find'):
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

        self.op_desc= tk.Label(header_frame, text="procedure_desc")
        self.op_desc.pack(side="top")

        self.notes = tkst.ScrolledText(info_frame, width=90, height=30)
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

        self.msg= tk.Label(self, text="Hi Luke! Your progress is saved when you click 'Export CSV'.\nI've designed the app to load the saved state so you can safely quit and re-open after exporting.")
        self.msg.pack(side="bottom")

        bottom_buttons = tk.Frame(self, height=10)
        bottom_buttons.pack(side="bottom", pady=5)

        notes_inputs = tk.Frame(self)
        notes_inputs.pack(side="bottom", pady=3)

        outcome_inputs = tk.Frame(self)
        outcome_inputs.pack(side="bottom", pady=3)

        input_buttons = tk.Frame(self, height=10)
        input_buttons.pack(side="bottom", pady=5)

        def toggle_button(button, event):
            button.toggle()
    
        self.l1_button = tk.Checkbutton(input_buttons)
        self.l1_button.pack(side="left")
        self.l1_label = tk.Label(input_buttons, text="L1/2")
        self.l1_label.pack(side="left")
        self.l1_label.bind("<Button-1>", functools.partial(toggle_button, self.l1_button))

        self.l2_button = tk.Checkbutton(input_buttons)
        self.l2_button.pack(side="left")
        self.l2_label = tk.Label(input_buttons, text="L2/3")
        self.l2_label.pack(side="left")
        self.l2_label.bind("<Button-1>", functools.partial(toggle_button, self.l2_button))

        self.l3_button = tk.Checkbutton(input_buttons)
        self.l3_button.pack(side="left")
        self.l3_label = tk.Label(input_buttons, text="L3/4")
        self.l3_label.pack(side="left")
        self.l3_label.bind("<Button-1>", functools.partial(toggle_button, self.l3_button))

        self.l4_button = tk.Checkbutton(input_buttons)
        self.l4_button.pack(side="left")
        self.l4_label = tk.Label(input_buttons, text="L4/5")
        self.l4_label.pack(side="left")
        self.l4_label.bind("<Button-1>", functools.partial(toggle_button, self.l4_button))

        self.l5_button = tk.Checkbutton(input_buttons)
        self.l5_button.pack(side="left")
        self.l5_label = tk.Label(input_buttons, text="L5/S1")
        self.l5_label.pack(side="left")
        self.l5_label.bind("<Button-1>", functools.partial(toggle_button, self.l5_button))

        self.other_button = tk.Checkbutton(input_buttons)
        self.other_button.pack(side="left")
        self.other_label= tk.Label(input_buttons, text="Other")
        self.other_label.pack(side="left")


        self.outcome_label= tk.Label(outcome_inputs, text="Outcome")
        self.outcome_label.pack(side="left", padx=5)
        self.outcome_text = tk.Text(outcome_inputs, height=1)
        self.outcome_text.pack(side="left", padx=5)

        self.notes_label= tk.Label(notes_inputs, text="Notes")
        self.notes_label.pack(side="left", padx=5)
        self.notes_text = tk.Text(notes_inputs, height=1)
        self.notes_text.pack(side="left", padx=5)


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
        headers = [
                "MRN",
                "L1/L2",
                "L2/L3",
                "L3/L4",
                "L4/L5",
                "L5/S1",
                "Other",
                "Outcome",
                "Notes"]
        with open(OUTPUT_FILE, 'w+') as f:
            f.write(','.join(headers))
            f.write('\n')
            for mrn in self.mrns:
                row = [
                        mrn,
                        '1' if self.patients[mrn]['l1'].get() else '0',
                        '1' if self.patients[mrn]['l2'].get() else '0', 
                        '1' if self.patients[mrn]['l3'].get() else '0', 
                        '1' if self.patients[mrn]['l4'].get() else '0', 
                        '1' if self.patients[mrn]['l5'].get() else '0',
                        '1' if self.patients[mrn]['other'].get() else '0',
                        self.patients[mrn]['outcome'].get(),
                        self.patients[mrn]['user_notes'].get()]
                f.write(','.join(row))
                f.write('\n')


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
