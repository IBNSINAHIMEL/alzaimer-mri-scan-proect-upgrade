from PIL import Image
import numpy as np
import io

def preprocess_mri(image_file, size=(176, 176)):
    """Resize and normalize MRI image for model prediction"""
    try:
        # Read image file
        if hasattr(image_file, 'read'):
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
        else:
            image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image
        image = image.resize(size)
        
        # Convert to numpy array and normalize
        img_array = np.array(image) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
        
    except Exception as e:
        print(f"Error preprocessing MRI image: {e}")
        raise e