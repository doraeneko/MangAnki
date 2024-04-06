#
# Manganki
# (C) 2024-current Andreas Gaiser
#

from clipboard import *
from delegates import *
from PIL import Image, ImageTk, ImageDraw

SCALE_FILE = "screenshot_scale.png"


class ImageCanvas(tk.Canvas):
    def __init__(
        self, delegate: Delegate = None, master=None, width=500, height=500, **kwargs
    ):
        super().__init__(master, width=width, height=height, **kwargs)
        self._delegate = delegate
        self._width = width
        self._height = height
        self._orig_width = width
        self._orig_height = height
        self._temp_img = None
        self._master = master
        self._marking_image = None
        self._pil_screenshot = None
        self._pil_screenshot_with_marking = None
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        delegate.add_image_marking_listener(self.on_image_marking_change)
        delegate.add_image_listener(self.update_clipboard_image)
        self.update_clipboard_image()

    def resize_canvas(self, new_width, new_height):
        self._width = new_width
        self._height = new_height
        self.config(width=new_width, height=new_height)

    def create_marking(self, x1, y1, x2, y2, **kwargs):
        if "alpha" in kwargs:
            alpha = int(kwargs.pop("alpha") * 255)
            fill = kwargs.pop("fill")
            fill = self.winfo_rgb(fill) + (alpha,)
            marking_image = Image.new("RGBA", (x2 - x1, y2 - y1), fill)
            self._pil_screenshot_with_marking = self._pil_screenshot.copy()
            self._pil_screenshot_with_marking.paste(
                marking_image, (x1, y1, x2, y2), marking_image
            )
            marking_image = ImageTk.PhotoImage(marking_image)
            self._marking_image = marking_image
            self.create_image(x1, y1, image=marking_image, anchor="nw")
        return self.create_rectangle(x1, y1, x2, y2, **kwargs)

    def update_screenshot(self, image: PhotoImage, max_width, max_height):
        image.write(SCALE_FILE, format="png")
        pillow_image = Image.open(SCALE_FILE, formats=["png"]).convert("RGBA")
        pillow_image.thumbnail((max_width, max_height), Image.LANCZOS)
        pillow_image.save(SCALE_FILE)
        self._pil_screenshot = pillow_image
        result = PhotoImage(file=SCALE_FILE, format="png")
        self._temp_img = (
            result  # stupid garbage collection destroys the picture otherwise (!)
        )
        self._delegate.set_image_with_marking(self._temp_img)
        return result

    def update_clipboard_image(self):
        image = self._delegate.get_raw_image()
        if image:
            image = self.update_screenshot(image, self._orig_width, self._orig_height)
            self.resize_canvas(image.width(), image.height())
            self.create_image(0, 0, image=image, anchor=tk.NW)
        else:
            self.delete("all")
            self.resize_canvas(self._width, self._height)

    def draw_marking(self):
        if not self._delegate.get_raw_image():
            return
        self.update_clipboard_image()
        (x1, y1, x2, y2) = self._delegate.get_image_marking()
        self.create_marking(
            x1,
            y1,
            x2,
            y2,
            alpha=0.2,
            fill="yellow",
            outline="red",
        )

    def on_click(self, event):
        self.update_clipboard_image()
        self._delegate.set_image_marking(event.x, event.y, event.x, event.y)

    def on_drag(self, event):
        (x1, y1, _, _) = self._delegate.get_image_marking()
        self._delegate.set_image_marking(x1, y1, event.x, event.y)

    def update_marking_image(self):
        self._delegate.set_image_with_marking(self._pil_screenshot_with_marking)

    def on_image_marking_change(self):
        self.draw_marking()

    def on_release(self, event):
        (x1, y1, _, _) = self._delegate.get_image_marking()
        self._delegate.set_image_marking(x1, y1, event.x, event.y)
        self.update_marking_image()
