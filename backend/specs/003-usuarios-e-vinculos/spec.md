# Especificação da funcionalidade: Usuários e vínculos com a empresa

**Branch da funcionalidade**: `003-usuarios-e-vinculos`

**Criada em**: 2026-10-04

**Situação**: Rascunho

**Entrada**: funcionalidade 2 do backlog, etapa 1.3 de `docs/ordem-de-desenvolvimento.md` (P0).
Usuário é identidade global; o vínculo liga o usuário a uma empresa (Princípio V).

## Cenários de uso e testes *(obrigatório)*

### História 1 - Cadastrar um usuário (Prioridade: P1)

Um usuário é cadastrado com nome e e-mail. O e-mail identifica a pessoa em todo o sistema e será
usado no login (etapa 1.4).

**Por que esta prioridade**: sem usuário não há quem execute auditorias, nem autor real no
histórico.

**Teste independente**: cadastrar um usuário e verificar que existe, está ativo e tem registro
"usuário cadastrado" no histórico; tentar repetir o e-mail com outra combinação de maiúsculas e
verificar a recusa.

**Cenários de aceitação**:

1. **Dado** nome e e-mail válidos e não cadastrados, **quando** o usuário é cadastrado, **então** ele
   fica gravado, ativo, com o e-mail em letras minúsculas, e o histórico registra "usuário cadastrado"
   sem empresa.
2. **Dado** um e-mail já cadastrado, mesmo escrito com outras maiúsculas e minúsculas, **quando** o
   cadastro é tentado, **então** é recusado com erro de e-mail já cadastrado.
3. **Dado** um e-mail sem `@`, sem domínio, com espaços internos ou com mais de 254 caracteres,
   **quando** o cadastro é tentado, **então** é recusado com erro de e-mail inválido.
4. **Dado** nome vazio ou com mais de 150 caracteres, **quando** o cadastro é tentado, **então** é
   recusado.

---

### História 2 - Vincular um usuário a uma empresa (Prioridade: P1)

Um usuário cadastrado é vinculado a uma empresa. A mesma pessoa pode ter vínculo com várias empresas.

**Por que esta prioridade**: o vínculo é o que dá acesso a uma empresa; sem ele, o usuário não
participa de nada.

**Teste independente**: vincular um usuário a duas empresas e verificar os dois vínculos ativos e os
registros "usuário vinculado" no histórico de cada empresa.

**Cenários de aceitação**:

1. **Dado** um usuário e uma empresa ativa, **quando** o usuário é vinculado, **então** o vínculo é
   criado ativo e o histórico da empresa registra "usuário vinculado".
2. **Dado** um usuário já vinculado à empresa (ativo ou desativado), **quando** se tenta vinculá-lo de
   novo, **então** é recusado com erro de vínculo já existente.
3. **Dado** uma empresa desativada, **quando** se tenta vincular um usuário, **então** é recusado.
4. **Dado** um usuário ou uma empresa inexistente, **quando** se tenta vincular, **então** é recusado
   com erro de não encontrado.

---

### História 3 - Desativar e reativar um vínculo (Prioridade: P2)

O acesso de um usuário a uma empresa é retirado desativando o vínculo, e pode ser devolvido
reativando-o. O usuário e os outros vínculos dele não mudam.

**Por que esta prioridade**: pessoas saem de empresas clientes; o Princípio III proíbe excluir.

**Teste independente**: com um usuário vinculado a duas empresas, desativar um vínculo e verificar que
o outro continua ativo e que o usuário continua ativo.

**Cenários de aceitação**:

1. **Dado** um vínculo ativo, **quando** é desativado, **então** passa a desativado e o histórico da
   empresa registra "vínculo desativado"; o usuário e os outros vínculos não mudam.
2. **Dado** um vínculo desativado, **quando** é reativado, **então** volta a ativo e o histórico
   registra "vínculo reativado".
3. **Dado** um vínculo já desativado (ou já ativo), **quando** se tenta desativar (ou reativar) de
   novo, **então** é recusado com erro claro e sem registro.

---

### História 4 - Alterar nome e e-mail do usuário (Prioridade: P2)

Nome e e-mail podem ser corrigidos. O histórico registra apenas o que mudou.

**Por que esta prioridade**: correções acontecem, mas o cadastro vem antes.

**Teste independente**: alterar o nome e verificar o registro "usuário alterado" só com o nome
anterior e o novo.

**Cenários de aceitação**:

1. **Dado** um usuário, **quando** o nome é alterado, **então** o novo nome fica gravado e o histórico
   registra "usuário alterado" com o nome anterior e o novo, sem citar o e-mail.
2. **Dado** um novo e-mail que pertence a outro usuário, **quando** a alteração é tentada, **então** é
   recusada e o usuário continua igual.
3. **Dado** uma alteração que repete os valores atuais (inclusive o e-mail com outras maiúsculas),
   **quando** é enviada, **então** nada muda e nenhum registro é criado.

---

### História 5 - Consultar usuários (Prioridade: P3)

Consulta de um usuário pelo identificador e listagem dos usuários vinculados a uma empresa.

**Por que esta prioridade**: necessária para administrar, depende das anteriores.

**Teste independente**: vincular usuários a duas empresas, desativar um vínculo e listar cada
empresa com e sem filtro.

**Cenários de aceitação**:

1. **Dado** um usuário, **quando** consultado pelo identificador, **então** retorna nome, e-mail e
   situação.
2. **Dado** usuários vinculados às empresas A e B, **quando** os usuários da empresa A são listados,
   **então** só aparecem os vinculados a A, com a situação do vínculo, em ordem alfabética de nome e
   em páginas.
3. **Dado** vínculos ativos e desativados, **quando** a listagem filtra por situação do vínculo,
   **então** só aparecem os da situação pedida.

---

### Casos de borda

- Espaços nas pontas do nome e do e-mail são descartados.
- E-mail com maiúsculas é guardado em minúsculas; a comparação de unicidade ignora maiúsculas.
- Dois cadastros simultâneos com o mesmo e-mail: apenas um é aceito.
- Dois vínculos simultâneos do mesmo usuário com a mesma empresa: apenas um é aceito.
- Vínculo de empresa que foi desativada depois: o vínculo continua existindo; a empresa desativada
  já impede o uso (etapas seguintes).
- Falha ao gravar o histórico: a ação também não é gravada.

## Requisitos *(obrigatório)*

### Requisitos funcionais

- **RF-001**: O sistema DEVE permitir cadastrar usuário com nome (1 a 150 caracteres) e e-mail.
- **RF-002**: O e-mail DEVE ser válido (uma parte local, `@`, domínio com ponto, sem espaços, até 254
  caracteres), guardado em minúsculas e único no sistema.
- **RF-003**: Todo usuário nasce ativo. Esta funcionalidade não desativa usuários (etapa 1.6).
- **RF-004**: O sistema DEVE permitir alterar nome e e-mail com as mesmas validações; alteração sem
  mudança efetiva NÃO DEVE gerar registro.
- **RF-005**: O sistema DEVE permitir vincular um usuário a uma empresa ativa, no máximo um vínculo
  por par usuário-empresa.
- **RF-006**: O sistema DEVE permitir desativar e reativar um vínculo, sem afetar o usuário nem os
  outros vínculos, e recusar desativar o desativado ou reativar o ativo.
- **RF-007**: O sistema NÃO DEVE oferecer forma de excluir usuário ou vínculo.
- **RF-008**: Cadastro e alteração de usuário DEVEM gerar registro no histórico sem empresa; vínculo,
  desativação e reativação de vínculo DEVEM gerar registro no histórico da empresa do vínculo; tudo
  na mesma gravação da mudança.
- **RF-009**: Os detalhes do histórico DEVEM conter apenas o necessário: o cadastro não repete nome e
  e-mail; a alteração guarda só os campos alterados com anterior e novo.
- **RF-010**: O sistema DEVE permitir consultar um usuário e listar os usuários de uma empresa com a
  situação do vínculo, filtro opcional por essa situação, ordem alfabética de nome e paginação.
- **RF-011**: O autor de um registro de histórico do tipo usuário DEVE ser um usuário cadastrado.

### Entidades principais

- **Usuário**: identidade de uma pessoa no Assura. Nome, e-mail (único), situação (ativo).
- **Vínculo**: ligação de um usuário com uma empresa. Situação (ativo ou desativado). Receberá setor,
  cargo (item 4) e papel de administrador (etapa 1.5).

## Critérios de sucesso *(obrigatório)*

### Resultados mensuráveis

- **CS-001**: 0 usuários com e-mail repetido, considerando maiúsculas e minúsculas e tentativas
  simultâneas.
- **CS-002**: 0 pares usuário-empresa com mais de um vínculo.
- **CS-003**: 100% das ações desta funcionalidade têm exatamente um registro no histórico, e 0
  registros existem para ações recusadas.
- **CS-004**: Desativar um vínculo nunca altera o usuário nem outros vínculos, verificado em testes com
  um usuário vinculado a pelo menos duas empresas.

## Premissas

- Quem pode cadastrar e vincular (administrador do sistema; administrador da empresa na 1.5) passa a
  ser verificado com a autenticação (1.4). Até lá, o autor é informado por quem chama.
- Sem endpoint HTTP nesta funcionalidade.
- Setor e cargo entram com o item 4 (P1); senha com a etapa 1.4; desativação de usuário com a 1.6.
- O cadastro de usuário não cria vínculo automaticamente: são duas ações, cada uma com seu registro.
