import random
from uuid import UUID

from assura.historico import Autor
from assura.identidade.dominio.cnpj import calcular_digitos_verificadores

# Usuário gravado pela fixture `sessao` em todo teste com banco: autor padrão das ações.
ID_DO_AUTOR_DE_TESTE = UUID("01900000-0000-7000-8000-000000000001")
AUTOR_DE_TESTE = Autor.usuario(ID_DO_AUTOR_DE_TESTE)


def gerar_cnpj_valido() -> str:
    raiz_e_ordem = "".join(random.choices("0123456789", k=12))
    return raiz_e_ordem + calcular_digitos_verificadores(raiz_e_ordem)
