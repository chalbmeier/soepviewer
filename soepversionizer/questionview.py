import tkinter as tk
from soepversionizer.const import COLUMNS, PADDINGS


class QuestionView:

    def __init__(self, root, col=None, row=None, data=None):
        self.root = root
        self.data = data

    def update(self, event=None, input=None, output=None):
        self.data = input
        #self.col1_width = self.root.get_max_col1_length()

        question_groups = self.data.groupby(
            ['study', 'questionnaire', 'question']
        ).size().reset_index()
        
        i = 0 # row count
        for group in question_groups.iterrows():
            study = group[1]['study']
            questionnaire = group[1]['questionnaire']
            question_number = group[1]['question']

            # Display "title" of question
            self.display('Question: '+ question_number, row=i, column=0, height=1, width=20)
            self.display(f'{study}/{questionnaire}', row=i, column=1, height=1, width=40)

            # Display question content
            data = self.data.loc[(
                self.data['study']==study) &
                (self.data['questionnaire']==questionnaire) & 
                (self.data['question']==question_number)]
    
            text = self.data_to_text(data)
            self.display(text, row=i+1, column=1, height=text.count('\n')+4, width=40)
        
            i += 2

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

    def display(self, text, row, column, height=1, width=None):

        text_box = tk.Text(
            self.root.frame,
            height=height, 
            #width=30,
            wrap=tk.WORD, 
            borderwidth=0, 
            bg='green'
        ) 


        text_box.insert(tk.END, text)
        text_box.grid(row=row, column=column, sticky="ew", **PADDINGS['normal'])
        # Reset height 
        #height = text_box.tk.call((text_box._w, "count", "-update", "-displaylines", "1.0", "end"))
        #print(height)
        #self.root.frame.update_idletasks()
        height2 = text_box.count("1.0", "end", "displaylines", "update") # "update"
        height3 = text_box.count("1.0", "end", "lines", "update")
        print(f"Width of scrollable frame at adjusting start: {self.root.frame.winfo_width()}")
        #print(height2, height3)
        #https://stackoverflow.com/questions/33785771/tkinter-counting-lines-in-a-text-widget-with-word-wrapping#comment123556474_33787358

        #text_box.configure(state="disabled", height=height2)

        
        
        
   
