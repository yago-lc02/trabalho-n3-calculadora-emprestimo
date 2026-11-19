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

    # Constantes financeiras de multas
    DIAS_TOLERANCIA_ISENCAO: int = 3
    LIMITE_DIAS_FAIXA_PADRAO: int = 10
    VALOR_DIARIA_PADRAO: float = 2.50
    VALOR_DIARIA_EXCEDENTE: float = 5.00
    TETO_MAXIMO_MULTA: float = 150.00

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
        # Validação de perfil válido
        if not isinstance(perfil, PerfilUsuario):
            raise ValueError("Perfil de usuário inválido ou nulo.")

        # Validação de dias de atraso
        if not isinstance(dias_atraso, int) or dias_atraso < 0:
            raise ValueError("A quantidade de dias de atraso deve ser um inteiro não-negativo.")

        # 0 a 3 dias de atraso: tolerância total
        if dias_atraso <= self.DIAS_TOLERANCIA_ISENCAO:
            return 0.0

        # 4 a 10 dias de atraso: R$ 2,50/dia desde o 1º dia
        if dias_atraso <= self.LIMITE_DIAS_FAIXA_PADRAO:
            multa_calculada = dias_atraso * self.VALOR_DIARIA_PADRAO
        else:
            # Acima de 10 dias: 10 primeiros dias a R$ 2,50 + R$ 5,00 por dia excedente
            dias_excedentes = dias_atraso - self.LIMITE_DIAS_FAIXA_PADRAO
            multa_calculada = (
                (self.LIMITE_DIAS_FAIXA_PADRAO * self.VALOR_DIARIA_PADRAO) +
                (dias_excedentes * self.VALOR_DIARIA_EXCEDENTE)
            )

        # Aplicação do teto máximo de R$ 150,00
        return min(multa_calculada, self.TETO_MAXIMO_MULTA)
