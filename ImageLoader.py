from PIL import Image, ExifTags

class ImageLoader:
    @staticmethod
    def correct_image_orientation(image):
        """Corrects the orientation of an image using its Exif data."""
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())
            if exif[orientation] == 2:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            elif exif[orientation] == 3:
                image = image.rotate(180)
            elif exif[orientation] == 4:
                image = image.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            elif exif[orientation] == 5:
                image = image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif exif[orientation] == 6:
                image = image.rotate(-90, expand=True)
            elif exif[orientation] == 7:
                image = image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # Cases: image doesn't have getexif method or doesn't have Exif data.
            pass
        return image

    @staticmethod
    def load_image(image_path):
        """Load an image from the specified file path
            and process it.

        Args:
        - image_path (str): The path to the image file.

        Returns:
        - image (PIL.Image): The loaded image in RGB format with orientation
            corrected.
        """
        # Open the image using PIL
        image = Image.open(image_path)
        
        # Correct its orientation and ensure it's in RGB format
        image = ImageLoader.correct_image_orientation(image)
        image = image.convert("RGB")

        return image