"""Offline freeze support. No Docker, provider, or scientific controls here."""
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = '39a6968f3fbc870272987e251cc049e4c456e071'
PACKET = 'research/cal_context_free_packet_macos_rc1_20261009/candidate/'
DEPENDENCIES = {
    PACKET + 'prepare_packet.py': '33376fe6b1f910ba6a07103b0292dbb9a2d940757318705fa0ac182779002e43',
    PACKET + 'independent_packet_checker.py': '6b84015c19ab493483761c8ff8f885e3d63f0a0095f1e8d42c1105be4e91c448',
}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory():
    paths = list(HERE.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise ValueError('SYMLINK_IN_CANDIDATE')
    result = {str(p.relative_to(REPO)): sha(p) for p in sorted(paths)
              if p.is_file() and p != HERE / 'FREEZE.json'}
    for name, expected in DEPENDENCIES.items():
        if sha(REPO / name) != expected:
            raise ValueError('PACKET_DEPENDENCY_DRIFT:' + name)
        result[name] = expected
    return result


def validate_pins(pins):
    def require(ok, reason):
        if not ok:
            raise ValueError(reason)
    require(pins['docker_context'] == 'desktop-linux', 'CONTEXT_SUBSTITUTION')
    require(pins['docker_endpoint'].startswith('unix:///'), 'LOCAL_DAEMON_ENDPOINT_REQUIRED')
    require(pins['image_platform'] == 'linux/arm64', 'PLATFORM_SUBSTITUTION')
    require(re.fullmatch(r'sha256:[0-9a-f]{64}', pins['image_ref']) is not None and pins['image_ref'] == pins['image_id'], 'MISSING_IMMUTABLE_IMAGE_ID')
    require(re.fullmatch(r'sha256:[0-9a-f]{64}', pins['image_id']) is not None, 'MISSING_IMAGE_ID')
    require(pins['image_architecture'] == 'arm64' and pins['image_os'] == 'linux', 'IMAGE_PLATFORM')
    require(isinstance(pins['image_config_env'], list) and all(isinstance(x, str) for x in pins['image_config_env']), 'IMAGE_ENV')
    require(isinstance(pins['worker_config_env'], list) and all(isinstance(x, str) for x in pins['worker_config_env']), 'WORKER_ENV')
    require(pins['worker_config_env'] == [x for x in pins['image_config_env'] if not x.startswith('PATH=')]
            + ['PATH=/usr/local/bin:/usr/bin:/bin'] or
            pins['worker_config_env'] == [('PATH=/usr/local/bin:/usr/bin:/bin' if x.startswith('PATH=') else x)
                                         for x in pins['image_config_env']], 'WORKER_ENV_EXPECTATION')
    for key in ('platform', 'python', 'docker_engine', 'worker_python_version'):
        require(isinstance(pins[key], str) and pins[key] and 'REQUIRED' not in pins[key], 'MISSING_' + key)
    require('PYTHON_VERSION=' + pins['worker_python_version'] in pins['image_config_env'], 'PYTHON_VERSION_IMAGE_METADATA_MISMATCH')
    for key in ('docker_binary', 'python_binary', 'provider_binary', 'model_manifest'):
        record = pins[key]
        require(Path(record['path']).is_absolute(), 'ABSOLUTE_PATH_REQUIRED:' + key)
        require(re.fullmatch('[0-9a-f]{64}', record['sha256']) is not None, 'MISSING_HASH:' + key)
    require(Path(pins['model_blob_directory']).is_absolute(), 'MODEL_BLOB_PATH_REQUIRED')
    require(Path(pins['controller_home']).is_absolute(), 'CONTROLLER_HOME_REQUIRED')
    require(pins['provider_binary']['sha256'] == json.loads((HERE / 'PROVIDER.json').read_bytes())['binary']['sha256'], 'PROVIDER_SUBSTITUTION')
    require(pins['model_manifest']['sha256'] == json.loads((HERE / 'PROVIDER.json').read_bytes())['model_manifest_sha256'], 'MODEL_SUBSTITUTION')


def check_local(pins):
    validate_pins(pins)
    if platform.platform() != pins['platform'] or sys.version != pins['python']:
        raise ValueError('CONTROLLER_RUNTIME_DRIFT')
    if Path(sys.executable).resolve() != Path(pins['python_binary']['path']).resolve():
        raise ValueError('PYTHON_EXECUTABLE_DRIFT')
    for key in ('docker_binary', 'python_binary', 'provider_binary', 'model_manifest'):
        if sha(pins[key]['path']) != pins[key]['sha256']:
            raise ValueError('LOCAL_IDENTITY_DRIFT:' + key)
    provider = json.loads((HERE / 'PROVIDER.json').read_bytes())
    for blob in provider['model_blobs']:
        path = Path(pins['model_blob_directory']) / blob['digest'].replace(':', '-')
        if path.stat().st_size != blob['size'] or sha(path) != blob['digest'].split(':')[1]:
            raise ValueError('MODEL_BLOB_DRIFT')
