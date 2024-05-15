from PIL import Image, ExifTags
from iptcinfo3 import IPTCInfo

class ImageUtils:
    @staticmethod
    def correct_image_orientation(image) -> Image:
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
    def load_image(image_path) -> Image:
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
        image = ImageUtils.correct_image_orientation(image)
        image = image.convert("RGB")

        return image

    @staticmethod
    def generate_thumbnail(image_path, base_size=75):
        """
        Generate a thumbnail for the given image while maintaining aspect ratio.
        Also corrects the orientation based on the image's EXIF data.
        """
        img = ImageUtils.load_image(image_path)

        # Resize while maintaining aspect ratio
        aspect_ratio = img.width / img.height
        if img.width > img.height:
            new_width = base_size
            new_height = int(base_size / aspect_ratio)
        else:
            new_width = int(base_size * aspect_ratio)
            new_height = base_size
        
        img = img.resize((new_width, new_height))
        return img

    @staticmethod
    def get_iptc_keywords(image_path):
        """Extract keywords from the IPTC metadata of an image."""
        # Create an IPTCInfo object
        info = IPTCInfo(image_path)

        # Check for errors
        if info.error:
            print(f"ERROR: {info.error}")
            return []        

        # Return the list of keywords, if they exist
        return info['keywords']