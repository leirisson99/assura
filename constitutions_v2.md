# Constituição do Assura

Plataforma de gestão e auditoria de SGI que reduz o trabalho operacional do auditor.

Este documento define os princípios que toda especificação, plano e tarefa do Assura deve respeitar. Em caso de conflito entre uma especificação e esta constituição, a constituição prevalece.

## 1. Produto

- **Para quem:** empresas que mantêm um sistema de gestão integrado (qualidade, meio ambiente, segurança do trabalho) e seus auditores internos.
- **Problema:** o relatório de uma auditoria leva de 4 a 5 dias para ser montado depois da visita.
- **Resultado esperado:** relatório aprovado em até um dia.
- **Métrica principal:** tempo entre o fim da auditoria e o relatório aprovado, medido desde a Fase 1.
- **Posicionamento:** plataforma de gestão e auditoria de SGI. A IA é um meio de reduzir trabalho operacional, não o produto.

## 2. Princípios

### I. O sistema funciona sem IA

- O Assura é construído primeiro como um sistema completo sem IA. Todo fluxo fecha de ponta a ponta com entrada manual.
- A IA entra depois, como camada que acelera etapas que já existem. Ela nunca é o único caminho para concluir uma tarefa.
- Se um serviço de IA estiver indisponível, o usuário continua trabalhando pelo caminho manual.

### II. O auditor decide

- Nenhuma conclusão de auditoria é gravada como definitiva sem confirmação de uma pessoa.
- A IA sugere; o auditor confirma, corrige ou descarta. A IA nunca declara uma não conformidade, apenas sinaliza "possível divergência".
- O sistema guarda quem decidiu cada situação e quando, separado do que foi sugerido.

### III. Rastreabilidade de ponta a ponta

- Todo achado é rastreável pela cadeia: requisito → processo → documento → item verificado → resposta → evidência.
- Requisito é entidade própria, ligada a processos e a documentos. Não é texto livre.
- Toda resposta tem ao menos uma evidência ou a declaração explícita de que não houve.
- Evidência tem tipo: documento, foto, registro, entrevista, indicador ou sistema.
- A resposta registra quem foi entrevistado e em qual setor.

### IV. Histórico e imutabilidade

- Toda ação relevante gera um registro de histórico (quem, o quê, quando) em tabela só de inserção.
- Nada é excluído fisicamente: usuários, itens, requisitos e vínculos são desativados.
- Relatório aprovado e versão de documento aprovada não são alterados. Correção gera nova versão.
- O checklist de uma auditoria é uma cópia dos itens do banco. Mudanças posteriores no banco não alteram auditorias existentes.

### V. Isolamento por empresa

- Toda tabela de negócio carrega `empresa_id`, e toda consulta filtra por ele.
- Nenhum endpoint devolve dados de uma empresa a um usuário sem vínculo ativo com ela.
- O `empresa_id` vem sempre da sessão do usuário, nunca de um valor informado pelo cliente ou por um modelo de IA.
- O isolamento é coberto por testes automatizados; uma falha nesses testes bloqueia a entrega.

### VI. Papéis fixos e simples

- Usuário é identidade. Setor, cargo e permissões ficam no vínculo com a empresa.
- Papéis: administrador do sistema, administrador da empresa e, por projeto, responsável, membro e leitor.
- Cargo não é papel: cargo serve para atribuir trabalho, papel define o que a pessoa pode fazer.
- Toda empresa tem ao menos um administrador e todo projeto tem ao menos um responsável. O sistema impede a remoção do último.
- Um projeto pode ter vários responsáveis, e a titularidade pode ser transferida.
- Permissões configuráveis não entram enquanto os papéis fixos atenderem.

### VII. O campo vem primeiro

- A execução da auditoria é pensada para celular, com poucos toques por item: situação por botão, evidência em texto curto, foto opcional.
- Rede instável é condição normal. Nenhuma resposta registrada pode ser perdida por falta de sinal.
- Nada que o auditor faz em campo espera por processamento em segundo plano.
- Telas administrativas (cadastros, banco de itens, documentos, relatório) são web.

### VIII. Escopo guiado por evidência

- Uma funcionalidade só é especificada com evidência de necessidade vinda de auditores ou clientes.
- Toda funcionalidade é classificada como P0, P1 ou P2 antes de ser especificada. Só P0 entra em uma primeira entrega.
- O cadastro inicial de uma empresa (processos, requisitos, itens) precisa ser viável em horas, não em dias. Importação por planilha é P0.

### IX. Privacidade e LGPD

- Evidências, fotos, nomes de entrevistados e, futuramente, áudios são dados pessoais e são tratados como tal.
- O acesso às evidências é restrito a quem participa da auditoria e aos administradores da empresa.
- Dados de uma empresa nunca são usados como contexto para outra empresa nem para treinar modelos.
- A gravação de áudio, quando existir, exige ciência das pessoas gravadas e prazo de retenção definido por empresa.
- Do texto das normas guarda-se apenas o número da cláusula e um título próprio. O conteúdo das normas é protegido por direito autoral e não é reproduzido.

### X. Simplicidade

- Uma única aplicação, organizada em módulos. Serviços separados só com justificativa registrada.
- Não se constrói para um requisito futuro hipotético. A única exceção são as reservas no modelo de dados listadas na seção 5.
- Entre duas soluções que atendem ao requisito, escolhe-se a que tem menos partes.

## 3. Fases

| Fase | Conteúdo | IA |
|---|---|---|
| 1 | Identidade e acesso; requisitos, processos e banco de itens; auditoria no celular; relatório por modelo de documento; ações com responsável e prazo | Nenhuma |
| 2 | Resposta por voz; transcrição; estruturação da fala; redação da não conformidade; rascunho do relatório | Etapas fixas |
| 3 | Análise de divergência contra procedimentos; perguntas sobre documentos; investigação de causa; sugestão de ações e de itens; padrões entre auditorias | Agentes |

- A gestão de documentos é pré-requisito da Fase 3. Sua posição em relação à Fase 1 está em "Decisões em aberto".
- Tratativa completa de não conformidade e regulatórios não têm fase definida e dependem do Princípio VIII.

## 4. Stack

- Frontend: Next.js (telas web e execução em campo como aplicativo web responsivo).
- Backend: Python com FastAPI.
- Banco de dados: PostgreSQL.
- Arquivos: armazenamento de objetos, com link temporário para acesso. O banco guarda apenas os dados do arquivo.
- IA (a partir da Fase 2): Strands Agents sobre Amazon Bedrock.

## 5. Arquitetura de IA

Vale a partir da Fase 2. Nenhum código de IA, fila de processamento ou integração com provedor é escrito na Fase 1.

### Reservas no modelo de dados da Fase 1

- A resposta tem a situação decidida pelo auditor e um campo separado, vazio, para a situação sugerida.
- A evidência tem tipo, o que permite acrescentar áudio na Fase 2 sem migração estrutural.

### Três formas de usar IA

1. **Sem IA.** Alertas de prazo, acompanhamento de ações e indicadores são código comum.
2. **Etapa fixa.** Chamada direta ao modelo, com entrada e saída definidas por esquema. Usada para transcrição, estruturação da fala, redação da não conformidade e rascunho do relatório.
3. **Agente.** Usado somente quando a tarefa exige decidir quais dados consultar.

Sempre se escolhe a forma mais simples que resolve.

### Agentes

São três, um por fase do trabalho do auditor. Criar outro exige alteração desta constituição.

| Agente | Quando atua | O que faz | Ferramentas |
|---|---|---|---|
| Planejamento | Ao criar a auditoria (web) | Sugere itens do checklist, aponta pontos de atenção e riscos, propõe o plano | Banco de itens, requisitos, histórico, ações, documentos |
| Execução | A cada item respondido (celular) | Compara a resposta com o procedimento, responde perguntas sobre documentos, avisa quando falta evidência | Documentos vigentes, auditoria em andamento |
| Pós-auditoria | Após o encerramento (web) | Conduz a investigação de causa pelo método dos 5 porquês, sugere ações corretivas, aponta padrões entre auditorias | Auditoria concluída, histórico, ações |

### Regras

- **Sem agente coordenador.** A tela em que o usuário está determina qual agente é chamado. Essa escolha é código comum.
- **Ferramentas somente de leitura.** Nenhum agente grava, altera ou exclui dados.
- **Ferramentas filtradas por empresa,** conforme o Princípio V.
- **Citação obrigatória.** Toda afirmação baseada em documento traz documento, seção e trecho. Sem fonte, o agente diz que não encontrou.
- **Saída validada.** Toda saída estruturada é validada contra um esquema antes de ser usada. Saída inválida vira erro tratado, não dado.
- **Provedor atrás de interface.** A lógica de negócio não chama Strands nem Bedrock diretamente.
- **Medição.** A concordância entre a sugestão da IA e a decisão do auditor é registrada desde a primeira etapa de IA.
- **Ordem de construção:** etapas fixas na Fase 2; na Fase 3, agente de execução, depois pós-auditoria, depois planejamento.

## 6. Padrões de engenharia

### Domínio (DDD)

- O código é organizado por contexto de negócio: identidade e acesso, requisitos e banco de itens, auditoria, ações, documentos.
- Cada contexto tem três camadas: domínio (entidades e regras), aplicação (casos de uso) e infraestrutura (banco, armazenamento, HTTP).
- A camada de domínio não importa FastAPI, SQLAlchemy nem qualquer biblioteca de infraestrutura.
- Regras que nunca podem ser violadas ficam na entidade que as protege.
- Um contexto só acessa outro pela interface pública dele, nunca pelas tabelas.
- Existe um glossário único de termos do domínio, validado com os auditores. O mesmo termo é usado na conversa, na interface e no código.
- Padrões táticos (agregados, objetos de valor, eventos de domínio) entram quando resolvem um problema concreto. Cadastros simples podem ser simples.

### Testes primeiro (TDD)

- Regra de negócio nasce de um teste que falha: escrever o teste, ver falhar, implementar o mínimo, refatorar.
- Testes de domínio são unitários e rodam sem banco. Casos de uso têm testes de integração com banco real.
- O nome do teste descreve o comportamento esperado (ex.: `test_ultimo_responsavel_nao_pode_ser_removido`).
- Correção de defeito começa por um teste que o reproduz.
- Permissões, isolamento por empresa e imutabilidade têm testes obrigatórios.
- Código sem regra de negócio (configuração, mapeamento simples) não exige teste escrito antes.

### Código limpo

- Nomes de funções e variáveis descrevem o que fazem ou o que guardam. Função começa com verbo (`aprovar_versao_documento`), booleano responde a uma pergunta (`relatorio_esta_aprovado`).
- Sem abreviações nem nomes genéricos (`data`, `info`, `tmp`, `processar`, `handle`), exceto siglas do próprio domínio.
- Uma função faz uma coisa. Se o nome precisa de "e", ela é dividida.
- Comentário explica o porquê de uma decisão; o que o código faz deve estar claro pelos nomes.
- Valores com significado de negócio viram constantes ou enumerações nomeadas.
- Erros de negócio são exceções com nome do domínio (`UltimoResponsavelNaoPodeSerRemovido`).
- Formatação e análise estática são automáticas e obrigatórias antes de cada entrega.
- Toda migração de banco é versionada e reversível.

## 7. Decisões em aberto

- Idioma do código (os exemplos deste documento assumem português).
- Posição da gestão de documentos: antes, junto ou depois da auditoria na Fase 1.
- Classificação dos achados: termos e níveis usados pelos auditores.
- Formato do relatório: modelo real usado pelos auditores.
- Auditoria com um auditor ou com equipe auditora.
- Auditoria sempre dentro de um projeto ou também avulsa.
- Edição vigente da ISO 19011 e normas cobertas (ISO 9001, 14001, 45001).
- Escopo da tratativa de não conformidade e do módulo de regulatórios.
- Provedores de transcrição e modelo de linguagem (somente na Fase 2).

## 8. Governança

- Esta constituição prevalece sobre especificações, planos e tarefas.
- Toda especificação declara como atende aos princípios aplicáveis. Exceções são registradas com motivo e prazo de revisão.
- Uma decisão em aberto, quando fechada, sai da seção 7 e entra na seção correspondente.
- Alterações exigem acordo dos três sócios e atualização da versão: mudança de princípio incrementa a versão principal; acréscimo incrementa a secundária; ajuste de redação incrementa a de correção.

**Versão:** 2.0.0 (rascunho, ainda não ratificada pelos sócios) | **Última alteração:** 2026-10-04