"""Analysis prompts for the TCU feature."""

from __future__ import annotations


def analise_acordaos() -> str:
    """Análise dos acórdãos mais recentes do TCU.

    Gera um resumo analítico das decisões recentes do tribunal.
    """
    return (
        "Faça uma análise dos acórdãos mais recentes do TCU:\n\n"
        "1. Use consultar_acordaos(quantidade=20) para obter os últimos acórdãos\n"
        "2. Agrupe por colegiado (Plenário, 1ª Câmara, 2ª Câmara)\n"
        "3. Identifique os relatores mais frequentes\n"
        "4. Resuma os principais temas dos sumários\n"
        "5. Apresente um panorama geral das decisões recentes"
    )
