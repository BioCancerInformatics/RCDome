# Email: RCDome V026_update_4 — instalação, consulta e verificação do aplicativo

**Para:** Emanuell Rodrigues de Souza; Victor dos Santos Lopes; Higor Almeida Cordeiro Nogueira
**De:** Enrique Medina-Acosta
**Assunto:** RCDome V026_update_4 — instalação, consulta e verificação do aplicativo

---

Emanuell, Victor e Higor,

O pacote do aplicativo foi atualizado para **RCDome_V026_update_4**. Segue o guia de instalação, consulta e verificação.

## O que o pacote contém

**Todos os módulos do app** (RCD entities, Gene Catalog, RCDome Board + Q&A, Operational Definitions + Comparator, RCD Network, About).
**O changelog completo** (`CHANGELOG_V026_4.md`).
**A pasta `governance/`** com os documentos de governança (protocolo de resposta, contratos de rastreabilidade e auditoria).

## Instalação

1. Baixe `RCDome_V026_update_4.zip` da pasta do Google Drive (link abaixo) e extraia em uma pasta local.
2. Crie um arquivo `.Renviron` na pasta extraída com a chave (compartilhada em separado, nunca no repositório): `DEEPSEEK_API_KEY=...`
3. No R ou RStudio:
   ```r
   setwd(".../RCDome_Atlas/APP")
   shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
   ```

## Consulta

**RCD entities**: selecione uma entidade e veja os genes associados.
**Gene Catalog**: clique em um gene para abrir a página do gene.
**RCDome Board**: gere a síntese em prosa de uma entidade (e gene opcional).
**Q&A**: faça perguntas livres sobre qualquer entidade ou gene.
**Operational Definitions**: consulte a definição operacional de cada entidade.
**Compare Definitions**: compare 2 a 4 entidades lado a lado.
**RCD Network**: veja as associações gene→entidade.

## Verificação

**Confirme que o app abre e carrega a matriz V026** (22.473 genes × 71 colunas).
**Confirme que o Board e o Q&A respondem sem alucinação** (apenas dados da matriz/decoder).
**Confirme os benchmarks registrados** no `CHANGELOG_V026_4.md` e na pasta `governance/`.
**Reportem qualquer erro item por item**, com o passo reproduzido e o resultado observado.

## Links

**Zip/pasta (Google Drive)**: https://drive.google.com/drive/folders/1J8NO3U88GpAeIkdG2Bfo7lXLqu-aHykl?usp=sharing
**Repositório (privado)**: https://github.com/BioCancerInformatics/RCDome

Enrique

---

*Nota: esta mensagem foi redigida com assistência de IA generativa e revisada/aprovada por humano, conforme as regras de governança de Medina para escrita científica com IA (transparência, consentimento e revisão humana).*
