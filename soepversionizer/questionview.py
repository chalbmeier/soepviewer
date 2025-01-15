import pandas as pd
import tkinter as tk
from soepversionizer.const import COLUMNS, PADDINGS
from soepversionizer.input_handlers import ScrollEventHandler


class QuestionView:

    def __init__(self, root, col=None, row=None, data=None):
        self.root = root
        self.width = self.root.frame.winfo_width() # width of parent frame in px
        self.data = data

    def update(self, event=None, input=None, output=None):
        self.data = input
        #self.col1_width = self.root.get_max_col1_length()

        questions = self.data.groupby(
            ['study', 'questionnaire', 'question']
        ).size().reset_index()
        
        i = 0 # row count
        for question in questions.iterrows():
            study = question[1]['study']
            questionnaire = question[1]['questionnaire']
            question_number = question[1]['question']

            # Display "title" of question
            self.display('Question: '+ question_number, row=i, column=0, height=1)
            self.display(f'{study}/{questionnaire}', row=i, column=1, height=1)
            i += 1

            # Display question content
            data = self.data.loc[(
                self.data['study']==study) &
                (self.data['questionnaire']==questionnaire) & 
                (self.data['question']==question_number)]

            display_instruction = True
            display_scale = False
            display_answers = True

            if display_answers==True:
                # Get pattern of anwer_lists of current question
                item_answerlist = (data
                                   .loc[data['answer_list']!="", ['item', 'answer_list']]
                                   .sort_index()
                                   .reset_index())
                
                item_answerlist['next_is_equal'] = item_answerlist['answer_list']==item_answerlist['answer_list'].shift(-1)

            for item in data.iterrows():
                text1= item[1]['item']
                self.display(text1, row=i, column=0, height=self.get_lines(text1, col_split=0.2))

                text2 = item[1]['text_de']

                if display_instruction==True:
                    instruction = item[1]['instruction_de']
                    if instruction!="":
                        text2 += '\n' + instruction

                if display_scale==True:
                    scale = item[1]['scale']
                    if scale!="":
                        text2 += '\n' + scale

                self.display(text2, row=i, column=1, height=self.get_lines(text2, col_split=0.8))
            
                i += 1
                
                if display_answers==True:
                    
                    if print_answer_list(item[1]['item'], item_answerlist)==True:

                        answer_list = item[1]['answer_list']    
                        answers_string = answers_as_string(
                            self.root.answers,
                            select_dict={'answer_list': answer_list},
                            remove_missings=False
                        )

                        text1 = 'Answers'
                        self.display(text1, row=i, column=0, height=self.get_lines(text1, col_split=0.2))

                        text2 = answers_string
                        self.display(text2, row=i, column=1, height=self.get_lines(text2, col_split=0.8))

                        i+=1
                  

    def display(self, text, row, column, height=1):

        text_box = tk.Text(
            self.root.frame,
            height=height, 
            wrap=tk.WORD, 
            borderwidth=0, 
        ) 

        text_box.insert(tk.END, text)
        text_box.configure(state='disabled') # text is read-only
        text_box.grid(row=row, column=column, sticky="ne", **PADDINGS['normal'])  


    def data_to_text(self, df):
        text = ""
        rows = df.to_dict('index')
        for k, v in rows.items():
            col1_text = v[COLUMNS['item']] 
            #extra_space1 = self.col1_width - len(col1_text) + 2
            #text +=  col1_text + ' '*extra_space1 + v[COLUMNS['text']] + '\n'
            text += v[COLUMNS['text']] 

            instruction = v[COLUMNS['instruction']]
            if len(instruction)>0:
                text += instruction 
        return text

          
        
    def get_lines(self, string, col_split, font_pt=12):

        lines = 0
        for s in string.split('\n'):
            chars = len(s)
            width = col_split*self.width / (font_pt*1.333) # width of cell in points, refactor
            lines += 1 + int(chars/width)
        return lines
   
def print_answer_list(item, item_to_answerlist):
    """Looks for position of item + answer_list combination in item_to_answerlist.
    Returns True if item has an answer_list AND the subsequent item has a different answer_list.
    The function assumes that every value of item_to_answerlist['item'] is distinct. And the
    funtion assumes that item_to_answerlist['answer_list'] does not have missing values. 

    Parameters
    ----------
    item : str
        An item name
    item_to_answerlist : pandas DataFrame
        A DataFrame with columns 'item', 'answer_list', 'next_is_equal'

    Returns
    -------
    bool
    """

    if item not in item_to_answerlist['item'].values:
        return False

    return not item_to_answerlist.loc[item_to_answerlist['item']==item, ['next_is_equal']].values


def answers_as_string(df, select_dict=None, language='de', remove_missings=True):
    """Generates a string of value + label pairs in Pandas Dataframe"""

    if language=='de':
        label = 'label_de'
    else:
        label = 'label'

    # Select rows
    select = pd.Series(True, index=df.index)

    if select_dict is not None:
        for k, v in select_dict.items():
            select &= df[k]==v
    
    if remove_missings==True:
        select &= df[['value']].astype('int')>=0

    df = df[select]
    result = df.apply(lambda row: add_value_label_cols(row), axis=1)
    result = '\n'.join(result.values)

    return result

def add_value_label_cols(series):
    return '['+ series['value'] + '] ' + series['label_de']

