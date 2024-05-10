######################################################################
# MangAnki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Main window containing all controls.
######################################################################

import webbrowser
from aqt.qt import *
from PyQt6.QtWidgets import QMainWindow, QWidget, QSizePolicy
from PyQt6.QtCore import Qt

try:
    from .clipboard_image_widget import ClipboardImageWidget
    from .app_logic import AppState
    from .dict_lookup import DictionaryEntry
    from .anki_transfer import add_reviewer_card
    from .app_logic import AppState, AppLogic
    from .info_window import InfoWindow
    from .splash_screen import SplashScreen
except:
    from clipboard_image_widget import ClipboardImageWidget
    from app_logic import AppState, AppLogic
    from dict_lookup import DictionaryEntry
    from anki_transfer import add_reviewer_card
    from app_logic import AppState, AppLogic
    from info_window import InfoWindow
    from splash_screen import SplashScreen


class PreparationWorker(QThread):
    """Load dictionary asynchronously"""

    finished = pyqtSignal()

    def __init__(self, app_logic: AppLogic):
        super().__init__()
        self._app_logic = app_logic

    def run(self):
        self._app_logic.do_initial_loading_tasks()
        self._app_logic.read_stored_program_state()
        self.finished.emit()


class MangAnkiWindow(QMainWindow):
    """Main window of the plugin."""

    def __init__(self):
        super().__init__()
        self._app_logic = AppLogic()
        self.closeEvent = self.on_close
        self._r = self._app_logic.get_resources()
        self._status_label = None
        self._web_lookup_button = None
        self._transfer_button = None
        self._translations_listbox = None
        self._list_box_label = None
        self._entry_edit = None
        self._entry_label = None
        self._canvas = None
        self._default_font = None
        self._layout = None
        self._central_widget = None
        self._in_process_of_state_updating = False
        self._info_window = InfoWindow()
        self._info_menu = None
        self._canvas_box = None
        self._focus_counter = None
        self._language_combo_box = None
        self._tag_label = None
        self._tag_edit = None
        self.build_gui()
        self.add_listeners()
        self._splash_screen = SplashScreen()
        self._prep_worker = PreparationWorker(self._app_logic)
        self._prep_worker.finished.connect(self.on_preparation_done)
        self._splash_screen.show()
        self.hide()
        self._prep_worker.start()

    def on_preparation_done(self):
        self._splash_screen.close()
        self._language_combo_box.clear()
        self.show()
        self._r["AppState"] = AppState.INITIAL

    def build_gui(self):
        self.setWindowTitle("MangAnki")
        menubar = self.menuBar()
        self._info_menu = menubar.addMenu("Info")
        self._info_menu.aboutToShow.connect(self.open_info_window)
        self._central_widget = QWidget()
        self._default_font = QFont()
        self._default_font.setPointSize(14)
        self._central_widget.setFont(self._default_font)
        self.setCentralWidget(self._central_widget)
        self._layout = QVBoxLayout()
        self._central_widget.setLayout(self._layout)
        preferred_language_label = QLabel("Preferred Translation Language:")
        self._layout.addWidget(preferred_language_label)
        self._language_combo_box = QComboBox()
        self._language_combo_box.clear()
        self._language_combo_box.currentIndexChanged.connect(
            self.on_preferred_language_changed
        )
        self._layout.addWidget(self._language_combo_box)
        canvas_layout = QGridLayout()
        canvas_box = QGroupBox("Screenshot and marking:")
        canvas_size = 300
        canvas_box_size = canvas_size + 50
        canvas_box.setFixedSize(canvas_box_size, canvas_box_size)
        canvas_box.setMaximumHeight(canvas_box_size)
        canvas_box.setMinimumHeight(canvas_box_size)
        canvas_box.setMaximumWidth(canvas_box_size)
        canvas_box.setMinimumWidth(canvas_box_size)
        self._canvas_box = canvas_box
        self._canvas = ClipboardImageWidget(self, self._r, canvas_size, canvas_size)
        self._canvas.setFixedSize(canvas_size, canvas_size)
        canvas_layout.addWidget(
            self._canvas, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        canvas_box.setLayout(canvas_layout)
        self._layout.addWidget(canvas_box)
        hbox_layout = QHBoxLayout()
        self._entry_label = QLabel("Expression:")
        hbox_layout.addWidget(self._entry_label)
        self._entry_edit = QLineEdit()
        hbox_layout.addWidget(self._entry_edit)
        self._entry_edit.textEdited.connect(self.on_entry_changed)
        self._layout.addLayout(hbox_layout)
        self._list_box_label = QLabel("Found entries:")
        self._layout.addWidget(self._list_box_label)
        self._translations_listbox = QListWidget()
        self.update_listbox()
        self._layout.addWidget(self._translations_listbox)
        hbox_layout = QHBoxLayout()
        self._tag_label = QLabel("Tag (optional): ")
        hbox_layout.addWidget(self._tag_label)
        self._tag_edit = QLineEdit()
        hbox_layout.addWidget(self._tag_edit)
        self._tag_edit.textEdited.connect(self.on_tag_edit_changed)
        self._layout.addLayout(hbox_layout)
        self._translations_listbox.itemSelectionChanged.connect(self.on_selection_changed)
        hbox_layout = QHBoxLayout()
        self._transfer_button = QPushButton("Transfer")
        self._transfer_button.clicked.connect(self.on_transfer_click)
        hbox_layout.addWidget(self._transfer_button)
        self._web_lookup_button = QPushButton("Web lookup")
        self._web_lookup_button.clicked.connect(self.on_link_click)
        hbox_layout.addWidget(self._web_lookup_button)
        hbox_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self._layout.addLayout(hbox_layout)
        self._status_label = QLabel()
        self.statusBar().addWidget(self._status_label)
        self.setFixedSize(self.minimumSizeHint())
        self.update_status_for_gui_controls()

    def open_info_window(self):
        self._info_window.show()

    def add_listeners(self):
        self._r.add_listener("AppState", self.update_status_for_gui_controls)
        self._r.add_listener("PossibleEntries", self.update_listbox)
        self._r.add_listener("Tag", self.update_tag_edit_content)

    def stress_on_canvas(self):
        self._focus_counter = 5
        self.blinking_on_canvas()

    def blinking_on_canvas(self):
        if self._focus_counter % 2 == 0:
            self._canvas_box.setStyleSheet("")
            self._canvas_box.setFont(self._default_font)
        else:
            self._canvas_box.setStyleSheet("background-color: lightyellow;")
            self._canvas_box.setFont(self._default_font)
        if self._focus_counter > 0:
            self._focus_counter -= 1
            QTimer.singleShot(200, self.blinking_on_canvas)

    def on_close(self, event):
        self._app_logic.store_program_state()

    def update_listbox(self):
        entries = self._r["PossibleEntries"]
        self._translations_listbox.clear()
        if entries:
            for entry in entries:
                assert isinstance(entry, DictionaryEntry)
                self._translations_listbox.addItem(
                    entry.stringify(self._r["PreferredTranslationLanguage"])
                )
        self._translations_listbox.clearSelection()
        self._translations_listbox.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

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
        if current_state == AppState.LOADING_AND_PREPARING:
            self._canvas.setDisabled(True)
            self._entry_edit.setEnabled(False)
            self._transfer_button.setEnabled(False)
            self._web_lookup_button.setEnabled(False)
            self._entry_edit.setText("")
            self.update_listbox()
            self.set_status_message(
                "Welcome! Please wait until the dictionary is loaded..."
            )
        elif current_state == AppState.INITIAL:
            self._canvas.setDisabled(False)
            self._entry_edit.setEnabled(False)
            self._transfer_button.setEnabled(False)
            self._web_lookup_button.setEnabled(False)
            self._entry_edit.setText("")
            self.update_listbox()
            self.update_language_combobox()
            self.set_status_message(
                'Copy a picture to the clipboard, e.g using "Snipping" tool.'
            )
        elif current_state == AppState.IMAGE_COPIED_NO_MARKING:
            self._canvas.setDisabled(False)
            self._transfer_button.setEnabled(False)
            self._web_lookup_button.setEnabled(False)
            self._entry_edit.setText("")
            self._entry_edit.setEnabled(False)
            self.update_listbox()
            self.set_status_message(
                "Mark the card expression in the picture using the mouse."
            )
            self.stress_on_canvas()
        elif current_state == AppState.MARKING_GIVEN_NO_EXPR:
            self._canvas.setDisabled(False)
            self._entry_edit.setEnabled(True)
            self._transfer_button.setEnabled(False)
            self._web_lookup_button.setEnabled(False)
            self.set_status_message(
                "Enter the desired expression (hiragana/kanji) for the card."
            )
        elif current_state == AppState.EXPR_GIVEN_NO_ENTRY_SELECTED:
            self._canvas.setDisabled(False)
            self._entry_edit.setEnabled(True)
            self._transfer_button.setEnabled(False)
            self._web_lookup_button.setEnabled(False)
            self.update_listbox()
            self.set_status_message("Please choose the desired translation entry.")
        elif current_state == AppState.ENTRY_SELECTED_READY_TO_TRANSFER:
            self._canvas.setDisabled(False)
            self._transfer_button.setEnabled(True)
            self._web_lookup_button.setEnabled(True)
            self.set_status_message(
                'Please click on "Transfer" to move the entry to Anki.'
            )
        else:
            self.set_status_message("Unknown state.")
        self._in_process_of_state_updating = False

    def set_status_message(self, message):
        self._status_label.setText(message)

    def on_preferred_language_changed(self):
        if self._in_process_of_state_updating:
            return
        self._r["PreferredTranslationLanguage"] = self._language_combo_box.currentText()

    def on_entry_changed(self):
        if self._in_process_of_state_updating:
            return
        self._r["CurrentEntry"] = self._entry_edit.text()

    def on_selection_changed(self):
        if self._in_process_of_state_updating:
            return
        current_index = self._translations_listbox.currentRow()
        if current_index != -1:
            self._r["SelectedTranslationIndex"] = current_index

    def on_link_click(self):
        link = self._r["SelectedTranslation"].get_takoboto_link_for_web()
        if link:
            webbrowser.open(link)

    def on_tag_edit_changed(self):
        if self._tag_edit.text() != self._r["Tag"]:
            self._r["Tag"] = self._tag_edit.text()

    def update_tag_edit_content(self):
        if self._tag_edit.text() != self._r["Tag"]:
            self._tag_edit.setText(self._r["Tag"])

    def on_transfer_click(self):
        add_reviewer_card(
            self._r["SelectedTranslation"],
            self._r["Image"],
            self._r["PreferredTranslationLanguage"],
            self._r["Tag"],
        )
