#
# Manganki
# (C) 2024-current Andreas Gaiser
#

import typing
from PIL import ImageGrab, ImageFile
from tkinter import PhotoImage
import tkinter as tk


class ClipboardHandling:
    """Used for polling the clipboard to grab images (and later maybe audio files)"""

    def __init__(self, parent):
        self._parent = parent
        self._clipboard_data = None
        self._listeners = []
        self._parent.after(2000, self._auto_update, 500)

    def add_listener(
        self, listener: typing.Callable[[typing.Optional[tk.PhotoImage]], None]
    ):
        """Add a listener. If a new image is copied to the clipboard, every listener is called with the image
        as its argument."""
        self._listeners.append(listener)

    def _auto_update(self, miliseconds=500):
        self.update_history()
        self._parent.after(miliseconds, self._auto_update, miliseconds)

    def update_history(self):
        try:
            new_clipboard_data = ImageGrab.grabclipboard()
            if not isinstance(new_clipboard_data, ImageFile.ImageFile):
                new_clipboard_data = None
            if new_clipboard_data != self._clipboard_data:
                self._clipboard_data = new_clipboard_data
                if new_clipboard_data is not None:
                    new_clipboard_data.save("screenshot.png")
                    image = PhotoImage(file="screenshot.png")
                    for listener in self._listeners:
                        listener(image)
        except tk.TclError as e:
            print("ERROR: %s" % e)
            self._clipboard_data = None
            # apparently there can be race conditions regarding the clipboard
