import ctypes
from os.path import join
from pathlib import Path
from platformdirs import user_config_dir
import tkinter as tk
import tomllib
from .algorithms import ItemNameSimilarity, LevenshteinSimilarity
from .data import Data
from .database import Database
from .layout import Layout
from .questionnaireview import QuestionnaireView
from .nav_elements import Box, FileMenu, Popup, QuestionButtons
from .similarity_widgets import SimilarityWidget
from .utils import ListVar

class Versionizer():

    def __init__(
            self, 
            read_config=True,
            doku_repos=None, 
            questionnaire_files=None, 
            version=None,
            build_db_at_start=True,
            database=None,
            ):

        # Read config.toml
        self.config_file = None
        if read_config:
            doku_repos, version, questionnaire_files = self.read_config()

        # Start tkinter app instance
        self.set_dpi_awareness()
        self.db_loading_err = False
        self.root = tk.Tk()
        self.root.title("SOEP Metadata Viewer")
        self.root.lift() # Window to front at start
      
        # Build database at startup
        if build_db_at_start==True:
            database = self.create_database(
                doku_repos=doku_repos,
                version=version,
                questionnaire_files=questionnaire_files
            )
  
        self.questionnaire_files = questionnaire_files
        self.database = database

        #############################################################
        # Dynamically updated variables
        #############################################################
        self.file_left = tk.StringVar(self.root)
        self.file_left.set("Fragebogen auswählen")
        self.study_left = tk.StringVar(self.root)
        self.questionnaire_left = tk.StringVar(self.root)
        self.questions_left = ListVar(self.root)
        self.question_left = tk.StringVar(self.root)
        self.trigger_data_update_left = tk.BooleanVar(self.root)
        self.data_update_left = tk.BooleanVar(self.root)

        self.file_right = tk.StringVar(self.root)
        self.study_right = tk.StringVar(self.root)
        self.questionnaire_right = tk.StringVar(self.root)
        self.questions_right = ListVar(self.root)
        self.question_right = tk.StringVar(self.root)
        self.trigger_data_update_right = tk.BooleanVar(self.root)
        self.data_update_right = tk.BooleanVar(self.root)

        # Non-visible data object to manage data variables and their updates
        self.data_left = Data(
            database=self.database,
            file=self.file_left,
            study=self.study_left,
            questionnaire=self.questionnaire_left,
            questions=self.questions_left,
            data_update=self.data_update_left,
        )

        self.data_right = Data(
            database=self.database,
            file = self.file_right,
            study=self.study_right,
            questionnaire=self.questionnaire_right,
            questions=self.questions_right,
            data_update=self.data_update_right,
        )

        # Initialize algorithms
        item_name_similarity = ItemNameSimilarity(data=self.database.questions_var)

        levenshtein_similarity = LevenshteinSimilarity(
            database=self.database,
            study=self.study_left,
            questionnaire=self.questionnaire_left,
        )

        #############################################################
        # Layout 
        ############################################################
        self.layout = Layout(root=self.root)
        self.root.geometry(f"{self.layout.width}x{self.layout.height}")
        self.root.configure(background='white')

        ### Dropdown menu for file selection
        self.menu_left = FileMenu(
            self.root,
            textvariable=self.file_left, 
            study=self.study_left,
            questionnaire=self.questionnaire_left,
            questions=self.questions_left,
            trigger_data_update = self.trigger_data_update_left,
            values=self.questionnaire_files,
            file_to_questionnaire = self.database.file_to_questionnaire,
            layout=self.layout,
            row=0,
            column=0,
        )
        
        self.menu_right = FileMenu(
            self.root, 
            textvariable=self.file_right,
            study=self.study_right,
            questionnaire=self.questionnaire_right,
            questions=self.questions_right,
            trigger_data_update = self.trigger_data_update_right,
            values=self.questionnaire_files,
            file_to_questionnaire = self.database.file_to_questionnaire,
            questionnaire_to_file = self.database.questionnaire_to_file,
            layout=self.layout,
            row=0,
            column=2,
        ) 

        ### Buttons for question selection
        self.buttons_left = QuestionButtons(
            self.root,
            row=1,
            column=0,
            height=self.layout.buttons_widget.get_height(),
            selected=self.question_left,
            questions=self.questions_left,
            layout=self.layout.buttons_widget
        )

        self.buttons_right = QuestionButtons(
            self.root,
            row=1,
            column=2,
            height=self.layout.buttons_widget.get_height(),
            selected=self.question_right,
            questions=self.questions_right,
            layout=self.layout.buttons_widget,
        )

        self.bar1_left = Box(
            self.root,
            row=2,
            column=0,
            height=1,
            color='light grey',
            **self.layout.paddings['normal'],
        ) 

        self.bar1_right = Box(
            self.root,
            row=2,
            column=2,
            height=1,
            color='light grey',
            **self.layout.paddings['normal'],
        ) 

        ### Viewers to show selected questions
        self.questionnaire_view1 = QuestionnaireView(
            root=self.root, 
            row=3, 
            column=0, 
            height=self.layout.questions_widget.get_height(),
            padx=10,
            database=self.database,
            study=self.study_left,
            questionnaire=self.questionnaire_left,
            question=self.question_left,
            layout=self.layout.questions_widget
        )
    
        self.questionnaire_view2 = QuestionnaireView(
            root=self.root, 
            row=3, 
            column=2,
            height=self.layout.questions_widget.get_height(),
            padx=10,
            database=self.database,
            study=self.study_right,
            questionnaire=self.questionnaire_right,
            question=self.question_right,
            layout=self.layout.questions_widget
        )

        self.title_box_left = Box(
            self.root,
            row=4,
            column=0,
            height=1,
            layout=self.layout,
            color='gray98',
            text="Fragen mit demselben Item- oder Variablennamen",
            padx=10,
            pady=2,
            columnspan=2,
        ) 

        self.title_box_right = Box(
            self.root,
            row=4,
            column=2,
            height=1,
            layout=self.layout,
            color='gray98',
            text="Ähnliche Fragen (Levenshtein-Distanz)",
            padx=15,
            pady=2,
            columnspan=2,
        ) 

        self.similarity_widget_left = SimilarityWidget(
            root=self.root,
            row=5,
            column=0,
            height=self.layout.similarity_widget_left.get_height(),
            padx=15,
            study=self.study_left,
            questionnaire=self.questionnaire_left,
            question=self.question_left,
            output_study=self.study_right,
            output_questionnaire=self.questionnaire_right,
            output_data=self.data_right,
            output_question=self.question_right,
            algorithm=item_name_similarity,
            layout=self.layout.similarity_widget_left
        )

 
        self.similarity_widget_right = SimilarityWidget(
            root=self.root,
            row=5,
            column=2,
            height=self.layout.similarity_widget_right.get_height(),
            padx=10,
            study=self.study_left,
            questionnaire=self.questionnaire_left,
            question=self.question_left,
            output_study=self.study_right,
            output_questionnaire=self.questionnaire_right,
            output_data=self.data_right,
            output_question=self.question_right,
            algorithm=levenshtein_similarity,
            statistic='distance',
            layout=self.layout.similarity_widget_right,
        )

        self.footer_bar = Box(
            self.root,
            row=6,
            column=0,
            height=1,
            color='light grey',
            **self.layout.paddings['normal'],
            columnspan=4,
        ) 

        self.footer = Box(
            self.root,
            row=7,
            column=0,
            height=1,
            layout=self.layout,
            color='white',
            text=f"Einstellungen: {self.config_file}",
            padx=15,
            pady=2,
            columnspan=4,
        ) 

        if self.db_loading_err:
            err_text = (
                f"Eine oder mehrere der angegebenen Dateien wurden nicht gefunden.\n"
                f"Bitte die Angaben überprüfen:\n"
                f"\n"
                f"{self.config_file}\n"
            )
            popup = Popup(
                    self.root,
                    err_text,
                    width=650,
                    height=120, 
                    position='left',
                    title='Fehler'
                    )

            popup.show()

        ########################################
        # Functionality
        ########################################
        self.trigger_data_update_left.trace_add("write", self.data_left.update)
        self.data_update_left.trace_add("write", self.buttons_left.update)
        self.data_update_left.trace_add("write", self.questionnaire_view1.update_data)
        #self.data_update_left.trace_add("write", self.calculate)
        self.data_update_left.trace_add("write", self.similarity_widget_right.update_data)

        self.question_left.trace_add("write", self.questionnaire_view1.update)
        self.question_left.trace_add("write", self.similarity_widget_left.update)
        self.question_left.trace_add("write", self.similarity_widget_right.update)

        self.trigger_data_update_right.trace_add("write", self.data_right.update)
        self.data_update_right.trace_add("write", self.menu_right.check_file)
        self.data_update_right.trace_add("write", self.buttons_right.update)
        self.data_update_right.trace_add("write", self.questionnaire_view2.update_data)
        self.question_right.trace_add("write", self.questionnaire_view2.update)

        #self.run_asyncio_loop() # additional loop for pop-ups
        self.root.mainloop()

    def read_config(self):

        file = Path(user_config_dir(appname="soepviewer")) / "config.toml"
        
        # Create standard config if it does not exist
        if not file.exists():
            file.parent.mkdir(parents=True, exist_ok=True)
            with open(file, 'w') as f:
                f.write(self.standard_config())

        # Read and parse config file
        with open(file, 'rb') as f:
            config = tomllib.load(f)

        # Paths to documentation directories
        dokurepos = [path.strip() for path in config['dokurepos'].values()]
        
        # Version
        version = [version.strip() for version in config['versions']['versions']]
  
        # Paths to questionnaire CSVs
        questionnaire_files = []
        for k, path in config['dokurepos'].items():
            try:
                files = list(config['questionnaires'][k].values())[0]
                questionnaire_files += [join(path.strip(), file) for file in files]
            except:
                print("Something is wrong with config.toml") # implement proper exception

        self.config_file = file

        return dokurepos, version, questionnaire_files


    def set_dpi_awareness(self):
        """
        Set DPI awareness, relevant for retrieving geometry of 
        multi-screen setups and rendering of fontsg
        """
        try: # Windows 8.1 and later
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception as e:
            pass
        try: # Before Windows 8.1
            ctypes.windll.user32.SetProcessDPIAware()
        except: # Windows 8 or before
            pass

    def create_database(self, questionnaire_files, doku_repos, version):

        try:
            database = Database(paths = questionnaire_files, doku_repos=doku_repos, version=version)
            database.build(create_context=True)
            database.merge_quest_log_gen()
        except (FileNotFoundError, ValueError):
            self.db_loading_err = True

        return database
    
    def standard_config(self):
        config = (
            "[versions]\n"
            "versions = ['v39']  # Search for variable names in these versions, ex: versions = ['v39', 'v40']\n"
            "\n"
            "[dokurepos]\n"
            "path1 = 'C:/Users/chh/Work/02_git/Dokumentation/'  # path to SOEP-Core documentation\n"
            "path2 = 'C:/Users/chh/Work/02_git/soep-lee2-compare/' # path to SOEP-LEE2-Compare documentation\n"
            "\n"
            "[questionnaires.path1]\n"
            "files = [\n"
            "    'questionnaires/soep-core-2021-lee2estab/questions.csv',\n"
            "    'questionnaires/soep-core-2023-lee2estab/questions.csv',\n"
            "    'questionnaires/soep-core-2020-selfempl/questions.csv',\n"
            "    'questionnaires/soep-core-2022-selfempl/questions.csv',\n"
            "    'questionnaires/soep-core-2024-selfempl/questions.csv',\n"
            "]\n"
            "\n"
            "[questionnaires.path2]\n"
            "files = [\n"
            "    'questionnaires/soep-lee2-compare-2022-estab/questions.csv',\n"
            "    'questionnaires/soep-lee2-compare-2023-estab/questions.csv',\n"
            "    'questionnaires/soep-lee2-compare-2024-estab/questions.csv',\n"
            "]\n"
        )
        return config
    


def start():
    """Starts a new instance of the app. For command line."""
    Versionizer()


 

