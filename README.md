# tontoc

*Front-end* de compilador para a linguagem **TONTO** (*Textual Ontology Language*), atualmente em desenvolvimento na fase do analisador léxico (*lexer*). Desenvolvido em **Python 3.14** utilizando a biblioteca **PLY** (*Python Lex-Yacc*).

Projeto desenvolvido para a disciplina de **Compiladores** do Departamento de Computação do Centro de Ciências Exatas e Naturais (CCEN) da **Universidade Federal Rural do Semi-Árido (UFERSA)**, sob orientação do **Prof. Dr. Patrício de Alencar Silva**.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura do Analisador](#arquitetura-do-analisador)
  - [Pipeline de Processamento](#pipeline-de-processamento)
  - [Separação de Responsabilidades](#separação-de-responsabilidades)
  - [Decisões de Projeto e Estratégias Léxicas](#decisões-de-projeto-e-estratégias-léxicas)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Como Executar](#como-executar)
- [Saídas e Relatórios Gerados](#saídas-e-relatórios-gerados)
  - [1. Visão Analítica de Tokens](#1-visão-analítica-de-tokens)
  - [2. Tabela de Síntese Estatística](#2-tabela-de-síntese-estatística)
  - [3. Diagnóstico de Erros Contextual](#3-diagnóstico-de-erros-contextual)
- [Conjunto de Testes e Validação](#conjunto-de-testes-e-validação)

---

## Visão Geral

O **`tontoc`** é o *front-end* de um compilador para a linguagem TONTO e, no momento, encontra-se na fase de implementação do seu analisador léxico (*lexer*). O analisador processa arquivos com extensão `.tonto`, transformando o fluxo de caracteres de entrada em um fluxo ordenado de tokens com coordenadas dimensionais (linha e coluna), garantindo a conformidade com as regras gramaticais e convenções de nomenclatura estabelecidas.

Em caso de divergências sintático-léxicas, o analisador aplica recuperação por descarte de caracteres ou interceptação de padrões malformados, emitindo relatórios diagnósticos com apontadores visuais e sugestões corretivas.

---

## Arquitetura do Analisador

O projeto foi construído seguindo princípios de arquitetura em camadas e separação estrita de responsabilidades, garantindo desacoplamento entre o motor de análise, a lógica de diagnóstico, a interface de linha de comando e a formatação de relatórios.

### Pipeline de Processamento

```text
  [ Arquivo .tonto ]
          │
          ▼
   ┌──────────────┐
   │    Reader    │  Leitura segura com tratamento de I/O e encoding
   └──────┬───────┘
          │ Código-fonte (string)
          ▼
   ┌──────────────┐
   │  LexerRules  │  Definições formais de Regex, precedência e palavras reservadas
   └──────┬───────┘
          │ Herança e regras declarativas
          ▼
   ┌──────────────┐
   │    Lexer     │  Motor PLY, estado, cálculo de colunas e captura de tokens
   └──────┬───────┘
          │ Tokens tipados + Lista de LexicalError
          ▼
   ┌──────────────┐
   │ LexerReporter│  Geração das visões analítica, síntese e diagnóstico
   └──────┬───────┘
          │ Relatório formatado (ANSI / Texto puro)
          ▼
   ┌──────────────┐
   │     CLI      │  Emissão na saída padrão/erro e definição do exit code
   └──────────────┘
```

### Separação de Responsabilidades

Os componentes do pacote `src/tontoc` estão estruturados da seguinte forma:

- **`tontoc.lexer.rules.LexerRules`**: Classe abstrata que centraliza a especificação formal das regras léxicas do PLY:
  - Tabela de palavras reservadas, estereótipos de classes, estereótipos de relações, meta-atributos e tipos nativos.
  - Expressões regulares para delimitadores, operadores de associação, agregação e comentários.
  - Regras de identificadores com garantia de precedência através da ordem de declaração de funções `t_*` (como a prioridade de `CUSTOM_DATA_TYPE` sobre os demais identificadores) e asserções *lookahead* negativas `(?![a-zA-Z0-9_])`, evitando ambiguidades entre palavras-chave e identificadores.

- **`tontoc.lexer.lexer.Lexer`**: Especialização de `LexerRules` que encapsula o motor `ply.lex`:
  - Gerencia o ciclo de vida do lexer (`lex.lex(object=self)`).
  - Controla o estado de análise, o acumulador de tokens reconhecidos e a coleção de erros léxicos encontrados.
  - Executa o cálculo de posição coluna-a-coluna a cada token emitido.

- **`tontoc.lexer.errors.LexicalError`**: Modelo de domínio para falhas léxicas:
  - Encapsula coordenadas de ocorrência (`lineno`, `column`), o valor textual com falha e a linha correspondente do código-fonte.
  - Implementa um motor heurístico interno (`_diagnose`) que inspeciona a estrutura do identificador inválido (presença indevida de dígitos numéricos, sublinhados no início/fim, ausência de sufixos obrigatórios como `Class` ou `DataType`) e gera diagnósticos objetivos acompanhados de sugestões de correção no padrão de compiladores modernos (Clang/Rust).

- **`tontoc.lexer.reporter.LexerReporter`**: Camada de projeção e visualização:
  - Produz a **Visão Analítica** detalhada de tokens.
  - Consolida a **Tabela de Síntese Estatística** com contadores das estruturas ontológicas reconhecidas.
  - Renderiza o **Painel de Erros**, extraindo o contexto do código com marcadores de posição (`^^^^`).

- **`tontoc.cli` & `tontoc.args`**: Ponto de entrada da aplicação CLI:
  - Faz o parsing dos argumentos da linha de comando com `argparse`.
  - Orquestra a leitura de arquivos através de `tontoc.reader` com tratamento resiliente de exceções de I/O.
  - Define os códigos de saída do processo conforme a presença ou ausência de erros.

- **`tontoc.colors.Style`**: Módulo utilitário de estilização ANSI sem dependências externas, com detecção de TTY (`isatty()`) e respeito automático à especificação [NO_COLOR](https://no-color.org).

### Decisões de Projeto e Estratégias Léxicas

Como o analisador opera de forma puramente léxica (*stateless* e desacoplado de um *parser* sintático), foram adotadas decisões de engenharia específicas para eliminar ambiguidades entre padrões semelhantes e garantir diagnósticos precisos.

#### 1. Precedência na Definição de Regras: Novos Tipos (`DataType`)

No motor léxico do **PLY**, as regras declaradas por meio de funções (`def t_*`) são avaliadas na **ordem exata em que são definidas no código-fonte**. Isso confere controle determinístico sobre a prioridade de casamento de padrões que compartilham prefixos ou estruturas semelhantes.

A especificação de novos tipos (`CUSTOM_DATA_TYPE`) estabelece que devem iniciar com qualquer letra (`[a-zA-Z]`), sem conter números ou sublinhados, e terminar obrigatoriamente com a subcadeia `DataType` (ex.: `CPFDataType`, `PhoneNumberDataType`, `emailDataType`).

Na classe `LexerRules`, a regra `t_CUSTOM_DATA_TYPE` foi intencionalmente posicionada **antes das demais definições de identificadores** (`t_INSTANCE_ID`, `t_CLASS_ID`, `t_RELATION_ID` e `t_MALFORMED_IDENTIFIER`):

- **Prevenção de conflito com relações (`RELATION_ID`):** Diferente dos identificadores de classes (que iniciam obrigatoriamente com maiúscula), a especificação permite que novos tipos iniciem com qualquer letra (`[a-zA-Z]`), incluindo minúsculas (ex.: `cpfDataType`, `emailDataType`). Como os identificadores de relações casam qualquer termo iniciado por minúscula (`[a-z][a-zA-Z]*`), se `t_RELATION_ID` fosse declarada antes de `t_CUSTOM_DATA_TYPE`, termos válidos como `cpfDataType` seriam capturados avidamente como relações, nunca alcançando o reconhecimento de tipo customizado.
- **Eliminação de ambiguidade com classes (`CLASS_ID`):** Na especificação original da linguagem, onde classes não possuíam sufixo e aceitavam qualquer palavra iniciada por maiúscula (`[A-Z][a-zA-Z_]*`), a antecipação de `CUSTOM_DATA_TYPE` era indispensável para que tipos como `CPFDataType` não fossem classificados como classes. Com a adoção do sufixo obrigatório `Class`, a colisão direta foi eliminada no nível de expressão regular, mantendo a precedência necessária essencialmente contra `RELATION_ID`.
- **Hierarquia estrita de resolução:** A ordenação sequencial `CUSTOM_DATA_TYPE` → `INSTANCE_ID` → `CLASS_ID` → `RELATION_ID` → `MALFORMED_IDENTIFIER` estabelece um funil no qual regras mais específicas e com sufixos identificadores são avaliadas primeiro, restando para `t_MALFORMED_IDENTIFIER` apenas cadeias que violaram as convenções da linguagem.

#### 2. Sufixo `Class` em Identificadores de Classe

Na especificação original da disciplina (`docs/trabalho-01.md`), a convenção para identificadores de classes estabelecia apenas que deveriam iniciar com letra maiúscula, sem conter dígitos numéricos (ex.: `Person`, `University`).

O projeto **`tontoc`** adicionou uma regra complementar em relação à especificação original: **a obrigatoriedade do sufixo `Class` nos identificadores de classes** (ex.: `PersonClass`, `UniversityClass`).

Essa decisão foi adotada para resolver um desafio inerente à análise puramente léxica:

1. **Ambiguidade entre Classes com Números e Instâncias Válidas**:
   Um dos requisitos do trabalho é diagnosticar erros quando classes contêm números. Pela especificação, identificadores de instâncias iniciam com qualquer letra (`[a-zA-Z]`) e terminam obrigatoriamente com dígitos numéricos (ex.: `Planeta1`, `pizza03`). Sem uma regra de diferenciação, uma entrada como `Pessoa1` ou `Person1` (uma tentativa inválida de declarar classe com número) casaria avidamente como um `INSTANCE_ID` válido, mascarando o erro léxico.
2. **Preservação da Natureza Stateless / Context-Free do Lexer**:
   Sem o sufixo, a única maneira de o analisador saber se `Pessoa1` é uma instância legítima ou uma classe com número seria inspecionar o contexto anterior (verificar se o token precedente era um estereótipo de classe como `kind`, `role`, `phase` ou `package`). Isso introduziria controle de estado e acoplamento sintático prematuro no motor léxico.
3. **Harmonização com a Regra de Novos Tipos (`*DataType`)**:
   De forma análoga à especificação original — que já exige o sufixo `DataType` para discriminar tipos de dados customizados de maneira estritamente léxica —, o sufixo `Class` proporciona determinismo na tokenização. Isso permite à regra `t_MALFORMED_IDENTIFIER` isolar a intenção do usuário e gerar mensagens diagnósticas precisas (apontando se o identificador de classe contém números ou se falta o sufixo `Class`), sem conflitar com instâncias válidas.

#### 3. Estratégia de Diagnóstico e Recuperação de Erros

A análise léxica utiliza uma estratégia em dois níveis para interceptar e diagnosticar problemas sem interromper o fluxo de varredura:

1. **Interceptação de Identificadores Malformados (`t_MALFORMED_IDENTIFIER`)**:
   Definida com uma expressão abrangente `[a-zA-Z0-9_]+` posicionada estrategicamente após as regras de identificadores válidos. Qualquer cadeia contendo caracteres válidos para identificadores, mas que viole as convenções da gramática (como falta do sufixo `Class`, números em relações, sublinhados em `DataType` ou dígitos no início), é capturada como uma unidade léxica completa. Isso previne que o analisador fragmente o identificador inválido em múltiplos tokens desconexos.

2. **Captura de Caracteres Ilegais (`t_error`)**:
   Caracteres que não pertencem ao alfabeto permitido pela especificação da linguagem (tais como `$`, `#`, `!`, `&`, entre outros) disparam a rotina de erro padrão do PLY. O erro é registrado com suas coordenadas e o caractere inválido é descartado via `self._lexer.skip(1)`, permitindo a recuperação imediata do analisador para processar o restante do arquivo.

---

## Estrutura do Repositório

```text
tontoc/
├── docs/
│   └── trabalho-01.md         # Especificação formal da avaliação acadêmica
├── examples/
│   ├── valid/                 # Conjunto sintaticamente válido de testes unitários
│   │   ├── 01_datatypes_and_classes.tonto
│   │   ├── 02_relations_and_stereotypes.tonto
│   │   └── 03_genset_and_instances.tonto
│   ├── invalid/               # Casos de teste negativos para validação diagnóstica
│   │   ├── 01_illegal_characters.tonto
│   │   ├── 02_invalid_identifiers.tonto
│   │   └── 03_invalid_datatypes.tonto
│   └── validation/            # Modelos ontológicos oficiais fornecidos pelo professor
│       ├── car-example/
│       ├── food-allergy-example/
│       ├── hospital-model/
│       ├── ontology-design-patterns-em-tonto/
│       ├── pizzaria-model/
│       └── tdah-example/
├── src/
│   └── tontoc/
│       ├── __init__.py        # Exportação da API pública (main e analyze)
│       ├── args.py            # Parser de argumentos da linha de comando
│       ├── cli.py             # Controlador de execução via terminal
│       ├── colors.py          # Formatação ANSI e suporte a NO_COLOR
│       ├── lib.py             # Fachada do analisador léxico
│       ├── reader.py          # Leitura de arquivos com tratamento de exceções
│       └── lexer/             # Núcleo léxico baseado em PLY
│           ├── __init__.py
│           ├── errors.py      # Modelo LexicalError e motor de sugestões
│           ├── lexer.py       # Gerenciador do motor PLY e controle de estado
│           ├── reporter.py    # Gerador de relatórios (analítico, síntese e erros)
│           ├── rules.py       # Especificação declarativa de regras e tokens
│           └── types.py       # Tipagem e estrutura de tokens
├── pyproject.toml             # Metadados do projeto e dependências
└── README.md
```

---

## Como Executar

Para avaliar o analisador sem a necessidade de instalar dependências ou clonar o projeto localmente:

🔗 **[https://tontoc-webrunner.vercel.app/](https://tontoc-webrunner.vercel.app/)**

A versão web executa o núcleo do `tontoc` diretamente no navegador utilizando **WebAssembly (Pyodide)**. A interface disponibiliza editor de código com carregamento de exemplos pré-configurados, suporte a upload de arquivos `.tonto` e exibição instantânea dos relatórios da análise léxica.

---

## Saídas e Relatórios Gerados

A execução do `tontoc` organiza os dados inspecionados em até três seções:

### 1. Visão Analítica de Tokens
Lista tabular de cada unidade léxica reconhecida no fluxo de entrada, contendo suas coordenadas espaciais e tipagem:

```text
--- Visão Analítica dos Tokens ---

Line   Col    Token Type                 Lexeme/Value
------------------------------------------------------------
1      1      KW_PACKAGE                 package
1      9      CLASS_ID                   UniversidadeClass
3      1      ST_KIND                    kind
3      6      CLASS_ID                   PessoaClass
3      18     LBRACE                     {
4      5      RELATION_ID                nome
4      10     COLON                      :
4      12     TYPE_STRING                string
5      5      RELATION_ID                cpf
5      9      COLON                      :
5      11     CUSTOM_DATA_TYPE           CPFDataType
6      5      INSTANCE_ID                cadastro01
6      16     COLON                      :
6      18     TYPE_NUMBER                number
7      1      RBRACE                     }
```

### 2. Tabela de Síntese Estatística
Sumário quantitativo consolidado das categorias estruturais presentes no modelo ontológico:

```text
--- Tabela de Síntese Estatística ---

Categoria                                Quantidade
----------------------------------------------------
Classes (CLASS_ID)                       2         
Relações (RELATION_ID)                   2         
Palavras-chave / Estereótipos (ST_*)     1         
Indivíduos / Instâncias (INSTANCE_ID)    1         
Palavras reservadas (KW_*)               1         
Meta-atributos (META_*)                  0         
Tipos Nativos (TYPE_*)                   2         
Tipos Customizados (CUSTOM_DATA_TYPE)    1         
Erros Léxicos                            0         
```

### 3. Diagnóstico de Erros Contextual
Quando são detectadas violações léxicas ou caracteres ilegais, o analisador apresenta um diagnóstico enriquecido com localização precisa, visualização do código-fonte e sugestão de resolução:

```text
--- Lista de Erros e Sugestões ---

error: Identificador malformado 'Sistema'
  --> Linha 1, Coluna 9
   |
 1 | package Sistema
   |         ^^^^^^^
   = Sugestão: Identificadores de classe devem terminar com o sufixo 'Class'.

error: Caractere ilegal '$'
  --> Linha 4, Coluna 5
   |
 4 |     $salario : number
   |     ^

error: Tipo de dado customizado malformado 'CPF_DataType'
  --> Linha 5, Coluna 11
   |
 5 |     cpf : CPF_DataType
   |           ^^^^^^^^^^^^
   = Sugestão: Novos tipos (DataType) não podem conter sublinhados.
```

---

## Conjunto de Testes e Validação

Para assegurar a robustez do analisador, o repositório conta com três suítes de teste no diretório `examples/`:

- **`examples/valid/`**: Modelos construídos para verificar o reconhecimento de todas as classes de tokens da especificação (estereótipos ontológicos, tipos primitivos e customizados, gensets, relações mereológicas e instâncias).
- **`examples/invalid/`**: Casos de teste negativos cobrindo classes específicas de violação léxica:
  - `01_illegal_characters.tonto`: Caracteres fora do alfabeto da linguagem (`$`, `#`, `!`, `^`, etc.).
  - `02_invalid_identifiers.tonto`: Violação das convenções de identificadores (classes sem `Class`, relações com dígitos, sublinhados mal posicionados).
  - `03_invalid_datatypes.tonto`: Violação de regras para `*DataType` (presença de números ou sublinhados).
- **`examples/validation/`**: **Conjunto oficial de ontologias em TONTO disponibilizado para a avaliação do projeto**, cobrindo domínios reais:
  - `car-example/`: Modelos de locação e posse veicular.
  - `food-allergy-example/`: Ontologia de alergias e intolerâncias alimentares.
  - `hospital-model/`: Modelos modulares de gestão de saúde pública e versão monobloco consolidada (`src/monobloco/hospital.tonto`).
  - `ontology-design-patterns-em-tonto/`: Implementações de padrões de projeto ontológico (ODPs) canônicos (`mode`, `phase`, `relator`, `role`, `subkind`).
  - `pizzaria-model/`: Ontologia comercial de catálogo e pedidos, modular e em monobloco (`src/monobloco/pizzaria-mono.tonto`).
  - `tdah-example/`: Ontologia diagnóstica e terapêutica sobre TDAH.
