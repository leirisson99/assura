# Guia de validação: Autenticação

## Pré-requisitos

- `docker compose up -d` na raiz; `pip install -e ".[dev]"` no `.venv` de `backend/`
- `ASSURA_CHAVE_DA_SESSAO` no `.env` (ver `.env.example`)

## Validar automaticamente

```sh
pytest
ruff check . && ruff format --check . && mypy
alembic upgrade head && alembic downgrade 0003 && alembic upgrade head
```

## Validar de ponta a ponta

```sh
python -m assura.criar_root --nome "Administrador" --email admin@assura.local
uvicorn assura.main:app --reload
```

Em http://localhost:8000/docs:

1. `POST /autenticacao/login` com o e-mail e a senha do root → recebe o token.
2. "Authorize" com o token → `GET /autenticacao/eu` mostra `administrador_do_sistema: true`.
3. Rodar `python -m assura.criar_root` de novo → recusado.

## Testes por cenário

| Cenário (spec) | Testes |
|---|---|
| Senha e regras do usuário | `tests/identidade/unidade/test_senha.py`, `test_usuario.py` |
| História 1: root | `tests/identidade/integracao/test_criar_root.py` |
| História 2: login e sessão | `tests/identidade/integracao/test_autenticar.py`, `tests/identidade/http/test_rotas_de_autenticacao.py` |
| História 3: trocar senha | `tests/identidade/integracao/test_trocar_propria_senha.py`, testes HTTP |
| História 4: redefinir senha | `tests/identidade/integracao/test_redefinir_senha.py`, testes HTTP |
