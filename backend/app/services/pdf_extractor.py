from typing import List, Dict, Any
from pathlib import Path
import os
import fitz  # PyMuPDF
from app.core.logging import logger
from app.utils.text_cleaning import clean_extracted_text

class PDFExtractor:
    @staticmethod
    def extract_document(pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF page by page preserving:
        - Exact 1-based page numbers
        - Text content (digital text or OCR for image-based/scanned pages)
        - Title / section candidates
        - Page dimensions
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
        # Locate tessdata directory for PyMuPDF C-level OCR engine
        tess_dir = Path(__file__).resolve().parent.parent.parent / "tessdata"
        tess_data_available = tess_dir.exists() and (tess_dir / "eng.traineddata").exists()
        if tess_data_available:
            os.environ["TESSDATA_PREFIX"] = str(tess_dir.resolve())

        pages_data = []
        try:
            doc = fitz.open(str(path))
            total_pages = len(doc)
            logger.info(f"Extracting PDF with PyMuPDF: {path.name} ({total_pages} pages, OCR available: {tess_data_available})")
            
            for page_idx in range(total_pages):
                page = doc[page_idx]
                raw_text = page.get_text("text")
                blocks = page.get_text("blocks")
                
                # If page has very little or no digital text (e.g., scanned document or image-based PDF)
                # automatically trigger high-resolution PyMuPDF OCR on the page
                if len(raw_text.strip()) < 40 and tess_data_available:
                    try:
                        tp = page.get_textpage_ocr(tessdata=str(tess_dir.resolve()), language="eng", dpi=150, full=True)
                        ocr_text = page.get_text("text", textpage=tp)
                        if len(ocr_text.strip()) > len(raw_text.strip()):
                            raw_text = ocr_text
                            blocks = page.get_text("blocks", textpage=tp)
                            logger.info(f"Page {page_idx + 1} of {path.name}: OCR extracted {len(ocr_text)} characters from scanned/image content.")
                    except Exception as ocr_err:
                        logger.warning(f"OCR fallback failed on page {page_idx + 1} of {path.name}: {ocr_err}")

                cleaned = clean_extracted_text(raw_text)
                
                # Check for headings or bold blocks
                first_heading = None
                for b in blocks:
                    block_text = b[4].strip() if len(b) > 4 else ""
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
