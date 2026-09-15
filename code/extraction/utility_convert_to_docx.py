"""
Convert RCDome_Methods_Section.md to formatted .docx
A4, Calibri 12pt, 6pt spacing, proper clickable hyperlinks
"""
import re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_hyperlink(paragraph, url, text, font_size=9):
    """Add a proper clickable hyperlink to a paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rStyle = OxmlElement('w:rStyle')
    rStyle.set(qn('w:val'), 'Hyperlink')
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '0000FF')
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(font_size * 2)))
    rPr.append(rStyle)
    rPr.append(c)
    rPr.append(u)
    rPr.append(sz)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return paragraph

INPUT = r"D:\Pré-artigo 5-optosis model\Cellular_Spatial_RCD_manuscript\RCDome_manuscript\docs\RCDome_manuscript.md"
OUTPUT = r"D:\Pré-artigo 5-optosis model\Cellular_Spatial_RCD_manuscript\RCDome_manuscript\docs\RCDome_manuscript_001.docx"

doc = Document()

# A4 page setup
section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

# Default style
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(12)
style.font.color.rgb = RGBColor(0, 0, 0)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.space_before = Pt(0)

with open(INPUT, 'r', encoding='utf-8') as f:
    text = f.read()

sections = re.split(r'\n(?=## )', text)

for sec in sections:
    lines = sec.strip().split('\n')
    if not lines: continue
    
    heading_match = re.match(r'^(#{1,4})\s+(.+)', lines[0])
    if heading_match:
        title = heading_match.group(2).strip()
        h = doc.add_heading(title, level=len(heading_match.group(1)))
        for run in h.runs:
            run.font.name = 'Calibri'
            run.font.color.rgb = RGBColor(0, 0, 0)
        lines = lines[1:]
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Tables
        if line.startswith('|') and i+1 < len(lines) and '---' in lines[i+1]:
            headers = [c.strip() for c in line.split('|') if c.strip()]
            table_rows = [headers]
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [c.strip() for c in lines[i].split('|') if c.strip()]
                table_rows.append(row)
                i += 1
            
            tbl = doc.add_table(rows=len(table_rows), cols=len(table_rows[0]))
            tbl.style = 'Light Grid Accent 1'
            for ri, row in enumerate(table_rows):
                for ci, cell_text in enumerate(row):
                    cell = tbl.rows[ri].cells[ci]
                    clean_text = cell_text.replace('`', '')
                    url_match = re.search(r'(https?://[^\s|]+)', clean_text)
                    
                    p = cell.paragraphs[0]
                    p.clear()
                    p.paragraph_format.space_after = Pt(2)
                    
                    if url_match:
                        url = url_match.group(1)
                        prefix = clean_text[:clean_text.find(url)].strip()
                        if prefix:
                            run = p.add_run(prefix)
                            run.font.name = 'Calibri'
                            run.font.size = Pt(10)
                            run.font.color.rgb = RGBColor(0, 0, 0)
                            if ri == 0: run.bold = True
                        add_hyperlink(p, url, url, font_size=8)
                    else:
                        run = p.add_run(clean_text)
                        run.font.name = 'Calibri'
                        run.font.size = Pt(10)
                        run.font.color.rgb = RGBColor(0, 0, 0)
                        if ri == 0: run.bold = True
            doc.add_paragraph()
            continue
        
        # Regular paragraph with possible URLs
        clean = line.replace('`', '')
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', clean)
        urls = re.findall(r'(https?://[^\s\)]+)', clean)
        
        if clean:
            p = doc.add_paragraph()
            remaining = clean
            for url in urls:
                idx = remaining.find(url)
                if idx > 0:
                    run = p.add_run(remaining[:idx])
                    run.font.name = 'Calibri'
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(0, 0, 0)
                add_hyperlink(p, url, url)
                remaining = remaining[idx + len(url):]
            
            if remaining.strip():
                run = p.add_run(remaining)
                run.font.name = 'Calibri'
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(0, 0, 0)
        
        i += 1

doc.save(OUTPUT)
print(f"Saved: {OUTPUT}")
