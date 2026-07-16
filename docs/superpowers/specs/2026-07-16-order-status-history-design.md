# Histórico de Status do Pedido — Design

## Objetivo

Registrar de forma auditável todas as mudanças de status de um pedido, incluindo a criação inicial, o status anterior, o novo status, o usuário responsável e a data da alteração.

## Escopo

O histórico deve registrar:

- criação do pedido: `null -> DRAFT`;
- confirmação: `DRAFT -> CONFIRMED`;
- cancelamento: `DRAFT/CONFIRMED -> CANCELLED`;
- conclusão: `CONFIRMED -> COMPLETED`.

A consulta será feita por um endpoint separado:

```text
GET /api/v1/orders/{order_id}/history
```

## Modelo de dados

Tabela:

```text
order_status_history
```

Campos:

```text
id
order_id
previous_status
new_status
changed_by_user_id
created_at
```

### Regras dos campos

- `id`: UUID da ocorrência.
- `order_id`: UUID do pedido.
- `previous_status`: status anterior; aceita `null` apenas na criação.
- `new_status`: novo status do pedido.
- `changed_by_user_id`: UUID do usuário que realizou a ação.
- `created_at`: data e hora da alteração em UTC.

## Arquitetura

Será criado um módulo de histórico dentro de `orders`, seguindo os padrões já existentes:

```text
app/modules/orders/order_status_history_model.py
app/modules/orders/order_status_history_repository.py
app/modules/orders/order_status_history_schemas.py
```

Também será criada uma migration Alembic para a tabela.

## Integração com os fluxos existentes

### Criação do pedido

Ao criar um pedido:

```text
previous_status = null
new_status = DRAFT
changed_by_user_id = current_user.id
```

### Confirmação

Ao confirmar:

```text
previous_status = DRAFT
new_status = CONFIRMED
changed_by_user_id = current_user.id
```

### Cancelamento

Ao cancelar:

```text
previous_status = DRAFT ou CONFIRMED
new_status = CANCELLED
changed_by_user_id = current_user.id
```

### Conclusão

Ao concluir:

```text
previous_status = CONFIRMED
new_status = COMPLETED
changed_by_user_id = current_user.id
```

## Transações

O histórico será gravado na mesma transação da alteração do pedido.

Se qualquer parte da operação falhar:

- o status do pedido não será persistido;
- o histórico não será persistido;
- será executado `rollback`.

## Endpoint

```text
GET /api/v1/orders/{order_id}/history
```

### Permissões

```text
ADMINISTRADOR
PRODUTOR
VENDEDOR
```

### Ordenação

Os registros serão retornados do mais antigo para o mais recente:

```text
created_at ASC
```

### Respostas

```text
200 — histórico retornado
404 — pedido não encontrado
403 — usuário sem permissão
```

## Testes

Serão criados testes para:

- registrar `null -> DRAFT` na criação;
- registrar confirmação;
- registrar cancelamento;
- registrar conclusão;
- salvar o usuário responsável;
- garantir rollback junto com o pedido;
- listar o histórico em ordem cronológica;
- retornar `404` para pedido inexistente;
- validar permissões do endpoint.

## Fora do escopo

Não será criada agora uma tabela genérica de auditoria para todas as entidades do sistema.

Também não serão registrados:

- alterações de itens;
- alterações de preços;
- alterações de cliente;
- observações ou motivos livres.
