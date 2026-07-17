@'
# Design do módulo de Produtos — AgroSales

## 1. Objetivo

Substituir o placeholder atual de Produtos por um módulo completo, integrado ao backend FastAPI e ao frontend Angular.

O módulo permitirá cadastrar, consultar, editar, alterar o status e excluir produtos, respeitando vínculos com estoque, lotes e pedidos.

## 2. Estratégia de implementação

O desenvolvimento será feito de ponta a ponta, com backend e frontend evoluindo em etapas.

### Etapa 1 — Backend sem imagem

- alteração do modelo e banco de dados;
- migration Alembic;
- schemas de entrada e saída;
- regras de negócio;
- repository e service;
- endpoints de CRUD;
- filtros, busca e paginação;
- testes automatizados.

### Etapa 2 — Imagem do produto

- upload da imagem principal;
- validação de formato e tamanho;
- processamento e conversão para WebP;
- substituição segura da imagem;
- disponibilização do arquivo pela API;
- testes automatizados.

### Etapa 3 — Frontend

- listagem em tabela no desktop;
- cards no celular;
- filtros e busca;
- painel lateral de cadastro e edição;
- upload e visualização da imagem;
- criação rápida de categoria;
- ações de status e exclusão;
- integração com a API.

## 3. Dados do produto

O produto terá:

- identificador UUID;
- código;
- nome;
- categoria opcional;
- unidade de medida;
- unidade personalizada, quando utilizada a opção `OUTRO`;
- preço de custo;
- preço padrão de venda;
- preço mínimo permitido;
- descrição curta;
- descrição detalhada;
- observações internas;
- caminho da imagem principal;
- status;
- data de criação;
- data da última atualização.

## 4. Código do produto

O backend gerará automaticamente um código para novos produtos.

Formato:

```text
PRD-000001