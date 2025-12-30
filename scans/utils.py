from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os
from .apps import ScansConfig

def analyze_image(image_path, scan_type='CKD'):
    """
    Analyze medical scan image based on scan type.
    
    Args:
        image_path: Path to the image file
        scan_type: Type of scan (CKD, XRAY, MRI, etc.)
    
    Returns:
        Dictionary with prediction results
    """
    # For now, we use the CKD model for all scan types
    # In the future, you can load different models based on scan_type
    model_paths = {
        'CKD': os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop', 'kidneymodel', 'my_model.h5'),
        # Add more model paths for different scan types as they become available
        # 'XRAY': 'path/to/xray_model.h5',
        # 'MRI': 'path/to/mri_model.h5',
    }
    
    # Get model path based on scan type, default to CKD
    model_path = model_paths.get(scan_type, model_paths['CKD'])
    
    # Ensure the model is loaded
    if ScansConfig.model is None:
        print(f"Model not loaded. Loading {scan_type} model now...")
        if os.path.exists(model_path):
            ScansConfig.model = load_model(model_path, compile=False)
            print(f"{scan_type} model loaded successfully!")
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
    predictions = model.predict(img_array, verbose=0)
    predicted_class = np.argmax(predictions, axis=1)

    return {
        'predictions': predictions.tolist(),
        'predicted_class': int(predicted_class[0]),
        'scan_type': scan_type
    }
