# Design: Módulo de Lotes do AgroSales

Data: 2026-07-18

## 1. Objetivo

Substituir o placeholder da rota `/lots` por um módulo completo de gestão de lotes e movimentações de estoque, integrado ao backend FastAPI e ao frontend Angular.

O módulo deve preservar a rastreabilidade do estoque. Saldos não serão alterados diretamente no formulário do lote, lotes não serão excluídos fisicamente e toda mudança de quantidade terá uma movimentação correspondente.

## 2. Escopo

A entrega inclui:

- listagem, busca e filtros de lotes;
- resumo operacional dos lotes;
- cadastro com entrada inicial auditável;
- consulta detalhada;
- edição controlada de código e datas;
- ativação e inativação;
- registro e consulta de movimentações;
- integração da conclusão de pedidos com movimentação de venda;
- indicadores de validade e disponibilidade;
- permissões de Administrador e Produtor;
- testes de backend e frontend;
- validação real com PostgreSQL e API em Docker.

A entrega não inclui exclusão física de lotes, venda manual pela tela de Lotes, troca da variação vinculada nem edição direta dos saldos físico e reservado.

## 3. Abordagem escolhida

A implementação evoluirá a arquitetura existente sem criar uma API agregadora ou reestruturar todo o domínio de estoque.

Serão ampliados os módulos atuais de lotes e movimentações. O frontend seguirá os padrões dos módulos de Produtos e Variações, com componentes standalone, signals, formulários reativos e serviços HTTP.

Essa abordagem reduz o risco de regressões nas reservas FEFO e nos pedidos, mantém as responsabilidades atuais e concentra as mudanças no domínio de estoque.

## 4. Arquitetura

### 4.1 Backend

Arquivos principais:

```text
backend/app/modules/inventory/lot_schemas.py
backend/app/modules/inventory/lot_repository.py
backend/app/modules/inventory/lot_service.py
backend/app/api/routers/lots.py
backend/app/modules/inventory/movement_service.py
backend/app/modules/inventory/movement_repository.py
backend/app/api/routers/inventory_movements.py
backend/app/modules/orders/order_completion_service.py
```

Os routers tratarão autenticação, autorização e tradução de exceções para respostas HTTP. Os services concentrarão regras e coordenação transacional. Os repositories executarão consultas e persistência sem decidir regras de negócio.

### 4.2 Frontend

Será criada a pasta:

```text
frontend/src/app/features/lots/
```

Com os arquivos:

```text
lot.models.ts
lot.service.ts
lot.service.spec.ts
lots.component.ts
lots.component.html
lots.component.scss
lots.component.spec.ts
```

A rota `/lots` carregará `LotsComponent` no lugar do placeholder existente.

## 5. Permissões

Somente `ADMINISTRADOR` e `PRODUTOR` terão acesso à página e aos endpoints operacionais de lotes e movimentações.

O perfil `VENDEDOR` não verá Lotes no menu e não acessará a rota. A disponibilidade necessária para vendas será apresentada futuramente no fluxo de Pedidos, sem expor detalhes internos dos lotes.

O backend continuará sendo a fonte de verdade das permissões, independentemente das proteções existentes no frontend.

## 6. Contratos da API

### 6.1 Endpoints de lotes

```text
GET    /api/v1/lots
GET    /api/v1/lots/{lot_id}
POST   /api/v1/lots
PUT    /api/v1/lots/{lot_id}
PATCH  /api/v1/lots/{lot_id}/status
```

### 6.2 Endpoints de movimentações

```text
GET    /api/v1/inventory-movements?lot_id={lot_id}
POST   /api/v1/inventory-movements
```

### 6.3 Cadastro de lote

Requisição:

```json
{
  "product_variation_id": "UUID",
  "code": "LOTE-2026-001",
  "production_date": "2026-07-18",
  "expiration_date": "2026-08-18",
  "initial_quantity": 100,
  "initial_entry_reason": "Entrada de produção",
  "initial_entry_notes": null
}
```

`initial_quantity` deve ser maior ou igual a zero. Quando for maior que zero, `initial_entry_reason` será obrigatório e o backend registrará uma movimentação `ENTRY`. Quando for zero, o lote será criado sem movimentação inicial e o motivo será opcional.

O backend nunca aceitará `reserved_quantity` no cadastro. Essa quantidade é controlada exclusivamente pelo fluxo de reservas.

### 6.4 Resposta do lote

A resposta conterá:

```text
id
product_variation_id
code
production_date
expiration_date
physical_quantity
reserved_quantity
available_quantity
status
expiration_state
created_at
updated_at
```

`available_quantity` será calculada como:

```text
physical_quantity - reserved_quantity
```

`expiration_state` terá um dos valores:

```text
EXPIRED
EXPIRES_TODAY
EXPIRING_SOON
REGULAR
```

### 6.5 Resposta de movimentação

Além dos campos atuais, a resposta apresentará:

```text
created_at
user_name
```

O histórico poderá, assim, identificar quando a movimentação ocorreu e quem foi responsável sem exibir somente o UUID do usuário.

## 7. Regras de validade e disponibilidade

A classificação de validade será:

- `EXPIRED`: validade anterior à data atual;
- `EXPIRES_TODAY`: validade igual à data atual;
- `EXPIRING_SOON`: validade futura em até 30 dias corridos;
- `REGULAR`: validade futura superior a 30 dias corridos.

Um lote será apresentado como esgotado quando `available_quantity` for igual a zero. Esgotamento é uma situação calculada e não substitui o status operacional.

Lotes vencidos, inativos ou sem saldo disponível não poderão ser selecionados pelo FEFO.

## 8. Cadastro e transação inicial

O cadastro seguirá este fluxo:

1. validar a variação e exigir que esteja ativa;
2. validar unicidade do código;
3. validar datas;
4. criar o lote com quantidades física e reservada iguais a zero;
5. quando a quantidade inicial for maior que zero, adicionar uma movimentação `ENTRY` com saldo anterior zero e novo saldo igual à quantidade inicial;
6. executar um único `commit`;
7. atualizar e retornar o lote.

Qualquer falha executará `rollback`. Lote e entrada inicial nunca poderão ser persistidos parcialmente.

## 9. Edição controlada

Os únicos campos editáveis serão:

- código;
- data de produção;
- data de validade.

A variação vinculada será imutável. Quantidades não aparecerão no formulário de edição.

A edição será bloqueada quando existir qualquer reserva associada ao lote ou qualquer movimentação diferente da entrada inicial. Uma única movimentação `ENTRY` criada junto com o lote não impedirá correções de código ou datas.

O novo código continuará sujeito à unicidade. A validade não poderá ser anterior à produção nem anterior à data atual.

## 10. Status operacional

O status operacional terá os valores `ACTIVE` e `INACTIVE`.

Regras:

- inativação exige `reserved_quantity` igual a zero;
- reativação exige lote não vencido;
- reativação exige `available_quantity` maior que zero;
- status de validade e esgotamento continuarão calculados separadamente;
- nenhuma alteração de status apaga o histórico.

Não haverá endpoint de exclusão física.

## 11. Movimentações

Tipos disponíveis no domínio:

```text
ENTRY
SALE
LOSS
RETURN
ADJUSTMENT
```

Na tela de Lotes, o usuário poderá registrar `ENTRY`, `LOSS`, `RETURN` e `ADJUSTMENT`. `SALE` será criada exclusivamente pela conclusão de pedidos.

Regras de saldo:

- `ENTRY` e `RETURN` somam a quantidade ao saldo físico;
- `LOSS` subtrai a quantidade do saldo físico;
- `ADJUSTMENT` define o saldo físico final para a quantidade informada;
- `SALE` subtrai a quantidade consumida pela reserva;
- nenhum resultado pode ser negativo;
- nenhum resultado pode ficar abaixo da quantidade reservada.

Motivo será obrigatório e terá entre 3 e 255 caracteres. Observações serão opcionais.

## 12. Integração com pedidos

Ao concluir um pedido confirmado, para cada reserva consumida o backend deverá:

1. validar saldos físico e reservado;
2. reduzir a quantidade reservada;
3. registrar uma movimentação `SALE` com usuário responsável, quantidade, saldo anterior, saldo posterior e motivo referente ao pedido;
4. marcar a reserva como `CONSUMED`;
5. atualizar o pedido para `COMPLETED`;
6. registrar o histórico de status do pedido;
7. executar um único `commit`.

O serviço de movimentações deverá permitir adicionar uma movimentação à sessão sem executar `commit` próprio, para que a conclusão do pedido permaneça atômica.

Qualquer falha fará `rollback` completo do pedido, reservas, lotes, movimentações e histórico de status.

## 13. Interface

### 13.1 Cabeçalho e resumo

A página terá identificação “Estoque”, título “Lotes”, texto explicativo e botão “Novo lote”.

Quatro cartões mostrarão:

- total de lotes ativos;
- saldo disponível total;
- lotes próximos do vencimento;
- lotes vencidos.

### 13.2 Filtros

Serão oferecidos:

- busca por código, produto ou código da variação;
- filtro por produto;
- status operacional;
- situação da validade;
- disponibilidade com saldo ou esgotado.

Os filtros serão aplicados aos dados já carregados, seguindo o padrão atual dos módulos do frontend.

### 13.3 Tabela

Colunas:

```text
Lote
Produto
Variação
Produção
Validade
Físico
Reservado
Disponível
Situação
Status
Ações
```

Os indicadores usarão texto e estilo visual, sem depender exclusivamente de cor. Em telas menores, a tabela utilizará rolagem horizontal.

### 13.4 Formulário de lote

O cadastro solicitará produto, variação, código, datas, quantidade inicial, motivo e observações.

Primeiro será escolhido o produto. Em seguida, o campo de variação exibirá somente variações ativas vinculadas ao produto selecionado.

Na edição, produto e variação permanecerão bloqueados. Campos de quantidade, motivo e observações da entrada inicial não serão exibidos.

### 13.5 Detalhes e histórico

Um painel de detalhes mostrará os dados completos, saldos e histórico cronológico de movimentações.

Cada movimentação exibirá tipo, quantidade, saldo anterior, saldo posterior, motivo, observações, usuário e data. O painel oferecerá a ação “Registrar movimentação” para os tipos permitidos.

Estados de carregamento, erro, lista vazia, salvamento e ações bloqueadas terão mensagens explícitas.

## 14. Tratamento de erros

- `400`: operação ou transição inválida;
- `403`: perfil sem permissão;
- `404`: lote ou variação não encontrado;
- `409`: código duplicado ou edição bloqueada pelo histórico;
- `422`: datas, quantidades ou saldos inválidos;
- `500`: falha inesperada após `rollback`.

O frontend apresentará mensagens específicas sempre que o backend fornecer um detalhe de negócio seguro para exibição. Falhas inesperadas usarão mensagens genéricas e manterão o formulário aberto para correção ou nova tentativa.

## 15. Estratégia TDD

Cada capacidade seguirá o ciclo:

1. escrever teste vermelho;
2. executar e confirmar a falha esperada;
3. implementar o mínimo necessário;
4. executar e confirmar o teste verde;
5. rodar os testes relacionados antes de avançar.

### 15.1 Backend

Os testes cobrirão:

- criação com saldo zero;
- criação com entrada inicial;
- transação única e `rollback` completo;
- código duplicado e datas inválidas;
- consulta individual;
- cálculos de disponibilidade e validade;
- edição permitida e bloqueada;
- ativação, inativação e seus bloqueios;
- regras de todas as movimentações;
- usuário e data no histórico;
- movimentação `SALE` na conclusão do pedido;
- atomicidade da conclusão;
- permissões;
- preservação do comportamento FEFO.

### 15.2 Frontend

Os testes cobrirão:

- contratos do serviço HTTP;
- carregamento de lotes, produtos e variações;
- busca, filtros e cartões de resumo;
- validações do cadastro;
- filtragem de variações por produto;
- edição controlada;
- alteração de status;
- detalhes e histórico;
- movimentações permitidas;
- ausência de venda manual;
- estados de carregamento, erro e lista vazia;
- proteção da rota por perfil.

## 16. Validação final

Comandos mínimos:

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest
python -m ruff check .

cd "C:\Projetos\agrosales\frontend"
npm test -- --include="src/app/features/lots/*.spec.ts" --watch=false
npm run build
```

O teste Angular não utilizará `--run`.

O fluxo real em Docker deverá validar:

1. criação de lote;
2. entrada inicial no histórico;
3. entrada, perda, devolução e ajuste;
4. bloqueios de saldo, edição e status;
5. confirmação e conclusão de pedido;
6. movimentação de venda;
7. saldos e reservas resultantes;
8. persistência após recarregar a página.

## 17. Critérios de conclusão

O módulo será considerado concluído somente quando:

- backend e frontend estiverem integrados;
- regras e permissões estiverem cobertas por testes;
- testes relacionados estiverem passando;
- suíte geral do backend estiver passando;
- build do frontend estiver passando;
- erros do Ruff introduzidos pela entrega forem zero;
- o fluxo real tiver sido validado com PostgreSQL e API em Docker;
- nenhuma funcionalidade existente tiver sido quebrada;
- um ZIP com os arquivos da entrega tiver sido preparado sem mudanças não relacionadas.
