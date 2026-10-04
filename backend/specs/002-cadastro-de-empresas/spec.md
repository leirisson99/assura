# Especificação da funcionalidade: Cadastro de empresas

**Branch da funcionalidade**: `002-cadastro-de-empresas`

**Criada em**: 2026-10-04

**Situação**: Rascunho

**Entrada**: funcionalidade 1 do backlog, etapa 1.2 de `docs/ordem-de-desenvolvimento.md` (P0).
O administrador do sistema cadastra, altera, desativa e reativa empresas, e consulta as empresas
cadastradas. Toda ação fica no histórico de ações (funcionalidade 001).

## Cenários de uso e testes *(obrigatório)*

### História 1 - Cadastrar uma empresa (Prioridade: P1)

O administrador do sistema cadastra uma empresa cliente informando razão social, nome fantasia
(opcional) e CNPJ. A empresa nasce ativa e o cadastro fica registrado no histórico.

**Por que esta prioridade**: tudo o que vem depois (usuários, vínculos, projetos, auditorias)
pertence a uma empresa. Sem empresa cadastrada, nada mais existe.

**Teste independente**: cadastrar uma empresa com dados válidos e verificar que ela existe, está
ativa e tem um registro "empresa cadastrada" no histórico; tentar cadastrar com dados inválidos ou
CNPJ repetido e verificar que nada é gravado.

**Cenários de aceitação**:

1. **Dado** razão social, nome fantasia e um CNPJ válido ainda não cadastrado, **quando** o
   administrador do sistema cadastra a empresa, **então** ela fica gravada, ativa, e o histórico tem
   um registro "empresa cadastrada" com o autor, a empresa como objeto e os dados informados.
2. **Dado** um CNPJ com máscara (`12.345.678/0001-95`) ou sem máscara (`12345678000195`),
   **quando** a empresa é cadastrada, **então** o CNPJ é guardado sem máscara e as duas formas são
   tratadas como o mesmo CNPJ.
3. **Dado** um CNPJ alfanumérico válido (formato em vigor desde julho de 2026), **quando** a empresa
   é cadastrada, **então** o cadastro é aceito.
4. **Dado** um CNPJ com dígitos verificadores errados, tamanho errado ou caracteres não permitidos,
   **quando** o cadastro é tentado, **então** é recusado com erro de CNPJ inválido.
5. **Dado** um CNPJ já usado por outra empresa, ativa ou desativada, **quando** o cadastro é
   tentado, **então** é recusado com erro de CNPJ já cadastrado.
6. **Dado** razão social vazia, **quando** o cadastro é tentado, **então** é recusado.

---

### História 2 - Alterar os dados de uma empresa (Prioridade: P2)

O administrador do sistema corrige a razão social, o nome fantasia ou o CNPJ de uma empresa. O
histórico guarda apenas o que mudou, com o valor anterior e o novo.

**Por que esta prioridade**: erros de digitação e mudanças de razão social acontecem, mas o
cadastro precisa existir antes.

**Teste independente**: alterar um campo e verificar o novo valor e o registro "empresa alterada"
com valor anterior e novo apenas desse campo.

**Cenários de aceitação**:

1. **Dado** uma empresa cadastrada, **quando** o administrador altera a razão social, **então** a
   empresa passa a ter a nova razão social e o histórico registra "empresa alterada" com a razão
   social anterior e a nova, sem citar os campos que não mudaram.
2. **Dado** uma alteração que repete os valores atuais, **quando** é enviada, **então** nada muda e
   nenhum registro é criado.
3. **Dado** um novo CNPJ que já pertence a outra empresa, **quando** a alteração é tentada,
   **então** é recusada e a empresa continua igual.
4. **Dado** uma empresa desativada, **quando** o administrador altera seus dados, **então** a
   alteração é aceita (desativar não congela o cadastro).
5. **Dado** um identificador de empresa que não existe, **quando** a alteração é tentada, **então**
   é recusada com erro de empresa não encontrada.

---

### História 3 - Desativar e reativar uma empresa (Prioridade: P2)

O administrador do sistema desativa uma empresa que deixou de ser cliente, sem perder nenhum dado,
e pode reativá-la depois.

**Por que esta prioridade**: o Princípio III proíbe exclusão; desativar é a forma de tirar uma
empresa de uso.

**Teste independente**: desativar uma empresa ativa, verificar a situação e o registro "empresa
desativada"; reativar e verificar "empresa reativada".

**Cenários de aceitação**:

1. **Dado** uma empresa ativa, **quando** é desativada, **então** passa a desativada, continua
   existindo com todos os dados e o histórico registra "empresa desativada".
2. **Dado** uma empresa desativada, **quando** é reativada, **então** volta a ativa e o histórico
   registra "empresa reativada".
3. **Dado** uma empresa já desativada, **quando** se tenta desativá-la de novo, **então** a ação é
   recusada com erro claro. O mesmo vale para reativar uma empresa já ativa.

---

### História 4 - Consultar empresas (Prioridade: P3)

O administrador do sistema consulta uma empresa pelo identificador e lista as empresas, filtrando
por situação.

**Por que esta prioridade**: necessária para administrar, mas depende das anteriores.

**Teste independente**: cadastrar empresas ativas e desativadas e listar com e sem filtro.

**Cenários de aceitação**:

1. **Dado** uma empresa cadastrada, **quando** consultada pelo identificador, **então** retorna
   razão social, nome fantasia, CNPJ e situação.
2. **Dado** empresas ativas e desativadas, **quando** listadas com filtro "ativas", **então** só as
   ativas aparecem; sem filtro, aparecem todas.
3. **Dado** a listagem, **quando** há resultados, **então** vêm em ordem alfabética de razão social,
   em páginas de tamanho limitado.
4. **Dado** um identificador inexistente, **quando** consultado, **então** retorna erro de empresa
   não encontrada.

---

### Casos de borda

- Espaços no início e no fim da razão social e do nome fantasia são descartados; nome fantasia só
  com espaços é tratado como não informado.
- Razão social ou nome fantasia com mais de 150 caracteres: recusado.
- CNPJ com letras minúsculas no formato alfanumérico: convertido para maiúsculas antes de validar.
- CNPJ com todos os caracteres iguais (`00000000000000`, `11111111111111`): recusado, mesmo que os
  dígitos verificadores "batam".
- Dois cadastros simultâneos com o mesmo CNPJ: apenas um é aceito.
- Falha ao gravar o histórico: o cadastro, a alteração ou a mudança de situação também não é gravado.

## Requisitos *(obrigatório)*

### Requisitos funcionais

- **RF-001**: O sistema DEVE permitir ao administrador do sistema cadastrar empresa com razão social
  (obrigatória), nome fantasia (opcional) e CNPJ (obrigatório).
- **RF-002**: O sistema DEVE validar o CNPJ pelos dígitos verificadores, aceitando o formato
  numérico e o alfanumérico (12 caracteres de letras maiúsculas ou números seguidos de 2 dígitos),
  com ou sem máscara, e guardá-lo sem máscara.
- **RF-003**: O CNPJ DEVE ser único entre todas as empresas, incluindo as desativadas.
- **RF-004**: Toda empresa nasce ativa.
- **RF-005**: O sistema DEVE permitir alterar razão social, nome fantasia e CNPJ, com as mesmas
  validações do cadastro.
- **RF-006**: O sistema DEVE permitir desativar uma empresa ativa e reativar uma desativada, e
  recusar desativar o que já está desativado ou reativar o que já está ativo.
- **RF-007**: O sistema NÃO DEVE oferecer forma de excluir uma empresa.
- **RF-008**: Cada cadastro, alteração, desativação e reativação DEVE gerar exatamente um registro
  no histórico de ações, com o autor, a empresa como objeto e como empresa do registro, na mesma
  gravação da mudança.
- **RF-009**: O registro de alteração DEVE conter apenas os campos alterados, com valor anterior e
  novo; alteração sem mudança efetiva NÃO DEVE gerar registro.
- **RF-010**: O sistema DEVE permitir consultar uma empresa pelo identificador e listar empresas com
  filtro opcional por situação, em ordem alfabética de razão social e paginadas.
- **RF-011**: O histórico de ações DEVE aceitar como empresa do registro apenas empresas
  cadastradas (ou nenhuma).

### Entidades principais

- **Empresa**: cliente que usa o Assura. Atributos: razão social, nome fantasia (opcional), CNPJ
  (único), situação (ativa ou desativada).
- **CNPJ**: identificador da empresa na Receita Federal, em formato numérico ou alfanumérico, com
  dois dígitos verificadores.

## Critérios de sucesso *(obrigatório)*

### Resultados mensuráveis

- **CS-001**: 100% dos CNPJs inválidos dos casos de teste (numéricos e alfanuméricos) são recusados e
  100% dos válidos são aceitos.
- **CS-002**: 0 empresas com CNPJ repetido, mesmo com tentativas simultâneas.
- **CS-003**: 100% das ações sobre empresas têm exatamente um registro correspondente no histórico,
  e 0 registros existem para ações recusadas.
- **CS-004**: 0 empresas excluídas: toda empresa cadastrada continua consultável.

## Premissas

- Usuários e autenticação ainda não existem (etapas 1.3 e 1.4). O autor das ações é informado por
  quem chama; a restrição "só o administrador do sistema" passa a ser verificada quando houver
  autenticação.
- Sem endpoint HTTP nesta funcionalidade; a exposição vem com a autenticação.
- Os registros de histórico das ações sobre uma empresa pertencem à própria empresa, para que o
  futuro administrador da empresa veja quando e como ela foi cadastrada e alterada.
- Endereço, contatos e normas certificadas ficam fora desta funcionalidade; entram quando houver
  necessidade.
- A listagem é usada pelo administrador do sistema e não precisa de busca por texto nesta etapa.
