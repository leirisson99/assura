# Plano de implementação: Usuários e vínculos com a empresa

**Branch**: `003-usuarios-e-vinculos` | **Data**: 2026-10-04 | **Spec**: [spec.md](spec.md)

## Resumo

Acrescentar ao contexto `identidade` as entidades `Usuario` e `Vinculo`, o objeto de valor `Email`
e os casos de uso cadastrar e alterar usuário, vincular, desativar e reativar vínculo, consultar
usuário e listar usuários da empresa. A migração `0003` cria as tabelas `usuario` e `vinculo` e liga
`registro_de_historico.autor_usuario_id` a `usuario.id`. Segue os mesmos padrões da 002: histórico
na sessão de quem chama, unicidade garantida também pelo banco, sem exclusão.

## Contexto técnico

**Linguagem/Versão**: Python 3.14 · **Dependências**: SQLAlchemy 2.x, Alembic, psycopg 3 (nenhuma
nova) · **Armazenamento**: PostgreSQL 17, tabelas `usuario` e `vinculo` · **Testes**: pytest, unidade
sem banco e integração em `assura_teste` · **Tipo**: serviço web (backend)

## Verificação da constituição

| Princípio / padrão | Como esta funcionalidade atende | Situação |
|---|---|---|
| III. Rastreabilidade | Todas as ações no histórico; vínculo e usuário só são desativados | OK |
| IV. Isolamento por empresa | `vinculo` carrega `empresa_id`; listagem de usuários é sempre por empresa | OK |
| V. Papéis fixos | Usuário é identidade; o vínculo receberá setor, cargo e papel | OK |
| IX. LGPD | Histórico do cadastro sem nome e e-mail; alteração só com o que mudou | OK |
| X. Simplicidade | Mesmo contexto e padrões da 002 | OK |
| DDD / TDD / Qualidade | Domínio sem infraestrutura; testes antes; migração reversível | OK |

**Exceção registrada**: a tabela `usuario` não tem `empresa_id`. O usuário é identidade global por
decisão do Princípio V; o isolamento por empresa fica no `vinculo`.

**Reavaliação pós-design**: sem violações.

## Estrutura do projeto

```text
src/assura/
├── historico/dominio/registro_de_historico.py     # + tipos USUARIO_* e VINCULO_*
├── historico/infraestrutura/tabela.py             # + chave estrangeira autor_usuario_id → usuario
└── identidade/
    ├── dominio/{email.py, usuario.py, vinculo.py, erros.py}
    ├── aplicacao/{portas.py, historico_do_usuario.py, cadastrar_usuario.py, alterar_usuario.py,
    │              vincular_usuario.py, mudar_situacao_do_vinculo.py, consultar_usuarios.py}
    └── infraestrutura/{tabela.py, usuarios_sqlalchemy.py, vinculos_sqlalchemy.py}

migrations/versions/0003_criar_usuario_e_vinculo.py

tests/
├── conftest.py                                    # sessão já com o usuário autor de teste
└── identidade/{unidade, integracao}/
```

## Rastreamento de complexidade

Nenhuma violação a justificar.
