# Guia de validação: Administrador da empresa

## Validar automaticamente

Em `backend/`:

```sh
pytest
ruff check . && ruff format --check . && mypy
alembic upgrade head && alembic downgrade 0004 && alembic upgrade head
```

## Fluxo completo por HTTP (CS-003)

Coberto por `tests/identidade/http/test_fluxo_da_etapa_1.py`:

1. root entra e cadastra a empresa A (`POST /empresas`);
2. root inclui Maria em A (`POST /empresas/{A}/usuarios`) e define a senha dela
   (`POST /usuarios/{maria}/senha`);
3. root torna Maria administradora (`POST /vinculos/{v}/administrador`);
4. Maria entra, troca a senha provisória, inclui João em A e redefine a senha dele;
5. Maria consulta o histórico de A e vê as ações; tenta ver a empresa B e recebe 403;
6. Maria tenta remover o próprio papel sendo a única administradora e recebe 409.

## Testes por cenário

| Cenário (spec) | Testes |
|---|---|
| Papel no vínculo | `tests/identidade/unidade/test_vinculo.py` |
| Permissões | `tests/identidade/integracao/test_permissoes.py` |
| História 1 | `tests/identidade/integracao/test_administrador_da_empresa.py` |
| História 2 | `tests/identidade/integracao/test_incluir_usuario_na_empresa.py` e permissões nos testes existentes |
| História 3 | `tests/identidade/integracao/test_redefinir_senha.py` |
| História 4 | `tests/identidade/http/` |
