from pathlib import Path
from os.path import join
import soepdoku as soep
from soepversionizer.const import COLUMNS

class Data():

    def __init__(
            self, 
            viewer=None, 
            buttons=None, 
            data=None, 
            aux_data=None, 
            study=None, 
            questionnaire=None, 
            associated_viewer=None
        ):

        self.viewer = viewer
        self.buttons = buttons
        self.data = data
        self.aux_data = aux_data
        self.study = study
        self.questionnaire = questionnaire
        self.associated_viewer = associated_viewer
        self.questions = None
        self.max_col1_length = 7
        

    def update(self, event, input, output):

        # Load new data
        file = input.get()
        self.data = soep.read_csv(file)

        try:
            answers_file = join(Path(file).parents[0], 'answers.csv')
            self.answers = soep.read_csv(answers_file)
        except:
            self.answers = None

        self.questions = self.data['question'].unique().tolist()
        self.study = self.data.loc[0, 'study']
        self.questionnaire = self.data.loc[0, 'questionnaire']
        self.max_col1_length = max(len(i) for i in self.data[COLUMNS['item']].unique())

        # Update elements that display data
        if self.viewer is not None:
            self.viewer.updata_data(input=self)
        if self.associated_viewer is not None:
            self.associated_viewer.update_meta(study=self.study, questionnaire=self.questionnaire)
        if self.buttons is not None:
            self.buttons.update(input=self)

