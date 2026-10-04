# Contrato HTTP: desativação de usuário

Acrescenta duas rotas ao contrato da etapa 1 (`specs/005-administrador-da-empresa/contracts/http.md`).
Mesmas regras: `Authorization: Bearer <token>` de usuário com senha definitiva e erros
`{"detail": "<motivo>"}`.

## Usuários

| Método e rota | Quem | Resposta | Erros |
|---|---|---|---|
| `POST /usuarios/{id}/desativacao` | sistema | 200 `Usuario` | 403 sem permissão; 404 usuário inexistente; 409 já desativado, último administrador de empresa, último administrador do sistema |
| `POST /usuarios/{id}/reativacao` | sistema | 200 `Usuario` | 403 sem permissão; 404 usuário inexistente; 409 já ativo |

`Usuario`: `{id, nome, email, situacao, administrador_do_sistema}`, com `situacao` em `ativo` ou
`desativado`.

## Efeitos nas rotas existentes

| Rota | Efeito |
|---|---|
| `POST /autenticacao/login` (etapa 1.4) | usuário desativado recebe o mesmo 401 de senha errada |
| Qualquer rota com sessão | sessão de usuário desativado recebe 401 |
| `GET /usuarios/{id}` e `GET /empresas/{id}/usuarios` | `usuario.situacao` mostra `desativado` |
| `DELETE /vinculos/{id}/administrador`, `POST /vinculos/{id}/desativacao` | 409 quando o vínculo é o último administrador ativo, desconsiderando usuários desativados |
