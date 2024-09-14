from tensorflow.keras.preprocessing import image
import numpy as np
from .apps import ScansConfig

def analyze_image(image_path):
    model = ScansConfig.model
    
    # Resize image to 28x28 (the size expected by your model)
    img = image.load_img(image_path, target_size=(28, 28))  
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize if required by your model

    # Run prediction
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)

    return {
        'predictions': predictions.tolist(),  # Convert to list for JSON compatibility
        'predicted_class': predicted_class[0]  # Return the predicted class
    }
