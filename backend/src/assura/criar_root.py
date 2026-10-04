"""Cria o primeiro administrador do sistema (root).

Uso: python -m assura.criar_root --nome "Nome" --email admin@empresa.com
A senha é pedida duas vezes, sem aparecer na tela.
"""

import argparse
import sys
from getpass import getpass

from assura.compartilhado.infraestrutura.banco import criar_fabrica_de_sessoes, criar_motor
from assura.configuracao import configuracao
from assura.historico import RegistrarAcao, criar_historico
from assura.identidade.aplicacao.criar_root import CriarRoot
from assura.identidade.dominio.erros import ErroDeIdentidade
from assura.identidade.infraestrutura.resumo_de_senha_argon2 import GeradorDeResumoArgon2
from assura.identidade.infraestrutura.usuarios_sqlalchemy import criar_usuarios

CODIGO_DE_FALHA = 1


def ler_argumentos() -> argparse.Namespace:
    leitor = argparse.ArgumentParser(description="Cria o primeiro administrador do sistema.")
    leitor.add_argument("--nome", required=True)
    leitor.add_argument("--email", required=True)
    return leitor.parse_args()


def criar_root(nome: str, email: str) -> int:
    senha = getpass("Senha: ")
    if getpass("Confirme a senha: ") != senha:
        print("as senhas não conferem", file=sys.stderr)
        return CODIGO_DE_FALHA
    fabrica_de_sessoes = criar_fabrica_de_sessoes(criar_motor(configuracao.url_banco_de_dados))
    with fabrica_de_sessoes() as sessao:
        try:
            root = CriarRoot(
                criar_usuarios(sessao),
                GeradorDeResumoArgon2(),
                RegistrarAcao(criar_historico(sessao)),
            ).executar(nome=nome, email=email, senha=senha)
        except ErroDeIdentidade as erro:
            print(erro, file=sys.stderr)
            return CODIGO_DE_FALHA
        sessao.commit()
    print(f"root criado: {root.email.valor}")
    return 0


if __name__ == "__main__":
    argumentos = ler_argumentos()
    sys.exit(criar_root(argumentos.nome, argumentos.email))
