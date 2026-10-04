# Guia de validação: Usuários e vínculos com a empresa

## Pré-requisitos

- `docker compose up -d` na raiz e dependências instaladas no `.venv` de `backend/`

## Validar

Em `backend/`:

```sh
pytest
ruff check . && ruff format --check . && mypy
alembic upgrade head && alembic downgrade 0002 && alembic upgrade head
```

## Resultados esperados

| Cenário (spec) | Testes |
|---|---|
| E-mail, usuário e vínculo sem banco | `tests/identidade/unidade/test_email.py`, `test_usuario.py`, `test_vinculo.py` |
| História 1: cadastrar usuário | `tests/identidade/integracao/test_cadastrar_usuario.py` |
| História 2: vincular | `tests/identidade/integracao/test_vincular_usuario.py` |
| História 3: desativar e reativar vínculo | `tests/identidade/integracao/test_mudar_situacao_do_vinculo.py` |
| História 4: alterar usuário | `tests/identidade/integracao/test_alterar_usuario.py` |
| História 5: consultar | `tests/identidade/integracao/test_consultar_usuarios.py` |
| Autor do histórico é usuário cadastrado | `tests/historico/integracao/test_registrar_acao.py` |
