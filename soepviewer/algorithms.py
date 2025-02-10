import numpy as np
import pandas as pd
from soepdoku.const import DATA_SCALES
from soepdoku.merge import _concat_columns_to_array
import threading

class LevenshteinSimilarity():

    def __init__(
            self,
            study,
            questionnaire,
            database,
        ):

        import Levenshtein

        self.study = study
        self.questionnaire = questionnaire
        self.database = database
        self.distance = Levenshtein.distance
        self.similar_questions = None

    def update_data(self):

        study = self.study.get()
        questionnaire = self.questionnaire.get()
        
        mask = ((self.database.questions['study']==study) &
                (self.database.questions['questionnaire']==questionnaire))
        
        #mask2 = ((self.database.questions['study']=='soep-core') &
        #        (self.database.questions['questionnaire']=='soep-core-2021-lee2estab'))
        
    
        self.similar_questions = self.get_similar_questions(
            self.database.questions[mask],
            self.database.questions[~mask],
            compare_columns=['context', 'text_de'], # order of columns determines order of string concatenation
        )
        
    def get_data(self, study, questionnaire, question):
        
        data = self.similar_questions.loc[
            (self.similar_questions['study']==study) & 
            (self.similar_questions['questionnaire']==questionnaire) &
            (self.similar_questions['question']==question),
            ['study_out', 'questionnaire_out', 'question_out', 'distance']
        ]
        
        data = data.groupby(
            ['study_out', 'questionnaire_out', 'question_out'], as_index=False
        ).min(
            'distance'
        ).to_dict('records')

        return data


    def get_similar_questions( 
            self,
            questionnaire1,
            questionnaire2,
            compare_columns = ['context', 'text_de'],
            n=10,
        ):

        """For each question in questionnaire1, find the n most similar questions
        in questionnaire2 

        Parameters
        ----------
        questionnaire1 : DataFrame
        questionnaire2 : DataFrame
        compare_columns : list of str
            List of column names of questionnaire1 and questionnaire2 that are compared to each other.
        algorithm : str, optional
            Algorithm to calculate similarity between questions.
        Returns
        -------
        DataFrame

        """
          
        # Select only items that contain data
        mask1 = questionnaire1.scale.isin(DATA_SCALES)
        mask2 = questionnaire2.scale.isin(DATA_SCALES)

        texts1 = _concat_columns_to_array(questionnaire1.loc[mask1, compare_columns])
        texts2 = _concat_columns_to_array(questionnaire2.loc[mask2, compare_columns])
        indices1 = questionnaire1[mask1].index
        indices2 = questionnaire2[mask2].index

        question_ids = pd.factorize(
            questionnaire2.loc[
                mask2, ['study', 'questionnaire', 'question']
             ].apply(tuple, axis=1)
        )[0]

        calculate = True
        df = None

        #i1 = questionnaire1.loc[
        #    (questionnaire1['question']=="44a") & (questionnaire1['item']=="anz_homeoffice")].index[0]
        #i2 = questionnaire2.loc[
        #       (questionnaire2['study']=="soep-core") &
        #        (questionnaire2['questionnaire']=="soep-core-2023-lee2estab") &
        #       (questionnaire2['question']=="28") & 
        #        (questionnaire2['item']=="elb0245_v2")
        #    ].index[0]
        
        #i1 = indices1.tolist().index(i1)
        #print(f"Indices {i1} {i2}")


        if calculate:

            result = np.full((sum(mask1), n, 3), np.nan)

            for i, s1 in enumerate(texts1):
          
                for j, s2, qid in zip(indices2, texts2, question_ids):

                    newdist =  self.distance(s1, s2)/(max(len(s1), len(s2)))

                    maximum = np.max(result[i][:][:, 1]) # current max distance
                    idx = np.argmax(result[i][:][:, 1]) # index of maximum
                    #qid_max = result[i][:][:, 2] # question id of current maximum
                    
                    # Question already in result?
                    try:
                        idx_q = np.nonzero(result[i][:][:, 2]==qid)[0][0]
                        #maximum_q = result[i][idx_q][1]
                    except:
                        idx_q = None
                        maximum_q = None

                    # if new value is lower than current maximum
                    if (np.isnan(maximum)) | (newdist<maximum):

                        # new question not in result -> add question
                        if (idx_q is None):        
                            result[i][idx][0] = j
                            result[i][idx][1] = newdist        
                            result[i][idx][2] = qid
                        
                        # New question already in result
                        # -> Update its value if new value is lower than its current value
                        elif (idx_q is not None) & (idx_q==idx):
                            result[i][idx_q][0] = j
                            result[i][idx_q][1] = newdist

                        # Don't add a question twice
                        else:
                            pass

                    # Don't add new values > current maximum 
                    else:
                        pass



            # Merge result to questionnaire1
            d0, d1, d2 = result.shape
            arr_reshaped = result.reshape(d0*d1, 3)
            df = pd.DataFrame(arr_reshaped, columns=['index_2', 'distance', 'question_id'])
            df['index_1'] = np.repeat(indices1, n)
        
            #questionnaire1.loc[mask1, ['index_2', 'distance']] = result

            df = pd.merge(
                df,
                questionnaire1[['study', 'questionnaire', 'question', 'item']],
                left_on='index_1',
                right_on=questionnaire1.index,
                how = 'left',
            )

            df = pd.merge(
                df,
                questionnaire2[['study', 'questionnaire', 'question', 'item']],
                left_on='index_2',
                right_on=questionnaire2.index,
                how = 'left',
                suffixes = ['', '_out'],
            )

        return df


class ItemNameSimilarity():

    def __init__(self, data):
        self.data = data

    def update_data(self):
        pass

    def get_data(self, study, questionnaire, question):

        # Get item and variable names associated with a question
        search_for = self.data.loc[
            (self.data['study']==study) &
            (self.data['questionnaire']==questionnaire) & 
            (self.data['question']==question) & 
            (self.data['scale'].isin(['bin', 'cat', 'int', 'chr'])),
            ['item_nov', 'variable_nov'] # item and variable name without version suffix
        ].values

        
        search_for = set([i for row in search_for for i in row if (i!='') & (not self._is_numeric(i))])

        # Search for other questions with same item/variable names
        select1 = (
            (self.data['item_nov'].isin(search_for)) | 
            (self.data['variable_nov'].isin(search_for))
            )
        select2 = ~(
            (self.data['study']==study) &
            (self.data['questionnaire']==questionnaire) &
            (self.data['question']==question)
        )

        index = self.data.loc[(select1 & select2)].index
        index = index.drop_duplicates()
        
        matches = self.data.loc[
            index, ['study', 'questionnaire', 'question']
            ].groupby(
                ['study', 'questionnaire', 'question'], as_index=False
            ).first(
            ).rename(
                columns={
                    'study': 'study_out',
                    'questionnaire': 'questionnaire_out',
                    'question': 'question_out'
                }
            ).to_dict('records')
                
        return matches
            
        #select = pd.Series(False, index=self.data.index)
        #for match in matches:
        #    select |= (self.data['study']==match['study']) & (self.data['questionnaire']==match['questionnaire']) & (self.data['question']==match['question'])
        
        #return self.data[select]

    def _is_numeric(self, string):
        # series.str.fullmatch(r'[\+-]?\d+') # is string integer?
        try:
            int(string)
        except ValueError:
            return False                         
        else:
            return True


class ThreadedTask(threading.Thread):
    """Creates a threaded task. The task is executed by calling
    the start() method of ThreadedTask. The tasks communicates with the tkinter
     app through a queue.Queue() instance. """

    def __init__(self, queue, target_func):
        super().__init__()
        self.queue = queue
        self.target_func = target_func
    def run(self):
        self.target_func() # execute target function
        self.queue.put("Finished")
       

