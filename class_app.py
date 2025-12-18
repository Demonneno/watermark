from re import X
import tkinter as tk
from tkinter import ttk, Label
from tkinter import filedialog
from tkinter.filedialog import askopenfilename as openfile

# from turtle import mainloop
from PIL import Image, ImageTk, ImageDraw, ImageFont
# import os
# import sys

DEFAULT_FONT_SIZE = 60
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 200


def user_image():
    while True:
        try:
            file = openfile()
            if file:
                return file
            else:
                print("openfile cancelled")
        except OSError:
            print("Choose a file")


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Image Editing Tool: Watermarking")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.tk.call("tk", "scaling", 2.0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.watermark_text = tk.StringVar(value="Sample Text")

        self.preview = Preview(self, watermark_var=self.watermark_text)
        self.tree = Tree(self, watermark_var=self.watermark_text)

        self.preview.grid(row=0, column=1, sticky="nsew")
        self.tree.grid(row=0, column=0, sticky="ns")


class Preview(ttk.Frame):
    def __init__(self, parent, watermark_var):
        super().__init__(parent, width=700, relief="sunken")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.watermark_var = watermark_var
        self.wm_x = 100
        self.wm_y = 100
        self.dragging = False

        self.wm_x_display = 400
        self.wm_y_display = 300
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.label = ttk.Label(self, text="Preview")
        self.label.grid(row=0, column=0, sticky="nsew")
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)

        self.base_font_size = DEFAULT_FONT_SIZE
        try:
            self.font = ImageFont.truetype("arial.ttf", self.base_font_size)
        except OSError:
            self.font = ImageFont.load_default(size=self.base_font_size)

    def load_image(self):
        path = openfile(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if not path:
            return

        img = Image.open(path).convert("RGBA")
        img_copy = img.copy()

        self.preview_image = img.copy()
        self.preview_image.thumbnail((700, 400), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(img_copy)
        self.label.configure(image=photo, text="")
        self.photo = photo

        self.original_image = img
        self.img_width, self.img_height = img.size
        self.wm_x = self.img_width // 2
        self.wm_y = self.img_height // 2

        self.wm_x_display = 350  # center of 700px preview
        self.wm_y_display = 300

        self.redraw_with_watermark()

    def update_font_size(self, new_size):
        self.base_font_size = new_size

        try:
            self.font = ImageFont.truetype("arial.ttf", new_size)
        except OSError:
            self.font = ImageFont.load_default(size=new_size)

        if hasattr(self, "original_image"):
            self.redraw_with_watermark()

    def start_drag(self, event):
        if not hasattr(self, "original_image"):
            return
        # Store where we clicked relative to current watermark position
        self.drag_offset_x = event.x - self.wm_x_display
        self.drag_offset_y = event.y - self.wm_y_display
        self.dragging = True

    def drag(self, event):
        if not self.dragging:
            return
        # Follow mouse exactly in preview coordinates
        self.wm_x_display = event.x - self.drag_offset_x
        self.wm_y_display = event.y - self.drag_offset_y
        self.redraw_with_watermark()

    def stop_drag(self, event):
        self.dragging = False

    def redraw_with_watermark(self):
        if not hasattr(self, "original_image"):
            return

        img = self.preview_image.copy()
        draw = ImageDraw.Draw(img)

        text = self.watermark_var.get()

        draw.text(
            (self.wm_x_display, self.wm_y_display),
            text,
            fill="white",
            font=self.font,
            stroke_width=4,
            stroke_fill="black",
            anchor="mm",
        )

        self.photo = ImageTk.PhotoImage(img)
        self.label.configure(image=self.photo)
        self.label.image = self.photo  # type: ignore

    def save_image(self):
        if not hasattr(self, "original_image"):
            return

        final = self.original_image.copy()
        draw = ImageDraw.Draw(final)

        scale_x = final.width / self.preview_image.width
        scale_y = final.height / self.preview_image.height
        scale = min(scale_x, scale_y)
        font_size = int(self.base_font_size * scale)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default(size=font_size)

        draw.text(
            (self.wm_x_display * scale_x, self.wm_y_display * scale_y),
            self.watermark_var.get(),
            fill="white",
            font=font,
            stroke_width=int(4 * scale),
            stroke_fill="black",
            anchor="mm",
        )

        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            final.save(path)


class Tree(ttk.Frame):
    def __init__(self, parent, watermark_var):
        super().__init__(parent, width=250, relief="raised", padding=10)
        self.watermark_var = watermark_var

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Image Selection", font=("", 12)).grid(
            row=0, column=0, sticky="n", padx=10, pady=10
        )
        ttk.Button(
            self, text="Choose your Image", command=parent.preview.load_image
        ).grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(self, text="Watermark", font=("", 12)).grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )

        ttk.Label(self, text="Font Size", font=("", 12)).grid(
            row=3, column=0, sticky="w", padx=10, pady=(20, 5)
        )
        self.font_size_var = tk.IntVar(value=DEFAULT_FONT_SIZE)
        slider = ttk.Scale(
            self,
            from_=MIN_FONT_SIZE,
            to=MAX_FONT_SIZE,
            orient="horizontal",
            variable=self.font_size_var,
            command=lambda val: parent.preview.update_font_size(int(float(val))),
        )
        slider.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(self, textvariable=self.font_size_var).grid(
            row=5, column=0, sticky="e", padx=70
        )

        entry = ttk.Entry(self, textvariable=self.watermark_var, font=("", 11))
        entry.grid(row=6, column=0, sticky="ew", padx=10, pady=5)

        ttk.Button(
            self, text="Save Watermarked Image", command=parent.preview.save_image
        ).grid(row=7, column=0, sticky="ew", padx=10, pady=20)

        # tree = ttk.Treeview(self)
        # tree.grid(row=1, column=0, sticky="nsew")


def main() -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
