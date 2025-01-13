import tkinter as tk
import tkinter.ttk as ttk
from soepversionizer import Database
from soepversionizer.algorithms import get_questions_with_same_item_name
from soepversionizer.const import FONTS, HEIGHT, PADDINGS, WIDTH
from soepversionizer.data import Data
from soepversionizer.questionnaireview import QuestionnaireView, ScrollFrame
from soepversionizer.questionview import QuestionView
from soepversionizer.nav_elements import FileMenu, QuestionButtons
from ctypes import windll


class Versionizer():

    def __init__(self, questionnaire_files, doku_repos, version, build_db_at_start=True, questions=None, quest_expl=None):

        windll.shcore.SetProcessDpiAwareness(1) # sharp fonts on Windows

        # Build database at startup
        if build_db_at_start==True:
            database = Database(paths = questionnaire_files, doku_repos=doku_repos, version=version)
            database.build()
            questions, quest_expl = database.merge_quest_log_gen()

        self.questionnaire_files = questionnaire_files
        self.questions = questions
        self.quest_expl = quest_expl
    
        #############################################################
        # Layout 
        ############################################################
        self.root = tk.Tk()
        self.root.title("SOEP Variable Versionizer")

        self.width = WIDTH
        self.height = HEIGHT
        self.root.geometry(f"{self.width}x{self.height}")
        self.font_main = FONTS['main']
        
        ### Main grid layout
        self.root.columnconfigure(0, weight=1) # content column
        self.root.columnconfigure(1, weight=0) # scrollbar
        self.root.columnconfigure(2, weight=1) # content column 
        self.root.columnconfigure(3, weight=0) # scrollbar  
  

        ### Dropdown menu for file selection
        self.selected_file1 = tk.StringVar(self.root)
        self.selected_file1.set(self.questionnaire_files[0])
        self.selected_study1 = tk.StringVar(self.root)
        self.selected_study1.set("")
        self.selected_questionnaire1 = tk.StringVar(self.root)
        self.selected_questionnaire1.set("")
        self.selected_file2 = tk.StringVar(self.root)
        self.selected_file2.set(self.questionnaire_files[0])

        menu_left = FileMenu(
            self.root,
            textvariable=self.selected_file1, 
            values=self.questionnaire_files,
            row=0,
            column=0,
        )
        
        menu_right = FileMenu(
            self.root, 
            textvariable=self.selected_file2,
            values=self.questionnaire_files,
            row=0,
            column=2,
        ) 

        ### Buttons for question selection
        buttons_left = QuestionButtons(self.root, row=1, column=0)
        buttons_right = QuestionButtons(self.root, row=1, column=2)
        
        ### Viewers to show selected questions
        self.scroll_frame_left = ScrollFrame(root=self.root, row=2, column=0)
        self.scroll_frame_right = ScrollFrame(root=self.root, row=2, column=2)

        self.questionnaire_view1 = QuestionnaireView(self.scroll_frame_left.frame)
        self.questionnaire_view2 = QuestionnaireView(self.scroll_frame_right.frame)
        #self.questionnaire_view3 = QuestionnaireView(self.scrollable_frame, col=0, row=3, title="Associated questions" )

        ########################################
        # Functionality
        ########################################

        ### Data objects for currently loaded data
        self.data1 = Data(
            viewer = self.questionnaire_view1,
            buttons = buttons_left,
            #associated_viewer=self.questionnaire_view3
        )

        self.data2 = Data(
            viewer = self.questionnaire_view2,
            buttons = buttons_right
        )

        # Set target of file menu
        menu_left.set_target(self.data1)
        menu_right.set_target(self.data2)

        # Set target of buttons
        buttons_left.set_viewers([self.questionnaire_view1])
        buttons_right.set_viewers([self.questionnaire_view2])


        #self.data3 = Data(
        #    viewer = self.questionnaire_view3,
        #   buttons = None,
        #    data = self.questions,
        #    aux_data= self.quest_expl,
        #)

        # Configure views
        #self.questionnaire_view3.data = self.questions
        #self.questionnaire_view3.aux_data = self.quest_expl

        #self.questionnaire_view1.update = MethodType(select_new_question, self.questionnaire_view1)
        #self.questionnaire_view2.update = MethodType(select_new_question, self.questionnaire_view2)
        #self.questionnaire_view3.update = MethodType(show_questions_with_same_item_name, self.questionnaire_view3)

        self.root.mainloop()

        


#### Different update functions for QuestionnaireView
def select_new_question(self, event=None, input=None, output=None):

     # Get new data
    newdata = [self.data.loc[self.data['question']==input]]

    # Remove previous view
    for widget in self.frame.winfo_children():
        widget.destroy()

    self.quest_views = [QuestionView(self, data=self.data)]

    for q, d in zip(self.quest_views, newdata):
        q.update(input = d)


def show_questions_with_same_item_name(self, event=None, input=None, output=None):

    # Remove previous view
    for widget in self.frame.winfo_children():
        widget.destroy()

    # Get new data
    newdata = get_questions_with_same_item_name(
        self.data, 
        self.aux_data, 
        study=self.study, # study of viewer1/data1
        questionnaire=self.questionnaire, # questionnaire of viewer/data 1 
        #study = 'soep-core',
        #questionnaire = 'soep-core-2021-lee2estab',
        question=input
    )
    self.quest_views = [QuestionView(self, data=self.data)]
    self.quest_views[0].update(input = newdata)
 

