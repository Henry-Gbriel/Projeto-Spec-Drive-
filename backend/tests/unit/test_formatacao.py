from datetime import date

from observatorio.config import mascarar_url
from observatorio.regras.formatacao import data_br, mes_abreviado


def test_mes_abreviado_em_portugues():
    assert mes_abreviado(date(2016, 1, 1)) == "jan/2016"
    assert mes_abreviado(date(2026, 9, 1)) == "set/2026"
    assert mes_abreviado(date(2025, 12, 1)) == "dez/2025"


def test_data_br():
    assert data_br(date(2026, 10, 22)) == "22/10/2026"


def test_mascarar_url_esconde_a_senha():
    url = "postgresql://coletor:segredo@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
    assert "segredo" not in mascarar_url(url)
    assert mascarar_url(None) == "(não definida)"
