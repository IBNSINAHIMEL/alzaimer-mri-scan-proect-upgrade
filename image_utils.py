import os
import hashlib
from cryptography.fernet import Fernet
from PIL import Image
import io
import base64

class ImageProcessor:
    def __init__(self):
        self.upload_folder = 'static/uploads'
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def generate_key(self):
        """Generate encryption key"""
        return Fernet.generate_key()
    
    def encrypt_image(self, image_data, key):
        """Encrypt image data"""
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(image_data)
        return encrypted_data
    
    def decrypt_image(self, encrypted_data, key):
        """Decrypt image data"""
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data
    
    def generate_hash(self, image_data):
        """Generate hash for image"""
        return hashlib.sha256(image_data).hexdigest()
    
    def compress_image(self, image_file, max_size=(400, 400)):
        """Compress image for storage - IMPROVED VERSION"""
        try:
            print("🖼️ Starting image compression...")
            
            # Reset file pointer if it's a file object
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
            
            # Read image data
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                print(f"📊 Original image size: {len(image_data)} bytes")
            else:
                image_data = image_file
                print(f"📊 Original image size: {len(image_data)} bytes")
            
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            print(f"🖼️ Image mode: {image.mode}, Size: {image.size}")
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P', 'LA'):
                image = image.convert('RGB')
                print("🔄 Converted image to RGB")
            
            # Resize if larger than max_size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                print(f"📐 Resized image to: {image.size}")
            
            # Save to bytes with compression
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            compressed_data = img_byte_arr.getvalue()
            
            print(f"📦 Compressed image size: {len(compressed_data)} bytes")
            return compressed_data
            
        except Exception as e:
            print(f"❌ Error compressing image: {e}")
            # Return original data if compression fails
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
            if hasattr(image_file, 'read'):
                original_data = image_file.read()
                print(f"🔄 Using original data: {len(original_data)} bytes")
                return original_data
            print(f"🔄 Using original data: {len(image_file)} bytes")
            return image_file
    
    def save_image_file(self, image_data, filename):
        """Save image to file system - IMPROVED VERSION"""
        try:
            if not image_data:
                print("❌ No image data to save")
                return None
            
            clean_filename = "".join(c for c in filename if c.isalnum()or c in ('-','-','-'))
            filepath = os.path.join(self.upload_folder, filename)
            print(f"💾 Saving image to: {filepath}")
            print(f"📁 Data size to save: {len(image_data)} bytes")
            
            # Ensure upload directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # Verify the file was saved
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"✅ Image saved successfully: {filepath} ({file_size} bytes)")
                return clean_filename
            else:
                print("❌ File was not created")
                return None
                
        except Exception as e:
            print(f"❌ Error saving image file: {e}")
            return None
    
    def get_image_url(self, prediction_id):
        """Get image URL for display"""
        # Look for any file that matches the pattern
        upload_dir = 'static/uploads'
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if f"prediction_{prediction_id}" in filename:
                    return f"/static/uploads/{filename}"
        return None

# Initialize image processor
image_processor = ImageProcessor()

# Password hashing function
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()
