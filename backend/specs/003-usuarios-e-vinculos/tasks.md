# Tarefas: Usuários e vínculos com a empresa

**Entrada**: documentos em `specs/003-usuarios-e-vinculos/` · **Testes**: obrigatórios (TDD), escritos
antes e vistos falhar · **Formato**: `[ID] [P?] [História] Descrição` · caminhos relativos a
`backend/`.

## Fase 1: Fundação (bloqueia todas as histórias)

- [X] T001 Acrescentar `USUARIO_CADASTRADO`, `USUARIO_ALTERADO`, `USUARIO_VINCULADO`, `VINCULO_DESATIVADO` e `VINCULO_REATIVADO` em `TipoDeAcao` (`src/assura/historico/dominio/registro_de_historico.py`)
- [X] T002 [P] Testes de domínio em `tests/identidade/unidade/test_email.py`, `test_usuario.py` e `test_vinculo.py`: e-mail "parte local, `@`, domínio com ponto, sem espaços, até 254 caracteres" em minúsculas; nome "obrigatório, sem espaços nas pontas, até 150 caracteres"; `alterar_dados` só com campos alterados; vínculo nasce ativo, `VinculoJaDesativado`, `VinculoJaAtivo`
- [X] T003 Implementar `Email` (`src/assura/identidade/dominio/email.py`), `Usuario` (`usuario.py`), `Vinculo` (`vinculo.py`) e os erros novos em `erros.py`
- [X] T004 Criar as portas `Usuarios` e `Vinculos` e o tipo `UsuarioDaEmpresa` em `src/assura/identidade/aplicacao/portas.py`
- [X] T005 Criar as tabelas `usuario` e `vinculo` em `src/assura/identidade/infraestrutura/tabela.py` conforme data-model.md e a chave estrangeira `autor_usuario_id → usuario.id` em `src/assura/historico/infraestrutura/tabela.py`
- [X] T006 Criar a migração `migrations/versions/0003_criar_usuario_e_vinculo.py` (nomes de `CHECK` com `op.f`; `downgrade` reverte)
- [X] T007 Ajustar `tests/conftest.py`: `sessao` grava o usuário autor de teste (`ID_DO_AUTOR_DE_TESTE` em `tests/apoio.py`); fixture `criar_usuario`; testes que usam `Autor.usuario(uuid4())` passam a usar usuários gravados; teste de que autor inexistente é recusado em `tests/historico/integracao/test_registrar_acao.py`

## Fase 2: História 1 - Cadastrar usuário (P1) — MVP

- [X] T008 [P] [US1] Testes em `tests/identidade/integracao/test_cadastrar_usuario.py`: gravado e ativo, e-mail em minúsculas, e-mail repetido com outras maiúsculas recusado, dados inválidos não gravam, restrição do banco vira `EmailJaCadastrado`, registro `usuario_cadastrado` sem empresa e com detalhes vazios
- [X] T009 [US1] Implementar `CadastrarUsuario` (`src/assura/identidade/aplicacao/cadastrar_usuario.py`), `historico_do_usuario.py` e `UsuariosSqlAlchemy` (adicionar, obter, existe_email) em `src/assura/identidade/infraestrutura/usuarios_sqlalchemy.py`; exportar em `src/assura/identidade/__init__.py`

## Fase 3: História 2 - Vincular usuário a empresa (P1)

- [X] T010 [P] [US2] Testes em `tests/identidade/integracao/test_vincular_usuario.py`: vínculo ativo e registro `usuario_vinculado` na empresa; usuário em duas empresas; vínculo repetido (ativo ou desativado) recusado; empresa desativada recusada; usuário ou empresa inexistente; restrição do banco vira `VinculoJaExiste`
- [X] T011 [US2] Implementar `VincularUsuario` (`vincular_usuario.py`) e `VinculosSqlAlchemy` (adicionar, obter, existe, atualizar) em `vinculos_sqlalchemy.py`; exportar

## Fase 4: História 3 - Desativar e reativar vínculo (P2)

- [X] T012 [P] [US3] Testes em `tests/identidade/integracao/test_mudar_situacao_do_vinculo.py`: desativar e reativar com registros; repetir é recusado sem registro; outro vínculo e o usuário não mudam; vínculo inexistente
- [X] T013 [US3] Implementar `DesativarVinculo` e `ReativarVinculo` em `mudar_situacao_do_vinculo.py`; exportar

## Fase 5: História 4 - Alterar usuário (P2)

- [X] T014 [P] [US4] Testes em `tests/identidade/integracao/test_alterar_usuario.py`: alteração gravada; registro `usuario_alterado` só com o que mudou; e-mail de outro usuário recusado; sem mudança (inclusive maiúsculas no e-mail) sem registro; usuário inexistente
- [X] T015 [US4] Implementar `AlterarUsuario` em `alterar_usuario.py` e `UsuariosSqlAlchemy.atualizar`; exportar

## Fase 6: História 5 - Consultar usuários (P3)

- [X] T016 [P] [US5] Testes em `tests/identidade/integracao/test_consultar_usuarios.py`: obter; inexistente; listar só os da empresa pedida com a situação do vínculo; filtro por situação; ordem por nome; paginação
- [X] T017 [US5] Implementar `ConsultarUsuarios` em `consultar_usuarios.py` e `VinculosSqlAlchemy.listar_da_empresa`; exportar

## Fase 7: Acabamento

- [X] T018 [P] `ruff check`, `ruff format`, `mypy`
- [X] T019 Executar `quickstart.md` (testes e ida e volta da migração 0003, conferindo os nomes das restrições)

## Dependências

Fase 1 → História 1 → História 2 → História 3; História 4 depende só da 1; História 5 depende da 2.
Paralelos: os arquivos de teste de cada história.

## Estratégia

MVP = Fases 1 e 2 (usuários reais e autor do histórico ligado a eles).
