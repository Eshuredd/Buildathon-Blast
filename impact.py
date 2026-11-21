"""Conservative file-level impact selection; line maps are not used to narrow."""
import gzip
import json
import re
from collections import defaultdict, deque
from pathlib import Path

REVISION = "eb11aec4be8cb2122afe713a4816662c3f0fb2fa"
HUNK = re.compile(r"@@ -([0-9]{1,10})(?:,([0-9]{1,10}))? \+([0-9]{1,10})(?:,([0-9]{1,10}))? @@(?:.*)?")
HEADER = re.compile(r"diff --git (a/\S+) (b/\S+)")
INDEX = re.compile(r"index [0-9a-f]+\.\.[0-9a-f]+(?: [0-7]+)?")

class UnboundedPatch(ValueError):
    pass

def normalized(path):
    path = path.replace("\\", "/")
    if not path or path.startswith("/") or "\x00" in path or ":" in path:
        raise UnboundedPatch("unsafe path")
    if any(p in ("", ".", "..") for p in path.split("/")):
        raise UnboundedPatch("ambiguous path")
    return path

def parse_patch(raw):
    """Validate every byte's decoded line and every hunk count; never rewrite input."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise UnboundedPatch("non-UTF8 patch") from error
    if "\x00" in text or "\r" in text:
        raise UnboundedPatch("binary or unexpected line endings")
    lines = text.removesuffix("\n").split("\n")
    if not text:
        raise UnboundedPatch("empty patch")
    paths, index = {}, 0
    while index < len(lines):
        match = HEADER.fullmatch(lines[index])
        if not match:
            raise UnboundedPatch("unrecognized diff section")
        before, after = (normalized(p[2:]) for p in match.groups())
        if before != after:
            raise UnboundedPatch("rename")
        index += 1
        if index < len(lines) and INDEX.fullmatch(lines[index]):
            index += 1
        if (index + 1 >= len(lines) or not lines[index].startswith("--- a/")
                or not lines[index + 1].startswith("+++ b/")
                or normalized(lines[index][6:]) != before
                or normalized(lines[index + 1][6:]) != after):
            raise UnboundedPatch("new, deleted, metadata-only or unsupported file")
        index += 2
        hunks = []
        previous_old, previous_new = -1, -1
        while index < len(lines) and not lines[index].startswith("diff --git "):
            match = HUNK.fullmatch(lines[index])
            if not match:
                raise UnboundedPatch("unparsed hunk header or trailing data")
            old_start, old_count, new_start, new_count = match.groups()
            old_start, new_start = int(old_start), int(new_start)
            old_count = int(old_count) if old_count is not None else 1
            new_count = int(new_count) if new_count is not None else 1
            if (old_start < previous_old or new_start < previous_new
                or (old_count and not old_start) or (new_count and not new_start)
                or (not old_count and not new_count)):
                raise UnboundedPatch("invalid hunk coordinates")
            previous_old, previous_new = old_start + old_count, new_start + new_count
            index += 1
            old_seen, new_seen, changes = 0, 0, 0
            hunk = []
            old_anchor = old_start + (old_count == 0)
            while old_seen < old_count or new_seen < new_count:
                if index >= len(lines) or not lines[index] or lines[index][0] not in " +-":
                    raise UnboundedPatch("truncated hunk")
                hunk.append((old_anchor + old_seen, lines[index]))
                sign = lines[index][0]
                old_seen += sign in " -"
                new_seen += sign in " +"
                changes += sign in "+-"
                index += 1
                if index < len(lines) and lines[index] == r"\ No newline at end of file":
                    hunk.append((old_anchor + old_seen, lines[index]))
                    index += 1
                if old_seen > old_count or new_seen > new_count:
                    raise UnboundedPatch("hunk length mismatch")
            if not changes:
                raise UnboundedPatch("hunk has no edits")
            hunks.append(hunk)
        if not hunks:
            raise UnboundedPatch("no hunks")
        if before in paths:
            raise UnboundedPatch("duplicate diff section")
        paths[before] = hunks
    return paths

def affected_files(raw):
    return set(parse_patch(raw))

class FileSelector:
    def __init__(self, tests, map_path):
        self.tests = tests
        self.all_numbers = {t["number"] for t in tests}
        self.by_file = defaultdict(set)
        self.number_by_node = {}
        for t in tests:
            self.by_file[normalized(t["file"])].add(t["number"])
            self.number_by_node[t["id"]] = t["number"]
        self.problem = None
        try:
            self.data = json.loads(gzip.decompress(Path(map_path).read_bytes()))
            if self.data["revision"] != REVISION or self.data["schema"] != 1:
                raise ValueError("map revision/schema mismatch")
            self._index()
        except (OSError, EOFError, ValueError, KeyError, TypeError, IndexError) as error:
            self.problem = "maps unavailable or invalid: " + type(error).__name__

    def _index(self):
        data = self.data
        self.files = data["files"]
        self.file_index = {name: i for i,name in enumerate(self.files)}
        self.dependencies = defaultdict(set)
        self.global_files = {i for i, _ in data["global"]["lines"]} | set(data["global"]["reads"])
        self.reverse = {int(k):v for k,v in data["reverse_imports"].items()}
        self.dynamic = set(data["dynamic_import_files"])
        self.nodes = data["nodes"]
        self.missing = set(self.number_by_node) - set(self.nodes)
        self.unobserved = set()
        for node in self.missing:
            self.unobserved.update(self.by_file[normalized(node.split("::", 1)[0])])
        for node, number in self.number_by_node.items():
            entry = self.nodes.get(node)
            if entry is None:
                continue
            touched = set()
            for lines in entry["phases"].values():
                touched.update(i for i,_ in lines)
            for reads in entry["reads"].values():
                touched.update(reads)
            file = node.split("::", 1)[0]
            touched.update(i for i,_ in data["collection"].get(file, {}).get("lines", []))
            touched.update(data["collection"].get(file, {}).get("reads", []))
            for fixture in entry["fixtures"]:
                info = data["fixtures"][fixture]
                touched.update(i for i,_ in info["lines"])
                touched.update(info["reads"])
                if info["source"]["file"] in self.file_index:
                    touched.add(self.file_index[info["source"]["file"]])
            if file in self.file_index:
                touched.add(self.file_index[file])
            call = entry["phases"]["call"]
            if not call:
                self.unobserved.add(number)
            for i in touched:
                self.dependencies[i].add(number)
        # Coverage from a shared fixture's teardown may be attributed to its last
        # consumer; union setup/teardown for that fixture's source test module.
        # This deliberately broadens class/module lifecycles rather than narrowing.
        for file, numbers in self.by_file.items():
            shared = set()
            for node, number in self.number_by_node.items():
                if number not in numbers or node not in self.nodes:
                    continue
                entry = self.nodes[node]
                for phase in ("setup", "teardown"):
                    shared.update(i for i,_ in entry["phases"][phase])
                    shared.update(entry["reads"][phase])
            for i in shared:
                self.dependencies[i].update(numbers)

    def select(self, raw):
        if self.problem:
            return self.all_numbers, self.problem
        try:
            paths = affected_files(raw)
            affected = set()
            for path in paths:
                index = self.file_index.get(path)
                if index is None:
                    raise UnboundedPatch("unknown file")
                if path in self.data.get("syntax_errors", []):
                    raise UnboundedPatch("source dependency parse failed")
                if path.endswith(("conftest.py", "pyproject.toml", "pytest.ini", "setup.cfg",
                                  "setup.py", "tox.ini")):
                    raise UnboundedPatch("configuration or shared fixture")
                if path.endswith(".py") and not path.startswith(("sqlglot/", "tests/")):
                    raise UnboundedPatch("code outside mapped packages")
                queue = deque([index])
                while queue:
                    current = queue.popleft()
                    if current in affected:
                        continue
                    affected.add(current)
                    queue.extend(self.reverse.get(current, []))
            if affected & self.global_files:
                raise UnboundedPatch("global collection dependency")
            if affected & self.dynamic:
                raise UnboundedPatch("dynamic import dependency")
            selected = set(self.unobserved)
            for index in affected:
                selected.update(self.dependencies.get(index, ()))
                file = self.files[index]
                selected.update(self.by_file.get(file, ()))
            for node in self.missing:
                file = normalized(node.split("::", 1)[0])
                # Unknown nodes cannot be safely excluded from changed dependency code.
                if any(p.startswith("sqlglot/") for p in paths) or \
                        any(self.file_index.get(p) in affected for p in [file]):
                    selected.update(self.by_file[file])
            if not selected:
                raise UnboundedPatch("no bounded observed dependency")
            return selected, "file dependencies"
        except (UnboundedPatch, KeyError, TypeError, IndexError) as error:
            return self.all_numbers, "full fallback: " + str(error)
