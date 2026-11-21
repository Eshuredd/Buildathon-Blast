"""Compile compact, node-ID-keyed maps from pinned source and raw coverage only."""
import argparse
import ast
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import coverage

REVISION = "eb11aec4be8cb2122afe713a4816662c3f0fb2fa"

def intervals(lines):
    result = []
    for n in sorted(set(lines)):
        if result and n == result[-1][1] + 1:
            result[-1][1] = n
        else:
            result.append([n, n])
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    source = args.source.resolve()
    paths = sorted(str(path.relative_to(source)).replace("\\", "/")
                   for path in source.rglob("*") if path.is_file()
                   and ".git" not in path.relative_to(source).parts
                   and "__pycache__" not in path.parts)
    numbers = {name: n for n, name in enumerate(paths)}
    meta = json.loads((args.raw / "metadata.json").read_bytes())
    if meta["pytest_exit"] != 0:
        raise SystemExit("Refusing maps from a failing pinned-base run")
    context_lines = defaultdict(lambda: defaultdict(set))
    data = coverage.CoverageData(basename=str(args.raw / ".coverage"))
    data.read()
    if not data.measured_files():
        raise SystemExit("No combined line coverage: refusing empty maps")
    for filename in sorted(data.measured_files()):
        try:
            relative = str(Path(filename).relative_to(source))
        except ValueError:
            continue
        if relative not in numbers:
            continue
        index = numbers[relative]
        for line, contexts in data.contexts_by_lineno(filename).items():
            for context in contexts:
                if "|" in context:
                    parts = context.split("|")
                    context = "global" if parts[-1] == "global" else "|".join(parts[-2:])
                context_lines[context][index].add(line)

    measured_context_count = len(context_lines)

    def encoded(context):
        return [[i, intervals(lines)] for i, lines in sorted(context_lines[context].items())]

    def known_reads(context):
        return sorted({numbers[f] for f in meta["reads"].get(context, []) if f in numbers})

    nodes = {}
    for node in meta["nodes"]:
        phases = {phase: encoded(node + "|" + phase) for phase in ("setup", "call", "teardown")}
        read_phases = {phase: known_reads(node + "|" + phase) for phase in phases}
        nodes[node] = {"phases": phases, "reads": read_phases, "fixtures": []}
    # Pytest defines unittest class fixtures in its own package, so their
    # source is outside the checkout. Recover the generated class relationship
    # from pytest's pinned naming convention; unknown external fixtures broaden.
    keys = set(meta["fixture_reads"])
    keys.update(ctx[len("fixture|"):] for ctx in context_lines if ctx.startswith("fixture|"))
    for key in sorted(keys):
        if key in meta["fixture_users"]:
            continue
        marker = "_unittest_setUpClass_fixture_"
        name = key.rsplit("::", 1)[-1]
        if name.startswith(marker):
            cls = name[len(marker):]
            users = [node for node in nodes if cls in node.split("::")[1:-1]]
        else:
            users = list(nodes)
        if users:
            source_files = sorted({node.split("::",1)[0] for node in users})
            meta["fixture_users"][key] = users
            meta["fixture_sources"][key] = {"file": source_files[0], "scope": "class-or-shared",
                                             "external": True}
    fixtures = {}
    for key, users in sorted(meta["fixture_users"].items()):
        fixtures[key] = {"source": meta["fixture_sources"][key],
                         "nodes": users,
                         "lines": encoded("fixture|" + key),
                         "reads": sorted({numbers[f] for f in meta["fixture_reads"].get(key, [])
                                          if f in numbers})}
        for node in users:
            if node in nodes:
                nodes[node]["fixtures"].append(key)
    collection = {}
    for name in paths:
        ctx = "collection|" + name
        lines, reads = encoded(ctx), known_reads(ctx)
        if lines or reads:
            collection[name] = {"lines": lines, "reads": reads}
    modules = {}
    for name in paths:
        if name.endswith(".py") and name.startswith(("sqlglot/", "tests/")):
            module = name[:-3].replace("/", ".")
            if module.endswith(".__init__"):
                module = module[:-9]
            modules[module] = name
    reverse = defaultdict(set)
    functions = {}
    dynamic = []
    syntax_errors = []
    for module, name in sorted(modules.items()):
        index = numbers[name]
        try:
            tree = ast.parse((source / name).read_bytes(), filename=name)
        except SyntaxError:
            syntax_errors.append(name)
            continue
        functions[index] = sorted(
            [[node.name, min([node.lineno] + [d.lineno for d in node.decorator_list]), node.end_lineno]
             for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
            key=lambda x: (x[1], x[2], x[0]))
        package = module if name.endswith("/__init__.py") else module.rpartition(".")[0]
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                prefix = node.module or ""
                if node.level:
                    parts = package.split(".")
                    keep = len(parts) - node.level + 1
                    prefix = ".".join(parts[:keep] + ([prefix] if prefix else []))
                imports.add(prefix)
                imports.update(prefix + "." + alias.name for alias in node.names)
            elif isinstance(node, ast.Call):
                target = node.func
                if ((isinstance(target, ast.Name) and target.id == "__import__")
                    or (isinstance(target, ast.Attribute) and target.attr == "import_module")):
                    dynamic.append(index)
        for imported in imports:
            # Importing a symbol uses its defining module and all package initializers.
            chunks = imported.split(".")
            for end in range(1, len(chunks) + 1):
                prefix = ".".join(chunks[:end])
                if prefix in modules and modules[prefix] != name:
                    reverse[numbers[modules[prefix]]].add(index)
    hashes = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in paths}
    payload = {"schema": 1, "revision": REVISION, "files": paths,
               "source_sha256": hashes, "nodes": nodes, "collection": collection,
               "global": {"lines": encoded("global"), "reads": known_reads("global")},
               "fixtures": fixtures, "functions": functions,
               "reverse_imports": {str(k): sorted(v) for k,v in sorted(reverse.items())},
               "dynamic_import_files": sorted(set(dynamic)), "syntax_errors": syntax_errors,
               "instrumentation": {"coverage": meta["coverage"], "python": meta["python"],
                                   "skip_integration": meta["skip_integration"],
                                   "pytest_exit": meta["pytest_exit"]}}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    args.out.mkdir(parents=True, exist_ok=True)
    packed = gzip.compress(blob, compresslevel=9, mtime=0)
    (args.out / "base-map.json.gz").write_bytes(packed)
    report = {"revision": REVISION, "nodes": len(nodes), "source_files": len(paths),
              "coverage_contexts": measured_context_count, "collection_files": len(collection),
              "fixtures": len(fixtures), "function_ranges": sum(map(len, functions.values())),
              "reverse_import_edges": sum(map(len, reverse.values())),
              "dynamic_import_files": [paths[i] for i in sorted(set(dynamic))],
              "syntax_errors": syntax_errors, "map_bytes": len(packed),
              "map_uncompressed_bytes": len(blob),
              "map_sha256": hashlib.sha256(packed).hexdigest()}
    (args.out / "generation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
