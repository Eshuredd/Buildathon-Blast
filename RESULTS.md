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
