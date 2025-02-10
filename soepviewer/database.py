
import os
from pathlib import Path
import re
import pandas as pd
import numpy as np
from pandas import DataFrame
import soepdoku as soep
from soepdoku.const import DATA_SCALES
from soepdoku.utils import listify
from soepdoku.merge import concat_str_cols, merge_quest_log_gen

class Database():

    def __init__(self, paths, doku_repos, version):

        self.paths = paths # paths to all relevant questionnaires
        self.doku_repos = doku_repos # paths to Documentation top level, ex.: ['C:/Dokumentation', 'C:/Dokumentation_2']
        self.version = version # ex.: 'v39'
        self.questions = None
        self.logical_variables = None
        self.generations = None
        self.answers = None
        self.questions_var = None
        self.file_to_questionnaire = None
        self.questionnaire_to_file = None


    def build(self, create_context=True):
        
        self.questions = self.stack_questions()

        if create_context:
            self.questions = self.create_context(self.questions, columns=['text_de']) # 'instruction_de'

        self.logical_variables = self.stack_logical_variables()

        self.generations = self.stack_generations()

        self.answers = self.stack_answers()

        return None


    def merge_quest_log_gen(self):
        
   
        if self.logical_variables is None:
            self.logical_variables = DataFrame(
                columns=['study', 'dataset', 'variable', 'questionnaire', 'question', 'item']
                )
        
        if self.generations is None:
           self.generations = DataFrame(
               columns=[
                    'input_study', 'input_version', 'input_dataset', 'input_variable',
                    'output_variable', 'output_dataset', 'output_version', 'output_study'
                ]
           )

        item_to_variables = merge_quest_log_gen(
            self.questions, 
            self.logical_variables, 
            self.generations, 
            show_dataset=True, 
            show_version=True
        )

        questions = pd.merge(
            self.questions, 
            item_to_variables, 
            how='left',
            on=['study', 'questionnaire', 'question', 'item']
        )   

        # One row per variable
        quest_expl = questions[['study', 'questionnaire', 'question', 'item', 'scale', 'output']].copy()
        #quest_expl['output'] = quest_expl['output'].replace(to_replace='v0', value='') # if output='v0'
        quest_expl['output'] = quest_expl['output'].apply(lambda x: x.split(','))
        quest_expl = quest_expl.explode('output').reset_index()

        # Transform strings in 'output' (ex. v39/lee2estab/elb0001) to separate columns
        new_cols = ['version', 'dataset', 'variable']
        #quest_expl[new_cols] = quest_expl['output'].apply(lambda x: x.split('/')).apply(pd.Series)
        quest_expl[new_cols] = quest_expl['output'].apply(lambda x: split_string(x)).apply(pd.Series)
        quest_expl[new_cols] = quest_expl[new_cols].fillna('')

        # Remove version suffices, ex.: elb0001_v1 -> elb0001
        quest_expl['item_nov'] = quest_expl['item'].apply(lambda item: remove_version_suffix(item))
        quest_expl['variable_nov'] = quest_expl['variable'].apply(
            lambda item: remove_version_suffix(item))
        
        quest_expl = quest_expl.sort_values(by=['dataset', 'version', 'variable'])
        self.questions_var = quest_expl


    def stack_questions(self):
        # Read and append questions.csv
        relevant_cols = ['study', 'questionnaire', 'question', 'item', 'text_de', 'instruction_de', 'scale', 'answer_list']

        dfs = [soep.read_csv(f) for f in self.paths]

        self.file_to_questionnaire = {}
        self.questionnaire_to_file = {}

        for df, f in zip(dfs, self.paths):
            _study = df.loc[0, 'study']
            _questionnaire = df.loc[0, 'questionnaire']
            self.file_to_questionnaire[f] = {
                'study': _study, 
                'questionnaire': _questionnaire,
                'questions':  df['question'].unique().tolist(),
            }

            self.questionnaire_to_file[(_study, _questionnaire)] = {
                'file': f,
            }
    
        questions = self.stack_dfs(dfs, relevant_columns=relevant_cols)

        return questions


    def stack_logical_variables(self):
        
        # Get all logical_variables.csv

        datasets = []
        relevant_cols = [
            'study',
            'dataset',
            'variable', 
            'questionnaire', 
            'question',
            'item'
        ]

        for path in self.paths:
            parent = Path(path).parents[0]
            logicals_file = Path.joinpath(parent, 'logical_variables.csv')

            try:
                datasets.append(soep.read_csv(logicals_file))
            except:
                pass
                
        logical_variables = self.stack_dfs(datasets, relevant_columns=relevant_cols)

        return logical_variables


    def stack_generations(self, versions=None):

        relevant_cols = [
            'input_study',
            'input_version',
            'input_dataset',
            'input_variable',
            'output_variable',
            'output_dataset',
            'output_version',
            'output_study',
        ]

        if versions is None:
            versions = self.version

        # Get paths to all relevant generations.csv, takes time
        files = []
        for doku_repo in self.doku_repos:
            files += get_paths(doku_repo, filename = 'generations.csv', include_version_dir=versions, ignore_top_level=True)
       
        # Read and append
        dfs = [soep.read_csv(f) for f in files]
        generations = self.stack_dfs(dfs, relevant_columns=relevant_cols)

        return generations
    

    def stack_dfs(self, dfs, relevant_columns=None):

        if relevant_columns is None:
            relevant_columns = []

        dfs = [df for df in dfs if all([col in df.columns for col in relevant_columns])]
        dfs = [df[relevant_columns] for df in dfs]
        
        n = len(dfs)
        if n==0:
            return None
        elif n==1:
            return dfs[0]
        else:
            stacked = dfs[0]

            for df in dfs[1:]:
                stacked = pd.concat([stacked, df], ignore_index=True)

        return stacked


    def stack_answers(self):

        if self.file_to_questionnaire is None:
            return

        dfs = []

        for f in self.paths:

            study = self.file_to_questionnaire[f]['study']
            questionnaire = self.file_to_questionnaire[f]['questionnaire']

            try:
                answers_file = os.path.join(Path(f).parents[0], 'answers.csv')
                dfs.append(soep.read_csv(answers_file))
            except:
                pass
        relevant_cols = ['study', 'questionnaire', 'answer_list', 'value', 'label_de', 'label']
        answers = self.stack_dfs(dfs, relevant_columns=relevant_cols)
        return answers
    

    def create_context(self, df, columns=None):

        """Creates an extented string that includes an item's text plus its question context 

        Parameters
        ----------
        data : DataFrame
            A Soep-style questionnaire as DataFrame
        columns : list of strings
            Columns that contain contextual information, ex.: ['text_de', 'instruction_de']

        Returns
        -------
        DataFrame
            Returns data with the additional column 'context'

        """

        # Select items that provide context
        context_items = ~df['scale'].isin(DATA_SCALES)
        df.loc[context_items, 'context'] = df.apply(
                lambda x: concat_str_cols(x, columns, sep=' '), axis=1
            )
        
        df.loc[~context_items, 'context'] = ""

        # Cast context to corresponding items
        question_id = ['study', 'questionnaire', 'question']
        context_by_question = df.groupby(question_id, as_index=False)['context'].apply(
            lambda x: _single_space_join(x)
            )
        df = df.merge(context_by_question, how='left', left_on=question_id, right_on=question_id)
        df = df.rename(columns={'context_y': 'context'}).drop(columns=['context_x'])

        return df
    

def _single_space_join(x):
    result = ""
    for row in x:
        if isinstance(row, float):
            if ~np.isnan(row):
                result += ' ' + str(row)
        else:
            if row != "":
                result += ' ' + row
    return result.strip()
            

def split_string(string):
    result = string.split('/')
    if len(result)!=3:
        result = [np.nan, np.nan, np.nan]
    return result

def is_version_string(string):    
    if re.search('v[0-9].', string) is not None:
        return True
    return False


def remove_version_suffix(string):

    versionsuffix = re.search('_v[0-9]*', string) # ex.: '_v1'
    if versionsuffix is not None:
            return string[:versionsuffix.start()] # everything before '_v1'  
    return string


def search_files(
        path,
        filename="", 
        include_version_dir=None,
        skip_dir=None,
        key_value=None,
        ignore_top_level=False
        ):
    """Walks through the directories in path and searches for CSVs.

    Parameters
    ----------   
    path : str or path object
        Search in this path
    filename : str, optional
        Search for files with this name.
    include_version_dir: list of str, optional
        Include these directories of versions in search. Has precedence over skip_dir
        Example: include_version_dir = ['v39', 'v40']
    skip_dir : list of str, optional
        Skip these directories in search (default None)
    ignore_top_level: bool, optional
        Ignore files that are not in a version directory, ex.: Ignore datasets/ap/generations.csv (default False) 
    key_value : dict
        Return only paths to CSVs that contain specified value in column.
        Example: key_value={'name': 'soep-core-2021-pe'} returns only CSVs
        that contain 'soep-core-2021-pe' in column 'name'.

    Returns
    -------
        list of str or path objects
    
    """
    results = []
    
    for root, dirs, files in os.walk(path, topdown=True):

        basename = os.path.basename(root) # ex.: basename = 'v37', or 'pl'
       
        if skip_dir is not None:
            if basename in skip_dir:
                files = []

        if include_version_dir is not None:
            if (is_version_string(basename)) & (basename not in include_version_dir):
                files = []

        if (ignore_top_level==True) & (not is_version_string(basename)):
            files = []

    
        for file in files:
            if (file.endswith(".csv")) and (filename==file):

                if key_value is None:
                    results.append(os.path.join(root, file))
                else:
                    try:
                        result = search_csv(os.path.join(root, file), key_value)
                    except:
                        pass
                    else:
                        if result is not None:
                            results.append(result)
    return results

def search_csv(path, key_value):
    """ Searches in CSV for key_value
    
    Parameters
    ----------
    path : str or path object
        Path to a single CSV file.
    key_value : dict
        Search for {key: values} in CSV. key are colum names. Values are search strings or list of
        search strings. For a single key, the search is successful if at least one value of list is found.
        For multiple keys, the search is successful if all keys were a success. 
        Function assumes that dict is ordered.

    Returns
    -------
    str or path object
        Path to CSV if key_value was found. Else returns None.
    
    """

    if key_value is None:
        return path

    # Open csv and search
    import csv

    found = [False for i in range(len(key_value))]

    key_value = listify(key_value)
   
    with open(path, newline="", encoding="utf-8") as csvfile:
        
        reader = csv.DictReader(csvfile)
    
        for row in reader:
            for i, (key, values) in enumerate(key_value.items()):
                if (row[key] in values) & (row[key]!=""):
                    found[i] = True
            if all(found):
                break
    if all(found):
        return path

def get_paths(
        path, 
        filename='logical_variables.csv', 
        col_value=None, 
        include_version_dir=None, 
        skip_dir=None, 
        ignore_top_level=False
        ):

    """Gets all absolute paths to CSVs in SOEP Dokumentation/questionnaires and 
    Dokumentation/datasets. 
    
    Parameters
    ----------  
    path : str or path object
        Path to SOEP Dokumentation repository
    filename : str, optional
        Name of CSV that is searched for (defaut 'logical_variables')
    col_value : dict or Pandas DataFrame, optional
        Return only paths to CSVs that contain specified value in column.
        Example: col_value={'name': 'soep-core-2021-pe'} returns only CSVs
        that contain 'soep-core-2021-pe' in column 'name'.
    include_version_dir: list of str, optional
        Include these directories of versions in search. Has precedence over skip_dir
        Example: include_version_dir = ['v39', 'v40']
    skip_dir : list of str, optional
        Skip these directories in search (default None)
    ignore_top_level: bool, optional
        Ignore files that are not in a version directory, ex.: Ignore datasets/ap/generations.csv (default False) 

    Returns
    -------
    list of str
        List of absolute paths 

    """

    datapath = os.path.join(path, 'datasets')
    questpath = os.path.join(path, 'questionnaires')

    if col_value is not None:
        if isinstance(col_value, DataFrame):
            name = col_value.loc[0, 'questionnaire']
            key_value = {'questionnaire': name}

        elif isinstance(col_value, dict):
            key_value = col_value
    else:
        key_value = None
    
    # Find *.csv
    paths = []
    for path in [datapath, questpath]:
        result = search_files(
            path,
            key_value=key_value,
            filename=filename,
            include_version_dir=include_version_dir,
            skip_dir=skip_dir,
            ignore_top_level=ignore_top_level
        )
        paths += result
    return paths




