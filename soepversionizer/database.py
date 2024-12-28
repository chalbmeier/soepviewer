
import os
from pathlib import Path
import re
import pandas as pd
from pandas import DataFrame
import soepdoku as soep
from soepdoku.utils import listify
from soepdoku.merge import merge_quest_log_gen

class Database():

    def __init__(self, paths, doku_repos, version):

        self.paths = paths # paths to all relevant questionnaires
        self.doku_repos = doku_repos # paths to Documentation top level, ex.: ['C:/Dokumentation', 'C:/Dokumentation_2']
        self.version = version # ex.: 'v39'
        self.questions = None
        self.logical_variables = None
        self.generations = None


    def build(self):
        
        self.questions = self.stack_questions()

        self.logical_variables = self.stack_logical_variables()

        self.generations = self.stack_generations()

        return None


    def merge_quest_log_gen(self):
            
        item_to_variables = merge_quest_log_gen(
            self.questions, 
            self.logical_variables, 
            self.generations, 
            show_dataset=False, 
            show_version=False
        )

        questions = pd.merge(
            self.questions, 
            item_to_variables, 
            how='left',
            on=['study', 'questionnaire', 'question', 'item']
        )

        quest_expl = questions[['item', 'output']].copy()
        quest_expl['output'] = quest_expl['output'].str.split(',')
        quest_expl = quest_expl.explode('output')
        quest_expl['item'] = quest_expl['item'].apply(lambda item: remove_version_suffix(item))
        quest_expl['output'] = quest_expl['output'].apply(lambda item: remove_version_suffix(item))

        return (questions, quest_expl)


    def stack_questions(self):
        # Read and append questions.csv
        relevant_cols = ['study', 'questionnaire', 'question', 'item', 'text_de', 'instruction_de', 'scale', 'answer_list']

        dfs = [soep.read_csv(f) for f in self.paths]
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
            files += get_paths(doku_repo, filename = 'generations.csv', include_version_dir=[versions], ignore_top_level=True)
        
        # Read and append
        dfs = [soep.read_csv(f) for f in files]
        generations = self.stack_dfs(dfs, relevant_columns=relevant_cols)

        return generations
    
    def stack_dfs(self, dfs, relevant_columns=None):

        if relevant_columns is None:
            relevant_columns = []

        dfs = [df for df in dfs if all([col in df.columns for col in relevant_columns])]
        dfs = [df[relevant_columns] for df in dfs]
        
        stacked = dfs[0]

        for df in dfs[1:]:
            stacked = pd.concat([stacked, df], ignore_index=True)

        return stacked
        

    def get_questions_with_same_name(self):

        # Get iassociated variable names of self.questionnaire
        names = self.get_variable_names(self)

        return None
    
    def get_variable_names(self):

        # Read logical_variables.csv
        parent = Path(self.questionnaire.path).parents[0]
        logicals_file = Path.joinpath(parent, 'logical_variables.csv') 
        try:
            logical_variables = soep.read_csv(logicals_file)
        except:
            logical_variables = None
        #print(logical_variables)
            

def is_version_string(string):    
    if re.search('v[0-9].', string) is not None:
        return True
    return False


def remove_version_suffix(string):

    versionsuffix = re.search('_v[0-9]*', string) # ex.: '_v1'
    if versionsuffix is not None:
            return string[:versionsuffix.start()] # everything before '_v1'  
    return string


def search_files(path, filename="",  include_version_dir=None, skip_dir=None, key_value=None, ignore_top_level=False):
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

def get_paths(path, filename='logical_variables.csv', col_value=None, include_version_dir=None, skip_dir=None, ignore_top_level=False):

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




