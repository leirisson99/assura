# Modelo de dados: Desativação de usuário

## Domínio

### Usuario (alterado)

| Atributo | Regra |
|---|---|
| situacao | `ativo` ou `desativado`; nasce `ativo` |

Métodos: `desativar()` (recusa quem já está desativado com `UsuarioJaDesativado`) e `reativar()`
(recusa quem já está ativo com `UsuarioJaAtivo`). Senha, dados e o indicador de administrador do
sistema não mudam.

Transições:

```text
ativo ──desativar()──► desativado
  ▲                        │
  └───────reativar()───────┘
```

### Regras na aplicação

Dependem de outros usuários e vínculos, por isso ficam nos casos de uso:

- `UltimoAdministradorNaoPodeSerRemovido` (existente): a empresa ficaria sem administrador ativo
  (usuário ativo, vínculo ativo e administrador).
- `UltimoAdministradorDoSistemaNaoPodeSerDesativado` (novo).

## Portas

| Porta | Mudança |
|---|---|
| `Vinculos.contar_administradores_ativos(empresa_id) -> int` | substituída por `listar_administradores_ativos(empresa_id) -> list[UUID]` (ids dos vínculos; junta `usuario`; bloqueia as linhas) |
| `Usuarios.contar_administradores_do_sistema_ativos() -> int` | nova |

## Banco: `usuario` (migração 0006)

| Restrição | Antes | Depois |
|---|---|---|
| `situacao_valida` | `situacao IN ('ativo')` | `situacao IN ('ativo', 'desativado')` |

Sem colunas novas. A volta recria a restrição antiga e falha se houver usuário desativado.

## Histórico

| Ação | Tipo | Objeto | Empresa | Detalhes |
|---|---|---|---|---|
| desativar usuário | `usuario_desativado` | `usuario/<id>` | nenhuma | — |
| reativar usuário | `usuario_reativado` | `usuario/<id>` | nenhuma | — |
