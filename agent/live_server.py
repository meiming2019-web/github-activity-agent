"""Run the unchanged MCP implementation in a separate live database namespace."""

import importlib.util
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
FROZEN_DATABASE = ROOT / 'data/github.duckdb'
LIVE_DATABASE = ROOT / 'data/github_live.duckdb'


def live_path(path=LIVE_DATABASE, frozen=FROZEN_DATABASE):
    """Reject frozen aliases, symlink files, and shared hard links before opening."""
    path, frozen = Path(path), Path(frozen)
    if path.name != 'github_live.duckdb' or path.is_symlink():
        raise ValueError('Live database must be a non-symlink github_live.duckdb file.')
    resolved = path.resolve()
    if resolved == frozen.resolve() or (path.exists() and frozen.exists() and path.samefile(frozen)):
        raise ValueError('The frozen database cannot be used as a live output.')
    if resolved.is_relative_to((ROOT / 'eval').resolve()):
        raise ValueError('Live files cannot be stored under eval/.')
    for candidate in (path, Path(str(path) + '.wal'), Path(str(path) + '.ingest.lock')):
        if candidate.is_symlink() or (candidate.exists() and candidate.stat().st_nlink != 1):
            raise ValueError('Live database and sidecar files cannot be aliases or shared hard links.')
    return resolved


def isolated_server(path, *, live=True):
    """Load original code independently; never mutate agent.mcp_server globals."""
    path = live_path(path) if live else Path(path).resolve()
    name = '_github_live_mcp_' + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, ROOT / 'agent/mcp_server.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        del sys.modules[name]
    module.DATABASE_PATH = path
    return module


def main():
    """Explicit stdio entry; importing this module starts no server."""
    path = live_path()
    if not path.is_file():
        raise ValueError('Live database missing; run scripts/ingest_live.py first.')
    isolated_server(path).server.run(transport='stdio')


if __name__ == '__main__':
    main()
