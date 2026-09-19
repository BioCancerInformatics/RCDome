# FINAL compliance audit — Victor app-report (2026-09-19)

**Result: 46 checks, 0 FAIL**

Scope: app code, supplementary tables, matrix, decoder, manuscript, board prompt, propagation.

- [PASS] 53 rows
- [PASS] 39 cols
- [PASS] Methuosis: primary_refs=24726643
- [PASS] Autophagy: primary_refs=36864290
- [PASS] Necrosis: primary_refs=31827074
- [PASS] Oxeiptosis: primary_refs=29255269
- [PASS] Mitoptosis: primary_refs=33705288
- [PASS] Apoptosis: primary_refs=17562483
- [PASS] Mitochondrial permeability transition: primary_refs=23483560
- [PASS] Paraptosis: primary_refs=11121041
- [PASS] composite category=COMPOSITE
- [PASS] composite definition_status=COMPOSITE
- [PASS] composite galluzzi_nccd_status=COMPOSITE
- [PASS] composite citation explains NCCD component
- [PASS] VCD category=TAXON
- [PASS] VCD founding=15358773
- [PASS] VCD secondary=24344187;35390283
- [PASS] VCD citation = Dictyostelium + plant
- [PASS] COMPOSITE status only on composite
- [PASS] no NOT_IN_NCCD (non-composite) still lists 29362479
- [PASS] decoder XLSX cells consistent
- [PASS] mod_od.R composite founding branch
- [PASS] mod_od.R multi-PMID render_pmids
- [PASS] mod_od.R citation first PMID
- [PASS] mod_rcd_grid.R collapse="\n\n"
- [PASS] mod_board.R NCCD desc includes / COMPOSITE
- [PASS] mod_od.R parses
- [PASS] mod_rcd_grid.R parses
- [PASS] mod_board.R parses
- [PASS] detail_page_wireframe.html: copies-identical=True, unified=True, no-stale-href=True
- [PASS] explore.html: copies-identical=True, unified=True, no-stale-href=True
- [PASS] module_placeholder.html: copies-identical=True, unified=True, no-stale-href=True
- [PASS] generate_detail_page.py: copies-identical=True, unified=True, no-stale-href=True
- [PASS] Table S3: 8 entities Key References cleaned
- [PASS] Table S11: all decoder changes mirrored
- [PASS] matrix does NOT mirror decoder reference fields
- [PASS] matrix VCD decoder_category=TAXON
- [PASS] no 'fixedfixed'
- [PASS] 'is fixed and' present (typo fixed)
- [PASS] manuscript 29362479 only as NCCD consensus citation
- [PASS] decoder CSV: 3 copies identical
- [PASS] decoder XLSX: 1 copies identical
- [PASS] mod_od.R: 1 copies identical
- [PASS] mod_rcd_grid.R: 1 copies identical
- [PASS] mod_board.R: 1 copies identical
- [PASS] no hardcoded stale PMIDs
