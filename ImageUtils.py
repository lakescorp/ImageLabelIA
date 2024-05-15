from PIL import Image, ExifTags
from iptcinfo3 import IPTCInfo

class ImageUtils:

    @staticmethod
    def generate_thumbnail(image_path, base_size=75):
        """
        Generate a thumbnail for the given image while maintaining aspect ratio.
        Also corrects the orientation based on the image's EXIF data.
        """
        img = Image.open(image_path)
        
        # Correct orientation based on EXIF data
        exif = img._getexif()
        img = img.convert("RGB")
        
        # Attempt to get the orientation tag from the image's EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            if exif is not None and orientation in exif:
                if exif[orientation] == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 3:
                    img = img.rotate(180)
                elif exif[orientation] == 4:
                    img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 6:
                    img = img.rotate(-90, expand=True)
                elif exif[orientation] == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # Cases where the image doesn't have EXIF data
            print(f"No EXIF data for {image_path}")
            pass

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