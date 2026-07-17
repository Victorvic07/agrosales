# Rota de atualização de produto

## Objetivo

Adicionar `PUT /api/v1/products/{product_id}` ao roteador de produtos, imediatamente antes da rota `PATCH /{product_id}/status`.

## Implementação

- Receber `ProductUpdate` e retornar `ProductRead`.
- Permitir acesso somente aos perfis `ADMINISTRADOR` e `PRODUTOR`.
- Construir `ProductService` com os repositórios de produto e categoria já usados pelo roteador.
- Delegar a atualização a `ProductService.update(product_id, data)`.
- Importar `InvalidProductPriceError`, que ainda não está presente no roteador.
- Não alterar service, repository, schemas ou contratos existentes.

## Tratamento de erros

- `ProductNotFoundError` e `CategoryNotFoundError`: HTTP 404.
- `ProductAlreadyExistsError` e `ProductCodeAlreadyExistsError`: HTTP 409.
- `InvalidProductPriceError` e `ValueError`: HTTP 422.

## Verificação

- Confirmar primeiro que os testes de atualização falham sem a rota.
- Executar `tests/test_products_api.py` após a implementação.
- Executar os testes relacionados a produtos para detectar regressões.
