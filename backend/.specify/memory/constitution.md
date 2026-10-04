# Constituição do Assura

Plataforma de gestão e auditoria de SGI que reduz o trabalho operacional do auditor.

Este documento define os princípios que toda especificação, plano e tarefa do Assura deve
respeitar. Em caso de conflito entre uma especificação e esta constituição, a constituição
prevalece.

## Princípios

### I. O sistema funciona sem IA

- O Assura é construído primeiro como um sistema completo sem IA. Todo fluxo (montar
  checklist, executar auditoria, gerar relatório, acompanhar ações) funciona de ponta a ponta
  com entrada manual.
- A IA entra depois, como uma camada que acelera etapas que já existem. Ela nunca é o único
  caminho para concluir uma tarefa.
- Se um serviço de IA estiver indisponível, o auditor continua trabalhando pelo caminho manual.
- O relatório da V1 é gerado por modelo de documento preenchido com os dados registrados, sem
  geração de texto por IA.

### II. O auditor decide

- Nenhuma conclusão de auditoria é gravada como definitiva sem confirmação de uma pessoa.
- Quando a IA for adicionada, ela sugere e o auditor confirma, corrige ou descarta. A IA nunca
  declara uma não conformidade.
- O sistema guarda quem decidiu cada situação e quando.

### III. Rastreabilidade e imutabilidade

- Toda ação relevante gera um registro de histórico (quem, o quê, quando) em tabela só de
  inserção.
- Nada é excluído fisicamente: usuários, itens do banco e vínculos são desativados.
- Relatório aprovado não é alterado. Correção gera nova versão.
- O checklist de uma auditoria é uma cópia dos itens do banco. Mudanças posteriores no banco
  não alteram auditorias existentes.

### IV. Isolamento por empresa

- Toda tabela de negócio carrega `empresa_id`, e toda consulta filtra por ele.
- Nenhum endpoint devolve dados de uma empresa a um usuário sem vínculo ativo com ela.
- O isolamento é coberto por testes automatizados; uma falha nesses testes bloqueia a entrega.

### V. Papéis fixos e simples

- Usuário é identidade. Setor, cargo e permissões ficam no vínculo com a empresa.
- Papéis existentes: administrador do sistema, administrador da empresa; por projeto, responsável,
  membro e leitor; por auditoria avulsa, responsável; e, por auditoria, auditor líder e auditor.
- Cargo não é papel: cargo serve para atribuir trabalho, papel define o que a pessoa pode fazer.
- Toda empresa tem ao menos um administrador, todo projeto e toda auditoria avulsa têm ao menos um
  responsável, e toda auditoria iniciada tem ao menos um auditor líder. O sistema impede a remoção
  do último.
- Permissões configuráveis não entram enquanto os papéis fixos atenderem.

### VI. O campo vem primeiro

- A execução da auditoria é pensada para celular, com poucos toques por item: situação por
  botão, evidência em texto curto, foto opcional.
- Rede instável é condição normal. Nenhuma resposta registrada pode ser perdida por falta de
  sinal.
- Telas administrativas (cadastros, banco de itens, relatório) são web.

### VII. Escopo por fases

- **Fase 1 (sem IA):** empresa, usuários e papéis; banco de itens; montagem do checklist por
  filtro; execução no celular; relatório gerado por modelo; ações com responsável e prazo.
- **Fase 2 (IA na execução):** resposta por voz, transcrição e estruturação da fala, rascunho
  de relatório redigido por IA.
- **Fase 3 (IA sobre documentos):** cadastro de documentos, busca neles e análise de
  divergência contra procedimentos.
- Controle de documentos completo, tratativa completa de não conformidade e regulatórios só
  entram com evidência de necessidade vinda de auditores ou clientes.
- Toda funcionalidade é classificada como P0, P1 ou P2 antes de ser especificada. Só P0 entra
  em uma primeira entrega.
- A métrica de sucesso é o tempo entre o fim da auditoria e o relatório aprovado, medida desde
  a Fase 1.

### VIII. Preparado para a IA, sem construí-la antes da hora

- O modelo de dados da Fase 1 já separa a situação decidida pelo auditor de uma futura situação
  sugerida, e já prevê anexos por resposta. Isso evita migrações dolorosas na Fase 2.
- Nenhum código de IA, fila de processamento ou integração com provedor é escrito na Fase 1.
- Quando a IA entrar: transcrição e estruturação ficam em etapas separadas, cada provedor atrás
  de uma interface, toda saída validada contra um esquema, e a concordância entre sugestão e
  decisão do auditor é medida.

### IX. Privacidade e LGPD

- Evidências, fotos e, futuramente, áudios podem conter dados pessoais e são tratados como tal.
- O acesso às evidências é restrito a quem participa da auditoria e aos administradores da
  empresa.
- Dados de uma empresa nunca são usados como contexto para outra empresa.
- A gravação de áudio, quando existir, exige ciência das pessoas gravadas e prazo de retenção
  definido.

### X. Simplicidade

- Uma única aplicação, organizada em módulos. Serviços separados só com justificativa
  registrada.
- Não se constrói para um requisito futuro hipotético, com a exceção explícita do Princípio
  VIII.
- Entre duas soluções que atendem ao requisito, escolhe-se a que tem menos partes.

## Padrões de engenharia

### Domínio (DDD)

- O código é organizado por contexto de negócio, não por tipo técnico. Contextos iniciais:
  identidade e acesso, banco de itens, auditoria, ações, documentos.
- Cada contexto tem três camadas: domínio (entidades e regras), aplicação (casos de uso) e
  infraestrutura (banco, armazenamento, HTTP).
- A camada de domínio não importa FastAPI, SQLAlchemy nem qualquer biblioteca de
  infraestrutura. Regras de negócio são testáveis sem banco e sem servidor.
- Regras que nunca podem ser violadas ficam na entidade que as protege (ex.: a auditoria impede
  alteração depois do relatório aprovado; o projeto impede a remoção do último responsável).
- Um contexto só acessa outro pela interface pública dele, nunca pelas tabelas.
- Existe um glossário único de termos do domínio. O mesmo termo é usado na conversa com os
  auditores, na interface e no código.
- Padrões táticos (agregados, objetos de valor, eventos de domínio) entram quando resolvem um
  problema concreto, não por padrão. Cadastros simples podem ser simples.

### Testes primeiro (TDD)

- Regra de negócio nasce de um teste que falha: escrever o teste, ver falhar, implementar o
  mínimo, refatorar.
- Testes de domínio são unitários e rodam sem banco. Casos de uso têm testes de integração com
  banco real.
- O nome do teste descreve o comportamento esperado (ex.:
  `test_auditoria_com_relatorio_aprovado_nao_aceita_nova_resposta`).
- Correção de defeito começa por um teste que o reproduz.
- Código sem regra de negócio (configuração, mapeamento simples) não exige teste escrito antes.

### Código limpo

- Nomes de funções e variáveis descrevem o que fazem ou o que guardam. Função começa com verbo
  (`aprovar_versao_documento`), booleano responde a uma pergunta (`relatorio_esta_aprovado`).
- Sem abreviações, siglas internas ou nomes genéricos (`data`, `info`, `tmp`, `x`, `processar`,
  `handle`), exceto siglas do próprio domínio.
- Uma função faz uma coisa. Se o nome precisa de "e", ela é dividida.
- Comentário explica o porquê de uma decisão; o que o código faz deve estar claro pelos nomes.
- Sem números ou textos soltos com significado de negócio: viram constantes ou enumerações
  nomeadas.
- Erros de negócio são exceções com nome do domínio (`UltimoResponsavelNaoPodeSerRemovido`),
  não códigos nem mensagens genéricas.
- Formatação e análise estática são automáticas e obrigatórias antes de cada entrega.

## Padrões de qualidade

- Regras de permissão, isolamento por empresa e imutabilidade têm testes automatizados
  obrigatórios.
- Toda migração de banco é versionada e reversível.
- Termos do domínio seguem o vocabulário dos auditores, validado com eles, na interface e no
  código.

## Stack

- Frontend: Next.js (telas web e execução em campo como aplicativo web responsivo).
- Backend: Python com FastAPI.
- Banco de dados: PostgreSQL.
- IA (a partir da Fase 2): Strands Agents sobre Amazon Bedrock.

## Decisões em aberto

- Classificação dos achados (termos e níveis usados pelos auditores).
- Formato do relatório (modelo real usado pelos auditores).
- Edição vigente da ISO 19011 e normas cobertas (ISO 9001, 14001, 45001).
- Provedores de transcrição e de modelo de linguagem (somente na Fase 2).

## Decisões tomadas

- **2026-10-04:** a auditoria é realizada por uma equipe auditora, não por um único auditor. A
  auditoria pode ser criada sem equipe, mas só pode ser iniciada com ao menos um auditor líder;
  depois de iniciada, o sistema impede a remoção do último. O auditor líder pode realizar todas as
  ações da auditoria, inclusive aprovar o relatório; os demais auditores executam os itens do
  checklist.
- **2026-10-04:** a auditoria pode ser realizada dentro de um projeto ou de forma avulsa, sem
  vínculo com projeto. A auditoria avulsa tem ao menos um responsável, papel equivalente ao
  responsável do projeto, e só pode ser iniciada depois de vinculada a ao menos um auditor líder.

## Governança

- Esta constituição prevalece sobre especificações, planos e tarefas.
- Toda especificação declara como atende aos princípios aplicáveis. Exceções são registradas
  com motivo e prazo de revisão.
- Alterações exigem acordo dos três sócios e atualização da versão: mudança de princípio
  incrementa a versão principal; acréscimo incrementa a secundária; ajuste de redação
  incrementa a de correção.

**Versão**: 1.0.0 (rascunho) | **Ratificada**: TODO(RATIFICATION_DATE): pendente de ratificação pelos três sócios | **Última alteração**: 2026-10-04
