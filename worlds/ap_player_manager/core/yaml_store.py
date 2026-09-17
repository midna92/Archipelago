from pathlib import Path
from typing import Dict, List

import yaml


def discover_player_yamls(players_directory: Path) -> Dict[str, List[Path]]:
    """Group the *.yaml files in players_directory by their `game` key."""
    games: Dict[str, List[Path]] = {}

    if not players_directory.exists():
        return games

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
