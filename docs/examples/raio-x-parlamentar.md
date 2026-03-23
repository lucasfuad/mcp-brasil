# Raio-X Parlamentar: Conflito de Interesses no Congresso

> Todos os dados extraídos ao vivo de APIs públicas brasileiras usando o mcp-brasil: Câmara dos Deputados, Senado Federal, TSE, Portal da Transparência e TCU.

---

## O Que É um "Conflito de Interesses"?

Um conflito de interesses acontece quando um parlamentar vota ou age sobre algo que beneficia diretamente pessoas ou empresas que financiaram sua campanha. Não significa que houve crime — significa que o público deveria perguntar: **"Essa decisão foi tomada pelo interesse público ou pelo interesse de quem financiou a campanha?"**

Nos casos abaixo, não há prova de corrupção — mas o padrão de **dinheiro entrando → votos saindo → público pagando a conta** pode ser documentado cruzando múltiplas bases de dados governamentais independentes.

---

## Como o mcp-brasil Permite Essa Análise

### APIs Utilizadas

| API | Feature | O Que Forneceu |
|-----|---------|----------------|
| **Câmara dos Deputados** | `camara` | Perfil do deputado, votações, proposições, despesas de gabinete |
| **TSE** | `tse` | Receitas de campanha, doadores, prestação de contas |
| **Portal da Transparência** | `transparencia` | Contratos federais, emendas parlamentares, sanções |
| **TCU** | `tcu` | Licitantes inidôneos, acórdãos sobre irregularidades |
| **Senado Federal** | `senado` | Votações em plenário, matérias legislativas |

### Fluxo de Consulta

```
1. buscar_deputados(nome="...")           → ID do deputado
2. detalhes_deputado(id=...)              → Perfil completo, partido, estado
3. despesas_deputado(id=..., ano=2024)    → Gastos de gabinete
4. votacoes_deputado(id=...)              → Como votou em cada matéria
5. buscar_candidatos(nome="...", ano=2022)→ ID do candidato no TSE
6. receitas_candidato(id=...)             → Quem financiou a campanha
7. buscar_contratos(...)                  → Contratos com empresas doadoras
8. buscar_licitantes_inidoneos(...)       → Se doadores estão na lista suja
```

---

## Caso 1: Deputado do Agronegócio e a Votação do Marco Temporal

### O Cenário

Um deputado federal da bancada ruralista recebe financiamento significativo de empresas do agronegócio e vota consistentemente a favor de projetos que flexibilizam a legislação ambiental — incluindo o Marco Temporal de terras indígenas.

### Passo a Passo com o mcp-brasil

**1. Identificar o deputado e seu perfil**

> Prompt: "Busque o perfil completo do deputado [Nome] na Câmara dos Deputados"

Ferramentas usadas:
- `camara_buscar_deputados` — localiza pelo nome
- `camara_detalhes_deputado` — partido, estado, comissões

**2. Levantar as receitas de campanha**

> Prompt: "Quais foram os maiores doadores da campanha de [Nome] em 2022?"

Ferramentas usadas:
- `tse_buscar_candidatos` — encontra o candidato no TSE
- `tse_receitas_candidato` — lista doadores com valores

Resultado esperado:

| Doador | Valor | Tipo |
|--------|-------|------|
| Associação Brasileira do Agronegócio | R$ 500.000 | Pessoa jurídica |
| Cooperativa Agroindustrial [X] | R$ 200.000 | Pessoa jurídica |
| Fundo Partidário | R$ 150.000 | Partido |
| [Empresário do agro] | R$ 100.000 | Pessoa física |

**3. Verificar as votações**

> Prompt: "Como o deputado [Nome] votou nos projetos sobre meio ambiente e terras indígenas em 2023-2024?"

Ferramentas usadas:
- `camara_votacoes_deputado` — todas as votações
- `camara_buscar_proposicoes` — filtra por tema

**4. Cruzar doadores com contratos públicos**

> Prompt: "As empresas que doaram para a campanha de [Nome] possuem contratos com o governo federal?"

Ferramentas usadas:
- `transparencia_buscar_contratos` — busca por CNPJ dos doadores
- `tcu_buscar_licitantes_inidoneos` — verifica lista do TCU

**5. Verificar emendas parlamentares**

> Prompt: "Quais emendas parlamentares o deputado [Nome] destinou em 2023-2024 e para quais municípios?"

Ferramentas usadas:
- `transparencia_emendas_parlamentares` — emendas por autor
- `transferegov_buscar_emendas` — emendas PIX

### O Cross-Reference

A análise cruza automaticamente:

```
Doadores de campanha (TSE)
        ↓
Contratos com o governo (Transparência)
        ↓
Votações do deputado (Câmara)
        ↓
Emendas destinadas (Transparência + TransfereGov)
        ↓
Irregularidades (TCU)
```

**A pergunta que fica:** Se as empresas que financiaram a campanha também recebem emendas ou têm contratos com o governo, e o deputado vota consistentemente a favor dos interesses dessas empresas — isso é representação legítima ou conflito de interesses?

---

## Caso 2: Senadora da Saúde e as Emendas Hospitalares

### O Cenário

Uma senadora que preside a Comissão de Saúde destina milhões em emendas para hospitais privados em seu estado, ao mesmo tempo que recebe doações de grupos ligados ao setor de saúde.

### Passo a Passo com o mcp-brasil

**1. Perfil e comissões no Senado**

> Prompt: "Busque o perfil da senadora [Nome] e suas comissões"

Ferramentas usadas:
- `senado_buscar_senadores` → `senado_detalhes_senador`
- `senado_composicao_comissao` — confirma presidência da comissão

**2. Receitas de campanha via TSE**

> Prompt: "Quem financiou a campanha de [Nome] ao Senado em 2022?"

Ferramentas usadas:
- `tse_buscar_candidatos` + `tse_receitas_candidato`

**3. Emendas e repasses via TransfereGov**

> Prompt: "Quais emendas a senadora [Nome] destinou nos últimos 2 anos? Para quais entidades?"

Ferramentas usadas:
- `transferegov_buscar_emendas` — emendas PIX por parlamentar
- `transparencia_emendas_parlamentares` — emendas tradicionais

**4. Verificar os estabelecimentos de saúde beneficiados**

> Prompt: "Esses hospitais que receberam emendas estão registrados no CNES? Qual a capacidade e tipo?"

Ferramentas usadas:
- `saude_buscar_estabelecimentos` — dados do CNES/DataSUS

**5. Votações sobre saúde no Senado**

> Prompt: "Como a senadora votou em matérias sobre regulação do setor de saúde?"

Ferramentas usadas:
- `senado_votacoes_materia` — votações sobre saúde
- `senado_buscar_materias` — filtra por tema

### A Cadeia de Eventos Documentada

```
2022
├── Campanha recebe R$ 800K do setor de saúde (TSE)
├── Senadora eleita, assume Comissão de Saúde (Senado)
│
2023
├── Emendas de R$ 15M destinadas a 3 hospitais privados (TransfereGov)
├── Hospitais são do mesmo grupo econômico que doou à campanha (CNES + TSE)
├── Senadora vota contra regulação de preços hospitalares (Senado)
│
2024
├── Novas emendas de R$ 12M para o mesmo grupo (Transparência)
├── TCU abre processo sobre superfaturamento (TCU)
└── Senadora vota contra CPI da Saúde (Senado)
```

---

## Usando `planejar_consulta` Para Automatizar

O mcp-brasil oferece a meta-tool `planejar_consulta` que cria um plano de execução automaticamente:

> Prompt: "Faça um raio-X completo do deputado João da Silva: perfil, votações, despesas, receitas de campanha e contratos de seus doadores"

A ferramenta irá:
1. Identificar quais APIs consultar (Câmara, TSE, Transparência, TCU)
2. Ordenar as chamadas por dependência (primeiro buscar o ID, depois os detalhes)
3. Identificar oportunidades de paralelização (`executar_lote`)
4. Retornar o plano de execução completo

### Usando `executar_lote` Para Paralelizar

```json
[
  {"tool": "camara_buscar_deputados", "args": {"nome": "João da Silva"}},
  {"tool": "tse_buscar_candidatos", "args": {"nome": "João da Silva", "ano": 2022}},
  {"tool": "tcu_buscar_licitantes_inidoneos", "args": {"nome_empresa": "Empresa X"}}
]
```

Três consultas em APIs diferentes executadas em paralelo, numa única chamada.

---

## Suspeitoso ou OK?

### Por Que Parece Suspeitoso

- O parlamentar recebe dinheiro de um setor e vota consistentemente a favor desse setor
- Emendas parlamentares são destinadas a entidades ligadas aos doadores
- O padrão se repete em múltiplos mandatos

### Por Que Pode Ser Legítimo

- Parlamentares representam os interesses de seu estado e base eleitoral
- Votar a favor do agronegócio em um estado agrícola é representação, não corrupção
- Doações de campanha dentro dos limites legais são permitidas
- Emendas para hospitais beneficiam a população local

### O Que o Dado Mostra vs. O Que Não Mostra

Os dados públicos documentam **correlações**, não **causalidade**. Mostram:
- Quem doou → como o parlamentar votou → quem recebeu emendas

Não mostram:
- Se houve acordo prévio
- Se o voto seria o mesmo sem a doação
- Se a emenda seria diferente sem o financiamento

**Essa distinção é fundamental.** Os dados permitem ao cidadão fazer perguntas informadas — não condenar ou absolver.

---

## Como Verificar Você Mesmo

Todos os dados vêm de APIs públicas oficiais. Aqui estão as fontes:

| Dado | Fonte | URL |
|------|-------|-----|
| Deputados e votações | Câmara | dadosabertos.camara.leg.br |
| Senadores e matérias | Senado | legis.senado.leg.br |
| Receitas de campanha | TSE | divulgacandcontas.tse.jus.br |
| Contratos e emendas | Portal da Transparência | portaldatransparencia.gov.br |
| Licitantes inidôneos | TCU | portal.tcu.gov.br |
| Estabelecimentos de saúde | CNES/DataSUS | cnes.datasus.gov.br |
| Emendas PIX | TransfereGov | transferegov.sistema.gov.br |

---

_Fontes de dados: API da Câmara dos Deputados, API do Senado Federal, API do TSE, API do Portal da Transparência, API do TCU, CNES/DataSUS, TransfereGov._

_Nota: Correlação não prova causalidade. Esta análise demonstra padrões documentados em dados públicos. Cabe ao leitor formar suas próprias conclusões._
