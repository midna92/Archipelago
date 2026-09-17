from dataclasses import dataclass, fields
from typing import Any, List, Optional, get_type_hints

from worlds.AutoWorld import AutoWorldRegister


@dataclass
class OptionField:
    name: str
    option_class: type
    default: Any
    option_class_mro: tuple
    display_name: Optional[str]


@dataclass
class GameOptions:
    game_name: str
    options_dataclass_name: str
    fields: List[OptionField]


def get_game_options(game_name: str) -> Optional[GameOptions]:
    """Introspect a registered world's options_dataclass, or None if the game is unknown."""
    world = AutoWorldRegister.world_types.get(game_name)

    if world is None:
        return None

    options_dataclass = world.options_dataclass
    type_hints = get_type_hints(options_dataclass)

    option_fields = []

    for field in fields(options_dataclass):
        option_class = type_hints[field.name]

        option_fields.append(OptionField(
            name=field.name,
            option_class=option_class,
            default=field.default,
            option_class_mro=option_class.__mro__,
            display_name=getattr(option_class, "display_name", None),
        ))

    return GameOptions(
        game_name=game_name,
        options_dataclass_name=options_dataclass.__name__,
        fields=option_fields,
    )
