from django.apps import AppConfig
from tensorflow.keras.models import load_model

class ScansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scans'
    model = None  # Placeholder for the model

    def ready(self):
        # Load the model when the app is ready
        if not ScansConfig.model:
            ScansConfig.model = load_model('C:/Users/pc/Desktop/kidneymodel/my_model.h5')
            print("Model loaded successfully!")
