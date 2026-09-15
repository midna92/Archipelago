from worlds.LauncherComponents import Component, components, Type
from .ap_player_manager import run

components.append(Component("Player Manager",
                            func=run,
                            component_type=Type.TOOL,
                            description="Manages players in Archipelago"))
