######################################################################
# Manganki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Version 0.0.1
# - initial version
#
######################################################################


from PyQt6.QtWidgets import QApplication

try:
    from .resources import Resources
    from .manganki_window import MangAnkiWindow
    from .app_logic import AppLogic
    from .dict_lookup import DictionaryLookup, DictionaryEntry
except:
    from resources import Resources
    from manganki_window import MangAnkiWindow
    from app_logic import AppLogic
    from dict_lookup import DictionaryLookup, DictionaryEntry

from aqt import mw, dialogs
from aqt.qt import *


def main():
    app = QApplication(sys.argv)
    window = MangAnkiWindow()
    sys.exit(app.exec())


def start_plugin():
    if not hasattr(mw, "manganki_window"):
        mw.manganki_window = MangAnkiWindow()
    else:
        mw.manganki_window.show()
    dialogs.open("AddCards", mw)


if __name__ == "__main__":
    main()
else:
    # Add a button to the main toolbar
    action = QAction("Manganki", mw)
    action.triggered.connect(start_plugin)
    mw.form.menuTools.addAction(action)
