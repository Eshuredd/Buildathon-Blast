# RWX Blast Radius — Phase 2

A deterministic file-level test selector for SQLGlot at
eb11aec4be8cb2122afe713a4816662c3f0fb2fa. This is a local Phase 2 candidate;
independent holdout verification and final packaging have not been performed.

Run from the WSL2 Linux filesystem checkout at /home/eshum/Buildathon-Blast.

~~~bash
make test
make sample
make control
~~~

The starter/ directory is the unchanged official benchmark and is excluded from
Git and the submission Docker context. Its score.py supplies local scoring.
Download the official kit from the [track brief](https://www.joinbuilders.org/buildathon/tracks/blast-radius)
if setting up another checkout; unpack it into an empty starter/.

## Runtime

/data/tests.json supplies pytest node IDs, test numbers and recorded seconds.
Each patch is validated in full as a supported unified diff. Lookup paths use
forward slashes; the original patch bytes are never modified.

Selection unions file coverage from setup, call, teardown, collection, fixture
lifecycles, subprocess tasks and observed repository file reads. It expands
through static reverse imports and includes affected test files. Missing mapped
nodes broaden their entire test file. Unobserved tests are always retained.
Malformed or unsupported patches, additions, deletions, renames, unknown files,
configuration, dynamic imports, global collection dependencies, or no bounded
observed dependency select all tests. Comments receive the same treatment as
other edits. The runtime does not apply patches or run pytest.

The line coverage and function ranges in the map are collected for later work.
**Phase 2 selection only uses file identities**, without using hunk lines or
function ranges to narrow.

Scheduling tries one through eight workers (bounded by the test count), sorts
by descending integer-millisecond duration then ascending test number, and
assigns each test to the least-loaded worker, breaking ties by worker index.
It minimizes peak load plus 2,000 ms per occupied worker, preferring fewer
workers on an equal cost. Identical selected sets reuse schedules within a
batch. Output is compact JSON lines; logs go to stderr. An empty manifest
produces workers: [].

The container only includes the pinned Python base, runtime code and the compact
map. It has no source checkout, raw coverage, sample patches, or labels. Runtime
network access is unnecessary.

## Reproduce maps

~~~bash
bash tools/regenerate.sh /home/eshum/blast-regeneration
~~~

The target cache must be outside this checkout and must not already contain a
raw/ directory. Bootstrap downloads the fixed SQLGlot revision and installs
the unchanged starter requirements.lock plus coverage==7.10.7 in the pinned
Python image. Reference pytest runs have SKIP_INTEGRATION=0, no runtime
network, a two-CPU quota, two-CPU affinity, 4 GiB RAM, and a 256-process cap.
The affinity prevents Python's process pools from using all host-visible CPUs.
Adjust affinity only to another pair of valid host CPUs if 0 and 1 are absent.

The collector instruments all pytest phases and collection, tracks Python file
reads, records fixture relationships, and attributes process-pool tasks to
their submitting test. Pytest-generated unittest class fixtures are joined
back to every member of their class; unknown external fixtures broaden to all
nodes. Child process data is combined with parent coverage. The compiler takes
only pinned source and raw measurements, never runtime test numbers, patches,
or expected labels. It stores maps by pytest node ID.

Coverage is observational and cannot prove every possible dependency. Static
imports and broad fallbacks reduce that risk; Phase 3 must independently verify
recall before packaging. Native-extension internals and non-Python file reads
are not line traced. Unseen data paths and import behavior remain a risk.

The tools/benchmark.py evaluation harness targets this Windows/WSL Docker Desktop
environment. It calls the official scorer and uses an exclusive, retained
parent cgroup in the Docker VM to measure complete user + system CPU after
each scored container exits. It does not enter the submission image.
See RESULTS.md for commands, all measurements, and limits.
