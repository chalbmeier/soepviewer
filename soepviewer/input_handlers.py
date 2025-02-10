
class ScrollEventHandler:

    def __init__(self, canvas):
        self.canvas = canvas

    def on_mouse_wheel(self, event):
        if event.num == 4:  # macOS scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # macOS scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows and Linux
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def disable_mouse_wheel(self, event):
        """Prevent child widgets from responding to the mouse wheel."""
        return "break"