"""
Chart Type Classifier.
Classifies chart images into categories (bar, line, pie, radar, scatter, etc.)
This helps in selecting the right extraction strategy or prompt for the VLM.
"""

import torch
try:
    from torchvision import models, transforms
    from PIL import Image
except ImportError:
    print("Please install torchvision and Pillow.")

class ChartClassifier:
    def __init__(self, model_path: str = None, device: str = "cpu"):
        """
        Initialize the Chart Classifier using EfficientNet-B0.
        :param model_path: Path to the fine-tuned model weights (if available).
        """
        self.device = device
        self.classes = ['bar', 'line', 'pie', 'scatter', 'radar', 'table', 'other']
        
        try:
            # Use a lightweight EfficientNet-B0
            self.model = models.efficientnet_b0(pretrained=False)
            # Modify final layer for our classes
            num_ftrs = self.model.classifier[1].in_features
            self.model.classifier[1] = torch.nn.Linear(num_ftrs, len(self.classes))
            
            if model_path:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                
            self.model.to(self.device)
            self.model.eval()
            
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
            ])
            self.initialized = True
        except Exception as e:
            print(f"Failed to initialize ChartClassifier: {e}")
            self.initialized = False

    def classify(self, image_path: str) -> str:
        """
        Predict the chart type of the given image.
        """
        if not self.initialized:
            return "unknown"
            
        try:
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                _, predicted = torch.max(outputs, 1)
                
            return self.classes[predicted.item()]
        except Exception as e:
            print(f"Error classifying {image_path}: {e}")
            return "error"

if __name__ == "__main__":
    classifier = ChartClassifier()
    print("ChartClassifier module is ready.")
