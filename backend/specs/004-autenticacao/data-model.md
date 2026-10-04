# Modelo de dados: Autenticação

## Domínio

### Usuario (alterado)

| Atributo novo | Regra |
|---|---|
| resumo_da_senha | resumo argon2id ou nenhum (usuário que ainda não recebeu senha) |
| senha_provisoria | verdadeiro após redefinição pelo administrador; falso após troca pelo usuário |
| administrador_do_sistema | verdadeiro só para o root nesta etapa |

Métodos: `definir_senha_provisoria(resumo)`, `definir_senha_definitiva(resumo)`,
`tem_senha` (propriedade).

### Senha

`validar_senha(texto)`: 8 a 128 caracteres, senão `SenhaInvalida`. A senha nunca é guardada.

### UsuarioAutenticado (leitura)

`id`, `administrador_do_sistema`, `senha_provisoria`: o que as regras de permissão precisam.

### Erros novos

`SenhaInvalida`, `CredenciaisInvalidas`, `SenhaAtualIncorreta`, `PermissaoNegada`,
`SenhaProvisoriaPrecisaSerTrocada`, `AdministradorDoSistemaJaExiste`, `SessaoInvalida`.

## Banco: `usuario` (migração 0004)

| Coluna nova | Tipo | Restrição |
|---|---|---|
| resumo_da_senha | text | nulo permitido |
| senha_provisoria | boolean | não nulo, padrão `false`; `CHECK (NOT senha_provisoria OR resumo_da_senha IS NOT NULL)` |
| administrador_do_sistema | boolean | não nulo, padrão `false` |
