import queue
import tkinter as tk
from .algorithms import ThreadedTask
from .nav_elements import Popup, ScrollFrame


class SimilarityWidget(ScrollFrame):

    def __init__(
            self,
            root,
            height,
            column=None,
            row=None,
            padx=5,
            pady=5,
            title=None,
            study=None,
            questionnaire=None,
            question=None,
            output_study=None,
            output_questionnaire=None,
            output_data=None,
            output_question=None,
            algorithm=None,
            statistic=None,
            round_digits=3,
            layout=None,
    ):
                
        super().__init__(
            root, 
            column=column, 
            row=row, 
            height=height,
            padx=padx,
            pady=pady,
            column_config=layout.column_config,
            title = title,
            layout=layout,
        )
        
        self.study = study
        self.questionnaire = questionnaire
        self.question = question
        self.output_study = output_study
        self.output_questionnaire = output_questionnaire
        self.output_data = output_data
        self.output_question = output_question
        self.algorithm = algorithm
        self.statistic = statistic
        self.round_digits = round_digits
        self.selected = tk.StringVar(value="") # value of selected element

    def update_data(self, event=None, input=None, output=None):
        
        # Create a popup window
        self.popup = Popup(
            self.root,
            text="Levenshtein-Distanzen werden berechnet.\nBitte warten ...",
            width=450,
            height=100,
            position='left'
        )
        self.popup.show()


        # Calculation in separate thread
        self.queue = queue.Queue()
 
        ThreadedTask(
            queue=self.queue,
            target_func=self.algorithm.update_data
            ).start()
        
        self.root.after(100, self.process_queue)


    def process_queue(self):
        try:
            _ = self.queue.get_nowait() # Expects queued tasked to be finished
            self.popup.close()
        except queue.Empty:
            self.root.after(100, self.process_queue)
    

    def update(self, event=None, input=None, output=None):
       
        # Get new data
        question = self.question.get()
        study = self.study.get()
        questionnaire = self.questionnaire.get()

        data = self.algorithm.get_data(
            study=study,
            questionnaire=questionnaire,
            question=question
        )

        # display new data
        self.destroy()
        self.display(data)

    def destroy(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def display(self, data):

        # Sort
        if self.statistic is None:
            data = sorted(data, key=lambda d: (d['study_out'], d['questionnaire_out'], d['question_out']))
        else:
             data = sorted(data, key=lambda d: d[self.statistic])

        for i, entry in enumerate(data):
            text = '/'.join([entry[k] for k in ['study_out', 'questionnaire_out', 'question_out']])
            button = tk.Radiobutton(
                self.frame, 
                text=text,
                value=text,
                variable = self.selected,
                command=self.on_select,
                height=1,
                indicatoron=False,
                offrelief='flat', 
                overrelief='groove',
                pady=0,
                bg='white'
            )

            button.grid(row=i, column=0, padx=5, sticky='NW')

            if self.statistic is not None:
                label = tk.Label(
                    self.frame,
                    text=str(round(entry[self.statistic], self.round_digits)),
                    bg='white',
                    height=1,
                )
                label.grid(row=i, column=1, sticky='NE', padx=10)

            

        # Update layout of parent scrollable frame
        super().update()

    
    def on_select(self):
        study, questionnaire, question = self.selected.get().split('/')
        self.output_data.update(study=study, questionnaire=questionnaire)
        self.output_question.set(question)


