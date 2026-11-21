"""Build return-statement anchors from the pinned source and Phase 2 map."""
import argparse
import ast
import gzip
import hashlib
import json
from pathlib import Path


class ReturnSites(ast.NodeVisitor):
    def __init__(self, lines):
        self.lines = lines
        self.functions = []
        self.sites = {}

    def visit_FunctionDef(self, node):
        start = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
        self.functions.append((start, node.end_lineno))
        self.generic_visit(node)
        self.functions.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Return(self, node):
        if not self.functions or node.lineno != node.end_lineno or node.value is None:
            return
        line = self.lines[node.lineno - 1]
        if not line.lstrip().startswith("return ") or "\t" in line[:node.col_offset]:
            return
        start, end = self.functions[-1]
        self.sites[node.lineno] = [start, end, hashlib.sha256(line.encode()).hexdigest()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--base-map", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base = json.loads(gzip.decompress(args.base_map.read_bytes()))
    files = {}
    for name, expected_hash in sorted(base["source_sha256"].items()):
        if not name.startswith("sqlglot/") or not name.endswith(".py"):
            continue
        content = (args.source / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError(f"source differs from pinned map: {name}")
        lines = content.decode("utf-8").split("\n")
        visitor = ReturnSites(lines)
        visitor.visit(ast.parse(content, filename=name))
        if visitor.sites:
            files[name] = {"source_hash": expected_hash, "returns": visitor.sites}
    payload = json.dumps({"schema": 1, "revision": base["revision"], "files": files},
                         separators=(",", ":"), sort_keys=True).encode()
    args.out.write_bytes(gzip.compress(payload, mtime=0))
    print(f"{sum(len(f['returns']) for f in files.values())} return anchors across {len(files)} files")
    print(f"{args.out.stat().st_size} compressed bytes")


if __name__ == "__main__":
    main()
