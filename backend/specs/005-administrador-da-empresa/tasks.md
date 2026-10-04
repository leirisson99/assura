# Tarefas: Administrador da empresa

**Entrada**: documentos em `specs/005-administrador-da-empresa/` · **Testes**: obrigatórios (TDD),
escritos antes e vistos falhar · **Formato**: `[ID] [P?] [História] Descrição` · caminhos relativos a
`backend/`.

## Fase 1: Fundação

- [X] T001 Acrescentar `ADMINISTRADOR_DEFINIDO` e `ADMINISTRADOR_REMOVIDO` em `TipoDeAcao`
- [X] T002 [P] Testes em `tests/identidade/unidade/test_vinculo.py`: nasce sem papel; tornar e remover; `VinculoDesativadoNaoPodeSerAdministrador`, `VinculoJaEAdministrador`, `VinculoNaoEAdministrador`; `e_administrador_ativo`
- [X] T003 Implementar o papel em `src/assura/identidade/dominio/vinculo.py` e os erros novos (inclusive `UltimoAdministradorNaoPodeSerRemovido`)
- [X] T004 Coluna `vinculo.administrador_da_empresa` "não nulo, padrão `false`", índice parcial e migração `migrations/versions/0005_acrescentar_administrador_ao_vinculo.py`; `Vinculos` ganha `obter_do_usuario_na_empresa`, `listar_ativos_do_usuario` e `contar_administradores_ativos` (com `FOR UPDATE`)
- [X] T005 [P] Testes em `tests/identidade/integracao/test_permissoes.py`: administrador do sistema; administrador da empresa ativo; vínculo desativado, empresa desativada, vínculo comum e outra empresa recusados; quem pode ver um usuário
- [X] T006 Implementar `Permissoes` em `src/assura/identidade/aplicacao/permissoes.py`

## Fase 2: Casos de uso com solicitante

- [X] T007 Trocar `autor` por `solicitante` em todos os casos de uso de `identidade` com a permissão da tabela de research.md; ajustar testes existentes para usar `SOLICITANTE` (administrador do sistema); recusas por permissão reunidas em `tests/identidade/integracao/test_permissoes_dos_casos_de_uso.py`

## Fase 3: História 1 - Papel de administrador (P1)

- [X] T008 [P] [US1] Testes em `tests/identidade/integracao/test_administrador_da_empresa.py`: tornar e remover com registros; último administrador protegido ao remover papel e ao desativar vínculo; vínculo desativado; sem permissão; administrador da empresa torna outro
- [X] T009 [US1] Implementar `TornarAdministrador` e `RemoverAdministrador` e a proteção do último em `DesativarVinculo`

## Fase 4: História 2 - Incluir usuário na empresa (P1)

- [X] T010 [P] [US2] Testes em `tests/identidade/integracao/test_incluir_usuario_na_empresa.py`: e-mail novo cadastra e vincula; e-mail existente só vincula sem mudar nome; já vinculado; outra empresa recusada
- [X] T011 [US2] Implementar `IncluirUsuarioNaEmpresa`

## Fase 5: História 3 - Redefinição pelo administrador da empresa (P1)

- [X] T012 [P] [US3] Testes em `tests/identidade/integracao/test_redefinir_senha.py`: alvo só da empresa (aceito); alvo em duas empresas (recusado); alvo administrador do sistema (recusado)
- [X] T013 [US3] Implementar a regra em `RedefinirSenha`

## Fase 6: História 4 - Rotas HTTP (P2)

- [X] T014 Tradução de erros por categoria em `src/assura/compartilhado/infraestrutura/http.py`; contextos registram suas categorias
- [X] T015 [P] [US4] Testes HTTP em `tests/identidade/http/`: empresas, usuários, vínculos, histórico (permissão e isolamento com duas empresas) e o fluxo completo `test_fluxo_da_etapa_1.py`
- [X] T016 [US4] Implementar as rotas conforme `contracts/http.md` em `src/assura/identidade/infraestrutura/` e `src/assura/historico/infraestrutura/http.py`; registrar em `src/assura/main.py`

## Fase 7: Acabamento

- [X] T017 [P] `ruff`, `mypy`
- [X] T018 Executar `quickstart.md` (ida e volta da migração 0005)

## Dependências

Fase 1 → Fase 2 → Histórias 1, 2 e 3 → História 4.
