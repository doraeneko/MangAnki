#
# Manganki
# (C) 2024-current Andreas Gaiser
#

import dataclasses
import xml.etree.ElementTree as ET
import typing


@dataclasses.dataclass
class DictionaryEntry:
    translations_eng: typing.List[str] = dataclasses.field(default_factory=list)
    translations_main_lang: typing.List[str] = dataclasses.field(default_factory=list)
    unique_id: str = ""
    kanji_readings: typing.List[str] = dataclasses.field(default_factory=list)
    kana_readings: typing.List[str] = dataclasses.field(default_factory=list)

    def stringify(self):
        if self.translations_main_lang:
            return ",".join(self.translations_main_lang)
        else:
            return ",".join(self.translations_eng)


XML_NAMESPACE = {"xml": "http://www.w3.org/XML/1998/namespace"}


class DictionaryLookup:
    def __init__(self, preferred_language: str):
        self._tree = None
        self._root = None
        self._preferred_language = preferred_language
        self._kanji_to_entry = {}
        self._reading_to_entry = {}

    def parse_file(self, file_path):
        try:
            self._tree = ET.parse(file_path)
            self._root = self._tree.getroot()
        except Exception as e:
            print("Could not load dict file %s: %s" % (file_path, e))
            raise
        self.create_entries()

    def look_up(self, text):
        result = []
        if text in self._kanji_to_entry:
            result.extend(self._kanji_to_entry[text])
        if text in self._reading_to_entry:
            result.extend(self._reading_to_entry[text])
        return result

    def create_entries(self):
        for entry_node in self._root.iter("entry"):
            id = entry_node.find("ent_seq")
            dict_entry = DictionaryEntry()
            dict_entry.unique_id = id.text
            # find all possible translations
            preferred_gloss_tags = entry_node.findall(
                ".//gloss[@xml:lang='%s']" % self._preferred_language, XML_NAMESPACE
            )
            for tag in preferred_gloss_tags:
                dict_entry.translations_main_lang.append(tag.text)
            if self._preferred_language != "eng":
                en_gloss_tags = entry_node.findall(
                    ".//gloss[@xml:lang='eng']", XML_NAMESPACE
                )
                for tag in en_gloss_tags:
                    dict_entry.translations_eng.append(tag.text)

            reb_tags = entry_node.findall(".//reb")
            for tag in reb_tags:
                self._reading_to_entry.setdefault(tag.text, []).append(dict_entry)
                dict_entry.kana_readings.append(tag.text)
            keb_tags = entry_node.findall(".//keb")
            for tag in keb_tags:
                self._kanji_to_entry.setdefault(tag.text, []).append(dict_entry)
                dict_entry.kanji_readings.append(tag.text)
