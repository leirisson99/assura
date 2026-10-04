# Pesquisa: Administrador da empresa

## 1. Onde fica o papel

- **Decisão**: `vinculo.administrador_da_empresa` (booleano). O Princípio V põe permissões no vínculo;
  um vínculo por usuário e empresa já existe.

## 2. Último administrador com ações simultâneas

- **Decisão**: antes de retirar o papel ou desativar o vínculo de um administrador, a aplicação chama
  `Vinculos.contar_administradores_ativos(empresa_id)`, que faz `SELECT ... FOR UPDATE` nas linhas de
  vínculos administradores ativos da empresa. A segunda transação simultânea espera a primeira e conta
  de novo. Se o vínculo em questão é o único, `UltimoAdministradorNaoPodeSerRemovido`.
- **Alternativa rejeitada**: gatilho no banco (regra de negócio fora do domínio).

## 3. Permissões

- **Decisão**: `Permissoes(vinculos, empresas)` com `exigir_administrador_do_sistema`,
  `exigir_administrador_da_empresa(solicitante, empresa_id)` (administrador do sistema também passa) e
  `exigir_pode_ver_usuario`. É administrador da empresa quem tem vínculo ativo, marcado, com empresa
  ativa (RF-004).
- **Casos de uso**: recebem `solicitante: UsuarioAutenticado`; o autor do histórico é
  `Autor.usuario(solicitante.id)`. `CriarRoot` continua com autor `sistema`.

| Ação | Quem pode |
|---|---|
| Empresas: cadastrar, alterar, desativar, reativar, listar | administrador do sistema |
| Empresa: obter | administrador do sistema ou da empresa |
| Incluir usuário na empresa, listar usuários, desativar e reativar vínculo, tornar e remover administrador | administrador do sistema ou da empresa |
| Cadastrar e alterar usuário, vincular por id | administrador do sistema |
| Obter usuário | o próprio, administrador do sistema, administrador de empresa onde o usuário tem vínculo |
| Redefinir senha | administrador do sistema; administrador da empresa se todos os vínculos ativos do alvo são com a empresa dele e o alvo não é administrador do sistema |
| Histórico | administrador do sistema (todo); administrador da empresa (da empresa) |

## 4. Incluir usuário na empresa

- **Decisão**: `IncluirUsuarioNaEmpresa(empresa_id, nome, email)`: se o e-mail não existe, cadastra e
  vincula; se existe, vincula o usuário existente sem alterar nome. Cada parte registra o seu tipo de
  ação.

## 5. Erros para HTTP

| Categoria | Status | Erros |
|---|---|---|
| Sem sessão | 401 | `CredenciaisInvalidas`, sessão inválida |
| Sem permissão | 403 | `PermissaoNegada`, `ConsultaAOutraEmpresaNaoPermitida`, senha provisória |
| Não encontrado | 404 | `*NaoEncontrad*` |
| Conflito com o estado | 409 | `*JaCadastrado`, `*JaExiste`, `*JaAtiv*`, `*JaDesativad*`, `UltimoAdministradorNaoPodeSerRemovido`, `EmpresaDesativadaNaoAceitaVinculo`, `VinculoDesativadoNaoPodeSerAdministrador`, `VinculoJaEAdministrador`, `VinculoNaoEAdministrador` |
| Dados inválidos | 422 | demais erros de domínio (`CnpjInvalido`, `SenhaInvalida`, `PeriodoInvalido`, `PaginaInvalida`...) |

A tradução fica num único lugar (`compartilhado/infraestrutura/http.py`), por categoria de erro
registrada pelos contextos.
