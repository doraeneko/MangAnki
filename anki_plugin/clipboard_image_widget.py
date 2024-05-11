######################################################################
# MangAnki
# Anki plugin to help with vocab mining of online mangas
# Copyright 2024, Andreas Gaiser
######################################################################
# Widget for displaying clipboard images and setting a marking.
######################################################################
import os

from aqt.qt import *
from PyQt6.QtWidgets import QApplication, QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QPen, QImage
from PyQt6.QtCore import Qt, QPoint, QUrl

try:
    from .resources import Resources
    from .app_logic import AppState
except:
    from resources import Resources
    from app_logic import AppState


class ClipboardImageWidget(QWidget):
    def __init__(self, parent, resources: Resources, width=500, height=500):
        super().__init__(parent)
        self._r = resources
        self._parent = parent
        self.setGeometry(0, 0, width, height)
        self._max_width = width
        self._max_height = height
        self._drawing = False
        self._last_point = QPoint()
        self._current_point = QPoint()
        self.setMaximumHeight(self._max_height)
        self.setMinimumHeight(min(50, self._max_height))
        self.setMaximumWidth(self._max_width)
        self.setMinimumWidth(min(50, self._max_width))
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    def get_rect_coords(self, p0, p1):
        width = abs(p0.x() - p1.x())
        height = abs(p0.y() - p1.y())
        start_x = min(p0.x(), p1.x())
        start_y = min(p0.y(), p1.y())
        return start_x, start_y, width, height

    def on_clipboard_changed(self):
        if self._r.AppState == AppState.LOADING_AND_PREPARING:
            return
        mime_data = self.clipboard.mimeData()
        if mime_data.hasImage():
            # Retrieve image data
            image = mime_data.imageData()
            if image.width() > self._max_width or image.height() > self._max_height:
                # scale image
                self._r["OriginalClipboardImage"] = QPixmap.fromImage(image).scaled(
                    self._max_width,
                    self._max_height,
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                    transformMode=Qt.TransformationMode.SmoothTransformation,
                )
            else:
                self._r["OriginalClipboardImage"] = QPixmap.fromImage(image)
            self._r["Marking"] = None
            self.update_image()
        elif mime_data.hasUrls() and len(mime_data.urls()) == 1:
            self._r["AudioPathUrl"] = mime_data.urls()[0]
        # Clear canvas if clipboard does not contain an image
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._r["Image"]:
            self._drawing = True
            self._last_point = event.pos()
            self._current_point = event.pos()

    def mouseMoveEvent(self, event):
        if self._drawing:
            self._current_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._r["Image"]:
            self._drawing = False
            shape = (self._last_point, self._current_point)
            self._r["Marking"] = shape
            self.update()

    def update_image(self):
        image_var = QImage(self.size(), QImage.Format.Format_ARGB32)
        self.render(image_var)
        self._r["Image"] = image_var
        # image_var.save("imagename.png")

    def paintEvent(self, event):
        self.draw(self._r["Marking"])

    def draw(self, marking):
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.GlobalColor.red)
        painter.setPen(pen)
        if self._r["OriginalClipboardImage"]:
            bg_img = self._r["OriginalClipboardImage"]
            self.setMinimumHeight(bg_img.height())
            self.setMaximumHeight(bg_img.height())
            self.setMinimumWidth(bg_img.width())
            self.setMaximumWidth(bg_img.width())
            self.resize(bg_img.width(), bg_img.height())
            painter.drawPixmap(0, 0, bg_img)
        if marking:
            painter.setOpacity(0.3)
            painter.fillRect(
                *self.get_rect_coords(marking[0], marking[1]), QColor(255, 255, 0)
            )
            self.update_image()

        if self._drawing:
            painter.drawRect(
                *self.get_rect_coords(self._last_point, self._current_point)
            )
        self.adjustSize()
        painter.setOpacity(1.0)
        pen.setColor(Qt.GlobalColor.black)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.size().width(), self.size().height())
