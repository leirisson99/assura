# Especificação da funcionalidade: Histórico de ações

**Branch da funcionalidade**: `001-historico-de-acoes`

**Criada em**: 2026-10-04

**Situação**: Rascunho

**Entrada**: funcionalidade 10 do backlog, etapa 1.1 de `docs/ordem-de-desenvolvimento.md` (P0).
Registro de quem fez o quê e quando para toda ação relevante do Assura (Princípio III).

## Cenários de uso e testes *(obrigatório)*

### História 1 - Registrar uma ação junto com a mudança que ela causou (Prioridade: P1)

Sempre que uma funcionalidade do Assura realiza uma ação relevante (por exemplo, cadastrar uma
empresa ou desativar um usuário), ela registra no histórico quem fez, o que fez, sobre qual objeto,
em qual empresa, quando e com quais detalhes. O registro e a mudança acontecem juntos: ou os dois
ficam gravados, ou nenhum.

**Por que esta prioridade**: é a base de rastreabilidade de todo o sistema. As funcionalidades
seguintes (empresas, usuários, vínculos, administrador da empresa, desativação) dependem dela para
cumprir o Princípio III desde o primeiro dia.

**Teste independente**: executar uma ação de negócio de exemplo e verificar que existe exatamente um
registro com autor, tipo de ação, objeto, empresa, data e hora e detalhes corretos; forçar uma falha
na ação e verificar que nenhum registro foi criado.

**Cenários de aceitação**:

1. **Dado** um usuário autor e uma empresa, **quando** uma ação de negócio é concluída, **então**
   o histórico tem um novo registro com o autor, o tipo de ação, o tipo e o identificador do objeto,
   a empresa, a data e hora do servidor e os detalhes da mudança.
2. **Dado** uma ação de negócio que falha depois de iniciar o registro, **quando** a falha ocorre,
   **então** nem a mudança nem o registro de histórico ficam gravados.
3. **Dado** uma falha ao gravar o registro de histórico, **quando** a ação de negócio é executada,
   **então** a mudança de negócio também não é gravada.
4. **Dado** uma ação do administrador do sistema que não pertence a nenhuma empresa (por exemplo,
   cadastrar uma nova empresa antes de ela existir), **quando** é registrada, **então** o registro fica
   sem empresa e só é visível para administradores do sistema.

---

### História 2 - Garantir que o histórico não pode ser alterado nem apagado (Prioridade: P1)

Nenhum registro do histórico pode ser alterado ou excluído depois de gravado, nem pela aplicação nem
por um comando executado diretamente no banco de dados por engano.

**Por que esta prioridade**: um histórico que pode ser alterado não serve como prova em auditoria.
A imutabilidade faz parte do Princípio III e tem teste obrigatório pelos padrões de qualidade.

**Teste independente**: gravar um registro e tentar alterá-lo e excluí-lo, tanto pela aplicação quanto
por comando direto no banco; as tentativas são rejeitadas e o registro permanece igual.

**Cenários de aceitação**:

1. **Dado** um registro gravado, **quando** a aplicação tenta alterá-lo ou excluí-lo, **então** não
   existe operação disponível para isso.
2. **Dado** um registro gravado, **quando** alguém executa diretamente no banco um comando de
   alteração ou exclusão sobre o histórico, **então** o banco rejeita o comando e o registro permanece
   inalterado.

---

### História 3 - Consultar o histórico com filtros, respeitando a empresa (Prioridade: P2)

O administrador da empresa consulta o histórico da própria empresa, filtrando por período, autor, tipo
de ação e objeto. O administrador do sistema consulta o histórico de todas as empresas, inclusive os
registros sem empresa.

**Por que esta prioridade**: a consulta dá valor ao registro, mas o registro precisa existir antes.
A tela web de consulta fica para depois; esta funcionalidade entrega a consulta como capacidade do
sistema, para ser exposta quando houver autenticação.

**Teste independente**: gravar registros em duas empresas e sem empresa; consultar como administrador
de uma empresa e verificar que só aparecem os registros dela; consultar como administrador do sistema e
verificar que aparecem todos; aplicar cada filtro e verificar o resultado.

**Cenários de aceitação**:

1. **Dado** registros das empresas A e B, **quando** o administrador da empresa A consulta o
   histórico, **então** recebe apenas registros da empresa A.
2. **Dado** registros das empresas A e B e registros sem empresa, **quando** o administrador do sistema
   consulta, **então** recebe todos.
3. **Dado** registros de vários períodos, autores, tipos de ação e objetos, **quando** a consulta usa
   um ou mais filtros, **então** só retornam registros que atendem a todos os filtros informados.
4. **Dado** uma consulta, **quando** há resultados, **então** eles vêm do mais recente para o mais
   antigo, em páginas de tamanho limitado.
5. **Dado** o administrador da empresa A, **quando** ele tenta consultar o histórico da empresa B,
   **então** a consulta é recusada.

---

### Casos de borda

- Ação sem autor identificado: não é aceita. Todo registro tem autor; até existir autenticação
  (etapa 1.4), o autor é informado por quem chama a capacidade de registro.
- Ação automática do próprio sistema (sem pessoa por trás): registrada com o autor "sistema",
  distinguível de um usuário.
- Tipo de ação desconhecido: não é aceito. Os tipos de ação formam uma lista nomeada e fechada, que
  cresce com cada funcionalidade.
- Registro de empresa sem empresa informada, ou usuário de empresa consultando sem empresa: recusado.
- Período com início depois do fim: consulta recusada com erro claro.
- Consulta sem resultados: retorna lista vazia, não erro.
- Detalhes da mudança com dados pessoais: guardar apenas o necessário para entender a mudança
  (Princípio IX).
- Duas ações no mesmo instante: ambas são registradas, e a ordem entre elas é estável.

## Requisitos *(obrigatório)*

### Requisitos funcionais

- **RF-001**: O sistema DEVE oferecer às demais funcionalidades uma forma única de registrar uma
  ação no histórico.
- **RF-002**: Cada registro DEVE conter: autor (usuário ou "sistema"), tipo de ação, tipo do objeto
  afetado, identificador do objeto afetado, empresa (ou nenhuma, só para ações do administrador do
  sistema fora de empresa), data e hora do servidor e detalhes da mudança.
- **RF-003**: A data e a hora DEVEM ser definidas pelo servidor no momento do registro, nunca
  informadas por quem chama.
- **RF-004**: O registro de histórico e a mudança de negócio DEVEM ser gravados juntos: se um
  falhar, nenhum dos dois fica gravado.
- **RF-005**: O sistema NÃO DEVE oferecer nenhuma forma de alterar ou excluir um registro de
  histórico.
- **RF-006**: O armazenamento DEVE rejeitar alteração e exclusão de registros de histórico mesmo
  quando o comando é executado diretamente, fora da aplicação.
- **RF-007**: Os tipos de ação DEVEM ser uma lista nomeada e fechada; registros com tipo fora da
  lista DEVEM ser recusados.
- **RF-008**: Registros sem autor DEVEM ser recusados.
- **RF-009**: O sistema DEVE permitir consultar o histórico filtrando por período, autor, tipo de
  ação e objeto (tipo e identificador), combinando os filtros informados.
- **RF-010**: A consulta feita por um administrador da empresa DEVE retornar apenas registros da
  própria empresa e DEVE recusar consulta a outra empresa.
- **RF-011**: A consulta feita pelo administrador do sistema DEVE poder retornar registros de todas as
  empresas e os registros sem empresa.
- **RF-012**: Os resultados DEVEM vir do mais recente para o mais antigo, em páginas de tamanho
  limitado.
- **RF-013**: O isolamento por empresa e a imutabilidade DEVEM ser cobertos por testes automatizados
  que bloqueiam a entrega quando falham.

### Entidades principais

- **Registro de histórico**: uma ação relevante já realizada. Atributos: autor, tipo de ação, tipo
  do objeto, identificador do objeto, empresa (opcional), data e hora, detalhes. Nunca muda depois
  de criado.
- **Tipo de ação**: nome de uma ação do domínio (por exemplo, "empresa cadastrada", "usuário
  desativado"). Lista fechada; cada funcionalidade acrescenta os seus.
- **Autor**: quem realizou a ação: um usuário (identificado) ou o próprio sistema.
- **Solicitante da consulta**: quem consulta e com qual alcance: administrador do sistema (todas as
  empresas) ou administrador de uma empresa (só a dele).

## Critérios de sucesso *(obrigatório)*

### Resultados mensuráveis

- **CS-001**: 100% das ações de negócio concluídas têm exatamente um registro de histórico
  correspondente; 0 registros existem para ações que falharam.
- **CS-002**: 0 registros de histórico alterados ou excluídos, verificado por tentativas de alteração e
  exclusão pela aplicação e diretamente no armazenamento.
- **CS-003**: 0 registros de outra empresa retornados em consultas de administradores de empresa,
  verificado por testes automatizados com no mínimo duas empresas.
- **CS-004**: Um administrador encontra as ações de um objeto específico em um histórico com 100 mil
  registros em até 2 segundos.

## Premissas

- Usuários, empresas e autenticação ainda não existem (etapas 1.2 a 1.4). Até lá, o autor e o alcance
  de quem consulta são informados por quem chama a capacidade; quando a autenticação existir, eles
  passam a vir da sessão.
- A consulta não é exposta por endereço web nesta funcionalidade: sem autenticação, isso exporia o
  histórico de todas as empresas. A exposição entra junto com a autenticação (etapa 1.4) e a tela,
  depois.
- Nenhuma ação de negócio real existe ainda; os testes usam uma ação de exemplo. As próximas
  funcionalidades acrescentam seus tipos de ação.
- O histórico é mantido por tempo indeterminado. Política de retenção, se necessária, será decidida
  depois.
- Os detalhes da mudança são um conteúdo livre e estruturado definido por cada tipo de ação.
