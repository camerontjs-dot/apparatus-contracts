#!/usr/bin/env python3
"""Operator-only pre-exposure generator. Does NOT qualify or auto-discover pins."""
import argparse
import datetime
import hashlib
import json
import subprocess
from pathlib import Path
from identity import BASE, HERE, REPO, inventory, validate_pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pins-path', type=Path, required=True, help='external controller-only exact runtime pins')
    parser.add_argument('--prepared-commit', required=True)
    parser.add_argument('--frozen-at', required=True, help='explicit ISO UTC timestamp, before any exposure')
    args = parser.parse_args()
    def git(*command):
        return subprocess.check_output(['git', '-C', str(REPO), *command]).decode().strip()
    if git('rev-parse', 'HEAD') != args.prepared_commit or git('status', '--porcelain', '--untracked-files=all'):
        raise SystemExit('Commit the complete reviewed preparation first; clean worktree required.')
    subprocess.run(['git', '-C', str(REPO), 'merge-base', '--is-ancestor', BASE, args.prepared_commit], check=True)
    changed = git('diff', '--name-only', BASE, args.prepared_commit).splitlines()
    if not all(x.startswith(str(HERE.relative_to(REPO)) + '/') for x in changed):
        raise SystemExit('Only the new successor directory may differ from base')
    when = datetime.datetime.fromisoformat(args.frozen_at)
    if when.utcoffset() != datetime.timedelta(0):
        raise SystemExit('UTC freeze timestamp required')
    if args.pins_path.resolve().is_relative_to(REPO):
        raise SystemExit('Runtime pins must stay outside the public repository')
    pin_bytes = args.pins_path.read_bytes()
    pins = json.loads(pin_bytes)
    validate_pins(pins)
    files = inventory()
    tracked = set(git('ls-files').splitlines())
    if not set(files) <= tracked:
        raise SystemExit('Every frozen file must be tracked in the preparation commit')
    obj = {'schema': 'cal-fixed-ollama-launcher-freeze/2',
           'experiment_id': 'cal-fixed-ollama-public-synthetic-rc1-20261009',
           'state': 'FROZEN_BEFORE_EXPOSURE', 'prepared_commit': args.prepared_commit,
           'base_commit': BASE, 'frozen_at': args.frozen_at,
           'pins_sha256': hashlib.sha256(pin_bytes).hexdigest(),
           'public_pins': {
               'image_ref': pins['image_ref'], 'image_id': pins['image_id'],
               'docker_engine': pins['docker_engine'], 'image_architecture': pins['image_architecture'],
               'worker_python_version': pins['worker_python_version'],
               'provider_binary_sha256': pins['provider_binary']['sha256'],
               'model_manifest_sha256': pins['model_manifest']['sha256'],
           },
           'frozen_files': files, 'model_inference_calls_authorized': 0,
           'owner': 'camerontjs-dot/apparatus-contracts#173',
           'first_failure_rule': 'terminal; no rerun or repair; owned cleanup only',
           'candidate_identity': 'separate committed HEAD plus externally supplied FREEZE.json SHA-256',
           'expected_outcomes_file': 'PROTOCOL.md', 'source_informed': True}
    with (HERE / 'FREEZE.json').open('x') as stream:
        stream.write(json.dumps(obj, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    main()
