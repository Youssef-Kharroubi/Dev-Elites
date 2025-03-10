#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
import numpy as np
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt



# In[2]:


def load_image_opencv(image_path):
    
    # Load image using OpenCV (BGR format)
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError("Error: Image not found or cannot be loaded.")
    
    return image


# In[3]:


def convert_opencv_to_pil(image_cv):
   
    # Convert from BGR (OpenCV) to RGB (PIL)
    image_pil = Image.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))
    return image_pil


# In[4]:


def convert_to_grayscale(image):
    
    if isinstance(image, np.ndarray):  # OpenCV (BGR format)
        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif isinstance(image, Image.Image):  # PIL format
        grayscale_image = image.convert("L")
    else:
        raise ValueError("Unsupported image type.")
    
    return grayscale_image


# In[5]:


def apply_adaptive_thresholding(image, block_size=3, constant=2, max_value=255):
    
    if not isinstance(image, np.ndarray):
        raise ValueError("Input image should be a NumPy array (grayscale image).")
    
    # Apply adaptive thresholding
    thresholded_image = cv2.adaptiveThreshold(
        image,
        max_value,  # Maximum value for white pixels
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Adaptive method
        cv2.THRESH_BINARY,  # Binary thresholding
        block_size,  # Size of the local neighborhood
        constant  # Constant to subtract from the computed threshold
    )

    return thresholded_image


# In[6]:


def denoise_image(image):
    
    if isinstance(image, np.ndarray):  # OpenCV (BGR format)
        denoised_image = cv2.fastNlMeansDenoising(image, None, 30, 7, 21)
    elif isinstance(image, Image.Image):  # PIL format
        # Convert to NumPy array, apply denoising, then convert back
        image_cv = np.array(image)
        denoised_image = cv2.fastNlMeansDenoising(image_cv, None, 30, 7, 21)
        denoised_image = Image.fromarray(denoised_image)
    else:
        raise ValueError("Unsupported image type.")
    
    return denoised_image


# In[7]:


def enhance_contrast(image, alpha=1.5, beta=0, factor=1.5):

    if isinstance(image, np.ndarray):  # OpenCV format (NumPy array)
        # Enhance contrast using OpenCV's convertScaleAbs
        enhanced_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    elif isinstance(image, Image.Image):  # PIL format
        # Enhance contrast using PIL ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(factor)
    else:
        raise ValueError("Unsupported image type. The image must be either a NumPy array (OpenCV) or a PIL Image.")

    return enhanced_image


# In[8]:


def thick_font(image):
    # Invert the image, apply dilation, and then invert it back
    image = cv2.bitwise_not(image)
    kernel = np.ones((2, 2), np.uint8)  # Kernel of size 2x2
    image = cv2.dilate(image, kernel, iterations=1)  # Dilation to thicken the text
    image = cv2.bitwise_not(image)  # Invert back to original colors
    return image


# In[9]:


def sharpen_image(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)


# In[10]:


def detect_skew_angle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Finding contours to detect the skew angle
    coords = np.column_stack(np.where(thresh > 0))
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    
    # Correcting the angle so that it's between -90 and 90 degrees
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    return angle


# In[11]:


def correct_skew(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    
    # Get the rotation matrix for the given angle
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Rotate the image
    rotated = cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated


# In[ ]:




