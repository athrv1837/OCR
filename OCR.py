import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io

# Set Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set page config
st.set_page_config(page_title="Text Extractor", layout="wide")

def process_image(image):
    # Convert PIL Image to OpenCV format (NumPy array)
    img = np.array(image)
    
    # Check if the image is valid
    if img is None or img.size == 0:
        raise ValueError("Invalid image: Could not process the input image.")
    
    # Check the number of dimensions
    if len(img.shape) == 2:  # Grayscale image (height, width)
        gray = img
    elif len(img.shape) == 3:  # Color image (height, width, channels)
        if img.shape[2] == 4:  # RGBA image
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        raise ValueError("Unsupported image format: Image has unexpected dimensions.")
    
    # Apply bilateral filter
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    return thresh

def main():
    st.title("Text Extractor")
    st.write("Upload an image to extract text from it")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
    
    col1, col2 = st.columns(2)
    
    if uploaded_file is not None:
        # Read image
        try:
            image = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
            return
        
        # Display original image
        with col1:
            st.subheader("Original Image")
            st.image(image, use_container_width=True)
        
        # Process image button
        if st.button("Extract Text"):
            with st.spinner("Processing image..."):
                try:
                    # Process image
                    processed_img = process_image(image)
                    
                    # Convert processed image to PIL format for display
                    processed_img_pil = Image.fromarray(processed_img)
                    
                    # Display processed image
                    with col2:
                        st.subheader("Processed Image")
                        st.image(processed_img_pil, use_container_width=True)
                    
                    # Extract text
                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(processed_img, config=custom_config)
                    
                    # Display results
                    st.subheader("Extracted Text:")
                    st.text_area("", text, height=200)
                    
                    # Download button for extracted text
                    if text:
                        st.download_button(
                            label="Download text",
                            data=text,
                            file_name="extracted_text.txt",
                            mime="text/plain"
                        )
                except (pytesseract.TesseractError, ValueError) as e:
                    st.error(f"Error during processing or text extraction: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()