import pytesseract
import cv2
from PIL import Image

# Set Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the image
img1 = cv2.imread("image.png")
if img1 is None:
    print("Error: Could not load image.png. Check the file path or name.")
    exit()
cv2.imshow("Original Image", img1)
cv2.waitKey(0)

img2 = Image.open("image.png")
img2.show()

# Preprocessing the image
gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
# gray = cv2.GaussianBlur(gray, (1,1), 0)
gray = cv2.bilateralFilter(gray, 9, 75, 75)
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

cv2.imshow("Processed Image", thresh)
cv2.waitKey(0)
cv2.imwrite("processed_thresh.png", thresh)

# Extract text from image
try:
    text = pytesseract.image_to_string(thresh, config='--psm 6 --oem 1')
    print("Extracted Text : ")
    print(text)
except pytesseract.TesseractError as e:
    print("Tesseract Error:", e)

