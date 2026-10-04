# Plano de implementação: Autenticação

**Branch**: `004-autenticacao` | **Data**: 2026-10-04 | **Spec**: [spec.md](spec.md)

## Resumo

O `Usuario` ganha resumo de senha (argon2id), indicação de senha provisória e de administrador do
sistema. Casos de uso novos em `identidade`: `Autenticar`, `TrocarPropriaSenha`, `RedefinirSenha` e
`CriarRoot`. O resumo de senha e o token ficam atrás de portas (`GeradorDeResumoDeSenha`,
`EmissorDeSessao`) com implementações argon2 e JWT (HS256). Entram os primeiros endpoints HTTP
(login, quem sou eu, trocar senha, redefinir senha) e a dependência FastAPI que identifica o usuário
da sessão e controla a transação da requisição. O root é criado por `python -m assura.criar_root`.

## Contexto técnico

**Linguagem/Versão**: Python 3.14 · **Dependências novas**: `argon2-cffi` (resumo de senha),
`pyjwt` (sessão) · **Armazenamento**: PostgreSQL 17, colunas novas em `usuario` (migração `0004`) ·
**Testes**: pytest; HTTP com `TestClient` e a sessão de teste injetada · **Tipo**: serviço web

## Verificação da constituição

| Princípio / padrão | Como esta funcionalidade atende | Situação |
|---|---|---|
| II. O auditor decide | Base para saber quem decide cada ação | OK |
| III. Rastreabilidade | Troca, redefinição e root no histórico, sem a senha | OK |
| IV. Isolamento | Regra de redefinição pelo administrador da empresa limitada a vínculo único (1.5) | OK |
| V. Papéis fixos | Administrador do sistema como indicação no usuário; nada configurável | OK |
| IX. LGPD | Senha nunca guardada nem registrada; resumo fora do histórico | OK |
| X. Simplicidade | Duas dependências pequenas e consolidadas; sem renovação de token | OK |
| DDD | Domínio não importa argon2 nem JWT; HTTP em `infraestrutura` | OK |
| TDD / Qualidade | Testes antes; migração reversível | OK |

**Dependências justificadas**: escrever algoritmos de resumo de senha ou de assinatura de token à mão
é um risco de segurança; as bibliotecas escolhidas são as de referência em Python.

## Estrutura do projeto

```text
src/assura/
├── configuracao.py                          # + chave_da_sessao, validade_da_sessao_em_horas
├── main.py                                  # + rotas de autenticação
├── criar_root.py                            # comando de terminal
├── compartilhado/infraestrutura/http.py     # sessão do banco por requisição (commit/rollback)
└── identidade/
    ├── dominio/{senha.py, usuario.py, erros.py}
    ├── aplicacao/{portas.py, autenticar.py, trocar_propria_senha.py,
    │              redefinir_senha.py, criar_root.py}
    └── infraestrutura/{resumo_de_senha_argon2.py, sessao_jwt.py, http.py}

migrations/versions/0004_acrescentar_senha_ao_usuario.py
tests/identidade/{unidade, integracao, http}/
```

## Rastreamento de complexidade

Nenhuma violação a justificar.
