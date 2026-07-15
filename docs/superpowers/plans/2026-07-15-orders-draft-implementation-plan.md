# Pedidos e Itens em Rascunho — Plano de Implementação

## Objetivo

Implementar pedidos em `DRAFT` e seus itens, incluindo cálculo de totais, preço mínimo, atualização de item repetido e bloqueio de edição fora do rascunho.

## Arquivos novos

```text
backend/app/modules/orders/__init__.py
backend/app/modules/orders/order_model.py
backend/app/modules/orders/order_item_model.py
backend/app/modules/orders/order_schemas.py
backend/app/modules/orders/order_repository.py
backend/app/modules/orders/order_service.py
backend/app/api/routers/orders.py
backend/app/migrations/versions/0008_create_orders_and_items.py
backend/tests/test_order_models.py
backend/tests/test_order_schemas.py
backend/tests/test_order_repository.py
backend/tests/test_order_service.py
backend/tests/test_orders_api.py
backend/tests/test_order_migration.py
```

## Arquivos alterados

```text
backend/app/api/dependencies.py
backend/app/main.py
```

## Regras globais

- Todo pedido nasce como `DRAFT`.
- O cliente deve existir e estar ativo.
- O usuário autenticado será o vendedor.
- Todos os perfis podem criar e editar rascunhos.
- Pedidos fora de `DRAFT` não podem ter itens alterados.
- A mesma variação não pode aparecer duplicada.
- Ao adicionar novamente, a quantidade do item existente é atualizada.
- O preço inicial vem de `standard_price`.
- Apenas `ADMINISTRADOR` pode usar preço abaixo de `minimum_price`.
- `quantity` e `unit_price` devem ser maiores que zero.
- `discount_amount` não pode ser negativo nem maior que o valor bruto.
- `total_amount = quantity × unit_price - discount_amount`.
- O pedido deve recalcular `subtotal`, `discount_total` e `total_amount`.

## Tarefa 1 — Modelos

Criar `OrderStatus` com:

```text
DRAFT
CONFIRMED
CANCELLED
COMPLETED
```

Criar `orders` com:

```text
id
customer_id
seller_id
status
subtotal
discount_total
total_amount
notes
created_at
updated_at
confirmed_at
cancelled_at
completed_at
```

Criar `order_items` com:

```text
id
order_id
product_variation_id
quantity
unit_price
discount_amount
total_amount
created_at
updated_at
```

Adicionar restrição única em:

```text
order_id + product_variation_id
```

Testar nomes das tabelas e valores do enum.

Commit:

```powershell
git commit -m "feat: adiciona modelos de pedidos"
```

## Tarefa 2 — Schemas

Criar:

```text
OrderCreate
OrderUpdate
OrderItemCreate
OrderItemUpdate
OrderItemRead
OrderRead
```

Validações:

- quantidade maior que zero;
- preço maior que zero;
- desconto maior ou igual a zero;
- observações com até 2000 caracteres.

Commit:

```powershell
git commit -m "feat: adiciona schemas de pedidos"
```

## Tarefa 3 — Repository

Criar `OrderRepository` com:

```text
get_by_id
list_all
add_order
get_item_by_id
get_item_by_variation
add_item
delete_item
commit
refresh
```

O `get_by_id` e o `list_all` devem carregar os itens com `selectinload`.

Commit:

```powershell
git commit -m "feat: adiciona repository de pedidos"
```

## Tarefa 4 — Service

Criar erros:

```text
OrderNotFoundError
OrderItemNotFoundError
OrderNotEditableError
InactiveCustomerError
ProductVariationNotFoundError
PriceBelowMinimumError
InvalidDiscountError
```

Criar operações:

```text
create_order
update_order
add_item
update_item
delete_item
```

Regras principais:

- validar cliente ativo;
- validar pedido em `DRAFT`;
- validar variação ativa;
- usar `standard_price` quando `unit_price` não vier;
- impedir preço abaixo do mínimo para produtor e vendedor;
- permitir abaixo do mínimo para administrador;
- atualizar quantidade quando a variação já estiver no pedido;
- recalcular todos os totais depois de qualquer alteração.

Commit:

```powershell
git commit -m "feat: adiciona regras de pedidos em rascunho"
```

## Tarefa 5 — Migração 0008

Criar:

```text
backend/app/migrations/versions/0008_create_orders_and_items.py
```

A migração deve:

- criar enum `order_status`;
- criar `orders`;
- criar `order_items`;
- adicionar chaves estrangeiras;
- adicionar índices;
- adicionar restrições de quantidade, preço, desconto e total;
- usar `down_revision = "0007"`.

Commit:

```powershell
git commit -m "feat: adiciona migracao de pedidos"
```

## Tarefa 6 — API

Criar endpoints:

```text
GET    /api/v1/orders
GET    /api/v1/orders/{order_id}
POST   /api/v1/orders
PATCH  /api/v1/orders/{order_id}
POST   /api/v1/orders/{order_id}/items
PATCH  /api/v1/orders/{order_id}/items/{item_id}
DELETE /api/v1/orders/{order_id}/items/{item_id}
```

Permitir os três perfis nos endpoints de rascunho.

Mapear erros:

```text
404 — pedido, item ou variação não encontrada
409 — pedido fora de DRAFT
422 — cliente inativo
422 — preço abaixo do mínimo
422 — desconto inválido
```

Adicionar `get_order_repository` em `dependencies.py` e registrar o router em `main.py`.

Commit:

```powershell
git commit -m "feat: adiciona API de pedidos em rascunho"
```

## Tarefa 7 — Verificação

No PC principal:

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest -v
```

No notebook com Docker:

```powershell
cd "\\192.168.100.37\Projetos\agrosales"
docker compose up -d --build api
docker compose exec api alembic upgrade head
docker compose exec api alembic current
```

Esperado:

```text
0008 (head)
```

Confirmar:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "\d orders"
docker compose exec db psql -U agrosales -d agrosales -c "\d order_items"
```

Validar no Swagger:

```text
http://192.168.100.30:8000/docs
```

Criar pedido:

```json
{
  "customer_id": "UUID-REAL-DE-CLIENTE-ATIVO",
  "notes": "Entrega pela manhã"
}
```

Adicionar item:

```json
{
  "product_variation_id": "UUID-REAL-DA-VARIACAO",
  "quantity": 10,
  "unit_price": null,
  "discount_amount": 0
}
```

Resultado esperado:

- pedido com status `DRAFT`;
- item criado;
- totais recalculados;
- dados persistidos no PostgreSQL.
