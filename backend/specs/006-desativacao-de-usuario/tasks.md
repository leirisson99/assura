# Tarefas: Desativação de usuário

**Entrada**: documentos em `specs/006-desativacao-de-usuario/` · **Testes**: obrigatórios (TDD),
escritos antes e vistos falhar · **Formato**: `[ID] [P?] [História] Descrição` · caminhos relativos a
`backend/`.

## Fase 1: Fundação

- [X] T001 Acrescentar `USUARIO_DESATIVADO` e `USUARIO_REATIVADO` em `TipoDeAcao` (`src/assura/historico/dominio/registro_de_historico.py`)
- [X] T002 [P] Testes em `tests/identidade/unidade/test_usuario.py`: desativar ativo; reativar desativado; `UsuarioJaDesativado`; `UsuarioJaAtivo`; desativar não muda nome, e-mail, senha nem administrador do sistema
- [X] T003 Implementar `SituacaoDoUsuario.DESATIVADO`, `Usuario.desativar()` e `Usuario.reativar()` em `src/assura/identidade/dominio/usuario.py`; erros `UsuarioJaDesativado`, `UsuarioJaAtivo` e `UltimoAdministradorDoSistemaNaoPodeSerDesativado` em `src/assura/identidade/dominio/erros.py`; exportar em `src/assura/identidade/__init__.py`
- [X] T004 Restrição `usuario.situacao_valida` com `'desativado'` em `src/assura/identidade/infraestrutura/tabela.py` e migração `migrations/versions/0006_permitir_usuario_desativado.py` (volta recria a restrição antiga)

## Fase 2: Administrador ativo exige usuário ativo (base da História 2)

- [X] T005 [P] Testes em `tests/identidade/integracao/test_administrador_da_empresa.py` e `test_mudar_situacao_do_vinculo.py`: com A (usuário desativado) e B administradores, retirar o papel ou desativar o vínculo de B é recusado; desativar o vínculo de A é aceito
- [X] T006 Trocar `Vinculos.contar_administradores_ativos` por `listar_administradores_ativos` em `src/assura/identidade/aplicacao/portas.py` e `src/assura/identidade/infraestrutura/vinculos_sqlalchemy.py`: junta `usuario` ativo, `FOR UPDATE` nas duas tabelas, ordem por id do vínculo
- [X] T007 Substituir `exigir_que_nao_seja_o_ultimo_administrador` por `exigir_que_a_empresa_mantenha_administrador(vinculos, empresa_id, vinculo_id)` em `src/assura/identidade/aplicacao/mudar_situacao_do_vinculo.py` e usar em `administrador_da_empresa.py`

## Fase 3: História 1 - Desativar um usuário (P1)

- [X] T008 [P] [US1] Testes em `tests/identidade/integracao/test_mudar_situacao_do_usuario.py`: desativar com registro `usuario_desativado` sem empresa; vínculos, senha e histórico intactos; já desativado recusado sem registro; administrador de empresa e usuário comum recusados por permissão
- [X] T009 [P] [US1] Testes em `tests/identidade/integracao/test_autenticar.py`: usuário desativado com senha certa recebe `CredenciaisInvalidas` com a mesma mensagem de senha errada
- [X] T010 [US1] Implementar `DesativarUsuario` em `src/assura/identidade/aplicacao/mudar_situacao_do_usuario.py` (permissão e registro; as regras de último administrador entram na Fase 4); exportar em `src/assura/identidade/__init__.py`

## Fase 4: História 2 - Ninguém fica sem administrador (P1)

- [X] T011 [P] [US2] Testes em `test_mudar_situacao_do_usuario.py`: único administrador de uma empresa recusado com a razão social na mensagem, inclusive em empresa desativada; com A e B administradores, desativar A é aceito; root recusado como último administrador do sistema
- [X] T012 [P] [US2] Teste em `tests/identidade/integracao/test_ultimo_administrador_simultaneo.py`: desativar o usuário A e retirar o papel de B ao mesmo tempo, com duas conexões; só uma ação é aceita e a empresa mantém um administrador ativo
- [X] T013 [US2] `Usuarios.contar_administradores_do_sistema_ativos` em `portas.py` e `usuarios_sqlalchemy.py`; em `DesativarUsuario`, conferir o último administrador do sistema e, em ordem de id da empresa, o último administrador de cada empresa em que o usuário tem vínculo administrador ativo

## Fase 5: História 3 - Reativar um usuário (P2)

- [X] T014 [P] [US3] Testes em `test_mudar_situacao_do_usuario.py`: reativar com registro `usuario_reativado`; volta a entrar com a mesma senha; volta a contar como administrador da empresa; já ativo recusado sem registro; sem permissão recusado
- [X] T015 [US3] Implementar `ReativarUsuario` em `mudar_situacao_do_usuario.py`; exportar

## Fase 6: História 4 - HTTP e casos de borda (P2)

- [X] T016 Categorias 409 de `UsuarioJaDesativado`, `UsuarioJaAtivo` e `UltimoAdministradorDoSistemaNaoPodeSerDesativado` em `src/assura/identidade/infraestrutura/http.py`
- [X] T017 [P] [US4] Testes HTTP em `tests/identidade/http/`: desativar e reativar pelo root; 403 para administrador de empresa; 404; 409 já desativado e root; token aberto antes da desativação recebe 401; `GET /empresas/{id}/usuarios` mostra `situacao` `desativado`
- [X] T018 [US4] Rotas `POST /usuarios/{id}/desativacao` e `POST /usuarios/{id}/reativacao` em `src/assura/identidade/infraestrutura/rotas_de_usuarios.py` e dependências em `dependencias_http.py`, conforme `contracts/http.md`
- [X] T019 [P] Testes de casos de borda: incluir usuário desativado numa empresa cria o vínculo e ele continua desativado (`test_incluir_usuario_na_empresa.py`); redefinir a senha de desativado é aceito e ele continua sem entrar (`test_redefinir_senha.py`)

## Fase 7: Acabamento

- [X] T020 [P] `ruff`, `mypy`
- [X] T021 Executar `quickstart.md` (ida e volta da migração 0006)

## Dependências

Fase 1 → Fase 2 → História 1 → História 2 → História 3 → História 4 → Acabamento.

A Fase 2 vem antes da História 1 porque, sem ela, desativar um administrador deixaria a empresa
contando com ele. As Histórias 1 e 2 tocam o mesmo caso de uso e seguem em sequência; T019 pode correr
em paralelo a partir da História 1.

## Estratégia

Entrega única: a etapa 1.6 só fecha com as quatro histórias. O MVP interno é Fase 1 + Fase 2 +
Histórias 1 e 2 (desativar com segurança); reativação e HTTP completam a etapa.
