# Pesquisa: Usuários e vínculos com a empresa

## 1. Validação de e-mail

- **Decisão**: validação estrutural simples: uma parte local sem espaços, `@`, domínio com ao menos um
  ponto, sem espaços, até 254 caracteres; normalizado com `strip()` e `lower()`.
- **Motivo**: a validação definitiva de um e-mail é ele receber mensagens; regras completas da RFC
  5322 rejeitam endereços reais ou aceitam lixo. Sem dependência nova (Princípio X).
- **Alternativa rejeitada**: biblioteca `email-validator` (consulta DNS, dependência extra).

## 2. Unicidade

- **Decisão**: e-mail guardado em minúsculas com restrição `UNIQUE`; vínculo com `UNIQUE (usuario_id,
  empresa_id)`. Verificação prévia no caso de uso para erro claro e tradução da violação do banco
  (dentro de savepoint), como na 002.

## 3. Autor do histórico

- **Decisão**: `registro_de_historico.autor_usuario_id` passa a referenciar `usuario.id`
  (`ON DELETE RESTRICT`), como previsto no modelo da 001.
- **Consequência nos testes**: a fixture `sessao` grava um usuário fixo de teste
  (`ID_DO_AUTOR_DE_TESTE`) dentro da transação de cada teste; testes que precisam de vários autores
  usam a fixture `criar_usuario`.

## 4. Histórico e dados pessoais

- **Decisão**: `usuario_cadastrado` com detalhes vazios (o próprio usuário guarda nome e e-mail);
  `usuario_alterado` com anterior e novo só dos campos alterados; `usuario_vinculado` com
  `usuario_id`; `vinculo_desativado` e `vinculo_reativado` com `usuario_id`.
- **Objetos**: `usuario/<id>` sem empresa para ações sobre o usuário; `vinculo/<id>` com a empresa do
  vínculo para ações sobre o vínculo.
- **Motivo**: Princípio IX; registros sem empresa só são vistos pelo administrador do sistema.

## 5. Listagem de usuários da empresa

- **Decisão**: o caso de uso devolve `UsuarioDaEmpresa(usuario, vinculo)`; a consulta junta `vinculo`
  e `usuario` filtrando por `empresa_id`, ordena por `lower(nome)` e `usuario.id`, paginada com
  `Pagina`.
- **Motivo**: o isolamento por empresa é aplicado na própria consulta (Princípio IV).
