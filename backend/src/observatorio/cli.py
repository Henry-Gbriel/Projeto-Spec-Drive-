"""Linha de comando das rotinas de dados (coletar, situacao, sincronizar-catalogo)."""

import logging

import typer

from observatorio.catalogo import carregar_catalogo, sincronizar_catalogo
from observatorio.coleta import conectores_padrao
from observatorio.publicacao.publicar import republicar
from observatorio.repositorio.conexao import conectar_coletor
from observatorio.repositorio.tratado import travar_indicador
from observatorio.rotina import executar

app = typer.Typer(help="Rotinas de dados do Observatório do Real.", no_args_is_help=True)


@app.callback()
def _configurar(verboso: bool = typer.Option(False, "--verboso", "-v")) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verboso else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@app.command("sincronizar-catalogo")
def sincronizar() -> None:
    """Copia dados/catalogo.yaml para o banco (metadados e selos do catálogo)."""
    indicadores = carregar_catalogo()
    with conectar_coletor() as conn:
        sincronizar_catalogo(conn, indicadores)
    typer.echo(f"Catálogo sincronizado: {len(indicadores)} indicadores.")


@app.command()
def coletar(
    indicador: list[str] = typer.Option(None, "--indicador", "-i", help="Código do indicador."),
    todos: bool = typer.Option(False, "--todos", help="Todos os indicadores ativos."),
    carga_completa: bool = typer.Option(False, "--carga-completa", help="Recoleta o histórico."),
    simular_falha: bool = typer.Option(
        False, "--simular-falha", help="Simula falha da fonte (cenário V6 do quickstart)."
    ),
) -> None:
    """Coleta, trata, valida e publica os indicadores ativos."""
    catalogo = carregar_catalogo()
    if not todos and not indicador:
        raise typer.BadParameter("informe --indicador CODIGO ou --todos")
    if not todos:
        desconhecidos = set(indicador) - {i.codigo for i in catalogo}
        if desconhecidos:
            raise typer.BadParameter(f"indicador desconhecido: {', '.join(sorted(desconhecidos))}")
        catalogo = [i for i in catalogo if i.codigo in indicador]

    with conectar_coletor() as conn:
        sincronizar_catalogo(conn, carregar_catalogo())
        resultados = executar(
            conn,
            catalogo,
            conectores_padrao(),
            carga_completa=carga_completa,
            simular_falha=simular_falha,
        )

    for r in resultados:
        detalhe = (
            f"+{r.n_inseridas} novos, {r.n_revisadas} revisados"
            if r.n_inseridas or r.n_revisadas
            else ""
        )
        avisos = sum(1 for o in r.ocorrencias if o.severidade == "aviso")
        typer.echo(
            f"{r.codigo:<14} {r.status:<13} {detalhe} {f'{avisos} aviso(s)' if avisos else ''} "
            f"{r.mensagem}".rstrip()
        )
    if any(r.com_erro for r in resultados):
        raise typer.Exit(code=1)


@app.command()
def publicar(
    indicador: list[str] = typer.Option(..., "--indicador", "-i", help="Código do indicador."),
) -> None:
    """Regrava os dados publicados a partir da versão vigente, sem coletar."""
    catalogo = {i.codigo: i for i in carregar_catalogo()}
    desconhecidos = set(indicador) - set(catalogo)
    if desconhecidos:
        raise typer.BadParameter(f"indicador desconhecido: {', '.join(sorted(desconhecidos))}")
    falhou = False
    with conectar_coletor() as conn:
        sincronizar_catalogo(conn, list(catalogo.values()))
        for codigo in indicador:
            try:
                with conn.transaction():
                    travar_indicador(conn, codigo)
                    total = republicar(conn, catalogo[codigo])
                typer.echo(f"{codigo:<14} republicado   {total} observações")
            except ValueError as erro:
                falhou = True
                typer.echo(f"{codigo:<14} não publicado {erro}")
    if falhou:
        raise typer.Exit(code=1)


@app.command()
def situacao() -> None:
    """Mostra a versão publicada, a última coleta e os avisos de cada indicador."""
    with conectar_coletor() as conn:
        linhas = conn.execute(
            """
            SELECT p.codigo, p.situacao, p.periodo_inicio, p.periodo_fim,
                   p.ultima_atualizacao_valida, p.versao_id,
                   (SELECT c.status FROM bruto.coleta c WHERE c.indicador_codigo = p.codigo
                    ORDER BY c.iniciada_em DESC, c.id DESC LIMIT 1) AS ultima_coleta,
                   (SELECT count(*) FROM tratado.ocorrencia_validacao o
                    WHERE o.versao_id = p.versao_id AND o.severidade = 'aviso') AS avisos
            FROM publico.indicador_publicado p
            WHERE p.publicado
            ORDER BY p.ordem
            """
        ).fetchall()
    typer.echo(f"{'indicador':<24} {'situação':<22} {'período':<23} {'versão':<7} coleta  avisos")
    for linha in linhas:
        periodo = (
            f"{linha['periodo_inicio']:%Y-%m} a {linha['periodo_fim']:%Y-%m}"
            if linha["periodo_inicio"]
            else "-"
        )
        typer.echo(
            f"{linha['codigo']:<24} {linha['situacao']:<22} {periodo:<23} "
            f"{linha['versao_id'] or '-'!s:<7} {linha['ultima_coleta'] or '-':<7} {linha['avisos']}"
        )


if __name__ == "__main__":
    app()
