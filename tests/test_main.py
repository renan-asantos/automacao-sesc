import pytest
from freezegun import freeze_time
from src.main import main

HTML_COM_BANNER = """
<html>
    <body>
        <p>
            <b>
                <font color="black">COMUNICADO
            </font></b><font color="black"><br>
            <b>As inscrições para hospedagem em dezembro de 2026 estarão liberadas de 27 de agosto até 30 de agosto, às
            23h.*.&nbsp;<br>
            O resultado do sorteio será divulgado em 01 de setembro, a partir das 14h*.&nbsp;<br>
            O prazo para pagamento da inscrição atendida finaliza em 03 de setembro, às 23h*.&nbsp;<br>
                * horário de Brasília Valores sujeitos a alteração. </b><br>
            <i>Havendo necessidade técnica ou operacional, as datas e os horários poderão ser alterados.</i> <br>
            </font>
        </p>
    </body>
</html>
"""

HTML_SEM_BANNER = """
<html>
    <body>
        <p>Outro conteúdo qualquer</p>
    </body>
</html>
"""

@pytest.fixture
def mock_resposta_sucesso(mocker):
    """Fixture que mocka uma resposta HTTP de sucesso."""
    def _mock(html_content: str = HTML_COM_BANNER):
        mock_response = mocker.MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = mocker.MagicMock()
        return mock_response
    return _mock


@pytest.fixture
def mock_httpx_client(mocker, mock_resposta_sucesso):
    """
    Fixture que mocka o httpx2.Client com uma resposta de sucesso.
    Por padrão usa HTML_COM_BANNER, mas pode ser sobrescrita.
    """
    def _mock_httpx(html_content: str = HTML_COM_BANNER):
        mock_response = mock_resposta_sucesso(html_content)

        mock_client = mocker.MagicMock()
        mock_client.get.return_value = mock_response

        mock_client_instance = mocker.MagicMock()
        mock_client_instance.__enter__.return_value = mock_client
        mock_client_instance.__exit__ = mocker.MagicMock()

        mocker.patch('main.httpx2.Client', return_value=mock_client_instance)

    return _mock_httpx


@freeze_time("2026-08-20 00:00:00", tz_offset=-3)
def test_main_7_dias_antes(mock_httpx_client, capsys):
    mock_httpx_client(HTML_COM_BANNER)
    main()
    captured = capsys.readouterr()
    assert "VAI ABRIR LOGO EM! Faltam 7 dias" in captured.out


@freeze_time("2026-08-25 00:00:00", tz_offset=-3)
def test_main_2_dias_antes(mock_httpx_client, capsys):
    mock_httpx_client(HTML_COM_BANNER)
    main()
    captured = capsys.readouterr()
    assert "VAI ABRIR LOGO EM! Faltam 2 dias" in captured.out


@freeze_time("2026-08-31 00:00:00", tz_offset=-3)
def test_main_inscricoes_passaram(mock_httpx_client, capsys):
    mock_httpx_client(HTML_COM_BANNER)
    main()
    captured = capsys.readouterr()
    assert "Já passou as inscrições" in captured.out


@freeze_time("2026-08-27 00:00:00", tz_offset=-3)
def test_main_dia_da_abertura(mock_httpx_client, capsys):
    """No dia da abertura, deve mostrar 'Faltam 0 dias'."""
    mock_httpx_client(HTML_COM_BANNER)
    main()
    captured = capsys.readouterr()
    assert "Faltam 0 dias" in captured.out


@freeze_time("2026-08-20 00:00:00", tz_offset=-3)
def test_main_exibe_comunicado_corretamente(mock_httpx_client, capsys):
    """Verifica se o comunicado é exibido corretamente."""
    mock_httpx_client(HTML_COM_BANNER)
    main()
    captured = capsys.readouterr()
    assert "COMUNICADO" in captured.out
    assert "dezembro de 2026" in captured.out
    assert "27 de agosto" in captured.out
    assert "30 de agosto" in captured.out


@freeze_time("2026-08-20 00:00:00", tz_offset=-3)
def test_main_sem_banner(mock_httpx_client, capsys):
    """Quando o banner COMUNICADO não é encontrado."""
    mock_httpx_client(HTML_SEM_BANNER)
    main()
    captured = capsys.readouterr()
    assert "⚠️ Não encontrei o banner COMUNICADO na estrutura esperada." in captured.out