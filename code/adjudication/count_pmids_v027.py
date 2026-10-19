# -*- coding: utf-8 -*-
"""count_pmids_v027.py — canonical deterministic PMID counter (H43).

Rule (single source of truth):
    A "valid PMID" is a 7- or 8-digit token (PubMed IDs are 8 digits; legacy IDs may be 7).
    Tokens are split on ';' and whitespace. Only the four PMID columns count:
        pmid_list, llm_pmids, epmc_pmids, elicit_pmids.
    Count = number of DISTINCT valid PMIDs across the four columns.

Result for the frozen V027 matrix: 319,548 unique PMIDs.
"""
import csv
import re
import sys

MATRIX = ('D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript/'
          'RCDome_distribution/data/unified_gene_rcd_matrix_V027.csv')
PMID_COLS = ['pmid_list', 'llm_pmids', 'epmc_pmids', 'elicit_pmids']
TOKEN = re.compile(r'\d{7,8}')


def main() -> int:
    with open(MATRIX, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    pmids = set()
    for row in rows:
        for col in PMID_COLS:
            for m in TOKEN.findall(str(row.get(col) or '')):
                pmids.add(m)
    print(f'unique PMIDs (7-8 digit, 4 columns): {len(pmids):,}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
