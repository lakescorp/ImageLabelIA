from transformers import ViTImageProcessor, ViTForImageClassification
import torch.nn.functional as F
import torch

from ImageUtils import ImageUtils

class ImageClassifier:
    def __init__(self):
        # Define the device (use CUDA if available, otherwise use CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load the pretrained Vision Transformer (ViT) image processor and model
        self.processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
        self.model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224').to(self.device)

    def classify(self, image_path):
        """
        Classify an image using the pretrained Vision Transformer (ViT) model.

        Args:
        - image_path (str): Path to the image to be classified.

        Returns:
        - List of predicted classes for the image.
        """

        image = ImageUtils.load_image(image_path)

        # Preprocess the image and convert to tensor format suitable for the model
        inputs = self.processor(images=[image], return_tensors="pt")
        inputs = {key: val.to(self.device) for key, val in inputs.items()}

        # Predict the class of the image using the Vision Transformer (ViT)
        outputs = self.model(**inputs)
        logits = outputs.logits
        
        # Convert logits to probabilities
        probabilities = F.softmax(logits, dim=1)

        # Get the predicted class index
        predicted_class_idx = torch.argmax(probabilities, dim=1).item()

        # Return the label of the predicted class
        classes_detected = []
        if self.model.config.id2label[predicted_class_idx]:
            classes_detected= self.model.config.id2label[predicted_class_idx].split(", ")
        return classes_detected
