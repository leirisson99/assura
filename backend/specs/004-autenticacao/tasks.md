# Tarefas: Autenticação

**Entrada**: documentos em `specs/004-autenticacao/` · **Testes**: obrigatórios (TDD), escritos antes
e vistos falhar · **Formato**: `[ID] [P?] [História] Descrição` · caminhos relativos a `backend/`.

## Fase 1: Preparação

- [X] T001 Acrescentar `argon2-cffi` e `pyjwt` às dependências em `pyproject.toml`; `chave_da_sessao` (sem padrão) e `validade_da_sessao_em_horas` (8) em `src/assura/configuracao.py`; `ASSURA_CHAVE_DA_SESSAO` em `.env.example`; chave de teste no ambiente dos testes em `tests/conftest.py`
- [X] T002 Acrescentar `SENHA_TROCADA` e `SENHA_REDEFINIDA` em `TipoDeAcao`

## Fase 2: Fundação

- [X] T003 [P] Testes de domínio em `tests/identidade/unidade/test_senha.py` ("8 a 128 caracteres", espaços preservados) e novos casos em `tests/identidade/unidade/test_usuario.py` (sem senha ao cadastrar; definir senha provisória e definitiva)
- [X] T004 Implementar `validar_senha` em `src/assura/identidade/dominio/senha.py`, os erros novos e os atributos `resumo_da_senha`, `senha_provisoria`, `administrador_do_sistema` em `Usuario`
- [X] T005 [P] Testes das implementações em `tests/identidade/unidade/test_resumo_de_senha_argon2.py` e `test_sessao_jwt.py` (emitir e ler; vencida, adulterada e com outra chave recusadas)
- [X] T006 Criar as portas `GeradorDeResumoDeSenha` e `EmissorDeSessao` e `UsuarioAutenticado` em `src/assura/identidade/aplicacao/portas.py`; implementar `resumo_de_senha_argon2.py` e `sessao_jwt.py` em `src/assura/identidade/infraestrutura/`
- [X] T007 Colunas novas em `tabela_usuario` com `CHECK (NOT senha_provisoria OR resumo_da_senha IS NOT NULL)`, migração `migrations/versions/0004_acrescentar_senha_ao_usuario.py`, `Usuarios.obter_por_email` e `Usuarios.existe_administrador_do_sistema`

## Fase 3: História 1 - Criar o root (P1)

- [X] T008 [P] [US1] Testes em `tests/identidade/integracao/test_criar_root.py`: root criado administrador com senha definitiva e registro com autor sistema; segundo root recusado; senha inválida recusada
- [X] T009 [US1] Implementar `CriarRoot` em `src/assura/identidade/aplicacao/criar_root.py` e o comando `src/assura/criar_root.py` (argumentos `--nome` e `--email`, senha por `getpass` com confirmação)

## Fase 4: História 2 - Entrar no sistema (P1)

- [X] T010 [P] [US2] Testes em `tests/identidade/integracao/test_autenticar.py`: credenciais corretas; e-mail com maiúsculas; senha errada, e-mail inexistente e usuário sem senha dão `CredenciaisInvalidas`
- [X] T011 [US2] Implementar `Autenticar` em `src/assura/identidade/aplicacao/autenticar.py` (resumo descartável para e-mail inexistente)
- [X] T012 [P] [US2] Testes HTTP em `tests/identidade/http/test_rotas_de_autenticacao.py`: login 200 e 401; `GET /autenticacao/eu` com token válido, sem token, vencido, adulterado e de usuário inexistente
- [X] T013 [US2] Implementar `src/assura/compartilhado/infraestrutura/http.py` (sessão do banco por requisição) e `src/assura/identidade/infraestrutura/http.py` (rotas e dependências de usuário autenticado); registrar as rotas em `src/assura/main.py`

## Fase 5: História 3 - Trocar a própria senha (P1)

- [X] T014 [P] [US3] Testes em `tests/identidade/integracao/test_trocar_propria_senha.py` e HTTP: troca com senha atual correta, senha antiga deixa de valer, deixa de ser provisória, registro `senha_trocada` sem detalhes; senha atual errada; nova senha inválida; senha provisória recusada (403) fora de "eu" e "trocar senha"
- [X] T015 [US3] Implementar `TrocarPropriaSenha` e a rota `POST /autenticacao/eu/senha`

## Fase 6: História 4 - Redefinir senha (P2)

- [X] T016 [P] [US4] Testes em `tests/identidade/integracao/test_redefinir_senha.py` e HTTP: administrador do sistema redefine, senha vira provisória, registro `senha_redefinida` sem detalhes; não administrador recebe `PermissaoNegada` (403); usuário inexistente (404); senha inválida (422)
- [X] T017 [US4] Implementar `RedefinirSenha` e a rota `POST /usuarios/{usuario_id}/senha`

## Fase 7: Acabamento

- [X] T018 [P] `ruff`, `mypy`; verificar que nenhuma senha nem resumo aparece no histórico
- [X] T019 Executar `quickstart.md` de ponta a ponta (root, login, quem sou eu) e atualizar o README

## Dependências

Fases 1 e 2 → História 1 e História 2 → Histórias 3 e 4. Paralelos: arquivos de teste de cada fase.
