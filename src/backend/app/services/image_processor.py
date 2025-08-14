import io
import logging

import pytesseract
from PIL import Image


class ImageProcessor:
    def __init__(self):
        # Configure tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass

    async def extract_text(self, image_data: bytes) -> str:
        """
        Extract text from image using OCR
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Preprocess image for better OCR
            image = self._preprocess_image(image)

            # Extract text using tesseract
            extracted_text = pytesseract.image_to_string(image, config="--psm 6")

            return extracted_text.strip()

        except Exception as e:
            logging.error(f"Error extracting text from image: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}") from e

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        """
        # Convert to grayscale
        if image.mode != "L":
            image = image.convert("L")

        # Resize if too small
        width, height = image.size
        if width < 300 or height < 300:
            scale_factor = max(300 / width, 300 / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return image
