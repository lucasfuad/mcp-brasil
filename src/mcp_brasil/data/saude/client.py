"""HTTP client for the CNES/DataSUS API.

Endpoints:
    - /estabelecimentos          → buscar_estabelecimentos
    - /estabelecimentos/{cnes}   → buscar_estabelecimento_por_cnes
    - /profissionais             → buscar_profissionais
    - /tipodeestabelecimento     → listar_tipos_estabelecimento
    - /leitos                    → consultar_leitos
"""

from __future__ import annotations

from typing import Any

from mcp_brasil._shared.http_client import http_get
from mcp_brasil.exceptions import HttpClientError

from .constants import (
    DEFAULT_LIMIT,
    ESTABELECIMENTOS_URL,
    LEITOS_URL,
    MAX_LIMIT,
    PROFISSIONAIS_URL,
    TIPOS_URL,
)
from .schemas import (
    Estabelecimento,
    EstabelecimentoDetalhe,
    Leito,
    Profissional,
    TipoEstabelecimento,
)


def _ensure_list(data: Any, url: str) -> list[dict[str, Any]]:
    """Validate that API response is a list of dicts.

    The DataSUS API sometimes returns a JSON string or dict on errors
    instead of the expected list, causing 'str' has no attribute 'get'.
    """
    if isinstance(data, list):
        return data
    raise HttpClientError(
        f"Unexpected response from {url}: expected list, got {type(data).__name__}"
    )


def _ensure_dict(data: Any, url: str) -> dict[str, Any]:
    """Validate that API response is a dict."""
    if isinstance(data, dict):
        return data
    raise HttpClientError(
        f"Unexpected response from {url}: expected dict, got {type(data).__name__}"
    )


def _parse_estabelecimento(raw: dict[str, Any]) -> Estabelecimento:
    """Parse a raw establishment dict into an Estabelecimento model."""
    return Estabelecimento(
        codigo_cnes=str(raw.get("codigo_cnes", "") or ""),
        nome_fantasia=raw.get("nome_fantasia"),
        nome_razao_social=raw.get("nome_razao_social"),
        natureza_organizacao=raw.get("natureza_organizacao"),
        tipo_gestao=raw.get("tipo_gestao"),
        codigo_tipo=str(raw.get("codigo_tipo_estabelecimento", "") or ""),
        descricao_tipo=raw.get("descricao_tipo_estabelecimento"),
        codigo_municipio=str(raw.get("codigo_municipio", "") or ""),
        codigo_uf=str(raw.get("codigo_uf", "") or ""),
        endereco=raw.get("endereco"),
    )


def _parse_profissional(raw: dict[str, Any]) -> Profissional:
    """Parse a raw professional dict into a Profissional model."""
    return Profissional(
        codigo_cnes=str(raw.get("codigo_cnes", "") or ""),
        nome=raw.get("nome"),
        cns=raw.get("cns"),
        cbo=raw.get("cbo"),
        descricao_cbo=raw.get("descricao_cbo"),
    )


def _parse_tipo(raw: dict[str, Any]) -> TipoEstabelecimento:
    """Parse a raw type dict into a TipoEstabelecimento model."""
    return TipoEstabelecimento(
        codigo=str(raw.get("codigo_tipo_estabelecimento", "") or ""),
        descricao=raw.get("descricao_tipo_estabelecimento"),
    )


def _parse_leito(raw: dict[str, Any]) -> Leito:
    """Parse a raw bed dict into a Leito model."""
    return Leito(
        codigo_cnes=str(raw.get("codigo_cnes", "") or ""),
        tipo_leito=raw.get("tipo_leito"),
        especialidade=raw.get("especialidade"),
        existente=raw.get("existente"),
        sus=raw.get("sus"),
    )


async def buscar_estabelecimentos(
    *,
    codigo_municipio: str | None = None,
    codigo_uf: str | None = None,
    status: int | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[Estabelecimento]:
    """Search health establishments from CNES.

    API: GET /estabelecimentos

    Args:
        codigo_municipio: IBGE municipality code (e.g. "355030").
        codigo_uf: IBGE state code (e.g. "35").
        status: 1 for active, 0 for inactive.
        limit: Max results per page.
        offset: Pagination offset.
    """
    params: dict[str, Any] = {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
    }
    if codigo_municipio:
        params["codigo_municipio"] = codigo_municipio
    if codigo_uf:
        params["codigo_uf"] = codigo_uf
    if status is not None:
        params["status"] = status

    raw = await http_get(ESTABELECIMENTOS_URL, params=params)
    data = _ensure_list(raw, ESTABELECIMENTOS_URL)
    return [_parse_estabelecimento(item) for item in data]


async def buscar_profissionais(
    *,
    codigo_municipio: str | None = None,
    cnes: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[Profissional]:
    """Search health professionals from CNES.

    API: GET /profissionais

    Args:
        codigo_municipio: IBGE municipality code.
        cnes: CNES establishment code.
        limit: Max results per page.
        offset: Pagination offset.
    """
    params: dict[str, Any] = {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
    }
    if codigo_municipio:
        params["codigo_municipio"] = codigo_municipio
    if cnes:
        params["cnes"] = cnes

    raw = await http_get(PROFISSIONAIS_URL, params=params)
    data = _ensure_list(raw, PROFISSIONAIS_URL)
    return [_parse_profissional(item) for item in data]


async def listar_tipos_estabelecimento() -> list[TipoEstabelecimento]:
    """Fetch all establishment types from CNES.

    API: GET /tipodeestabelecimento
    """
    raw = await http_get(TIPOS_URL)
    data = _ensure_list(raw, TIPOS_URL)
    return [_parse_tipo(item) for item in data]


async def consultar_leitos(
    *,
    codigo_municipio: str | None = None,
    cnes: str | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[Leito]:
    """Search hospital beds from CNES.

    API: GET /leitos

    Args:
        codigo_municipio: IBGE municipality code.
        cnes: CNES establishment code.
        limit: Max results per page.
        offset: Pagination offset.
    """
    params: dict[str, Any] = {
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
    }
    if codigo_municipio:
        params["codigo_municipio"] = codigo_municipio
    if cnes:
        params["cnes"] = cnes

    raw = await http_get(LEITOS_URL, params=params)
    data = _ensure_list(raw, LEITOS_URL)
    return [_parse_leito(item) for item in data]


def _parse_estabelecimento_detalhe(raw: dict[str, Any]) -> EstabelecimentoDetalhe:
    """Parse a raw establishment dict into an EstabelecimentoDetalhe model."""
    return EstabelecimentoDetalhe(
        codigo_cnes=str(raw.get("codigo_cnes", "") or ""),
        nome_fantasia=raw.get("nome_fantasia"),
        nome_razao_social=raw.get("nome_razao_social"),
        natureza_organizacao=raw.get("natureza_organizacao"),
        tipo_gestao=raw.get("tipo_gestao"),
        codigo_tipo=str(raw.get("codigo_tipo_estabelecimento", "") or ""),
        descricao_tipo=raw.get("descricao_tipo_estabelecimento"),
        codigo_municipio=str(raw.get("codigo_municipio", "") or ""),
        codigo_uf=str(raw.get("codigo_uf", "") or ""),
        endereco=raw.get("endereco"),
        bairro=raw.get("bairro"),
        cep=raw.get("cep"),
        telefone=raw.get("telefone"),
        latitude=raw.get("latitude"),
        longitude=raw.get("longitude"),
        cnpj=raw.get("cnpj"),
        data_atualizacao=raw.get("data_atualizacao"),
    )


async def buscar_estabelecimento_por_cnes(cnes: str) -> EstabelecimentoDetalhe | None:
    """Fetch a single establishment by its CNES code.

    API: GET /estabelecimentos/{cnes}

    Args:
        cnes: CNES code (7 digits).
    """
    url = f"{ESTABELECIMENTOS_URL}/{cnes}"
    raw = await http_get(url)
    if not raw:
        return None
    data = _ensure_dict(raw, url)
    return _parse_estabelecimento_detalhe(data)


async def buscar_estabelecimentos_por_tipo(
    *,
    codigo_tipo: str,
    codigo_municipio: str | None = None,
    codigo_uf: str | None = None,
    status: int = 1,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> list[Estabelecimento]:
    """Search establishments filtered by type code.

    API: GET /estabelecimentos

    Args:
        codigo_tipo: Establishment type code (e.g. "73" for Pronto Atendimento).
        codigo_municipio: IBGE municipality code.
        codigo_uf: IBGE state code.
        status: 1 for active, 0 for inactive.
        limit: Max results per page.
        offset: Pagination offset.
    """
    params: dict[str, Any] = {
        "codigo_tipo_estabelecimento": codigo_tipo,
        "status": status,
        "limit": min(limit, MAX_LIMIT),
        "offset": offset,
    }
    if codigo_municipio:
        params["codigo_municipio"] = codigo_municipio
    if codigo_uf:
        params["codigo_uf"] = codigo_uf

    raw = await http_get(ESTABELECIMENTOS_URL, params=params)
    data = _ensure_list(raw, ESTABELECIMENTOS_URL)
    return [_parse_estabelecimento(item) for item in data]
