# Pesquisa: Autenticação

## 1. Resumo de senha

- **Decisão**: argon2id com os parâmetros padrão da `argon2-cffi` (recomendação da OWASP). O
  `PasswordHasher.check_needs_rehash` permite atualizar o resumo no login se os parâmetros mudarem.
- **Alternativas**: bcrypt (limite de 72 bytes), PBKDF2 (mais fraco contra GPU).

## 2. Política de senha

- **Decisão**: 8 a 128 caracteres, sem regras de composição e sem cortar espaços (NIST SP 800-63B).

## 3. Sessão

- **Decisão**: JWT HS256 com `sub` (id do usuário), `iat` e `exp` (8 horas). Chave secreta em
  `ASSURA_CHAVE_DA_SESSAO`, sem valor padrão: a aplicação não sobe sem ela.
- **Revogação**: o token não carrega permissões; a cada requisição o usuário é lido do banco (ativo,
  administrador do sistema, senha provisória). Desativar o usuário (1.6) corta o acesso na hora.
- **Alternativas**: sessão gravada no servidor (escolha do usuário foi JWT); token de renovação
  (adiado, Princípio X).

## 4. Respostas iguais no login

- **Decisão**: e-mail inexistente e usuário sem senha conferem a senha contra um resumo fixo
  descartável, para que o tempo de resposta não revele se o e-mail existe. Todos os casos levantam
  `CredenciaisInvalidas`.

## 5. Senha provisória

- **Decisão**: a dependência HTTP padrão (`exigir_usuario_com_senha_definitiva`) recusa com 403
  quem tem senha provisória. "Quem sou eu" e "trocar senha" usam a dependência que aceita senha
  provisória.

## 6. Transação nas requisições HTTP

- **Decisão**: dependência `obter_sessao_do_banco` abre uma sessão por requisição, faz commit se o
  endpoint termina sem erro e rollback se não. Os casos de uso continuam sem commit. Nos testes, a
  dependência é substituída pela sessão de teste.

## 7. Root

- **Decisão**: `python -m assura.criar_root --nome ... --email ...` pede a senha duas vezes com
  `getpass`. O caso de uso `CriarRoot` recusa se já houver administrador do sistema
  (`AdministradorDoSistemaJaExiste`). Autor do histórico: `sistema`. Detalhes do registro:
  `{"administrador_do_sistema": true}`.

## 8. Erros de domínio para HTTP

| Erro | Status |
|---|---|
| `CredenciaisInvalidas`, sessão inválida | 401 |
| `SenhaProvisoriaPrecisaSerTrocada`, `PermissaoNegada` | 403 |
| `SenhaInvalida`, `SenhaAtualIncorreta` | 422 |
| `UsuarioNaoEncontrado` | 404 |
