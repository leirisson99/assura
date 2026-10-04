# Plano de implementação: Administrador da empresa

**Branch**: `005-administrador-da-empresa` | **Data**: 2026-10-04 | **Spec**: [spec.md](spec.md)

## Resumo

O `Vinculo` ganha `administrador_da_empresa`. Um serviço de aplicação `Permissoes` concentra as
regras de quem pode o quê (administrador do sistema; administrador ativo de empresa ativa). Todos os
casos de uso de `identidade` passam a receber o `solicitante` (`UsuarioAutenticado`) em vez do
`autor`, verificar a permissão e registrar o histórico com `Autor.usuario(solicitante.id)`. Casos de
uso novos: `TornarAdministrador`, `RemoverAdministrador`, `IncluirUsuarioNaEmpresa`. A regra do
último administrador usa bloqueio de linhas (`SELECT ... FOR UPDATE`) para resistir a ações
simultâneas. Rotas HTTP para empresas, usuários, vínculos e histórico, com tradução única de erros de
domínio para códigos HTTP.

## Contexto técnico

**Linguagem/Versão**: Python 3.14 · **Dependências**: nenhuma nova · **Armazenamento**: coluna
`vinculo.administrador_da_empresa` (migração `0005`) · **Testes**: pytest, unidade, integração e HTTP

## Verificação da constituição

| Princípio / padrão | Como esta funcionalidade atende | Situação |
|---|---|---|
| III. Rastreabilidade | Definir e remover administrador no histórico da empresa | OK |
| IV. Isolamento por empresa | Toda rota de empresa verifica o vínculo administrador; testes com duas empresas | OK |
| V. Papéis fixos | Administrador do sistema (no usuário) e administrador da empresa (no vínculo); último protegido | OK |
| IX. LGPD | Administrador de empresa só vê usuários de empresas em comum | OK |
| X. Simplicidade | Um serviço de permissões; sem permissões configuráveis | OK |
| DDD / TDD / Qualidade | Regras no domínio e na aplicação; HTTP só traduz; testes antes; migração reversível | OK |

**Reavaliação pós-design**: sem violações.

## Estrutura do projeto

```text
src/assura/
├── historico/dominio/registro_de_historico.py      # + ADMINISTRADOR_DEFINIDO, ADMINISTRADOR_REMOVIDO
├── compartilhado/infraestrutura/http.py             # sessão por requisição e tradução de erros
└── identidade/
    ├── dominio/{vinculo.py, erros.py}
    ├── aplicacao/{permissoes.py, administrador_da_empresa.py, incluir_usuario_na_empresa.py, ...}
    └── infraestrutura/{dependencias_http.py, respostas_http.py, http.py, rotas_de_empresas.py,
                        rotas_de_usuarios.py, rotas_de_vinculos.py, rotas_de_historico.py}

migrations/versions/0005_acrescentar_administrador_ao_vinculo.py
tests/identidade/{unidade, integracao, http}/
```

**Ajuste durante a implementação**: as rotas do histórico ficaram em `identidade`
(`rotas_de_historico.py`), porque quem pode consultar depende dos papéis, que são de identidade; o
contexto `historico` continua sem depender de `identidade`.

## Rastreamento de complexidade

Nenhuma violação a justificar.
