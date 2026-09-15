import tkinter as tk
from dataclasses import fields
from pathlib import Path
from tkinter import ttk
from typing import get_type_hints

import yaml

from worlds import AutoWorldRegister


class ApPlayerManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Player Manager")
        self.geometry("1100x700")
        self.minsize(800, 500)

        self._create_menu()
        self._create_layout()
        self._create_statusbar()

        self.load_yaml_tree()

    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open...")
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Save As...")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")

        preset_menu = tk.Menu(menubar, tearoff=False)
        preset_menu.add_command(label="Create Preset")
        preset_menu.add_command(label="Manage Presets")

        randomize_menu = tk.Menu(menubar, tearoff=False)
        randomize_menu.add_command(label="Randomize Options")
        randomize_menu.add_command(label="Create Random Session")

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        menubar.add_cascade(label="Preset", menu=preset_menu)
        menubar.add_cascade(label="Randomize", menu=randomize_menu)

        self.config(menu=menubar)

    def _create_layout(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        self._create_sidebar(paned)
        self._create_editor(paned)

    def _create_sidebar(self, parent):
        sidebar = ttk.Frame(parent, padding=(0, 0, 8, 0))

        # Player YAML Tree
        yaml_frame = ttk.LabelFrame(
            sidebar,
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
            self._on_yaml_selected,
        )

        # Tree Buttons
        yaml_buttons = ttk.Frame(sidebar)
        yaml_buttons.pack(fill=tk.X, pady=(6, 0))

        ttk.Button(
            yaml_buttons,
            text="Open...",
        ).pack(side=tk.LEFT)

        ttk.Button(
            yaml_buttons,
            text="New",
        ).pack(side=tk.LEFT, padx=(4, 0))

        # Presets
        preset_frame = ttk.LabelFrame(
            sidebar,
            text="Presets for Player 1",
            padding=6,
        )
        preset_frame.pack(fill=tk.X, pady=(8, 0))

        self.preset_list = tk.Listbox(
            preset_frame,
            height=5,
        )
        self.preset_list.pack(fill=tk.X)

        self.preset_list.insert(tk.END, "Casual")
        self.preset_list.insert(tk.END, "Hard")
        self.preset_list.insert(tk.END, "No Glitches")

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

        parent.add(sidebar, weight=1)

    def _create_editor(self, parent):
        editor = ttk.Frame(
            parent,
            padding=(8, 0, 0, 0),
        )

        # Header
        header = ttk.Frame(editor)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Selected Player",
            font=("TkDefaultFont", 14, "bold"),
        ).pack(side=tk.LEFT)

        # Game
        game_frame = ttk.Frame(editor)
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

        # Options
        self.options_frame = ttk.LabelFrame(
            editor,
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

        # Actions
        actions = ttk.Frame(editor)
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

        parent.add(editor, weight=3)

    def _create_statusbar(self):
        self.status = ttk.Label(
            self,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2),
        )
        self.status.pack(fill=tk.X)

    def _on_yaml_selected(self, event):
        selection = self.yaml_tree.selection()

        if not selection:
            return

        item = selection[0]
        parent = self.yaml_tree.parent(item)

        if parent:
            # Only handle Player entries, not Game nodes.
            game = self.yaml_tree.item(parent, "text")
            player = self.yaml_tree.item(item, "text")

            self.status.config(
                text=f"Selected: {game} / {player}"
            )

            self.show_options(game)

    def show_options(self, game_name):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        world = AutoWorldRegister.world_types.get(game_name)

        if world is None:
            ttk.Label(
                self.options_frame,
                text=f"World nicht gefunden: {game_name}"
            ).pack(anchor="w")
            return

        options_dataclass = world.options_dataclass

        text = tk.Text(
            self.options_frame,
            height=20,
            width=80
        )
        text.pack(fill="both", expand=True)

        text.insert("end", f"Game: {game_name}\n")
        text.insert("end", f"Options: {options_dataclass.__name__}\n")
        text.insert("end", "-" * 60 + "\n\n")

        type_hints = get_type_hints(options_dataclass)

        for field in fields(options_dataclass):
            option_class = type_hints[field.name]

            text.insert("end", f"Option: {field.name}\n")
            text.insert("end", f"  Class: {option_class}\n")
            text.insert("end", f"  Default: {field.default}\n")
            text.insert("end", f"  MRO: {option_class.__mro__}\n")

            if hasattr(option_class, "display_name"):
                text.insert(
                    "end",
                    f"  Display Name: {option_class.display_name}\n"
                )

            text.insert("end", "\n")

    def load_yaml_tree(self):
        self.yaml_tree.delete(*self.yaml_tree.get_children())

        yaml_directory = Path("Players")

        if not yaml_directory.exists():
            self.status.config(
                text=f"YAML directory not found: {yaml_directory}"
            )
            return

        games = {}

        for yaml_file in yaml_directory.glob("*.yaml"):
            try:
                with yaml_file.open("r", encoding="utf-8") as file:
                    data = yaml.safe_load(file)

                if not isinstance(data, dict):
                    continue

                game = data.get("game")

                if not game:
                    continue

                games.setdefault(game, []).append(yaml_file)

            except yaml.YAMLError as exc:
                print(f"Could not read {yaml_file}: {exc}")

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

        self.status.config(
            text=f"{sum(len(files) for files in games.values())} YAML(s) found"
        )


def run():
    app = ApPlayerManager()
    app.mainloop()
