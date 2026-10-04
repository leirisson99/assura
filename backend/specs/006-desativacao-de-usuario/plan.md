# Plano de implementação: Desativação de usuário

**Branch**: `006-desativacao-de-usuario` | **Data**: 2026-10-04 | **Spec**: [spec.md](spec.md)

## Resumo

O `Usuario` ganha a situação `desativado`, com `desativar()` e `reativar()`. Casos de uso novos
`DesativarUsuario` e `ReativarUsuario`, exclusivos do administrador do sistema, com registro no
histórico sem empresa. O corte de acesso já existe (login e sessão conferem a situação a cada uso).
A regra do último administrador da empresa passa a contar só usuários ativos: a porta
`contar_administradores_ativos` vira `listar_administradores_ativos`, que junta a tabela `usuario` e
bloqueia as linhas das duas tabelas para resistir a ações simultâneas. Duas rotas HTTP novas.

## Contexto técnico

**Linguagem/Versão**: Python 3.14 · **Dependências**: nenhuma nova · **Armazenamento**: restrição
`usuario.situacao_valida` aceita `desativado` (migração `0006`) · **Testes**: pytest, unidade,
integração (inclusive concorrência com duas conexões) e HTTP

## Verificação da constituição (v2)

| Princípio / padrão | Como esta funcionalidade atende | Situação |
|---|---|---|
| IV. Histórico e imutabilidade | Nada é excluído: usuário, senha, vínculos e histórico ficam; desativar e reativar registram no histórico | OK |
| V. Isolamento por empresa | Ação exclusiva do administrador do sistema; administrador de empresa recebe recusa | OK |
| VI. Papéis fixos | Nenhuma empresa nem o sistema ficam sem administrador ativo; papéis preservados na reativação | OK |
| IX. LGPD | Desativação não expõe dados; login de desativado não revela que a conta existe | OK |
| X. Simplicidade | Sem bloqueio para administradores do sistema enquanto só existe o root | OK |
| DDD / TDD / Código limpo | Transição no domínio, regras entre objetos na aplicação, HTTP só traduz; testes antes; migração reversível | OK |

**Reavaliação pós-design**: sem violações.

## Estrutura do projeto

```text
src/assura/
├── historico/dominio/registro_de_historico.py      # + USUARIO_DESATIVADO, USUARIO_REATIVADO
└── identidade/
    ├── dominio/{usuario.py, erros.py}              # desativar, reativar; erros novos
    ├── aplicacao/
    │   ├── portas.py                               # listar_administradores_ativos, contar_administradores_do_sistema_ativos
    │   ├── mudar_situacao_do_vinculo.py            # exigir_que_a_empresa_mantenha_administrador
    │   ├── administrador_da_empresa.py             # usa a regra nova
    │   └── mudar_situacao_do_usuario.py            # DesativarUsuario, ReativarUsuario (novo)
    └── infraestrutura/
        ├── tabela.py, vinculos_sqlalchemy.py, usuarios_sqlalchemy.py
        ├── http.py                                 # categorias dos erros novos
        └── rotas_de_usuarios.py                    # desativacao, reativacao

migrations/versions/0006_permitir_usuario_desativado.py
tests/identidade/{unidade, integracao, http}/
```

**Ajustes durante a implementação**:

- `dependencias_http.py` não mudou: os repositórios da requisição já têm o que os dois casos de uso
  usam.
- Os testes da Fase 2 ficaram todos em `test_administrador_da_empresa.py`, que já tinha os
  auxiliares de vínculo administrador.
- O teste de concorrência foi conferido ao contrário: com o bloqueio só em `vinculo`
  (`FOR UPDATE OF vinculo`), o cenário "desativar A e retirar o papel de B" deixa a empresa sem
  administrador e o teste falha, como previsto na pesquisa (seção 4).

## Rastreamento de complexidade

Nenhuma violação a justificar.
