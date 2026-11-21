import gzip
import json
import random
import tempfile
import unittest
from pathlib import Path
from scheduler import schedule
from impact import FileSelector, UnboundedPatch, affected_files, REVISION

def patch(path="sqlglot/a.py"):
    return (f"diff --git a/{path} b/{path}\nindex 1234567..abcdef0 100644\n"
            f"--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n-old\n+new\n").encode()

def cost(workers, tests):
    durations = {t["number"]: round(t["seconds"] * 1000) for t in tests}
    return max((sum(durations[n] for n in w) for w in workers), default=0) + 2000*len(workers)

class SchedulerTests(unittest.TestCase):
    def test_empty_and_worker_cost(self):
        self.assertEqual(schedule([]), [])
        tests = [{"number": i, "seconds": 1} for i in range(8)]
        self.assertEqual(schedule(tests), [[0,2,4,6], [1,3,5,7]])
        self.assertEqual(cost(schedule(tests),tests), 8000)
        long = [{"number": i, "seconds": 30} for i in range(8)]
        self.assertEqual(schedule(long), [[i] for i in range(8)])

    def test_determinism_and_all_candidate_costs(self):
        rng=random.Random(42)
        for count in (1,2,7,8,9,31):
            tests=[{"number":i,"seconds":rng.randrange(0,60000)/1000} for i in range(count)]
            result=schedule(tests)
            self.assertEqual(sorted(n for w in result for n in w), list(range(count)))
            self.assertLessEqual(len(result),8)
            shuffled=list(reversed(tests))
            self.assertEqual(result,schedule(shuffled))
            candidate=[]
            for k in range(1,min(8,count)+1):
                loads=[0]*k
                for t in sorted(tests,key=lambda t:(-round(t["seconds"]*1000),t["number"])):
                    j=loads.index(min(loads))
                    loads[j]+=round(t["seconds"]*1000)
                candidate.append((max(loads)+2000*k,k))
            self.assertEqual((cost(result,tests),len(result)),min(candidate))

class PatchTests(unittest.TestCase):
    def test_full_parse_and_rejections(self):
        self.assertEqual(affected_files(patch()),{"sqlglot/a.py"})
        self.assertEqual(affected_files(patch()+patch("tests/test_a.py")),
                         {"sqlglot/a.py","tests/test_a.py"})
        for raw in (b"",patch()+b"garbage\n",patch().replace(b"@@ -1 +1",b"@@ -1,2 +1"),
                    patch().replace(b"+new\n",b""),b"\xff",patch("../escape.py"),
                    patch().replace(b"--- a/",b"--- /dev/null "),
                    patch().replace(b"+new\n",b"+new\r\n")):
            with self.assertRaises(UnboundedPatch):
                affected_files(raw)

    def test_backslash_lookup_keeps_original_bytes(self):
        raw=patch().replace(b"sqlglot/a.py", b"sqlglot\\a.py")
        original=raw[:]
        self.assertEqual(affected_files(raw),{"sqlglot/a.py"})
        self.assertEqual(raw, original)

    def test_insertion_and_newline_marker(self):
        raw=patch().replace(b"@@ -1 +1 @@\n-old\n+new\n",
                            b"@@ -1,0 +2 @@\n+new\n\\ No newline at end of file\n")
        self.assertEqual(affected_files(raw),{"sqlglot/a.py"})

class ConservativeMapTests(unittest.TestCase):
    def fixture(self, directory, missing=False):
        node="tests/test_a.py::test_a"
        data={"schema":1,"revision":REVISION,
              "files":["sqlglot/a.py","tests/test_a.py","tests/test_b.py"],
              "global":{"lines":[],"reads":[]},"collection":{},
              "reverse_imports":{},"dynamic_import_files":[],"fixtures":{},
              "nodes":{node:{"phases":{"setup":[],"call":[[0,[[1,2]]]],"teardown":[]},
                             "reads":{"setup":[],"call":[],"teardown":[]},"fixtures":[]}}}
        tests=[{"number":0,"id":node,"file":"tests/test_a.py","seconds":1},
               {"number":1,"id":"tests/test_b.py::test_b","file":"tests/test_b.py","seconds":1}]
        if not missing:
            data["nodes"][tests[1]["id"]]={"phases":{"setup":[],"call":[[2,[[1,1]]]],"teardown":[]},
                                        "reads":{"setup":[],"call":[],"teardown":[]},"fixtures":[]}
        path=Path(directory)/"map.gz"
        path.write_bytes(gzip.compress(json.dumps(data).encode()))
        return FileSelector(tests,path)

    def test_narrow_known_file_full_unknown_or_malformed(self):
        with tempfile.TemporaryDirectory() as d:
            selector=self.fixture(d)
            self.assertEqual(selector.select(patch())[0],{0})
            self.assertEqual(selector.select(patch("unknown.py"))[0],{0,1})
            self.assertEqual(selector.select(patch()+b"junk\n")[0],{0,1})

    def test_missing_node_broadens_whole_file(self):
        with tempfile.TemporaryDirectory() as d:
            selector=self.fixture(d,missing=True)
            self.assertEqual(selector.select(patch())[0],{0,1})

    def test_bad_map_falls_back(self):
        tests=[{"number":0,"id":"tests/t.py::a","file":"tests/t.py","seconds":0}]
        selector=FileSelector(tests,"/no-such-map.gz")
        self.assertEqual(selector.select(patch())[0],{0})

if __name__=="__main__":
    unittest.main()
