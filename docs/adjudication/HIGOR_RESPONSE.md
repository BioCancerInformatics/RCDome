Higor,

Google Drive
https://drive.google.com/drive/folders/1RJXKZoN7DK5l-NrLBpdG_yO0_d8BoSCo?usp=sharing

Durante a revisão do V026 recebemos três mensagens suas sobre o mesmo conjunto de peças — manuscrito, notas suplementares, tabelas, decoder e o Digital Molecular Board:

1. os quatro comentários curtos sobre a governança do Board;
2. a revisão ponto a ponto do V026 (dez pontos);
3. o documento "Revisão_manuscrito_HACN" (segunda leitura, com sua "Resposta" a cada ponto).

As três mensagens foram consolidadas em uma única frente de revisão e processadas sob o protocolo de governança do projeto: auditoria somente-leitura → adjudicação ponto a ponto → propagação horizontal (todas as peças) e vertical (contagens, resumos, legendas, figuras e descritores de variáveis) → verificação independente (93 verificações de conformidade, todas PASS). Nenhuma correção foi aplicada por substituição cega; cada ponto foi julgado contra a evidência já fixada, e os pontos que não procediam como redigidos foram reformulados em vez de aceitos. Toda correção tem registro de rastreabilidade (HIGOR_CORRECTIONS_APPLIED.md).

**Mensagem 1 — quatro comentários sobre o Board.** Os quatro procedem e foram aplicados: (1) a contradição "ends with" entre as regras 4 e 5 foi resolvida na seção única "Mandatory ending" (corpo → 3 queries → disclaimer); (2) "Four evidence tiers" → "Four provenance categories" (P1–P4), para não colidir com o campo `evidence_tier` (T1–T4) da matriz; (3) a ordem scrub → auditoria foi explicitada (o scrub determinístico roda primeiro; a auditoria roda sobre a saída scrubada); (4) "zero hallucination" → "zero hallucination recorded in the performed benchmark" (ausência observada, não garantia geral).

**Mensagem 2 — revisão do V026 (dez pontos).** Nove pontos procederam e foram aplicados; um (ponto 9) não procedia como redigido e foi reformulado.

1. **Tiers T1–T4 — procede.** Decisão final: separar, e não unificar, as duas métricas. `evidence_tier` (fontes + validação LLM) e `confidence_tier` (pontuação ponderada D=4, B=3, A=1, C=1) agora são descritas como métricas independentes em Methods.
2. **Europe PMC — procede.** Adotamos a redação do documento "Revisão_manuscrito_HACN": "Phase 2B queried the Europe PMC full-text index and processed 167,868 open-access full-text articles."
3. **Denominador — procede.** Todos os denominadores foram explicitados: 22.473 linhas = 21.568 pares únicos gene–RCD + 905 linhas de corroboração.
4. e 8. **Direção — procede.** Contagens recontadas sobre os 21.568 pares únicos (REGULATOR 9.489, EXECUTOR 469, MARKER 5, UNCERTAIN 11.605; direção PROMOTES 5.070, PROTECTS 4.755, UNCLEAR 11.743) e o escopo da direção deixou de ser restrito a REGULATOR; a Figura 3C foi corrigida.
5. **Soma dos tiers — procede.** T1 = 2.864 e T3 = 8.212 corrigidos (soma 22.473).
6. **"EXECUTOR precision 100%" — procede.** Substituído por "Unsupported EXECUTOR claims remaining: 0" no manuscrito, na Figura 2 e na Tabela S14 (gate G4). A precisão 10/10 ficou restrita ao benchmark de seleção de modelo.
7. **Origem das definições — procede após reconciliação.** 20 de novo (19 rascunho-fundador + 1 pré-PubMed), 20/20 NCCD (integridade verbatim) e 33 non-NCCD.
9. **"28 entidades" — reformulado.** Agora é proveniência (cobertura multi-optosis), não limitação; todas as 53 entidades têm definição ancorada a um PMID de referência.
10. **"for the first time" — procede.** Removido e substituído por "explicit" e "quantitatively measurable".

**Mensagem 3 — "Revisão_manuscrito_HACN".** Sua análise mais profunda confirmou e acrescentou correções, todas aplicadas: a separação `evidence_tier` / `confidence_tier` (consolidada acima); a localização restante da redação do EXECUTOR (Tabela S14, gate G4); a reversão para 20 de novo (não 19) e 20/20 NCCD (não 19/20), com 33 non-NCCD confirmado. Também adotamos a redação do Europe PMC (ponto 2 da revisão do V026) e a reformulação do "28 entidades" como proveniência (ponto 9).

**Governança, propagação, proveniência e desafio humano.** Todas as correções foram propagadas horizontalmente (manuscrito, matriz, notas, tabelas suplementares, descritores de variáveis, decoder, app, Board e contrato de rastreabilidade) e verticalmente (contagens, resumos, legendas e figuras). A verificação independente está em COMPLIANCE_AUDIT.md/.xlsx (93/93 PASS). O contrato (docs/RCDome_Traceability_Contract.md) foi atualizado com as três decisões do Board. A revisão humana foi o gate final: pontos procedentes foram aplicados; pontos não procedentes como redigidos foram reformulados; nenhum número foi alterado sem reconto direto na matriz.

Google Drive

Enrique

*Nota: esta mensagem foi redigida com assistência de IA generativa e revisada/aprovada por humano, conforme as regras de governança de Medina para escrita científica com IA (transparência, consentimento e revisão humana).*
