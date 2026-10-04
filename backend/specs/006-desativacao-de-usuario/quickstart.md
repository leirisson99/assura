# Guia de validação: Desativação de usuário

## Validar automaticamente

Em `backend/`:

```sh
pytest
ruff check . && ruff format --check . && mypy
alembic upgrade head && alembic downgrade 0005 && alembic upgrade head
```

A volta para `0005` só funciona sem usuários desativados no banco (ver [data-model.md](data-model.md)).

## Fluxo por HTTP

1. root cadastra as empresas A e B, inclui Maria nas duas e a torna administradora de A junto com
   João;
2. Maria entra e guarda o token;
3. root desativa Maria (`POST /usuarios/{maria}/desativacao`): 200, `situacao` `desativado`;
4. Maria usa o token guardado em `GET /autenticacao/eu`: 401;
5. Maria tenta entrar de novo: 401 com a mesma mensagem de senha errada;
6. root tenta retirar o papel de João em A (`DELETE /vinculos/{v}/administrador`): 409, João é o
   último administrador ativo;
7. root reativa Maria (`POST /usuarios/{maria}/reativacao`): 200; Maria entra com a mesma senha e
   continua administradora de A;
8. root tenta desativar a si mesmo: 409, último administrador do sistema.

## Testes por cenário

| Cenário (spec) | Testes |
|---|---|
| Situação no usuário | `tests/identidade/unidade/test_usuario.py` |
| História 1 | `tests/identidade/integracao/test_mudar_situacao_do_usuario.py`, `test_autenticar.py` |
| História 2 | `test_mudar_situacao_do_usuario.py`, `test_administrador_da_empresa.py`, `test_ultimo_administrador_simultaneo.py` |
| História 3 | `test_mudar_situacao_do_usuario.py` |
| História 4 | `tests/identidade/http/test_rotas_de_desativacao_de_usuario.py` |
| Casos de borda | `test_incluir_usuario_na_empresa.py`, `test_redefinir_senha.py` |
