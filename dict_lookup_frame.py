#
# Manganki
# (C) 2024-current Andreas Gaiser
#

import tkinter as tk
from delegates import Delegate


class DictLookupFrame(tk.Frame):
    def __init__(self, delegate: Delegate, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._font = ("Helvetica", 14)
        self._small_font = ("Helvetica", 12)
        self._super_small_font = ("Helvetica", 8)
        self._entry_value = tk.StringVar()
        self._entry = None
        self._listbox = None
        self._delegate = delegate
        self._delegate.add_entry_listener(self.update_controls)
        self._delegate.add_current_translation_entry_listener(
            self.on_change_current_translation_entry
        )
        self.create_widgets()

    def on_changing_entry(self, *args):
        self._delegate.set_current_dict_entry(self._entry_value.get())

    def on_select_listbox(self, event):
        selected_item_index = self._listbox.curselection()
        self._delegate.get_dict_entry_translations()
        if selected_item_index and len(selected_item_index) == 1:
            self._delegate.set_translation_entry_by_index(selected_item_index[0])

    def on_change_current_translation_entry(self):
        entry = self._delegate.get_current_translation_entry()
        if entry.kanji_readings:
            self._expression_text.set(";".join(entry.kanji_readings))
            self._reading_text.set(";".join(entry.kana_readings))
        else:
            self._expression_text.set(";".join(entry.kana_readings))
        self._translation.delete("1.0", tk.END)
        if entry.translations_main_lang:
            self._translation.insert("1.0", ";".join(entry.translations_main_lang))
        else:
            self._translation.insert("1.0", ";".join(entry.translations_eng))
        self._add_card_button.config(
            state="normal"
            if entry.kanji_readings or entry.kana_readings
            else "disabled"
        )

    def on_link_click(self):
        link = self._delegate.get_current_takoboto_link()
        if link:
            import webbrowser

            webbrowser.open(link)

    def on_add_card(self):
        if (
            self._delegate.get_raw_image() is None
            or self._delegate.image_marking_invalid()
        ):
            from tkinter import messagebox

            messagebox.showwarning(
                "Image or image marking invalid",
                "Please copy an appropriate image to the clibpoard and mark the appropriate word in the image.",
            )
            return
        self._delegate.add_anki_card(
            self._expression_text.get(),
            self._reading_text.get(),
            self._translation.get("1.0", tk.END),
            self._delegate.get_current_translation_entry().unique_id,
            self._delegate.get_image_with_marking(),
        )

    def update_controls(self):
        self._listbox.delete(0, tk.END)
        for translation in self._delegate.get_dict_entry_translations():
            self._listbox.insert(tk.END, translation)
        # self._dict_entry_listener

    def create_widgets(self):
        self._entry_value.trace_add("write", self.on_changing_entry)
        self._lookup_label = tk.Label(self, text="Entry lookup", justify="left")
        self._lookup_label.grid(row=0, column=0, padx=0, pady=0)
        self._entry = tk.Entry(self, textvariable=self._entry_value, font=self._font)
        self._entry.grid(row=0, column=1, padx=0, pady=0)
        self._listbox = tk.Listbox(self, font=self._font, selectmode="browse")
        self._listbox.grid(row=1, column=0, columnspan=2, padx=0, pady=0)
        self._listbox.bind("<<ListboxSelect>>", self.on_select_listbox)
        self._expression_label = tk.Label(
            self, text="Expression", anchor="e", justify=tk.LEFT
        )
        self._expression_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self._expression_text = tk.StringVar()
        self._expression = tk.Entry(
            self, textvariable=self._expression_text, font=self._font
        )
        self._expression.grid(row=2, column=1, padx=0, pady=0)
        self._reading_label = tk.Label(
            self, text="Reading", anchor="e", justify=tk.LEFT
        )
        self._reading_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self._reading_text = tk.StringVar()
        self._reading = tk.Entry(self, textvariable=self._reading_text, font=self._font)
        self._reading.grid(row=3, column=1, padx=5, pady=5)

        self._translation_label = tk.Label(
            self, text="Translation", anchor="e", justify=tk.LEFT
        )
        self._translation_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self._translation = tk.Text(self, width=22, height=4, font=self._small_font)
        self._translation.grid(row=4, column=1, padx=5, pady=5)
        self._link_button = tk.Button(
            self, text="Takoboto link", command=self.on_link_click
        )
        self._link_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self._add_card_button = tk.Button(
            self, text="Add card", command=self.on_add_card
        )
        self._add_card_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        self._add_card_button.config(state="disabled")
        jdict_ack = """
Acknowledgment: This tool uses the JMdict/EDICT and KANJIDIC dictionary files. These files are the property of the Electronic Dictionary Research and Development Group, and are used in conformance with the Group's licence. See also https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project.
"""
        self._ack_jdict_label = tk.Label(
            self,
            text=jdict_ack,
            anchor="w",
            font=self._super_small_font,
            justify="left",
            wraplength=330,
        )
        self._ack_jdict_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
