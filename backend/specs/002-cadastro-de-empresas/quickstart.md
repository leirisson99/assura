# Guia de validação: Cadastro de empresas

## Pré-requisitos

- `docker compose up -d` na raiz e dependências instaladas no `.venv` de `backend/`

## Validar

Em `backend/`:

```sh
pytest
ruff check . && ruff format --check . && mypy
alembic upgrade head && alembic downgrade 0001 && alembic upgrade head
```

## Resultados esperados

| Cenário (spec) | Testes |
|---|---|
| CNPJ numérico e alfanumérico, máscara, dígitos | `tests/identidade/unidade/test_cnpj.py` |
| Regras da empresa (dados, situação, alteração) | `tests/identidade/unidade/test_empresa.py` |
| História 1: cadastro, unicidade, histórico | `tests/identidade/integracao/test_cadastrar_empresa.py` |
| História 2: alteração | `tests/identidade/integracao/test_alterar_empresa.py` |
| História 3: desativar e reativar | `tests/identidade/integracao/test_mudar_situacao_da_empresa.py` |
| História 4: consulta e listagem | `tests/identidade/integracao/test_consultar_empresas.py` |
| Histórico só aceita empresa cadastrada | `tests/historico/integracao/test_registrar_acao.py` |
