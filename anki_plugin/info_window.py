######################################################################
# Manganki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Info window: Licenses and acknowledgments
######################################################################

from aqt.qt import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget

JMDICT_ACKNOWLEDGMENTS = """
<h2>Acknowledgments</h2>
<p>This plugin uses the JMdict/EDICT and KANJIDIC dictionary files. These files are the property of the Electronic
 Dictionary Research and Development Group, and are used in conformance with the Group's licence. 
 See also <a href="https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project">this site</a>.
</p>
<p>
This plugin uses the handy JSON export files from <a href=https://github.com/scriptin/jmdict-simplified>jmdict-simplified</a>.
</p>
"""
LICENSE_NOTE = """
<h2>License</h2>
MIT License

Copyright (c) 2024 Andreas Gaiser
<p></p>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.build_ui()

    def build_ui(self):
        self.setWindowTitle("Info")
        self.setGeometry(100, 100, 300, 500)
        layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        text = JMDICT_ACKNOWLEDGMENTS + LICENSE_NOTE
        info_text.setHtml(text)
        layout.addWidget(info_text)
        self.setLayout(layout)
