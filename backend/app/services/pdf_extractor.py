from typing import List, Dict, Any
from pathlib import Path
import fitz  # PyMuPDF
from app.core.logging import logger
from app.utils.text_cleaning import clean_extracted_text

class PDFExtractor:
    @staticmethod
    def extract_document(pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF page by page preserving:
        - Exact 1-based page numbers
        - Text content
        - Title / section candidates
        - Page dimensions
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
        pages_data = []
        try:
            doc = fitz.open(str(path))
            total_pages = len(doc)
            logger.info(f"Extracting PDF with PyMuPDF: {path.name} ({total_pages} pages)")
            
            for page_idx in range(total_pages):
                page = doc[page_idx]
                raw_text = page.get_text("text")
                cleaned = clean_extracted_text(raw_text)
                
                # Check for headings or bold blocks
                blocks = page.get_text("blocks")
                first_heading = None
                for b in blocks:
                    block_text = b[4].strip()
                    if block_text and len(block_text) < 120 and ("\n" not in block_text or len(block_text.split("\n")) <= 2):
                        first_heading = block_text
                        break

                pages_data.append({
                    "page_number": page_idx + 1,  # 1-based indexing for citations
                    "raw_text": raw_text,
                    "cleaned_text": cleaned,
                    "first_heading": first_heading,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "char_count": len(cleaned)
                })
            
            doc.close()
            return pages_data
        except Exception as e:
            logger.error(f"PyMuPDF failed to process {pdf_path}: {e}")
            raise e
