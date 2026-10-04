# Tarefas: Histórico de ações

**Entrada**: documentos de design em `specs/001-historico-de-acoes/`
**Pré-requisitos**: plan.md, spec.md, research.md, data-model.md, contracts/interface-publica.md

**Testes**: obrigatórios (TDD é padrão da constituição). Em cada história, os testes são escritos
primeiro e devem falhar antes da implementação.

**Formato**: `[ID] [P?] [História] Descrição`. `[P]` indica tarefa paralelizável (arquivos
diferentes, sem dependência pendente). Caminhos relativos a `backend/`.

## Fase 1: Preparação

- [X] T001 Criar os pacotes do contexto: `src/assura/compartilhado/__init__.py`, `src/assura/compartilhado/infraestrutura/__init__.py`, `src/assura/historico/{__init__,dominio/__init__,aplicacao/__init__,infraestrutura/__init__}.py` e `tests/historico/{__init__,unidade/__init__,integracao/__init__}.py`
- [X] T002 [P] Acrescentar `url_banco_de_dados_de_teste` (padrão `postgresql+psycopg://assura:assura@localhost:5433/assura_teste`) em `src/assura/configuracao.py` e em `.env.example`

## Fase 2: Fundação (bloqueia todas as histórias)

- [X] T003 Criar `src/assura/compartilhado/infraestrutura/banco.py` com `metadados` (MetaData com convenção de nomes), `criar_motor(url)` e `criar_fabrica_de_sessoes(motor)`
- [X] T004 Criar o domínio em `src/assura/historico/dominio/registro_de_historico.py`: `TipoDeAcao(StrEnum)` sem membros; `TipoDeAutor` (`usuario`, `sistema`); `Autor` com `Autor.usuario(id)` e `Autor.sistema()`; `ObjetoAfetado(tipo, identificador)` que recusa texto vazio com `ObjetoAfetadoInvalido`; `RegistroDeHistorico` imutável (`frozen`) com `id`, `autor`, `tipo_de_acao`, `objeto`, `empresa_id` (opcional), `registrado_em`, `detalhes` e fábrica `RegistroDeHistorico.criar(...)` que gera UUID v7 e recusa tipo fora de `TipoDeAcao` com `TipoDeAcaoDesconhecido`
- [X] T005 [P] Criar os erros em `src/assura/historico/dominio/erros.py`: `TipoDeAcaoDesconhecido`, `ObjetoAfetadoInvalido`, `PeriodoInvalido`, `PaginaInvalida`, `ConsultaAOutraEmpresaNaoPermitida`
- [X] T006 Criar a porta `HistoricoDeAcoes` (Protocol com `adicionar(registro)` e `consultar(filtro, pagina)`) e o tipo `Relogio` em `src/assura/historico/aplicacao/portas.py`
- [X] T007 Criar o mapeamento da tabela `registro_de_historico` em `src/assura/historico/infraestrutura/tabela.py` com as colunas de data-model.md: `autor_tipo` com `CHECK (autor_tipo IN ('usuario','sistema'))`, `autor_usuario_id` "obrigatório se `autor_tipo = 'usuario'`, nulo se `sistema`", `empresa_id` "nulo permitido", `detalhes` jsonb "não nulo, padrão `{}`" e os índices `(empresa_id, registrado_em DESC)`, `(objeto_tipo, objeto_id)`, `(autor_usuario_id)`
- [X] T008 Criar a migração `migrations/versions/0001_criar_registro_de_historico.py` com a tabela, os índices, a função `impedir_alteracao_do_historico()` e os gatilhos `BEFORE UPDATE OR DELETE FOR EACH ROW` e `BEFORE TRUNCATE FOR EACH STATEMENT`; `downgrade` remove tudo. Apontar `target_metadata` de `migrations/env.py` para `Base.metadata`
- [X] T009 Criar `tests/conftest.py`: cria o banco `assura_teste` se não existir, roda `alembic upgrade head` uma vez por sessão e fornece a fixture `sessao` dentro de transação externa desfeita no fim (`join_transaction_mode="create_savepoint"`); criar `tests/historico/tipos_de_teste.py` com `TipoDeAcaoDeTeste(TipoDeAcao)` contendo `ACAO_DE_EXEMPLO`

**Ponto de controle**: domínio, tabela e banco de teste prontos.

## Fase 3: História 1 - Registrar uma ação junto com a mudança (P1) — MVP

**Objetivo**: outras funcionalidades registram ações na mesma transação da mudança de negócio.
**Teste independente**: ação de exemplo gera exatamente um registro; falha em qualquer lado não grava nada.

### Testes da História 1 (escrever primeiro, ver falhar)

- [X] T010 [P] [US1] Testes de domínio em `tests/historico/unidade/test_registro_de_historico.py`: autor usuário exige id, autor sistema não tem id, objeto com texto vazio é recusado, tipo fora de `TipoDeAcao` é recusado, `registrado_em` vem do relógio e não de quem chama, ids gerados em sequência são crescentes
- [X] T011 [P] [US1] Testes de integração em `tests/historico/integracao/test_registrar_acao.py`: registro gravado com todos os campos; registro sem empresa; falha da ação depois do registro desfaz os dois; falha ao gravar o histórico desfaz a mudança de negócio (usar tabela de exemplo criada no próprio teste)

### Implementação da História 1

- [X] T012 [US1] Implementar `RegistrarAcao` em `src/assura/historico/aplicacao/registrar_acao.py` (recebe `HistoricoDeAcoes` e `Relogio`, cria o registro e adiciona sem commit)
- [X] T013 [US1] Implementar `HistoricoDeAcoesSqlAlchemy.adicionar` e `criar_historico(sessao)` em `src/assura/historico/infraestrutura/historico_sqlalchemy.py`
- [X] T014 [US1] Exportar a interface pública em `src/assura/historico/__init__.py` conforme `contracts/interface-publica.md`

**Ponto de controle**: História 1 funcional e testada.

## Fase 4: História 2 - Histórico não pode ser alterado nem apagado (P1)

**Objetivo**: imutabilidade garantida pela aplicação e pelo banco.
**Teste independente**: `UPDATE`, `DELETE` e `TRUNCATE` diretos são rejeitados e o registro continua igual.

- [X] T015 [P] [US2] Testes em `tests/historico/integracao/test_imutabilidade.py`: `UPDATE`, `DELETE` e `TRUNCATE` por SQL direto lançam erro com a mensagem do gatilho; registro permanece igual; `HistoricoDeAcoes` não expõe método de alterar ou excluir
- [X] T016 [P] [US2] Teste em `tests/historico/integracao/test_migracao.py`: `alembic downgrade base` e `upgrade head` funcionam (migração reversível)
- [X] T017 [US2] Ajustar a migração de T008 se algum teste de T015 ou T016 falhar

**Ponto de controle**: Princípio III coberto por testes.

## Fase 5: História 3 - Consultar com filtros, respeitando a empresa (P2)

**Objetivo**: administrador da empresa vê só a dele; administrador do sistema vê tudo.
**Teste independente**: registros em duas empresas e sem empresa; cada solicitante vê só o seu alcance.

### Testes da História 3 (escrever primeiro, ver falhar)

- [X] T018 [P] [US3] Testes de domínio em `tests/historico/unidade/test_consulta.py`: administrador da empresa só consulta a própria (`ConsultaAOutraEmpresaNaoPermitida` para outra); administrador do sistema consulta qualquer uma ou todas; `inicio` depois de `fim` gera `PeriodoInvalido`; página fora de "1 a 200, padrão 50" gera `PaginaInvalida`
- [X] T019 [P] [US3] Testes de integração em `tests/historico/integracao/test_consultar_historico.py`: isolamento entre empresas A e B; registros sem empresa só para o administrador do sistema; cada filtro (período, autor, tipo de ação, objeto) e combinação; ordem do mais recente para o mais antigo; paginação; lista vazia sem erro

### Implementação da História 3

- [X] T020 [US3] Criar `SolicitanteDaConsulta`, `FiltroDoHistorico` e `Pagina` em `src/assura/historico/dominio/consulta.py`, com o cálculo da empresa efetiva da consulta
- [X] T021 [US3] Implementar `ConsultarHistorico` em `src/assura/historico/aplicacao/consultar_historico.py`
- [X] T022 [US3] Implementar `HistoricoDeAcoesSqlAlchemy.consultar` com filtros, ordem `registrado_em DESC, id DESC` e paginação em `src/assura/historico/infraestrutura/historico_sqlalchemy.py`
- [X] T023 [US3] Exportar `ConsultarHistorico`, `SolicitanteDaConsulta`, `FiltroDoHistorico` e `Pagina` em `src/assura/historico/__init__.py`

**Ponto de controle**: as três histórias funcionam de forma independente.

## Fase 6: Acabamento

- [X] T024 [P] Rodar `ruff check`, `ruff format` e `mypy` (estrito) e corrigir o que aparecer
- [X] T025 [P] Atualizar `README.md` da raiz com o banco de teste e o comando `pytest`
- [X] T026 Executar os passos de `quickstart.md`, incluindo a conferência manual da imutabilidade

## Dependências e ordem

- Fase 1 → Fase 2 → Histórias. As histórias 1 e 2 dependem só da Fase 2 (a 2 usa a migração de T008 e
  registros gravados pela infraestrutura de T013, então roda depois da 1). A História 3 depende da 1.
- Dentro de cada história: testes → domínio → aplicação → infraestrutura → exportação.

### Paralelismo

- Fase 2: T005 em paralelo com T004.
- História 1: T010 e T011 juntos.
- História 2: T015 e T016 juntos.
- História 3: T018 e T019 juntos.

## Estratégia

1. MVP = Fases 1, 2 e 3: as próximas funcionalidades (1.2 em diante) já podem registrar ações.
2. Fase 4 fecha a exigência de imutabilidade (obrigatória pela constituição antes da entrega).
3. Fase 5 entrega a consulta, que será exposta por HTTP junto com a autenticação (1.4).
