import keyboard
import threading
import pystray
from PIL import Image, ImageDraw
import pytesseract
import cv2
import numpy as np
from PIL import ImageGrab
import pyperclip
import win32gui
import win32con
import sys
import os

class TextExtractor:
    def __init__(self):
        self.running = True
        self.hotkey = 'ctrl+shift+z'  # Default hotkey
        
    def create_icon(self):
        # Create a simple icon
        icon_size = 64
        image = Image.new('RGB', (icon_size, icon_size), color='white')
        dc = ImageDraw.Draw(image)
        dc.text((10, 10), "OCR", fill='black')
        
        return image
        
    def setup_tray(self):
        icon_image = self.create_icon()
        menu = (
            pystray.MenuItem("Extract Text (Ctrl+Shift+T)", self.start_extraction),
            pystray.MenuItem("Exit", self.quit_application)
        )
        self.icon = pystray.Icon("TextExtractor", icon_image, "Text Extractor", menu)
        
    def quit_application(self, icon, item):
        self.running = False
        self.icon.stop()
        os._exit(0)
        
    def start_extraction(self, icon=None, item=None):
        region = self.capture_screen_region()
        if region is None:
            return
            
        processed = self.process_image(region)
        self.extract_text(processed)
        
    # Your existing methods with slight modifications
    def capture_screen_region(self):
        # ... existing capture_screen_region code ...
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        
        cv2.namedWindow('Select Region', cv2.WINDOW_NORMAL)
        hwnd = win32gui.FindWindow(None, 'Select Region')
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        
        global img, img_copy, drawing, ix, iy
        img = screen.copy()
        img_copy = img.copy()
        drawing = False
        ix, iy = -1, -1
        
        params = {'selection': None}
        cv2.setMouseCallback('Select Region', self.on_mouse, params)
        
        while params['selection'] is None:
            cv2.imshow('Select Region', img_copy)
            if cv2.waitKey(1) & 0xFF == 27:
                cv2.destroyAllWindows()
                return None
                
        x, y, w, h = params['selection']
        return screen[y:y+h, x:x+w]

    def on_mouse(self, event, x, y, flags, params):
        global ix, iy, drawing, img, img_copy
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_copy = img.copy()
                cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            params['selection'] = (min(ix, x), min(iy, y), abs(x - ix), abs(y - iy))
            cv2.destroyAllWindows()

    def process_image(self, img):
        # ... existing process_image code ...
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        gray = cv2.medianBlur(gray, 3)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        return thresh

    def extract_text(self, processed):
        try:
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(processed, config=custom_config)
            text = text.strip()
            
            if text:
                pyperclip.copy(text)
                # Optional: Show a notification
                self.icon.notify("Text copied to clipboard!")
            
        except pytesseract.TesseractError as e:
            self.icon.notify("Error: Could not extract text")

    def run(self):
        # Set up Tesseract path
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Register the hotkey
        keyboard.add_hotkey(self.hotkey, self.start_extraction)
        
        # Setup system tray
        self.setup_tray()
        
        # Run the system tray icon
        self.icon.run()

if __name__ == "__main__":
    extractor = TextExtractor()
    extractor.run()