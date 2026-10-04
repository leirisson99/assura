from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_usuario
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha, Usuarios
from assura.identidade.dominio.erros import SenhaAtualIncorreta
from assura.identidade.dominio.senha import validar_senha


class TrocarPropriaSenha:
    def __init__(
        self,
        usuarios: Usuarios,
        gerador_de_resumo: GeradorDeResumoDeSenha,
        registrar_acao: RegistrarAcao,
    ) -> None:
        self._usuarios = usuarios
        self._gerador_de_resumo = gerador_de_resumo
        self._registrar_acao = registrar_acao

    def executar(self, *, usuario_id: UUID, senha_atual: str, nova_senha: str) -> None:
        usuario = self._usuarios.obter(usuario_id)
        senha_atual_confere = (
            usuario.resumo_da_senha is not None
            and self._gerador_de_resumo.conferir(usuario.resumo_da_senha, senha_atual)
        )
        if not senha_atual_confere:
            raise SenhaAtualIncorreta("a senha atual não confere")
        usuario.definir_senha_definitiva(self._gerador_de_resumo.gerar(validar_senha(nova_senha)))
        self._usuarios.atualizar(usuario)
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.usuario(usuario.id),
            tipo_de_acao=TipoDeAcao.SENHA_TROCADA,
            usuario_id=usuario.id,
        )
