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

    functions = {"add_library": []}
    for file in sorted(src.rglob("*Functions.cmake")):
        content = file.read_text()
        for match in re.finditer(
            r"function\(\s*([A-Za-z_]+_add_library)\b(.*?)endfunction",
            content,
            re.DOTALL,
        ):
            function = match.group(1)
            body = match.group(2)
            clean = re.sub(r"#.*", "", body)
            arguments = re.search(
                r'cmake_parse_arguments\(\s*\S+\s*"[^"]*"\s*"[^"]*"\s*"([^"]*)"',
                clean,
                re.DOTALL,
            )
            functions[function] = arguments.group(1).split(";") if arguments else []
    packages = {}
    generated = {}
    includes = {}
    header_globs = {}
    header_filters = {}
    header_sets = {}
    for file in sorted(src.rglob("CMakeLists.txt")):
        package = file.parent.relative_to(src).as_posix()
        prefix = package.replace("/", "_")
        content = file.read_text()
        conditional_ranges = []
        condition_stack = []
        for match in re.finditer(
            r"(?im)^\s*(if|endif)\s*\((.*?)\)",
            content,
        ):
            command = match.group(1).lower()
            if command == "if":
                condition_stack.append((match.start(), match.group(2).strip()))
            elif condition_stack:
                start, condition = condition_stack.pop()
                conditional_ranges.append((start, match.end(), condition))
        for match in re.finditer(
            r"file\(\s*GLOB_RECURSE\s+([A-Za-z0-9_]+)(.*?)\)",
            content,
            re.DOTALL,
        ):
            variable = match.group(1)
            body = match.group(2)
            for pattern in re.findall(r'"([^"]+\.(?:h|hh|hpp))"', body):
                pattern = pattern.replace("${CMAKE_CURRENT_SOURCE_DIR}/", "")
                header_globs.setdefault(
                    variable,
                    {
                        "package": package,
                        "patterns": set(),
                    },
                )["patterns"].add(pattern)
        for match in re.finditer(
            r'list\(\s*FILTER\s+([A-Za-z0-9_]+)\s+(INCLUDE|EXCLUDE)\s+REGEX\s+"([^"]+)"\s*\)',
            content,
        ):
            header_filters.setdefault(match.group(1), []).append(
                (match.group(2), match.group(3))
            )
        for match in re.finditer(
            r"[A-Za-z_]+_install_headers\(\s*(\S+)\s+\S+\s+\$\{([A-Za-z0-9_]+)\}\s*\)",
            content,
        ):
            conditions = [
                condition
                for start, end, condition in conditional_ranges
                if start < match.start() < end
            ]
            header_sets[match.group(2)] = {
                "package": package,
                "include_prefix": match.group(1),
                "conditions": conditions,
            }
        for match in re.finditer(
            r"configure_file\(\s*(\S+)\s+(\S+)\s*\)", content, re.DOTALL
        ):
            template = match.group(1)
            output = match.group(2)
            template_path = file.parent / template
            template_content = template_path.read_text()
            substitutions = {}
            for variable in re.findall(r"@([A-Za-z0-9_]+)@", template_content):
                value = re.search(
                    rf'set\(\s*{re.escape(variable)}\s+"?([^"\s\)]+)"?', content
                )
                if value:
                    substitutions[variable] = value.group(1)
            generated[output] = {
                "template": template,
                "package": package,
                "substitutions": substitutions,
            }
        for match in re.finditer(
            r"target_include_directories\(\s*([A-Za-z0-9_]+)\s+INTERFACE(.*?)\)",
            content,
            re.DOTALL,
        ):
            includes[match.group(1)] = match.group(2).split()
        for function in sorted(functions):
            for match in sorted(
                re.finditer(
                    rf"{re.escape(function)}\((.*?)\)",
                    content,
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
                fields = {}
                arguments = functions[function]
                for argument in arguments:
                    others = "|".join(re.escape(x) for x in arguments if x != argument)
                    if others:
                        pattern = (
                            rf"\b{re.escape(argument)}\b(.*?)(?=\b(?:{others})\b|$)"
                        )
                    else:
                        pattern = rf"\b{re.escape(argument)}\b(.*?)$"
                    value = re.search(pattern, text, re.DOTALL)
                    fields[argument] = value.group(1).split() if value else []
                packages.setdefault(package, {})[name] = {
                    "label": label,
                    "function": function,
                    **{key.lower(): value for key, value in fields.items()},
                }
    for name, paths in includes.items():
        for path in paths:
            match = re.match(r"\$<BUILD_INTERFACE:(.+)>", path)
            if not match:
                continue
            include = match.group(1)
            for output, value in generated.items():
                if output.startswith(f"{include}/"):
                    value["target"] = name
                    value["include"] = include
            for output, value in generated.items():
                target = value.get("target")
                if not target:
                    continue
                package = value["package"]
                if package in packages and target in packages[package]:
                    packages[package][target]["generated"] = {
                        "template": value["template"],
                        "output": output,
                        "include": value["include"],
                        "substitutions": value["substitutions"],
                    }

    headers = {}
    for variable, value in header_globs.items():
        package = value["package"]
        root = src / package
        files = {
            path.relative_to(root).as_posix()
            for pattern in value["patterns"]
            for path in root.rglob(pattern)
        }
        for operation, regex in header_filters.get(variable, []):
            if operation == "INCLUDE":
                files = {path for path in files if re.search(regex, path)}
            else:
                files = {path for path in files if not re.search(regex, path)}
        headers[variable] = sorted(files)

    header_packages = {
        header_set["package"]
        for variable, header_set in header_sets.items()
        if not header_set["conditions"] and headers.get(variable)
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
            'load("@bazel_skylib//rules:expand_template.bzl", "expand_template")',
            'load("@rules_cc//cc:defs.bzl", "cc_library")',
            "",
            'package(default_visibility = ["//visibility:public"])',
            "",
        ]
        for variable, header_set in sorted(header_sets.items()):
            if header_set["package"] != package:
                continue
            if header_set["conditions"]:
                continue
            public_headers = headers.get(variable, [])
            if not public_headers:
                continue
            lines.append("cc_library(")
            lines.append('    name = "headers",')
            lines.append("    hdrs = [")
            for x in public_headers:
                lines.append(f'        "{x}",')
            lines.append("    ],")
            lines.append(f'    include_prefix = "{header_set["include_prefix"]}",')
            lines.append(")")
            lines.append("")
        for name, target in sorted(targets.items()):
            hdrs = []
            if "generated" in target:
                generated = target["generated"]
                rule = f"{target['label']}_h"
                output = Path(generated["output"]).name
                relative = generated["output"].removeprefix(f"{generated['include']}/")
                include_prefix = Path(relative).parent.as_posix()
                lines.append("expand_template(")
                lines.append(f'    name = "{rule}",')
                lines.append(f'    out = "{output}",')
                lines.append("    substitutions = {")
                for key, value in sorted(generated["substitutions"].items()):
                    lines.append(f'        "@{key}@": "{value}",')
                lines.append("    },")
                lines.append(f'    template = "{generated["template"]}",')
                lines.append(")")
                lines.append("")
                hdrs.append(f":{rule}")
            hdrs.extend(target.get("headers", []))
            lines.append("cc_library(")
            lines.append(f'    name = "{target["label"]}",')
            if hdrs:
                lines.append("    hdrs = [")
                for x in hdrs:
                    lines.append(f'        "{x}",')
                lines.append("    ],")
            if "generated" in target and include_prefix != ".":
                lines.append(f'    include_prefix = "{include_prefix}",')
            srcs = target.get("srcs", [])
            if srcs:
                lines.append("    srcs = [")
                for x in srcs:
                    lines.append(f'        "{x}",')
                lines.append("    ],")
            deps = []
            if target["function"] != "add_library":
                for header_package in header_packages:
                    if package == header_package or package.startswith(
                        f"{header_package}/"
                    ):
                        if package == header_package:
                            deps.append(":headers")
                        else:
                            deps.append(f"//{header_package}:headers")
            for x in target.get("deps", []) + target.get("exported_deps", []):
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
