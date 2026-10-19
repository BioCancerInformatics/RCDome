# -*- coding: utf-8 -*-
import docx, sys
from docx.shared import Pt, RGBColor
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/RCDome_manuscript_V024_supplementary_information.docx'
doc = docx.Document(PATH)

first_p = doc.paragraphs[0]

def add_before(runs, style=None):
    p = first_p.insert_paragraph_before()
    if style:
        p.style = doc.styles[style]
    for text, bold in runs:
        r = p.add_run(text)
        r.bold = bold
    return p

# ===== Front page (matching manuscript V024 front page, Calibri) =====
add_before([('RCDome: A Multi-Database Human Gene Atlas of Regulated Cell Death', False)], style='Heading 1')
add_before([])
add_before([('Running title:', True), (' RCDome: Human RCD Gene Atlas', False)])
add_before([('Keywords', True), (': regulated cell death, human gene atlas, knowledge platform, multi-database integration, operational definitions, traceability', False)])
add_before([])
add_before([('Emanuell Rodrigues de Souza#', False), (', Victor dos Santos Lopes#', False),
            (', Higor Almeida Cordeiro Nogueira', False), (', and Enrique Medina-Acosta*', False)])
add_before([])
add_before([('Laboratório de Biotecnologia, Centro de Biociências e Biotecnologia, Universidade Estadual do Norte '
             'Fluminense, Avenida Alberto Lamego 2000, Parque California, Campos dos Goytacazes, RJ, CEP 28015-602, Brazil.', False)])
add_before([])
add_before([('*', False), ('Corresponding author', True), (': Enrique Medina-Acosta: quique@uenf.br', False)])
add_before([])
add_before([('Author e-mails', True), (':', False)])
add_before([('Emanuell Rodrigues de Souza: souza.ers00@gmail.com', False)])
add_before([('Victor dos Santos Lopes: victor94santos.lopes@gmail.com', False)])
add_before([('Higor Almeida Cordeiro Nogueira: higoralmeida1995@gmail.com', False)])
add_before([('Enrique Medina-Acosta: quique@uenf.br', False)])
add_before([])
add_before([('#', False), (' Authors share first authorship', False)])

# ===== Uniformize to Calibri (manuscript font) =====
def set_style(name, size, bold):
    try:
        st = doc.styles[name]
        st.font.name = 'Calibri'
        st.font.size = Pt(size)
        st.font.bold = bold
        st.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    except KeyError:
        pass

set_style('Normal', 12, False)
set_style('Title', 16, True)
set_style('Heading 1', 14, True)
set_style('Heading 2', 12, True)

for p in doc.paragraphs:
    sname = p.style.name
    tsize = {'Title': 16, 'Heading 1': 14, 'Heading 2': 12}.get(sname, 12)
    is_note_title = p.text.strip().startswith('RCDome:')
    for r in p.runs:
        r.font.name = 'Calibri'
        r.font.size = Pt(tsize)
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        if is_note_title:
            r.font.bold = True

for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = 'Calibri'
                    r.font.size = Pt(10)
                    r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    try:
        for cell in t.rows[0].cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.bold = True
    except Exception:
        pass

doc.save(PATH)
print('front page added + uniformized to Calibri (manuscript font)')
