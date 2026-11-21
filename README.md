# RWX Blast Radius

A deterministic test selector for SQLGlot at
eb11aec4be8cb2122afe713a4816662c3f0fb2fa. The verified selector reference is
cda723539a174fc94444474fc7c69f35927763bb. It passed the independent
holdout with zero missed failing commits across four patches.

Run the following from the checkout root on a Linux filesystem. The reference
environment is WSL2 Ubuntu with Docker Desktop and linux/amd64 images.

~~~bash
make test
make sample
make control
~~~

The starter/ directory is the unchanged official benchmark and is excluded from
Git and the submission Docker context. Its score.py supplies local scoring.
Download the official kit from the [track brief](https://www.joinbuilders.org/buildathon/tracks/blast-radius)
and unpack it into an empty starter/ directory.

make sample runs the submission with the official runtime restrictions and
prints simulated seconds and misses. make control runs the all-tests
scheduler control. To compute CPU-inclusive local scores on WSL with Docker
Desktop, use the benchmark harness with the unchanged starter scorer.

~~~bash
make build IMAGE=blast-review
python3 tools/benchmark.py --root "$PWD" --image blast-review --version review-sample \
  --evidence /tmp/blast-review
~~~

Each total adds container user and system CPU to simulated time. Simulated
time is the busiest worker load per patch plus two seconds per occupied worker
and a 300-second penalty per missed commit. The local contest-style result is
the median of three valid totals, rounded half-up to 0.1 seconds.

## Runtime

/data/tests.json supplies pytest node IDs, test numbers and recorded seconds.
Each patch is validated in full as a supported unified diff. Lookup paths use
forward slashes; the original patch bytes are never modified.

The file-level fallback unions file coverage from setup, call, teardown, collection, fixture
lifecycles, subprocess tasks and observed repository file reads. It expands
through static reverse imports and includes affected test files. Missing mapped
nodes broaden their entire test file. Unobserved tests are always retained.
Malformed or unsupported patches, additions, deletions, renames, unknown files,
configuration, dynamic imports, global collection dependencies, or no bounded
observed dependency select all tests. Comments receive the same treatment as
other edits. The runtime does not apply patches or run pytest.

The default selector narrows only certified edits to a single return in each
hunk. It reads old-side hunk coordinates and checks the original statement or
context line against a digest derived from the pinned source. The permitted
forms are a same-indent return replacement and a same-indent return insertion
immediately before a verified return. The replacement expression uses simple
syntax and can refer only to names already present in the original expression.

The selection includes coverage of the whole enclosing function, including
shared setup and teardown. It also includes matching collection and fixture
coverage, recorded source readers, and unresolved manifest nodes. The selector
uses file-level rules if any hunk is ineligible or coverage cannot bound the
function. File-level rules broaden through static imports and may select the
full suite. Use the runtime option --mode file to reproduce file-level behavior.

Scheduling tries one through eight workers (bounded by the test count), sorts
by descending integer-millisecond duration then ascending test number, and
assigns each test to the least-loaded worker, breaking ties by worker index.
It minimizes peak load plus 2,000 ms per occupied worker, preferring fewer
workers on an equal cost. Identical selected sets reuse schedules within a
batch. Output is compact JSON lines; logs go to stderr. An empty manifest
produces workers: [].

The root Dockerfile copies four runtime modules and two compact maps onto the
pinned Python 3.13 base. The selector reads patches and the test manifest from
read-only mounts and runs with networking disabled.

## Reproduce maps

~~~bash
CACHE=/tmp/blast-regeneration
bash tools/regenerate.sh "$CACHE"
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
or expected labels. It stores coverage maps by pytest node ID. To regenerate
the return anchors after compiling the base map, run the following with WSL
Python 3.12 and the same pinned source directory.

~~~bash
python3 tools/generate_line_sites.py \
  --source "$CACHE/sqlglot-eb11aec4be8cb2122afe713a4816662c3f0fb2fa" \
  --base-map maps/base-map.json.gz --out maps/return-sites.json.gz
~~~

Coverage is observational and cannot prove every possible dependency. Static
imports and broad fallbacks reduce that risk. Coverage of native extensions,
non-Python file reads, and unobserved execution paths is limited.

The tools/benchmark.py evaluation harness targets this Windows/WSL Docker Desktop
environment. It calls the official scorer and uses an exclusive, retained
parent cgroup in the Docker VM to measure complete user + system CPU after
each scored container exits. It does not enter the submission image.
## Verification

The Phase 3 holdout covered added code, a fixture change, an import-time
failure, and an unaffected edit. The selector missed zero of three failing
commits at a median total of 78.7 seconds. Four patches provide limited
evidence for unseen contest commits. See [RESULTS.md](RESULTS.md) for
the official sample, local runtime checks, image audit, and build measurements.

## Credits and license

The track, starter, and official scorer are provided by RWX and Builders
Buildathon. SQLGlot is developed by Toby Mao and the SQLGlot contributors.
Map generation uses pytest and coverage.py. This project's code is available
under the [MIT License](LICENSE). Upstream projects retain their own licenses.
