import random

from assura.identidade.dominio.cnpj import calcular_digitos_verificadores


def gerar_cnpj_valido() -> str:
    raiz_e_ordem = "".join(random.choices("0123456789", k=12))
    return raiz_e_ordem + calcular_digitos_verificadores(raiz_e_ordem)
