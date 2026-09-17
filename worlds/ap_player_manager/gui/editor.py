import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..core.options_introspect import get_game_options
from ..core.yaml_store import discover_player_yamls


class Editor(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, padding=(8, 0, 0, 0), **kwargs)

        self._create_header()
        self._create_game_selector()
        self._create_options_panel()
        self._create_actions()

    def _create_header(self):
        header = ttk.Frame(self)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Selected Player",
            font=("TkDefaultFont", 14, "bold"),
        ).pack(side=tk.LEFT)

    def _create_game_selector(self):
        game_frame = ttk.Frame(self)
        game_frame.pack(fill=tk.X, pady=(15, 10))

        ttk.Label(
            game_frame,
            text="Game:",
        ).pack(side=tk.LEFT)

        self.game_combo = ttk.Combobox(
            game_frame,
            state="readonly",
        )
        self.game_combo.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(8, 0),
        )

    def _create_options_panel(self):
        self.options_frame = ttk.LabelFrame(
            self,
            text="Options",
            padding=10,
        )
        self.options_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        ttk.Label(
            self.options_frame,
            text="Show options of selected apworld dynamically",
        ).pack(expand=True)

    def _create_actions(self):
        actions = ttk.Frame(self)
        actions.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(
            actions,
            text="Reset to Default",
        ).pack(side=tk.LEFT)

        ttk.Button(
            actions,
            text="Apply Preset",
        ).pack(side=tk.LEFT, padx=(4, 0))

        ttk.Frame(actions).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
        )

        ttk.Button(
            actions,
            text="Save As...",
        ).pack(side=tk.RIGHT)

        ttk.Button(
            actions,
            text="Save",
        ).pack(side=tk.RIGHT, padx=(0, 4))

    def load_available_games(self, player_template_directory: Path) -> None:
        if player_template_directory.exists():
            games = discover_player_yamls(player_template_directory)
            self.game_combo["values"] = [*games.keys()]

    def select_game(self, game_name: str) -> None:
        self.game_combo.current(self.game_combo["values"].index(game_name))

    def show_options(self, game_name: str):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        game_options = get_game_options(game_name)

        if game_options is None:
            ttk.Label(
                self.options_frame,
                text=f"World nicht gefunden: {game_name}"
            ).pack(anchor="w")
            return

        text = tk.Text(
            self.options_frame,
            height=20,
            width=80
        )
        text.pack(fill="both", expand=True)

        text.insert("end", f"Game: {game_options.game_name}\n")
        text.insert("end", f"Options: {game_options.options_dataclass_name}\n")
        text.insert("end", "-" * 60 + "\n\n")

        for option_field in game_options.fields:
            text.insert("end", f"Option: {option_field.name}\n")
            text.insert("end", f"  Class: {option_field.option_class}\n")
            text.insert("end", f"  Default: {option_field.default}\n")
            text.insert("end", f"  MRO: {option_field.option_class_mro}\n")

            if option_field.display_name is not None:
                text.insert(
                    "end",
                    f"  Display Name: {option_field.display_name}\n"
                )

            text.insert("end", "\n")
