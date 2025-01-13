import tkinter as tk
from tkinter import ttk
from soepversionizer.const import COLUMNS, PADDINGS, FONTS
from soepversionizer.questionview import QuestionView

class ScrollFrame():

    def __init__(self, root, row, column):

        self.root = root

        # Scrollable canvas + frame for questions 
        self.canvas = tk.Canvas(self.root, bg="pink")
        self.canvas.grid(row=row, column=column, sticky="nsew", **PADDINGS['normal'])

        v_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=row, column=column+1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scrollbar.set)

        # Scrollable canvas contains two columns
        self.frame = ttk.Frame(self.canvas)
        self.frame.columnconfigure(0, minsize=40, weight=1) 
        self.frame.columnconfigure(1, minsize=100, weight=1)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw", tags="frame")
        self.canvas.bind("<Configure>", self.adjust_frame_width)
        self.frame.bind("<Configure>", self.update_scroll_region)

        print(f"Width of scrollable frame at start: {self.frame.winfo_width()}")

   
    def adjust_frame_width(self, event):
        width = self.canvas.winfo_width()
        self.canvas.itemconfig("frame", width=width)
        
        # Adjust width of columns inside frame
        self.frame.columnconfigure(0, minsize=int(width*0.3))
        self.frame.columnconfigure(1, minsize=int(width*0.7))

    def update_scroll_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class QuestionnaireView:

    def __init__(self, root, col=None, row=None, data=None, aux_data=None, title="", study=None, questionnaire=None):
        
        self.root = root
        #self.frame = tk.LabelFrame(root, text=title, **PADDINGS['normal'], font=FONTS['main'], bg='red') 
        self.frame = self.root
        #self.frame = tk.Label(root, text=title, **PADDINGS['normal'], font=FONTS['main'])
        text1 = "1"
        label = tk.Label(self.root, text=text1, **PADDINGS['normal'], font=FONTS['main'], wraplength=2000) 
        label.grid(row=0, column=0)
        text2 = "1"
        label = tk.Label(self.root, text=text2, **PADDINGS['normal'], font=FONTS['main'], wraplength=2000) 
        label.grid(row=0, column=1)
        self.data = data
        self.aux_data = aux_data
        self.study = study
        self.questionnaire = questionnaire

        # Create columns within frame

        #self.frame.grid(row=row, column=col, sticky="nsew", **PADDINGS['normal'])
        #self.frame.columnconfigure(0, weight=0)
        #self.frame.columnconfigure(1, weight=1)
            

        self.quest_views = []

        self.columns = [
            COLUMNS['question'],
            COLUMNS['item'],
            COLUMNS['text'],
            COLUMNS['instruction'], 
            COLUMNS['scale'], 
            COLUMNS['answer_list']
        ]

    def updata_data(self, event=None, input=None, output=None):
        self.data = input.data
        self.questions = input.questions

    def update_meta(self, study, questionnaire):
        self.study = study
        self.questionnaire = questionnaire

    def update(self, event=None, input=None, output=None):
        
        # Get new data
        newdata = [self.data.loc[self.data['question']==input]]

        # Remove previous view
        for widget in self.frame.winfo_children():
            widget.destroy()

        self.quest_views = [QuestionView(self)]

        for q, d in zip(self.quest_views, newdata):
            q.update(input = d)

        print(f"Width of questionnaire view root frame: {self.frame.winfo_width()}")