from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

_Signature = Tuple[Tuple[str, int, int], ...]

_cache: Dict[str, Tuple[_Signature, Dict[str, List[Path]]]] = {}


def _directory_signature(players_directory: Path) -> _Signature:
    """Cheap per-file fingerprint (name, mtime_ns, size) for every *.yaml in
    the directory, without opening/parsing any of them. Changes whenever a
    file is added, removed, renamed, or rewritten in place."""
    if not players_directory.exists():
        return ()

    entries = []
    for yaml_file in players_directory.glob("*.yaml"):
        stat = yaml_file.stat()
        entries.append((yaml_file.name, stat.st_mtime_ns, stat.st_size))

    return tuple(sorted(entries))


def _scan_player_yamls(players_directory: Path) -> Dict[str, List[Path]]:
    games: Dict[str, List[Path]] = {}

    for yaml_file in players_directory.glob("*.yaml"):
        try:
            with yaml_file.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Could not read {yaml_file}: {exc}")
            continue

        if not isinstance(data, dict):
            continue

        game = data.get("game")

        if not game:
            continue

        games.setdefault(game, []).append(yaml_file)

    return games


def discover_player_yamls(players_directory: Path) -> Dict[str, List[Path]]:
    """Group the *.yaml files in players_directory by their `game` key.

    Cached per directory: re-scanning (and re-parsing every YAML) only
    happens when a file in the directory was added, removed, renamed, or
    rewritten since the last call, so callers/writers never need to
    invalidate the cache manually. The returned dict is a fresh top-level
    copy; the Path lists inside are shared and should be treated as
    read-only.
    """
    if not players_directory.exists():
        return {}

    cache_key = str(players_directory.resolve())
    signature = _directory_signature(players_directory)

    cached = _cache.get(cache_key)
    if cached is not None and cached[0] == signature:
        return dict(cached[1])

    games = _scan_player_yamls(players_directory)
    _cache[cache_key] = (signature, games)
    return dict(games)


def invalidate_cache(players_directory: Optional[Path] = None) -> None:
    """Force the next discover_player_yamls call to re-scan, bypassing the
    fingerprint check. Not required for correctness under normal
    add/remove/edit operations - the fingerprint already catches those on
    the next call. Provided for write paths that want a guaranteed-fresh
    read immediately after writing. Pass None to clear the cache entirely.
    """
    if players_directory is None:
        _cache.clear()
        return

    _cache.pop(str(players_directory.resolve()), None)
