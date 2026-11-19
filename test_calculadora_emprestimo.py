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


class TestCalculoMulta:
    """Testes unitários para o RF02: Cálculo de Multa por Atraso."""

    # -------------------------------------------------------------------------
    # Faixa 1: Isenção de 0 a 3 dias (Tolerância R$ 0,00)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("dias", [0, 1, 2, 3])
    def test_deve_isentar_multa_quando_atraso_for_de_zero_a_tres_dias(self, dias):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.GRADUACAO

        # Act
        multa = calculadora.calcular_multa(dias, perfil)

        # Assert
        assert multa == 0.0

    # -------------------------------------------------------------------------
    # Faixa 2: Cobrança linear de 4 a 10 dias (R$ 2,50 por dia)
    # -------------------------------------------------------------------------
    def test_deve_cobrar_dois_reais_e_cinquenta_por_dia_no_limite_inicial_de_4_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.GRADUACAO
        dias = 4  # 4 * 2.50 = 10.00

        # Act
        multa = calculadora.calcular_multa(dias, perfil)

        # Assert
        assert multa == 10.00

    def test_deve_cobrar_vinte_e_cinco_reais_no_limite_superior_de_10_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.GRADUACAO
        dias = 10  # 10 * 2.50 = 25.00

        # Act
        multa = calculadora.calcular_multa(dias, perfil)

        # Assert
        assert multa == 25.00

    # -------------------------------------------------------------------------
    # Faixa 3: Cobrança acima de 10 dias (R$ 25,00 + R$ 5,00/dia adicional)
    # -------------------------------------------------------------------------
    def test_deve_cobrar_adicional_de_cinco_reais_no_limite_de_11_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.POS_GRADUACAO
        dias = 11  # 25.00 + (1 * 5.00) = 30.00

        # Act
        multa = calculadora.calcular_multa(dias, perfil)

        # Assert
        assert multa == 30.00

    # -------------------------------------------------------------------------
    # Teto Máximo: Limite de R$ 150,00 (fronteiras críticas no 35º e 36º dia)
    # -------------------------------------------------------------------------
    def test_deve_atingir_exatamente_teto_maximo_no_limite_de_35_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.PROFESSOR
        dias = 35  # 25.00 + (25 * 5.00) = 150.00

        # Act
        multa = calculadora.calcular_multa(dias, perfil)

        # Assert
        assert multa == 150.00

    def test_deve_limitar_ao_teto_maximo_de_150_reais_quando_ultrapassar_35_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.PROFESSOR
        dias = 36  # Calculado daria 155.00, deve limitar a 150.00

        # Act
        multa = calculadora.calcular_multa(dias, perfil)

        # Assert
        assert multa == 150.00

    def test_deve_limitar_ao_teto_mesmo_com_atraso_longo_de_100_dias(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()
        perfil = PerfilUsuario.GRADUACAO
        dias = 100

        # Act
        multa = calculadora.calcular_multa(dias, perfil)

        # Assert
        assert multa == 150.00

    # -------------------------------------------------------------------------
    # Validações de Entradas Inválidas no RF02
    # -------------------------------------------------------------------------
    def test_deve_lancar_erro_quando_dias_de_atraso_forem_negativos(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()

        # Act & Assert
        with pytest.raises(ValueError):
            calculadora.calcular_multa(-1, PerfilUsuario.GRADUACAO)

    def test_deve_lancar_erro_quando_perfil_for_nulo_no_calculo_de_multa(self):
        # Arrange
        calculadora = CalculadoraEmprestimo()

        # Act & Assert
        with pytest.raises(ValueError):
            calculadora.calcular_multa(5, None)  # type: ignore
