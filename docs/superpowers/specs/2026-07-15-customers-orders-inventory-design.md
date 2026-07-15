# Design: Clientes, Pedidos e Integração com Estoque

Data: 2026-07-15

## Objetivo

Implementar os módulos de clientes, pedidos e itens de pedido, integrados ao estoque por reservas FEFO.

A entrega será dividida em cinco etapas:

1. cadastro de clientes;
2. pedidos e itens;
3. confirmação com reserva FEFO;
4. cancelamento com liberação;
5. conclusão com baixa física.

## Clientes

### Tabela `customers`

Campos:

```text
id
customer_type
document_type
document
name
phone
email
street
number
complement
neighborhood
city
state
zip_code
is_active
created_at
updated_at
```

### Tipos e regras

`customer_type`: `INDIVIDUAL` ou `COMPANY`.

`document_type`: `CPF` ou `CNPJ`.

- `document` deve ser único;
- o documento será validado conforme o tipo;
- o endereço principal ficará em `customers`;
- clientes inativos permanecem no banco;
- clientes inativos não podem ser usados em novos pedidos;
- `ADMINISTRADOR`, `PRODUTOR` e `VENDEDOR` podem criar e editar;
- somente `ADMINISTRADOR` e `PRODUTOR` podem inativar;
- exclusão física não será permitida.

## Pedidos

### Tabela `orders`

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

Status:

```text
DRAFT
CONFIRMED
CANCELLED
COMPLETED
```

### Tabela `order_items`

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

### Regras

- todo pedido nasce `DRAFT`;
- deve apontar para cliente ativo;
- o usuário autenticado será o vendedor;
- `notes` será opcional;
- todos os perfis podem criar e editar rascunhos;
- apenas `ADMINISTRADOR` e `PRODUTOR` podem confirmar, cancelar e concluir;
- pedidos fora de `DRAFT` não podem ter itens alterados;
- a mesma variação não pode aparecer duplicada;
- ao adicionar novamente, a quantidade do item existente será atualizada.

## Preços e cálculos

- preço inicial: `standard_price`;
- `PRODUTOR` e `VENDEDOR` não podem usar preço abaixo de `minimum_price`;
- `ADMINISTRADOR` pode vender abaixo do mínimo;
- `unit_price` deve ser maior que zero;
- `discount_amount` é valor fixo total por item;
- `total_amount = quantity × unit_price - discount_amount`;
- `subtotal = soma de quantity × unit_price`;
- `discount_total = soma de discount_amount`;
- `total_amount do pedido = subtotal - discount_total`;
- `quantity` deve ser maior que zero;
- desconto não pode ser negativo nem maior que o valor bruto.

## Confirmação do pedido

Transição:

```text
DRAFT → CONFIRMED
```

Fluxo:

1. validar pedido em `DRAFT`;
2. validar ao menos um item;
3. validar cliente ativo;
4. processar todos os itens por FEFO;
5. criar reservas;
6. atualizar `reserved_quantity`;
7. vincular cada reserva a `order_item_id`;
8. alterar status para `CONFIRMED`;
9. preencher `confirmed_at`;
10. executar um único `commit`.

Se qualquer item não tiver estoque suficiente:

- toda a confirmação será rejeitada;
- nenhuma reserva será mantida;
- nenhum lote ficará alterado;
- o pedido continuará `DRAFT`;
- ocorrerá `rollback`.

## Alteração em `stock_reservations`

Adicionar:

```text
order_item_id
```

Chave estrangeira para:

```text
order_items.id
```

## Cancelamento

Transição principal:

```text
CONFIRMED → CANCELLED
```

- reservas `ACTIVE` viram `RELEASED`;
- `reserved_quantity` dos lotes é reduzido;
- `cancelled_at` é preenchido;
- tudo ocorre em uma transação;
- pedidos `DRAFT` podem ser cancelados sem alterar estoque;
- pedidos `COMPLETED` não podem ser cancelados.

## Conclusão

Transição:

```text
CONFIRMED → COMPLETED
```

Para cada reserva:

```text
physical_quantity -= reservation.quantity
reserved_quantity -= reservation.quantity
reservation.status = CONSUMED
```

Depois:

- status vira `COMPLETED`;
- `completed_at` é preenchido;
- tudo ocorre em uma única transação;
- nenhum saldo pode ficar negativo.

## Permissões

### Clientes

| Ação | Administrador | Produtor | Vendedor |
|---|---:|---:|---:|
| Consultar | Sim | Sim | Sim |
| Criar | Sim | Sim | Sim |
| Editar | Sim | Sim | Sim |
| Inativar | Sim | Sim | Não |

### Pedidos

| Ação | Administrador | Produtor | Vendedor |
|---|---:|---:|---:|
| Criar rascunho | Sim | Sim | Sim |
| Editar rascunho | Sim | Sim | Sim |
| Confirmar | Sim | Sim | Não |
| Cancelar | Sim | Sim | Não |
| Concluir | Sim | Sim | Não |
| Preço abaixo do mínimo | Sim | Não | Não |

## Arquitetura

### Clientes

```text
backend/app/modules/customers/customer_model.py
backend/app/modules/customers/customer_schemas.py
backend/app/modules/customers/customer_repository.py
backend/app/modules/customers/customer_service.py
backend/app/api/routers/customers.py
```

### Pedidos

```text
backend/app/modules/orders/order_model.py
backend/app/modules/orders/order_item_model.py
backend/app/modules/orders/order_schemas.py
backend/app/modules/orders/order_repository.py
backend/app/modules/orders/order_service.py
backend/app/modules/orders/order_confirmation_service.py
backend/app/modules/orders/order_cancellation_service.py
backend/app/modules/orders/order_completion_service.py
backend/app/api/routers/orders.py
```

### Migrações

1. `customers`;
2. `orders` e `order_items`;
3. `order_item_id` em `stock_reservations`.

## Erros esperados

- `400`: transição inválida;
- `403`: sem permissão;
- `404`: recurso não encontrado;
- `409`: documento duplicado;
- `422`: documento inválido;
- `422`: quantidade inválida;
- `422`: desconto inválido;
- `422`: preço abaixo do mínimo sem autorização;
- `422`: estoque insuficiente;
- `422`: pedido sem itens;
- `500`: erro inesperado após rollback.

## Estratégia de testes

### Clientes

- pessoa física e jurídica;
- documento duplicado;
- CPF e CNPJ inválidos;
- edição;
- permissões de inativação;
- cliente inativo bloqueado em novo pedido.

### Pedidos e itens

- criação em `DRAFT`;
- inclusão e atualização de item;
- uso de `standard_price`;
- recálculo de totais;
- bloqueio de edição fora de `DRAFT`;
- preço mínimo por perfil;
- desconto inválido.

### Confirmação

- FEFO;
- divisão entre lotes;
- vínculo por `order_item_id`;
- rollback completo;
- permissão.

### Cancelamento

- liberação das reservas;
- redução de `reserved_quantity`;
- status `RELEASED`;
- bloqueio após conclusão.

### Conclusão

- redução de estoque físico e reservado;
- status `CONSUMED`;
- prevenção de saldo negativo;
- transação única.

## Critérios de conclusão

- migrações aplicadas;
- testes passando;
- clientes gerenciáveis no Swagger;
- pedidos e itens funcionais;
- confirmação com FEFO;
- cancelamento liberando estoque;
- conclusão baixando estoque;
- permissões respeitadas;
- nenhuma persistência parcial;
- código salvo no GitHub.
