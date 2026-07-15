# Design: Reserva FEFO Persistente via API

Data: 2026-07-15

## Objetivo

Implementar o endpoint `POST /api/v1/stock-reservations` para criar reservas persistentes de estoque usando FEFO (First Expired, First Out).

A operação deve selecionar os lotes válidos que vencem primeiro, dividir a quantidade entre vários lotes quando necessário, atualizar `reserved_quantity` e gravar as linhas correspondentes em `stock_reservations`, sempre em uma única transação.

## Contrato da API

### Endpoint

`POST /api/v1/stock-reservations`

### Permissões

Podem criar reservas:

- `ADMINISTRADOR`
- `PRODUTOR`

O perfil `VENDEDOR` deve receber `403 Forbidden`.

### Corpo

```json
{
  "product_variation_id": "UUID",
  "quantity": 50
}
```

### Resposta de sucesso

Status: `201 Created`

```json
{
  "product_variation_id": "UUID",
  "requested_quantity": 50,
  "reserved_quantity": 50,
  "allocations": [
    {
      "reservation_id": "UUID",
      "lot_id": "UUID",
      "lot_code": "LOTE-001",
      "quantity": 30,
      "expiration_date": "2026-07-20"
    },
    {
      "reservation_id": "UUID",
      "lot_id": "UUID",
      "lot_code": "LOTE-002",
      "quantity": 20,
      "expiration_date": "2026-07-30"
    }
  ]
}
```

## Regras de negócio

1. A quantidade deve ser maior que zero.
2. A variação deve existir e estar ativa.
3. Apenas lotes da variação solicitada podem ser usados.
4. Lotes vencidos, inativos, esgotados ou sem saldo devem ser ignorados.
5. O saldo disponível é `physical_quantity - reserved_quantity`.
6. Os lotes devem ser ordenados por vencimento, data de produção e código.
7. A reserva pode ser dividida entre vários lotes.
8. Cada lote utilizado gera uma linha em `stock_reservations`.
9. `reserved_quantity` deve ser atualizado no mesmo fluxo.
10. A operação executa somente um `commit`.
11. Estoque insuficiente retorna `422`.
12. Qualquer falha deve executar `rollback`.
13. Nenhuma alteração parcial pode permanecer.

## Arquitetura

Arquivos novos:

```text
backend/app/modules/inventory/reservation_repository.py
backend/app/modules/inventory/reservation_application_service.py
backend/app/api/routers/stock_reservations.py
backend/tests/test_stock_reservations_api.py
```

Arquivos atualizados:

```text
backend/app/modules/inventory/reservation_schemas.py
backend/app/api/dependencies.py
backend/app/main.py
```

### ReservationRepository

- buscar lotes elegíveis;
- aplicar bloqueio de linha;
- adicionar reservas à sessão;
- não executar `commit`.

### ReservationApplicationService

- validar a variação;
- carregar os lotes;
- aplicar FEFO;
- atualizar os lotes;
- criar reservas;
- executar um único `commit`;
- executar `rollback` em caso de falha;
- montar a resposta.

### Router

- validar autenticação e autorização;
- receber o corpo;
- chamar o serviço;
- converter erros de domínio em respostas HTTP;
- retornar o resumo.

## Fluxo

```text
POST /api/v1/stock-reservations
        ↓
autenticação e autorização
        ↓
validação da variação
        ↓
busca de lotes com bloqueio
        ↓
ordenação FEFO
        ↓
cálculo das alocações
        ↓
atualização de reserved_quantity
        ↓
criação das reservas
        ↓
commit único
        ↓
resposta
```

## Erros

- `403`: usuário sem permissão.
- `404`: variação inexistente ou inativa.
- `422`: quantidade inválida.
- `422`: estoque insuficiente.
- `500`: falha inesperada após rollback.

## Concorrência

A consulta dos lotes deve usar bloqueio de linha no PostgreSQL para reduzir o risco de duas requisições reservarem o mesmo saldo simultaneamente. O bloqueio permanece ativo até o `commit` ou `rollback`.

## Testes

Os testes devem cobrir:

1. administrador cria reserva;
2. produtor cria reserva;
3. vendedor recebe `403`;
4. quantidade inválida é rejeitada;
5. variação inexistente ou inativa retorna `404`;
6. o lote que vence primeiro é usado primeiro;
7. a reserva pode ser dividida;
8. lotes inválidos são ignorados;
9. estoque insuficiente retorna `422`;
10. estoque insuficiente não altera lotes;
11. cada lote gera uma reserva;
12. a resposta contém todas as alocações;
13. ocorre apenas um `commit`;
14. falhas executam `rollback`.

## Critérios de conclusão

- testes passando;
- endpoint visível no Swagger;
- reserva criada no PostgreSQL;
- `reserved_quantity` atualizado;
- linhas gravadas em `stock_reservations`;
- nenhuma persistência parcial;
- código salvo no GitHub.
