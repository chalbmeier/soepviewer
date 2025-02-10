import pandas as pd
import tkinter as tk

class QuestionView:

    def __init__(
            self,
            root,
            col=None,
            row=None,
            data=None,
            answers=None,
            layout=None,
        
        ):
        self.root = root
        self.width = self.root.frame.winfo_width() # width of parent frame in px
        self.data = data
        self.answers = answers
        self.layout = layout

    def update(self, event=None, data=None, data_aux=None, answers=None, output=None):
        self.data = data
        self.data_aux = data_aux
        self.answers = answers
       
       # Get content
        content = self.get_content(
            incl_instruction=True,
            incl_scale=True,
            incl_variables=True,
            incl_answers=True,
        )

        # Display content
        self.display(content)


    def get_content(
            self,
            incl_instruction=True,
            incl_scale=True,
            incl_variables=True,
            incl_answers=True
        ):


        # Group items into questions
        questions = self.data.groupby(
            ['study', 'questionnaire', 'question']
        ).size().reset_index()

        i = 0 # row count
        content = {}
        
        for question in questions.iterrows():

            study = question[1]['study']
            questionnaire = question[1]['questionnaire']
            question_number = question[1]['question']

            #### Title of question
            text = f'Frage {question_number}: {study}/{questionnaire}'
            content[i]  = [{'style': 'title', 'text': text}]

            i += 1

            data = self.data.loc[(
                self.data['study']==study) &
                (self.data['questionnaire']==questionnaire) & 
                (self.data['question']==question_number)]


            if incl_answers==True:
                all_answer_lists = data.loc[
                    data['answer_list']!="", 'answer_list'].values
                answer_list_printed = {al: False for al in all_answer_lists}

            ### Items
            for item in data.iterrows():
                
                # Item name
                item_name = item[1]['item']
                content[i] = [{'style': 'item_name', 'text': item_name}]
                i += 1
                
                # Scale
                if incl_scale==True:
                    scale = item[1]['scale']
                    if scale!="":
                        content[i] = [{'style': 'scale', 'text': scale}]                
                        i += 1 

                # Item text
                content[i] = [{'style': 'normal', 'text': item[1]['text_de']}]

                # Item instruction
                if incl_instruction==True:
                    instruction = item[1]['instruction_de']
                    if instruction!="":
                        content[i].append({'style': 'instruction', 'text': '\n' + instruction})
                i += 1

                # Item answer categories
                if incl_answers==True:
                    answer_list = item[1]['answer_list']  
                    if answer_list!="":
                        if answer_list_printed[answer_list]==False: # print answer_list only once
                     
                            answers_string = answers_as_string(
                                self.answers,
                                select_dict={'answer_list': answer_list},
                                remove_missings=False
                            )

                            content[i] = [{'style': 'normal', 'text': answers_string}]
                            answer_list_printed[answer_list] = True
                        
                            i+=1

                # Item variable names
                if incl_variables==True:
                  
                    variables = get_variables(
                        df=self.data_aux,
                        study=study,
                        questionnaire=questionnaire,
                        question=question_number,
                        item=item_name,
                        columns=['dataset', 'version', 'variable']
                    )

                    if (variables!="") & (variables!="/v0/"):
                        content[i] = [{'style': 'variable', 'text': variables}]
              
                i += 1
                
        return content


    def display(self, content):

        row = 0
        for _, cell_content in content.items():
            
            style = cell_content[0]['style']

            if style=="scale":
                row -= 1 # scale in same row as item name

            column, col_span, col_split = self.layout.get_column_params(style)

            self.add_text_box(
                cell_content,
                row=row,
                column=column,
                col_split=col_split,
                col_span=col_span
            )

            row += 1


    def add_text_box(self, cell_content, row, column, col_split, col_span):

        # Calculate number of lines in text box
        lines = self.get_lines(cell_content, col_split=col_split)

        text_box = tk.Text(
            self.root.frame,
            font=self.layout.font_sans_serif,
            height=lines, 
            wrap=tk.WORD, 
            borderwidth=0,
            bd=0,
            pady=0,
        )

        j = 1       
        for content in cell_content:

            # Configure text box style
            style = content['style']
            self.layout.tag_configure(text_box, style)

            text = content['text']
            text_box.insert(f"{j}.0", text)
            paragraphs = j + text.count('\n')
            text_box.tag_add(style, f"{j}.0", f"{paragraphs}.end")
    
            j = paragraphs + 1

        text_box.configure(state='disabled')  # text is read-only       

        text_box.grid(
            row=row,
            column=column,
            sticky="nw",
            **self.layout.paddings['normal'],
            columnspan=col_span
        )  
        
    
    def get_lines(self, cell_content, col_split, font_pt=12):

        total_text = ' '.join([i['text'] for i in cell_content])
        font_pt = self.layout.font_size_text

        lines = 0
        for s in total_text.split('\n'):
            chars = len(s)
            width = col_split*self.width / font_pt # width of cell in points
            lines += 1 + int(chars/width)
        return lines

   

def answers_as_string(df, select_dict=None, language='de', remove_missings=False):
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
        pass # implement

    df = df[select]
    result = df.apply(lambda row: add_value_label_cols(row), axis=1)
    result = '\n'.join(result.values)

    return result

def add_value_label_cols(series):
    return '['+ series['value'] + '] ' + series['label_de']


def get_variables(df, study, questionnaire, question, item, columns):
    selection = df.loc[
        (df['study']==study) &
        (df['questionnaire']==questionnaire) &
        (df['question']==question) &
        (df['item']==item),
        columns
    ].values
    
    variable_str = '\n'.join(['/'.join(row) for row in selection if any([i!="" for i in row])])

    return variable_str