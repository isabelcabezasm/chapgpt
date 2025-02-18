import io
from PIL import ImageFile
import numpy as np

from keras.preprocessing import image as keras_image
from keras.models import Model
from keras.applications.resnet50 import ResNet50, preprocess_input



def load_and_preprocess_image(image: ImageFile, target_size=(224, 224)) -> np.ndarray:
    """
    Load an image from the specified path and preprocess it for ResNet50.

    Parameters:
    - image (PIL.Image): Input image in format PIL.ImageFile.
    - target_size (tuple): The target size to resize the image for ResNet50 input.

    Returns:
    - img (PIL.Image.Image): The loaded image (preprocesed).
    - img_data (np.ndarray): The preprocessed image data suitable for ResNet50.
    """
    
    # Resize the image to the target size
    image = image.resize(target_size)

    # Convert the image to a numpy array
    img_data = keras_image.img_to_array(image)
    
    # Expand dimensions to match the input shape for ResNet50
    img_data = np.expand_dims(img_data, axis=0)
    
    # Preprocess the image data for ResNet50
    img_data = preprocess_input(img_data)
    
    return img_data


def extract_ResNet_features(img_data: np.ndarray) -> np.ndarray:
    """
    Extract features from an image using the pre-trained ResNet50 model.

    Parameters:
    - img_data (np.ndarray): The preprocessed image data.

    Returns:
    - features (np.ndarray): The extracted features.
    """
    # Load ResNet50 model with weights trained on ImageNet 
    base_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
    # Create a new model without the without the top layer
    model = Model(inputs=base_model.input, outputs=base_model.output)

    # Extract features from the image data
    features = model.predict(img_data)    
    # Flatten the features to a 1D array
    return features.flatten()


def get_embeddings(img: io.BytesIO) -> list[list[float]]:
    # Load and preprocess an image (replace with your image path)

    # Load the image with the specified target size
    img = keras_image.load_img(img)
    img_data_db = load_and_preprocess_image(img)
    features_bd = extract_ResNet_features(img_data_db)
    return features_bd.tolist()
