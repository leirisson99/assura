# Ordem de desenvolvimento

Sequência das funcionalidades de [funcionalidades.md](funcionalidades.md) (números entre parênteses) organizada por dependência: cada etapa usa apenas o que as anteriores já entregaram, e nada construído precisa ser refeito depois.

Itens marcados com **[falta no backlog]** são pré-requisitos que não aparecem na lista de funcionalidades.

## Primeira entrega (P0)

### Etapa 1 — Empresa e usuários

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 1.1 | Histórico de ações (10) | — |
| 1.2 | Cadastro de empresas pelo administrador do sistema (1) | 1.1 |
| 1.3 | Cadastro de usuários e vínculo com a empresa (2) | 1.2 |
| 1.4 | Autenticação (login e sessão) **[falta no backlog]** | 1.3 |
| 1.5 | Administrador da empresa, no mínimo um por empresa (3) | 1.3, 1.4 |
| 1.6 | Desativação de usuário sem exclusão (9) | 1.5 |

O histórico vem primeiro porque toda ação a partir do cadastro de empresas já precisa ser registrada (Princípio III). O isolamento por empresa e seus testes (Princípio IV) nascem junto com o 1.2 e acompanham todas as etapas seguintes.

### Etapa 2 — Projetos

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 2.1 | Criação de projetos (5) | Etapa 1 |
| 2.2 | Papéis por projeto: responsável, membro e leitor (6) | 2.1 |
| 2.3 | Vários responsáveis e bloqueio de remoção do último (7) | 2.2 |

### Etapa 3 — Banco de itens

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 3.1 | Cadastro de processos da empresa (11) | Etapa 1 |
| 3.2 | Cadastro de itens de verificação, com requisito e processo (12) | 3.1 |
| 3.3 | Ativar e desativar itens (13) | 3.2 |

A etapa 3 não depende da etapa 2 e pode ser desenvolvida em paralelo a ela.

### Etapa 4 — Preparação da auditoria

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 4.1 | Criação da auditoria: escopo, data e equipe auditora (15) | Etapa 1 (e etapa 2 quando vinculada a projeto) |
| 4.2 | Montagem do checklist por filtro de processo e requisito (16) | 4.1, etapa 3 |
| 4.3 | Registro das reuniões de abertura e de encerramento (18) | 4.1 |

**Decidido (2026-10-04):** a auditoria pode ser criada dentro de um projeto ou de forma avulsa. A auditoria avulsa depende só da etapa 1; a vinculada a projeto depende também da etapa 2.

### Etapa 5 — Execução em campo

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 5.1 | Execução no celular: situação por botão e evidência em texto (19) | 4.2 |
| 5.2 | Item avulso criado em campo (20) | 5.1 |

Para que o modo sem internet (22) não exija refazer a execução depois, as respostas já nascem com identificador gerado no aparelho e o envio ao servidor é idempotente (reenviar a mesma resposta não a duplica). O modelo de dados já separa a situação decidida da sugerida e prevê anexos por resposta (Princípio VIII).

### Etapa 6 — Achados e relatório

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 6.1 | Registro de achados a partir das respostas (25) | 5.1 |
| 6.2 | Relatório gerado por modelo de documento (23) | 4.3, 6.1 |
| 6.3 | Revisão, aprovação e versões do relatório (24) | 6.2 |
| 6.4 | Medição do tempo entre o fim da auditoria e o relatório aprovado **[falta no backlog]** | 4.3, 6.3 |

**Decisões necessárias:** classificação dos achados (antes de 6.1) e formato do relatório (antes de 6.2).

### Etapa 7 — Ações

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 7.1 | Ação corretiva com causa, responsável e prazo (26) | 6.1 |
| 7.2 | Acompanhamento de prazos e encerramento (27) | 7.1 |

Com a etapa 7, o ciclo completo da Fase 1 funciona de ponta a ponta sem IA (Princípio I).

### Etapa 8 — Gestão de documentos

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 8.1 | Cadastro de documentos com código, tipo, processo e dono (30) | 3.1 |
| 8.2 | Upload de arquivo e controle de versões (31) | 8.1 |
| 8.3 | Aprovação em uma etapa, com uma única versão vigente (32) | 8.2 |
| 8.4 | Lista mestra (33) | 8.3 |

**Conflito pendente:** a constituição coloca o cadastro de documentos na Fase 3 e não na primeira entrega. A etapa fica por último na primeira entrega porque o ciclo de auditoria não depende dela; se o conflito for resolvido tirando-a da Fase 1, ela sai daqui sem afetar as etapas anteriores.

## Segunda entrega (P1)

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 9.1 | Foto como evidência (21) | Etapa 5 |
| 9.2 | Funcionamento sem internet, com envio posterior (22) | 9.1 |
| 9.3 | Cadastro de setores e cargos (4) | Etapa 1 |
| 9.4 | Transferência de titularidade do projeto (8) | Etapa 2 |
| 9.5 | Importação de itens por planilha (14) | Etapa 3 |
| 9.6 | Duplicar uma auditoria anterior (17) | Etapa 4 |
| 9.7 | Verificação de eficácia da ação (28) | Etapa 7 |
| 9.8 | Exportação de não conformidades para outro sistema (29) | Etapa 7 |
| 9.9 | Revisão periódica com alerta de vencimento (34) | Etapa 8 |
| 9.10 | Confirmação de leitura (35) | Etapa 8 |
| 9.11 | Documentos de origem externa (36) | Etapa 8 |
| 9.12 | Ligação entre item de verificação e documento (37) | Etapas 3 e 8 |

A foto (9.1) vem antes do modo sem internet (9.2) para que a sincronização seja construída uma única vez já cobrindo respostas e fotos. Os dois abrem a segunda entrega por causa do Princípio VI (nenhuma resposta perdida por falta de sinal). Os demais itens são independentes entre si e podem seguir a ordem de valor para os auditores.

## Fase 2 — IA na execução

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 10.1 | Resposta por voz com transcrição (38) | Etapa 5, 9.2 |
| 10.2 | Estruturação da fala em situação e evidência, com confirmação do auditor (39) | 10.1 |
| 10.3 | Rascunho do relatório redigido por IA (40) | Etapa 6 |

## Fase 3 — IA sobre documentos

| Ordem | Funcionalidade | Depende de |
|---|---|---|
| 11.1 | Perguntas sobre os documentos, com citação da fonte (41) | Etapa 8 |
| 11.2 | Análise de divergência entre a resposta e o procedimento (42) | 9.12, 11.1 |

## Fora das fases da constituição

Sem posição na sequência até serem incluídos na constituição ou terem a necessidade comprovada:

- Sugestão de itens de checklist (43)
- Padrões entre auditorias e painel de indicadores (44)
- Tratativa completa de não conformidade (45)
- Módulo de regulatórios (46)
