Prezado Higor,

Recebemos suas observações sobre a versão V026 do manuscrito. Abaixo, a análise ponto a ponto, com os números conferidos diretamente na matriz unificada (22.473 linhas). Onde a observação procede, indicamos a correção a ser aplicada.

**1. Definição dos níveis de evidência T1–T4 — procede.**
As duas descrições (número de fontes + confirmação LLM; e pontuação ponderada dos canais A–D) são a mesma regra escrita duas vezes. Vamos unificar em uma única definição: a pontuação ponderada (D=4, B=3, A=1, C=1) refinada pelo status da validação em duas chamadas (T1 = pontuação ≥7, ou ≥4 com LLM CONFIRMED; T2 = 4–6, ou 2–3 com CONFIRMED; T3 = 2–3 com NEEDS_CONTEXT/NEEDS_LITERATURE, ou 1 com CONFIRMED; T4 = 1 com UNCLEAR/UNVERIFIED).

**2. Europe PMC — procede.**
O número correto é 12,3 milhões de artigos em texto completo (de 48,9 milhões de resumos). O texto será corrigido.

**3. Denominador (linhas vs. pares) — procede.**
Vamos explicitar o denominador em cada contagem: 22.473 linhas da matriz = 21.568 pares únicos gene–RCD + 905 linhas de corroboração. As contagens de role/direction/tier referem-se às 22.473 linhas.

**4 e 8. Contagens de direção — procede (duas causas).**
As contagens do manuscrito estão defasadas em relação à matriz. Os valores corretos na matriz são: REGULATOR 9.971, EXECUTOR 580, MARKER 6, UNCERTAIN 11.916; direção PROMOTES 5.452, PROTECTS 4.964, UNCLEAR 12.057. Além disso, a direção não se restringe a REGULATOR — inclui EXECUTOR e UNCERTAIN. A Figura 3C será corrigida para não afirmar "among the regulators".

**5. Soma dos tiers — procede.**
Os valores corretos são T1 = 2.864, T2 = 5.686, T3 = 8.212, T4 = 5.711 (soma 22.473). O manuscrito trazia T1 = 2.862 e T3 = 8.213 (soma 22.472).

**6. "EXECUTOR precision 100%" — procede.**
A precisão não pode ser reportada como 100% nesse contexto: com os 192 registros EXECUTOR rebaixados a REGULATOR, restam zero previsões positivas, e precisão = 0/0 é indefinida. A redação será alterada para "nenhuma classificação EXECUTOR sem suporte permaneceu após a governança". A precisão de 100% (10/10) pertence ao benchmark de seleção de modelo, e será descrita separadamente.

**7. Origem das definições — parcialmente procede; requer reconciliação.**
Na matriz (decoder), a distribuição é NCCD 20, Rodrigues 12, de novo 19, pré-PubMed 1, composta 1 (= 53). O manuscrito informa "20 de novo" (na verdade 19 de novo + 1 pré-PubMed), "19/19 NCCD" (checagem de integridade verbatim) e "40 non-NCCD". Os três números serão reconciliados com a distribuição da matriz.

**9. "28 entidades sem definição referenciada por PMID" — não procede como redigido.**
O manuscrito diz "28 entidades sem definição multi-optosis", não "sem PMID". Todas as 53 entidades possuem definição ancorada a um PMID fundador. A frase será reformulada para deixar isso explícito.

**10. "for the first time" — procede.**
As expressões serão removidas; substituídas por "explicit" e "quantitatively measurable".

As correções serão aplicadas ao manuscrito com registro de rastreabilidade e os números recontados a partir da matriz.

Atenciosamente,
Enrique
