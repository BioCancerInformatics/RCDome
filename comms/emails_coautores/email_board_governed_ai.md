# Email: Digital Molecular RCD Board — agente de IA governado e auto-auditado

**Para:** Emanuell Rodrigues de Souza; Victor dos Santos Lopes; Higor Almeida Cordeiro Nogueira
**De:** Enrique Medina-Acosta
**Assunto:** RCDome: Digital Molecular RCD Board implementado com agente de IA totalmente governado e auto-auditado

---

Emanuell, Victor e Higor,

Boa notícia: o **Digital Molecular RCD Board** foi implementado e validado. Trata-se de um agente de IA totalmente governado e auto-auditado que explora a matriz RCDome e o decoder RCDome para responder a consultas gene–RCD. Segue o resumo da lógica, da governança, da política e do benchmark.

## Lógica

O Board combina dois componentes:

1. **Síntese em prosa** — para uma entidade (e gene opcional), gera uma síntese contínua, com fonte e hedge, estritamente a partir da matriz e do decoder.

2. **Q&A de IA** — um submódulo de recuperação aumentada (RAG) que responde perguntas livres sobre **todas as 53 entidades e todos os 9.265 genes**. Uma camada estática injeta o índice completo gene→entidade (as 22.473 associações; nada é apagado). Uma camada dinâmica recupera, para cada pergunta, os registros completos em quatro dimensões (classe mecanística, papel, direção, tier e PMID). Assim, um gene registrado como executor em uma forma e regulador em outra é mostrado com ambos os registros — sem funil de dados.

## Governança (zero alucinação)

- Apenas os termos "RCDome database" e "RCDome decoder"; as palavras nuas "database", "decoder" e "matrix" são proibidas.
- Verbos causais assertivos são substituídos por hedge ("pode sugerir", "é consistente com", "requer validação").
- Toda resposta termina com o disclaimer exato; pergunta fora do escopo recebe a recusa exata.
- Nunca inventa gene, PMID ou fato; só cita PMIDs presentes nos dados.
- Controle negativo: par ausente é relatado como "not recorded", sem inventar papel ou direção.

## Política

Nenhum limite artificial: o índice estático mantém as 22.473 associações e as seis classificações (MECHANISTIC, LITERATURE_GAP, CONTEXT_GAP, CO_OCCURRENCE, DATABASE_ONLY, INSUFFICIENT_DATA) permanecem alcançáveis em qualquer consulta.

## Benchmark (estatística completa)

**Board (9 testes):** golden 26/26 = 100% · censo 53/53 = 100% · estabilidade de fatos 73/73 = 100% · governança 1 violação em 2.142 checagens = 0,047% · anti-alucinação 4/4 = 100% · articulação 78/79 = 98,7%.

**Q&A (2 testes, n = 100 cada):** precisão positiva 100/100 = 100% · controles negativos 100/100 = 100% · Wilson 95% IC 96,3–100% · binomial bicaudal p = 0,010.

O modelo é o deepseek-chat (temperatura 0,3 no Q&A; 0,7 na síntese). O detalhe completo está na Supplementary Note S4.

## Próximos passos

- Todos: testar o Board e o Q&A no app (aba logo após o Gene Catalog).
- Todos: revisar a Supplementary Note S4 (governança + benchmark).

## Instalação e execução

O pacote atualizado está disponível em:

- **Zip**: `RCDome_V026_update_2.zip` — https://drive.google.com/file/d/11-_6A2JN0PV6TgYLnXhgOttoOTKodYH5/view?usp=sharing
- **Google Drive (pasta)**: https://drive.google.com/drive/folders/1my9M5CT-1SmM4mSnhZKVdWVnzt9Av5y1?usp=sharing
- **Repositório (privado)**: `CHANGELOG_V026_2.md` em `results/changelogs/` — https://github.com/BioCancerInformatics/RCDome

Para instalar e rodar:

1. Baixe `RCDome_V026_update_2.zip` (link acima) e extraia em uma pasta local.
2. Crie um arquivo `.Renviron` na pasta extraída com a chave (compartilhada em separado, nunca no repositório): `DEEPSEEK_API_KEY=...`
3. No R ou RStudio:
   ```r
   setwd(".../RCDome_Atlas/APP")
   shiny::runApp(appDir = ".", port = 8890, launch.browser = TRUE)
   ```
4. O Board fica na aba logo após o Gene Catalog: selecione a entidade, gere a síntese e use o Q&A.

Enrique

---

*Nota: esta mensagem foi redigida com assistência de IA generativa e revisada/aprovada por humano, conforme as regras de governança de Medina para escrita científica com IA (transparência, consentimento e revisão humana).*
