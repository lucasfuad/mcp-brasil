"""Tests for the TCU tool functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_brasil.data.tcu import tools
from mcp_brasil.data.tcu.schemas import (
    Acordao,
    CertidaoConsolidada,
    CertidaoItem,
    Inabilitado,
    Inidoneo,
    PedidoCongresso,
)

CLIENT_MODULE = "mcp_brasil.data.tcu.client"


def _mock_ctx() -> MagicMock:
    """Create a mock Context with async log methods."""
    ctx = MagicMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    return ctx


class TestConsultarAcordaos:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Acordao(
                key="ACORDAO-COMPLETO-123",
                tipo="ACORDAO",
                anoAcordao="2026",
                titulo="ACORDAO 100/2026 ATA 1/2026 - PLENARIO",
                numeroAcordao="100",
                numeroAta="1/2026",
                colegiado="Plenário",
                dataSessao="18/03/2026",
                relator="BRUNO DANTAS",
                situacao="OFICIALIZADO",
                sumario="EMBARGOS DE DECLARAÇÃO",
                urlAcordao="https://contas.tcu.gov.br/...",
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_acordaos",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_acordaos(ctx)
        assert "100" in result
        assert "2026" in result
        assert "Plenário" in result
        assert "BRUNO DANTAS" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_acordaos",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.consultar_acordaos(ctx)
        assert "Nenhum acórdão" in result

    @pytest.mark.asyncio
    async def test_truncates_long_sumario(self) -> None:
        mock_data = [
            Acordao(
                key="ACORDAO-COMPLETO-456",
                anoAcordao="2026",
                numeroAcordao="200",
                numeroAta="2/2026",
                colegiado="1ª Câmara",
                dataSessao="19/03/2026",
                relator="ANA ARRAES",
                sumario="A" * 200,
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_acordaos",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_acordaos(ctx)
        assert "..." in result


class TestConsultarInabilitados:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Inabilitado(
                nome="FULANO DA SILVA",
                cpf="123.456.789-00",
                processo="026.615/2020-7",
                deliberacao="AC-000738/2022-PL",
                data_transito_julgado="2022-07-16T03:00:00Z",
                data_final="2027-07-16T03:00:00Z",
                data_acordao="2022-04-06T17:30:00Z",
                uf="MA",
                municipio="SANTA INES",
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_inabilitados",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_inabilitados(ctx)
        assert "FULANO DA SILVA" in result
        assert "123.456.789-00" in result
        assert "MA" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_inabilitados",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.consultar_inabilitados(ctx)
        assert "Nenhum inabilitado" in result

    @pytest.mark.asyncio
    async def test_with_cpf(self) -> None:
        mock_data = [
            Inabilitado(
                nome="BELTRANO",
                cpf="999.888.777-66",
                processo="001.000/2023-1",
                deliberacao="AC-001000/2023-PL",
                data_transito_julgado="2023-01-01T00:00:00Z",
                data_final="2028-01-01T00:00:00Z",
                data_acordao="2023-01-01T00:00:00Z",
                uf="SP",
                municipio="SAO PAULO",
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_inabilitados",
            new_callable=AsyncMock,
            return_value=mock_data,
        ) as mock_client:
            result = await tools.consultar_inabilitados(ctx, cpf="99988877766")
        mock_client.assert_called_once_with(cpf="99988877766", offset=0, limit=25)
        assert "BELTRANO" in result


class TestConsultarInidoneos:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Inidoneo(
                nome="EMPRESA LTDA",
                cpf_cnpj="07.405.573/0001-44",
                processo="007.720/2012-2",
                deliberacao="AC-002099/2015-PL",
                data_transito_julgado="2021-09-30T03:00:00Z",
                data_final="2026-09-30T03:00:00Z",
                data_acordao="2015-08-19T17:30:00Z",
                uf="DF",
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_inidoneos",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_inidoneos(ctx)
        assert "EMPRESA LTDA" in result
        assert "07.405.573/0001-44" in result
        assert "DF" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_inidoneos",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.consultar_inidoneos(ctx)
        assert "Nenhum licitante inidôneo" in result


class TestConsultarCertidoes:
    @pytest.mark.asyncio
    async def test_formats_result(self) -> None:
        mock_data = CertidaoConsolidada(
            razaoSocial="Banco do Brasil S.A.",
            nomeFantasia="BB",
            cnpj="00.000.000/0001-91",
            certidoes=[
                CertidaoItem(
                    emissor="TCU",
                    tipo="Inidoneos",
                    descricao="Licitantes Inidôneos",
                    situacao="NADA_CONSTA",
                    dataHoraEmissao="22/03/2026 23:14",
                ),
                CertidaoItem(
                    emissor="CNJ",
                    tipo="CNIA",
                    descricao="CNIA",
                    situacao="NADA_CONSTA",
                    dataHoraEmissao="22/03/2026 23:14",
                ),
            ],
            seCnpjEncontradoNaBaseTcu=True,
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_certidoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_certidoes(ctx, cnpj="00000000000191")
        assert "Banco do Brasil" in result
        assert "NADA_CONSTA" in result
        assert "TCU" in result
        assert "CNJ" in result

    @pytest.mark.asyncio
    async def test_empty_certidoes(self) -> None:
        mock_data = CertidaoConsolidada(
            razaoSocial="Empresa X",
            nomeFantasia="",
            cnpj="11.111.111/0001-11",
            certidoes=[],
            seCnpjEncontradoNaBaseTcu=False,
        )
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_certidoes",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_certidoes(ctx, cnpj="11111111000111")
        assert "Nenhuma certidão" in result


class TestConsultarPedidosCongresso:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            PedidoCongresso(
                tipo="REQ",
                numero=4,
                data_aprovacao="2026-02-19T03:00:00Z",
                assunto="Informações sobre obras ferroviárias",
                autor="Dr. Hiran",
                processo_scn="004.808/2026-6",
                link_proposicao="https://senado.leg.br/...",
            ),
        ]
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_pedidos_congresso",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_pedidos_congresso(ctx)
        assert "REQ" in result
        assert "Dr. Hiran" in result
        assert "004.808/2026-6" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        ctx = _mock_ctx()
        with patch(
            f"{CLIENT_MODULE}.consultar_pedidos_congresso",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.consultar_pedidos_congresso(ctx)
        assert "Nenhum pedido" in result
