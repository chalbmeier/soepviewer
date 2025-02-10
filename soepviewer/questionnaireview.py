from .questionview import QuestionView
from .nav_elements import ScrollFrame


class QuestionnaireView(ScrollFrame):

    """A modified ScrollFrame that displays a question with its several items"""

    def __init__(
            self,
            root,
            height,
            column=None,
            row=None,
            database=None,
            title="",
            study=None,
            questionnaire=None,
            question=None,
            padx=5,
            pady=5,
            layout=None,
        ):
        
        super().__init__(
            root, 
            column=column, 
            row=row, 
            height=height, 
            column_config=layout.column_config,
            padx=padx,
            pady=pady,
            layout=layout,
            )
        
        self.database = database
        self.study = study
        self.questionnaire = questionnaire
        self.question = question
        self.data_subset = None
        self.questions_var_subset = None
        self.answers_subset = None

        self.quest_views = []


    def update_data(self, event=None, input=None, output=None):
        study = self.study.get()
        questionnaire = self.questionnaire.get()

        self.data_subset = self.database.questions.loc[
            (self.database.questions['study']==study) &
            (self.database.questions['questionnaire']==questionnaire)]
        
        self.questions_var_subset = self.database.questions_var.loc[
            (self.database.questions_var['study']==study) &
            (self.database.questions_var['questionnaire']==questionnaire)
        ]

        self.answers_subset = self.database.answers.loc[
            (self.database.answers['study']==study) &
            (self.database.answers['questionnaire']==questionnaire)
        ]

      
    def update_meta(self, study, questionnaire):
        self.study = study
        self.questionnaire = questionnaire

    def update(self, event=None, input=None, output=None):
    
        # Remove previous view
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Get new question
        question = self.question.get()
        newdata = [self.data_subset.loc[self.data_subset['question']==question]]
        newdata_aux = self.questions_var_subset.loc[(self.questions_var_subset['question']==question)]

        # Creates new QuestionView if data are updated by user input
        self.question_views = [QuestionView(self, layout=self.layout)] 

        for q, d in zip(self.question_views, newdata):
            q.update(data = d, data_aux=newdata_aux, answers=self.answers_subset)

        # Update layout of parent scrollable frame
        super().update()  