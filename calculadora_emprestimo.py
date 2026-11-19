from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple


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
    # Mapeamento de regras por perfil: (limite_maximo, prazo_devolucao_dias)
    REGRAS_PERFIL: Dict[PerfilUsuario, Tuple[int, int]] = {
        PerfilUsuario.GRADUACAO: (3, 15),
        PerfilUsuario.POS_GRADUACAO: (5, 30),
        PerfilUsuario.PROFESSOR: (10, 45),
    }

    def validar_emprestimo(
        self,
        perfil: PerfilUsuario,
        livros_emprestados: int,
        livros_solicitados: int,
        possui_pendencias: bool
    ) -> ResultadoEmprestimo:
        # Validação de perfil válido
        if not isinstance(perfil, PerfilUsuario):
            raise ValueError("Perfil de usuário inválido ou nulo.")

        # Validação de quantidades de livros
        if not isinstance(livros_emprestados, int) or livros_emprestados < 0:
            raise ValueError("A quantidade de livros emprestados deve ser um inteiro não-negativo.")

        if not isinstance(livros_solicitados, int) or livros_solicitados <= 0:
            raise ValueError("A quantidade de livros solicitados deve ser maior que zero.")

        # Bloqueio por pendência financeira ou atraso anterior
        if possui_pendencias:
            raise RegraNegocioException("Empréstimo recusado: usuário possui pendência financeira ou atraso ativo.")

        limite_max, prazo_dias = self.REGRAS_PERFIL[perfil]
        total_livros = livros_emprestados + livros_solicitados

        # Bloqueio por estouro de limite da categoria
        if total_livros > limite_max:
            raise RegraNegocioException(
                f"Empréstimo recusado: a quantidade solicitada ultrapassa o limite máximo de {limite_max} livros para {perfil.value}."
            )

        return ResultadoEmprestimo(
            aprovado=True,
            prazo_dias=prazo_dias,
            limite_maximo=limite_max
        )

    def calcular_multa(
        self,
        dias_atraso: int,
        perfil: PerfilUsuario
    ) -> float:
        raise NotImplementedError("Método ainda não implementado no ciclo TDD")
