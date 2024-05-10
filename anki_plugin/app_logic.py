######################################################################
# MangAnki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Application logic (i.e., resource manipulation) is done in
# AppLogic. The state of the
# application is stored in resource AppState.
######################################################################

import enum
import os
import pickle
import asyncio

try:
    from .resources import Resource, Resources
    from . import dict_lookup
    from .dict_lookup import DictionaryLookup, DictionaryEntry
except:
    from resources import Resource, Resources
    import dict_lookup
    from dict_lookup import DictionaryLookup, DictionaryEntry


class AppState(enum.Enum):
    LOADING_AND_PREPARING = 0
    INITIAL = 1
    IMAGE_COPIED_NO_MARKING = 2
    MARKING_GIVEN_NO_EXPR = 3
    EXPR_GIVEN_NO_ENTRY_SELECTED = 4
    ENTRY_SELECTED_READY_TO_TRANSFER = 5


APP_STATE_STORE_FILE = "%s/%s" % (os.path.dirname(__file__), "app.pickle")


class AppLogic:
    def __init__(self):
        resources_dict = {
            "AppState": AppState.LOADING_AND_PREPARING,
            "Image": None,
            "OriginalClipboardImage": None,
            "Marking": None,
            "CurrentEntry": None,
            "SelectedTranslationIndex": None,
            "SelectedTranslation": None,
            "PossibleEntries": None,
            "Dictionary": None,
            "CurrentTakobotoLink": None,
            "TranslationLanguages": None,
            "PreferredTranslationLanguage": "eng",
            "Tag": "",
        }
        self._r = Resources(resources_dict)
        self._r.add_listener(
            "OriginalClipboardImage", self.on_change_original_clipboard_image
        )
        self._r.add_listener("Marking", self.on_change_marking)
        self._r.add_listener("CurrentEntry", self.on_change_current_entry)
        self._r.add_listener(
            "SelectedTranslationIndex", self.on_change_selected_translation_index
        )
        self._r.add_listener(
            "PreferredTranslationLanguage",
            self.on_change_preferred_translation_language,
        )

    def do_initial_loading_tasks(self):
        self._r.Dictionary = dict_lookup.DictionaryLookup.de_pickle()
        if self._r.Dictionary is None:
            self._r.Dictionary = DictionaryLookup()
            self._r.Dictionary.parse_file()
            self._r.Dictionary.pickle()  # for next time
        self._r.TranslationLanguages = self._r.Dictionary.get_languages()

    def get_resources(self):
        return self._r

    def get_state(self):
        return self._r.AppState

    def _reset_entry_resources(self):
        self._r.CurrentEntry = None
        self._r.SelectedTranslationIndex = None
        self._r.SelectedTranslation = None
        self._r.PossibleEntries = None
        self._r.CurrentTakobotoLink = None

    def on_change_original_clipboard_image(self):
        self._reset_entry_resources()
        if self._r.AppState == AppState.LOADING_AND_PREPARING:
            return
        self._r.AppState = AppState.INITIAL
        if self._r.OriginalClipboardImage:
            self._r.AppState = AppState.IMAGE_COPIED_NO_MARKING
        else:
            # jump to initial state
            self._r.AppState = AppState.INITIAL

    def on_change_marking(self):
        if self._r.Marking and self._r.AppState in [AppState.IMAGE_COPIED_NO_MARKING]:
            self._r.AppState = AppState.MARKING_GIVEN_NO_EXPR

    def on_change_current_entry(self):
        if self._r.AppState == AppState.LOADING_AND_PREPARING:
            return
        self._r.CurrentTakobotoLink = None
        self._r.PossibleEntries = self._r.Dictionary.look_up(self._r.CurrentEntry)
        self._r.SelectedTranslationIndex = None
        self._r.SelectedTranslation = None
        if (
            self._r.PossibleEntries
            and self._r.AppState == AppState.MARKING_GIVEN_NO_EXPR
        ):
            self._r.AppState = AppState.EXPR_GIVEN_NO_ENTRY_SELECTED
        elif self._r.AppState != AppState.INITIAL:
            self._r.AppState = AppState.MARKING_GIVEN_NO_EXPR

    def on_change_selected_translation_index(self):
        self._r.SelectedTranslation = None
        if self._r.SelectedTranslationIndex is not None:
            self._r.SelectedTranslation = self._r.PossibleEntries[
                self._r.SelectedTranslationIndex
            ]
            if self._r.AppState in [AppState.EXPR_GIVEN_NO_ENTRY_SELECTED]:
                self._r.AppState = AppState.ENTRY_SELECTED_READY_TO_TRANSFER

    def on_change_preferred_translation_language(self):
        current_entry = self._r.CurrentEntry
        self._r.CurrentEntry = ""
        self._r.CurrentEntry = current_entry

    def store_program_state(self):
        to_be_stored = {
            "preferred_translation_language": self._r.PreferredTranslationLanguage,
            "tag": self._r.Tag,
        }
        try:
            with open(APP_STATE_STORE_FILE, "wb") as pickle_file:
                pickle.dump(to_be_stored, pickle_file)
        except Exception as e:
            print("Could not save program state: %s" % e)

    def read_stored_program_state(self):
        """Restores program settings."""
        try:
            with open(APP_STATE_STORE_FILE, "rb") as pickle_file:
                pickled_entity = pickle.load(pickle_file)
                self._r.PreferredTranslationLanguage = pickled_entity[
                    "preferred_translation_language"
                ]
                self._r.Tag = pickled_entity["tag"]
        except Exception as e:
            print("Could not restore program state (normal for startup): %s" % e)
