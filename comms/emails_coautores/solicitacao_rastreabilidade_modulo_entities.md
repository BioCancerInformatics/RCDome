# Solicitação de rastreabilidade: módulos RCD Entities e RCD Network

**Para:** Emanuell Rodrigues de Souza
**De:** Enrique Medina-Acosta
**Assunto:** RCDome: rastreabilidade obrigatória das informações dos módulos RCD Entities e RCD Network

---

Emanuell,

O RCDome é um repositório fundamentado em rastreabilidade e auditabilidade. Toda informação nele incorporada deve possuir origem identificável, lógica de geração documentada e teste estatístico ou *benchmark* que permita verificar sua precisão e confiabilidade. A matriz, o RCDome Decoder e os módulos que desenvolvemos deste lado — Gene Catalog, RCDome Board, Operational Definitions e Compare Definitions — seguem rigorosamente esse princípio. Todos foram auditados, e sua documentação, código e lógica de desenvolvimento encontram-se registrados no GitHub do projeto, sem exceção.

Os módulos **RCD Entities** e **RCD Network**, que estão sob sua responsabilidade, ainda contêm informações que não atendem integralmente a esses requisitos. Em particular, as descrições mecanísticas armazenadas na pasta *descricao RCDs*, as figuras e os minilogos não apresentam, no repositório do projeto, proveniência suficientemente documentada, referências verificáveis e, principalmente, o código-fonte e a lógica utilizados para sua geração. Essa ausência impede a reprodução independente, a auditoria do conteúdo e a avaliação de sua conformidade com as regras de governança e com a política de curadoria e agrupamento do RCDome.

Para que essas informações possam permanecer no RCDome, preciso que você forneça, para cada componente:

1. O código-fonte completo e a lógica utilizados para extrair, processar ou gerar a informação.

2. O teste, validação ou *benchmark* utilizado para verificar a precisão e a consistência da informação gerada.

3. Os documentos e registros de proveniência necessários para que o resultado possa ser reproduzido de forma independente.

4. Para cada figura, minilogo e resumo associado a uma **RCD Entity**, o código-fonte utilizado para sua geração e uma descrição explícita da lógica e do procedimento empregados, documentados em formato adequado para posterior incorporação à seção **Methods** ou a uma **Supplementary Note** do manuscrito.

5. Todo o material será rigorosamente auditado quanto à conformidade com as regras de governança, rastreabilidade e política de curadoria do RCDome. O código, a documentação metodológica, os testes de validação e os registros de proveniência deverão ser depositados no GitHub do projeto. Componentes que não atendam a esses requisitos não poderão ser incorporados à versão final do RCDome.

A regra de governança deve ser inequívoca: **informação sem rastreabilidade, sem proveniência documentada, sem código ou lógica reprodutível e, quando aplicável, sem validação ou *benchmark* será excluída do aplicativo e do repositório**. Da mesma forma, quando IA tiver sido utilizada para exploração, síntese ou geração de conteúdo, o procedimento empregado deverá estar explicitamente documentado. Um conceito apresentado apenas como texto ou representação gráfica, sem documentação que permita reconstruir como foi obtido, não atende aos requisitos de governança do RCDome.

Precisamos garantir que **RCD Entities** e **RCD Network** alcancem o mesmo padrão de rastreabilidade, reprodutibilidade e auditabilidade aplicado aos demais componentes do projeto.

Enrique

---

*Nota: esta mensagem foi redigida com assistência de IA generativa e revisada/aprovada por humano, conforme as regras de governança de Medina para escrita científica com IA (transparência, consentimento e revisão humana).*
