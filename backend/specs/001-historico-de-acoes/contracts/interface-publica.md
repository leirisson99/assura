# Contrato: interface pública do contexto `historico`

Outros contextos usam o histórico apenas pelo que `assura.historico` exporta (padrão DDD da
constituição: um contexto só acessa outro pela interface pública, nunca pelas tabelas).
Nenhum endpoint HTTP nesta funcionalidade.

## Registrar uma ação

```python
from assura.historico import Autor, ObjetoAfetado, RegistrarAcao, TipoDeAcao, criar_historico

registrar_acao = RegistrarAcao(criar_historico(sessao))
registro = registrar_acao.executar(
    autor=Autor.usuario(usuario_id),
    tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,  # membro acrescentado pela funcionalidade 1.2
    objeto=ObjetoAfetado(tipo="empresa", identificador=str(empresa_id)),
    empresa_id=empresa_id,  # None só para ações fora de empresa
    detalhes={"nome": "Empresa X"},
)
```

- `sessao` é a mesma sessão em que a ação de negócio grava sua mudança. `RegistrarAcao` não faz
  commit; quem abriu a transação confirma tudo de uma vez.
- Erros: `TipoDeAcaoDesconhecido`, `ObjetoAfetadoInvalido`.
- Retorna o `RegistroDeHistorico` criado.

## Consultar

```python
from assura.historico import ConsultarHistorico, FiltroDoHistorico, Pagina, SolicitanteDaConsulta

consultar = ConsultarHistorico(criar_historico(sessao))
registros = consultar.executar(
    solicitante=SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
    filtro=FiltroDoHistorico(objeto=ObjetoAfetado(tipo="empresa", identificador="...")),
    pagina=Pagina(numero=1, tamanho=50),
)
```

- Retorna lista de `RegistroDeHistorico`, do mais recente para o mais antigo.
- Erros: `ConsultaAOutraEmpresaNaoPermitida`, `PeriodoInvalido`, `PaginaInvalida`.

## Acrescentar um tipo de ação

Cada funcionalidade adiciona membros em `TipoDeAcao`
(`src/assura/historico/dominio/registro_de_historico.py`), com valor em `snake_case` no passado:
`EMPRESA_CADASTRADA = "empresa_cadastrada"`. Não é preciso migração.
