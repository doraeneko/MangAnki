######################################################################
# MangAnki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Interface to JMDICT dictionary file
######################################################################

import dataclasses
import typing
import json
import os
import pickle

DICT_FILE_NAME = "%s/%s" % (os.path.dirname(__file__), "jmdict-all-3.5.0.json")
PICKLE_FILE_NAME = "%s/%s" % (os.path.dirname(__file__), "jmdict-all-3.5.0.json.pickle")


@dataclasses.dataclass
class DictionaryEntry:
    """Single dictionary entry, containing translations and readings, and the ID from
    JDict."""

    translations: typing.Dict[str, typing.List[str]] = dataclasses.field(
        default_factory=dict
    )
    """Language prefix -> translations"""
    unique_id: str = ""
    kanji_readings: typing.List[str] = dataclasses.field(default_factory=list)
    kana_readings: typing.List[str] = dataclasses.field(default_factory=list)

    def stringify(self, preferred_language: str = "eng"):
        result = ", ".join(self.kana_readings + self.kanji_readings)
        result += ": "
        if preferred_language in self.translations:
            result += ", ".join(self.translations[preferred_language])
        else:
            result += ", ".join(self.translations["eng"])
        return result

    def get_expression(self):
        if self.kanji_readings:
            return ", ".join(self.kanji_readings)
        else:
            return ", ".join(self.kana_readings)

    def get_reading(self):
        if self.kanji_readings:
            return ", ".join(self.kana_readings)
        return ""

    def get_translation(self, preferred_language: str = "eng"):
        if preferred_language in self.translations:
            return ", ".join(self.translations[preferred_language])
        elif "eng" in self.translations:
            return ", ".join(self.translations["eng"])
        else:
            return "<no matching translation>"

    def get_takoboto_link_for_card(self):
        return (
            "intent:#Intent;package=jp.takoboto;action=jp.takoboto.WORD;i.word=%s;S.browser_fallback_url=http%%3A%%2F%%2Ftakoboto.jp%%2F%%3Fw%%3D%s;end"
            % (self.unique_id, self.unique_id)
        )

    def get_takoboto_link_for_web(self):
        return "https://takoboto.jp/?w=%s" % self.unique_id


class DictionaryLookup:
    """Parses JSON file containing dictionary items, and provides a method look_up(text)
    for getting matching DictionaryEntry's for text. Can also be serialized via pickle
    for faster lookup"""

    def __init__(self):
        self._data = None
        self._kanji_to_entry = {}
        self._kana_to_entry = {}
        self._language_abbreviations = set()

    def parse_file(self):
        try:
            with open(DICT_FILE_NAME, encoding="utf-8") as f:
                self._data = json.load(f)
        except OSError:
            print("Could not open Dictionary file %s." % DICT_FILE_NAME)
            self._data = {}
        self.create_entries()

    def get_languages(self):
        return self._language_abbreviations

    def create_entries(self):
        for entry in self._data["words"]:
            kana_readings = []
            kanji_readings = []
            for reading in entry["kanji"]:
                if "rK" in reading["tags"] or "io" in reading["tags"]:
                    # skip rare readings
                    continue
                kanji_readings.append(reading["text"])
            for reading in entry["kana"]:
                if "rK" in reading["tags"] or "io" in reading["tags"]:
                    # skip rare readings
                    continue
                kana_readings.append(reading["text"])
            dict_entry = DictionaryEntry()
            dict_entry.unique_id = entry["id"]
            dict_entry.kana_readings = kana_readings
            dict_entry.kanji_readings = kanji_readings
            for sense in entry["sense"]:
                for glob in sense["gloss"]:
                    language = glob["lang"]
                    self._language_abbreviations.add(language)
                    translation = glob["text"]
                    if sense["partOfSpeech"]:
                        translation = "%s [%s]" % (
                            translation,
                            ", ".join(sense["partOfSpeech"]),
                        )
                    dict_entry.translations.setdefault(language, []).append(translation)
            for reading in kana_readings:
                self._kana_to_entry.setdefault(reading, []).append(dict_entry)
            for reading in kanji_readings:
                self._kanji_to_entry.setdefault(reading, []).append(dict_entry)

    def look_up(self, text):
        result = []
        if text in self._kanji_to_entry:
            result.extend(self._kanji_to_entry[text])
        if text in self._kana_to_entry:
            result.extend(self._kana_to_entry[text])
        return result

    def pickle(self):
        with open(PICKLE_FILE_NAME, "wb") as pickle_file:
            pickle.dump(self, pickle_file)

    @staticmethod
    def de_pickle():
        """Returns the de-pickled dictionary structure stored in pickle_filename. If
        loading failed, None is returned."""
        try:
            with open(PICKLE_FILE_NAME, "rb") as pickle_file:
                return pickle.load(pickle_file)
        except Exception as e:
            return None
