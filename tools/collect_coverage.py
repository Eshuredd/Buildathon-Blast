"""Record pinned-base pytest coverage and resource reads, without labels."""
import inspect
from concurrent.futures import ProcessPoolExecutor
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import coverage
import pytest

ROOT = Path.cwd()
OUT = Path(os.environ["BLAST_RAW_DIR"])
OUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("BLAST_CONTEXT", "")
cov = coverage.Coverage(config_file="/tools/coverage.ini")
context = os.environ.get("BLAST_CONTEXT", "global")
reads = defaultdict(set)
fixture_reads = defaultdict(set)
fixture_users = defaultdict(set)
fixture_sources = {}
active_fixtures = []
nodes = []
reports = []
busy = False

def relative(filename):
    if not isinstance(filename, (str, bytes)):
        return None
    filename = os.fsdecode(filename)
    value = os.path.abspath(filename)
    prefix = str(ROOT) + os.sep
    if value.startswith(prefix):
        return value[len(prefix):].replace(os.sep, "/")
    return None

def audit(event, args):
    global busy
    if event != "open" or busy:
        return
    busy = True
    try:
        name = relative(args[0])
        if name and not name.endswith((".pyc", ".pyo")):
            reads[context].add(name)
            if __name__ != "__main__":
                with (OUT / ("child-reads-" + str(os.getpid()) + ".jsonl")).open("a") as log:
                    log.write(json.dumps([context, name]) + "\n")
            for key in active_fixtures:
                fixture_reads[key].add(name)
    finally:
        busy = False

def switch(value):
    global context
    previous = context
    context = value
    os.environ["BLAST_CONTEXT"] = value
    cov.switch_context(value)
    return previous

class Plugin:
    @pytest.hookimpl(hookwrapper=True)
    def pytest_make_collect_report(self, collector):
        file = relative(str(collector.path))
        previous = switch("collection|" + file if file and file.endswith(".py") else "global")
        try:
            yield
        finally:
            switch(previous)

    def pytest_collection_modifyitems(self, items):
        for item in items:
            nodes.append(item.nodeid)
            info = getattr(item, "_fixtureinfo", None)
            if info:
                for name, definitions in info.name2fixturedefs.items():
                    for definition in definitions or ():
                        source = relative(inspect.getsourcefile(definition.func) or "")
                        if source:
                            key = source + "::" + name
                            fixture_sources[key] = {"file": source, "scope": definition.scope}
                            fixture_users[key].add(item.nodeid)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item):
        previous = switch(item.nodeid + "|setup")
        try:
            yield
        finally:
            switch(previous)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        previous = switch(item.nodeid + "|call")
        try:
            yield
        finally:
            switch(previous)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self, item):
        previous = switch(item.nodeid + "|teardown")
        try:
            yield
        finally:
            switch(previous)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef, request):
        source = relative(inspect.getsourcefile(fixturedef.func) or "")
        key = (source or "external") + "::" + fixturedef.argname
        active_fixtures.append(key)
        previous = switch("fixture|" + key)
        try:
            yield
        finally:
            switch(previous)
            active_fixtures.pop()

    def pytest_runtest_logreport(self, report):
        if report.failed:
            print("\nFAILED " + report.nodeid + "\n" + str(report.longrepr), file=sys.stderr, flush=True)
        reports.append({"id": report.nodeid, "phase": report.when,
                        "outcome": report.outcome, "duration": report.duration})

    def pytest_collectreport(self, report):
        if report.failed:
            reports.append({"id": report.nodeid, "phase": "collection", "outcome": "failed"})

def run_in_context(value, function, args, kwargs):
    global context
    previous = context
    context = value
    current = coverage.Coverage.current()
    if current is not None:
        current.switch_context(value)
    try:
        return function(*args, **kwargs)
    finally:
        context = previous
        if current is not None:
            current.switch_context(previous)

original_submit = ProcessPoolExecutor.submit

def submit_with_context(self, function, /, *args, **kwargs):
    return original_submit(self, run_in_context, context, function, args, kwargs)

sys.addaudithook(audit)
if __name__ == "__main__":
    ProcessPoolExecutor.submit = submit_with_context
    cov.start()
    switch("global")
    paths = os.environ.get("BLAST_TEST_PATHS", "tests").split()
    code = pytest.main(paths + ["-q", "-p", "no:cacheprovider"], plugins=[Plugin()])
    cov.stop()
    cov.save()
    cov.combine(keep=True)
    combined = coverage.CoverageData(basename=str(OUT / ".coverage"))
    combined.update(cov.get_data())
    combined.write()
    for log in OUT.glob("child-reads-*.jsonl"):
        for line in log.read_text().splitlines():
            child_context, file = json.loads(line)
            reads[child_context].add(file)
    metadata = {"nodes": sorted(nodes), "reads": {k: sorted(v) for k, v in reads.items()},
                "fixture_reads": {k: sorted(v) for k, v in fixture_reads.items()},
                "fixture_users": {k: sorted(v) for k, v in fixture_users.items()},
                "fixture_sources": fixture_sources, "reports": reports, "pytest_exit": int(code),
                "python": sys.version, "coverage": coverage.__version__,
                "skip_integration": os.environ.get("SKIP_INTEGRATION")}
    (OUT / "metadata.json").write_text(json.dumps(metadata, sort_keys=True))
    raise SystemExit(code)
