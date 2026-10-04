# Pesquisa: Desativação de usuário

## 1. Situação do usuário

- **Decisão**: `SituacaoDoUsuario` ganha `DESATIVADO`. `Usuario.desativar()` recusa quem já está
  desativado com `UsuarioJaDesativado`; `Usuario.reativar()` recusa quem já está ativo com
  `UsuarioJaAtivo`. Mesmo desenho de `Vinculo` e `Empresa`.
- **Banco**: a restrição `situacao_valida` da tabela `usuario` passa a aceitar `'desativado'`
  (migração `0006`). A volta da migração recria a restrição antiga e falha se houver usuário
  desativado, em vez de reativá-lo sem ninguém ter decidido.

## 2. Acesso cortado na hora

- **Decisão**: nada muda. O login (`Autenticar`) já trata usuário que não está ativo como
  inexistente, conferindo a senha contra o resumo descartável (mesma resposta e mesmo tempo), e
  `obter_usuario_da_sessao` relê a situação no banco a cada requisição (etapa 1.4, research.md).
  Esta funcionalidade só acrescenta os testes com a situação "desativado" de verdade.

## 3. Quem conta como administrador ativo da empresa

- **Decisão**: administrador ativo é quem tem vínculo ativo, marcado como administrador, **e usuário
  ativo** (RF-006). A porta `Vinculos.contar_administradores_ativos(empresa_id) -> int` é trocada por
  `Vinculos.listar_administradores_ativos(empresa_id) -> list[UUID]`, que devolve os ids dos vínculos
  e junta a tabela `usuario`.
- **Regra do último administrador**: `exigir_que_a_empresa_mantenha_administrador(vinculos,
  empresa_id, vinculo_id)` recusa só quando a lista é exatamente `[vinculo_id]`. Usada ao retirar o
  papel, ao desativar o vínculo e ao desativar o usuário.
- **Por que lista e não contagem**: com a situação do usuário na regra, o alvo pode ser um vínculo
  administrador cujo usuário já está desativado. Ele não está na contagem, e "contagem ≤ 1" recusaria
  desativar o vínculo dele quando há exatamente um outro administrador, o que é permitido.
- **Alternativa rejeitada**: desativar o usuário retirar também o papel de administrador dos
  vínculos dele. Violaria o RF-009 (a reativação devolve os mesmos papéis) e criaria registros de
  "administrador removido" que ninguém pediu.

## 4. Ações simultâneas

- **Decisão**: a consulta de `listar_administradores_ativos` bloqueia as linhas de `vinculo` **e** de
  `usuario` que participam da junção (`SELECT ... FOR UPDATE` sem `OF`), em ordem de id do vínculo.
- **Por quê**: desativar o usuário A altera só a linha de A em `usuario`. Se só os vínculos fossem
  bloqueados, a transação que retira o papel de B, ao ser liberada, conferiria de novo a linha do
  vínculo mas não a do usuário A, e ainda contaria A como ativo. Com as duas tabelas bloqueadas, o
  PostgreSQL relê a linha de A já desativada e B passa a ser o último.
- **Várias empresas**: desativar um usuário administrador de várias empresas confere as empresas em
  ordem de id. Duas desativações simultâneas bloqueiam na mesma ordem e não se travam.
- **Teste**: como em `test_ultimo_administrador_simultaneo.py`, com duas conexões reais: desativar o
  usuário A e retirar o papel de B ao mesmo tempo; só uma das duas é aceita.

## 5. Último administrador do sistema

- **Decisão**: `Usuarios.contar_administradores_do_sistema_ativos() -> int`. Desativar um
  administrador do sistema com contagem ≤ 1 é recusado com
  `UltimoAdministradorDoSistemaNaoPodeSerDesativado`.
- **Sem bloqueio de linhas**: hoje só existe o root e não há como criar outro administrador do
  sistema (spec, Premissas). O bloqueio entra quando existir essa possibilidade (Princípio X).

## 6. Casos de uso e permissões

| Ação | Quem pode | Histórico |
|---|---|---|
| `DesativarUsuario` | administrador do sistema | `usuario_desativado`, sem empresa |
| `ReativarUsuario` | administrador do sistema | `usuario_reativado`, sem empresa |

- `DesativarUsuario` confere, nesta ordem: permissão, último administrador do sistema, último
  administrador de cada empresa em que o usuário tem vínculo administrador ativo. A mensagem do erro
  de empresa traz a razão social.
- Incluir usuário desativado numa empresa e redefinir a senha dele continuam funcionando como hoje;
  o usuário segue desativado (spec, Casos de borda). Só ganham testes.

## 7. Erros para HTTP

| Erro | Categoria |
|---|---|
| `UsuarioJaDesativado`, `UsuarioJaAtivo`, `UltimoAdministradorDoSistemaNaoPodeSerDesativado` | 409 conflito com o estado |

`UltimoAdministradorNaoPodeSerRemovido` já é 409.
