"""Evaluation-side join check; the generator never reads a manifest."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--map",type=Path,required=True)
p.add_argument("--manifest",type=Path,required=True)
p.add_argument("--out",type=Path,required=True)
args=p.parse_args()
packed=args.map.read_bytes()
data=json.loads(gzip.decompress(packed))
tests=json.loads(args.manifest.read_bytes())["tests"]
nodes=data["nodes"]
missing=sorted(t["id"] for t in tests if t["id"] not in nodes)
no_call=sorted(t["id"] for t in tests if t["id"] in nodes and not nodes[t["id"]]["phases"]["call"])
reports={
    "manifest_tests":len(tests),"mapped_nodes":len(nodes),"matched_nodes":len(tests)-len(missing),
    "unmatched_manifest_ids":missing,
    "map_ids_not_numbered":sorted(set(nodes)-{t["id"] for t in tests}),
    "nodes_without_call_coverage":no_call,
    "setup_nodes":sum(bool(n["phases"]["setup"]) for n in nodes.values()),
    "call_nodes":sum(bool(n["phases"]["call"]) for n in nodes.values()),
    "teardown_nodes":sum(bool(n["phases"]["teardown"]) for n in nodes.values()),
    "fixture_relationships":len(data["fixtures"]),
    "fixture_node_edges":sum(len(f["nodes"]) for f in data["fixtures"].values()),
    "fixture_read_edges":sum(len(f["reads"]) for f in data["fixtures"].values()),
    "collection_files":len(data["collection"]),
    "map_sha256":hashlib.sha256(packed).hexdigest(),"map_bytes":len(packed),
}
args.out.write_text(json.dumps(reports,indent=2)+"\n")
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in reports.items()},indent=2))
