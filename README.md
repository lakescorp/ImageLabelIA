# 📸 Image Classifier for Photographers 📸

This repository is designed for photographers 📷! It provides a graphical application to classify and detect objects in images. Use the power of the `Vision Transformer (ViT)` for classification and the `DEtection TRansformer (DETR)` for object detection. Easily select a folder with your images and let the application highlight the magic within them.

## ✨ Features:

- 🚀 Multi-threaded image processing.
- 🔄 Progress bar and process status updates.
- 🤖 Option to trust AI and apply all suggestions.
- 🖼 Thumbnails of images on the canvas.
- 🛑 Ability to stop the ongoing processing.
- 🌙 Dark mode.

## 🛠 Setup

### Dependencies:

- [Transformers](https://github.com/huggingface/transformers)
- [Torch](https://pytorch.org/)
- [Pillow (PIL)](https://python-pillow.org/)
- [tkinter](https://docs.python.org/3/library/tkinter.html)
- [IPTCInfo3](https://pypi.org/project/IPTCInfo3/)
- [Exiv2](https://www.exiv2.org/)

### Installation:

1. Clone the repository:

```
git clone https://github.com/lakescorp/ImageLabelIA.git
cd ImageLabelIA
```

2. Install the required packages:

```
pip install transformers torch pillow iptcinfo3
```

## 🚀 Usage:

Run the main script:

```
python app.py
```

Once the GUI launches:

1. 📂 Click on "Process Folder" to select a directory with images.
2. ⚙️ Choose desired options.
3. 👁‍🗨 The application will display each image with its classification and detected objects.
4. 🔍 You can click on each image to view it in full size.

## 🤝 Contribution:

Pull requests are welcome. For significant changes, please open an issue first to discuss what you'd like to change.

## 📜 License:

[MIT](https://choosealicense.com/licenses/mit/)
