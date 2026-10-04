# Modelo de dados: Histórico de ações

## Domínio

### RegistroDeHistorico (entidade imutável)

| Atributo | Tipo | Regra |
|---|---|---|
| id | UUID v7 | gerado no registro |
| autor | Autor | obrigatório |
| tipo_de_acao | TipoDeAcao | membro da enumeração; senão `TipoDeAcaoDesconhecido` |
| objeto | ObjetoAfetado | obrigatório |
| empresa_id | UUID ou nenhum | nenhum só para ações fora de empresa |
| registrado_em | data e hora com fuso | definida pelo `Relogio` do servidor |
| detalhes | dicionário JSON | padrão vazio |

Sem transições de estado: o registro nasce pronto e nunca muda.

### Autor (objeto de valor)

| Forma | tipo | usuario_id |
|---|---|---|
| `Autor.usuario(id)` | `usuario` | obrigatório |
| `Autor.sistema()` | `sistema` | nenhum |

### ObjetoAfetado (objeto de valor)

| Atributo | Regra |
|---|---|
| tipo | texto não vazio (ex.: `empresa`, `usuario`) |
| identificador | texto não vazio |

Texto vazio gera `ObjetoAfetadoInvalido`.

### SolicitanteDaConsulta (objeto de valor)

| Forma | Alcance |
|---|---|
| `administrador_do_sistema()` | todas as empresas e registros sem empresa |
| `administrador_da_empresa(empresa_id)` | apenas `empresa_id` |

### FiltroDoHistorico (objeto de valor)

Todos opcionais: `empresa_id`, `inicio`, `fim`, `autor`, `tipo_de_acao`, `objeto`.
`inicio` depois de `fim` gera `PeriodoInvalido`. Filtros informados combinam com "e".

### Pagina

`numero` (a partir de 1) e `tamanho` (1 a 200, padrão 50). Fora disso: `PaginaInvalida`.

### Erros do domínio

`TipoDeAcaoDesconhecido`, `ObjetoAfetadoInvalido`, `PeriodoInvalido`, `PaginaInvalida`,
`ConsultaAOutraEmpresaNaoPermitida`.

## Banco: tabela `registro_de_historico`

| Coluna | Tipo | Restrição |
|---|---|---|
| id | uuid | chave primária |
| autor_tipo | text | `CHECK (autor_tipo IN ('usuario','sistema'))` |
| autor_usuario_id | uuid | obrigatório se `autor_tipo = 'usuario'`, nulo se `sistema` (`CHECK`) |
| tipo_de_acao | text | não nulo |
| objeto_tipo | text | não nulo |
| objeto_id | text | não nulo |
| empresa_id | uuid | nulo permitido; chave estrangeira entra com a tabela de empresas (1.2) |
| registrado_em | timestamptz | não nulo |
| detalhes | jsonb | não nulo, padrão `{}` |

Índices: `(empresa_id, registrado_em DESC)`, `(objeto_tipo, objeto_id)`, `(autor_usuario_id)`.

Gatilhos: `BEFORE UPDATE OR DELETE FOR EACH ROW` e `BEFORE TRUNCATE FOR EACH STATEMENT`, ambos
executando `impedir_alteracao_do_historico()`, que lança exceção.
