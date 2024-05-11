######################################################################
# MangAnki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Settings window
######################################################################


from aqt.qt import *

try:
    from .app_logic import AppState
    from .dict_lookup import DictionaryEntry
    from .app_logic import AppState, AppLogic
except:
    from app_logic import AppState, AppLogic
    from dict_lookup import DictionaryEntry
    from app_logic import AppState, AppLogic


class SettingsWindow(QDialog):
    """Settings window of the add-on."""

    def __init__(self, app_logic: AppLogic):
        super().__init__()
        self._app_logic = app_logic
        self._r = self._app_logic.get_resources()
        self._central_widget = None
        self._default_font = None
        self._layout = None
        self._language_combo_box = None
        self._tag_label = None
        self._tag_edit = None
        self._in_process_of_state_updating = False
        self.build_gui()
        self.add_listeners()

    def build_gui(self):
        self.setWindowTitle("MangAnki settings")
        self._layout = QVBoxLayout(self)
        self._default_font = QFont()
        self._default_font.setPointSize(14)
        # self._central_widget.setFont(self._default_font)
        preferred_language_label = QLabel("Preferred translation language:")
        preferred_language_label.setFont(self._default_font)
        self._layout.addWidget(preferred_language_label)
        self._language_combo_box = QComboBox()
        self._language_combo_box.clear()
        self._language_combo_box.currentIndexChanged.connect(
            self.on_preferred_language_changed
        )
        self._language_combo_box.setFont(self._default_font)
        self._layout.addWidget(self._language_combo_box)
        hbox_layout = QHBoxLayout()
        self._tag_label = QLabel("Anki Tag (optional): ")
        self._tag_label.setFont(self._default_font)
        hbox_layout.addWidget(self._tag_label)
        self._tag_edit = QLineEdit()
        self._tag_edit.setFont(self._default_font)
        hbox_layout.addWidget(self._tag_edit)
        self._tag_edit.textEdited.connect(self.on_tag_edit_changed)
        self._layout.addLayout(hbox_layout)
        # self.setFixedSize(self.minimumSizeHint())
        self.update_status_for_gui_controls()

    def add_listeners(self):
        self._r.add_listener("Tag", self.update_tag_edit_content)

    def on_preparation_done(self):
        self._language_combo_box.clear()

    def update_language_combobox(self):
        if self._r["AppState"] == AppState.LOADING_AND_PREPARING:
            return
        self._language_combo_box.setCurrentText(self._r["PreferredTranslationLanguage"])

    def update_status_for_gui_controls(self):
        if self._r["AppState"] == AppState.LOADING_AND_PREPARING:
            return
        self._in_process_of_state_updating = True
        self._language_combo_box.clear()
        for language in sorted(self._r["TranslationLanguages"]):
            self._language_combo_box.addItem(language)
        self.update_language_combobox()
        current_state = self._r["AppState"]
        if current_state == AppState.INITIAL:
            self.update_language_combobox()
        elif current_state == AppState.IMAGE_COPIED_NO_MARKING:
            pass
        elif current_state == AppState.MARKING_GIVEN_NO_EXPR:
            pass
        elif current_state == AppState.EXPR_GIVEN_NO_ENTRY_SELECTED:
            pass
        elif current_state == AppState.ENTRY_SELECTED_READY_TO_TRANSFER:
            pass
        else:
            self.set_status_message("Unknown state.")
        self._in_process_of_state_updating = False

    def on_preferred_language_changed(self):
        if self._in_process_of_state_updating:
            return
        self._r["PreferredTranslationLanguage"] = self._language_combo_box.currentText()

    def on_tag_edit_changed(self):
        if self._tag_edit.text() != self._r["Tag"]:
            self._r["Tag"] = self._tag_edit.text()

    def update_tag_edit_content(self):
        if self._tag_edit.text() != self._r["Tag"]:
            self._tag_edit.setText(self._r["Tag"])
