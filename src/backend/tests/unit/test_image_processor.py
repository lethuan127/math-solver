import io
from unittest.mock import patch

from PIL import Image

from app.services.image_processor import ImageProcessor


class TestImageProcessor:
    def setup_method(self):
        self.processor = ImageProcessor()

    @patch("pytesseract.image_to_string")
    def test_extract_text_from_image(self, mock_tesseract):
        mock_tesseract.return_value = "2 + 2 = ?"

        # Create test image
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        result = self.processor.extract_text(img_bytes.getvalue())

        assert result == "2 + 2 = ?"
        mock_tesseract.assert_called_once()

    def test_validate_image_format(self):
        # Valid image formats
        assert self.processor.is_valid_image_format("test.jpg")
        assert self.processor.is_valid_image_format("test.png")
        assert self.processor.is_valid_image_format("test.jpeg")

        # Invalid formats
        assert not self.processor.is_valid_image_format("test.txt")
        assert not self.processor.is_valid_image_format("test.pdf")
