from typing import List, Dict, Any
from app.utils.text_cleaning import extract_section_title

class ChunkingService:
    @staticmethod
    def chunk_document_pages(
        pages_data: List[Dict[str, Any]],
        chunk_size_words: int = 250,
        overlap_words: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Splits extracted pages into semantic chunks while strictly preserving:
        - Exact page number
        - Section header
        - Continuity through sliding overlap
        """
        all_chunks = []

        for page in pages_data:
            page_num = page["page_number"]
            page_text = page["cleaned_text"]
            default_heading = page.get("first_heading") or f"Page {page_num}"

            if not page_text:
                continue

            words = page_text.split()
            if len(words) <= chunk_size_words:
                all_chunks.append({
                    "page_number": page_num,
                    "section_heading": default_heading,
                    "chunk_text": page_text,
                    "chunk_metadata": {
                        "word_count": len(words),
                        "char_count": len(page_text),
                        "page_number": page_num
                    }
                })
                continue

            # Sliding window chunking within the page
            start = 0
            sub_index = 1
            while start < len(words):
                end = min(start + chunk_size_words, len(words))
                chunk_slice = " ".join(words[start:end])
                
                # Check for sub-section title
                sub_heading = extract_section_title(chunk_slice) or f"{default_heading} (Part {sub_index})"

                all_chunks.append({
                    "page_number": page_num,
                    "section_heading": sub_heading,
                    "chunk_text": chunk_slice,
                    "chunk_metadata": {
                        "word_count": len(words[start:end]),
                        "char_count": len(chunk_slice),
                        "page_number": page_num,
                        "sub_index": sub_index
                    }
                })

                if end == len(words):
                    break
                start += (chunk_size_words - overlap_words)
                sub_index += 1

        return all_chunks
