#
# Manganki
# (C) 2024-current Andreas Gaiser
#

import argparse
import sys
from tkinter import Canvas, Frame, Label, messagebox
import tkinter.font as tkFont

from models import *
from clipboard import *
from image_canvas import ImageCanvas
from delegates import Delegate
from dict_lookup_frame import DictLookupFrame
import dict_lookup
import anki_interface

MAX_WIDTH = 1024
MAX_HEIGHT = 768


class App:
    def get_delegate(self):
        return self._delegate

    def __init__(self, root, dict_lookup, anki_connection):
        self._root = root
        self._clipboard_handling = ClipboardHandling(root)
        self._image_canvas = None
        self._delegate = Delegate(
            self,
            AppModel(),
            clipboard_handling=self._clipboard_handling,
            dict_lookup=dict_lookup,
            anki_connection=anki_connection,
        )
        self.create_widgets()
        self._clipboard_handling.add_listener(self._delegate.set_image)

    def create_widgets(self):
        self._root.title("MangAnki")
        self._root.config(bg="skyblue")
        root.maxsize(MAX_WIDTH, MAX_HEIGHT)
        root.config(bg="skyblue")  # specify background color
        left_frame = Frame(root, width=MAX_WIDTH / 3, height=MAX_HEIGHT, bg="grey")
        left_frame.grid(row=0, column=0, padx=10, pady=5)
        right_frame = Frame(
            root, width=(2 * MAX_WIDTH) / 3, height=MAX_HEIGHT, bg="grey"
        )
        right_frame.grid(row=0, column=1, padx=10, pady=5)
        dict_lookup_frame = DictLookupFrame(
            self._delegate, left_frame, width=500, height=800
        )
        dict_lookup_frame.grid(row=0, column=0, padx=5, pady=5)
        image_canvas = ImageCanvas(self._delegate, right_frame, width=750, height=750)
        image_canvas.grid(row=0, column=0, padx=0, pady=0)
        image_canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self._image_canvas = image_canvas

    def start_loop(self):
        self.create_widgets()
        self._root.mainloop()


JMDICT_DEFAULT_FILE_PATH = "JMdict.xml"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Anki Path and Preferred Language Options"
    )
    parser.add_argument(
        "--collection_path",
        type=str,
        help="Path to .anki2 collection file",
        required=True,
    )
    parser.add_argument(
        "--media_path",
        type=str,
        help="Path to Anki media collection directory",
        required=True,
    )
    parser.add_argument(
        "--jdict_file_path",
        type=str,
        help="Path to JDICT xml input file",
        default=JMDICT_DEFAULT_FILE_PATH,
    )
    parser.add_argument(
        "--preferred_language",
        choices=["eng", "ger"],
        help="Preferred language (eng or ger)",
        default="eng",
    )
    parser.add_argument(
        "--deck_name",
        type=str,
        help="Name of Anki deck to store cards in",
        default="MangAnki",
    )

    args = parser.parse_args()
    collection_path = args.collection_path
    media_path = args.media_path
    deck_name = args.deck_name
    preferred_language = args.preferred_language
    jdict_file_path = args.jdict_file_path
    args = parser.parse_args()

    try:
        print("Connection to Anki...")
        anki_connection = anki_interface.AnkiInterface(
            collection_path=collection_path, media_path=media_path, deck_name=deck_name
        )
        print("Connection to Anki done.")
    except Exception as e:
        messagebox.showerror(
            "Error",
            'No connection to ANKI data base possible: "%s".'
            " Please check collection and media paths given and make sure that Anki itself is not running."
            % e,
        )
        sys.exit(1)
    try:
        print("Constructing dictionary lookup (can take some time)...")
        lookup = dict_lookup.DictionaryLookup(preferred_language=preferred_language)
        lookup.parse_file(jdict_file_path)
        print("Constructing dictionary lookup done.")
    except Exception as e:
        messagebox.showerror(
            "Error",
            'Could not construct JDICT lookup: "%s".'
            " Please check integrity of JMdict.xml." % e,
        )
        sys.exit(1)

    root = tk.Tk()
    app = App(root, lookup, anki_connection)
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=14)
    app.start_loop()
    anki_connection.save_and_close()
