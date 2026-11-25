from app.core.logging import logger

class OCRService:
    @staticmethod
    def extract_scanned_page(pdf_path: str, page_number: int) -> str:
        """
        Attempts OCR if page contains negligible text.
        Gracefully handles environments without tesseract-ocr binary installed.
        """
        try:
            import pytesseract
            from PIL import Image
            import fitz
            
            doc = fitz.open(pdf_path)
            page = doc[page_number - 1]
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
            doc.close()
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR not available or failed for page {page_number}: {e}")
            return ""
