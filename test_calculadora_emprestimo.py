import pytest
from calculadora_emprestimo import (
    CalculadoraEmprestimo,
    PerfilUsuario,
    RegraNegocioException,
)


class TestElegibilidadeEmprestimo:
    """Testes unitários para o RF01: Elegibilidade e Prazo de Empréstimo."""

    # -------------------------------------------------------------------------
    # Testes de Casos Válidos por Perfil (Limites e Prazos)
    # -------------------------------------------------------------------------
    def test_deve_aprovar_emprestimo_graduacao_no_limite_com_prazo_15_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.GRADUACAO
        livros_atuais = 1
        livros_pedidos = 2
        pendencias = False

        # Act
        resultado = calculadora.validar_emprestimo(
            perfil, livros_atuais, livros_pedidos, pendencias
        )

        # Assert
        assert resultado.aprovado is True
        assert resultado.prazo_dias == 15
        assert resultado.limite_maximo == 3

    def test_deve_aprovar_emprestimo_pos_graduacao_com_prazo_30_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.POS_GRADUACAO
        livros_atuais = 2
        livros_pedidos = 3
        pendencias = False

        # Act
        resultado = calculadora.validar_emprestimo(
            perfil, livros_atuais, livros_pedidos, pendencias
        )

        # Assert
        assert resultado.aprovado is True
        assert resultado.prazo_dias == 30
        assert resultado.limite_maximo == 5

    def test_deve_aprovar_emprestimo_professor_com_prazo_45_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.PROFESSOR
        livros_atuais = 5
        livros_pedidos = 5
        pendencias = False

        # Act
        resultado = calculadora.validar_emprestimo(
            perfil, livros_atuais, livros_pedidos, pendencias
        )

        # Assert
        assert resultado.aprovado is True
        assert resultado.prazo_dias == 45
        assert resultado.limite_maximo == 10

    # -------------------------------------------------------------------------
    # Testes de Bloqueios de Regra de Negócio
    # -------------------------------------------------------------------------
    def test_deve_bloquear_emprestimo_quando_usuario_possui_pendencia(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.GRADUACAO
        livros_atuais = 0
        livros_pedidos = 1
        pendencias = True

        # Act & Assert
        with pytest.raises(RegraNegocioException) as exc_info:
            calculadora.validar_emprestimo(
                perfil, livros_atuais, livros_pedidos, pendencias
            )
        assert "pendência" in str(exc_info.value).lower()

    def test_deve_bloquear_quando_quantidade_solicitada_ultrapassa_limite(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.GRADUACAO
        livros_atuais = 2
        livros_pedidos = 2  # Total: 4, limite é 3
        pendencias = False

        # Act & Assert
        with pytest.raises(RegraNegocioException) as exc_info:
            calculadora.validar_emprestimo(
                perfil, livros_atuais, livros_pedidos, pendencias
            )
        assert "limite" in str(exc_info.value).lower()

    # -------------------------------------------------------------------------
    # Testes de Entradas Inválidas (Valores Negativos e Perfil Nulo)
    # -------------------------------------------------------------------------
    def test_deve_lancar_erro_quando_perfil_for_invalido_ou_nulo(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()

        # Act & Assert
        with pytest.raises(ValueError):
            calculadora.validar_emprestimo(
                None, 0, 1, False  # type: ignore
            )

    def test_deve_lancar_erro_quando_livros_emprestados_forem_negativos(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()

        # Act & Assert
        with pytest.raises(ValueError):
            calculadora.validar_emprestimo(
                PerfilUsuario.GRADUACAO, -1, 1, False
            )

    def test_deve_lancar_erro_quando_livros_solicitados_forem_menor_ou_igual_a_zero(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()

        # Act & Assert
        with pytest.raises(ValueError):
            calculadora.validar_emprestimo(
                PerfilUsuario.GRADUACAO, 0, 0, False
            )
