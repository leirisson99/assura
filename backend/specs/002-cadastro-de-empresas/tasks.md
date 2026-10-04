# Tarefas: Cadastro de empresas

**Entrada**: documentos de design em `specs/002-cadastro-de-empresas/`
**Pré-requisitos**: plan.md, spec.md, research.md, data-model.md, contracts/interface-publica.md

**Testes**: obrigatórios (TDD da constituição); escritos antes e vistos falhar.

**Formato**: `[ID] [P?] [História] Descrição`. Caminhos relativos a `backend/`.

## Fase 1: Preparação

- [X] T001 Criar os pacotes `src/assura/compartilhado/dominio/`, `src/assura/identidade/{dominio,aplicacao,infraestrutura}/` e `tests/identidade/{unidade,integracao}/` com `__init__.py`

## Fase 2: Fundação (bloqueia todas as histórias)

- [X] T002 Mover `Pagina`, `PaginaInvalida`, `TAMANHO_DE_PAGINA_PADRAO` e `TAMANHO_DE_PAGINA_MAXIMO` para `src/assura/compartilhado/dominio/pagina.py`; ajustar `src/assura/historico/dominio/consulta.py`, `src/assura/historico/dominio/erros.py`, `src/assura/historico/__init__.py` e `tests/historico/unidade/test_consulta.py`
- [X] T003 Acrescentar `EMPRESA_CADASTRADA`, `EMPRESA_ALTERADA`, `EMPRESA_DESATIVADA` e `EMPRESA_REATIVADA` em `TipoDeAcao` (`src/assura/historico/dominio/registro_de_historico.py`); remover `tests/historico/tipos_de_teste.py` e usar os tipos reais nos testes do histórico
- [X] T004 [P] Testes do CNPJ em `tests/identidade/unidade/test_cnpj.py`: numérico válido com e sem máscara, alfanumérico válido (inclusive minúsculas), dígitos errados, tamanho errado, caracteres fora de `[0-9A-Z]` nos 12 primeiros ou letra nos 2 últimos, "um só caractere repetido", formatação `XX.XXX.XXX/XXXX-XX`
- [X] T005 [P] Testes da empresa em `tests/identidade/unidade/test_empresa.py`: nasce ativa; razão social "obrigatória, sem espaços nas pontas, até 150 caracteres"; nome fantasia "opcional; vazio vira nenhum; até 150 caracteres"; desativar e reativar com `EmpresaJaDesativada`/`EmpresaJaAtiva`; `alterar_dados` devolve só os campos alterados com anterior e novo
- [X] T006 Implementar `Cnpj` em `src/assura/identidade/dominio/cnpj.py` e os erros em `src/assura/identidade/dominio/erros.py`
- [X] T007 Implementar `Empresa` e `SituacaoDaEmpresa` em `src/assura/identidade/dominio/empresa.py`
- [X] T008 Criar a porta `Empresas` (adicionar, atualizar, obter, existe_cnpj, listar) em `src/assura/identidade/aplicacao/portas.py`
- [X] T009 Criar a tabela `empresa` em `src/assura/identidade/infraestrutura/tabela.py` conforme data-model.md (`CHECK (char_length(razao_social) BETWEEN 1 AND 150)`, `cnpj` char(14) `UNIQUE`, `CHECK (situacao IN ('ativa', 'desativada'))`) e a chave estrangeira `empresa_id → empresa.id` em `src/assura/historico/infraestrutura/tabela.py`
- [X] T010 Criar a migração `migrations/versions/0002_criar_empresa.py` (tabela, restrições, chave estrangeira do histórico; `downgrade` reverte) e importar a tabela em `migrations/env.py`
- [X] T011 Criar a fixture `criar_empresa` em `tests/conftest.py` (grava direto na tabela `empresa` com CNPJ gerado) e usá-la nos testes de integração do histórico no lugar de `uuid4()`; acrescentar teste em `tests/historico/integracao/test_registrar_acao.py` de que empresa inexistente é recusada

## Fase 3: História 1 - Cadastrar uma empresa (P1) — MVP

- [X] T012 [P] [US1] Testes em `tests/identidade/integracao/test_cadastrar_empresa.py`: empresa gravada e ativa; CNPJ guardado sem máscara; alfanumérico aceito; CNPJ repetido (ativa ou desativada) recusado; registro `empresa_cadastrada` com autor, objeto, empresa e detalhes; dados inválidos não gravam nada; violação da restrição única do banco vira `CnpjJaCadastrado`
- [X] T013 [US1] Implementar `CadastrarEmpresa` em `src/assura/identidade/aplicacao/cadastrar_empresa.py`
- [X] T014 [US1] Implementar `EmpresasSqlAlchemy.adicionar`, `existe_cnpj`, `obter` e `criar_empresas` em `src/assura/identidade/infraestrutura/empresas_sqlalchemy.py`
- [X] T015 [US1] Exportar a interface pública em `src/assura/identidade/__init__.py`

## Fase 4: História 2 - Alterar os dados (P2)

- [X] T016 [P] [US2] Testes em `tests/identidade/integracao/test_alterar_empresa.py`: alteração gravada; registro `empresa_alterada` só com campos alterados; sem mudança não grava registro; CNPJ de outra empresa recusado; empresa desativada pode ser alterada; empresa inexistente
- [X] T017 [US2] Implementar `AlterarEmpresa` em `src/assura/identidade/aplicacao/alterar_empresa.py` e `EmpresasSqlAlchemy.atualizar`

## Fase 5: História 3 - Desativar e reativar (P2)

- [X] T018 [P] [US3] Testes em `tests/identidade/integracao/test_mudar_situacao_da_empresa.py`: desativar e reativar gravam a situação e os registros `empresa_desativada`/`empresa_reativada`; repetir a ação é recusado sem registro; empresa inexistente
- [X] T019 [US3] Implementar `DesativarEmpresa` e `ReativarEmpresa` em `src/assura/identidade/aplicacao/mudar_situacao_da_empresa.py`

## Fase 6: História 4 - Consultar empresas (P3)

- [X] T020 [P] [US4] Testes em `tests/identidade/integracao/test_consultar_empresas.py`: obter por identificador; inexistente; listar todas, só ativas, só desativadas; ordem alfabética de razão social; paginação
- [X] T021 [US4] Implementar `ConsultarEmpresas` em `src/assura/identidade/aplicacao/consultar_empresas.py` e `EmpresasSqlAlchemy.listar`

## Fase 7: Acabamento

- [X] T022 [P] Rodar `ruff check`, `ruff format` e `mypy` e corrigir
- [X] T023 Executar `quickstart.md` (testes e ida e volta da migração 0002)

## Dependências

- Fase 1 → Fase 2 → História 1 → Histórias 2, 3 e 4 (independentes entre si; todas usam o cadastro
  para preparar dados).
- Paralelos: T004 e T005; os arquivos de teste de cada história.

## Estratégia

MVP = Fases 1 a 3 (empresas podem ser cadastradas e já aparecem no histórico). As histórias 2 a 4
completam o cadastro.
