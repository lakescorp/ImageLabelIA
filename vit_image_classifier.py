from transformers import ViTImageProcessor, ViTForImageClassification
import torch.nn.functional as F
from PIL import Image, ExifTags
import torch

class ViTImageClassifier:
    def __init__(self):
        # Define the device (use CUDA if available, otherwise use CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the pretrained Vision Transformer (ViT) image processor and model
        self.processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
        self.model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224').to(self.device)

    def _correct_image_orientation(self, image):
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

    def classify(self, image_path):
        """
        Classify an image using the pretrained Vision Transformer (ViT) model.

        Args:
        - image_path (str): Path to the image to be classified.

        Returns:
        - List of predicted classes for the image.
        """

        # Open the image using PIL
        image = Image.open(image_path)
        
        # Correct its orientation and ensure it's in RGB format
        image = self._correct_image_orientation(image)
        image = image.convert("RGB")

        # Preprocess the image and convert to tensor format suitable for the model
        inputs = self.processor(images=[image], return_tensors="pt")
        inputs = {key: val.to(self.device) for key, val in inputs.items()}

        # Predict the class of the image using the Vision Transformer (ViT)
        outputs = self.model(**inputs)
        logits = outputs.logits
        
        # Convert logits to probabilities
        probabilities = F.softmax(logits, dim=1)

        # Extract classes with high prediction probability (e.g., >= 0.9)
        predicted_classes = []
        for idx, probability in enumerate(probabilities):
            if probability[0] >= 0.9:
                predicted_classes.append(self.model.config.id2label[idx])

        # Return the list of predicted classes
        return predicted_classes
