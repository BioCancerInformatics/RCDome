# Email: RCDome — app Shiny (espelho V026) para execução local

**Para:** Emanuell, Victor, Higor
**De:** Enrique Medina-Acosta
**Assunto:** RCDome — app Shiny (espelho V026) para execução local no R Studio

---

Segue o app Shiny do RCDome (espelho V026), pronto para execução local.

**Google Drive:** [Google Drive](https://drive.google.com/drive/folders/1e5bVmd2iMcDclpws6YO-pFRpDWlHfytc?usp=sharing)

**Instruções (3 passos):**

1. Baixe `RCDome_V026_distribution.zip` e descompacte em uma pasta vazia.
2. No R Studio, aponte o diretório para a pasta descompactada:
   ```r
   setwd("CAMINHO_DA_PASTA_DESCOMPACTADA")
   ```
3. Rode o app:
   ```r
   shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
   ```

O app abre no navegador (http://127.0.0.1:8890). A chave da API DeepSeek já está configurada no pacote. Módulos disponíveis: Home, Explore RCDome, Operational Definitions, Compare Definitions, RCD entities, Gene Catalog, RCDome Board, Network e About.

Para exploração e avaliação das funcionalidades (módulo RCD entities (Emanuell) 55% — dependente de escusa!!).

Enrique

---

*Nota: esta mensagem foi redigida com assistência de IA generativa e revisada/aprovada por humano, conforme as regras de governança de Medina para escrita científica com IA (transparência, consentimento e revisão humana).*
