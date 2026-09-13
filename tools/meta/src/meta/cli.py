import re
import typer

from pathlib import Path

app = typer.Typer(no_args_is_help=True)


@app.command()
def generate(
    src: Path = typer.Option(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help="Upstream directory",
    ),
    dst: Path = typer.Option(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Output directory",
    ),
    version: str = typer.Option(..., help="Upstream tag"),
):
    typer.echo(f"src: {src}, dst: {dst}, version: {version}")

    functions = {"add_library"}
    for file in sorted(src.rglob("*Functions.cmake")):
        match = re.search(r"function\(\s*([A-Za-z_]+_add_library)\b", file.read_text())
        if match:
            functions.add(match.group(1))

    packages = {}
    for file in sorted(src.rglob("CMakeLists.txt")):
        package = file.parent.relative_to(src).as_posix()
        prefix = package.replace("/", "_")
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
                if name == prefix:
                    label = Path(package).name
                elif name.startswith(f"{prefix}_"):
                    label = name.removeprefix(f"{prefix}_")
                else:
                    label = name
                srcs = re.search(
                    r"\bSRCS\b(.*?)(?=\bDEPS\b|\bEXPORTED_DEPS\b|$)", text, re.DOTALL
                )
                deps = re.search(
                    r"\bDEPS\b(.*?)(?=\bSRCS\b|\bEXPORTED_DEPS\b|$)", text, re.DOTALL
                )
                exps = re.search(
                    r"\bEXPORTED_DEPS\b(.*?)(?=\bSRCS\b|\bDEPS\b|$)", text, re.DOTALL
                )
                packages.setdefault(package, {})[name] = {
                    "label": label,
                    "srcs": srcs.group(1).split() if srcs else [],
                    "deps": deps.group(1).split() if deps else [],
                    "exps": exps.group(1).split() if exps else [],
                }

    labels = {
        name: {
            "package": package,
            "label": target["label"],
        }
        for package, targets in packages.items()
        for name, target in targets.items()
    }

    for package, targets in sorted(packages.items()):
        out = dst / version / "overlay" / package
        out.mkdir(parents=True, exist_ok=True)
        lines = [
            'load("@rules_cc//cc:defs.bzl", "cc_library")',
            "",
            'package(default_visibility = ["//visibility:public"])',
            "",
        ]
        for name, target in sorted(targets.items()):
            lines.append("cc_library(")
            lines.append(f'    name = "{target["label"]}",')
            if target["srcs"]:
                lines.append("    srcs = [")
                for x in target["srcs"]:
                    lines.append(f'        "{x}",')
                lines.append("    ],")
            deps = []
            for x in target["deps"] + target["exps"]:
                if x in labels:
                    dep = labels[x]
                    if dep["package"] == package:
                        deps.append(f":{dep['label']}")
                    else:
                        deps.append(f"//{dep['package']}:{dep['label']}")
            if deps:
                lines.append("    deps = [")
                for x in sorted(set(deps)):
                    lines.append(f'        "{x}",')
                lines.append("    ],")
            lines.append(")")
            lines.append("")

        build = out / "BUILD.bazel"
        build.write_text("\n".join(lines))


@app.callback()
def main():
    pass
