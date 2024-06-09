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
    from .anki_transfer import transfer_given_infos
    from .app_logic import AppState, AppLogic
    from .info_window import InfoWindow
    from .splash_screen import SplashScreen
    from .playsound import playsound
    from .settings_window import SettingsWindow
except:
    from clipboard_image_widget import ClipboardImageWidget
    from app_logic import AppState, AppLogic
    from dict_lookup import DictionaryEntry
    from anki_transfer import transfer_given_infos
    from app_logic import AppState, AppLogic
    from info_window import InfoWindow
    from splash_screen import SplashScreen
    from playsound import playsound
    from settings_window import SettingsWindow


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
    """Main window of the add-on."""

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
        self._settings_menu = None
        self._info_window = InfoWindow()
        self._settings_window = SettingsWindow(self._app_logic)
        self._info_menu = None
        self._canvas_box = None
        self._focus_counter = None
        self._audio_label = None
        self._audio_edit = None
        self._audio_button = None
        self._audio_clear_button = None
        self._in_process_of_state_updating = False
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
        self.show()
        self._settings_window.on_preparation_done()
        self._r["AppState"] = AppState.INITIAL
        self._r["AudioPath"] = ""

    def build_gui(self):
        self.setWindowTitle("MangAnki")
        menubar = self.menuBar()
        self._info_menu = menubar.addMenu("Info")
        self._info_menu.aboutToShow.connect(self.open_info_window)
        self._settings_menu = menubar.addMenu("Settings")
        self._settings_menu.aboutToShow.connect(self.open_settings_window)
        self._central_widget = QWidget()
        self._default_font = QFont()
        self._default_font.setPointSize(14)
        self._central_widget.setFont(self._default_font)
        self.setCentralWidget(self._central_widget)
        self._layout = QVBoxLayout()
        self._central_widget.setLayout(self._layout)
        canvas_layout = QGridLayout()
        canvas_box = QGroupBox("Screenshot and marking:")
        canvas_size = 350
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
        self._translations_listbox.itemSelectionChanged.connect(
            self.on_selection_changed
        )
        hbox_layout = QHBoxLayout()
        self._audio_label = QLabel("Audio (opt.): ")
        self._layout.addWidget(self._audio_label)
        self._audio_edit = QLineEdit()
        hbox_layout.addWidget(self._audio_edit)
        self._audio_edit.textEdited.connect(self.on_audio_edit_changed)
        self._audio_button = QPushButton("𝄞")
        self._audio_button.clicked.connect(self.on_play_click)
        hbox_layout.addWidget(self._audio_button)
        self._audio_clear_button = QPushButton("X")
        self._audio_clear_button.clicked.connect(self.on_audio_clear)
        hbox_layout.addWidget(self._audio_clear_button)
        self._layout.addLayout(hbox_layout)

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

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

    def open_info_window(self):
        self._info_window.show()

    def open_settings_window(self):
        self._settings_window.exec()

    def add_listeners(self):
        self._r.add_listener("AppState", self.update_status_for_gui_controls)
        self._r.add_listener("PossibleEntries", self.update_listbox)
        self._r.add_listener("AudioPath", self.update_audio_edit_content)

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

    def update_status_for_gui_controls(self):
        if self._r["AppState"] == AppState.LOADING_AND_PREPARING:
            return
        self._in_process_of_state_updating = True
        self._settings_window.update_status_for_gui_controls()
        current_state = self._r["AppState"]
        if current_state == AppState.INITIAL:
            self._canvas.setDisabled(False)
            self._entry_edit.setEnabled(False)
            self._transfer_button.setEnabled(False)
            self._web_lookup_button.setEnabled(False)
            self._entry_edit.setText("")
            self.update_listbox()
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
            self._transfer_button.setEnabled(True)
            self._web_lookup_button.setEnabled(False)
            self.set_status_message(
                "Enter the desired expression (hiragana/kanji) for the card."
            )
        elif current_state == AppState.EXPR_GIVEN_NO_ENTRY_SELECTED:
            self._canvas.setDisabled(False)
            self._entry_edit.setEnabled(True)
            self._transfer_button.setEnabled(True)
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

    def on_audio_edit_changed(self):
        if self._audio_edit.text() != self._r["AudioPath"]:
            self._r["AudioPath"] = self._audio_edit.text()
        self._audio_button.setDisabled(not self._r["AudioPath"])

    def update_audio_edit_content(self):
        if self._audio_edit.text() != self._r["AudioPath"]:
            self._audio_edit.setText(self._r["AudioPath"])
        self._audio_button.setDisabled(not self._r["AudioPath"])

    def on_play_click(self):
        try:
            playsound(self._r["AudioPath"])
        except:
            self.show_error_message(
                "Could not play audio file: %s" % str(self._r["AudioPath"])
            )

    def on_audio_clear(self):
        self._r["AudioPath"] = ""

    def on_transfer_click(self):
        transfer_given_infos(
            self._r["CurrentEntry"],
            self._r["SelectedTranslation"],
            self._r["Image"],
            self._r["PreferredTranslationLanguage"],
            self._r["Tag"],
            self._r["AudioPath"],
        )
