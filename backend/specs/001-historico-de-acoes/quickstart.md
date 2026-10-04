# Guia de validação: Histórico de ações

## Pré-requisitos

- PostgreSQL do projeto rodando: `docker compose up -d` (na raiz do repositório, porta 5433)
- Dependências: `pip install -e ".[dev]"` no `.venv` de `backend/`

## Validar

Em `backend/`:

```sh
pytest                      # unidade e integração; cria o banco assura_teste se não existir
ruff check . && ruff format --check .
mypy
alembic upgrade head        # aplica a tabela no banco de desenvolvimento
alembic downgrade base      # confirma que a migração é reversível
alembic upgrade head
```

## Resultados esperados

| Cenário (spec) | Teste |
|---|---|
| História 1: registro com todos os campos e gravação conjunta | `tests/historico/integracao/test_registrar_acao.py` |
| História 2: alteração e exclusão rejeitadas pelo banco | `tests/historico/integracao/test_imutabilidade.py` |
| História 3: filtros, ordem, páginas e isolamento por empresa | `tests/historico/integracao/test_consultar_historico.py` |
| Regras de domínio sem banco | `tests/historico/unidade/` |

## Conferência manual da imutabilidade

```sh
docker compose exec postgres psql -U assura -c "TRUNCATE registro_de_historico;"
```

Esperado: erro `o histórico de ações não pode ser alterado nem excluído`.

Use `TRUNCATE`: o gatilho dele vale para o comando inteiro e dispara mesmo com a tabela vazia. Não
insira registros de teste no banco de desenvolvimento, porque eles não podem ser apagados depois
(só recriando a tabela com `alembic downgrade base` e `alembic upgrade head`).
