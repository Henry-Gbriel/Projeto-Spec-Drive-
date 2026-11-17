from fastapi import APIRouter

from observatorio.api.esquemas import Saude
from observatorio.repositorio import publico
from observatorio.repositorio.conexao import pool_api

roteador = APIRouter()


@roteador.get("/v1/saude", response_model=Saude, operation_id="obterSaude")
def obter_saude() -> Saude:
    try:
        with pool_api().connection(timeout=5) as conn:
            banco_ok = publico.verificar_banco(conn)
    except Exception:  # noqa: BLE001 - qualquer falha de banco vira "indisponivel"
        banco_ok = False
    return Saude(status="ok", banco="ok" if banco_ok else "indisponivel")
