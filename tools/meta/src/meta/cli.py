import re
import typer

from pathlib import Path

app = typer.Typer(no_args_is_help=True)


@app.command()
def generate(
    source: Path = typer.Option(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Upstream source",
    ),
    version: str = typer.Option(..., help="Upstream tag"),
):
    typer.echo(f"source:  {source}, version: {version}")

    functions = {"add_library"}
    for file in sorted(source.rglob("*Functions.cmake")):
        typer.echo(file.relative_to(source))
        match = re.search(r"function\(\s*([A-Za-z_]+_add_library)\b", file.read_text())
        if match:
            functions.add(match.group(1))

    targets = {}
    for file in sorted(source.rglob("CMakeLists.txt")):
        for function in sorted(functions):
            for match in sorted(
                re.finditer(
                    rf"{re.escape(function)}\((.*?)\)",
                    file.read_text(),
                    re.DOTALL,
                ),
                key=lambda match: match.group(1).split()[0],
            ):
                text = match.group(1).strip()
                name = text.split()[0]
                srcs = re.search(
                    r"\bSRCS\b(.*?)(?=\bDEPS\b|\bEXPORTED_DEPS\b|$)", text, re.DOTALL
                )
                deps = re.search(
                    r"\bDEPS\b(.*?)(?=\bSRCS\b|\bEXPORTED_DEPS\b|$)", text, re.DOTALL
                )
                exps = re.search(
                    r"\bEXPORTED_DEPS\b(.*?)(?=\bSRCS\b|\bDEPS\b|$)", text, re.DOTALL
                )
                targets[name] = {
                    "package": file.parent.relative_to(source).as_posix(),
                    "srcs": srcs.group(1).split() if srcs else [],
                    "deps": deps.group(1).split() if deps else [],
                    "exps": exps.group(1).split() if exps else [],
                }

    for name, target in sorted(targets.items()):
        typer.echo(f"{name}")
        typer.echo(f"  package: {target['package']}")
        typer.echo(f"  srcs: {target['srcs']}")
        typer.echo(f"  deps: {target['deps']}")
        typer.echo(f"  exported_deps: {target['exps']}")


@app.callback()
def main():
    pass
