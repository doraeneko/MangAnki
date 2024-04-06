#
# Manganki
# (C) 2024-current Andreas Gaiser
#

import PIL.Image
import anki_interface
import math
from models import *
from dict_lookup import DictionaryLookup, DictionaryEntry
from clipboard import ClipboardHandling


class Delegate:
    def __init__(
        self,
        app,
        model: AppModel,
        clipboard_handling: ClipboardHandling,
        dict_lookup: DictionaryLookup,
        anki_connection: anki_interface.AnkiInterface,
    ):
        self._app = app
        self._model = model
        self._clipboard_handling = clipboard_handling
        self._dict_lookup = dict_lookup
        self._anki_connection = anki_connection
        self._image_listener = []
        self._image_marking_listener = []
        self._dict_entry_listener = []
        self._current_translation_entry_listener = []

    # Get/Change properties from the model

    def get_raw_image(self):
        return self._model.image.current_raw_image

    def get_image_with_marking(self) -> PIL.Image.Image:
        return self._model.image.current_image_with_marking

    def set_image_with_marking(self, image: PIL.Image.Image):
        self._model.image.current_image_with_marking = image
        # no listeners yet

    def add_image_listener(self, listener):
        self._image_listener.append(listener)

    def add_image_marking_listener(self, listener):
        self._image_marking_listener.append(listener)

    def add_entry_listener(self, listener):
        self._dict_entry_listener.append(listener)

    def add_current_translation_entry_listener(self, listener):
        self._current_translation_entry_listener.append(listener)

    def set_image_marking(self, x1, y1, x2, y2):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        self._model.image.current_marking.LEFT = x1
        self._model.image.current_marking.TOP = y1
        self._model.image.current_marking.RIGHT = x2
        self._model.image.current_marking.BOTTOM = y2
        for listener in self._image_marking_listener:
            listener()

    def get_image_marking(self):
        return (
            self._model.image.current_marking.LEFT,
            self._model.image.current_marking.TOP,
            self._model.image.current_marking.RIGHT,
            self._model.image.current_marking.BOTTOM,
        )

    def image_marking_invalid(self):
        return abs(self._model.image.current_marking.LEFT - self._model.image.current_marking.RIGHT) < 2

    def get_dict_entry_translations(self):
        return self._model.dict.translations

    def set_translation_entry_by_index(self, index):
        try:
            self._model.dict.current_entry = self._model.dict.entries[index]
        except:
            self._model.dict.current_entry = DictionaryEntry()
        for listener in self._current_translation_entry_listener:
            listener()

    def get_current_translation_entry(self):
        return self._model.dict.current_entry

    def set_image(self, image):
        self._model.image.current_raw_image = image
        for listener in self._image_listener:
            listener()

    def set_current_dict_entry(self, text):
        self._model.dict.current_entry = text
        self._model.dict.entries = self._dict_lookup.look_up(text)
        self._model.dict.translations = [
            e.stringify() for e in self._model.dict.entries
        ]
        for listener in self._dict_entry_listener:
            listener()

    def set_current_translation_entry(self, index):
        self._model.dict.current_lookup

    def get_current_takoboto_link(self):
        entry = self.get_current_translation_entry()
        if entry.unique_id:
            link_text = "https://takoboto.jp/?w=%s" % (entry.unique_id)
            return link_text
        else:
            return ""

    def get_current_takoboto_card_entry(self):
        entry = self.get_current_translation_entry()
        if entry.unique_id:
            card_text = (
                "intent:#Intent;package=jp.takoboto;action=jp.takoboto.WORD;i.word=%s;S.browser_fallback_url=http%3A%2F%2Ftakoboto.jp%2F%3Fw%3D%s;end"
                % (entry.unique_id, entry.unique_id)
            )
            return card_text
        else:
            return ""

    def add_anki_card(self, expression, reading, translation, dict_id, image):
        self._anki_connection.add_card(expression, reading, translation, dict_id, image)
