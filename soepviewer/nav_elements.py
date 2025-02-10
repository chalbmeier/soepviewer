import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from .input_handlers import ScrollEventHandler

class FileMenu(ttk.Combobox):

    def __init__(
            self, 
            root, 
            textvariable, 
            values, 
            study, 
            questionnaire, 
            questions,
            trigger_data_update,
            file_to_questionnaire,
            questionnaire_to_file=None,
            row=0, 
            column=0,
            layout=None,
            **kwargs
            ):

        super().__init__(
            root, 
            textvariable=textvariable,
            values=values,
            state='readonly',
            width=300,
            font=layout.font_sans_serif,
            **kwargs
        )

        self.root = root
        self.textvariable=textvariable
        self.study = study
        self.questionnaire = questionnaire
        self.questions = questions
        self.file_to_questionnaire = file_to_questionnaire
        self.layout = layout
        self.grid(column=column, row=row, sticky=tk.W, **self.layout.paddings['normal'])
        self.trigger_data_update = trigger_data_update
        self.questionnaire_to_file = questionnaire_to_file

        self.bind("<<ComboboxSelected>>", lambda event: self.update(event, self.textvariable))
      

    def update(self, event, input, output=None):
        self.trigger_data_update.set(True)

    def check_file(self, event, input=None, output=None):
        study = self.study.get()
        questionnaire = self.questionnaire.get()
        current_file = self.textvariable.get()
        try:
            expected_file = self.questionnaire_to_file[(study, questionnaire)]['file']
            if expected_file!=current_file:
                self.textvariable.set(expected_file)
        except:
            pass


class Box():

    def __init__(
            self,
            root,
            row,
            column,
            height,
            width=None,
            layout=None,
            text=None,
            padx=5,
            pady=5,
            color='grey',
            columnspan=1,
    ):
        
        self.root = root
        self.width = width
        self.height = height
        self.layout = layout
        self.text = text
        self.color = color

        if self.text is None:
            box = tk.Frame(self.root, height=self.height, bg=color, padx=padx, pady=pady)

        else:
            box = tk.Text(
                self.root,
                font=self.layout.font_sans_serif,
                height=1,  
                borderwidth=0,
                bg=color,
                bd=0,
                padx=padx,
                pady=pady,
            )   
            box.insert('1.0', self.text)
            box.configure(state='disabled')

        box.grid(row=row, column=column, sticky="ew", columnspan=columnspan)
           

class ScrollFrame():

    """A scrollable canvas widget that contains a frame with a specified amount of columns"""

    def __init__(
            self,
            root,
            row,
            column,
            column_config,
            height=None,
            textvariable=None,
            title=None,
            bg='white',
            padx=5,
            pady=5,
            layout=None,
            ):

        self.root = root
        self.height = height
        self.column_config = column_config
        self.textvariable = textvariable
        self.title = title
        self.bg = bg
        self.layout = layout

        ##############################
        # Layout 
        ###############################

        if self.title is not None:
            title_label = tk.Label(self.root, text=self.title, height=1, bg=self.bg, padx=padx, pady=pady)
            title_label.grid(row=row, column=column, sticky="nsew")
            row += 1

        # Scrollable canvas + frame for questions 
        self.canvas = tk.Canvas(
            self.root,
            height=self.height,
            bg=self.bg,
            borderwidth=0,
            highlightthickness=0,
        )
        self.canvas.grid(row=row, column=column, sticky="nsew", padx=padx, pady=pady)

        v_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=row, column=column+1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scrollbar.set)

        # Scrollable canvas contains frame with columns
        width = self.canvas.winfo_width()
        self.frame = tk.Frame(
            self.canvas,
            bg=self.bg,
            borderwidth=0,
            highlightthickness=0
        )

        for k, v in self.column_config.items():
            self.frame.columnconfigure(
                k,
                minsize=int(width*v['col_split']), 
                weight=v['weight']
            ) 

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw", tags="frame")
        self.canvas.bind("<Configure>", self.adjust_frame_size)
        self.frame.bind("<Configure>", self.update_scroll_region)

        #############################
        # Handling of user input
        #############################

        # Bind mouse wheel input to widgets of canvas
        self.scroll_handler = ScrollEventHandler(self.canvas)
        self.bind_mouse_wheel([self.canvas, v_scrollbar] +  self.canvas.winfo_children())
    
    def update(self):
        """Call after new content has been added to frame"""
        self.bind_mouse_wheel(self.frame.winfo_children())
        self.reset_scroll_to_top()

    def adjust_frame_size(self, event):
        width = self.canvas.winfo_width()
        height = self.layout.get_height()
     
        self.canvas.config(height=height)
        self.canvas.itemconfig("frame", width=width)
        

        for k, v in self.column_config.items():
            self.frame.columnconfigure(
                k,
                minsize=int(width*v['col_split']), 
                weight=v['weight']
            ) 
        

    def update_scroll_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def reset_scroll_to_top(self):
        self.canvas.yview_moveto(0)

    def bind_mouse_wheel(self, widgets):
        for widget in widgets:
            self._bind_mouse_wheel(widget)

            try:
                self.bind_mouse_wheel(widget.winfo_children())
            except:
                pass

    def _bind_mouse_wheel(self, widget):
        widget.bind("<MouseWheel>", self.scroll_handler.on_mouse_wheel)  # Windows/Linux
        widget.bind("<Button-4>", self.scroll_handler.on_mouse_wheel)  # macOS scroll up
        widget.bind("<Button-5>", self.scroll_handler.on_mouse_wheel)  # macOS scroll down 


class QuestionButtons(ScrollFrame):

    def __init__(
            self, 
            root, 
            height=None, 
            questions=None, 
            selected=None, 
            row=0, 
            column=0,
            layout=None,
            ):

        super().__init__(
            root, 
            column=column, 
            row=row, 
            column_config=layout.column_config, 
            height=height,
            layout=layout
        )
        
        self.root = root
        self.bg = self.root.cget('bg')
 
        if selected is None:
            selected = tk.StringVar(value="") # value of selected button
        self.selected = selected
        self.questions = questions
        self.font = tkfont.Font(
            family=self.layout.font_mono,
            size=self.layout.font_size_nav, 
            weight="normal")
        self.borderwidth = 1


    def update(self, event=None, input=None, output=None):

        # Remove old buttons
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Current settings
        font = self.font.cget('family')
        font_size = self.font.cget('size')
        width = self.frame.winfo_width() 
        button_paddings = 2 * self.layout.paddings['small']['padx']
        
        questions = self.questions.get()
        frame_full = True
        i = 0
        j = 0
        occupied_px = 0
        for q in questions:
            
            text = f"{q}"

            # Get width of new button, +4 for inner default margin of Radiobutton
            button_width = self.font.measure(text) + 2*self.borderwidth + button_paddings + 4   
            occupied_px += button_width
       
            if occupied_px > (width-2):
                frame_full = True
                occupied_px = button_width
                i += 1
                j = 0

            if frame_full:
                # new frame in each row to vary column width across rows
                frame = tk.Frame(self.frame, bg=self.bg)
                frame.grid(row=i, column=0, sticky="nsew")
                frame_full = False            

           
            button = tk.Radiobutton(
                frame, 
                text=text,
                **self.layout.paddings['small'],
                value = text,
                font=(font, font_size),
                variable=self.selected,
                indicatoron=False,
                command=self.on_select,
                borderwidth=self.borderwidth,
            )

            button.grid(row=i, column=j, padx=0) # ,
            j +=1

        # Update layout of parent scrollable frame
        super().update()
     

    def on_select(self):
        pass


class Popup():

    """A pop-up window to display a message"""

    def __init__(self, root, text, width, height, position='left', title="Processing"):
        self.root = root
        self.text = text
        self.width = width
        self.height = height
        self.position = position
        self.title = title

    def show(self):

        # Content
        self.popup = tk.Toplevel(self.root)
        self.popup.title(self.title)
        tk.Label(self.popup, text=self.text).pack(padx=5, pady=5)

        # Position and geometry
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        if self.position=='left':
            self.popup.geometry(f"{self.width}x{self.height}+{x+250}+{y+400}") # improve calculation of position
        else:
            self.popup.geometry(f"{self.width}x{self.height}")
        self.popup.transient(self.root)
     

    def close(self):
        self.popup.destroy()
