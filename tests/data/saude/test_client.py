"""Tests for the Saúde HTTP client."""

import httpx
import pytest
import respx

from mcp_brasil.data.saude import client
from mcp_brasil.data.saude.constants import (
    ESTABELECIMENTOS_URL,
    LEITOS_URL,
    PROFISSIONAIS_URL,
    TIPOS_URL,
)
from mcp_brasil.exceptions import HttpClientError

# ---------------------------------------------------------------------------
# buscar_estabelecimentos
# ---------------------------------------------------------------------------


class TestBuscarEstabelecimentos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_establishments(self) -> None:
        respx.get(ESTABELECIMENTOS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "codigo_cnes": "1234567",
                        "nome_fantasia": "UBS Central",
                        "nome_razao_social": "Unidade Básica de Saúde Central",
                        "natureza_organizacao": "Administração Pública",
                        "tipo_gestao": "Municipal",
                        "codigo_tipo_estabelecimento": "01",
                        "descricao_tipo_estabelecimento": "Central de Regulação",
                        "codigo_municipio": "355030",
                        "codigo_uf": "35",
                        "endereco": "Rua ABC, 123",
                    }
                ],
            )
        )
        result = await client.buscar_estabelecimentos(codigo_municipio="355030")
        assert len(result) == 1
        assert result[0].codigo_cnes == "1234567"
        assert result[0].nome_fantasia == "UBS Central"
        assert result[0].codigo_municipio == "355030"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(ESTABELECIMENTOS_URL).mock(return_value=httpx.Response(200, json=[]))
        result = await client.buscar_estabelecimentos()
        assert result == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_sends_query_params(self) -> None:
        route = respx.get(ESTABELECIMENTOS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.buscar_estabelecimentos(
            codigo_municipio="355030", codigo_uf="35", status=1, limit=10, offset=5
        )
        req_url = str(route.calls[0].request.url)
        assert "codigo_municipio=355030" in req_url
        assert "codigo_uf=35" in req_url
        assert "status=1" in req_url
        assert "limit=10" in req_url
        assert "offset=5" in req_url

    @pytest.mark.asyncio
    @respx.mock
    async def test_limit_capped_at_max(self) -> None:
        route = respx.get(ESTABELECIMENTOS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.buscar_estabelecimentos(limit=999)
        req_url = str(route.calls[0].request.url)
        assert "limit=100" in req_url


# ---------------------------------------------------------------------------
# buscar_profissionais
# ---------------------------------------------------------------------------


class TestBuscarProfissionais:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_professionals(self) -> None:
        respx.get(PROFISSIONAIS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "codigo_cnes": "1234567",
                        "nome": "João Silva",
                        "cns": "123456789012345",
                        "cbo": "225125",
                        "descricao_cbo": "Médico generalista",
                    }
                ],
            )
        )
        result = await client.buscar_profissionais(cnes="1234567")
        assert len(result) == 1
        assert result[0].nome == "João Silva"
        assert result[0].cbo == "225125"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(PROFISSIONAIS_URL).mock(return_value=httpx.Response(200, json=[]))
        result = await client.buscar_profissionais()
        assert result == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_sends_query_params(self) -> None:
        route = respx.get(PROFISSIONAIS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.buscar_profissionais(
            codigo_municipio="355030", cnes="1234567", limit=10, offset=5
        )
        req_url = str(route.calls[0].request.url)
        assert "codigo_municipio=355030" in req_url
        assert "cnes=1234567" in req_url
        assert "limit=10" in req_url
        assert "offset=5" in req_url


# ---------------------------------------------------------------------------
# listar_tipos_estabelecimento
# ---------------------------------------------------------------------------


class TestListarTiposEstabelecimento:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_types(self) -> None:
        respx.get(TIPOS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "codigo_tipo_estabelecimento": "01",
                        "descricao_tipo_estabelecimento": "Central de Regulação",
                    },
                    {
                        "codigo_tipo_estabelecimento": "02",
                        "descricao_tipo_estabelecimento": "Hospital Geral",
                    },
                ],
            )
        )
        result = await client.listar_tipos_estabelecimento()
        assert len(result) == 2
        assert result[0].codigo == "01"
        assert result[0].descricao == "Central de Regulação"
        assert result[1].codigo == "02"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(TIPOS_URL).mock(return_value=httpx.Response(200, json=[]))
        result = await client.listar_tipos_estabelecimento()
        assert result == []


# ---------------------------------------------------------------------------
# consultar_leitos
# ---------------------------------------------------------------------------


class TestConsultarLeitos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_beds(self) -> None:
        respx.get(LEITOS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "codigo_cnes": "1234567",
                        "tipo_leito": "Cirúrgico",
                        "especialidade": "Cirurgia Geral",
                        "existente": 20,
                        "sus": 15,
                    }
                ],
            )
        )
        result = await client.consultar_leitos(cnes="1234567")
        assert len(result) == 1
        assert result[0].tipo_leito == "Cirúrgico"
        assert result[0].existente == 20
        assert result[0].sus == 15

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(LEITOS_URL).mock(return_value=httpx.Response(200, json=[]))
        result = await client.consultar_leitos()
        assert result == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_sends_query_params(self) -> None:
        route = respx.get(LEITOS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.consultar_leitos(
            codigo_municipio="355030", cnes="1234567", limit=50, offset=10
        )
        req_url = str(route.calls[0].request.url)
        assert "codigo_municipio=355030" in req_url
        assert "cnes=1234567" in req_url
        assert "limit=50" in req_url
        assert "offset=10" in req_url


# ---------------------------------------------------------------------------
# Parse functions
# ---------------------------------------------------------------------------


class TestParseEstabelecimento:
    def test_handles_missing_fields(self) -> None:
        result = client._parse_estabelecimento({})
        assert result.codigo_cnes == ""
        assert result.nome_fantasia is None

    def test_converts_numeric_codes_to_str(self) -> None:
        result = client._parse_estabelecimento(
            {"codigo_cnes": 1234567, "codigo_municipio": 355030, "codigo_uf": 35}
        )
        assert result.codigo_cnes == "1234567"
        assert result.codigo_municipio == "355030"
        assert result.codigo_uf == "35"


class TestParseProfissional:
    def test_handles_missing_fields(self) -> None:
        result = client._parse_profissional({})
        assert result.codigo_cnes == ""
        assert result.nome is None


class TestParseTipo:
    def test_handles_missing_fields(self) -> None:
        result = client._parse_tipo({})
        assert result.codigo == ""
        assert result.descricao is None


class TestParseLeito:
    def test_handles_missing_fields(self) -> None:
        result = client._parse_leito({})
        assert result.codigo_cnes == ""
        assert result.existente is None
        assert result.sus is None


# ---------------------------------------------------------------------------
# buscar_estabelecimento_por_cnes
# ---------------------------------------------------------------------------


class TestBuscarEstabelecimentoPorCnes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_detail(self) -> None:
        respx.get(f"{ESTABELECIMENTOS_URL}/1234567").mock(
            return_value=httpx.Response(
                200,
                json={
                    "codigo_cnes": "1234567",
                    "nome_fantasia": "Hospital São Paulo",
                    "nome_razao_social": "Hospital São Paulo Ltda",
                    "natureza_organizacao": "Administração Pública",
                    "tipo_gestao": "Estadual",
                    "codigo_tipo_estabelecimento": "05",
                    "descricao_tipo_estabelecimento": "Hospital Geral",
                    "codigo_municipio": "355030",
                    "codigo_uf": "35",
                    "endereco": "Rua Napoleão de Barros, 715",
                    "bairro": "Vila Clementino",
                    "cep": "04024-002",
                    "telefone": "(11) 5576-4000",
                    "latitude": -23.5989,
                    "longitude": -46.6423,
                    "cnpj": "12.345.678/0001-90",
                    "data_atualizacao": "2024-01-15",
                },
            )
        )
        result = await client.buscar_estabelecimento_por_cnes("1234567")
        assert result is not None
        assert result.codigo_cnes == "1234567"
        assert result.nome_fantasia == "Hospital São Paulo"
        assert result.telefone == "(11) 5576-4000"
        assert result.latitude == -23.5989

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_none_for_empty(self) -> None:
        respx.get(f"{ESTABELECIMENTOS_URL}/0000000").mock(
            return_value=httpx.Response(200, json={})
        )
        result = await client.buscar_estabelecimento_por_cnes("0000000")
        assert result is None


# ---------------------------------------------------------------------------
# buscar_estabelecimentos_por_tipo
# ---------------------------------------------------------------------------


class TestBuscarEstabelecimentosPorTipo:
    @pytest.mark.asyncio
    @respx.mock
    async def test_sends_tipo_param(self) -> None:
        route = respx.get(ESTABELECIMENTOS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.buscar_estabelecimentos_por_tipo(
            codigo_tipo="73",
            codigo_municipio="355030",
        )
        req_url = str(route.calls[0].request.url)
        assert "codigo_tipo_estabelecimento=73" in req_url
        assert "codigo_municipio=355030" in req_url
        assert "status=1" in req_url

    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_list(self) -> None:
        respx.get(ESTABELECIMENTOS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "codigo_cnes": "9876543",
                        "nome_fantasia": "UPA 24h",
                        "codigo_tipo_estabelecimento": "73",
                        "descricao_tipo_estabelecimento": "Pronto Atendimento",
                        "codigo_municipio": "220040",
                        "codigo_uf": "22",
                    }
                ],
            )
        )
        result = await client.buscar_estabelecimentos_por_tipo(codigo_tipo="73")
        assert len(result) == 1
        assert result[0].codigo_cnes == "9876543"
        assert result[0].descricao_tipo == "Pronto Atendimento"


# ---------------------------------------------------------------------------
# Parse detail function
# ---------------------------------------------------------------------------


class TestParseEstabelecimentoDetalhe:
    def test_handles_missing_fields(self) -> None:
        result = client._parse_estabelecimento_detalhe({})
        assert result.codigo_cnes == ""
        assert result.telefone is None
        assert result.latitude is None

    def test_parses_all_fields(self) -> None:
        result = client._parse_estabelecimento_detalhe(
            {
                "codigo_cnes": 1234567,
                "nome_fantasia": "Hospital X",
                "bairro": "Centro",
                "cep": "01000-000",
                "telefone": "1199999999",
                "latitude": -23.55,
                "longitude": -46.63,
                "cnpj": "12345678000190",
                "data_atualizacao": "2024-06-01",
            }
        )
        assert result.codigo_cnes == "1234567"
        assert result.bairro == "Centro"
        assert result.latitude == -23.55


# ---------------------------------------------------------------------------
# Malformed API responses (type validation)
# ---------------------------------------------------------------------------


class TestMalformedResponses:
    """Test that client functions raise HttpClientError on unexpected response types."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_estabelecimentos_string_response(self) -> None:
        respx.get(ESTABELECIMENTOS_URL).mock(
            return_value=httpx.Response(200, json="Service Unavailable")
        )
        with pytest.raises(HttpClientError, match="expected list"):
            await client.buscar_estabelecimentos()

    @pytest.mark.asyncio
    @respx.mock
    async def test_estabelecimentos_dict_response(self) -> None:
        respx.get(ESTABELECIMENTOS_URL).mock(
            return_value=httpx.Response(200, json={"error": "not found"})
        )
        with pytest.raises(HttpClientError, match="expected list"):
            await client.buscar_estabelecimentos()

    @pytest.mark.asyncio
    @respx.mock
    async def test_leitos_string_response(self) -> None:
        respx.get(LEITOS_URL).mock(return_value=httpx.Response(200, json="404 Not Found"))
        with pytest.raises(HttpClientError, match="expected list"):
            await client.consultar_leitos()

    @pytest.mark.asyncio
    @respx.mock
    async def test_profissionais_string_response(self) -> None:
        respx.get(PROFISSIONAIS_URL).mock(return_value=httpx.Response(200, json="error"))
        with pytest.raises(HttpClientError, match="expected list"):
            await client.buscar_profissionais()

    @pytest.mark.asyncio
    @respx.mock
    async def test_tipos_string_response(self) -> None:
        respx.get(TIPOS_URL).mock(return_value=httpx.Response(200, json="error"))
        with pytest.raises(HttpClientError, match="expected list"):
            await client.listar_tipos_estabelecimento()

    @pytest.mark.asyncio
    @respx.mock
    async def test_estabelecimento_por_cnes_string_response(self) -> None:
        respx.get(f"{ESTABELECIMENTOS_URL}/1234567").mock(
            return_value=httpx.Response(200, json="not found")
        )
        with pytest.raises(HttpClientError, match="expected dict"):
            await client.buscar_estabelecimento_por_cnes("1234567")
