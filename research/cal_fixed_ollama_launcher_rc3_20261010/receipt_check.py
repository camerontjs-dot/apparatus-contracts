"""Read-back custody validator; no imports from runner or adapter, no execution.

Same-controller, code-isolated checking; not independent authorship or attestation.
"""
import datetime
import hashlib
import json
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check(root, inventory, commands, tools, earliest, latest):
    root = Path(root)
    observed = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    if observed != set(inventory):
        raise ValueError('RECEIPT_INVENTORY_MISMATCH')
    for name, record in inventory.items():
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('NONREGULAR_RECEIPT')
        raw = path.read_bytes()
        if len(raw) != record['bytes'] or sha(raw) != record['sha256']:
            raise ValueError('RECEIPT_BYTES_MISMATCH:' + name)
    lower, upper = map(datetime.datetime.fromisoformat, (earliest, latest))
    def times(obj):
        start, end = map(datetime.datetime.fromisoformat, (obj['started_at'], obj['ended_at']))
        if not lower <= start <= end <= upper:
            raise ValueError('INVALID_RECEIPT_TIME')
    for number, expected in enumerate(commands, 1):
        directory = root / f'command-{number:03}'
        obj = json.loads((directory / 'receipt.json').read_bytes())
        if obj != expected or obj['serial'] != number or not obj['argv']:
            raise ValueError('COMMAND_METADATA_DRIFT')
        times(obj)
        if type(obj['exit_code']) is not int or type(obj['timed_out']) is not bool:
            raise ValueError('COMMAND_OUTCOME_MISSING')
        for stream in ('stdin', 'stdout', 'stderr'):
            if sha((directory / stream).read_bytes()) != obj[stream + '_sha256']:
                raise ValueError('COMMAND_STREAM_DRIFT')
    for number, expected in enumerate(tools, 1):
        obj = json.loads((root / f'tool-{number:03}.response.json').read_bytes())
        if obj != expected or sha((root / f'tool-{number:03}.request').read_bytes()) != obj['request_sha256']:
            raise ValueError('TOOL_RECEIPT_DRIFT')
        times(obj)
        if obj['expected_refusal'] and (obj['command_before'] != obj['command_after'] or obj['host_process_before'] != obj['host_process_after'] or
                obj['status'] != 'REFUSED' or obj['reason'] != obj['expected_refusal']):
            raise ValueError('DISPATCH_OCCURRED_BEFORE_REFUSAL')
    if (root / 'Q03.http-receipt.json').exists():
        http = json.loads((root / 'Q03.http-receipt.json').read_bytes())
        times(http)
        for kind in ('request', 'response'):
            if sha((root / f'Q03.{kind}.json').read_bytes()) != http[kind + '_sha256']:
                raise ValueError('HTTP_BYTES_DRIFT')
        if http['status'] != 200 or http['url'] != 'http://127.0.0.1:11434/api/chat':
            raise ValueError('HTTP_IDENTITY_DRIFT')
        obj = json.loads((root / 'Q03.response.json').read_bytes())
        if obj['_debug_info']['rendered_template'].encode() != (root / 'Q03.rendered-prompt.txt').read_bytes():
            raise ValueError('RENDER_RECEIPT_DRIFT')
    return {'checked_files': len(inventory), 'commands': len(commands), 'tools': len(tools),
            'scope': 'inventory, exact memory-ledger metadata, raw hashes, size, timestamps, HTTP and tool invariants'}
