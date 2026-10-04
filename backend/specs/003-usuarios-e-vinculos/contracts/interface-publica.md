# Contrato: interface pública do contexto `identidade` (usuários e vínculos)

Sem endpoint HTTP. Casos de uso recebem a sessão de quem chama e não fazem commit.

```python
from assura.historico import Autor, Pagina, RegistrarAcao, criar_historico
from assura.identidade import (
    AlterarUsuario,
    CadastrarUsuario,
    ConsultarUsuarios,
    DesativarVinculo,
    ReativarVinculo,
    SituacaoDoVinculo,
    VincularUsuario,
    criar_empresas,
    criar_usuarios,
    criar_vinculos,
)

usuarios, vinculos, empresas = criar_usuarios(sessao), criar_vinculos(sessao), criar_empresas(sessao)
registrar_acao = RegistrarAcao(criar_historico(sessao))

usuario = CadastrarUsuario(usuarios, registrar_acao).executar(
    autor=autor, nome="Maria Souza", email="Maria@Empresa.com"
)
AlterarUsuario(usuarios, registrar_acao).executar(
    autor=autor, usuario_id=usuario.id, nome="Maria S. Souza", email="maria@empresa.com"
)
vinculo = VincularUsuario(usuarios, empresas, vinculos, registrar_acao).executar(
    autor=autor, usuario_id=usuario.id, empresa_id=empresa_id
)
DesativarVinculo(vinculos, registrar_acao).executar(autor=autor, vinculo_id=vinculo.id)
ReativarVinculo(vinculos, registrar_acao).executar(autor=autor, vinculo_id=vinculo.id)

consultar = ConsultarUsuarios(usuarios, vinculos)
consultar.obter(usuario.id)
consultar.listar_da_empresa(empresa_id, situacao=SituacaoDoVinculo.ATIVO, pagina=Pagina())
```

| Caso de uso | Erros |
|---|---|
| CadastrarUsuario | `EmailInvalido`, `EmailJaCadastrado`, `NomeDeUsuarioInvalido` |
| AlterarUsuario | os do cadastro e `UsuarioNaoEncontrado` |
| VincularUsuario | `UsuarioNaoEncontrado`, `EmpresaNaoEncontrada`, `EmpresaDesativadaNaoAceitaVinculo`, `VinculoJaExiste` |
| DesativarVinculo / ReativarVinculo | `VinculoNaoEncontrado`, `VinculoJaDesativado` / `VinculoJaAtivo` |
| ConsultarUsuarios.obter | `UsuarioNaoEncontrado` |

Registros de histórico:

| Ação | Tipo | Objeto | Empresa | Detalhes |
|---|---|---|---|---|
| cadastrar usuário | `usuario_cadastrado` | `usuario/<id>` | nenhuma | vazio |
| alterar usuário | `usuario_alterado` | `usuario/<id>` | nenhuma | campos alterados com anterior e novo |
| vincular | `usuario_vinculado` | `vinculo/<id>` | a do vínculo | `usuario_id` |
| desativar vínculo | `vinculo_desativado` | `vinculo/<id>` | a do vínculo | `usuario_id` |
| reativar vínculo | `vinculo_reativado` | `vinculo/<id>` | a do vínculo | `usuario_id` |
