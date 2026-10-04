# Modelo de dados: Usuários e vínculos com a empresa

## Domínio

### Email (objeto de valor)

`Email.criar(texto)`: tira espaços das pontas, converte para minúsculas e valida "parte local, `@`,
domínio com ponto, sem espaços, até 254 caracteres". Inválido gera `EmailInvalido`.

### Usuario (entidade)

| Atributo | Regra |
|---|---|
| id | UUID v7 |
| nome | obrigatório, sem espaços nas pontas, até 150 caracteres (`NomeDeUsuarioInvalido`) |
| email | `Email`, único |
| situacao | `ativo` (desativação na etapa 1.6) |

`alterar_dados(nome, email)` devolve só os campos alterados com anterior e novo.

### Vinculo (entidade)

| Atributo | Regra |
|---|---|
| id | UUID v7 |
| usuario_id | usuário cadastrado |
| empresa_id | empresa ativa no momento do vínculo |
| situacao | `ativo` ou `desativado`; nasce `ativo` |

Transições: `desativar` (senão `VinculoJaDesativado`) e `reativar` (senão `VinculoJaAtivo`).

### UsuarioDaEmpresa (leitura)

Par `(usuario, vinculo)` devolvido pela listagem de usuários de uma empresa.

### Erros

`EmailInvalido`, `EmailJaCadastrado`, `NomeDeUsuarioInvalido`, `UsuarioNaoEncontrado`,
`VinculoJaExiste`, `VinculoNaoEncontrado`, `VinculoJaDesativado`, `VinculoJaAtivo`,
`EmpresaDesativadaNaoAceitaVinculo`.

## Banco

### `usuario`

| Coluna | Tipo | Restrição |
|---|---|---|
| id | uuid | chave primária |
| nome | text | `CHECK (char_length(nome) BETWEEN 1 AND 150)` |
| email | text | `UNIQUE`, `CHECK (email = lower(email))`, `CHECK (char_length(email) <= 254)` |
| situacao | text | `CHECK (situacao IN ('ativo'))`, ampliado na 1.6 |

### `vinculo`

| Coluna | Tipo | Restrição |
|---|---|---|
| id | uuid | chave primária |
| usuario_id | uuid | chave estrangeira → `usuario.id` |
| empresa_id | uuid | chave estrangeira → `empresa.id` |
| situacao | text | `CHECK (situacao IN ('ativo', 'desativado'))` |

`UNIQUE (usuario_id, empresa_id)`; índice em `empresa_id`.

### `registro_de_historico`

Chave estrangeira `autor_usuario_id → usuario.id`.
