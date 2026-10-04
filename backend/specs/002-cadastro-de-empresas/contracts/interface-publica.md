# Contrato: interface pública do contexto `identidade` (empresas)

Sem endpoint HTTP nesta funcionalidade. Todos os casos de uso recebem a sessão da transação de quem
chama e não fazem commit; o histórico é gravado na mesma sessão.

```python
from assura.historico import Autor, Pagina, RegistrarAcao, criar_historico
from assura.identidade import (
    AlterarEmpresa,
    CadastrarEmpresa,
    ConsultarEmpresas,
    DesativarEmpresa,
    ReativarEmpresa,
    SituacaoDaEmpresa,
    criar_empresas,
)

empresas = criar_empresas(sessao)
registrar_acao = RegistrarAcao(criar_historico(sessao))

empresa = CadastrarEmpresa(empresas, registrar_acao).executar(
    autor=Autor.usuario(usuario_id),
    razao_social="Empresa X Ltda",
    nome_fantasia="Empresa X",  # ou None
    cnpj="12.345.678/0001-95",  # numérico ou alfanumérico, com ou sem máscara
)
AlterarEmpresa(empresas, registrar_acao).executar(
    autor=autor, empresa_id=empresa.id, razao_social="...", nome_fantasia=None, cnpj="...",
)
DesativarEmpresa(empresas, registrar_acao).executar(autor=autor, empresa_id=empresa.id)
ReativarEmpresa(empresas, registrar_acao).executar(autor=autor, empresa_id=empresa.id)

consultar = ConsultarEmpresas(empresas)
consultar.obter(empresa.id)
consultar.listar(situacao=SituacaoDaEmpresa.ATIVA, pagina=Pagina())  # situacao=None: todas
```

| Caso de uso | Erros |
|---|---|
| CadastrarEmpresa | `CnpjInvalido`, `CnpjJaCadastrado`, `RazaoSocialInvalida`, `NomeFantasiaInvalido` |
| AlterarEmpresa | os do cadastro e `EmpresaNaoEncontrada` |
| DesativarEmpresa | `EmpresaNaoEncontrada`, `EmpresaJaDesativada` |
| ReativarEmpresa | `EmpresaNaoEncontrada`, `EmpresaJaAtiva` |
| ConsultarEmpresas.obter | `EmpresaNaoEncontrada` |

Registros de histórico gerados (objeto `empresa`/`<id>`, empresa do registro = a própria):

| Ação | Tipo | Detalhes |
|---|---|---|
| cadastro | `empresa_cadastrada` | `razao_social`, `nome_fantasia`, `cnpj` |
| alteração | `empresa_alterada` | `{campo: {"anterior": ..., "novo": ...}}` só dos campos alterados |
| desativação | `empresa_desativada` | vazio |
| reativação | `empresa_reativada` | vazio |
