import re

def clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    
    # Replace non-breaking spaces and other odd unicode spaces
    cleaned = text.replace('\xa0', ' ').replace('\u200b', '')
    
    # Fix hyphenated line breaks (e.g., "ther-\nmal" -> "thermal")
    cleaned = re.sub(r'(\w+)-\n(\w+)', r'\1\2', cleaned)
    
    # Replace multiple newlines with double newline (preserve paragraphs)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Replace multiple spaces/tabs with single space
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    
    # Remove control characters except standard whitespace
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned)
    
    return cleaned.strip()

def extract_section_title(text: str) -> str | None:
    """Heuristic to detect potential section title in the first lines of text"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None
    first_line = lines[0]
    # Check if first line looks like a header (short, capitalized, or numbered)
    if len(first_line) < 100:
        if re.match(r'^(Section|\d+\.|\b[A-Z\s]{4,}\b|Appendix|Chapter|Finding|Recommendation)', first_line):
            return first_line
    return None
