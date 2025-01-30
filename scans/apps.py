from django.apps import AppConfig
import tensorflow as tf
from tensorflow import keras
load_model = keras.models.load_model

print(f"TensorFlow version: {tf.__version__}")

class ScansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scans'
    model = None  # Placeholder for the model
