import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..core.options_introspect import get_game_options
from ..core.yaml_store import discover_player_yamls
from .option_widgets import build_option_widget


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

        self._options_canvas = tk.Canvas(self.options_frame, highlightthickness=0)
        self._options_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        options_scrollbar = ttk.Scrollbar(
            self.options_frame,
            orient=tk.VERTICAL,
            command=self._options_canvas.yview,
        )
        options_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._options_canvas.configure(yscrollcommand=options_scrollbar.set)

        self.options_list = ttk.Frame(self._options_canvas)
        options_list_id = self._options_canvas.create_window(
            (0, 0),
            window=self.options_list,
            anchor="nw",
        )

        self.options_list.bind(
            "<Configure>",
            lambda event: self._options_canvas.configure(
                scrollregion=self._options_canvas.bbox("all"),
            ),
        )
        self._options_canvas.bind(
            "<Configure>",
            lambda event: self._options_canvas.itemconfigure(options_list_id, width=event.width),
        )

        ttk.Label(
            self.options_list,
            text="Show options of selected apworld dynamically",
        ).pack(expand=True, pady=20)

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
        for widget in self.options_list.winfo_children():
            widget.destroy()

        game_options = get_game_options(game_name)

        if game_options is None:
            ttk.Label(
                self.options_list,
                text=f"World nicht gefunden: {game_name}",
            ).pack(anchor="w", pady=10)
            return

        for option_field in game_options.fields:
            self._add_option_row(option_field)

    def _add_option_row(self, option_field) -> None:
        row = ttk.Frame(self.options_list, padding=(0, 6))
        row.pack(fill=tk.X)

        ttk.Label(
            row,
            text=option_field.display_name or option_field.name,
            font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor="w")

        doc = (option_field.option_class.__doc__ or "").strip()
        if doc:
            ttk.Label(
                row,
                text=doc.splitlines()[0].strip(),
                foreground="gray",
                wraplength=520,
            ).pack(anchor="w")

        widget_area = ttk.Frame(row, padding=(0, 4, 0, 0))
        widget_area.pack(fill=tk.X)
        build_option_widget(widget_area, option_field.option_class, option_field.default)

        ttk.Separator(row, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(8, 0))
