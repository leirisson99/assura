# Contrato HTTP: etapa 1

Todas as rotas exigem `Authorization: Bearer <token>` de usuário com senha definitiva, exceto as de
autenticação (ver `specs/004-autenticacao/contracts/http.md`). Erros: `{"detail": "<motivo>"}` com 401,
403, 404, 409 ou 422 (ver research.md, seção 5). Listagens aceitam `pagina` (padrão 1) e `tamanho`
(padrão 50, máximo 200).

## Empresas

| Método e rota | Quem | Corpo / parâmetros | Resposta |
|---|---|---|---|
| `POST /empresas` | sistema | `{razao_social, nome_fantasia?, cnpj}` | 201 `Empresa` |
| `GET /empresas` | sistema | `situacao?` (`ativa`, `desativada`) | 200 `[Empresa]` |
| `GET /empresas/{id}` | sistema ou adm. da empresa | | 200 `Empresa` |
| `PUT /empresas/{id}` | sistema | `{razao_social, nome_fantasia?, cnpj}` | 200 `Empresa` |
| `POST /empresas/{id}/desativacao` | sistema | | 200 `Empresa` |
| `POST /empresas/{id}/reativacao` | sistema | | 200 `Empresa` |
| `GET /empresas/{id}/usuarios` | sistema ou adm. da empresa | `situacao?` (`ativo`, `desativado`) | 200 `[UsuarioDaEmpresa]` |
| `POST /empresas/{id}/usuarios` | sistema ou adm. da empresa | `{nome, email}` | 201 `UsuarioDaEmpresa` |
| `GET /empresas/{id}/historico` | sistema ou adm. da empresa | `inicio?`, `fim?`, `tipo_de_acao?`, `objeto_tipo?`, `objeto_id?`, `autor_usuario_id?` | 200 `[Registro]` |

`Empresa`: `{id, razao_social, nome_fantasia, cnpj, cnpj_formatado, situacao}`

`UsuarioDaEmpresa`: `{usuario: Usuario, vinculo: Vinculo}`

## Vínculos

| Método e rota | Quem | Resposta |
|---|---|---|
| `POST /vinculos/{id}/desativacao` | sistema ou adm. da empresa do vínculo | 200 `Vinculo` |
| `POST /vinculos/{id}/reativacao` | sistema ou adm. da empresa do vínculo | 200 `Vinculo` |
| `POST /vinculos/{id}/administrador` | sistema ou adm. da empresa do vínculo | 200 `Vinculo` |
| `DELETE /vinculos/{id}/administrador` | sistema ou adm. da empresa do vínculo | 200 `Vinculo` |

`Vinculo`: `{id, usuario_id, empresa_id, situacao, administrador_da_empresa}`

## Usuários

| Método e rota | Quem | Corpo | Resposta |
|---|---|---|---|
| `GET /usuarios/{id}` | o próprio, sistema, adm. de empresa em comum | | 200 `Usuario` |
| `PUT /usuarios/{id}` | sistema | `{nome, email}` | 200 `Usuario` |
| `POST /usuarios/{id}/senha` | sistema; adm. da empresa se o alvo só tem vínculo ativo com ela | `{senha_provisoria}` | 204 |

`Usuario`: `{id, nome, email, situacao, administrador_do_sistema}`

## Histórico

| Método e rota | Quem | Parâmetros | Resposta |
|---|---|---|---|
| `GET /historico` | sistema | os de `/empresas/{id}/historico` e `empresa_id?` | 200 `[Registro]` |

`Registro`: `{id, autor_tipo, autor_usuario_id, tipo_de_acao, objeto_tipo, objeto_id, empresa_id, registrado_em, detalhes}`
