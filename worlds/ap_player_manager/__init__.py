from worlds.LauncherComponents import Component, components, Type
from .gui.app import run

components.append(Component("Player Manager",
                            func=run,
                            component_type=Type.TOOL,
                            description="Manages players in Archipelago"))
