from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_vinculo
from assura.identidade.aplicacao.portas import Empresas, Usuarios, Vinculos
from assura.identidade.dominio.empresa import SituacaoDaEmpresa
from assura.identidade.dominio.erros import EmpresaDesativadaNaoAceitaVinculo, VinculoJaExiste
from assura.identidade.dominio.vinculo import Vinculo


class VincularUsuario:
    def __init__(
        self,
        usuarios: Usuarios,
        empresas: Empresas,
        vinculos: Vinculos,
        registrar_acao: RegistrarAcao,
    ) -> None:
        self._usuarios = usuarios
        self._empresas = empresas
        self._vinculos = vinculos
        self._registrar_acao = registrar_acao

    def executar(self, *, autor: Autor, usuario_id: UUID, empresa_id: UUID) -> Vinculo:
        usuario = self._usuarios.obter(usuario_id)
        empresa = self._empresas.obter(empresa_id)
        if empresa.situacao is SituacaoDaEmpresa.DESATIVADA:
            raise EmpresaDesativadaNaoAceitaVinculo(f"a empresa {empresa.id} está desativada")
        if self._vinculos.existe(usuario.id, empresa.id):
            raise VinculoJaExiste(
                f"o usuário {usuario.id} já tem vínculo com a empresa {empresa.id}"
            )
        vinculo = Vinculo.criar(usuario_id=usuario.id, empresa_id=empresa.id)
        self._vinculos.adicionar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=autor,
            tipo_de_acao=TipoDeAcao.USUARIO_VINCULADO,
            vinculo=vinculo,
        )
        return vinculo
