import tkinter as tk
from tkinter import ttk
from soepversionizer.const import COLUMNS, PADDINGS, FONTS
from soepversionizer.questionview import QuestionView
from soepversionizer.input_handlers import ScrollEventHandler

class ScrollFrame():

    """A scrollable canvas widget that contains a frame with two columns"""

    def __init__(self, root, row, column):

        self.root = root

        ##############################
        # Layout 
        ###############################

        # Scrollable canvas + frame for questions 
        self.canvas = tk.Canvas(self.root, bg="pink", height=600)
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

        #############################
        # Handling of user input
        #############################

        # Bind mouse wheel input to widgets of canvas
        self.scroll_handler = ScrollEventHandler(self.canvas)
        for widget in [self.canvas, v_scrollbar] +  self.canvas.winfo_children():
            widget.bind("<MouseWheel>", self.scroll_handler.on_mouse_wheel)  # Windows/Linux
            widget.bind("<Button-4>", self.scroll_handler.on_mouse_wheel)  # macOS scroll up
            widget.bind("<Button-5>", self.scroll_handler.on_mouse_wheel)  # macOS scroll down  

    def adjust_frame_width(self, event):
        width = self.canvas.winfo_width()
        self.canvas.itemconfig("frame", width=width)
        
        # Adjust width of columns inside frame
        self.frame.columnconfigure(0, minsize=int(width*0.2))
        self.frame.columnconfigure(1, minsize=int(width*0.8))

    def update_scroll_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class QuestionnaireView(ScrollFrame):

    """A modified ScrollFrame that displays a question with its several items"""

    def __init__(self, root, column=None, row=None, data=None, aux_data=None, title="", study=None, questionnaire=None):
        
        super().__init__(root, column=column, row=row)
        
        self.data = data
        self.aux_data = aux_data
        self.study = study
        self.questionnaire = questionnaire

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
        """Update if new data, e.g. questions.csv, is loaded

        Parameters
        ----------
        event : _type_, optional
            _description_, by default None
        input : Data object, optional
            The new data object
        output : _type_, optional
            _description_, by default None
        """
        
        self.data = input.data
        self.answers = input.answers
        self.questions = input.questions

    def update_meta(self, study, questionnaire):
        self.study = study
        self.questionnaire = questionnaire

    def update(self, event=None, input=None, output=None):
    
        # Remove previous view
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Get new question
        newdata = [self.data.loc[self.data['question']==input]]


        # Creates new QuestionView if data are updated by user input
        self.question_views = [QuestionView(self)] 

        for q, d in zip(self.question_views, newdata):
            q.update(input = d)

        # Bind mouse wheel input to widgets in QuestionView
        for widget in self.frame.winfo_children():
            widget.bind("<MouseWheel>", self.scroll_handler.on_mouse_wheel)  # Windows/Linux
            widget.bind("<Button-4>", self.scroll_handler.on_mouse_wheel)  # macOS scroll up
            widget.bind("<Button-5>", self.scroll_handler.on_mouse_wheel)  # macOS scroll down   

        #print(f"Width of questionnaire view root frame: {self.frame.winfo_width()}")