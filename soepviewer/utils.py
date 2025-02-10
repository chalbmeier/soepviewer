
class ListVar:
    """Copyright: ChatGPT, 22/01/2025"""
    def __init__(self, initial_value=None):
        if initial_value is None:
            initial_value = []
        self._list = initial_value
        self._callbacks = []

    def get(self):
        """Return the current list."""
        return self._list

    def set(self, new_list):
        """Set the list to a new value and notify callbacks."""
        self._list = new_list
        self._notify()

    def append(self, item):
        """Add an item to the list."""
        self._list.append(item)
        self._notify()

    def remove(self, item):
        """Remove an item from the list."""
        self._list.remove(item)
        self._notify()

    def trace_add(self, callback):
        """Add a callback to be notified when the list changes."""
        self._callbacks.append(callback)

    def _notify(self):
        """Notify all registered callbacks."""
        for callback in self._callbacks:
            callback()