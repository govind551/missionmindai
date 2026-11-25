import sys
import re
import html
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

def markdown_to_reportlab_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', escaped)
    escaped = re.sub(r'(?<![a-zA-Z0-9])\*([^*]+?)\*(?![a-zA-Z0-9])', r'<i>\1</i>', escaped)
    escaped = re.sub(r'`([^`]+?)`', r'<font face="Courier">\1</font>', escaped)
    return escaped

test_str = """### Documented Investigation Findings

Based on official technical reports from NASA, ISRO concerning historical mission(s) **Mars Climate Orbiter, GSLV-F10 / EOS-03, Space Shuttle Columbia (STS-107)**:
- **Mars Climate Orbiter (NASA)**: OFFICIAL INVESTIGATION REPORT // NASA // PAGE 3 & Thermal Control > "OFFICIAL INVESTIGATION REPORT"
- **GSLV-F10 / EOS-03 (ISRO)**: OFFICIAL REPORT *test*.
"""

styles = getSampleStyleSheet()
story = []
for line in test_str.split('\n'):
    line = line.strip()
    if not line:
        continue
    if line.startswith('### ') or line.startswith('## '):
        clean_line = markdown_to_reportlab_html(line.lstrip('#').strip())
        story.append(Paragraph(f'<b>{clean_line}</b>', styles['Normal']))
    elif line.startswith('- ') or line.startswith('* '):
        clean_line = markdown_to_reportlab_html(line[2:].strip())
        story.append(Paragraph(f'&bull; {clean_line}', styles['Normal']))
    else:
        clean_line = markdown_to_reportlab_html(line)
        story.append(Paragraph(clean_line, styles['Normal']))
    story.append(Spacer(1, 4))

doc = SimpleDocTemplate('test_reportlab_clean.pdf', pagesize=letter)
doc.build(story)
print('PDF generated successfully, size:', os.path.getsize('test_reportlab_clean.pdf'))
os.remove('test_reportlab_clean.pdf')
