# Phase 1 — unchanged starter baseline

Completed 2026-11-21 (Asia/Kolkata). Stopped at the Phase 1 checkpoint. No selector or scheduler implementation was changed. Work was solo, local, and CPU-only; nothing was pushed, published, submitted, or provisioned.

## Sources and access

| Source | URL / location | Access status |
| --- | --- | --- |
| Official brief | https://www.joinbuilders.org/buildathon/tracks/blast-radius | HTTP 200 via WSL curl; read in full. The first web-tool open failed, but a subsequent open succeeded. |
| Official starter, using the brief's download link | https://www.joinbuilders.org/buildathon/tracks/blast-radius/files/blast-radius-sample.tar.gz | HTTP 200; downloaded 38,398 bytes, extracted into a newly created empty `./starter`. No fallback copy needed. |
| Published scoring specification | https://www.joinbuilders.org/buildathon/tracks/blast-radius/files/SCORING.md | HTTP 200; byte-identical to the bundled `starter/SCORING.md`. |
| Bundled documentation and implementation | `starter/{README.md,SCORING.md,Makefile,Dockerfile,selector.py,score.py,requirements.lock}` | Read before the baseline run. Manifest, sample answer schema, and patch format inspected. |
| Project instructions | `AGENTS.md`, `PHASED_PROMPTS.md`, and `/mnt/c/Users/eshum/.codex/RTK.md` | Read; only Phase 1 executed. |

Archive SHA-256: `81efabbc69c3c4367d928f2dba0f33ce9dccccbd080b54721b2636e5d8afab9d`.

All 39 archived files were compared byte-for-byte with the extracted control after execution: zero differences. Patch bytes were preserved, including original LF line endings. Archive and HTTP headers are retained outside the submission tree in `/home/eshum/blast-phase1-evidence/`.

The required SQLGlot base is `eb11aec4be8cb2122afe713a4816662c3f0fb2fa`. Phase 1 does not need its source checkout or reference pytest runs. No dependencies from `requirements.lock` were installed: the unchanged baseline selector uses only Python's standard library. Future reference pytest runs must use the pinned image, that lock file, and `SKIP_INTEGRATION=0`.

## Workspace and isolation

The authoritative Linux working directory is `/home/eshum/Buildathon-Blast`, on WSL2's ext4 filesystem (`/dev/sdd`), not the Windows-mounted OneDrive filesystem. The baseline ran from `/home/eshum/Buildathon-Blast/starter`.

The attached Windows folder contains a review mirror of the starter and this report. Continue actual build and evaluation work in the Linux directory. Root `.gitignore` and `.dockerignore` exclude `starter/`, `.phase1/`, and `PHASED_PROMPTS.md`; `.dockerignore` also excludes `.git/`. No Git repository existed initially, and none was initialized or committed in Phase 1. No starter files were staged. Evidence and sample labels remain outside the future submission context.

The unchanged benchmark intentionally builds from `starter/` using its own Dockerfile. That Dockerfile copies only `selector.py`, so sample patches, labels, and the scorer are absent from the resulting image. This benchmark build is separate from the future root submission build, whose ignore file excludes the entire starter directory.

## Published baseline versus observed sample

The official brief publishes **1614.1 s**, described as running every test across three workers. It is the published contest reference, not a measurement of this local sample run. The practice reference of 150.3 s in project instructions is not the starter baseline or a local result. Official practice/final batch counts were not supplied; the downloaded kit contains 30 sample patches, so these scores must not be treated as measurements on the hidden batches.

| Version | Batch | Missed commits | Simulated seconds | Container CPU seconds (user + system) | Official total | Wall seconds | Stdout bytes |
| --- | --- | ---: | ---: | --- | --- | --- | ---: |
| Published starter reference | Published contest baseline; batch size unspecified | Not separately published | Not separately published | Not separately published | 1614.1 s published score | Not published | Not published |
| Unchanged downloaded starter, one run | Official sample, 30 patches, 1,620 numbered tests | 0 / 30 | 1210.470 | Unmeasured / unverified | Unverified: container CPU was not measured | 0.208060281 container event interval; 20.60 complete `make sample`, including build | 259,440 |

The official scorer accepted all 30 JSON lines. Each patch selected all 1,620 tests exactly once across three nonempty workers. Worker test counts were 500, 510, and 610; each worker's integer-millisecond load was 34,349 ms. Thus each patch cost 34.349 + 3 × 2 = 40.349 s, and 30 × 40.349 = 1210.470 s, with no miss penalty. Stdout is below both decimal and binary interpretations of the 2 MB limit. The unchanged starter uses JSON whitespace; compact serialization is deferred to later implementation.

Output SHA-256: `036431e8fe704396e86b62921403dd70f2722bca9a3eaec1975850b59240b7cc`.

Observed scorer output:

```text
Simulated: 1210.470 s
Misses:    0 (0.000 s of the simulated time)
CPU:       not measured here. The simulated seconds above are exact. The board adds the CPU seconds your container used and takes the middle of 3 runs.
```

`/usr/bin/time` measured 0.22 user seconds and 0.33 system seconds for the host `make` process tree, including Docker clients and the host scorer. **Those are not container CPU seconds and are not added to the score.** The container was removed by the starter's `--rm`; per-container user/system accounting was not captured. Docker events give the start-to-die wall interval above, which is not CPU time. There is no measured CPU-inclusive official total, no three-run median, and no claimed rounded contest score from this single baseline run.

## Environment

| Item | Observed value |
| --- | --- |
| Windows | Microsoft Windows 11 Home Single Language, x64; build 26200; WSL reports Windows 10.0.26200.9711 |
| WSL | 2.6.1.0; Ubuntu distribution running as WSL version 2 |
| Linux | Ubuntu 24.04.4 LTS; kernel `6.6.87.2-microsoft-standard-WSL2`; x86_64 |
| Linux working user | UID/GID 1000 (`eshum`) |
| Host CPU / WSL memory | AMD Ryzen 9 5900HX; 16 logical CPUs visible; approximately 7.5 GiB RAM and 2 GiB swap |
| Host Python / make | Python 3.12.3; GNU Make 4.3 |
| Docker Desktop | 4.47.0 (206054), reachable from the Ubuntu WSL shell |
| Docker client / engine | 28.4.0 / 28.4.0; API 1.51; default context; linux/amd64 |
| containerd / runc | 1.7.27 / 1.2.5 |
| Pinned base | `python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90` |
| Built control image | `blast-radius-entry:latest`, linux/amd64; reported image ID `sha256:39d81ac352e2b6f01147b2011a6932548a992f4190157cba5f02cabb766e4f83` |
| Build config digest | `sha256:7fee3227c9b5801aa411fa4d21ba741e016a29e5f179956663e718962ff002b9` |
| Image reported size / Python | 43,079,070 bytes; Python 3.13.18 verified in an additional restricted container |
| Image command | No ENTRYPOINT; `CMD ["python", "/app/selector.py"]` |
| RTK | Windows RTK 0.44.2; subsequent external shell commands used its proxy; no RTK installed inside Ubuntu |

The baseline's Docker invocation applied `--platform linux/amd64`, no network, two CPUs, 4 GiB memory with equal memory-swap limit, 256 processes, a read-only root, a 64 MiB writable `/tmp`, dropped capabilities, no-new-privileges, UID/GID 65534, `HOME=/tmp`, and read-only mounts of only patches and the manifest. It completed with exit code 0. The Makefile has no explicit wall timeout; its observed container interval was below 180 s. This is only a 30-patch local sample check, not a 270 s final-batch validation. Build CPU/RAM/time caps were not imposed by the unchanged Makefile; clean capped submission builds belong to Phase 2.

## Inspection findings

- Manifest: top-level `tests` and `skipped`; 1,620 numbered entries across 58 test files, plus one unnumbered skipped entry. Every numbered entry has `number`, `id`, `file`, and `seconds`. Numbers are contiguous 0–1619, and pytest node IDs are unique. Runtime numbers and durations must come from the manifest.
- Patches: 30 standalone unified diffs, 35 changed-file sections and 35 hunks, 21,037 bytes total, no CRLF sequences. Standard git headers, old/new file paths, and old/new hunk coordinates are present. No patch was applied or rewritten. Later lookup normalization must leave the original diff bytes intact.
- Evaluation labels: the sample answer file has a top-level `commits` mapping with `failing` test-number lists and `kind`. The Makefile mounts neither this file nor the scorer into the selector container.
- Starter selection: reads `/data/tests.json`, schedules all tests once using descending recorded seconds and least-loaded of three workers, then emits that selection for every sorted patch filename. It does not inspect patch contents or run SQLGlot tests.
- Scorer: checks UTF-8, JSON/shape, known and unique commit IDs, worker/list and integer test-number types, known and unique tests, up to eight nonempty workers, and complete patch coverage. It checks that sample answer IDs agree with patch filenames. Stdout size and container limits are harness obligations rather than checks implemented by `score.py`; the baseline's byte count was measured separately.
- Arithmetic: simulated cost is peak worker milliseconds + 2,000 ms per nonempty worker + 300,000 ms per missed commit; total adds container user + system CPU in microseconds. A submission uses the median of three valid totals and half-up rounding to 0.1 s. `score.py` uses `floor(seconds * 1000 + 0.5)`; the specification says `round(seconds * 1000)`. With the shipped three-decimal manifest these agree, so no current result is affected. Keep the official scorer authoritative for future comparisons.
- No blocking conflict between the published brief and this Phase 1 request was found. Preserving the unchanged starter is intentional at this checkpoint; later selector output should follow the project's compact-JSON requirement.

## Commands and evidence

External shell commands were invoked from Windows through `rtk proxy wsl -d Ubuntu -- bash -lc '...'`; the following shows their Linux equivalents. The authoritative baseline command was exactly `make sample`, with external logging and timing only:

```bash
mkdir -p /home/eshum/Buildathon-Blast /home/eshum/blast-phase1-evidence
curl -fL --max-time 45 -D /tmp/blast-brief.headers \
  https://www.joinbuilders.org/buildathon/tracks/blast-radius \
  -o /tmp/blast-brief.html
curl -fL --max-time 90 \
  -D /home/eshum/blast-phase1-evidence/archive.headers \
  https://www.joinbuilders.org/buildathon/tracks/blast-radius/files/blast-radius-sample.tar.gz \
  -o /home/eshum/blast-phase1-evidence/blast-radius-sample.tar.gz
curl -fL --max-time 45 \
  -D /home/eshum/blast-phase1-evidence/scoring.headers \
  https://www.joinbuilders.org/buildathon/tracks/blast-radius/files/SCORING.md \
  -o /home/eshum/blast-phase1-evidence/published-SCORING.md
mkdir /home/eshum/Buildathon-Blast/starter
tar -xzf /home/eshum/blast-phase1-evidence/blast-radius-sample.tar.gz \
  -C /home/eshum/Buildathon-Blast/starter
cd /home/eshum/Buildathon-Blast/starter
cmp SCORING.md /home/eshum/blast-phase1-evidence/published-SCORING.md
/usr/bin/time \
  -f 'make_sample_wall_seconds=%e\nmake_client_user_seconds=%U\nmake_client_system_seconds=%S\nexit_status=%x' \
  -o /home/eshum/blast-phase1-evidence/make-sample.time \
  make sample \
  > /home/eshum/blast-phase1-evidence/make-sample.stdout \
  2> /home/eshum/blast-phase1-evidence/make-sample.stderr
```

The Makefile expanded this to:

```bash
docker build --platform linux/amd64 --tag blast-radius-entry .
docker run --rm --platform linux/amd64 --network none --cpus 2 \
  --memory 4096m --memory-swap 4096m --pids-limit 256 --read-only \
  --tmpfs /tmp:rw,size=64m,mode=1777 --cap-drop ALL \
  --security-opt no-new-privileges --user 65534:65534 --env HOME=/tmp \
  --volume /home/eshum/Buildathon-Blast/starter/sample/commits:/data/commits:ro \
  --volume /home/eshum/Buildathon-Blast/starter/sample/tests.json:/data/tests.json:ro \
  blast-radius-entry > /home/eshum/Buildathon-Blast/starter/output.jsonl
python3 score.py /home/eshum/Buildathon-Blast/starter/sample \
  /home/eshum/Buildathon-Blast/starter/sample/answers.json \
  /home/eshum/Buildathon-Blast/starter/output.jsonl
```

Other inspection commands: `wsl --list --verbose`, `wsl --version`, `uname -a`, `cat /etc/os-release`, `id`, `df -T /home/eshum`, `python3 --version`, `make --version`, `docker version`, `docker info`, `lscpu`, `free -h`, `docker image inspect blast-radius-entry`, and `docker events --since 30m --until 1s --filter image=blast-radius-entry --format json`. A small evaluation-only inspector in `.phase1/inspect_phase1.py` compared archive bytes, inspected manifest/patch structure, measured stdout, and called the unchanged scorer's `evaluate_run`; it is excluded from the submission context.

Evidence includes HTTP headers, the downloaded archive and brief HTML, the published scoring file, build/run stdout and stderr, host timing, Docker start/die events, Docker info/image inspection, per-file archive SHA-256 values, and `inspection.json`. Evidence is mirrored under the attached folder's ignored `.phase1/evidence/` for review. The original selector stdout remains `starter/output.jsonl`.

## Checkpoint and remaining limits

No source, Docker, or baseline-execution blocker remains. Container restrictions were exercised by the unchanged Makefile. Container CPU accounting, CPU-inclusive total, median-of-three timing, and hidden practice/final budget checks remain unverified. These gaps do not change the exact 1210.470 simulated sample seconds or the zero observed misses. Stopped before selector or scheduler implementation, reusable map generation, or Phase 2.


# Phase 2 — scheduler control, reusable maps, and file selection

Completed 2026-11-21 (Asia/Kolkata). The authoritative checkout remains
/home/eshum/Buildathon-Blast on WSL2 ext4. Its Windows review mirror is
C:/Users/eshum/OneDrive/Desktop/Buildathon-Blast. Phase 1's historical
single-run, CPU-unmeasured result above is unchanged; the new rows below use
complete container CPU accounting. No repository was published or submitted.
No line-level narrowing or independent holdout work was performed.

## Source access and pinned environment

The official brief was downloaded again with HTTP 200 to
/home/eshum/blast-phase2-evidence/brief.html from
https://www.joinbuilders.org/buildathon/tracks/blast-radius.
The original starter and bundled scoring specification from Phase 1 remain the
reference. All 39 archived starter files were rechecked byte-for-byte after
Phase 2: zero differences. The starter image and all-tests scheduler image
remain available as local controls.

Pinned source was downloaded successfully from
https://codeload.github.com/tobymao/sqlglot/tar.gz/eb11aec4be8cb2122afe713a4816662c3f0fb2fa
and extracted outside the submission tree at
/home/eshum/blast-bootstrap/sqlglot-eb11aec4be8cb2122afe713a4816662c3f0fb2fa.
Archive SHA-256:
93b2445f15f395b81c20556777ece19a6c7507df950f13fa9fac4a3be739af0d.
The regeneration script verifies this archive hash.

Bootstrap used the exact pinned Python base from Phase 1, installed the
unchanged official requirements.lock, and added coverage==7.10.7 from PyPI.
No SQLGlot source was installed from another revision. Reference pytest runs
used PYTHONPATH=/src, SKIP_INTEGRATION=0, no network, a two-CPU quota, 4 GiB
RAM, a 256-process limit, and two-CPU affinity (0,1). The upstream source
mount was read-only.

The clean uninstrumented full suite passed: 1620 passed, one skipped,
25,440 passing subtests; pytest wall 108.06 s, complete Docker-command wall
113.11 s. The successful instrumented full suite also passed with the same
counts; pytest wall 262.52 s, complete Docker-command wall 274.51 s.
These are base-revision reference runs, not runtime selector budget checks.

Two unsuccessful instrumentation attempts were retained separately and
excluded from the maps. The first lacked a multiprocessing main guard,
causing spawned processes to re-enter pytest; it was interrupted and fixed.
The next exposed host over-parallelism: process pools saw 16 logical CPUs
despite a two-CPU quota, and the 256-process/thread cgroup limit was hit
(pids.events max=28; no OOM kills). It was interrupted. Two-CPU affinity
fixed that issue; the final run recorded no pids-limit hits or test failures.

The final collector passes the submitting test context into reused
ProcessPoolExecutor tasks, combines child and parent coverage, records
collection and phase-specific coverage, and audits Python reads of repository
files. A separate two-test process-pool smoke run passed with 65 subtests
and verified the final collector writes its combined .coverage file.
The successful full run's parallel coverage files were combined using the
official coverage CLI; the collector now writes the same combined format
directly. Empty combined measurements are rejected by the map compiler.

Coverage process handling follows
https://coverage.readthedocs.io/en/7.10.7/subprocess.html .
The initial empty-map compile was detected by the join audit, discarded,
and replaced with maps compiled from the complete combined measurements.
It was not used in a scored container benchmark.

## Scheduler-only control before selection changes

The new scheduler was implemented, built, and benchmarked with every test
selected before file selection was added. It tries worker counts 1 through
min(8, selected test count), orders by descending round(seconds * 1000) and
ascending test number, and assigns to the least-loaded worker with ascending
worker-index ties. It minimizes peak load plus 2000 ms per nonempty worker,
with fewer workers preferred on equal cost. It emits [] for zero tests.

The 1620-test control chooses four workers, costing 36.817 simulated seconds
per patch, compared with the starter's three-worker 40.349 seconds.
The original starter selector and its scheduling implementation were preserved.

## Reusable maps and manifest join

The compact map contains only data derived from pinned source and its
reference test run. Its generator reads no sample manifest, patch, commit ID,
or expected answer. Runtime test numbers are joined by pytest node ID.
Manifest joining is a separate evaluation-side command.

| Measurement | Result |
| --- | ---: |
| Compressed base-map.json.gz | 1,834,646 bytes |
| Uncompressed compact JSON | 14,841,981 bytes |
| Base source file identities / hashes | 364 |
| Map node IDs | 1621 |
| Numbered manifest tests matched | 1620 / 1620 |
| Unmatched numbered node IDs | 0 |
| Numbered nodes without call coverage | 0 |
| Extra map nodes | 1 (the unnumbered skipped test) |
| Coverage contexts | 1684 |
| Collection file contexts | 59 |
| Function ranges | 5286 |
| Static reverse import edges | 1593 |
| Fixture relationships / node edges | 4 / 280 |
| Fixture resource-read edges | 35 |
| Base AST syntax errors | 0 |

Map SHA-256: 8c64c0b6f9a2fabc1407608f9fcd9537c657673374bf87b88238bcffa166153a.

A second map compilation from the same raw measurements was byte-identical.
The complete capture/compile workflow is reproducible through
tools/regenerate.sh; that full script was not rerun end-to-end after the
successful capture. A fresh capture can vary in observational coverage;
no claim of byte-identical coverage across independent captures is made.

All 1620 numbered tests have call-phase source coverage. No source lines
occurred directly in pytest's setup phase; unittest's per-test setup is
inside its call phase, and class setup is separately stored in the four
fixture contexts. One node has directly attributed teardown source lines.
Shared setup/teardown file dependencies are broadened to the whole test
file. Pytest-generated unittest class fixtures are joined to all class
members. Unknown external fixture contexts broaden to all nodes.

The map also includes per-node line intervals, function ranges, source hashes,
collection effects, observed resource reads, fixture membership and static
reverse imports. Phase 2 selection consults file identities only. It does not
use hunk line numbers, line intervals, or enclosing functions to narrow tests.

## Valid container benchmark results

All three runs per control/candidate passed the unchanged official scorer.
Container CPU is measured as the difference in user_usec + system_usec in an
exclusive retained parent cgroup, after each container and every process in it
has exited. The parent is in the Docker Desktop VM and remains after Docker
removes the child cgroup. No build, host scorer, Docker CLI, map generator, or
other workload runs in that parent. This closes Phase 1's CPU-accounting gap
for these fresh runs.

Scored containers use every starter runtime restriction, plus
--cgroup-parent=/blast-phase2-accounting for accounting only. No measurement
wrapper or extra process runs in the scored container. Each wall measurement
below is the host Docker run command, including startup/removal; it is kept
separate from container CPU.

| Version / run | Batch | Missed commits | Simulated seconds | Container user s | Container system s | Container CPU s | Official total s | Wall s | Stdout bytes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| unchanged-starter / 1 | sample 30 | 0 | 1210.470 | 0.098795 | 0.055983 | 0.154778 | 1210.624778 | 0.717993 | 259,440 |
| unchanged-starter / 2 | sample 30 | 0 | 1210.470 | 0.126851 | 0.025774 | 0.152625 | 1210.622625 | 0.529317 | 259,440 |
| unchanged-starter / 3 | sample 30 | 0 | 1210.470 | 0.102633 | 0.047701 | 0.150334 | 1210.620334 | 0.536250 | 259,440 |
| scheduler-control / 1 | sample 30 | 0 | 1104.510 | 0.169961 | 0.032028 | 0.201989 | 1104.711989 | 0.613327 | 210,840 |
| scheduler-control / 2 | sample 30 | 0 | 1104.510 | 0.161977 | 0.044215 | 0.206192 | 1104.716192 | 0.594188 | 210,840 |
| scheduler-control / 3 | sample 30 | 0 | 1104.510 | 0.155698 | 0.025516 | 0.181214 | 1104.691214 | 0.591266 | 210,840 |
| file-level / 1 | sample 30 | 0 | 417.095 | 0.545967 | 0.229210 | 0.775177 | 417.870177 | 1.051778 | 62,853 |
| file-level / 2 | sample 30 | 0 | 417.095 | 0.505151 | 0.251337 | 0.756488 | 417.851488 | 0.993003 | 62,853 |
| file-level / 3 | sample 30 | 0 | 417.095 | 0.549059 | 0.222977 | 0.772036 | 417.867036 | 0.999508 | 62,853 |
| file-level stress / 1 | simulated final 45 | 0 | 682.415 | 0.595142 | 0.268740 | 0.863882 | 683.278882 | 1.089187 | 103,299 |

| Version | Median of three valid totals, seconds | Rounded local score (half-up, 0.1 s) | Byte-identical stdout |
| --- | ---: | ---: | --- |
| unchanged-starter | 1210.622625 | 1210.6 | Yes |
| scheduler-control | 1104.711989 | 1104.7 | Yes |
| file-level | 417.867036 | 417.9 | Yes |

The published 1614.1-second baseline remains a separate contest reference.
The local recall-first order and official score order agree: file-level,
scheduler-only, then unchanged starter; every candidate had zero sample
misses. The file-level candidate is the best verified local sample version
and remains available as blast-file-selector. These sample results do not
establish unseen-patch recall or clear the Phase 3 independent holdout gate.

File-level output selected 14,433 tests in total across the 30 patches,
ranging from 1 to 1620 per patch. Twenty-two patches used bounded file
dependencies; eight used a full-suite fallback due to a dynamic-import
dependency. These were also the eight full-suite selections. Occupied worker
counts were 1, 2, or 4. File-level stdout was 62,853 bytes, comfortably below
2 MB, and byte-identical across the three containers.

The 30-patch sample runs used a 180-second external timeout and completed in
about one second. The 45-patch local stress batch repeated official sample
patches with fresh opaque filenames, retaining labels only in the evaluation
harness. It is explicitly a simulated final-size batch, not unseen commits or
a measured official final batch. Its one valid run used a 270-second timeout,
took 1.089187 s wall, emitted 103,299 bytes and missed zero of 45. No median
submission score is claimed for this single stress run. Hidden practice and
final batch counts, behavior and timing remain unverified.

## Fallbacks and limitations

The complete patch must parse as a supported UTF-8 unified diff, including
all sections and hunk lengths. Lookup paths normalize backslashes without
altering raw patch bytes. Binary/invalid encoding, malformed or truncated
hunks, unexpected trailing data, unsupported metadata, renames, additions,
deletions, unknown files, configuration, source AST errors, dynamic-import
dependencies, global collection dependencies, or no bounded observed
dependency select the full suite. Comment edits are not assumed harmless.

For supported edits, selection unions file-level execution/read dependencies,
collection effects, shared fixture relationships and reverse imports, and
includes tests in affected test files. If a numbered manifest node lacks a
map entry, all manifest tests from its file are retained conservatively.
Nodes without call coverage are always retained. A missing, corrupt or
wrong-revision map falls back to all tests. Empty manifests still emit [].

Coverage cannot prove all future execution paths, especially added behavior,
dynamic state, native-extension file reads or unobserved resources. The current
selector is deliberately broad, but zero misses on these samples does not
prove hidden recall. Independent patches and the mandatory Phase 3 gate remain
outstanding. No line-level narrowing has begun.

Eight focused checks pass for scheduler cost/ties/determinism, full patch
parsing, malformed/truncated/unknown patches, insertion-only hunks, separator
normalization with byte preservation, invalid maps, and missing node fallback.
The shell regeneration script passes bash -n, and Python files compile.

## Clean submission build and source audit

An early clean trial used the actual root Dockerfile and intended context
while the scheduler control was still the implementation. It passed in
30.45 seconds, including first startup of the dedicated BuildKit builder.
After the map and file selector were ready, another clean trial with
--no-cache --pull passed in 2.80 seconds.

The dedicated docker-container builder uses moby/buildkit:v0.24.0 from
Docker Hub. Its inspected configuration is cpu_quota=400000,
cpu_period=100000, memory=8589934592 and memory-swap=8589934592: four CPUs
and 8 GiB. An external timeout enforces 600 seconds, with a five-second kill
grace. Host WSL RAM is about 7.5 GiB, so actual available physical memory is
slightly below the configured build cap. Neither build needed that capacity.
The final build reused pinned base layers but no Dockerfile instruction cache.

The final image is linux/amd64, 44,916,925 reported bytes, image ID
sha256:6abdb53fab2da8bc197b9f516dd097bdab4c53929719ba7008438706cdc5d57b.
Its /app contains exactly selector.py, scheduler.py, impact.py, and
maps/base-map.json.gz. The map is readable by UID/GID 65534 (mode 0644).
No upstream checkout, raw coverage, tests, patches, labels, or evaluation
harness is copied into the submission image.

Download audit: the actual submission Dockerfile has no RUN/download steps
and references only the pinned Python image on Docker Hub. Local bootstrap
downloads were the official kit, the fixed SQLGlot revision, public PyPI
packages, and the fixed-tag BuildKit image. The runtime uses only the Python
standard library and no network. Root .gitignore/.dockerignore exclude the
starter, raw/evaluation directories, and instruction-only phase prompts;
all source checkouts and raw measurements remain outside the submission tree.

## Commands and evidence

Commands ran through Windows RTK's WSL proxy; the following are Linux commands
from /home/eshum/Buildathon-Blast unless indicated otherwise.

~~~bash
# Full pinned reference run (source checkout outside the submission).
docker run --rm --platform linux/amd64 --network none --cpus 2 \
  --cpuset-cpus 0,1 --memory 4096m --memory-swap 4096m --pids-limit 256 \
  -e SKIP_INTEGRATION=0 -e PYTHONPATH=/src \
  -v /home/eshum/blast-bootstrap/sqlglot-eb11aec4be8cb2122afe713a4816662c3f0fb2fa:/src:ro \
  blast-map-bootstrap python -m pytest tests -q -p no:cacheprovider

# Reusable complete capture and map-generation workflow.
bash tools/regenerate.sh /home/eshum/blast-regeneration

# Actual compilation used the successful raw run:
docker run --rm --platform linux/amd64 --network none --cpus 2 \
  --memory 4096m --memory-swap 4096m --pids-limit 256 \
  -v /home/eshum/blast-bootstrap/sqlglot-eb11aec4be8cb2122afe713a4816662c3f0fb2fa:/src:ro \
  -v /home/eshum/Buildathon-Blast/tools:/tools:ro \
  -v /home/eshum/blast-phase2-evidence/raw:/raw \
  -v /home/eshum/Buildathon-Blast/maps:/maps \
  blast-coverage-bootstrap python /tools/generate_maps.py --source /src --raw /raw --out /maps
python3 tools/check_maps.py --map maps/base-map.json.gz \
  --manifest starter/sample/tests.json \
  --out /home/eshum/blast-phase2-evidence/manifest-join.json

# Capped builder setup and actual final clean trial.
docker buildx create --name blast-phase2-local --driver docker-container \
  --driver-opt image=moby/buildkit:v0.24.0 --driver-opt memory=8g \
  --driver-opt memory-swap=8g --driver-opt cpu-period=100000 \
  --driver-opt cpu-quota=400000
timeout --signal=TERM --kill-after=5s 600s docker buildx build \
  --builder blast-phase2-local --platform linux/amd64 --no-cache --pull \
  --load --tag blast-file-selector .

python3 tools/benchmark.py --image blast-radius-entry --version unchanged-starter
python3 tools/benchmark.py --image blast-scheduler-control --version scheduler-control --mode all
python3 tools/benchmark.py --image blast-file-selector --version file-level --mode file
python3 tools/benchmark.py --image blast-file-selector --version simulated-final45 \
  --mode file --sample /home/eshum/blast-phase2-evidence/stress45 --runs 1 --timeout 270
make test
~~~

The successful capture used the first reference command's restrictions plus
BLAST_RAW_DIR=/raw, read-only /tools, writable external /raw, and
python /tools/collect_coverage.py; an external 1200-second limit bounded map
capture. The exact scored Docker commands, before/after cgroup counters,
individual outputs and hashes are stored in the benchmark JSON files.

Evidence is at /home/eshum/blast-phase2-evidence, including successful and
unsuccessful run logs, raw coverage, compiler/join reports, build logs and
resource inspection, benchmark JSON, and output files. Only compact maps,
scripts, code, tests and documentation belong in Git. A review subset of
evidence is mirrored under the ignored Windows .phase2/evidence directory.

## Phase 2 checkpoint

Scheduler control, maps, manifest join, file-level selection and the capped
clean build are complete. No blocking source, dependency, Docker or test
failure remains. Independent holdout recall, hidden batch budgets and final
packaging are unverified and intentionally deferred. Stop here before
line-level narrowing.


## Local repository size and handoff

Git was initialized locally for Phase 2 so the compact map and generation
scripts can be preserved together. No remote is configured. Since Ubuntu had
no Git author identity, this repository uses the local-only identity
Codex <codex@local.invalid>; global Git configuration was not changed.

The tracked submission snapshot contains 23 files totaling 1,918,766 bytes,
below the 20,000,000-byte cap. This measures file contents, excluding .git,
the ignored starter, evaluation artifacts, raw coverage and external source.
The map itself is 1,834,646 bytes. Git ignore checks confirm that the starter's
selector, sample labels, phase prompts and local evidence are excluded.
The staged diff has no whitespace errors. The local Phase 2 commit is the
handoff checkpoint; obtain its SHA with git rev-parse HEAD.

All implementation and map files are mirrored for review in the attached
Windows folder. Continue execution and Git operations from the Linux
checkout. The clean final image and the unchanged controls remain available
locally. No Phase 3 or final submission packaging was performed.
