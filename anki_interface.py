#
# Manganki
# (C) 2024-current Andreas Gaiser
#

import anki
from anki.storage import Collection
from PIL import Image

FRONT_TEMPLATE = """
<H2>{{Sentence}}</H2>
"""
BACK_TEMPLATE = """
<H1>{{Expression}}</H1>
<H1>{{Reading}}</H1>
<H2>{{Translation}}</H2>
<H3><a href={{Takoboto Link}}>{{Expression}}</a></H3>
"""


class AnkiInterface:
    def get_model(self):
        model = self._collection.models.by_name(self._model_name)
        if not model:
            model = self._collection.models.new(self._model_name)
            model[
                "css"
            ] = """
                img {
                    max-width: 100%;
                    max-height: 100%;
                    }
                   .card {
                       font-family: Arial;
                       font-size: 20px;
                       text-align: center;
                       color: black;
                       background-color: white;
                   }
               """
            model["type"] = 0
            model["flds"] = [
                {
                    "name": "Expression",
                    "sticky": False,
                    "rtl": False,
                    "ord": 0,
                    "font": "Arial",
                    "size": 20,
                },
                {
                    "name": "Translation",
                    "sticky": False,
                    "rtl": False,
                    "ord": 0,
                    "font": "Arial",
                    "size": 20,
                },
                {
                    "name": "Reading",
                    "sticky": False,
                    "rtl": False,
                    "ord": 0,
                    "font": "Arial",
                    "size": 20,
                },
                {
                    "name": "Sentence",
                    "sticky": False,
                    "rtl": False,
                    "ord": 0,
                    "font": "Arial",
                    "size": 20,
                },
                {
                    "name": "Takoboto Link",
                    "sticky": False,
                    "rtl": False,
                    "ord": 0,
                    "font": "Arial",
                    "size": 20,
                },
            ]
            model["tmpls"] = [
                {"name": "MangAnki", "qfmt": FRONT_TEMPLATE, "afmt": BACK_TEMPLATE}
            ]
            model["sticky"] = []
            self._collection.models.add(model)
            self._collection.save()
            model = self._collection.models.by_name(self._model_name)
        return model

    def __init__(self, collection_path, media_path, deck_name):
        self._collection_path = collection_path
        self._deck_name = deck_name
        self._media_path = media_path
        self._deck = None
        self._model = None
        self._model_name = "MangAnki"
        try:
            self._collection = Collection(self._collection_path)
            # Get or possibly create the deck
            self._collection.decks.id(deck_name, True)
            self._deck = self._collection.decks.by_name(deck_name)
            self._model = self.get_model()
        except Exception as e:
            print("Exception in AnkiInterface: %s" % e)
            raise e

    def add_card(self, expression, reading, translation, dict_id, image: Image):
        import os, uuid

        note = anki.notes.Note(model=self._model, col=self._collection)
        note["Expression"] = expression
        note["Reading"] = reading
        note["Translation"] = translation
        random_filename = "%s.png" % str(uuid.uuid4())
        image.save(os.path.join(self._media_path, random_filename))
        note["Sentence"] = '<img src="%s"/>' % random_filename
        note["Takoboto Link"] = card_text = (
            "intent:#Intent;package=jp.takoboto;action=jp.takoboto.WORD;i.word=%s;S.browser_fallback_url=http%%3A%%2F%%2Ftakoboto.jp%%2F%%3Fw%%3D%s;end"
            % (dict_id, dict_id)
        )
        deck_id = self._collection.decks.id(self._deck_name)
        note.model()['did'] = deck_id
        self._collection.add_note(note, self._collection.decks.id(self._deck_name, True))
        self._collection.save()

    def save_and_close(self):
        self._collection.save()
        self._collection.close()