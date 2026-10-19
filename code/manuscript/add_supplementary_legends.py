# -*- coding: utf-8 -*-
import docx, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/'

S1 = ("Supplementary Figure S2. Database contribution and multi-database corroboration. (A) Number of "
"gene\u2013RCD associations contributed by each of the 20 source databases (log2-scaled axis; exact counts printed "
"at the end of each bar). (B) Number of source databases per association: 10,009 associations rest on a single "
"source, 6,313 are corroborated by two sources, and the count declines steeply with additional sources; the long "
"tail up to 14 sources marks the best-corroborated associations (e.g., the canonical executors), which carry the "
"strongest multi-database agreement.")

S2 = ("Supplementary Figure S3. Fraction of associations with mechanistic classification, per source. Each bar "
"shows the percentage of a source\u2019s gene\u2013RCD associations classified as mechanistically involved by the DeepSeek "
"chain-of-thought run (cot_mechanistic = YES), with the numerator and denominator printed at the end of each bar. "
"Classification yield ranges from 21.7% (XDeathDB, 378 of 1,739) to 90.0% (ncFO, 45 of 50), revealing which "
"sources contribute mostly mechanistically-validated associations.")

# ---- 1. Create the Supplementary Information file ----
supp = docx.Document()
h = supp.add_heading('RCDome \u2014 Supplementary Information', level=0)
supp.add_heading('Supplementary Figure Legends', level=1)
p1 = supp.add_paragraph(); p1.add_run(S1).bold = True
p2 = supp.add_paragraph(); p2.add_run(S2).bold = True
supp.save(BASE + 'RCDome_manuscript_V024_supplementary_information.docx')
print('created RCDome_manuscript_V024_supplementary_information.docx')

# ---- 2. Add callouts to the manuscript ----
doc = docx.Document(BASE + 'RCDome_manuscript_governance_V024.docx')

callout_S1 = (" Most associations rest on a single source (10,009 of 22,474 rows), 6,313 are corroborated by two "
"sources, and corroboration declines steeply with additional sources; the long tail up to 14 sources marks the "
"best-corroborated associations, such as the canonical executors (Supplementary Figure S3).")

callout_S2 = (" Classification yield varied markedly by source database: the fraction of associations classified as "
"mechanistically involved ranged from 21.7% (XDeathDB) to 90.0% (ncFO) (Supplementary Figure S3).")

done = {}
for p in doc.paragraphs:
    if '905 rows of genuine multi-database corroboration' in p.text and 'S1' not in done:
        p.add_run(callout_S1)
        done['S1'] = True
    if '10,016 (46.4%) were classified as mechanistically involved' in p.text and 'S2' not in done:
        p.add_run(callout_S2)
        done['S2'] = True

doc.save(BASE + 'RCDome_manuscript_governance_V024.docx')
print('callouts added:', done)
