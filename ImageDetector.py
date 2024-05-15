# Required imports
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from ImageUtils import ImageUtils

class ObjectDetector:
    def __init__(self):
        # Define the device (use CUDA if available, otherwise use CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load pretrained DETR image processor and model from Huggingface's transformers library
        self.processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50").to(self.device)

    def detect(self, image_path):
        """
        Detect objects in an image using the pretrained DETR model.

        Args:
        - image_path: Path to the image file.

        Returns:
        - List of detected objects in the image.
        """

        # Open the image using PIL and correct its orientation if needed
        image = ImageUtils.load_image(image_path)

        # Process the image and convert to tensors
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        # Run the model to detect objects
        outputs = self.model(**inputs)

        # Convert the model's outputs (bounding boxes and class logits) to the COCO API format
        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
        results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

        # Use a set to store unique detected objects
        detected_objects_set = set()
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            detected_objects_set.add(self.model.config.id2label[label.item()])

        # Return the list of detected objects
        return list(detected_objects_set)