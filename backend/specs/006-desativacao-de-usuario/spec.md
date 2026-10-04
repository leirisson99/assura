# Especificação da funcionalidade: Desativação de usuário

**Branch da funcionalidade**: `006-desativacao-de-usuario`

**Criada em**: 2026-10-04

**Situação**: Rascunho

**Entrada**: funcionalidade 9 do backlog, etapa 1.6 de `docs/ordem-de-desenvolvimento.md` (P0).
Desativar e reativar o usuário, sem exclusão, cortando o acesso dele a todas as empresas de uma vez.
Fecha a etapa 1.

## Cenários de uso e testes *(obrigatório)*

### História 1 - Desativar um usuário (Prioridade: P1)

O administrador do sistema desativa uma pessoa que deixou de usar o Assura (saiu da consultoria,
encerrou o contrato). O acesso dela acaba na hora, em todas as empresas, e nada do que ela fez ou
registrou se perde.

**Por que esta prioridade**: o Princípio IV proíbe exclusão; sem desativação, a única forma de tirar
o acesso de alguém seria desativar vínculo por vínculo, e o usuário continuaria entrando no sistema.

**Teste independente**: com um usuário vinculado a duas empresas e com uma sessão aberta, desativá-lo
e verificar que a sessão deixa de valer, que o login é recusado e que usuário, vínculos e histórico
continuam existindo.

**Cenários de aceitação**:

1. **Dado** um usuário ativo, **quando** o administrador do sistema o desativa, **então** ele passa a
   desativado, continua existindo com todos os dados e vínculos, e o histórico registra "usuário
   desativado".
2. **Dado** um usuário desativado com uma sessão aberta antes da desativação, **quando** ele faz
   qualquer requisição, **então** é recusada como sessão inválida.
3. **Dado** um usuário desativado, **quando** tenta entrar com e-mail e senha corretos, **então** é
   recusado com a mesma mensagem de credenciais inválidas, sem revelar que a conta existe.
4. **Dado** um usuário já desativado, **quando** se tenta desativá-lo de novo, **então** é recusado
   com erro claro e nada é registrado.
5. **Dado** um administrador de empresa ou um usuário comum, **quando** tenta desativar um usuário,
   **então** é recusado por falta de permissão.

---

### História 2 - Nenhuma empresa nem o sistema ficam sem administrador (Prioridade: P1)

Desativar um usuário não pode deixar uma empresa sem administrador que consiga entrar, nem deixar o
sistema sem administrador do sistema.

**Por que esta prioridade**: o Princípio VI exige ao menos um administrador por empresa; um
administrador desativado não administra nada.

**Teste independente**: tentar desativar o único administrador de uma empresa (recusado); com dois
administradores, desativar um e depois tentar retirar o papel do outro (recusado).

**Cenários de aceitação**:

1. **Dado** um usuário que é o único administrador ativo de alguma empresa, **quando** se tenta
   desativá-lo, **então** é recusado com erro "último administrador não pode ser removido", indicando
   a empresa.
2. **Dado** uma empresa com os administradores A e B, **quando** o usuário A é desativado, **então** a
   empresa passa a ter um administrador ativo (B), e retirar o papel ou desativar o vínculo de B é
   recusado.
3. **Dado** o único administrador do sistema ativo, **quando** se tenta desativá-lo, **então** é
   recusado.

---

### História 3 - Reativar um usuário (Prioridade: P2)

O administrador do sistema reativa uma pessoa que voltou a trabalhar com o Assura. Ela volta com os
mesmos vínculos e papéis que tinha.

**Por que esta prioridade**: desativação reversível evita cadastrar de novo a mesma pessoa, o que
partiria o histórico dela em dois usuários.

**Teste independente**: desativar e reativar um usuário e verificar que ele volta a entrar com a
mesma senha e com os mesmos vínculos.

**Cenários de aceitação**:

1. **Dado** um usuário desativado, **quando** o administrador do sistema o reativa, **então** ele
   volta a ativo, entra com a senha que tinha e o histórico registra "usuário reativado".
2. **Dado** um usuário que era administrador de uma empresa quando foi desativado, **quando** é
   reativado, **então** volta a contar como administrador dela.
3. **Dado** um usuário já ativo, **quando** se tenta reativá-lo, **então** é recusado com erro claro e
   nada é registrado.

---

### História 4 - Situação do usuário visível e disponível por HTTP (Prioridade: P2)

A desativação e a reativação ficam disponíveis por HTTP, e as consultas mostram se o usuário está
ativo ou desativado.

**Por que esta prioridade**: torna a funcionalidade utilizável pelo frontend; as regras estão nos
casos de uso.

**Teste independente**: desativar por HTTP, consultar o usuário e a lista de usuários da empresa e
ver a situação.

**Cenários de aceitação**:

1. **Dado** o administrador do sistema, **quando** desativa e reativa um usuário por HTTP, **então**
   as ações acontecem; qualquer outro usuário recebe recusa por permissão.
2. **Dado** um usuário desativado com vínculo ativo na empresa A, **quando** o administrador de A
   lista os usuários da empresa, **então** vê o usuário com a situação "desativado".

---

### Casos de borda

- Administrador do sistema tenta desativar a si mesmo: recusado, porque hoje ele é o único.
- Usuário que é o último administrador de uma empresa desativada: também recusado; a empresa pode
  ser reativada e precisa continuar administrável.
- Usuário sem nenhum vínculo: pode ser desativado normalmente.
- Usuário desativado incluído numa empresa por e-mail: o vínculo é criado, mas o usuário continua
  desativado e sem acesso até ser reativado.
- Redefinição de senha de usuário desativado: aceita, mas não devolve o acesso; só a reativação
  devolve.
- Desativar o usuário e, ao mesmo tempo, retirar o papel do outro administrador da mesma empresa:
  apenas uma das duas ações é aceita.

## Requisitos *(obrigatório)*

### Requisitos funcionais

- **RF-001**: O usuário DEVE ter situação ativo ou desativado. Todo usuário nasce ativo.
- **RF-002**: Desativar e reativar um usuário DEVEM ser exclusivos do administrador do sistema e
  registrados no histórico.
- **RF-003**: Desativar um usuário NÃO DEVE excluir nem alterar os dados, a senha, os vínculos ou o
  histórico dele.
- **RF-004**: Um usuário desativado NÃO DEVE entrar no sistema, e as sessões abertas antes da
  desativação DEVEM deixar de valer na requisição seguinte.
- **RF-005**: O login de usuário desativado DEVE ser recusado com a mesma resposta e no mesmo tempo
  de uma senha errada.
- **RF-006**: Só conta como administrador ativo de uma empresa quem tem usuário ativo, vínculo ativo
  e o papel de administrador. Essa contagem vale para todas as regras de último administrador.
- **RF-007**: O sistema DEVE recusar desativar um usuário que é o último administrador ativo de
  alguma empresa, mesmo com ações simultâneas, ou o último administrador do sistema ativo.
- **RF-008**: Desativar ou reativar o que já está na situação pedida DEVE ser recusado, sem registro
  no histórico.
- **RF-009**: A reativação DEVE devolver o acesso com a mesma senha, os mesmos vínculos e os mesmos
  papéis de antes.
- **RF-010**: A situação do usuário DEVE aparecer na consulta do usuário e na lista de usuários da
  empresa.
- **RF-011**: Desativar e reativar DEVEM estar disponíveis por HTTP, com as mesmas respostas
  distintas para falta de permissão, conflito com o estado, objeto inexistente e dados inválidos.

### Entidades principais

- **Usuário** (alterado): a situação passa a aceitar "desativado".

## Critérios de sucesso *(obrigatório)*

### Resultados mensuráveis

- **CS-001**: 0 requisições aceitas de um usuário desativado, inclusive com sessão aberta antes da
  desativação.
- **CS-002**: 0 empresas que já tiveram administrador e 0 sistemas ficam sem administrador ativo
  capaz de entrar, verificado inclusive com ações simultâneas.
- **CS-003**: 0 registros perdidos: depois de desativar e reativar, o usuário tem os mesmos dados,
  vínculos e histórico de antes.
- **CS-004**: Desativar uma pessoa que trabalha em várias empresas é uma única ação, em vez de uma
  por vínculo.

## Premissas

- O usuário é uma identidade compartilhada entre empresas (Princípio VI). Por isso só o
  administrador do sistema o desativa; o administrador da empresa retira o acesso à empresa dele
  desativando o vínculo (etapa 1.3).
- As ações sobre o usuário ficam no histórico sem empresa, como o cadastro e a alteração de usuário
  (etapa 1.3).
- Papéis em projetos e auditorias ainda não existem. Quando chegarem (etapas 2 e 4), a regra de
  último responsável e de último auditor líder também deve contar apenas usuários ativos.
- Hoje existe um único administrador do sistema, o root (etapa 1.4), e não há como criar outro.
  Pelo RF-007, o root não pode ser desativado enquanto for o único.
- Não há motivo de desativação nem data programada; a desativação vale a partir do momento em que é
  feita.
