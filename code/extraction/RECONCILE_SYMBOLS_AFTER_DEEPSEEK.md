# RECONCILIAÇÃO DE SÍMBOLOS — PÓS-DEEPSEEK (V022 -> V023)

A extração DeepSeek (deepseek_cot_v11_full.py) foi construída a partir dos símbolos da matriz V022.
A matriz foi atualizada para V023 e 6 símbolos mudaram. Quando a extração terminar, aplique este remap
aos resultados antes de fundir com a matriz/manuscrito V023.

Tabela (ver symbol_remap_V022_to_V023.csv):

  IL1RL1          -> IL33R
  AATK            -> LMTK1
  TNFAIP8L1       -> TIPE1
  TNFAIP8L2       -> TIPE2
  TNFAIP8L3       -> TIPE3
  ENSG00000274276 -> CBSL

Como aplicar (nos resultados da extração, ex. cot_v11_progress.json / saída final):
  - substitua o gene_symbol antigo pelo novo nas 6 linhas acima
  - todos os outros símbolos permanecem iguais
  - a contagem de pares (21.567) não muda

Observação: o manuscrito V023 NÃO menciona esses 6 genes, então não há texto a corrigir lá.
