######################################################################
# Manganki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Interface to Anki GUI
######################################################################


from aqt import mw, dialogs
from aqt.qt import *
from anki import notes
from anki.hooks import addHook
from PyQt6.QtGui import QImage

try:
    from .dict_lookup import DictionaryEntry
except:
    from dict_lookup import DictionaryEntry


def show_error_dialog(message):
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Icon.Warning)
    error_box.setText("Error")
    error_box.setInformativeText(message)
    error_box.setWindowTitle("Error")
    error_box.exec()


FRONT_TEMPLATE = """
<H2>{{Sentence}}</H2>
<H2>{{Audio}}</H2>
"""
BACK_TEMPLATE = """
<H1>{{Expression}}</H1>
<H1>{{Reading}}</H1>
<H2>{{Translation}}</H2>
<H3><a href={{Takoboto Link}}>{{Expression}}</a></H3>
"""

MODEL_NAME = "MangankiV1"


def get_model():
    model_name = MODEL_NAME
    model = mw.col.models.by_name(model_name)
    if not model:
        model = mw.col.models.new(model_name)
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
                "name": "Audio",
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
        mw.col.models.add(model)
        mw.col.save()
        model = mw.col.models.by_name(model_name)
    return model


def add_reviewer_card(
    dict_entry: DictionaryEntry,
    image: QImage,
    preferred_language: str = "eng",
    tag: str = "",
):
    image.save("temp.png")
    status = ""
    try:
        add_dialogue = dialogs.open("AddCards", mw)
        mw.onAddCard()
        note = notes.Note(model=get_model(), col=mw.col)
        if note:
            # new_expression = self.expression_edit.text()
            note["Expression"] = dict_entry.get_expression()
            note["Translation"] = dict_entry.get_translation(preferred_language)
            note["Reading"] = dict_entry.get_reading()
            note["Takoboto Link"] = dict_entry.get_takoboto_link_for_card()
            new_file = mw.col.media.add_file("temp.png")
            note["Sentence"] = '<img src="%s"/>' % new_file
            if tag:
                note.add_tag(tag)
            add_dialogue.set_note(note)
            # mw.reset()
            return
    except Exception as e:
        status = str(e)
    show_error_dialog("Card could not be added: %s" % status)
