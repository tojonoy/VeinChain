import torch
import torch.nn as nn
import numpy as np
import torchvision.transforms as transforms
from torchvision.models import resnet50
from torchvision.models import ResNet50_Weights
from PIL import Image

# Define device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize the image to match the ResNet input size
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),  # Normalize RGB images
])

# Load pre-trained ResNet-50
model = resnet50(weights=ResNet50_Weights.DEFAULT)

# Replace the fully connected layer to reduce dimensions to 128
model.fc = nn.Sequential(
    nn.Linear(2048, 128),  # Reduce to 128 dimensions
    nn.ReLU(),             # Add non-linearity
    nn.BatchNorm1d(128)    # Normalize feature vector
)

model = model.to(device)
model.eval()

# Function to extract feature vector from a PIL Image object
def extract_feature(image):
    if isinstance(image, np.ndarray):
        image = Image.fromarray((image * 255).astype(np.uint8))  # Convert NumPy array back to PIL
    image = image.convert("RGB")  # Ensure it's in RGB mode
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        feature = model(image).cpu().numpy().flatten()
    
    return feature
