import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable

from ..core.yaml_store import discover_player_yamls


class Sidebar(ttk.Frame):
    def __init__(self, parent, on_yaml_selected: Callable[[str, str], None], **kwargs):
        super().__init__(parent, padding=(0, 0, 8, 0), **kwargs)

        self._on_yaml_selected = on_yaml_selected

        self._create_yaml_tree()
        self._create_presets()

    def _create_yaml_tree(self):
        yaml_frame = ttk.LabelFrame(
            self,
            text="Player YAMLs",
            padding=6,
        )
        yaml_frame.pack(fill=tk.BOTH, expand=True)

        self.yaml_tree = ttk.Treeview(
            yaml_frame,
            show="tree",
            selectmode="browse",
            columns=("path",),
        )
        self.yaml_tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        scrollbar = ttk.Scrollbar(
            yaml_frame,
            orient=tk.VERTICAL,
            command=self.yaml_tree.yview,
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.yaml_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.yaml_tree.bind(
            "<<TreeviewSelect>>",
            self._handle_selection,
        )

        yaml_buttons = ttk.Frame(self)
        yaml_buttons.pack(fill=tk.X, pady=(6, 0))

        ttk.Button(
            yaml_buttons,
            text="Open...",
        ).pack(side=tk.LEFT)

        ttk.Button(
            yaml_buttons,
            text="New",
        ).pack(side=tk.LEFT, padx=(4, 0))

    def _create_presets(self):
        preset_frame = ttk.LabelFrame(
            self,
            text="Presets",
            padding=6,
        )
        preset_frame.pack(fill=tk.X, pady=(8, 0))

        self.preset_list = tk.Listbox(
            preset_frame,
            height=5,
        )
        self.preset_list.pack(fill=tk.X)

        preset_buttons = ttk.Frame(preset_frame)
        preset_buttons.pack(fill=tk.X, pady=(6, 0))

        ttk.Button(
            preset_buttons,
            text="New",
        ).pack(side=tk.LEFT)

        ttk.Button(
            preset_buttons,
            text="Manage...",
        ).pack(side=tk.LEFT, padx=(4, 0))

    def _handle_selection(self, event):
        selection = self.yaml_tree.selection()

        if not selection:
            return

        item = selection[0]
        parent = self.yaml_tree.parent(item)

        if not parent:
            return  # Only handle Player entries, not Game nodes.

        game = self.yaml_tree.item(parent, "text")
        player = self.yaml_tree.item(item, "text")

        self._on_yaml_selected(game, player)

    def load_yaml_tree(self, players_directory: Path) -> str:
        self.yaml_tree.delete(*self.yaml_tree.get_children())

        if not players_directory.exists():
            return f"YAML directory not found: {players_directory}"

        games = discover_player_yamls(players_directory)

        for game, files in sorted(games.items()):
            game_item = self.yaml_tree.insert(
                "",
                tk.END,
                text=game,
                open=True,
            )

            for yaml_file in sorted(files):
                self.yaml_tree.insert(
                    game_item,
                    tk.END,
                    text=yaml_file.stem,
                    values=(str(yaml_file),),
                )

        return f"{sum(len(files) for files in games.values())} YAML(s) found"

    def load_presets(self, game_name: str, presets_directory: Path):
        #self.preset_list.delete(tk.FIRST, tk.END)

        games = discover_player_yamls(presets_directory)

        for preset in games.get(game_name, []):
            self.preset_list.insert(tk.END, preset.stem)
