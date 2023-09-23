# Image Classifier with ViT and DETR

This repository provides a graphical application to classify images using the `Vision Transformer (ViT)` model and object detection using the `DEtection TRansformer (DETR)` model. The user can select a folder containing images to be processed, and the application will then display these images with associated class predictions and detected objects.

## Features:

- Multi-threaded image processing.
- Progress bar and process status updates.
- Option to trust AI and apply all suggestions.
- Thumbnails of images on the canvas.
- Ability to stop the ongoing processing.
- Dark mode.

## Setup

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
git clone <repository_url>
cd <repository_directory>
```

2. Install the required packages:

```
pip install transformers torch pillow iptcinfo3
```

## Usage:

Run the main script:

```
python app.py
```

Once the GUI launches:

1. Click on "Process Folder" to select a directory with images.
2. Choose desired options.
3. The application will display each image with its classification and detected objects.
4. You can click on each image to view it in full size.

## Contribution:

Pull requests are welcome. For significant changes, please open an issue first to discuss what you'd like to change.

## License:

[MIT](https://choosealicense.com/licenses/mit/)
