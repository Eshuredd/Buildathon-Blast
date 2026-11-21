"""Runtime selector with line, file, and all-tests modes."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from scheduler import schedule

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("all", "file", "line"), default="line")
    parser.add_argument("--data", type=Path, default=Path("/data"))
    args = parser.parse_args()
    tests = json.loads((args.data / "tests.json").read_bytes())["tests"]
    selector = None
    map_dir = Path(__file__).parent / "maps"
    if args.mode == "line":
        from line_impact import LineSelector
        selector = LineSelector(tests, map_dir / "base-map.json.gz",
                                map_dir / "return-sites.json.gz")
    elif args.mode == "file":
        from impact import FileSelector
        selector = FileSelector(tests, map_dir / "base-map.json.gz")
    all_workers = schedule(tests)
    cache = {}
    reasons = Counter()
    for patch in sorted((args.data / "commits").glob("*.patch")):
        if selector is None:
            workers = all_workers
            reasons["all-tests control"] += 1
        else:
            numbers, reason = selector.select(patch.read_bytes())
            reasons[reason] += 1
            key = tuple(sorted(numbers))
            if numbers == selector.all_numbers:
                workers = all_workers
            elif key in cache:
                workers = cache[key]
            else:
                workers = schedule([test for test in tests if test["number"] in numbers])
                cache[key] = workers
        print(json.dumps({"commit": patch.stem, "workers": workers}, separators=(",", ":")))
    print(json.dumps(dict(sorted(reasons.items())), separators=(",", ":")), file=sys.stderr)

if __name__ == "__main__":
    main()
