# Traceability — Victor app-report fixes (2026-09-19)

Approved fixes applied. No data deleted.

-   [HTML] D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome_distribution/www/explore.html: 2 back-link(s) -> Home-tab click
-   [HTML] D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome_distribution/www/detail_page_wireframe.html: 1 back-link(s) -> Home-tab click
-   [HTML] D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome_distribution/www/module_placeholder.html: 2 back-link(s) -> Home-tab click
-   [HTML] D:/RCDome_github\app/www/explore.html: 2 back-link(s) -> Home-tab click
-   [HTML] D:/RCDome_github\app/www/detail_page_wireframe.html: 1 back-link(s) -> Home-tab click
-   [HTML] D:/RCDome_github\app/www/module_placeholder.html: 2 back-link(s) -> Home-tab click
-   [HTML] D:/RCDome_github\app/explore.html: 2 back-link(s) -> Home-tab click
-   [HTML] D:/RCDome_github\app/detail_page_wireframe.html: 1 back-link(s) -> Home-tab click
-   [PY]  D:/RCDome_github\app/generate_detail_page.py: 1 back-link(s) -> Home-tab click
-   [R]    D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome_distribution/modules/mod_od.R: composite PMID render fixed
-   [R]    D:/RCDome_github\app/modules/mod_od.R: composite PMID render fixed
-   [R]    D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome_distribution/modules/mod_rcd_grid.R: build_decoder_desc collapse -> \n\n
-   [R]    D:/RCDome_github\app/modules/mod_rcd_grid.R: build_decoder_desc collapse -> \n\n
-   [DATA] Apoptosis: primary_refs_pmids '17562483;29362479' -> '17562483'
-   [DATA] Autophagy: primary_refs_pmids '36864290;29362479' -> '36864290'
-   [DATA] Methuosis: primary_refs_pmids '24726643;29362479' -> '24726643'
-   [DATA] Mitochondrial permeability transition: primary_refs_pmids '23483560;29362479' -> '23483560'
-   [DATA] Mitoptosis: primary_refs_pmids '33705288;29362479' -> '33705288'
-   [DATA] Necrosis: primary_refs_pmids '31827074;29362479' -> '31827074'
-   [DATA] Oxeiptosis: primary_refs_pmids '29255269;29362479' -> '29255269'
-   [DATA] Paraptosis: primary_refs_pmids '11121041;29362479' -> '11121041'
-   [DATA] Vacuolar cell death: reference_citation 'Kosta et al. 2004' -> 'Kosta et al. 2004 — name source; describes a non-vacuolar pathway'
-   [DATA] wrote D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.csv (9 cell changes)
-   [DATA] wrote D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.xlsx
-   [COPY] D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.csv -> D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome_distribution/data/RCDome_Decoder_53.csv
-   [COPY] D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.csv -> D:/RCDome_github\data/RCDome_Decoder_53.csv
-   [COPY] D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.csv -> D:/RCDome_github\app/data/RCDome_Decoder_53.csv
-   [COPY] D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.xlsx -> D:/RCDome_github\data/RCDome_Decoder_53.xlsx
## Additional approved fixes A + B (2026-09-19)

-   [CSV] Senescence and Autophagy in Cancer: 'Composite of Cellular senescence (PMID 29362479) + Autophagy (PMID 36864290)' -> 'Composite of Cellular senescence (NCCD_2018; PMID 29362479) + Autophagy (PMID 36864290) — composite pathway label, not a distinct NCCD entity'
-   [CSV] Vacuolar cell death: 'Kosta et al. 2004 — name source; describes a non-vacuolar pathway' -> 'Kosta et al. 2004 (Dictyostelium — name source; non-vacuolar pathway); plant context: Minina 2013 (PMID 24344187), Feng 2022 (PMID 35390283)'
-   wrote D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.csv (2 cells)
-   wrote D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome Decoder/RCDome_Decoder_53.xlsx
-   [COPY] -> D:/Pré-artigo 5-optosis model/Cellular_Spatial_RCD_manuscript/RCDome_manuscript\RCDome_distribution/data/RCDome_Decoder_53.csv
-   [COPY] -> D:/RCDome_github\data/RCDome_Decoder_53.csv
-   [COPY] -> D:/RCDome_github\app/data/RCDome_Decoder_53.csv
-   [COPY] -> D:/RCDome_github\data/RCDome_Decoder_53.xlsx
## Precision fix (2026-09-19): composite galluzzi_nccd_status

- "Senescence and Autophagy in Cancer": `galluzzi_nccd_status` NOT_IN_NCCD_2018 -> COMPOSITE (matching category=COMPOSITE and definition_status=COMPOSITE). This removes the apparent "NOT_IN_NCCD_2018 next to an NCCD_2018 PMID" contradiction in the data itself; the reference_pmid/primary_refs (29362479;36864290) remain the two component references, explained by the citation.
- mod_board.R field description updated to include / COMPOSITE.
