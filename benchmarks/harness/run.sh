#!/usr/bin/env bash
# Name: Benchmark runner
# Purpose: Runs one benchmark arm in a disposable workspace, records session, scope, and statistics artifacts, and executes the task verification command.
# Usage: ./benchmarks/harness/run.sh --arm baseline|optimized|coordinator-slim|direct-slim|tools-on-demand --task <file.json> [--workspace DIR] [--run-id ID] [--dry-run]
# Arguments: --arm selects the configuration and agent, --task selects the task definition, --workspace sets the target repository root, --run-id sets the output directory name, --dry-run prints the command.
# Environment: Requires bash, python3, and git. opencode is required to execute a run but not for --dry-run. OPENCODE_BENCH_MODEL must be a provider/model#variant identifier for execution.
# Outputs: Writes meta.json, session.jsonl, stats.json, run-stats.json, export.json, verification.log, status.txt, diff.patch, diff-stat.txt, and notes.md under benchmarks/results/<run-id>.
# Side effects: Executes opencode with --auto in a non-interactive session; use a disposable checkout.
# References: docs/benchmarks/methodology.md, benchmarks/tasks/*.json
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARM=""
TASK=""
WORKSPACE=""
CONFIG_COPY=0
RUN_ID=""
DRY=0

# Function: usage
# Description: Prints the command-line usage.
# Arguments: None.
# Returns: None.
# Side effects: Writes to standard output.
usage() {
  echo "usage: $0 --arm baseline|optimized|coordinator-slim|direct-slim|tools-on-demand --task <file.json> [--workspace DIR] [--run-id ID] [--dry-run]"
  echo "environment: OPENCODE_BENCH_MODEL=provider/model#variant is required for execution"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arm) ARM="${2:-}"; shift 2 ;;
    --task) TASK="${2:-}"; shift 2 ;;
    --workspace) WORKSPACE="${2:-}"; shift 2 ;;
    --run-id) RUN_ID="${2:-}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown: $1"; usage; exit 2 ;;
  esac
done

[[ -n "$ARM" && -n "$TASK" ]] || { usage; exit 2; }
[[ -f "$TASK" ]] || { echo "task not found: $TASK"; exit 2; }
command -v python3 >/dev/null || { echo "python3 not found"; exit 2; }
if [[ "$DRY" != "1" ]]; then
  command -v opencode >/dev/null || { echo "opencode not found"; exit 2; }
fi

IFS=$'\t' read -r TASK_ID PROMPT VERIFY MAX_WALL WORKDIR < <(python3 - "$TASK" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    task = json.load(handle)
print(
    "\t".join(
        [
            str(task["id"]),
            task["prompt"].replace("\n", " "),
            task["verification"],
            str(task.get("max_wall_time_seconds", 900)),
            task.get("working_directory", "."),
        ]
    )
)
PY
)

WORKSPACE="${WORKSPACE:-$ROOT}"
[[ -d "$WORKSPACE" ]] || { echo "working directory not found: $WORKSPACE"; exit 2; }
PROJECT_DIR="$WORKSPACE/$WORKDIR"
[[ -d "$PROJECT_DIR" ]] || { echo "working directory not found: $PROJECT_DIR"; exit 2; }

RUN_ID="${RUN_ID:-$ARM-$TASK_ID-$(date +%Y%m%d-%H%M%S)}"
OUT="$ROOT/benchmarks/results/$RUN_ID"
if [[ -e "$OUT" ]]; then
  echo "refusing to overwrite: $OUT"
  exit 2
fi

case "$ARM" in
  baseline)
    CONFIG="$ROOT/benchmarks/baseline/opencode.json"
    AGENT="build"
    ;;
  optimized)
    CONFIG="$WORKSPACE/.opencode/opencode.jsonc"
    AGENT="coordinator"
    ;;
  coordinator-slim)
    CONFIG="$ROOT/benchmarks/arms/slim.jsonc"
    CONFIG_COPY=1
    AGENT="coordinator"
    ;;
  direct-slim)
    CONFIG="$ROOT/benchmarks/arms/slim.jsonc"
    CONFIG_COPY=1
    AGENT="backend-developer"
    ;;
  tools-on-demand)
    CONFIG="$ROOT/benchmarks/arms/tools-on-demand.jsonc"
    CONFIG_COPY=1
    AGENT="coordinator"
    ;;
  *) echo "unknown arm: $ARM"; exit 2 ;;
esac

if [[ "$ARM" != "baseline" ]]; then
  if [[ ! -f "$CONFIG" ]]; then
    echo "arm $ARM requires $CONFIG (run the installer or add the benchmark config)"
    exit 2
  fi
  if [[ ! -f "$WORKSPACE/.opencode/agents/$AGENT.md" ]]; then
    echo "arm $ARM requires $WORKSPACE/.opencode/agents/$AGENT.md (run the installer)"
    exit 2
  fi
fi

if [[ "$CONFIG_COPY" == "1" && "$DRY" != "1" ]]; then
  mkdir -p "$WORKSPACE/.opencode"
  cp "$CONFIG" "$WORKSPACE/.opencode/opencode.jsonc"
  CONFIG="$WORKSPACE/.opencode/opencode.jsonc"
fi

COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
TARGET_COMMIT="$(git -C "$WORKSPACE" rev-parse HEAD 2>/dev/null || echo unknown)"
MODEL="${OPENCODE_BENCH_MODEL:-}"
if [[ "$DRY" != "1" && -z "$MODEL" ]]; then
  echo "OPENCODE_BENCH_MODEL is required, for example provider/model or provider/model#variant"
  exit 2
fi

echo "arm=$ARM task=$TASK_ID run=$RUN_ID"
echo "config=$CONFIG agent=$AGENT commit=$COMMIT workdir=$WORKDIR max_wall=${MAX_WALL}s"

if [[ "$DRY" == "1" ]]; then
  if [[ "$CONFIG_COPY" == "1" ]]; then
    echo "would copy: $CONFIG -> $WORKSPACE/.opencode/opencode.jsonc"
  fi
  echo "would run: XDG_CONFIG_HOME=<temp> OPENCODE_CONFIG=$CONFIG opencode --standalone run --agent $AGENT --model ${MODEL:-<provider/model>} --auto --format json <prompt> in $PROJECT_DIR"
  exit 0
fi

mkdir -p "$OUT"

BENCH_HOME="$(mktemp -d "${TMPDIR:-/tmp}/toolwright-bench.XXXXXX")"
trap 'rm -rf "$BENCH_HOME"' EXIT
export XDG_CONFIG_HOME="$BENCH_HOME/config"
mkdir -p "$XDG_CONFIG_HOME"

python3 - "$OUT/meta.json" "$RUN_ID" "$ARM" "$TASK" "$TASK_ID" "$COMMIT" "$MODEL" "$AGENT" "$MAX_WALL" "$WORKDIR" "$WORKSPACE" "$TARGET_COMMIT" <<'PY'
import datetime
import json
import subprocess
import sys

out, run_id, arm, task, task_id, commit, model, agent, max_wall, workdir, workspace, target_commit = sys.argv[1:]
json.dump(
    {
        "run_id": run_id,
        "arm": arm,
        "task_file": task,
        "task_id": task_id,
        "working_directory": workdir,
        "workspace": workspace,
        "commit": commit,
        "target_commit": target_commit,
        "model": model,
        "agent": agent,
        "max_wall_time_seconds": int(max_wall),
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "opencode_version": subprocess.run(
            ["opencode", "--version"], capture_output=True, text=True, check=False
        ).stdout.strip(),
    },
    open(out, "w", encoding="utf-8"),
    indent=2,
)
PY

cd "$PROJECT_DIR"

export XDG_CONFIG_HOME
export OPENCODE_CONFIG="$CONFIG"

START=$(date +%s)
set +e
python3 "$ROOT/scripts/benchmarking/run_with_timeout.py" "$MAX_WALL" -- \
  opencode --standalone run --agent "$AGENT" --model "$MODEL" --auto --format json "$PROMPT" \
  > "$OUT/session.jsonl" 2> "$OUT/session.err"
RUN_RC=$?
set -e
END=$(date +%s)

set +e
git -C "$PROJECT_DIR" status --short --untracked-files=all -- . > "$OUT/status.txt" 2> "$OUT/status.err"
git -C "$PROJECT_DIR" diff -- . > "$OUT/diff.patch" 2> "$OUT/diff.err"
git -C "$PROJECT_DIR" diff --stat -- . > "$OUT/diff-stat.txt" 2>> "$OUT/diff.err"
set -e

set +e
opencode stats --json --cost --project . > "$OUT/stats.json" 2> "$OUT/stats.err"
STATS_RC=$?

SID="$(python3 - "$OUT/session.jsonl" <<'PY2'
import re
import sys

try:
    text = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
except FileNotFoundError:
    text = ""
ids = re.findall(r"ses_[A-Za-z0-9]+", text)
print(ids[-1] if ids else "")
PY2
)"
if [[ -n "$SID" ]]; then
  opencode session export --sanitize "$SID" > "$OUT/export.json" 2> "$OUT/export.err"
  EXPORT_RC=$?
else
  echo "no session id found in session.jsonl; export skipped" > "$OUT/export.err"
  : > "$OUT/export.json"
  EXPORT_RC=0
fi

bash -lc "$VERIFY" > "$OUT/verification.log" 2>&1
VERIFY_RC=$?
set -e

python3 "$ROOT/scripts/benchmarking/summarize_session.py" "$OUT/session.jsonl" "$OUT/run-stats.json"

python3 - "$OUT/meta.json" "$RUN_RC" "$STATS_RC" "$EXPORT_RC" "$VERIFY_RC" "$START" "$END" <<'PY'
import datetime
import json
import sys

path, run_rc, stats_rc, export_rc, verify_rc, start, end = sys.argv[1:]
with open(path, encoding="utf-8") as handle:
    data = json.load(handle)
data.update(
    {
        "run_exit": int(run_rc),
        "stats_exit": int(stats_rc),
        "export_exit": int(export_rc),
        "verification_exit": int(verify_rc),
        "wall_time_seconds": int(end) - int(start),
        "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
)
json.dump(data, open(path, "w", encoding="utf-8"), indent=2)
PY

cat > "$OUT/notes.md" <<EOF
# $RUN_ID

- arm: $ARM
- task: $TASK_ID
- agent: $AGENT
- working directory: $WORKDIR
- run exit: $RUN_RC
- verification exit: $VERIFY_RC
- wall time: $((END-START))s
- wall limit: ${MAX_WALL}s

## Fill in

- correctness (tests + rubric):
- rework / follow-up prompts:
- human interventions:
- residual risks:
EOF

echo "artifacts: $OUT"
echo "run_exit=$RUN_RC verification_exit=$VERIFY_RC wall=$((END-START))s"
[[ "$VERIFY_RC" == "0" ]] || echo "VERIFICATION FAILED"
