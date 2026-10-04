# Pesquisa: Cadastro de empresas

## 1. CNPJ alfanumérico

- **Decisão**: `Cnpj` aceita 12 caracteres `[0-9A-Z]` seguidos de 2 dígitos `[0-9]`. O valor de cada
  caractere no cálculo é o código ASCII menos 48 (`0`–`9` valem 0–9, `A` vale 17 … `Z` vale 42).
  Pesos `5,4,3,2,9,8,7,6,5,4,3,2` para o primeiro dígito e `6,5,4,3,2,9,8,7,6,5,4,3,2` para o
  segundo; resto da divisão por 11 menor que 2 dá dígito 0, senão 11 menos o resto.
- **Motivo**: é a regra da Receita Federal para o CNPJ alfanumérico (em vigor desde julho de 2026).
  Para CNPJs só numéricos o resultado é idêntico ao cálculo tradicional, então um único algoritmo
  atende aos dois formatos.
- **Normalização**: remove espaços nas pontas e os caracteres de máscara `.`, `/` e `-`, e converte
  para maiúsculas. Guardado sem máscara, 14 caracteres. Sequências de um só caractere repetido são
  recusadas.

## 2. Unicidade do CNPJ

- **Decisão**: verificação no caso de uso (erro claro `CnpjJaCadastrado`) e restrição `UNIQUE` no
  banco. A gravação roda dentro de um savepoint; violação da restrição vira `CnpjJaCadastrado`.
- **Motivo**: a verificação prévia sozinha não impede dois cadastros simultâneos (CS-002).

## 3. Empresa do registro de histórico

- **Decisão**: ações sobre uma empresa registram `empresa_id` = a própria empresa, inclusive o
  cadastro (a empresa é gravada antes do registro, na mesma transação).
- **Motivo**: o administrador da empresa (1.5) verá a origem e as mudanças do cadastro da própria
  empresa. A spec 001 citava o cadastro de empresa como exemplo de ação "sem empresa"; com a empresa
  já gravada na transação, isso deixou de ser necessário.

## 4. Tipos de ação

- **Decisão**: `TipoDeAcao` ganha `EMPRESA_CADASTRADA`, `EMPRESA_ALTERADA`, `EMPRESA_DESATIVADA` e
  `EMPRESA_REATIVADA`.
- **Consequência**: uma enumeração com membros não pode ser estendida, então a subclasse de teste da
  001 (`TipoDeAcaoDeTeste`) deixa de existir; os testes do histórico passam a usar os tipos reais.

## 5. Chave estrangeira do histórico

- **Decisão**: `registro_de_historico.empresa_id` referencia `empresa.id` (`ON DELETE RESTRICT`,
  coerente com a ausência de exclusão). Os testes do histórico passam a criar empresas reais por uma
  fixture que grava direto na tabela `empresa`, sem gerar registros de histórico.

## 6. Paginação compartilhada

- **Decisão**: `Pagina` e `PaginaInvalida` vão para `assura.compartilhado.dominio.pagina`. O histórico
  continua exportando os mesmos nomes.
- **Motivo**: evitar que `identidade` importe o domínio de `historico` e evitar duplicação.

## 7. Alteração

- **Decisão**: `AlterarEmpresa` recebe os três campos completos (substituição), e o domínio devolve
  apenas os campos que mudaram (`{campo: {"anterior": ..., "novo": ...}}`). Sem mudança, nada é
  gravado nem registrado.
- **Motivo**: mais simples que alteração parcial e ainda atende RF-009.
