from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os
from .apps import ScansConfig

def analyze_image(image_path):
    # Ensure the model is loaded
    if ScansConfig.model is None:
        print("Model not loaded. Loading model now...")
        model_path = os.path.join('D:\\', 'FYP_Final', 'kidneymodel', 'my_model.h5')
        if os.path.exists(model_path):
            ScansConfig.model = load_model(model_path, compile=False)
            print("Model loaded successfully!")
            # Recompile the model with proper loss and optimizer
            ScansConfig.model.compile(optimizer=Adam(), loss=BinaryCrossentropy(), metrics=['accuracy'])
        else:
            raise FileNotFoundError(f"Model file not found at {model_path}")
    
    model = ScansConfig.model

    # Resize image to 28x28 (or the expected size for your model)
    img = load_img(image_path, target_size=(28, 28))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize the image

    # Run prediction
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)

    return {
        'predictions': predictions.tolist(),
        'predicted_class': int(predicted_class[0])
    }
