"""Configuração lida de variáveis de ambiente (ou do arquivo .env, nunca versionado)."""

import re
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[3]
CAMINHO_CATALOGO = RAIZ_REPOSITORIO / "dados" / "catalogo.yaml"
FUSO_HORARIO = ZoneInfo("America/Sao_Paulo")


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    coletor_database_url: str | None = None
    api_database_url: str | None = None
    cors_origens: str = "http://localhost:5173"
    ambiente: str = "local"

    @property
    def lista_cors(self) -> list[str]:
        return [origem.strip() for origem in self.cors_origens.split(",") if origem.strip()]

    @property
    def producao(self) -> bool:
        return self.ambiente == "producao"


@lru_cache
def obter_configuracao() -> Configuracao:
    return Configuracao()


def mascarar_url(url: str | None) -> str:
    """Esconde a senha de uma URL de conexão para que ela possa aparecer em logs."""
    if not url:
        return "(não definida)"
    return re.sub(r"(://[^:/@]+:)[^@]*@", r"\1***@", url)
