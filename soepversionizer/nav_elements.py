import tkinter as tk
from tkinter import ttk
from soepversionizer.const import FONTS, PADDINGS

class FileMenu(ttk.Combobox):

    def __init__(self, root, textvariable, values, row=0, column=0, **kwargs):

        super().__init__(
            root, 
            textvariable=textvariable,
            values=values,
            state='readonly',
            width=300,
            font=FONTS['main'],
            **kwargs
        )

        self.root = root
        self.textvariable = textvariable
        self.grid(column=column, row=row, sticky=tk.W, **PADDINGS['normal'])

   
    def set_target(self, target):
        self.target = target
        self.bind("<<ComboboxSelected>>", lambda event: target.update(event, self.textvariable, target))
    

class QuestionButtons:

    def __init__(self, root, row=0, column=0):
        self.frame = tk.Frame(root)
        self.frame.grid(row=row, column=column, sticky="nsew", **PADDINGS['normal'])
        self.selected = tk.StringVar(value="") # value of selected button


    def set_viewers(self, viewers):
        self.viewers = viewers

    def update(self, event=None, input=None, output=None):

        # Remove old buttons
        for widget in self.frame.winfo_children():
            widget.destroy()

        i = 0
        j = 0

        for q in input.questions:
            text = f"{q}"
            button = tk.Radiobutton(
                self.frame, 
                text=text,
                value = text,
                variable=self.selected,
                indicatoron=False,
                command=self.on_select,
            )
            
            button.grid(row=i, column=j, **PADDINGS['small'])
            j +=1
            if j==20:
                i += 1
                j = 0

    def on_select(self):
        for viewer in self.viewers:
            viewer.update(input=self.selected.get())
