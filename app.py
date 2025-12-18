import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from tkinter import font

import platform
from PIL import ImageFont

ROOT_HEIGHT = 700
ROOT_WIDTH = 1000
TREE_WIDTH = 250
PREVIEW_WIDTH = 700

PREVIEW_IMG_HEIGHT = 800
PREVIEW_IMG_WIDTH = 800

DEFAULT_FONT_SIZE = 30


def get_default_font(size=DEFAULT_FONT_SIZE):
    system = platform.system()
    try:
        if system == "Windows":
            return ImageFont.truetype("arial.ttf", size)
        elif system == "Darwin":  # macOS
            return ImageFont.truetype("Helvetica.ttf", size)
        elif system == "Linux":
            # Common Linux font files
            for name in [
                "DejaVuSans.ttf",
                "LiberationSans-Regular.ttf",
                "NotoSans-Regular.ttf",
                "Ubuntu-R.ttf",
                "JetBrainsMono-Regular.ttf",
            ]:
                try:
                    return ImageFont.truetype(name, size)
                except IOError:
                    continue
        # Try generic names as last resort
        for name in ["sans-serif", "DejaVu Sans", "Liberation Sans"]:
            try:
                return ImageFont.truetype(name, size)
            except IOError:
                continue
    except Exception:
        pass
    return ImageFont.load_default()


def select_img():
    open_image = filedialog.askopenfilename(
        initialdir="~/Pictures/", filetypes=[("Image File", (".jpg .png .bmp"))]
    )
    return open_image


def load_img(path):
    img = Image.open(path).convert("RGBA")
    return img


def create_preview(pil):
    preview_copy = pil.copy()
    max_w = image_preview_canvas.winfo_width() - 20
    max_h = image_preview_canvas.winfo_height() - 20
    preview_copy.thumbnail(
        size=(max_w, max_h),
        resample=Image.Resampling.LANCZOS,
    )
    # Store the actual preview size for save scaling
    image_preview_canvas.preview_width = preview_copy.width
    image_preview_canvas.preview_height = preview_copy.height
    return preview_copy


def center_image():
    if hasattr(image_preview_canvas, "image_id"):
        image = image_preview_canvas.image_id  # type: ignore[attr-defined]
        image_width = image_preview_canvas.winfo_width() // 2
        image_height = image_preview_canvas.winfo_height() // 2
        image_preview_canvas.coords(image, image_width, image_height)


def image_open():
    if (
        hasattr(image_preview_canvas, "watermark_image_id")
        and image_preview_canvas.watermark_image_id  # type: ignore[attr-defined]
    ):
        image_preview_canvas.delete(image_preview_canvas.watermark_image_id)  # type: ignore[attr-defined]
        image_preview_canvas.watermark_image_id = None  # type: ignore[attr-defined]

    watermark_textbox.delete(0, tk.END)
    img_path = select_img()
    if img_path:
        pil_img = load_img(img_path)
        pre_img = create_preview(pil_img)
        image = ImageTk.PhotoImage(pre_img)
        image_preview_canvas.original_pil = pil_img  # type: ignore[attr-defined]
        image_preview_canvas.keep_alive_photo = image  # type: ignore[attr-defined]
        image_preview_canvas.image_id = image_preview_canvas.create_image(  # type: ignore[attr-defined]
            0, 0, image=image, anchor=tk.CENTER, tags=("static")
        )
        center_image()
        create_text()
        field_status()
    else:
        messagebox.showinfo(
            title="Error Opening Image",
            message="There was an issue opening your file. Please try again.",
        )


def bbox_dims(font, text):
    bbox = font.getbbox(text)
    text_width = int((bbox[2] - bbox[0]) * 1.0)
    text_height = int((bbox[3] - bbox[1]) * 1.0)
    padding = 0
    return text_width, text_height, padding


def text_draw_dims(img, text_width, text_height):
    text_x = (img.width - text_width) // 2
    text_y = (img.height - text_height) // 2

    return text_x, text_y


def create_text():
    new_text = watermark_textbox.get().strip()
    canvas = image_preview_canvas

    if not new_text:
        if hasattr(canvas, "watermark_image_id") and canvas.watermark_image_id:  # type: ignore[attr-defined]
            canvas.itemconfigure(canvas.watermark_image_id, state="hidden")  # type: ignore[attr-defined]
        return

    try:
        font_size = int(watermark_text_size.get())
    except:
        font_size = 36

    font = get_default_font(font_size)
    text_width, text_height, padding = bbox_dims(font, new_text)
    image_preview_canvas.text_width, image_preview_canvas.text_height = (
        text_width,
        text_height,
    )
    img = Image.new(
        "RGBA", (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0)
    )
    draw = ImageDraw.Draw(img)
    text_x, text_y = text_draw_dims(img, text_width, text_height)
    r, g, b = getattr(image_preview_canvas, "watermark_rgb", (255, 255, 255))

    try:
        alpha = int(opacity_slider.get())
    except:
        alpha = 255

    fill_color = (r, g, b, alpha)

    draw.text(
        (text_x, text_y),
        new_text,
        font=font,
        fill=fill_color,
        anchor="lt",
    )  # type: ignore[attr-defined]
    photo = ImageTk.PhotoImage(img)

    if hasattr(canvas, "watermark_image_id") and canvas.watermark_image_id:  # type: ignore[attr-defined]
        canvas.itemconfigure(canvas.watermark_image_id, image=photo, state="normal")  # type: ignore[attr-defined]
    else:
        item_id = canvas.create_image(
            canvas.winfo_width() // 2,
            canvas.winfo_height() // 2,
            image=photo,
            anchor="center",
            tags=("draggable", "watermark"),
        )
        canvas.watermark_image_id = item_id  # type: ignore[attr-defined]
        canvas.tag_raise(item_id)

    canvas.watermark_photo = photo  # type: ignore[attr-defined]


def save_image_with_watermark():
    if not hasattr(image_preview_canvas, "original_pil"):
        messagebox.showinfo("No Image", "Load an image first.")
        return

    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All files", "*.*")],
    )
    if not save_path:
        return

    full_img = image_preview_canvas.original_pil.copy()
    canvas = image_preview_canvas

    new_text = watermark_textbox.get().strip()
    if new_text and canvas.watermark_image_id:
        # Get main preview image bounds (letterbox)
        main_x1, main_y1, main_x2, main_y2 = canvas.bbox(canvas.image_id)

        # Get watermark position relative to preview image (subtract letterbox offset)
        relative_x = canvas.wm_x_display - main_x1
        relative_y = canvas.wm_y_display - main_y1

        # Scale factors (using stored preview image size)
        preview_w = canvas.preview_width
        preview_h = canvas.preview_height

        scale_x = full_img.width / preview_w
        scale_y = full_img.height / preview_h

        full_x = relative_x * scale_x
        full_y = relative_y * scale_y

        # Font size (scaled)
        try:
            preview_font_size = int(watermark_text_size.get())
        except:
            preview_font_size = 36
        full_font_size = int(preview_font_size * scale_x)
        font = get_default_font(full_font_size)

        # Color and opacity
        r, g, b = canvas.watermark_rgb
        alpha = int(opacity_slider.get())
        fill = (r, g, b, alpha)

        # Draw
        draw = ImageDraw.Draw(full_img)
        draw.text((full_x, full_y), new_text, font=font, fill=fill, anchor="mm")

    full_img.save(save_path)
    messagebox.showinfo("Success", f"Saved:\n{save_path}")


def click(event):
    canvas = image_preview_canvas
    halo = 10
    closest_item = canvas.find_closest(event.x, event.y, halo=halo)
    if not closest_item:
        return
    candidate_id = closest_item[0]
    tags = canvas.gettags(candidate_id)
    if "draggable" not in tags:
        return
    canvas.current_id = candidate_id  # type: ignore[attr-defined]
    canvas.drag_start_x = event.x  # type: ignore[attr-defined]
    canvas.drag_start_y = event.y  # type: ignore[attr-defined]
    print(f"the draggable text is: {canvas.current_id}")  # type: ignore[attr-defined]

    canvas.config(cursor="hand2")


def drag_motion(event):
    canvas = image_preview_canvas
    if not hasattr(canvas, "current_id") or canvas.current_id is None:  # type: ignore[attr-defined]
        print(f"we failed at {canvas.current_id}!")  # type: ignore[attr-defined]
        return

    drag_id = canvas.current_id  # type: ignore[attr-defined]

    main_x1, main_y1, main_x2, main_y2 = canvas.bbox(canvas.image_id)  # type: ignore[attr-defined]
    overlay_x1, overlay_y1, overlay_x2, overlay_y2 = canvas.bbox(drag_id)

    desired_center_x = event.x
    desired_center_y = event.y

    overlay_width = overlay_x2 - overlay_x1
    overlay_height = overlay_y2 - overlay_y1
    half_width = overlay_width / 2
    half_height = overlay_height / 2

    new_center_x = max(
        main_x1 + half_width, min(main_x2 - half_width, desired_center_x)
    )
    new_center_y = max(
        main_y1 + half_height, min(main_y2 - half_height, desired_center_y)
    )

    current_center_x = (overlay_x1 + overlay_x2) / 2
    current_center_y = (overlay_y1 + overlay_y2) / 2

    dx = new_center_x - current_center_x
    dy = new_center_y - current_center_y

    canvas.move(drag_id, dx, dy)

    current_x, current_y = canvas.coords(drag_id)
    canvas.wm_x_display = current_x
    canvas.wm_y_display = current_y


def stop_drag(event):
    canvas = image_preview_canvas

    if hasattr(canvas, "current_id"):
        canvas.current_id = None  # type: ignore[attr-defined]

        canvas.config(cursor="")


def field_status():
    if hasattr(image_preview_canvas, "image_id") and image_preview_canvas.image_id:  # type: ignore[attr-defined]
        watermark_textbox.config(state="normal")
    else:
        watermark_textbox.config(state="disabled")
        watermark_textbox.delete(0, tk.END)


def color_chooser():
    result = colorchooser.askcolor(
        color=image_preview_canvas.watermark_color,  # type: ignore[attr-defined]
        title="Choose a Color",  # type: ignore[attr-defined]
    )
    rgb, hex_color = result
    if rgb is not None:
        r, g, b = [int(c) for c in rgb]
        image_preview_canvas.watermark_rgb = (r, g, b)  # type: ignore[attr-defined]
        image_preview_canvas.watermark_color = hex_color  # type: ignore[attr-defined]
        current_color_swatch.config(bg=f"{hex_color}")
        create_text()


root = tk.Tk()
root.geometry(f"{ROOT_WIDTH}x{ROOT_HEIGHT}")
root.config(bg="#333333", relief="raised")
root.resizable(False, False)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=0)
root.grid_columnconfigure(1, weight=1)
root.option_add("*Font", ("FireCode Nert Font", 16, "bold"))


tree = tk.Frame(
    root,
    relief="sunken",
    background="#000000",
    highlightbackground="#333333",
    highlightthickness=2,
    highlightcolor="#000000",
    width=TREE_WIDTH,
)
tree.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

image_sel_label = tk.Label(tree, text="Image Selection Menu")
image_sel_label.grid(row=0, column=0, sticky="ew")
image_sel_label.configure(anchor="center", bg="#222222", foreground="white")

image_sel_button = tk.Button(
    tree,
    text="Open Image",
    command=image_open,
    bg="#555555",
    foreground="white",
    relief="flat",
    activebackground="#777777",
    activeforeground="white",
    highlightthickness=0,
)
image_sel_button.grid(row=1, column=0, pady=(10, 0))

watermark_textbox_label = tk.Label(tree, text="Watermark Text")
watermark_textbox_label.grid(row=2, column=0, sticky="ew", pady=(10, 0))
watermark_textbox_label.configure(anchor="center", bg="#222222", foreground="white")

watermark_textbox = tk.Entry(tree)
watermark_textbox.grid(row=3, column=0, sticky="ew")
watermark_textbox.configure(
    background="#555555",
    foreground="white",
    relief="flat",
    borderwidth=0,
    highlightthickness=0,
)
watermark_textbox.bind("<KeyRelease>", lambda e: create_text())

watermark_text_size_label = tk.Label(tree, text="Font Size Adjustment")
watermark_text_size_label.grid(row=4, column=0, sticky="ew", pady=(10, 0))
watermark_text_size_label.configure(anchor="center", bg="#222222", foreground="white")

watermark_text_size = tk.Scale(tree)
watermark_text_size.configure(
    orient="horizontal",
    background="#555555",
    foreground="white",
    relief="flat",
    borderwidth=0,
    highlightthickness=0,
    from_=12,
    to=50,
)
watermark_text_size.set(DEFAULT_FONT_SIZE)
watermark_text_size.grid(row=5, column=0, sticky="ew")
watermark_text_size.bind("<Motion>", lambda e: create_text())

current_color_swatch = tk.Label(
    tree,
    bg=("#ffffff"),
    width=4,
    relief="flat",
    bd=2,
)
current_color_swatch.grid(row=6, column=0, pady=(10, 0))
current_color_swatch.bind("<Button-1>", lambda e: color_chooser())


opacity_slider_label = tk.Label(tree, text="Font Opacity Adjustment")
opacity_slider_label.grid(row=7, column=0, sticky="ew", pady=(10, 0))
opacity_slider_label.configure(anchor="center", bg="#222222", foreground="white")

opacity_slider = tk.Scale(tree, from_=0, to=255, orient="horizontal")
opacity_slider.configure(
    orient="horizontal",
    background="#555555",
    foreground="white",
    relief="flat",
    borderwidth=0,
    highlightthickness=0,
    from_=0,
    to=255,
)
opacity_slider.set(255)  # Default fully opaque
opacity_slider.grid(row=8, column=0, sticky="ew")
opacity_slider.bind("<Motion>", lambda e: create_text())  # Live update

save_button = tk.Button(tree, text="Save Image", command=save_image_with_watermark)
save_button.configure(
    anchor="center",
    bg="#555555",
    foreground="white",
    relief="flat",
    activebackground="#32a852",
    activeforeground="white",
    highlightthickness=0,
)
save_button.grid(row=9, column=0, pady=10, sticky="ew")

tree.grid_rowconfigure(10, weight=1)

exit_button = tk.Button(tree, text="Exit Tool", command=root.destroy)
exit_button.grid(row=11, column=0, sticky="s", pady=(10, 0))
exit_button.configure(
    anchor="center",
    bg="#555555",
    foreground="white",
    relief="flat",
    activebackground="#780000",
    activeforeground="white",
    highlightthickness=0,
)

preview_section = tk.Frame(
    root,
    relief="sunken",
    background="#000000",
    highlightbackground="#333333",
    highlightthickness=2,
    highlightcolor="#000000",
    width=PREVIEW_WIDTH,
)
preview_section.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

preview_section.rowconfigure(0, weight=0)
preview_section.rowconfigure(1, weight=1)
preview_section.columnconfigure(0, weight=1)

preview_label = tk.Label(preview_section, text="Preview Window")
preview_label.grid(row=0, column=0, sticky="ew")
preview_label.configure(anchor="center", bg="#222222", foreground="white")

image_preview_canvas = tk.Canvas(
    preview_section, highlightcolor="#000000", highlightthickness=0
)
image_preview_canvas.config(bg="#000000", highlightcolor="#000000")
image_preview_canvas.grid(row=1, column=0, sticky="nsew")

image_preview_canvas.watermark_rgb = (255, 255, 255)  # type: ignore[attr-defined]
image_preview_canvas.watermark_color = "#ffffff"  # type: ignore[attr-defined]

image_preview_canvas.watermark_image_id = None  # type: ignore[attr-defined]
image_preview_canvas.watermark_photo = None  # type: ignore[attr-defined]
image_preview_canvas.wm_x_display = 0
image_preview_canvas.wm_y_display = 0

image_preview_canvas.bind("<Configure>", lambda e: center_image())
image_preview_canvas.bind("<Button-1>", lambda e: click(e))
image_preview_canvas.bind("<B1-Motion>", lambda e: drag_motion(e))
image_preview_canvas.bind("<ButtonRelease-1>", lambda e: stop_drag(e))

print("Available fonts:", sorted(font.families()))
field_status()
root.mainloop()
