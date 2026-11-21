"""Local evaluation only: official scoring plus retained parent-cgroup CPU."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import time
from pathlib import Path

def cpu():
    out = subprocess.check_output(["wsl.exe", "-d", "docker-desktop", "--",
                                  "cat", "/sys/fs/cgroup/blast-phase2-accounting/cpu.stat"], cwd="/mnt/c")
    return {k: int(v) for k, v in (line.split() for line in out.decode().splitlines())}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("/home/eshum/Buildathon-Blast"))
    p.add_argument("--evidence", type=Path, default=Path("/home/eshum/blast-phase2-evidence"))
    p.add_argument("--image", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--mode", choices=("all", "file"))
    p.add_argument("--sample", type=Path)
    p.add_argument("--runs", type=int, choices=(1,3), default=3)
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args()
    subprocess.run(["wsl.exe", "-d", "docker-desktop", "--", "mkdir", "-p",
                    "/sys/fs/cgroup/blast-phase2-accounting"], cwd="/mnt/c", check=True)
    root, out = args.root, args.evidence
    sample = args.sample or root / "starter/sample"
    out.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("official", root / "starter/score.py")
    official = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(official)
    tests = json.loads((sample / "tests.json").read_bytes())["tests"]
    answers = json.loads((sample / "answers.json").read_bytes())["commits"]
    runs = []
    patch_count = len(list((sample / "commits").glob("*.patch")))
    for index in range(1, args.runs + 1):
        name = f"{args.version}-{index}"
        flags = ["docker", "run", "--rm", "--platform", "linux/amd64",
                 "--cgroup-parent=/blast-phase2-accounting",
                 "--network", "none", "--cpus", "2", "--memory", "4096m",
                 "--memory-swap", "4096m", "--pids-limit", "256", "--read-only",
                 "--tmpfs", "/tmp:rw,size=64m,mode=1777", "--cap-drop", "ALL",
                 "--security-opt", "no-new-privileges", "--user", "65534:65534",
                 "--env", "HOME=/tmp",
                 "--volume", f"{sample}/commits:/data/commits:ro",
                 "--volume", f"{sample}/tests.json:/data/tests.json:ro", args.image]
        if args.mode:
            flags += ["python", "/app/selector.py", "--mode", args.mode]
        before = cpu()
        start = time.perf_counter()
        result = subprocess.run(flags, capture_output=True, timeout=args.timeout)
        wall = time.perf_counter() - start
        after = cpu()
        stdout, stderr = result.stdout, result.stderr
        (out / f"{name}.jsonl").write_bytes(stdout)
        (out / f"{name}.stderr").write_bytes(stderr)
        evaluation = official.evaluate_run(stdout, tests, answers)
        if result.returncode or not evaluation["ok"] or len(stdout) > 2_000_000:
            raise RuntimeError((result.returncode, evaluation, stderr.decode(errors="replace")))
        delta = {k: after[k] - before[k] for k in ("usage_usec", "user_usec", "system_usec")}
        charged = delta["user_usec"] + delta["system_usec"]
        total = evaluation["simulated_milliseconds"] * 1000 + charged
        row = {"version": args.version, "run": index, "batch": f"local-{patch_count}",
               "missed_commits": len(evaluation["missed_commits"]),
               "simulated_seconds": evaluation["simulated_milliseconds"] / 1000,
               "container_user_seconds": delta["user_usec"] / 1e6,
               "container_system_seconds": delta["system_usec"] / 1e6,
               "container_cpu_seconds": charged / 1e6,
               "cgroup_usage_seconds": delta["usage_usec"] / 1e6,
               "total_microseconds": total, "official_total_seconds": total / 1e6,
               "wall_seconds": wall, "stdout_bytes": len(stdout),
               "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
               "cpu_before": before, "cpu_after": after, "command": flags}
        runs.append(row)
        print(json.dumps({k: row[k] for k in ("version","run","missed_commits",
              "simulated_seconds","container_cpu_seconds","official_total_seconds",
              "wall_seconds","stdout_bytes")}), flush=True)
    totals = sorted(r["total_microseconds"] for r in runs)
    summary = {"version": args.version, "runs": runs,
               "median_total_seconds": totals[1] / 1e6 if len(totals) == 3 else None,
               "rounded_score": ((totals[1] + 50_000) // 100_000) / 10 if len(totals) == 3 else None,
               "single_total_seconds": totals[0] / 1e6 if len(totals) == 1 else None,
               "byte_identical": len({r["stdout_sha256"] for r in runs}) == 1}
    (out / f"{args.version}-benchmark.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k:v for k,v in summary.items() if k != "runs"}))
if __name__ == "__main__":
    main()
