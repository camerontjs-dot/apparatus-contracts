#!/usr/bin/env python3
"""Create a byte-reproducible, uncompressed ZIP from wheel files."""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    wheel_files = sorted(path for path in args.wheel_dir.iterdir() if path.is_file() and path.suffix == ".whl")
    if not wheel_files:
        parser.error("wheel directory contains no .whl files")
    with ZipFile(args.output, "w", compression=ZIP_STORED) as archive:
        for path in wheel_files:
            info = ZipInfo(path.name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
