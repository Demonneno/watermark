# Image Watermark Tool

A lightweight, cross-platform desktop application for adding customizable watermarks to images. Built with **Tkinter** and **Pillow**, it provides a real-time preview with draggable text and logo overlays. An experimental class-based version has been created, but doesn't implement all of the procedural version's features; notably logo implementation. 

## Features

- Load images (JPG, PNG, BMP).
- Live text watermark:
  - Type any text.
  - Adjust font size with slider.
  - Change color via color picker.
  - Adjust opacity (transparency) with slider.
- Logo overlay:
  - Upload a PNG logo (supports transparency).
  - Resize with dedicated slider.
  - Drag to position.
- Draggable overlays:
  - Click and drag text or logo freely.
  - Overlays stay within image bounds.
- Accurate save:
  - Exports full-resolution image with both text and logo baked in.
  - Supports PNG and JPEG.

## Requirements

- Python 3.8+
- Pillow:
  ```bash
  pip install pillow
  ```

## Usage

1. Run the app:
   ```bash
   python app.py
   ```

2. Click **Open Image** and select a photo.

3. Text Watermark:
   - Type in the "Watermark Text" field.
   - Adjust font size, color, and opacity.
   - Drag the text overlay to position it.

4. Logo Watermark:
   - Click **Upload Logo** and select a PNG.
   - Adjust the logo size slider.
   - Drag the logo to position it.

5. Click **Save Image** to export the watermarked full-resolution photo.

## Notes

- Font rendering uses a cross-platform fallback chain (Arial on Windows, Helvetica on macOS, common sans-serif on Linux).
- Best results with transparent PNG logos.
- Both text and logo can be used simultaneously.

## Features To Be Added

While I don't intend on adding features to this immediately, it will be revisited to extend its use as a means of tinkering (how outplayed is that pun?) to keep the interim (okay, okay) juices flowing.

- Undo/Redo options
- Logo overlay colors
- Logo overlay opacity
- Multiple text / logo add-ins

## License

MIT License — feel free to use, modify, and share.

Enjoy watermarking your images! 🚀
"""
