######################################################################
# MangAnki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Splash screen for entertain during loading time.
######################################################################

import os
from aqt.qt import *
from PyQt6.QtCore import Qt

SPLASH_SCREEN_IMAGE = "%s/%s" % (os.path.dirname(__file__), "splashscreen.jpeg")


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(
            QPixmap(SPLASH_SCREEN_IMAGE).scaled(
                400,
                400,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.setDisabled(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        font = QFont("Arial", 20)  # Adjust the font size as needed
        text_label = QLabel("MangAnki is loading...", self)
        text_label.setStyleSheet("color: black;")
        text_label.setFont(font)
        text_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        text_label.move(5, 10)  #
        text_label.show()
