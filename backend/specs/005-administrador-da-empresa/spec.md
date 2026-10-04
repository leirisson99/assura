# Especificação da funcionalidade: Administrador da empresa

**Branch da funcionalidade**: `005-administrador-da-empresa`

**Criada em**: 2026-10-04

**Situação**: Rascunho

**Entrada**: funcionalidade 3 do backlog, etapa 1.5 de `docs/ordem-de-desenvolvimento.md` (P0).
Papel de administrador da empresa no vínculo, no mínimo um por empresa depois do primeiro, e as
permissões e rotas HTTP de tudo o que a etapa 1 já entregou (empresas, usuários, vínculos, senhas e
histórico).

## Cenários de uso e testes *(obrigatório)*

### História 1 - Tornar e deixar de ser administrador da empresa (Prioridade: P1)

O administrador do sistema, ou um administrador da própria empresa, torna um usuário vinculado
administrador da empresa ou retira esse papel. Depois que a empresa tem um administrador, o sistema
impede que ela fique sem nenhum.

**Por que esta prioridade**: o administrador da empresa é quem cuida dos usuários dela; sem ele, tudo
depende do administrador do sistema.

**Teste independente**: tornar um usuário administrador, tentar retirar o papel do único
administrador (recusado), tornar um segundo e retirar o primeiro (aceito).

**Cenários de aceitação**:

1. **Dado** um vínculo ativo, **quando** o administrador do sistema o torna administrador da empresa,
   **então** o vínculo passa a administrador e o histórico da empresa registra "administrador
   definido".
2. **Dado** uma empresa com dois administradores, **quando** um deles deixa de ser administrador,
   **então** a mudança é aceita e o histórico registra "administrador removido".
3. **Dado** o único administrador ativo da empresa, **quando** se tenta retirar o papel ou desativar o
   vínculo dele, **então** é recusado com erro "último administrador não pode ser removido".
4. **Dado** um vínculo desativado, **quando** se tenta torná-lo administrador, **então** é recusado.
5. **Dado** um usuário que não é administrador do sistema nem da empresa, **quando** tenta tornar
   alguém administrador, **então** é recusado por falta de permissão.

---

### História 2 - Administrador da empresa cuida dos usuários da empresa (Prioridade: P1)

O administrador da empresa inclui pessoas na empresa (cadastrando o usuário se o e-mail ainda não
existe, ou vinculando o usuário existente), lista os usuários da empresa e desativa ou reativa
vínculos, sem enxergar outras empresas.

**Por que esta prioridade**: é o trabalho do dia a dia do administrador da empresa.

**Teste independente**: com o administrador da empresa A, incluir um usuário novo e um existente,
listar, desativar um vínculo; tentar o mesmo na empresa B e ser recusado.

**Cenários de aceitação**:

1. **Dado** o administrador da empresa A e um e-mail não cadastrado, **quando** inclui a pessoa,
   **então** o usuário é cadastrado e vinculado a A, com os dois registros no histórico.
2. **Dado** um e-mail já cadastrado (pessoa que trabalha em outra empresa), **quando** o administrador
   da empresa A a inclui, **então** o usuário existente é vinculado a A, sem alterar o nome dele.
3. **Dado** o administrador da empresa A, **quando** tenta listar, incluir ou desativar vínculos da
   empresa B, **então** é recusado por falta de permissão.
4. **Dado** um administrador cujo vínculo foi desativado ou cuja empresa foi desativada, **quando**
   tenta agir como administrador, **então** é recusado.

---

### História 3 - Redefinir senha pelo administrador da empresa (Prioridade: P1)

O administrador da empresa redefine a senha de quem tem vínculo ativo apenas com a empresa dele.

**Por que esta prioridade**: decisão do usuário na etapa 1.4; tira do administrador do sistema o
atendimento de senhas esquecidas.

**Teste independente**: redefinir a senha de um usuário só da empresa A (aceito) e de um usuário de A
e B (recusado).

**Cenários de aceitação**:

1. **Dado** um usuário cujo único vínculo ativo é com a empresa A, **quando** o administrador de A
   redefine a senha dele, **então** a senha vira provisória.
2. **Dado** um usuário com vínculo ativo em A e em B, **quando** o administrador de A tenta redefinir
   a senha, **então** é recusado; só o administrador do sistema pode.
3. **Dado** um administrador do sistema como alvo, **quando** um administrador de empresa tenta
   redefinir a senha dele, **então** é recusado.

---

### História 4 - Rotas HTTP com permissões (Prioridade: P2)

Tudo o que a etapa 1 entregou fica disponível por HTTP, com a permissão de cada ação verificada.

**Por que esta prioridade**: torna o backend utilizável pelo frontend; as regras já existem nos
casos de uso.

**Teste independente**: percorrer o fluxo completo por HTTP: o root cadastra a empresa, inclui uma
pessoa, define senha, torna a pessoa administradora; a pessoa entra, troca a senha, inclui outra
pessoa e consulta o histórico da empresa.

**Cenários de aceitação**:

1. **Dado** o administrador do sistema, **quando** cadastra, altera, desativa, reativa e lista
   empresas, **então** as ações acontecem; qualquer outro usuário recebe recusa por permissão.
2. **Dado** o administrador da empresa, **quando** consulta a própria empresa e o histórico dela,
   **então** recebe os dados; para outra empresa, recebe recusa por permissão.
3. **Dado** um usuário comum, **quando** consulta o próprio usuário, **então** recebe os dados; outro
   usuário só é visível ao administrador do sistema e aos administradores de empresas em comum.
4. **Dado** um erro de regra (CNPJ repetido, último administrador, dados inválidos), **quando**
   ocorre, **então** a resposta indica o motivo com o código adequado (conflito, não encontrado,
   dados inválidos).

---

### Casos de borda

- Administrador da empresa desativa o próprio vínculo sendo o último: recusado.
- Dois administradores retiram o papel um do outro ao mesmo tempo: apenas um consegue; a empresa
  nunca fica sem administrador.
- Empresa ainda sem administrador: só o administrador do sistema age sobre ela.
- Tornar administrador quem já é (ou retirar de quem não é): recusado com erro claro e sem registro.
- Alterar nome e e-mail de usuário: só o administrador do sistema, porque o usuário é compartilhado
  entre empresas.

## Requisitos *(obrigatório)*

### Requisitos funcionais

- **RF-001**: O vínculo DEVE indicar se o usuário é administrador da empresa.
- **RF-002**: Tornar e deixar de ser administrador DEVEM ser permitidos ao administrador do sistema e
  aos administradores da própria empresa, e registrados no histórico da empresa.
- **RF-003**: Uma empresa que tem administrador ativo NÃO DEVE ficar sem nenhum, nem por retirada do
  papel nem por desativação do vínculo, mesmo com ações simultâneas.
- **RF-004**: É administrador da empresa para fins de permissão apenas quem tem vínculo ativo,
  marcado como administrador, com empresa ativa.
- **RF-005**: O administrador da empresa DEVE poder incluir pessoas (cadastrar ou vincular existente
  pelo e-mail), listar usuários e desativar e reativar vínculos da própria empresa.
- **RF-006**: O administrador da empresa DEVE poder redefinir a senha apenas de usuários cujos
  vínculos ativos são todos com a empresa dele e que não são administradores do sistema.
- **RF-007**: Cadastro, alteração, desativação, reativação e listagem de empresas, e alteração de
  usuários, DEVEM ser exclusivos do administrador do sistema.
- **RF-008**: O histórico DEVE ser consultável pelo administrador do sistema (todo) e pelo
  administrador da empresa (só o da empresa).
- **RF-009**: Toda ação DEVE estar disponível por HTTP, exigindo sessão com senha definitiva.
- **RF-010**: Falta de permissão, conflito com o estado atual, objeto inexistente e dados inválidos
  DEVEM ter respostas distintas.

### Entidades principais

- **Vínculo** (alterado): ganha a indicação de administrador da empresa.

## Critérios de sucesso *(obrigatório)*

### Resultados mensuráveis

- **CS-001**: 0 empresas que já tiveram administrador ficam sem administrador ativo, verificado
  inclusive com remoções simultâneas.
- **CS-002**: 0 dados de outra empresa acessíveis por administrador de empresa, verificado por testes
  de cada rota com duas empresas.
- **CS-003**: O fluxo completo da etapa 1 (cadastrar empresa até o administrador da empresa incluir
  pessoas) é executável só por HTTP.

## Premissas

- O primeiro administrador é definido pelo administrador do sistema depois do cadastro da empresa.
- Membros comuns ainda não têm ações na empresa (chegam com projetos e auditorias).
- O próprio usuário ainda não altera nome e e-mail; só o administrador do sistema.
- Tamanho de página e filtros das listagens seguem os já definidos (padrão 50, máximo 200).
