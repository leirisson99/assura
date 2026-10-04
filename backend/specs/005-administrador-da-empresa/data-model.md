# Modelo de dados: Administrador da empresa

## Domínio

### Vinculo (alterado)

| Atributo novo | Regra |
|---|---|
| administrador_da_empresa | falso ao criar |

Métodos: `tornar_administrador()` (recusa vínculo desativado com
`VinculoDesativadoNaoPodeSerAdministrador` e quem já é com `VinculoJaEAdministrador`) e
`remover_administrador()` (recusa quem não é com `VinculoNaoEAdministrador`).
`e_administrador_ativo` (propriedade): ativo e administrador.

A regra "último administrador" depende dos outros vínculos da empresa e fica no caso de uso:
`UltimoAdministradorNaoPodeSerRemovido`.

## Banco: `vinculo` (migração 0005)

| Coluna nova | Tipo | Restrição |
|---|---|---|
| administrador_da_empresa | boolean | não nulo, padrão `false` |

Índice parcial `ix_vinculo_administradores_ativos` em `empresa_id` onde
`administrador_da_empresa AND situacao = 'ativo'`.

## Histórico

| Ação | Tipo | Objeto | Empresa | Detalhes |
|---|---|---|---|---|
| tornar administrador | `administrador_definido` | `vinculo/<id>` | a do vínculo | `usuario_id` |
| remover administrador | `administrador_removido` | `vinculo/<id>` | a do vínculo | `usuario_id` |
