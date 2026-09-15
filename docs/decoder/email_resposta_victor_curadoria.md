# Email: Resposta a Victor e co-autores (curadoria biológica implementada)

**Para:** Victor dos Santos Lopes; Emanuell Rodrigues de Souza; Higor Almeida Cordeiro Nogueira
**De:** Enrique Medina-Acosta
**Assunto:** RCDome: curadoria biológica implementada integralmente (V026)

---

Prezados Victor, Emanuell e Higor,

A excelente curadoria biológica do Victor foi **integralmente implementada** no RCDome,
após a revisão profunda (propor → acordo humano → executar → ecoar → auditar) de cada
decisão. Segue o resumo do que mudou, para conhecimento de todos e para o Emanuell
atualizar o app.

## O que foi implementado (7 grupos)

1. **A)** MPT-driven necrosis passou a L1 (modalidade); MPT permanece L3 (trigger, `triggered_by`); Vacuolar cell death → L4 (morfológica, cross-species).
2. **B)** 7 campos ontológicos novos no decoder (species_scope, evidence_maturity, relationship_type, parent_entity, ontology_curator_verified, independent_replication, primary_discovery_reference).
3. **C)** hard gates G0–G6 como **camada adicional** (não substituição), com a coluna `hard_gate_status` (L1-ELIGIBLE 16 / NOT-L1 37).
4. **D)** tabela de adjudicação (Supplementary Table S12, 53×26) + separação formal das duas validações (associação gene–RCD automatizada vs status de modalidade curator-governed).
5. **E)** 23 reclassificações de nível + adjudicações específicas: **Anoikis → L2** (subtype_of intrinsic apoptosis) e **Mitotic death → L4** (driven_by mitotic catastrophe).
6. **F)** 5 inserções no manuscrito (fração mecanística ≠ validação independente; subtipo > parent; "RCD-related entities"; nomenclatura dinâmica via evidence_maturity; adjudicação curator-governed).
7. **G)** 9 relações ontológicas registradas (vocabulário de 12 valores).

## Recalibração V026 → V026

A distribuição canônica de níveis agora é:
**16 modalidades · 5 subtipos · 2 triggers · 12 funcional/contextual · 18 genérico/umbrella/legacy/taxon/emerging** (total 53).

## Matriz (agora 71 colunas)

Adicionei o bloco canônico do decoder à matriz, lado a lado com a proveniência Rodrigues:
`decoder_operational_definition` · `decoder_key_molecules` · `decoder_category` · `decoder_hard_gate_status`.

## 📦 Para o Emanuell (atualização do app Shiny)

Por favor, use o novo pacote ZIP (**RCDome_V026_update.zip**, 36 arquivos) do app (envio em anexo/seguinte mensagem) que contém:

1. **Matriz V026** (`unified_gene_rcd_matrix_V026.rds`, 22.473 × **71**), com os níveis recalibrados e o bloco `decoder_*`.
2. **Decoder** (`RCDome_Decoder_53.csv`, 53 × 39), as 53 definições operacionais + `founding_pmid`/`reference_pmid` para cada entidade.
3. **`pmid_title_lookup.json`** (10.141 PMIDs com título verificado).

Com isso, complete o **módulo de entidades RCD** usando os **PMIDs que agora estão tanto na matriz quanto no decoder**, cada detail page pode exibir a definição operacional,
as moléculas-chave, a categoria, o hard-gate status e os PMIDs de ancoragem.

## Verificação

A implementação foi auditada exaustivamente (46/46 na auditoria de conformidade completa (e 31/31 na auditoria do manuscrito contra matriz+decoder)):
níveis, definições (verbatim), dimensões e proveniência concordam entre matriz, decoder,
manuscrito, app e GitHub. O resumo completo está em `analysis/Victor_analysis/CURATION_PROCESS_DEEP_AUDIT.md`.

Agradeço novamente ao Victor pela profundidade da análise, que elevou a qualidade
ontológica do RCDome de forma decisiva.

Abraços,
Enrique

---

**Nota:** esta mensagem foi redigida com assistência de IA generativa e revisada/aprovada por humano, conforme as regras de governança de Medina para escrita científica com IA (transparência, consentimento e revisão humana).