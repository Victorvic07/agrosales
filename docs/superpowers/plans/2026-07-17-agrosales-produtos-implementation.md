# Plano de Implementação do Módulo de Produtos — AgroSales

> **Para execução agentic:** usar `superpowers:subagent-driven-development` ou `superpowers:executing-plans` para implementar este plano tarefa por tarefa.

**Objetivo:** Evoluir o módulo de Produtos para suportar cadastro completo, filtros, paginação, status, exclusão protegida, upload de imagem e integração com o frontend Angular.

**Arquitetura:** FastAPI + SQLAlchemy assíncrono + PostgreSQL + Pydantic no backend e Angular standalone no frontend. O desenvolvimento será incremental, orientado por testes e com commits pequenos.

**Stack:** Python 3.12, FastAPI, SQLAlchemy Async, PostgreSQL, Alembic, Pydantic, Pillow, Angular 22, Angular Material e Vitest.

## Restrições globais

- Imagem principal de até 5 MB.
- Formatos aceitos: JPG, JPEG, PNG e WebP.
- Conversão final para WebP.
- Dimensão máxima de 1200 × 1200, preservando proporção.
- Nome do arquivo: código do produto + UUID.
- Categoria opcional.
- Código automático editável e único.
- Unidade fixa com opção `OUTRO`.
- Status: `ATIVO`, `INATIVO`, `DESCONTINUADO`.
- Exclusão definitiva somente sem vínculos operacionais.
- Exclusão definitiva restrita ao administrador.
- `backend/uploads/` fora do Git.
- Fora do escopo: galeria, planilha, código de barras e armazenamento externo.

---

## Tarefa 1: Corrigir a base técnica

**Arquivos:**
- Modificar: `backend/app/api/dependencies.py`
- Modificar: arquivos com textos UTF-8 corrompidos tocados nesta implementação

- [ ] Remover imports duplicados, especialmente `LotRepository`.
- [ ] Reorganizar imports conforme Ruff.
- [ ] Corrigir textos como `AutenticaÃ§Ã£o`, `UsuÃ¡rios` e `VocÃª`.
- [ ] Rodar:

```powershell
cd C:\Projetos\agrosales\backend
python -m ruff check app tests
python -m pytest
```

- [ ] Commit:

```powershell
git add backend/app
 git commit -m "chore: organiza dependências e textos do backend"
```

---

## Tarefa 2: Criar enums e expandir o modelo

**Arquivos:**
- Criar: `backend/app/modules/products/enums.py`
- Modificar: `backend/app/modules/products/model.py`
- Modificar: `backend/tests/test_product_models.py`

**Interfaces:**

```python
from enum import StrEnum

class ProductUnit(StrEnum):
    UNIDADE = "UNIDADE"
    QUILOGRAMA = "QUILOGRAMA"
    GRAMA = "GRAMA"
    LITRO = "LITRO"
    MILILITRO = "MILILITRO"
    CAIXA = "CAIXA"
    PACOTE = "PACOTE"
    OUTRO = "OUTRO"

class ProductStatus(StrEnum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    DESCONTINUADO = "DESCONTINUADO"
```

Campos novos de `Product`:

- `code: str`, único, indexado, até 50 caracteres;
- `category_id: UUID | None`;
- `unit: ProductUnit`;
- `custom_unit: str | None`;
- `cost_price: Decimal`;
- `standard_price: Decimal`;
- `minimum_price: Decimal`;
- `short_description: str | None`;
- `detailed_description: str | None`;
- `internal_notes: str | None`;
- `image_path: str | None`;
- `status: ProductStatus`.

- [ ] Escrever testes do modelo.
- [ ] Rodar os testes para confirmar falha.
- [ ] Implementar enums e modelo.
- [ ] Rodar:

```powershell
python -m pytest tests/test_product_models.py -v
```

- [ ] Commit:

```powershell
git add backend/app/modules/products backend/tests/test_product_models.py
git commit -m "feat: expande modelo de produtos"
```

---

## Tarefa 3: Criar migration `0011_expand_products.py`

**Arquivos:**
- Criar: `backend/app/migrations/versions/0011_expand_products.py`
- Modificar: `backend/tests/test_product_migration.py`

Regras:

- criar enums PostgreSQL `product_unit` e `product_status`;
- adicionar colunas novas;
- copiar `description` para `short_description`;
- converter `is_active=True` em `ATIVO` e `False` em `INATIVO`;
- tornar `category_id` opcional;
- gerar códigos únicos para registros existentes;
- criar índice e constraint única para `code`;
- remover colunas antigas após migração;
- implementar `downgrade`.

- [ ] Escrever teste da migration.
- [ ] Implementar migration.
- [ ] Rodar:

```powershell
python -m pytest tests/test_product_migration.py -v
python -m alembic upgrade head
python -m alembic current
```

- [ ] Commit:

```powershell
git add backend/app/migrations/versions/0011_expand_products.py backend/tests/test_product_migration.py
git commit -m "feat: cria migration do cadastro completo de produtos"
```

---

## Tarefa 4: Implementar schemas e validações

**Arquivos:**
- Modificar: `backend/app/modules/products/schemas.py`
- Criar: `backend/tests/test_product_schemas.py`

**Interfaces:**

```python
class ProductCreate(BaseModel): ...
class ProductUpdate(BaseModel): ...
class ProductStatusUpdate(BaseModel): ...
class ProductRead(BaseModel): ...
class ProductListItem(BaseModel): ...
class ProductPage(BaseModel): ...
```

Validações:

- nome entre 2 e 150 caracteres;
- código opcional no cadastro;
- preços não negativos;
- `minimum_price <= standard_price`;
- `custom_unit` obrigatório quando `unit == OUTRO`;
- `custom_unit` vazio nas unidades fixas;
- categoria opcional;
- strings normalizadas com `strip()`.

- [ ] Escrever testes.
- [ ] Confirmar falha.
- [ ] Implementar com `model_validator`.
- [ ] Rodar testes.
- [ ] Commit:

```powershell
git add backend/app/modules/products/schemas.py backend/tests/test_product_schemas.py
git commit -m "feat: adiciona schemas completos de produtos"
```

---

## Tarefa 5: Implementar geração automática de código

**Arquivos:**
- Criar: `backend/app/modules/products/code_generator.py`
- Modificar: `backend/app/modules/products/repository.py`
- Criar: `backend/tests/test_product_code_generator.py`

**Interface:**

```python
async def generate_product_code(repository: ProductRepository) -> str:
    ...
```

Formato: `PRD-000001`.

- [ ] Testar primeiro código, incremento e colisão.
- [ ] Implementar consulta do maior código gerado.
- [ ] Implementar tentativa controlada em colisão.
- [ ] Manter índice único no banco como garantia final.
- [ ] Commit:

```powershell
git add backend/app/modules/products backend/tests/test_product_code_generator.py
git commit -m "feat: gera código automático de produto"
```

---

## Tarefa 6: Evoluir repository com CRUD, filtros e paginação

**Arquivo:** `backend/app/modules/products/repository.py`

**Interfaces:**

```python
async def get_by_code(self, code: str) -> Product | None: ...
async def list_page(
    self,
    *,
    search: str | None,
    category_id: UUID | None,
    unit: ProductUnit | None,
    status: ProductStatus | None,
    page: int,
    page_size: int,
) -> tuple[list[Product], int]: ...
async def create(self, data: ProductCreate, code: str) -> Product: ...
async def update(self, product: Product, data: ProductUpdate) -> Product: ...
async def delete(self, product: Product) -> None: ...
async def has_operational_links(self, product_id: UUID) -> bool: ...
```

Vínculos a verificar:

- variações;
- lotes vinculados às variações;
- movimentos vinculados aos lotes;
- reservas vinculadas aos lotes;
- itens de pedidos vinculados às variações.

- [ ] Escrever testes de repository.
- [ ] Implementar busca por código ou nome.
- [ ] Implementar filtros e paginação.
- [ ] Implementar `exists` para vínculos.
- [ ] Commit:

```powershell
git add backend/app/modules/products/repository.py backend/tests
git commit -m "feat: adiciona filtros e persistência completa de produtos"
```

---

## Tarefa 7: Implementar regras no service

**Arquivo:** `backend/app/modules/products/service.py`

**Exceções:**

```python
class ProductNotFoundError(Exception): ...
class CategoryNotFoundError(Exception): ...
class ProductCodeAlreadyExistsError(Exception): ...
class ProductHasLinksError(Exception): ...
```

**Métodos:**

```python
async def create(self, data: ProductCreate) -> Product: ...
async def update(self, product_id: UUID, data: ProductUpdate) -> Product: ...
async def change_status(self, product_id: UUID, data: ProductStatusUpdate) -> Product: ...
async def delete(self, product_id: UUID) -> str | None: ...
```

Regras:

- categoria `None` aceita;
- categoria informada deve existir e estar ativa;
- código manual deve ser único;
- código automático quando ausente;
- exclusão com vínculos retorna conflito;
- exclusão devolve `image_path` para remoção física;
- status pode transitar entre os três valores.

- [ ] Escrever testes unitários.
- [ ] Implementar o mínimo para passar.
- [ ] Commit:

```powershell
git add backend/app/modules/products/service.py backend/tests/test_product_service.py
git commit -m "feat: implementa regras de negócio de produtos"
```

---

## Tarefa 8: Implementar endpoints CRUD e status

**Arquivos:**
- Modificar: `backend/app/api/routers/products.py`
- Modificar: `backend/tests/test_products_api.py`
- Criar: `backend/tests/test_product_crud_api.py`

Endpoints:

```text
GET    /api/v1/products
GET    /api/v1/products/{product_id}
POST   /api/v1/products
PATCH  /api/v1/products/{product_id}
PATCH  /api/v1/products/{product_id}/status
DELETE /api/v1/products/{product_id}
```

Permissões:

- listar/consultar: ADMINISTRADOR, PRODUTOR, VENDEDOR;
- criar/editar/status: ADMINISTRADOR, PRODUTOR;
- excluir: ADMINISTRADOR.

Códigos HTTP:

- 200 consulta/edição/status;
- 201 criação;
- 204 exclusão;
- 404 produto/categoria inexistente;
- 409 código duplicado ou produto vinculado;
- 422 dados inválidos.

- [ ] Atualizar testes legados.
- [ ] Criar novos testes de rota.
- [ ] Implementar rotas.
- [ ] Rodar:

```powershell
python -m pytest tests/test_products_api.py tests/test_product_crud_api.py -v
```

- [ ] Commit:

```powershell
git add backend/app/api/routers/products.py backend/tests
git commit -m "feat: adiciona CRUD completo de produtos"
```

---

## Tarefa 9: Configurar uploads e arquivos estáticos

**Arquivos:**
- Modificar: `backend/app/core/config.py`
- Modificar: `backend/app/main.py`
- Modificar: `backend/pyproject.toml`
- Modificar: `.env.example`
- Modificar: `.gitignore`

Configurações:

```python
uploads_dir: str = Field(default="uploads", alias="UPLOADS_DIR")
product_image_max_bytes: int = Field(
    default=5 * 1024 * 1024,
    alias="PRODUCT_IMAGE_MAX_BYTES",
)
```

Dependências:

```toml
"Pillow>=11,<12"
"python-multipart>=0.0.20,<1.0"
```

Montagem estática:

```python
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
```

- [ ] Criar diretório em runtime.
- [ ] Adicionar `backend/uploads/` ao `.gitignore`.
- [ ] Testar configuração.
- [ ] Commit:

```powershell
git add backend/app/core/config.py backend/app/main.py backend/pyproject.toml .env.example .gitignore
git commit -m "feat: configura armazenamento local de imagens"
```

---

## Tarefa 10: Implementar processamento de imagem

**Arquivos:**
- Criar: `backend/app/modules/products/image_service.py`
- Criar: `backend/tests/test_product_image_service.py`

**Interfaces:**

```python
class InvalidProductImageError(Exception): ...
class ProductImageTooLargeError(Exception): ...

async def save_product_image(
    *,
    upload: UploadFile,
    product_code: str,
    uploads_dir: Path,
    max_bytes: int,
) -> str: ...

def delete_product_image(*, relative_path: str, uploads_dir: Path) -> None: ...
```

Regras:

- ler no máximo `max_bytes + 1`;
- validar com Pillow;
- aceitar JPEG, PNG e WebP;
- usar `ImageOps.exif_transpose`;
- redimensionar com `thumbnail((1200, 1200))`;
- salvar WebP;
- nome `CODIGO_UUID.webp`;
- impedir path traversal;
- apagar arquivo parcial em falha.

- [ ] Testar arquivo válido, inválido, limite, redimensionamento e WebP.
- [ ] Implementar.
- [ ] Commit:

```powershell
git add backend/app/modules/products/image_service.py backend/tests/test_product_image_service.py
git commit -m "feat: processa imagens de produtos"
```

---

## Tarefa 11: Implementar endpoints de imagem

Endpoints:

```text
POST   /api/v1/products/{product_id}/image
DELETE /api/v1/products/{product_id}/image
```

Fluxo de substituição:

1. carregar produto;
2. salvar imagem nova;
3. atualizar `image_path`;
4. confirmar transação;
5. apagar imagem antiga;
6. em falha de banco, apagar imagem nova e preservar a antiga.

- [ ] Criar testes de upload, substituição e exclusão.
- [ ] Implementar rollback seguro.
- [ ] Commit:

```powershell
git add backend/app/api/routers/products.py backend/app/modules/products backend/tests
git commit -m "feat: adiciona upload de imagem aos produtos"
```

---

## Tarefa 12: Validar backend completo

```powershell
cd C:\Projetos\agrosales\backend
python -m ruff check app tests
python -m pytest
python -m alembic current
```

Testes manuais no Swagger:

- criar sem categoria;
- gerar código automático;
- editar preços;
- filtrar e paginar;
- alterar status;
- enviar e substituir imagem;
- tentar excluir produto vinculado.

---

## Tarefa 13: Criar modelos e service Angular

**Arquivos:**
- Criar: `frontend/src/app/features/products/models/product.models.ts`
- Criar: `frontend/src/app/features/products/services/products.service.ts`
- Criar testes correspondentes.

Service:

```typescript
list(filters: ProductFilters): Observable<ProductPage>
getById(id: string): Observable<Product>
create(data: ProductCreate): Observable<Product>
update(id: string, data: ProductUpdate): Observable<Product>
changeStatus(id: string, status: ProductStatus): Observable<Product>
delete(id: string): Observable<void>
uploadImage(id: string, file: File): Observable<Product>
deleteImage(id: string): Observable<Product>
```

- [ ] Escrever testes.
- [ ] Implementar.
- [ ] Rodar testes.
- [ ] Commit.

---

## Tarefa 14: Implementar listagem responsiva

**Arquivos:**
- Criar página `products-page`.
- Criar componente `product-card`.
- Modificar rota `/products`.

Comportamento:

- tabela no desktop;
- cards no celular;
- busca por código/nome;
- filtros categoria, unidade e status;
- paginação;
- loading, vazio e erro;
- botão Novo produto.

- [ ] Escrever testes.
- [ ] Implementar.
- [ ] Rodar testes e build.
- [ ] Commit.

---

## Tarefa 15: Implementar painel lateral de cadastro e edição

**Arquivo:** `product-form-drawer`.

Campos:

- imagem;
- código;
- nome;
- categoria;
- criação rápida de categoria;
- unidade;
- unidade personalizada;
- preços;
- descrições;
- observações;
- status.

- [ ] Escrever testes de validação.
- [ ] Implementar Reactive Forms.
- [ ] Integrar criação e edição.
- [ ] Integrar upload após salvar.
- [ ] Exibir preview.
- [ ] Commit.

---

## Tarefa 16: Implementar ações e confirmações

Ações:

- ativar;
- inativar;
- descontinuar;
- excluir;
- remover imagem.

- [ ] Criar diálogos de confirmação.
- [ ] Tratar erro 409 de exclusão.
- [ ] Atualizar listagem após ação.
- [ ] Escrever testes.
- [ ] Rodar testes e build.
- [ ] Commit.

---

## Tarefa 17: Verificação final

Backend:

```powershell
cd C:\Projetos\agrosales\backend
python -m ruff check app tests
python -m pytest
python -m alembic current
```

Frontend:

```powershell
cd C:\Projetos\agrosales\frontend
npm test -- --watch=false
npm run build
```

Git:

```powershell
cd C:\Projetos\agrosales
git status
git --no-pager log --oneline -15
```

Critérios de aceite:

- todos os testes passam;
- build Angular passa;
- migration aplicada;
- upload gera WebP;
- CRUD completo;
- filtros e paginação funcionam;
- listagem responsiva;
- exclusão protegida;
- permissões respeitadas;
- working tree limpa.
