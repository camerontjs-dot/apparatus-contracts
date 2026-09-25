#!/bin/sh
set -eu

: "${ERS05_OUTPUT_ROOT:?qualification output directory required}"
: "${ERS05_TEMP_ROOT:?qualification temporary directory required}"
: "${ERS05_CONTROL_ROOT:?protected control worktree root required}"
: "${ERS05_MAINFRAME_ROOT:?MainFrame root required}"
: "${ERS05_APPARATUS_ROOT:?successor checkout required}"
: "${ERS05_APPARATUS_WORKBENCH:?apparatus workbench required}"
: "${ERS05_PR148_ROOT:?frozen PR 148 checkout required}"
: "${ERS05_PR149_ROOT:?frozen PR 149 checkout required}"
: "${ERS05_FROZEN_CHECKOUTS_ROOT:?frozen source checkouts required}"
: "${ERS05_FIXTURES_ROOT:?frozen fixtures required}"
: "${ERS05_SCIENTIFIC_SANDBOX:?scientific sandbox required}"
: "${ERS05_RUNTIME_ROOT:?frozen runtime required}"
: "${ERS05_CANARY_ROOT:?protected canary directory required}"
: "${ERS05_PROFILE:?write-deny profile required}"
: "${ERS05_RUNTIME_PYTHON:?frozen runtime Python required}"
: "${ERS05_GATE_SCRIPT:?strengthened gate script required}"
: "${ERS05_SOURCE_COMMIT:?frozen source commit required}"

if [ ! -d "$ERS05_OUTPUT_ROOT" ] || [ ! -d "$ERS05_TEMP_ROOT" ] || [ ! -d "$ERS05_CANARY_ROOT" ]; then
    echo "qualification output, temp, and canary directories must exist before launch" >&2
    exit 2
fi

exec sandbox-exec \
    -D "ERS05_ALLOWED_OUTPUT=$ERS05_OUTPUT_ROOT" \
    -D "ERS05_ALLOWED_TEMP=$ERS05_TEMP_ROOT" \
    -D "ERS05_MAINFRAME_ROOT=$ERS05_MAINFRAME_ROOT" \
    -D "ERS05_APPARATUS_ROOT=$ERS05_APPARATUS_ROOT" \
    -D "ERS05_APPARATUS_WORKBENCH=$ERS05_APPARATUS_WORKBENCH" \
    -D "ERS05_PR148_ROOT=$ERS05_PR148_ROOT" \
    -D "ERS05_PR149_ROOT=$ERS05_PR149_ROOT" \
    -D "ERS05_CONTROL_ROOT=$ERS05_CONTROL_ROOT" \
    -D "ERS05_FROZEN_CHECKOUTS_ROOT=$ERS05_FROZEN_CHECKOUTS_ROOT" \
    -D "ERS05_FIXTURES_ROOT=$ERS05_FIXTURES_ROOT" \
    -D "ERS05_SCIENTIFIC_SANDBOX=$ERS05_SCIENTIFIC_SANDBOX" \
    -D "ERS05_RUNTIME_ROOT=$ERS05_RUNTIME_ROOT" \
    -D "ERS05_CANARY_ROOT=$ERS05_CANARY_ROOT" \
    -f "$ERS05_PROFILE" \
    /usr/bin/env TMPDIR="$ERS05_TEMP_ROOT" GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1 \
    "$ERS05_RUNTIME_PYTHON" "$ERS05_GATE_SCRIPT" \
    --repo "$ERS05_APPARATUS_ROOT" \
    --source-commit "$ERS05_SOURCE_COMMIT" \
    --pr148-root "$ERS05_PR148_ROOT" \
    --pr149-root "$ERS05_PR149_ROOT" \
    --wrong-root "$ERS05_CONTROL_ROOT/wrong-root" \
    --wrong-disposition "$ERS05_CONTROL_ROOT/wrong-disposition" \
    --output-root "$ERS05_OUTPUT_ROOT" \
    --temp-root "$ERS05_TEMP_ROOT" \
    --control-root "$ERS05_CONTROL_ROOT" \
    --mainframe-root "$ERS05_MAINFRAME_ROOT" \
    --apparatus-workbench "$ERS05_APPARATUS_WORKBENCH" \
    --frozen-checkouts "$ERS05_FROZEN_CHECKOUTS_ROOT" \
    --fixtures-root "$ERS05_FIXTURES_ROOT" \
    --sandbox-root "$ERS05_SCIENTIFIC_SANDBOX" \
    --runtime-root "$ERS05_RUNTIME_ROOT" \
    --canary-root "$ERS05_CANARY_ROOT" \
    --profile "$ERS05_PROFILE" \
    --result "$ERS05_OUTPUT_ROOT/QUALIFICATION.json"
