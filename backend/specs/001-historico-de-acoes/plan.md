# Plano de implementação: Histórico de ações

**Branch**: `001-historico-de-acoes` | **Data**: 2026-10-04 | **Spec**: [spec.md](spec.md)

**Entrada**: especificação em `specs/001-historico-de-acoes/spec.md`

## Resumo

Criar o contexto `historico` com a capacidade de registrar ações (autor, tipo de ação, objeto,
empresa, data e hora, detalhes) e de consultá-las com filtros, respeitando o alcance de quem consulta.
O registro usa a mesma transação da ação de negócio de quem chama, o que garante a gravação conjunta.
A imutabilidade é garantida em duas camadas: a aplicação não tem operação de alterar ou excluir, e o
PostgreSQL rejeita `UPDATE`, `DELETE` e `TRUNCATE` na tabela por gatilho. Nenhum endpoint HTTP novo
nesta funcionalidade (ver premissas da spec).

## Contexto técnico

**Linguagem/Versão**: Python 3.14

**Dependências principais**: FastAPI (sem uso novo aqui), SQLAlchemy 2.x, Alembic, psycopg 3

**Armazenamento**: PostgreSQL 17 (tabela `registro_de_historico`, detalhes em JSONB)

**Testes**: pytest; unidade sem banco, integração com PostgreSQL real em banco `assura_teste`

**Plataforma**: servidor Linux/Windows com Docker para o banco

**Tipo de projeto**: serviço web (backend de aplicação web)

**Metas de desempenho**: consulta por objeto em histórico de 100 mil registros em até 2 s (CS-004)

**Restrições**: registro só de inserção; mesma transação da ação de negócio

**Escala**: dezenas de empresas, centenas de milhares de registros no primeiro ano

## Verificação da constituição

*PORTÃO: deve passar antes da Fase 0. Reavaliado depois da Fase 1.*

| Princípio / padrão | Como esta funcionalidade atende | Situação |
|---|---|---|
| I. Funciona sem IA | Nenhuma IA envolvida | OK |
| II. O auditor decide | O histórico registra quem decidiu; base para "quem e quando" | OK |
| III. Rastreabilidade e imutabilidade | É a própria implementação: tabela só de inserção, gatilho no banco | OK |
| IV. Isolamento por empresa | `empresa_id` na tabela; consulta filtrada pelo alcance do solicitante; testes obrigatórios | OK |
| V. Papéis fixos | Usa apenas administrador do sistema e administrador da empresa | OK |
| VI. Campo primeiro | Não se aplica (sem tela) | N/A |
| VII. Escopo por fases | Funcionalidade 10, P0, Fase 1 | OK |
| VIII. Preparado para IA | Nenhum código de IA | OK |
| IX. Privacidade e LGPD | Detalhes guardam só o necessário; consulta restrita a administradores | OK |
| X. Simplicidade | Um módulo, sem fila nem serviço separado; paginação simples por página | OK |
| DDD | Contexto `historico` com domínio, aplicação e infraestrutura; domínio sem SQLAlchemy | OK |
| TDD | Regras nascem de testes (ordem nas tarefas) | OK |
| Código limpo | Nomes em português do domínio; erros com nome do domínio | OK |
| Qualidade | Testes de isolamento e imutabilidade; migração versionada e reversível | OK |

**Exceção registrada**: `empresa_id` é opcional nesta tabela, porque ações do administrador do
sistema fora de empresa não pertencem a nenhuma. Registros sem empresa só aparecem para o
administrador do sistema, então o isolamento se mantém.

**Reavaliação pós-design**: sem violações. Nenhuma entrada em "Rastreamento de complexidade".

## Estrutura do projeto

### Documentação (esta funcionalidade)

```text
specs/001-historico-de-acoes/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── interface-publica.md
└── tasks.md             # gerado por /speckit-tasks
```

### Código-fonte

```text
src/assura/
├── compartilhado/
│   └── infraestrutura/
│       └── banco.py                  # metadados, motor e fábrica de sessões
└── historico/
    ├── __init__.py                   # interface pública do contexto
    ├── dominio/
    │   ├── registro_de_historico.py  # RegistroDeHistorico, Autor, ObjetoAfetado, TipoDeAcao
    │   ├── consulta.py               # SolicitanteDaConsulta, FiltroDoHistorico, Pagina
    │   └── erros.py
    ├── aplicacao/
    │   ├── portas.py                 # HistoricoDeAcoes (Protocol), Relogio
    │   ├── registrar_acao.py
    │   └── consultar_historico.py
    └── infraestrutura/
        ├── tabela.py                 # mapeamento SQLAlchemy
        └── historico_sqlalchemy.py   # implementação de HistoricoDeAcoes

migrations/versions/
└── 0001_criar_registro_de_historico.py

tests/
├── conftest.py                       # banco de teste, migração e sessão com rollback
└── historico/
    ├── unidade/
    └── integracao/
```

**Decisão de estrutura**: projeto único em `backend/`, organizado por contexto de negócio como
manda a constituição. `compartilhado/infraestrutura` guarda apenas o que todos os contextos usam
para falar com o banco.

## Rastreamento de complexidade

Nenhuma violação a justificar.
