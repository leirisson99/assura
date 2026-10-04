# Modelo de dados: Cadastro de empresas

## Domínio

### Cnpj (objeto de valor)

| Atributo | Regra |
|---|---|
| valor | 14 caracteres sem máscara: 12 de `[0-9A-Z]` + 2 dígitos verificadores; não pode ser um só caractere repetido |
| formatado | `XX.XXX.XXX/XXXX-XX` |

`Cnpj.criar(texto)` normaliza (pontas, máscara, maiúsculas) e valida; inválido gera `CnpjInvalido`.

### Empresa (entidade)

| Atributo | Regra |
|---|---|
| id | UUID v7 |
| razao_social | obrigatória, sem espaços nas pontas, até 150 caracteres (`RazaoSocialInvalida`) |
| nome_fantasia | opcional; vazio vira nenhum; até 150 caracteres (`NomeFantasiaInvalido`) |
| cnpj | `Cnpj` |
| situacao | `ativa` ou `desativada`; nasce `ativa` |

Transições: `ativa → desativada` (`desativar`, senão `EmpresaJaDesativada`) e
`desativada → ativa` (`reativar`, senão `EmpresaJaAtiva`). `alterar_dados` vale nas duas situações e
devolve os campos alterados.

### Erros

`CnpjInvalido`, `CnpjJaCadastrado`, `RazaoSocialInvalida`, `NomeFantasiaInvalido`,
`EmpresaNaoEncontrada`, `EmpresaJaDesativada`, `EmpresaJaAtiva`.

## Banco: tabela `empresa`

| Coluna | Tipo | Restrição |
|---|---|---|
| id | uuid | chave primária |
| razao_social | text | não nulo, `CHECK (char_length(razao_social) BETWEEN 1 AND 150)` |
| nome_fantasia | text | nulo permitido, `CHECK (char_length(nome_fantasia) BETWEEN 1 AND 150)` |
| cnpj | char(14) | não nulo, `UNIQUE` |
| situacao | text | `CHECK (situacao IN ('ativa', 'desativada'))` |

Alteração em `registro_de_historico`: chave estrangeira `empresa_id → empresa.id`.
