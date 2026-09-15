# TODO — Curadoria de Victor (pendências identificadas)

Registrado após o ocean-deep audit do GRUPO A (2026-09-05).

## Grupo E — Entidades com inconsistência nível × tipo (L1 vs morfologia/umbrella/contextual)

| # | Entidade | Nível atual | Tipo atual (matriz) | Nível proposto (Victor) | Ação |
|---|---|---|---|---|---|
| 1 | Necrosis | L1 | MORPHOLOGY_OR_OUTCOME | L4 | reclassificar para L4 |
| 2 | Oncosis | L1 | MORPHOLOGY_OR_OUTCOME | L4 | reclassificar para L4 |
| 3 | Metalloptosis | L1 | UMBRELLA | L5 | reclassificar para L5 (umbrella_for) |
| 4 | Regulated Necrosis | L1 | UMBRELLA | L5 | reclassificar para L5 (umbrella_for) |
| 5 | Ammonia-induced cell death | L1 | CONTEXTUAL_PROGRAM | L4/L5 | reclassificar |
| 6 | Phagoptosis | L1 | CONTEXTUAL_PROGRAM | L4 | reclassificar |
| 7 | Anoikis | L1 | CONTEXTUAL_PROGRAM | L2 | reclassificar para L2 (subtype_of Intrinsic apoptosis) |
| 8 | Autophagy | L1 | CELLULAR_PROCESS | L4 | reclassificar (processo, não modalidade de morte) |
| 9 | Autosis | L1 | SUBTYPE | L2 | reclassificar para L2 (subtype) |
| 10 | Erebosis | L1 | TAXON_OR_TISSUE_SPECIFIC_PROGRAM | L4 | reclassificar (específica de Drosophila) |
| 11 | Mitoptosis | L1 | LEGACY_OR_UNRESOLVED | L4/L5 | reclassificar (processo organelar, falha G0/G1) |
| 12 | PANoptosis | L1 | INTEGRATED_PROGRAM | L4 | reclassificar (integrated_program) — GRUPO D |

## Observações

- Itens 8–12 foram **surfaced pelo GROUP C deep audit** (cross-check hard_gate_status × matriz): decoder `category=Executioner/INTEGRATED` conflita com o tipo da matriz (CELLULAR_PROCESS/SUBTYPE/TAXON/LEGACY/INTEGRATED_PROGRAM).

- Estes 7 são o território do **GRUPO E** (adjudicações específicas) + o modelo ontológico do **GRUPO G** (relações).
- Não serão tratados agora (processo: uma discussão por vez, sem pular).
- Cada reclassificação exigirá: proposta → acordo humano → executar → ecoar → auditar (mesmo ciclo do GRUPO A).

## Status

- [ ] Necrosis → L4
- [ ] Oncosis → L4
- [ ] Metalloptosis → L5
- [ ] Regulated Necrosis → L5
- [ ] Ammonia-induced cell death → L4/L5
- [ ] Phagoptosis → L4
- [ ] Anoikis → L2
