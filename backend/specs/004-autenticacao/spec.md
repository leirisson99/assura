# Especificação da funcionalidade: Autenticação

**Branch da funcionalidade**: `004-autenticacao`

**Criada em**: 2026-10-04

**Situação**: Rascunho

**Entrada**: etapa 1.4 de `docs/ordem-de-desenvolvimento.md` (P0, pré-requisito que faltava no
backlog). Login com e-mail e senha própria, sessão por token, troca e redefinição de senha e criação
do primeiro administrador do sistema (root).

## Cenários de uso e testes *(obrigatório)*

### História 1 - Criar o root (Prioridade: P1)

Na instalação, quem opera o servidor cria o primeiro administrador do sistema (root) por um comando
de terminal, informando nome, e-mail e senha. A senha é digitada sem aparecer na tela.

**Por que esta prioridade**: sem o root ninguém consegue entrar, e nada pode ser cadastrado pelo
sistema.

**Teste independente**: rodar o comando num banco vazio e entrar com o e-mail e a senha informados;
rodar de novo e ver a recusa.

**Cenários de aceitação**:

1. **Dado** um sistema sem administrador do sistema, **quando** o comando é executado com dados
   válidos, **então** o root é criado como administrador do sistema, com a senha definitiva, e o
   histórico registra o cadastro com autor "sistema".
2. **Dado** que já existe um administrador do sistema, **quando** o comando é executado, **então** é
   recusado e nada muda.
3. **Dado** uma senha fraca ou a confirmação diferente da senha, **quando** o comando é executado,
   **então** é recusado.

---

### História 2 - Entrar no sistema (Prioridade: P1)

O usuário entra com e-mail e senha e recebe uma sessão válida por um período limitado.

**Por que esta prioridade**: todas as funções do sistema passam a depender de saber quem está
usando.

**Teste independente**: entrar com credenciais corretas, usar a sessão para consultar "quem sou eu";
tentar com senha errada e com sessão vencida.

**Cenários de aceitação**:

1. **Dado** e-mail e senha corretos de um usuário ativo, **quando** ele entra, **então** recebe uma
   sessão e a informação de se a senha é provisória.
2. **Dado** senha errada, e-mail inexistente ou usuário sem senha definida, **quando** tenta entrar,
   **então** recebe a mesma recusa genérica, sem revelar qual dado estava errado.
3. **Dado** o e-mail com outras maiúsculas e minúsculas, **quando** entra, **então** é aceito.
4. **Dado** uma sessão válida, **quando** consulta "quem sou eu", **então** recebe nome, e-mail, se é
   administrador do sistema e se a senha é provisória.
5. **Dado** uma sessão vencida, adulterada ou ausente, **quando** usa o sistema, **então** é recusado
   como não autenticado.

---

### História 3 - Trocar a própria senha (Prioridade: P1)

O usuário troca a própria senha informando a atual e a nova. Com senha provisória, essa é a única
ação permitida.

**Por que esta prioridade**: fecha o ciclo da senha provisória definida pelo administrador.

**Teste independente**: entrar com senha provisória, verificar que outras ações são recusadas,
trocar a senha e verificar que tudo é liberado.

**Cenários de aceitação**:

1. **Dado** a senha atual correta e uma nova senha válida, **quando** o usuário troca, **então** a
   nova senha passa a valer, a anterior deixa de valer, a senha deixa de ser provisória e o histórico
   registra "senha trocada" sem detalhes.
2. **Dado** a senha atual errada, **quando** tenta trocar, **então** é recusado.
3. **Dado** uma nova senha fraca, **quando** tenta trocar, **então** é recusado.
4. **Dado** um usuário com senha provisória, **quando** tenta qualquer ação além de "quem sou eu" e
   "trocar senha", **então** é recusado até trocar a senha.

---

### História 4 - Redefinir a senha de um usuário (Prioridade: P2)

O administrador define uma senha provisória para um usuário: no primeiro acesso (usuário recém
cadastrado ainda não tem senha) ou quando o usuário esqueceu a senha.

**Por que esta prioridade**: é como os usuários cadastrados ganham acesso; depende do login.

**Teste independente**: o administrador do sistema redefine a senha de um usuário, que entra com a
provisória e é obrigado a trocá-la.

**Cenários de aceitação**:

1. **Dado** o administrador do sistema, **quando** redefine a senha de um usuário, **então** a senha
   anterior deixa de valer, a nova vale como provisória e o histórico registra "senha redefinida" sem
   detalhes.
2. **Dado** um usuário que não é administrador do sistema, **quando** tenta redefinir uma senha,
   **então** é recusado por falta de permissão.
3. **Dado** uma senha provisória fraca, **quando** a redefinição é tentada, **então** é recusada.

---

### Casos de borda

- Senha com espaços: aceita como digitada, sem cortar pontas.
- Muitas tentativas de login erradas: fora desta etapa (ver premissas).
- Sessão emitida antes de o usuário ou o vínculo ser desativado: a verificação a cada uso garante
  que o usuário continua ativo.
- Redefinir a senha de quem tem sessão aberta: a sessão continua válida até vencer, mas a senha
  passa a ser provisória e só permite trocar a senha.

## Requisitos *(obrigatório)*

### Requisitos funcionais

- **RF-001**: A senha DEVE ter de 8 a 128 caracteres, sem exigências de composição.
- **RF-002**: A senha NÃO DEVE ser guardada; apenas um resumo com algoritmo resistente a força bruta.
- **RF-003**: O sistema DEVE autenticar por e-mail (sem diferenciar maiúsculas) e senha, e responder
  da mesma forma a e-mail inexistente, senha errada e usuário sem senha.
- **RF-004**: A sessão DEVE expirar em 8 horas e ser recusada se vencida, adulterada ou ausente.
- **RF-005**: A cada uso da sessão, o sistema DEVE confirmar que o usuário existe e está ativo.
- **RF-006**: Com senha provisória, o usuário DEVE ter acesso apenas a "quem sou eu" e "trocar a
  própria senha".
- **RF-007**: O usuário DEVE poder trocar a própria senha informando a atual.
- **RF-008**: O administrador do sistema DEVE poder redefinir a senha de qualquer usuário, que passa a
  ser provisória.
- **RF-009**: Na etapa 1.5, o administrador da empresa PODERÁ redefinir a senha apenas de usuários
  cujo único vínculo ativo é com a empresa dele; nesta etapa só o administrador do sistema redefine.
- **RF-010**: O root DEVE ser criado por comando de terminal, apenas quando não existe administrador
  do sistema, com senha definitiva confirmada por digitação dupla.
- **RF-011**: Troca, redefinição e criação do root DEVEM ser registradas no histórico sem empresa e
  sem a senha nem o resumo dela.

### Entidades principais

- **Usuário** (existente): ganha senha (resumo), indicação de senha provisória e indicação de
  administrador do sistema.
- **Sessão**: comprovante emitido no login, ligado a um usuário, com validade.

## Critérios de sucesso *(obrigatório)*

### Resultados mensuráveis

- **CS-001**: 0 senhas legíveis armazenadas; verificado na tabela de usuários e no histórico.
- **CS-002**: As respostas a e-mail inexistente, senha errada e usuário sem senha são idênticas.
- **CS-003**: 100% das ações fora de "quem sou eu" e "trocar senha" são recusadas para senha
  provisória.
- **CS-004**: Um novo ambiente fica pronto para uso (root criado e login feito) em menos de 2 minutos.

## Premissas

- Bloqueio por tentativas repetidas e registro de logins no histórico ficam para depois, quando houver
  exposição pública.
- Sem renovação automática da sessão: ao vencer, o usuário entra de novo.
- A chave de assinatura das sessões vem da configuração do servidor e não tem valor padrão em
  produção.
- O papel de administrador do sistema fica no usuário (não pertence a nenhuma empresa). Nomear outros
  administradores do sistema fica para depois.
- Recuperação de senha por e-mail não entra; o caminho é a redefinição pelo administrador.
