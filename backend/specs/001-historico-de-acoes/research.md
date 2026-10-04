# Pesquisa: Histórico de ações

## 1. Gravação conjunta com a ação de negócio

- **Decisão**: o caso de uso `RegistrarAcao` recebe um `HistoricoDeAcoes` ligado à sessão do
  banco de quem chama e só adiciona o registro à sessão. Quem controla a transação (o caso de uso de
  negócio ou, no futuro, a camada HTTP) faz o commit uma única vez.
- **Motivo**: uma transação do banco é o mecanismo mais simples para "os dois ou nenhum" (RF-004).
- **Alternativas rejeitadas**: eventos de domínio com publicação depois do commit (mais partes e
  risco de perder o registro); tabela de saída com processamento assíncrono (fila, contra o
  Princípio X).

## 2. Imutabilidade no banco

- **Decisão**: função PL/pgSQL `impedir_alteracao_do_historico()` acionada por gatilhos
  `BEFORE UPDATE OR DELETE` (por linha) e `BEFORE TRUNCATE` (por comando), que lançam exceção.
- **Motivo**: rejeita alteração mesmo fora da aplicação (RF-006) e vale para qualquer usuário do
  banco, inclusive o da aplicação.
- **Alternativas rejeitadas**: só `REVOKE UPDATE, DELETE` (não protege o dono da tabela, que hoje é
  o mesmo usuário da aplicação); regras `CREATE RULE ... DO INSTEAD NOTHING` (ignoram em silêncio, sem
  erro visível).
- **Observação**: a migração de reversão (`downgrade`) remove gatilhos, função e tabela. Isso é
  operação de esquema, não da aplicação, e atende "toda migração é reversível".

## 3. Data e hora do registro

- **Decisão**: definida pelo servidor da aplicação por um `Relogio` injetado (padrão:
  `datetime.now(UTC)`), gravada como `timestamptz`. Quem chama `RegistrarAcao` não informa a data.
- **Motivo**: RF-003; o relógio injetado permite testar filtros por período sem esperar o tempo.
- **Alternativa rejeitada**: `now()` do PostgreSQL como padrão da coluna; é a hora de início da
  transação (igual para todas as ações da mesma transação) e dificulta testar filtros por período.

## 4. Identificador e ordem estável

- **Decisão**: identificador UUID versão 7 (`uuid.uuid7()`, disponível no Python 3.14). A ordenação
  é `registrado_em DESC, id DESC`.
- **Motivo**: UUIDv7 é ordenado pelo tempo de criação, o que desempata ações no mesmo instante sem
  coluna extra.

## 5. Tipos de ação como lista fechada

- **Decisão**: enumeração `TipoDeAcao(StrEnum)` no domínio do histórico. Cada funcionalidade
  acrescenta os seus membros a ela. Nesta funcionalidade a enumeração nasce sem membros de negócio,
  porque nenhuma ação de negócio existe ainda; os testes declaram uma subclasse com uma ação de
  exemplo (enumerações sem membros podem ser estendidas em Python). O registro recusa qualquer valor
  que não seja membro de `TipoDeAcao` (RF-007).
- **Motivo**: lista fechada e nomeada, sem textos soltos (código limpo), sem criar tipos para
  funcionalidades que ainda não existem (Princípio X).
- **Alternativa rejeitada**: restrição `CHECK` no banco com a lista; exigiria migração a cada novo
  tipo e duplicaria a regra.

## 6. Autor

- **Decisão**: objeto de valor `Autor` com duas formas: `Autor.usuario(id)` e `Autor.sistema()`.
  No banco: `autor_tipo` (`usuario` ou `sistema`) e `autor_usuario_id` (obrigatório só para
  `usuario`, garantido por `CHECK`).
- **Motivo**: casos de borda da spec (ação automática registrada como "sistema"). Ainda não existe
  tabela de usuários, então `autor_usuario_id` não tem chave estrangeira; ela entra na etapa 1.3.

## 7. Consulta e alcance

- **Decisão**: `SolicitanteDaConsulta` com duas formas: `administrador_do_sistema()` e
  `administrador_da_empresa(empresa_id)`. O domínio calcula a empresa efetiva da consulta: o
  administrador da empresa sempre consulta só a dele e recebe `ConsultaAOutraEmpresaNaoPermitida`
  se pedir outra.
- **Paginação**: por número de página e tamanho (padrão 50, máximo 200). Simples e suficiente para o
  volume previsto (Princípio X); paginação por cursor fica para quando houver necessidade medida.
- **Índices**: `(empresa_id, registrado_em DESC)`, `(objeto_tipo, objeto_id)`,
  `(autor_usuario_id)` para atender CS-004.

## 8. Banco de teste

- **Decisão**: banco `assura_teste` no mesmo PostgreSQL do docker-compose, criado pelo `conftest.py`
  se não existir, com `alembic upgrade head` no início da sessão de testes. Cada teste roda dentro de
  uma transação externa desfeita no fim (sessão com `join_transaction_mode="create_savepoint"`).
- **Motivo**: integração com banco real (padrão TDD da constituição) sem precisar apagar registros, o
  que os gatilhos impediriam.
