# Contrato HTTP: Autenticação

Todas as rotas, exceto o login, exigem `Authorization: Bearer <token>`.

## POST /autenticacao/login

Corpo: `{"email": "maria@empresa.com", "senha": "..."}`

- 200: `{"token": "...", "tipo": "bearer", "expira_em": "2026-10-04T20:00:00Z", "senha_provisoria": false}`
- 401: `{"detail": "e-mail ou senha incorretos"}` (mesma resposta para todos os casos de falha)

## GET /autenticacao/eu

Aceita senha provisória.

- 200: `{"id": "...", "nome": "...", "email": "...", "administrador_do_sistema": false, "senha_provisoria": false}`
- 401: sessão ausente, vencida, adulterada ou de usuário inexistente

## POST /autenticacao/eu/senha

Aceita senha provisória. Corpo: `{"senha_atual": "...", "nova_senha": "..."}`

- 204: senha trocada, deixa de ser provisória
- 401: sessão inválida · 422: senha atual incorreta ou nova senha inválida

## POST /usuarios/{usuario_id}/senha

Exige senha definitiva e administrador do sistema. Corpo: `{"senha_provisoria": "..."}`

- 204: senha redefinida como provisória
- 401: sessão inválida · 403: sem permissão ou com senha provisória · 404: usuário inexistente ·
  422: senha inválida

## Comando de terminal

```sh
python -m assura.criar_root --nome "Nome do Administrador" --email admin@empresa.com
```

Pede a senha e a confirmação sem mostrá-las. Sai com código 1 e mensagem se já existir
administrador do sistema, se a senha for inválida ou se a confirmação não conferir.
