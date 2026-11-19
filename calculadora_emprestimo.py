from enum import Enum
from dataclasses import dataclass


class PerfilUsuario(Enum):
    GRADUACAO = "GRADUACAO"
    POS_GRADUACAO = "POS_GRADUACAO"
    PROFESSOR = "PROFESSOR"


class RegraNegocioException(Exception):
    """Exceção levantada quando uma regra de negócio da biblioteca é violada."""
    pass


@dataclass(frozen=True)
class ResultadoEmprestimo:
    aprovado: bool
    prazo_dias: int
    limite_maximo: int


class CalculadoraEmprestimo:
    def validar_emprestimo(
        self,
        perfil: PerfilUsuario,
        livros_emprestados: int,
        livros_solicitados: int,
        possui_pendencias: bool
    ) -> ResultadoEmprestimo:
        raise NotImplementedError("Método ainda não implementado no ciclo TDD")

    def calcular_multa(
        self,
        dias_atraso: int,
        perfil: PerfilUsuario
    ) -> float:
        raise NotImplementedError("Método ainda não implementado no ciclo TDD")
