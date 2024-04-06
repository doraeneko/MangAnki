#
# Manganki
# (C) 2024-current Andreas Gaiser
#

import typing
from tkinter import PhotoImage
from dataclasses import dataclass, field
from dict_lookup import DictionaryEntry
from PIL import Image


@dataclass
class Bounding_Box_XYXY:
    LEFT: int = 0
    TOP: int = 0
    RIGHT: int = 0
    BOTTOM: int = 0


@dataclass
class ImageModel:
    current_raw_image: typing.Optional[PhotoImage] = None
    current_image_with_marking: typing.Optional[Image.Image] = None
    current_marking: Bounding_Box_XYXY = Bounding_Box_XYXY(0, 0, 0, 0)


@dataclass
class DictModel:
    current_lookup: str = ""
    current_entry: typing.Optional[DictionaryEntry] = None
    entries: typing.List[DictionaryEntry] = field(default_factory=list)
    translations: typing.List[DictionaryEntry] = field(default_factory=list)


@dataclass
class AppModel:
    image: ImageModel = ImageModel()
    dict: DictModel = DictModel()
