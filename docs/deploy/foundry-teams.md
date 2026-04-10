# Deploy — Microsoft Teams via Azure AI Foundry

Guia para publicar o mcp-brasil como agente no Microsoft Teams usando o
Azure AI Foundry Agent Service com MCPTool.

## Arquitetura

```
Usuários Teams
    │
    ▼
Microsoft Teams (chat)
    │
    ▼
Azure AI Foundry Agent Service (gpt-4o / gpt-5.4-mini)
    │  MCPTool (streamable-HTTP)
    ▼
mcp-brasil Container App  ← auth via Connection
    │
    ▼
41 APIs governamentais brasileiras
```

## Pré-requisitos

| Recurso | Detalhe |
|---------|---------|
| mcp-brasil | Container App rodando com `AUTH_MODE=oauth` (ver [azure-oauth.md](azure-oauth.md)) |
| AI Services | Recurso Azure AI Services (S0) com modelo deployado (gpt-4o ou gpt-5.4-mini) |
| AI Project | Projeto no Azure AI Foundry ligado ao AI Services |
| Azure CLI | `az login` autenticado com permissão no projeto |
| Python deps | `uv sync --group foundry` |

## 1. Criar Connection para o MCP Server

No [Azure AI Foundry Portal](https://ai.azure.com):

1. Abra o projeto (ex: `agent-brasil`)
2. **Management Center** → **Connected resources** → **+ New connection**
3. Selecione **Custom keys**
4. Configure:
   - **Name:** `mcp-brasil`
   - **Access:** adicione a chave:
     - Key name: `Authorization`
     - Key value: `Bearer <MCP_BRASIL_API_TOKEN>` (ou configure OAuth
       client credentials se o server usa `AUTH_MODE=oauth`)
   - **Target:** `https://mcp-brasil.purplepond-78f67485.eastus2.azurecontainerapps.io/mcp`
5. Clique **Save**

> **Nota sobre OAuth:** Se o mcp-brasil usa `AUTH_MODE=oauth`, o MCPTool
> pode precisar de um token obtido via client credentials flow do App
> Registration. Nesse caso, use o `client_id` e `client_secret` do App
> Registration para obter um token e coloque como valor do header
> `Authorization`. Alternativamente, configure `AUTH_MODE=static` com
> `MCP_BRASIL_API_TOKEN` para simplificar.

## 2. Criar o Agente via Script

```bash
# Instalar dependências
uv sync --group foundry

# Variáveis (ajuste conforme seu ambiente)
export PROJECT_ENDPOINT="https://agent-brasil-resource.services.ai.azure.com/api/projects/agent-brasil"
export MODEL_DEPLOYMENT="gpt-4o"
export MCP_BRASIL_URL="https://mcp-brasil.purplepond-78f67485.eastus2.azurecontainerapps.io/mcp"
export MCP_CONNECTION_ID="mcp-brasil"  # nome da connection criada no passo 1

# Criar agente
python scripts/foundry_agent.py create
```

Output esperado:

```
Agent created: name=agente-brasil, version=1, id=agent_xxx
```

### Alternativa: Criar pelo Portal

1. Foundry Portal → projeto → **Agents** → **+ New agent**
2. Nome: `Agente Brasil`
3. Modelo: `gpt-4o`
4. Instructions: cole o system prompt de `scripts/foundry_agent.py`
5. Tools → **+ Add tool** → **MCP**
6. Configure:
   - Server label: `mcp-brasil`
   - Server URL: `https://mcp-brasil.purplepond-78f67485.eastus2.azurecontainerapps.io/mcp`
   - Connection: selecione `mcp-brasil` (criada no passo 1)
   - Require approval: `Never` (todas as tools são read-only)
7. Clique **Save**

## 3. Testar no Playground

No Foundry Portal → Agents → selecione `agente-brasil` → **Playground**.

Teste com perguntas como:

- "Qual a taxa Selic atual?"
- "Quais são as 10 maiores cidades do Brasil por população?"
- "Quais projetos de lei foram votados esta semana na Câmara?"

Ou via script:

```bash
python scripts/foundry_agent.py test --question "Qual a taxa Selic atual?"
```

## 4. Publicar no Teams

1. No Playground do agente, clique **Publish** (canto superior direito)
2. Selecione **Microsoft Teams**
3. Configure:
   - **App name:** `Agente Brasil`
   - **Description:** `Consulte dados governamentais brasileiros — IBGE, Banco Central, Câmara, Senado, Transparência e mais.`
   - **Icon:** use `docs/logo.png` do repositório
4. Clique **Publish**

## 5. Aprovação no M365 Admin Center

Após publicar, um admin do M365 precisa aprovar:

1. [M365 Admin Center](https://admin.microsoft.com) → **Settings** → **Integrated apps**
   (ou **Teams apps** → **Manage apps**)
2. Encontre `Agente Brasil` na lista de apps pendentes
3. Clique **Approve** → defina quem pode usar (todos ou grupos específicos)
4. Aguarde propagação (~1-2 horas)

## 6. Testar no Teams

1. Abra o Microsoft Teams
2. Pesquise por "Agente Brasil" na barra de busca
3. Inicie uma conversa
4. Envie: "Qual a taxa Selic atual?"
5. Verifique que a resposta contém dados reais do Banco Central

### Verificar logs

```bash
az containerapp logs show -n mcp-brasil -g rg-mcp-brasil --tail 30
```

## Troubleshooting

### Agente não encontra tools do MCP

- Verifique que a Connection está configurada corretamente (URL e auth)
- Verifique que o mcp-brasil está respondendo: `curl -sS https://mcp-brasil.../mcp`
- Se usa `code_mode`, o agente precisa chamar `search_tools` antes de usar
  tools específicas — isso é esperado

### Timeout nas respostas

- MCPTool tem timeout de 100s para chamadas não-streaming
- Se uma consulta demora mais, considere configurar scaling rules no
  Container App

### Token expirado na Connection

- Tokens estáticos não expiram, mas client credentials tokens sim
- Atualize o token na Connection periodicamente ou use Managed Identity
  (quando disponível)

### Rate limiting

Se muitos usuários usarem simultaneamente no Teams:

```bash
# Verificar e ajustar scaling
az containerapp update -n mcp-brasil -g rg-mcp-brasil \
  --min-replicas 1 --max-replicas 5
```

## Custos

| Componente | Custo |
|------------|-------|
| Foundry Agent Service | Gratuito (sem custo adicional) |
| GPT-4o | ~$2.50/1M input, ~$10/1M output |
| GPT-5.4-mini | ~$0.40/1M input, ~$1.60/1M output |
| Container App | Consumption plan (~$0.000016/vCPU-s) |

Para POC, recomenda-se `gpt-5.4-mini` para reduzir custos.

## Cleanup

```bash
# Deletar agente do Foundry
python scripts/foundry_agent.py delete

# A Connection e o Container App continuam existindo
```
