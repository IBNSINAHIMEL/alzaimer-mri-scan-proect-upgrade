import tensorflow as tf
import numpy as np
from PIL import Image
import os

class AlzheimerModel:
    def __init__(self):
        """Initialize with empty model and fixed class order"""
        self.model = None
        # ✅ Correct order based on dataset folder naming
        self.classes = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]

    def find_model_file(self):
        """Find model file automatically inside /models directory"""
        model_dir = os.path.join(os.getcwd(), "models")
        possible_files = [
            "Alzheimer_CNN_BestModel.h5",
            "Alzheimer_CNN_Final.h5",
        ]

        for file in possible_files:
            path = os.path.join(model_dir, file)
            if os.path.exists(path):
                print(f"✅ Found model file: {path}")
                return path

        print(f"❌ No model file found in {model_dir}")
        raise FileNotFoundError("No .h5 model file found! Please add it inside the 'models' folder.")

    def load_model(self, model_path=None):
        """Load the trained CNN model"""
        if model_path is None:
            model_path = self.find_model_file()

        try:
            print(f"🔄 Loading model from: {model_path}")
            self.model = tf.keras.models.load_model(model_path, compile=False)
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise e

    def preprocess_image(self, image_file):
        """Resize & normalize MRI image to match training size (128x128x3)"""
        try:
            img = Image.open(image_file).convert("RGB")
            img = img.resize((128, 128))  # ✅ matches your training image size
            img_array = np.array(img, dtype=np.float32) / 255.0  # normalize to [0, 1]
            img_array = np.expand_dims(img_array, axis=0)  # shape: (1, 128, 128, 3)
            return img_array
        except Exception as e:
            print(f"❌ Error during image preprocessing: {e}")
            raise e

    def predict(self, image_file):
        """Run prediction and return class + confidence"""
        if self.model is None:
            print("⚠️ Model not loaded yet — loading now...")
            self.load_model()

        processed_img = self.preprocess_image(image_file)

        try:
            prediction = self.model.predict(processed_img, verbose=0)
            predicted_index = np.argmax(prediction)
            predicted_class = self.classes[predicted_index]
            confidence = float(np.max(prediction)) * 100  # percentage

            print(f"✅ Prediction: {predicted_class} ({confidence:.2f}%)")

            return {
                "prediction": predicted_class,
                "confidence": round(confidence, 2),
                "all_predictions": {
                    label: round(float(prob) * 100, 2)
                    for label, prob in zip(self.classes, prediction[0])
                },
            }

        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            raise e


# 🌟 Create global instance for reuse
model_predictor = AlzheimerModel()

# Try loading at startup (optional but helpful)
try:
    model_predictor.load_model()
except Exception as e:
    print(f"⚠️ Model not loaded on startup: {e}")
    print("🔄 It will load automatically on the first prediction request.")
