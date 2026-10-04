# Plano de implementação: Cadastro de empresas

**Branch**: `002-cadastro-de-empresas` | **Data**: 2026-10-04 | **Spec**: [spec.md](spec.md)

**Entrada**: especificação em `specs/002-cadastro-de-empresas/spec.md`

## Resumo

Criar o contexto `identidade` (identidade e acesso, da constituição) com a entidade `Empresa`, o
objeto de valor `Cnpj` (numérico e alfanumérico) e os casos de uso cadastrar, alterar, desativar,
reativar, obter e listar. Cada caso de uso que muda a empresa registra a ação pelo `RegistrarAcao`
do contexto `historico`, na mesma sessão. A migração `0002` cria a tabela `empresa` com CNPJ único e
liga `registro_de_historico.empresa_id` a ela. A paginação passa para `compartilhado` para ser usada
pelos dois contextos.

## Contexto técnico

**Linguagem/Versão**: Python 3.14

**Dependências principais**: SQLAlchemy 2.x, Alembic, psycopg 3 (nenhuma nova)

**Armazenamento**: PostgreSQL 17, tabela `empresa`

**Testes**: pytest; unidade sem banco e integração no banco `assura_teste`

**Tipo de projeto**: serviço web (backend)

**Metas de desempenho**: sem metas novas; volume de dezenas a centenas de empresas

**Restrições**: CNPJ único garantido pelo banco; sem exclusão; histórico na mesma transação

## Verificação da constituição

| Princípio / padrão | Como esta funcionalidade atende | Situação |
|---|---|---|
| I. Funciona sem IA | Sem IA | OK |
| III. Rastreabilidade | Toda mudança registrada no histórico; desativação em vez de exclusão | OK |
| IV. Isolamento por empresa | A empresa é a unidade de isolamento; registros de histórico da empresa usam o `empresa_id` dela | OK |
| V. Papéis fixos | Ação do administrador do sistema; verificação do papel chega com a autenticação (1.4) | OK, com premissa registrada |
| VII. Escopo por fases | Funcionalidade 1, P0 | OK |
| IX. LGPD | CNPJ e razão social não são dados pessoais | OK |
| X. Simplicidade | Um contexto, sem serviços novos; reaproveita `Pagina` | OK |
| DDD | Contexto `identidade`; usa o histórico só pela interface pública `assura.historico` | OK |
| TDD | Testes antes da implementação em cada história | OK |
| Qualidade | Migração reversível; unicidade testada | OK |

**Observação de DDD**: a chave estrangeira `registro_de_historico.empresa_id → empresa.id` liga as
tabelas dos dois contextos no banco. É integridade referencial, não acesso: nenhum código de um
contexto lê a tabela do outro.

**Reavaliação pós-design**: sem violações.

## Estrutura do projeto

### Documentação

```text
specs/002-cadastro-de-empresas/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
└── contracts/interface-publica.md
```

### Código-fonte

```text
src/assura/
├── compartilhado/dominio/pagina.py             # Pagina e PaginaInvalida (movidas do histórico)
├── historico/dominio/registro_de_historico.py  # + tipos EMPRESA_*
├── historico/infraestrutura/tabela.py          # + chave estrangeira para empresa
└── identidade/
    ├── __init__.py                             # interface pública
    ├── dominio/{cnpj.py, empresa.py, erros.py}
    ├── aplicacao/{portas.py, cadastrar_empresa.py, alterar_empresa.py,
    │              mudar_situacao_da_empresa.py, consultar_empresas.py}
    └── infraestrutura/{tabela.py, empresas_sqlalchemy.py}

migrations/versions/0002_criar_empresa.py

tests/
├── conftest.py                                 # + fixture criar_empresa
└── identidade/{unidade, integracao}/
```

**Decisão de estrutura**: o contexto se chama `identidade` porque a constituição lista "identidade e
acesso" como contexto inicial; usuários e vínculos (1.3) entram nele.

## Rastreamento de complexidade

Nenhuma violação a justificar.
