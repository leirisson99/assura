from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import (
    registrar_acao_sobre_usuario,
    registrar_acao_sobre_vinculo,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import (
    Empresas,
    UsuarioAutenticado,
    UsuarioDaEmpresa,
    Usuarios,
    Vinculos,
)
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.empresa import SituacaoDaEmpresa
from assura.identidade.dominio.erros import EmpresaDesativadaNaoAceitaVinculo, VinculoJaExiste
from assura.identidade.dominio.usuario import Usuario
from assura.identidade.dominio.vinculo import Vinculo


class IncluirUsuarioNaEmpresa:
    """Inclui uma pessoa na empresa pelo e-mail: cadastra o usuário se ainda não existe ou vincula
    o existente (que pode trabalhar em outras empresas) sem alterar os dados dele."""

    def __init__(
        self,
        usuarios: Usuarios,
        empresas: Empresas,
        vinculos: Vinculos,
        permissoes: Permissoes,
        registrar_acao: RegistrarAcao,
    ) -> None:
        self._usuarios = usuarios
        self._empresas = empresas
        self._vinculos = vinculos
        self._permissoes = permissoes
        self._registrar_acao = registrar_acao

    def executar(
        self, *, solicitante: UsuarioAutenticado, empresa_id: UUID, nome: str, email: str
    ) -> UsuarioDaEmpresa:
        self._permissoes.exigir_administrador_da_empresa(solicitante, empresa_id)
        empresa = self._empresas.obter(empresa_id)
        if empresa.situacao is SituacaoDaEmpresa.DESATIVADA:
            raise EmpresaDesativadaNaoAceitaVinculo(f"a empresa {empresa.id} está desativada")
        autor = Autor.usuario(solicitante.id)
        usuario = self._usuarios.obter_por_email(Email.criar(email))
        if usuario is not None and self._vinculos.existe(usuario.id, empresa.id):
            raise VinculoJaExiste(f"{usuario.email.valor} já está na empresa")
        if usuario is None:
            usuario = self._cadastrar(nome=nome, email=email, autor=autor)
        vinculo = Vinculo.criar(usuario_id=usuario.id, empresa_id=empresa.id)
        self._vinculos.adicionar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=autor,
            tipo_de_acao=TipoDeAcao.USUARIO_VINCULADO,
            vinculo=vinculo,
        )
        return UsuarioDaEmpresa(usuario=usuario, vinculo=vinculo)

    def _cadastrar(self, *, nome: str, email: str, autor: Autor) -> Usuario:
        usuario = Usuario.cadastrar(nome=nome, email=Email.criar(email))
        self._usuarios.adicionar(usuario)
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=autor,
            tipo_de_acao=TipoDeAcao.USUARIO_CADASTRADO,
            usuario_id=usuario.id,
        )
        return usuario
