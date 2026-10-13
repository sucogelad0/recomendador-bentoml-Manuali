## Grupo
 - Gabriel Barbosa
 - Diogo Silas
 - Rafael Aimberê
 - Marcello Augusto
 - João Vinícius

# Origem — Módulo de Recomendação com IA

## 1. Descrição do projeto

Este projeto implementa um serviço de recomendação de produtos artesanais para o marketplace Origem, utilizando Python e BentoML.

O recomendador considera a técnica artesanal, a região e a ocorrência conjunta de produtos em cestas para sugerir itens relacionados ao produto visualizado pelo usuário.

O catálogo de teste contém 12 produtos artesanais fictícios, distribuídos entre diferentes técnicas e regiões.

## 2. Tecnologias utilizadas

- Python
- BentoML
- uv — gerenciamento de ambiente e dependências
- JSON — armazenamento dos dados sintéticos
- Pickle — armazenamento do artefato utilizado pelo serviço

## 3. Requisitos para execução

- Git
- Python compatível com as dependências do projeto
- uv instalado

## 4. Como instalar e executar

### 4.1. Clonar o repositório

Substitua `URL_DO_REPOSITORIO` pelo endereço real do repositório GitHub da squad.

```powershell
git clone URL_DO_REPOSITORIO
cd recomendador-bentoml
```

### 4.2. Instalar as dependências

```powershell
uv sync
```

O projeto deve incluir as dependências necessárias no arquivo `pyproject.toml` e manter o arquivo `uv.lock` versionado, caso tenha sido gerado.

### 4.3. Preparar e registrar o modelo

```powershell
uv run python treino.py
```

Esse comando carrega os dados e registra o modelo no BentoML.

### 4.4. Iniciar o serviço

```powershell
uv run bentoml serve service:Recomendador
```

Após a inicialização, o serviço fica disponível em:

`http://localhost:3000`

Mantenha o terminal do servidor aberto enquanto executa os testes.

## 5. Requisitos funcionais da AV1 e implementação

| Requisito funcional | Implementação no protótipo |
|---|---|
| Recomendar produtos artesanais relacionados ao produto visualizado | Endpoint `POST /recomendar`, considerando técnica, região e coocorrência em cestas |
| Recomendar produtos disponíveis | Filtro de estoque positivo no serviço |
| Não recomendar produtos de artesãos suspensos ou banidos | Verificação dos campos `status_artesao` ou `situacao_artesao`; depende da presença desses dados no artefato |
| Não favorecer anúncios patrocinados | A pontuação não utiliza patrocínio nem quantidade de pedidos |
| Permitir excluir produtos já vistos ou comprados | Parâmetro `excluir` do endpoint |
| Permitir controlar a quantidade de recomendações | Parâmetro `limite`, entre 1 e 12 |
| Tratar produto inexistente | Retorno `produto_inexistente` com lista vazia |
| Tratar limite inválido | Retorno `limite_invalido` com lista vazia |

### Endpoint principal

`POST /recomendar`

Parâmetros JSON:

- `produto_na_pagina`: identificador do produto visualizado.
- `limite`: quantidade de recomendações desejada, de 1 a 12.
- `excluir`: lista opcional de IDs que não devem aparecer na resposta.

Exemplo de entrada:

```json
{
  "produto_na_pagina": "p01",
  "limite": 4
}
```

A resposta contém a lista `items`, com identificador, nome, técnica, região, estoque, artesão, pontuação, justificativa e posição da recomendação.

## 6. Casos de teste

Os testes a seguir utilizam PowerShell e pressupõem que o serviço esteja ativo em `http://localhost:3000`.

### Teste 1 — Recomendação de produto existente

**Comando:**

```powershell
Invoke-RestMethod -Uri "http://localhost:3000/recomendar" -Method Post -ContentType "application/json" -Body '{"produto_na_pagina":"p01","limite":4}'
```

**Resultado esperado:**

- A resposta contém a lista `items`.
- São retornadas até quatro recomendações.
- O produto `p01` não aparece na lista.
- Os produtos recomendados possuem estoque positivo.
- A resposta informa a estratégia de recomendação utilizada.

**Resultado observado:** o teste retornou quatro produtos (`p02`, `p03`, `p10` e `p12`), todos com estoque positivo.

### Teste 2 — Produto inexistente

**Comando:**

```powershell
Invoke-RestMethod -Uri "http://localhost:3000/recomendar" -Method Post -ContentType "application/json" -Body '{"produto_na_pagina":"p99","limite":4}'
```

**Resultado esperado:**

```json
{
  "erro": "produto_inexistente",
  "produto_na_pagina": "p99",
  "items": []
}
```

**Resultado observado:** o serviço retornou `produto_inexistente`, o identificador `p99` e uma lista vazia.

### Teste 3 — Limite inválido

**Comando:**

```powershell
Invoke-RestMethod -Uri "http://localhost:3000/recomendar" -Method Post -ContentType "application/json" -Body '{"produto_na_pagina":"p01","limite":0}'
```

**Resultado esperado:**

```json
{
  "erro": "limite_invalido",
  "mensagem": "O limite deve estar entre 1 e 12.",
  "items": []
}
```

**Resultado observado:** o serviço retornou `limite_invalido`, a mensagem de validação e uma lista vazia.

## 7. Limitações do protótipo

- Os dados do catálogo são sintéticos e utilizados para demonstração.
- O serviço depende de um artefato de modelo previamente preparado e registrado no BentoML.
- A exclusão de artesãos suspensos ou banidos depende da inclusão e validação do status nos dados utilizados pelo recomendador.
- O protótipo não implementa pagamentos, cadastro de produtos, comunicação direta entre comprador e vendedor, logística, rastreamento ou autenticação.
- Os casos de teste verificam o conteúdo das respostas, não códigos HTTP específicos como `400` ou `404`.

## 8. Reprodutibilidade

Para reproduzir o projeto do zero, clone o repositório, instale as dependências com `uv sync`, execute `treino.py` e inicie o serviço BentoML. Em seguida, execute os comandos de teste desta documentação.
=======
# recomendador-bentoml-Manuali
Projeto da materia de IA
>>>>>>> d22d9bd1a00fd833e903164256e7dfc9e3cbcdcc
