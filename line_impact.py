"""Line selection for edits certified against pinned return statements."""
import ast
import gzip
import hashlib
import json

from impact import FileSelector, REVISION, UnboundedPatch, parse_patch

# This policy value is part of the frozen candidate.
ALLOW_INSERTIONS = True
EXPRESSION_NODES = (
    ast.Expression, ast.Constant, ast.Name, ast.Load, ast.BinOp, ast.UnaryOp,
    ast.BoolOp, ast.Compare, ast.IfExp, ast.operator, ast.unaryop, ast.boolop, ast.cmpop,
)


def return_expression(line):
    text = line.strip()
    if not text.startswith("return ") or len(text) > 4096 or "#" in text:
        return None
    try:
        expression = ast.parse(text.removeprefix("return "), mode="eval")
    except SyntaxError:
        return None
    nodes = list(ast.walk(expression))
    if any(not isinstance(node, EXPRESSION_NODES) for node in nodes):
        return None
    return {node.id for node in nodes if isinstance(node, ast.Name)}


def bounds_for_hunk(hunk, sites, allow_insertions):
    removed = [(number, line[1:]) for number, line in hunk if line.startswith("-")]
    added = [(number, line[1:]) for number, line in hunk if line.startswith("+")]
    if len(added) != 1 or any(line.startswith("\\") for _, line in hunk):
        return None
    new_anchor, new = added[0]
    if len(removed) == 1:
        number, old = removed[0]
        if new_anchor != number + 1:
            return None
    elif allow_insertions and not removed:
        # An insertion immediately before a verified return, at that same
        # indentation, is syntactically in the same block. Require that
        # exact old-side context line. Zero-context inserts stay file-level.
        number = new_anchor
        old = next((line[1:] for n, line in hunk
                    if n == number and line.startswith(" ")), None)
        if old is None:
            return None
    else:
        return None
    site = sites.get(str(number))
    if not site:
        return None
    start, end, digest = site
    if not start < number <= end or hashlib.sha256(old.encode()).hexdigest() != digest:
        return None
    old_indent = old[:len(old) - len(old.lstrip())]
    new_indent = new[:len(new) - len(new.lstrip())]
    if new_indent != old_indent or not old_indent or "\t" in old_indent:
        return None
    old_names, new_names = return_expression(old), return_expression(new)
    if old_names is None or new_names is None or not new_names <= old_names:
        return None
    return start, end


def covered(lines, index, start, end):
    return any(start <= high and low <= end
               for file_index, intervals in lines if file_index == index
               for low, high in intervals)


class LineSelector(FileSelector):
    def __init__(self, tests, base_map, site_map):
        super().__init__(tests, base_map)
        self.sites = {}
        self.scope_cache = {}
        if self.problem:
            return
        try:
            data = json.loads(gzip.decompress(site_map.read_bytes()))
            if data["schema"] == 1 and data["revision"] == REVISION:
                self.sites = data["files"]
        except (OSError, EOFError, ValueError, KeyError, TypeError):
            pass

    def select(self, raw):
        if self.sites:
            try:
                narrowed = self._narrow(parse_patch(raw))
                if narrowed is not None:
                    return narrowed, "bounded function dependencies"
            except (UnboundedPatch, KeyError, TypeError, IndexError):
                pass
        return super().select(raw)

    def _narrow(self, patch):
        numbers = set(self.unobserved)
        for path, hunks in patch.items():
            entry = self.sites.get(path)
            index = self.file_index.get(path)
            if index is None or index in self.dynamic or not entry:
                return None
            if entry["source_hash"] != self.data["source_sha256"].get(path):
                return None
            for hunk in hunks:
                bounds = bounds_for_hunk(hunk, entry["returns"], ALLOW_INSERTIONS)
                if bounds is None:
                    return None
                key = (index, *bounds)
                if key not in self.scope_cache:
                    self.scope_cache[key] = self._scope_dependencies(*key)
                selected = self.scope_cache[key]
                if selected is None:
                    return None
                numbers.update(selected)
        return numbers

    def _scope_dependencies(self, index, start, end):
        def hit(lines):
            return covered(lines, index, start, end)

        globals_ = self.data["global"]
        if index in globals_["reads"] or hit(globals_["lines"]):
            return None
        numbers = set()
        observed_function = False
        for node, number in self.number_by_node.items():
            entry = self.nodes.get(node)
            if not entry:
                continue
            file = node.split("::", 1)[0]
            phases = entry["phases"]
            if hit(phases["call"]):
                numbers.add(number)
                observed_function = True
            if any(hit(phases[phase]) for phase in ("setup", "teardown")):
                numbers.update(self.by_file[file])
                observed_function = True
            if any(index in reads for reads in entry["reads"].values()):
                numbers.add(number)
        for file, data in self.data["collection"].items():
            if index in data["reads"] or hit(data["lines"]):
                numbers.update(self.by_file.get(file, ()))
        for fixture in self.data["fixtures"].values():
            if index in fixture["reads"] or hit(fixture["lines"]):
                numbers.update(self.number_by_node[node] for node in fixture["nodes"]
                               if node in self.number_by_node)
        # A cold function is not evidence that changing it is irrelevant.
        return numbers if observed_function else None
