class Data():

    def __init__(
            self, 
            database=None,
            file=None,
            study=None, 
            questionnaire=None,
            questions=None,
            data_update=None,
        ):

        self.database = database
        self.file = file
        self.study = study
        self.questionnaire = questionnaire
        self.questions = questions
        self.data_update = data_update

    def update(self, event=None, input=None, output=None, study=None, questionnaire=None):

        c_study = self.study.get()
        c_questionnaire = self.questionnaire.get()
        new_data = False

        # Case: New study or questionnaire provided in update()
        if (study is not None) | (questionnaire is not None):
            if (study is not None) & (study!=c_study):
                self.study.set(study)
                new_data = True
            if (questionnaire is not None) & (questionnaire!=c_questionnaire):
                self.questionnaire.set(questionnaire)
                new_data = True

            # Update questions panel if necessary
            if new_data==True:
                study = self.study.get()
                questionnaire = self.questionnaire.get()
                file = self.database.questionnaire_to_file[(study, questionnaire)]['file']
                self.questions.set(self.database.file_to_questionnaire[file]['questions'])
                self.data_update.set(True)
            return
        
        # Case: file updated by user
        file = self.file.get()
        self.study.set(self.database.file_to_questionnaire[file]['study'])
        self.questionnaire.set(self.database.file_to_questionnaire[file]['questionnaire'])
        self.questions.set(self.database.file_to_questionnaire[file]['questions'])
        self.data_update.set(True)
        return
        

