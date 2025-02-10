import tkinter as tk
from tkinter import font

class Layout():

    """Defines parameters of the layout
    """

    def __init__(self, root):
        
        self.root = root
        self.height, self.width = self.get_curr_screen_geometry()

        ### Fonts
        self.font_size_nav = 9
        self.font_size_text = 10

        self.font_sans_serif = self.get_font('sans_serif', size=self.font_size_text, name='sans_serif')
        self.font_serif = self.get_font('serif', size=self.font_size_text, name='serif')
        self.font_mono = self.get_font('mono', size=self.font_size_text, name='mono')

        font_height = self.font_sans_serif.metrics('linespace')

        ### Main paddings
        self.paddings = {
            'normal': {'padx': 5, 'pady': 5},
            'small': {'padx': 3, 'pady': 3},
        }

        ### Main grid layout configuration
        self.root.columnconfigure(0, weight=1) # content column
        self.root.columnconfigure(1, weight=0) # scrollbar
        self.root.columnconfigure(2, weight=1) # content column 
        self.root.columnconfigure(3, weight=0) # scrollbar  
     
        self.root.rowconfigure(0, weight=0, minsize=10) # File menu
        self.root.rowconfigure(1, weight=0, minsize=10) # Buttons widget
        self.root.rowconfigure(3, weight=0, minsize=10) # Questions widget
        self.root.rowconfigure(4, minsize=font_height) # Similarity widget title box
        self.root.rowconfigure(5, weight=0, minsize=10) # Similarity widget
        self.root.rowconfigure(7, minsize=font_height) # Footer

        # Layout of widgets
        self.height_buttons_widget = 115    # px
        self.share_questions_widget = 0.55  # share of total height
        self.share_similarity_widget = 0.2 # share of total height
        self.max_height_similiary_widget = 250 # px

        self.buttons_widget = LayoutButtons(
            root=self.root, 
            layout=self,
            column_config= {0: {'minsize': 40, 'weight': 1, 'col_split': 1}}
        )
        
        self.questions_widget = LayoutQuestions(
            root=self.root,
            layout=self,
            column_config = {
                    0: {'minsize': 40, 'weight': 1, 'col_split': 0.4},
                    1: {'minsize': 100, 'weight': 1, 'col_split': 0.58},
                    2: {'minsize': 10, 'weight': 1, 'col_split': 0.01},
                },
            )
        
        self.similarity_widget_left = LayoutSimilarity(
            root=self.root, 
            layout=self,
            column_config={0: {'minsize': 40, 'weight': 1, 'col_split': 1}}
            )
        
        self.similarity_widget_right = LayoutSimilarity(
            root=self.root, 
            layout=self,
            column_config={
                    0: {'minsize': 100, 'weight': 1, 'col_split': 0.8},
                    1: {'minsize': 40, 'weight': 1, 'col_split': 0.2},
                },
            )


    def get_curr_screen_geometry(self):
        """
        Get the size of the current screen in a multi-screen setup.

        Source: https://stackoverflow.com/questions/3949844/how-can-i-get-the-screen-size-in-tkinter
        """
        
        root = tk.Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        height = int(0.80*root.winfo_screenheight()) # factor to account for decorations
        width = int(0.90*root.winfo_screenwidth()) 
        root.destroy()
        return height, width
    

    def get_font(self, type, size, name):
        """Searches for font in the list of installed fonts."""

        installed_fonts = tk.font.families()
        system_font_stack = self.get_system_font_stack() # https://systemfontstack.com/
        for fnt in system_font_stack[type]:
            if fnt in installed_fonts:
                return font.Font(font=(fnt, size), name=name)
        return None
    
        #if type=="sans_serif":
        #    return font.nametofont("TkDefaultFont")
        #if type=="serif":
        #    return None
        #if type=="mono":
         #   return font.nametofont("TkFixedFont")

    def get_system_font_stack(self):

        SYSTEMFONTSTACK = {
            'sans_serif': [
                '-apple-system', 
                'BlinkMacSystemFont',
                'Avenir Next',
                'Avenir',
                'Segoe UI',
                'Helvetica Neue',
                'Helvetica',
                'Cantarell',
                'Ubuntu',
                'Roboto',
                'Noto',
                'Arial',
                'Sans-Serif'
            ], 
            'serif': [
                'Iowan Old Style', 
                'Apple Garamond', 
                'Baskerville', 
                'Times New Roman', 
                'Droid Serif', 
                'Times', 
                'Source Serif Pro', 
                'Serif', 
                'Apple Color Emoji', 
                'Segoe UI Emoji', 
                'Segoe UI Symbol',
            ],
            'mono': [
                'Menlo',
                'Consolas', 
                'Monaco', 
                'Liberation Mono',
                'Lucida Console',
                'monospace'
            ]
        }
        return SYSTEMFONTSTACK
                

class LayoutButtons():

    def __init__(self, root, layout, column_config=None):
        self.root = root
        self.layout = layout
        self.height = self.layout.height_buttons_widget
        self.font_sans_serif = self.layout.font_sans_serif
        self.font_serif = self.layout.font_serif
        self.font_mono = self.layout.font_mono
        self.font_size_nav = self.layout.font_size_nav
        self.font_size_text = self.layout.font_size_text
        self.paddings = self.layout.paddings
        self.column_config = column_config

    

    def get_height(self):
        return self.height
    

class LayoutQuestions():

    def __init__(self, root, layout, column_config=None):
        self.root = root
        self.layout = layout
        self.column_config = column_config
        self.font_sans_serif = self.layout.font_sans_serif
        self.font_serif = self.layout.font_serif
        self.font_mono = self.layout.font_mono
        self.font_size_nav = self.layout.font_size_nav
        self.font_size_text = self.layout.font_size_text
        self.paddings = self.layout.paddings
    
    def get_height(self):
        screen_height = self.root.winfo_height()
        height_buttons = self.layout.buttons_widget.get_height() 
        height_similarity = self.layout.similarity_widget_left.get_height()
        height_other_boxes = 140 # refactor
        height = self.layout.share_questions_widget * screen_height
        add_height = (
            screen_height
            - height_buttons
            - height_similarity
            - height_other_boxes
            - height
        )
        self.height = min(0, add_height) + height
        return self.height
    


    def tag_configure(self, text_box, style):

        font = self.font_sans_serif.cget('family')
        size = self.font_sans_serif.cget('size')
        
        if style=="title":
            text_box.tag_configure("title", font=(font, size, "bold"))
        elif style=="normal":
            text_box.tag_configure("normal", font=(font, size)) 
        elif style=="item_name":
            text_box.tag_configure("item_name", font=(font, size, "bold"))
        elif style=="scale":
             text_box.tag_configure("scale", font=(font, size, "italic"), justify="right")
        elif style=="instruction":
            text_box.tag_configure("instruction", font=(font, size, "italic")) 
        elif style=="variable":
               text_box.tag_configure("variable", font=(font, size), foreground='MediumPurple4')
        else:
            pass

    def get_column_params(self, style):

        if style=="title":
            column = 0
            columnspan = 3
            col_split = 1
        elif style in ["normal", "item_name", "instruction", "variable"]:
            column = 0
            columnspan = 2
            col_split = self.column_config[0]['col_split'] + self.column_config[1]['col_split'] 
        elif style=="scale":
            column = 1
            columnspan = 2
            col_split = self.column_config[1]['col_split'] + self.column_config[2]['col_split'] 
        else:
            column = 0
            columnspan = 3
            col_split = 1
        return column, columnspan, col_split


class LayoutSimilarity():

    def __init__(self, root, layout, column_config):
        self.root = root
        self.layout = layout
        self.column_config = column_config
        self.font_sans_serif = self.layout.font_sans_serif
        self.font_serif = self.layout.font_serif
        self.font_mono = self.layout.font_mono
        self.font_size_nav = self.layout.font_size_nav
        self.font_size_text = self.layout.font_size_text
        self.paddings = self.layout.paddings
    

    def get_height(self):
        height = self.layout.share_similarity_widget * self.root.winfo_height()
        self.height = min(self.layout.max_height_similiary_widget, height)
        return self.height
      