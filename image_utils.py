from PIL import Image
import numpy as np

def preprocess_mri(image_file, size=(128, 128)):
    """Resize and normalize MRI image"""
    img = Image.open(image_file).convert('RGB')
    img = img.resize(size)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array
