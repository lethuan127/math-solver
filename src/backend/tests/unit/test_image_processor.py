import io
from unittest.mock import patch

import pytest
from PIL import Image

from app.services.image_processor import ImageProcessor


class TestImageProcessor:
    def setup_method(self):
        self.processor = ImageProcessor()

    @patch("pytesseract.image_to_string")
    @pytest.mark.asyncio
    async def test_extract_text_from_image(self, mock_tesseract):
        mock_tesseract.return_value = "2 + 2 = ?"

        # Create test image
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        result = await self.processor.extract_text(img_bytes.getvalue())

        assert result == "2 + 2 = ?"
        mock_tesseract.assert_called_once()

    def test_preprocess_image(self):
        # Test image preprocessing
        img = Image.new("RGB", (50, 50), color="white")
        processed = self.processor._preprocess_image(img)
        
        # Should be converted to grayscale and resized
        assert processed.mode == "L"
        assert processed.size[0] >= 300 or processed.size[1] >= 300
