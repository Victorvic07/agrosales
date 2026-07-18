# AgroSales Lotes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar o módulo completo de Lotes, com saldos auditáveis, movimentações, integração com Pedidos e interface Angular testada.

**Architecture:** Evoluir os módulos existentes de `inventory` sem migration. Repositórios apenas consultam/adicionam entidades; serviços concentram regras e transações; routers traduzem erros HTTP. No frontend, uma feature standalone segue o padrão de Produtos e Variações e combina lotes, produtos e variações no cliente.

**Tech Stack:** Python, FastAPI, SQLAlchemy assíncrono, Pydantic, PostgreSQL, Pytest, Angular 22, TypeScript 6, RxJS, Vitest e SCSS.

## Global Constraints

- Seguir TDD: teste vermelho, falha confirmada, implementação mínima e teste verde.
- Não criar migration: `lots.status` já é `String(30)` e aceita `ACTIVE`/`INACTIVE`.
- Somente `ADMINISTRADOR` e `PRODUTOR` acessam Lotes e Movimentações.
- Não permitir exclusão física, troca de variação ou edição direta de saldos.
- Toda alteração de saldo deve produzir uma movimentação.
- Cadastro com entrada inicial e conclusão de pedido devem usar uma única transação.
- Preservar as mudanças locais existentes de Variações; cada commit deve adicionar somente os caminhos da tarefa.
- Não usar `--run` nos testes Angular.
- Manter o padrão visual atual e não adicionar dependências.
- Preparar um ZIP final apenas com arquivos desta entrega.

---

## File Map

**Backend — modificar**

- `backend/app/modules/inventory/lot_model.py`: status operacional e propriedades calculadas.
- `backend/app/modules/inventory/lot_schemas.py`: contratos de criação, edição, status e leitura.
- `backend/app/modules/inventory/lot_repository.py`: consultas de conflito e histórico; persistência sem commit.
- `backend/app/modules/inventory/lot_service.py`: regras e transações de lote.
- `backend/app/api/routers/lots.py`: GET/POST/PUT/PATCH e erros HTTP.
- `backend/app/modules/inventory/movement_model.py`: nome do usuário para leitura.
- `backend/app/modules/inventory/movement_schemas.py`: validação condicional e histórico enriquecido.
- `backend/app/modules/inventory/movement_repository.py`: eager loading do usuário e busca por ID.
- `backend/app/modules/inventory/movement_service.py`: separar cálculo/adição de commit.
- `backend/app/api/routers/inventory_movements.py`: retorno enriquecido e bloqueio de venda manual.
- `backend/app/modules/orders/order_completion_service.py`: movimentação `SALE` atômica.

**Backend — testar**

- `backend/tests/test_lots.py`
- `backend/tests/test_lots_api.py`
- `backend/tests/test_inventory_movements.py`
- `backend/tests/test_inventory_movement_service.py`
- `backend/tests/test_inventory_movements_api.py`
- `backend/tests/test_order_completion_service.py`
- `backend/tests/test_order_completion_api.py`
- `backend/tests/test_reservation_repository.py`

**Frontend — criar**

- `frontend/src/app/features/lots/lot.models.ts`: contratos TypeScript.
- `frontend/src/app/features/lots/lot.service.ts`: chamadas HTTP.
- `frontend/src/app/features/lots/lot.service.spec.ts`: contratos HTTP.
- `frontend/src/app/features/lots/lots.component.ts`: estado, formulários e ações.
- `frontend/src/app/features/lots/lots.component.html`: página, drawers e histórico.
- `frontend/src/app/features/lots/lots.component.scss`: layout responsivo.
- `frontend/src/app/features/lots/lots.component.spec.ts`: comportamento da tela.

**Frontend — modificar**

- `frontend/src/app/app.routes.ts`: trocar o placeholder por `LotsComponent`.

---

### Task 1: Status e contratos calculados do lote

**Files:**
- Modify: `backend/app/modules/inventory/lot_model.py`
- Modify: `backend/app/modules/inventory/lot_schemas.py`
- Test: `backend/tests/test_lots.py`

**Interfaces:**
- Produces: `LotStatus`, `ExpirationState`, `LotCreate`, `LotUpdate`, `LotStatusUpdate`, `LotRead`.
- Produces: `Lot.available_quantity` e `Lot.expiration_state`.

- [ ] **Step 1: Escrever testes vermelhos de contratos e validade**

Adicionar testes que construam `LotCreate` com `initial_quantity`, exijam motivo quando a quantidade for positiva, aceitem zero, rejeitem validade passada e verifiquem as quatro situações com `date.today()` e `timedelta`:

```python
def test_lot_create_requires_reason_for_initial_entry() -> None:
    with pytest.raises(ValidationError):
        LotCreate(
            product_variation_id=uuid4(), code="LOTE-001",
            production_date=date.today(),
            expiration_date=date.today() + timedelta(days=10),
            initial_quantity=Decimal("10"),
        )

def test_lot_reports_available_quantity_and_expiration_state() -> None:
    lot = Lot(
        product_variation_id=uuid4(), code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=30),
        physical_quantity=Decimal("100"), reserved_quantity=Decimal("25"),
    )
    assert lot.available_quantity == Decimal("75")
    assert lot.expiration_state == ExpirationState.EXPIRING_SOON
```

- [ ] **Step 2: Confirmar a falha**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_lots.py -v`

Expected: FAIL por ausência de `initial_quantity`, `ExpirationState` e novos schemas.

- [ ] **Step 3: Implementar os contratos mínimos**

Usar `StrEnum`; manter a coluna como string:

```python
class LotStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class ExpirationState(StrEnum):
    EXPIRED = "EXPIRED"
    EXPIRES_TODAY = "EXPIRES_TODAY"
    EXPIRING_SOON = "EXPIRING_SOON"
    REGULAR = "REGULAR"

@property
def expiration_state(self) -> ExpirationState:
    days = (self.expiration_date - date.today()).days
    if days < 0:
        return ExpirationState.EXPIRED
    if days == 0:
        return ExpirationState.EXPIRES_TODAY
    if days <= 30:
        return ExpirationState.EXPIRING_SOON
    return ExpirationState.REGULAR
```

Definir em `lot_schemas.py`:

```python
class LotCreate(BaseModel):
    product_variation_id: UUID
    code: str = Field(min_length=2, max_length=80)
    production_date: date
    expiration_date: date
    initial_quantity: Decimal = Field(default=0, ge=0)
    initial_entry_reason: str | None = Field(default=None, min_length=3, max_length=255)
    initial_entry_notes: str | None = None

class LotUpdate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    production_date: date
    expiration_date: date

class LotStatusUpdate(BaseModel):
    status: LotStatus

class LotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    product_variation_id: UUID
    code: str
    production_date: date
    expiration_date: date
    physical_quantity: Decimal
    reserved_quantity: Decimal
    available_quantity: Decimal
    status: str
    expiration_state: ExpirationState
    created_at: datetime
    updated_at: datetime
```

O `model_validator` compartilhado deve rejeitar validade anterior à produção, validade passada e quantidade positiva sem motivo não vazio.

- [ ] **Step 4: Confirmar o verde**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_lots.py -v`

Expected: PASS.

- [ ] **Step 5: Commit isolado**

```powershell
git add backend/app/modules/inventory/lot_model.py backend/app/modules/inventory/lot_schemas.py backend/tests/test_lots.py
git commit -m "feat: define contratos completos de lotes"
```

---

### Task 2: Movimentações reutilizáveis e histórico enriquecido

**Files:**
- Modify: `backend/app/modules/inventory/movement_model.py`
- Modify: `backend/app/modules/inventory/movement_schemas.py`
- Modify: `backend/app/modules/inventory/movement_repository.py`
- Modify: `backend/app/modules/inventory/movement_service.py`
- Modify: `backend/app/api/routers/inventory_movements.py`
- Test: `backend/tests/test_inventory_movements.py`
- Test: `backend/tests/test_inventory_movement_service.py`
- Test: `backend/tests/test_inventory_movements_api.py`

**Interfaces:**
- Produces: `InventoryMovementService.add_movement(...)` sem commit.
- Preserves: `register_movement(...)` com commit para endpoint independente.
- Produces: `InventoryMovementRepository.get_by_id()` e respostas com `created_at`, `user_name`.

- [ ] **Step 1: Escrever testes vermelhos**

Cobrir ajuste para saldo zero, rejeição de quantidade zero nos outros tipos, `add_movement` sem commit, retorno com nome/data e bloqueio de `SALE` manual:

```python
def test_adjustment_accepts_zero_as_final_balance() -> None:
    data = InventoryMovementCreate(
        lot_id=uuid4(), movement_type=MovementType.ADJUSTMENT,
        quantity=Decimal("0"), reason="Inventário físico",
    )
    assert data.quantity == Decimal("0")

@pytest.mark.asyncio
async def test_add_movement_does_not_commit() -> None:
    movement = service.add_movement(
        lot=lot, user_id=uuid4(), movement_type=MovementType.ENTRY,
        quantity=Decimal("5"), reason="Entrada complementar",
    )
    assert movement.new_balance == Decimal("105")
    session.commit.assert_not_called()
```

- [ ] **Step 2: Confirmar a falha**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_inventory_movements.py tests/test_inventory_movement_service.py tests/test_inventory_movements_api.py -v`

Expected: FAIL por ajuste zero inválido, ausência de `add_movement` e campos do histórico.

- [ ] **Step 3: Separar cálculo e commit**

Implementar:

```python
def add_movement(
    self, lot: Lot, user_id: UUID, movement_type: MovementType,
    quantity: Decimal, reason: str, notes: str | None = None,
) -> InventoryMovement:
    previous_balance = lot.physical_quantity
    if movement_type in {MovementType.ENTRY, MovementType.RETURN}:
        new_balance = previous_balance + quantity
    elif movement_type in {MovementType.SALE, MovementType.LOSS}:
        new_balance = previous_balance - quantity
    elif movement_type == MovementType.ADJUSTMENT:
        new_balance = quantity
    else:
        raise ValueError("Tipo de movimentação inválido")
    if new_balance < 0:
        raise InsufficientStockError("Quantidade insuficiente no lote")
    if new_balance < lot.reserved_quantity:
        raise InsufficientStockError("O saldo não pode ficar abaixo da quantidade reservada")
    lot.physical_quantity = new_balance
    movement = InventoryMovement(
        lot_id=lot.id, user_id=user_id, movement_type=movement_type,
        quantity=quantity, previous_balance=previous_balance,
        new_balance=new_balance, reason=reason, notes=notes,
    )
    self.session.add(movement)
    return movement
```

`register_movement` chama `add_movement`, executa um commit, refresh e retorna.

- [ ] **Step 4: Enriquecer leitura e impedir venda manual**

Adicionar `created_at` e `user_name` ao schema, propriedade `user_name` ao model, `selectinload(InventoryMovement.user)` nas listagens e `get_by_id`. No router, rejeitar `SALE` com HTTP 400 antes de chamar o serviço; após POST, recarregar pelo repository para obter o usuário.

- [ ] **Step 5: Confirmar o verde**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_inventory_movements.py tests/test_inventory_movement_service.py tests/test_inventory_movements_api.py -v`

Expected: PASS.

- [ ] **Step 6: Commit isolado**

```powershell
git add backend/app/modules/inventory/movement_model.py backend/app/modules/inventory/movement_schemas.py backend/app/modules/inventory/movement_repository.py backend/app/modules/inventory/movement_service.py backend/app/api/routers/inventory_movements.py backend/tests/test_inventory_movements.py backend/tests/test_inventory_movement_service.py backend/tests/test_inventory_movements_api.py
git commit -m "feat: torna movimentacoes de estoque auditaveis"
```

---

### Task 3: Serviço transacional e persistência de lotes

**Files:**
- Modify: `backend/app/modules/inventory/lot_repository.py`
- Modify: `backend/app/modules/inventory/lot_service.py`
- Test: `backend/tests/test_lots.py`

**Interfaces:**
- Consumes: `InventoryMovementService.add_movement`.
- Produces: `LotService.create(data, user_id)`, `get`, `update`, `change_status`.
- Produces: `LotRepository.has_blocking_history(lot_id)`.

- [ ] **Step 1: Escrever testes vermelhos do serviço**

Testar criação com zero, criação com `ENTRY`, um commit, rollback, conflito de código, edição bloqueada, inativação com reserva e reativação vencida/esgotada. Usar `MagicMock` para sessão e `AsyncMock` para repositories.

```python
@pytest.mark.asyncio
async def test_create_lot_and_initial_entry_in_one_transaction() -> None:
    result = await service.create(data, user_id)
    assert result.physical_quantity == Decimal("100")
    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()
    movement_service.add_movement.assert_called_once()

@pytest.mark.asyncio
async def test_create_rolls_back_when_entry_fails() -> None:
    movement_service.add_movement.side_effect = RuntimeError("failure")
    with pytest.raises(RuntimeError):
        await service.create(data, user_id)
    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
```

- [ ] **Step 2: Confirmar a falha**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_lots.py -v`

Expected: FAIL porque repository ainda commita e o service não possui as operações.

- [ ] **Step 3: Tornar repository livre de commit**

Criar `add(lot)`, `refresh(lot)`, `get_by_code_excluding_id`, `has_blocking_history`. Esta última retorna verdadeiro se houver qualquer reserva ou se as movimentações não forem exatamente zero registros ou uma única `ENTRY`.

- [ ] **Step 4: Implementar o serviço mínimo**

O construtor recebe `session`, `lot_repository`, `variation_repository` e `movement_service`. `create` valida variação ativa, código e datas, adiciona lote com saldos zero, executa `flush`, adiciona `ENTRY` se necessário e então faz um único commit/refresh. `update` valida histórico e conflito. `change_status` aplica os bloqueios aprovados. Todos envolvem `try/except` com rollback.

- [ ] **Step 5: Confirmar o verde**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_lots.py -v`

Expected: PASS.

- [ ] **Step 6: Commit isolado**

```powershell
git add backend/app/modules/inventory/lot_repository.py backend/app/modules/inventory/lot_service.py backend/tests/test_lots.py
git commit -m "feat: implementa regras transacionais de lotes"
```

---

### Task 4: API completa de lotes e permissões

**Files:**
- Modify: `backend/app/api/routers/lots.py`
- Test: `backend/tests/test_lots_api.py`

**Interfaces:**
- Consumes: schemas e métodos do `LotService` das Tasks 1 e 3.
- Produces: GET coleção/ID, POST, PUT e PATCH status.

- [ ] **Step 1: Escrever testes vermelhos dos endpoints**

Cobrir retorno enriquecido, 404 por ID, POST com usuário, PUT, PATCH, mapeamento 409/422 e Vendedor recebendo 403 também no GET.

```python
def test_vendor_cannot_list_lots(client) -> None:
    app.dependency_overrides[get_current_user] = lambda: vendor
    response = client.get("/api/v1/lots")
    app.dependency_overrides.clear()
    assert response.status_code == 403

def test_producer_updates_lot_status(client) -> None:
    response = client.patch(
        f"/api/v1/lots/{lot.id}/status", json={"status": "INACTIVE"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "INACTIVE"
```

- [ ] **Step 2: Confirmar a falha**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_lots_api.py -v`

Expected: FAIL nos novos endpoints, campos e permissão de consulta.

- [ ] **Step 3: Implementar router**

Injetar `AsyncSession` e `current_user`, construir o service em helper local e restringir todas as rotas a Administrador/Produtor. Mapear inexistência para 404, conflito/edição bloqueada para 409 e regra de validade/saldo para 422.

- [ ] **Step 4: Confirmar o verde e regressão do backend de estoque**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_lots_api.py tests/test_stock_reservations.py tests/test_stock_reservations_api.py tests/test_fefo_reservation_service.py -v`

Expected: PASS.

- [ ] **Step 5: Commit isolado**

```powershell
git add backend/app/api/routers/lots.py backend/tests/test_lots_api.py
git commit -m "feat: completa api de lotes"
```

---

### Task 5: Venda auditável na conclusão do pedido

**Files:**
- Modify: `backend/app/modules/orders/order_completion_service.py`
- Modify: `backend/app/api/routers/orders.py`
- Test: `backend/tests/test_order_completion_service.py`
- Test: `backend/tests/test_order_completion_api.py`

**Interfaces:**
- Consumes: `InventoryMovementService.add_movement`.
- Preserves: `OrderCompletionService.complete(order_id, changed_by_user_id)`.

- [ ] **Step 1: Escrever teste vermelho de movimentação SALE**

```python
@pytest.mark.asyncio
async def test_completion_adds_sale_movement_before_single_commit() -> None:
    result = await service.complete(order.id, changed_by_user_id=user_id)
    assert result.status == OrderStatus.COMPLETED
    movement_service.add_movement.assert_called_once_with(
        lot=lot, user_id=user_id, movement_type=MovementType.SALE,
        quantity=reservation.quantity,
        reason=f"Baixa do pedido {order.id}", notes=None,
    )
    session.commit.assert_awaited_once()
```

Adicionar teste de exceção em `add_movement` confirmando rollback e nenhum commit.

- [ ] **Step 2: Confirmar a falha**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_order_completion_service.py tests/test_order_completion_api.py -v`

Expected: FAIL porque a conclusão altera o saldo diretamente.

- [ ] **Step 3: Integrar sem commit intermediário**

Injetar ou construir `InventoryMovementService(session)`. Para cada reserva validada, primeiro reduzir `reserved_quantity`, depois chamar `add_movement` com `SALE`; remover a subtração direta de `physical_quantity`. Exigir `changed_by_user_id` para a conclusão via API. Manter o único commit já existente no final.

- [ ] **Step 4: Confirmar o verde e regressão de pedidos**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_order_completion_service.py tests/test_order_completion_api.py tests/test_order_cancellation_service.py tests/test_order_confirmation_service.py -v`

Expected: PASS.

- [ ] **Step 5: Commit isolado**

```powershell
git add backend/app/modules/orders/order_completion_service.py backend/app/api/routers/orders.py backend/tests/test_order_completion_service.py backend/tests/test_order_completion_api.py
git commit -m "feat: registra venda ao concluir pedido"
```

---

### Task 6: Modelos e serviço HTTP do frontend

**Files:**
- Create: `frontend/src/app/features/lots/lot.models.ts`
- Create: `frontend/src/app/features/lots/lot.service.ts`
- Create: `frontend/src/app/features/lots/lot.service.spec.ts`

**Interfaces:**
- Produces: `Lot`, `LotCreate`, `LotUpdate`, `LotStatusUpdate`, `InventoryMovement`, `InventoryMovementCreate`.
- Produces: `LotService.list/get/create/update/updateStatus/listMovements/createMovement`.

- [ ] **Step 1: Escrever spec vermelho do serviço**

Testar métodos e URLs exatas com `HttpTestingController`, incluindo `GET /lots/{id}`, `PUT`, `PATCH /status`, `GET /inventory-movements?lot_id=...` e `POST /inventory-movements`.

- [ ] **Step 2: Confirmar a falha**

Run: `cd C:\Projetos\agrosales\frontend; npm test -- --include="src/app/features/lots/lot.service.spec.ts" --watch=false`

Expected: FAIL porque os arquivos ainda não existem.

- [ ] **Step 3: Criar contratos TypeScript**

Usar unions exatas:

```typescript
export type LotStatus = 'ACTIVE' | 'INACTIVE';
export type ExpirationState = 'EXPIRED' | 'EXPIRES_TODAY' | 'EXPIRING_SOON' | 'REGULAR';
export type MovementType = 'ENTRY' | 'SALE' | 'LOSS' | 'RETURN' | 'ADJUSTMENT';

export interface Lot {
  id: string; product_variation_id: string; code: string;
  production_date: string; expiration_date: string;
  physical_quantity: string; reserved_quantity: string;
  available_quantity: string; status: LotStatus;
  expiration_state: ExpirationState; created_at: string; updated_at: string;
}
```

Definir os payloads conforme o design; `LotUpdate` contém somente código e datas; `InventoryMovementCreate` não aceita `SALE` no tipo público da tela.

- [ ] **Step 4: Criar o serviço mínimo**

Usar `HttpClient`, `lotsUrl = '/api/v1/lots'` e `movementsUrl = '/api/v1/inventory-movements'`. Não transformar respostas nem duplicar regras do backend.

- [ ] **Step 5: Confirmar o verde e commit**

Run: `cd C:\Projetos\agrosales\frontend; npm test -- --include="src/app/features/lots/lot.service.spec.ts" --watch=false`

Expected: todos os testes do arquivo PASS.

```powershell
git add frontend/src/app/features/lots/lot.models.ts frontend/src/app/features/lots/lot.service.ts frontend/src/app/features/lots/lot.service.spec.ts
git commit -m "feat: adiciona cliente http de lotes"
```

---

### Task 7: Página, resumo, busca e filtros

**Files:**
- Create: `frontend/src/app/features/lots/lots.component.ts`
- Create: `frontend/src/app/features/lots/lots.component.html`
- Create: `frontend/src/app/features/lots/lots.component.scss`
- Create: `frontend/src/app/features/lots/lots.component.spec.ts`
- Modify: `frontend/src/app/app.routes.ts`

**Interfaces:**
- Consumes: `LotService`, `ProductService`, `ProductVariationService`.
- Produces: `LotsComponent` e rota `/lots` para `producerRoles`.

- [ ] **Step 1: Escrever testes vermelhos de leitura**

Testar `forkJoin` no início, loading/erro/vazio, nomes de produto/variação, cinco filtros e os quatro cartões. Datas fixas nos fixtures devem ser relativas ao relógio falso do Vitest para evitar testes frágeis.

```typescript
it('filters by code, product, status, expiration and availability', () => {
  fixture.detectChanges();
  component.searchTerm.set('tomate');
  component.statusFilter.set('ACTIVE');
  component.expirationFilter.set('EXPIRING_SOON');
  component.availabilityFilter.set('AVAILABLE');
  expect(component.filteredLots().map((lot) => lot.id)).toEqual(['lot-1']);
});
```

- [ ] **Step 2: Confirmar a falha**

Run: `cd C:\Projetos\agrosales\frontend; npm test -- --include="src/app/features/lots/lots.component.spec.ts" --watch=false`

Expected: FAIL porque o componente ainda não existe.

- [ ] **Step 3: Implementar estado derivado**

Criar signals para dados, loading, erro e filtros; computeds para `filteredLots`, `activeLotsCount`, `availableTotal`, `expiringSoonCount` e `expiredCount`. Comparar números com `Number(lot.available_quantity)`. Resolver produto pela variação e variação por ID sem alterar os modelos existentes.

- [ ] **Step 4: Criar template e estilos de leitura**

Implementar cabeçalho, quatro cartões, controles rotulados, tabela de onze colunas, badges textuais, estados e rolagem horizontal. Copiar os tokens visuais da feature de Variações, adaptando classes para `.lots-page`; não importar Angular Material novo.

- [ ] **Step 5: Trocar a rota**

Em `app.routes.ts`, manter `producerRoles` e alterar somente `loadComponent` de `/lots` para importar `./features/lots/lots.component` e retornar `LotsComponent`.

- [ ] **Step 6: Confirmar o verde e commit**

Run: `cd C:\Projetos\agrosales\frontend; npm test -- --include="src/app/features/lots/lots.component.spec.ts" --watch=false`

Expected: PASS.

```powershell
git add frontend/src/app/features/lots/lots.component.ts frontend/src/app/features/lots/lots.component.html frontend/src/app/features/lots/lots.component.scss frontend/src/app/features/lots/lots.component.spec.ts frontend/src/app/app.routes.ts
git commit -m "feat: adiciona consulta e filtros de lotes"
```

---

### Task 8: Cadastro, edição, status, detalhes e movimentações no frontend

**Files:**
- Modify: `frontend/src/app/features/lots/lots.component.ts`
- Modify: `frontend/src/app/features/lots/lots.component.html`
- Modify: `frontend/src/app/features/lots/lots.component.scss`
- Modify: `frontend/src/app/features/lots/lots.component.spec.ts`

**Interfaces:**
- Consumes: todos os métodos de `LotService`.
- Produces: fluxo operacional completo da página.

- [ ] **Step 1: Escrever testes vermelhos do cadastro**

Cobrir variações ativas filtradas pelo produto, campos obrigatórios, validade, quantidade/motivo, payload e atualização da lista. Na edição, confirmar produto/variação imutáveis e ausência dos campos de saldo.

- [ ] **Step 2: Escrever testes vermelhos de status e detalhes**

Cobrir PATCH, mensagens do backend, carregamento de histórico, ordenação cronológica, labels dos tipos e bloqueios explicados.

- [ ] **Step 3: Escrever testes vermelhos de movimentação**

Garantir que as opções sejam apenas `ENTRY`, `LOSS`, `RETURN`, `ADJUSTMENT`; validar quantidade zero apenas no ajuste; enviar motivo/observações; recarregar lote e histórico após sucesso.

- [ ] **Step 4: Confirmar as falhas**

Run: `cd C:\Projetos\agrosales\frontend; npm test -- --include="src/app/features/lots/lots.component.spec.ts" --watch=false`

Expected: FAIL nos fluxos ainda ausentes.

- [ ] **Step 5: Implementar formulários reativos e ações**

Criar `lotForm` e `movementForm` com `FormBuilder.nonNullable`, signals de drawers, item selecionado, saving e erros. Usar `HttpErrorResponse` para preferir `error.error.detail` quando for string e fallback seguro quando não for. Após cada mutação, substituir o lote na signal ou recarregá-lo pelo GET individual.

- [ ] **Step 6: Implementar drawers acessíveis**

Adicionar formulário de lote, painel de detalhes/histórico e formulário de movimentação. Todo botão terá `type`, drawers terão `aria-label`, botões de fechar terão nome acessível e mensagens usarão texto, não apenas cor.

- [ ] **Step 7: Confirmar o verde e commit**

Run: `cd C:\Projetos\agrosales\frontend; npm test -- --include="src/app/features/lots/*.spec.ts" --watch=false`

Expected: todos os testes de Lotes PASS.

```powershell
git add frontend/src/app/features/lots/lots.component.ts frontend/src/app/features/lots/lots.component.html frontend/src/app/features/lots/lots.component.scss frontend/src/app/features/lots/lots.component.spec.ts
git commit -m "feat: completa gestao de lotes e movimentacoes"
```

---

### Task 9: Regressão, validação real e ZIP

**Files:**
- Verify: `backend/`
- Verify: `frontend/`
- Create: `C:\Projetos\agrosales\agrosales-lotes-entrega.zip`

**Interfaces:**
- Produces: evidência de testes, build, fluxo real e arquivo de entrega.

- [ ] **Step 1: Executar testes direcionados do backend**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest tests/test_lots.py tests/test_lots_api.py tests/test_inventory_movements.py tests/test_inventory_movement_service.py tests/test_inventory_movements_api.py tests/test_order_completion_service.py tests/test_order_completion_api.py tests/test_reservation_repository.py -v`

Expected: PASS sem falhas.

- [ ] **Step 2: Executar suíte geral e Ruff**

Run: `cd C:\Projetos\agrosales\backend; python -m pytest`

Expected: todos os testes PASS.

Run: `cd C:\Projetos\agrosales\backend; python -m ruff check .`

Expected: nenhum erro nos arquivos alterados; erros antigos, se ainda existirem, devem ser listados separadamente e não corrigidos fora do escopo.

- [ ] **Step 3: Executar testes e build do frontend**

Run: `cd C:\Projetos\agrosales\frontend; npm test -- --include="src/app/features/lots/*.spec.ts" --watch=false`

Expected: PASS.

Run: `cd C:\Projetos\agrosales\frontend; npm run build`

Expected: build concluído sem erro.

- [ ] **Step 4: Validar o fluxo real em Docker**

No notebook, reconstruir a API se a imagem estiver antiga. Validar via frontend/Swagger: lote com entrada inicial; histórico; entrada, perda, devolução e ajuste; bloqueios; confirmação/conclusão de pedido; `SALE`; saldos e persistência após recarga. Registrar IDs e valores observados no handoff final.

- [ ] **Step 5: Preparar ZIP sem mudanças alheias**

Criar uma pasta temporária, copiar preservando os caminhos apenas dos arquivos listados no File Map que realmente foram alterados/criados e compactar como `C:\Projetos\agrosales\agrosales-lotes-entrega.zip`. Conferir com `Get-ChildItem` que o ZIP não contém `product-variations/`, outros ZIPs ou arquivos de configuração não relacionados.

- [ ] **Step 6: Conferir o diff e fazer commit final apenas se necessário**

Run: `git -c safe.directory=C:/Projetos/agrosales -C C:\Projetos\agrosales status --short`

Expected: mudanças preexistentes de Variações continuam separadas; nenhum arquivo novo de Lotes fica sem commit, exceto o ZIP de entrega, que não deve ser commitado.

