import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .editor import Editor
from .sidebar import Sidebar


class ApPlayerManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Player Manager")
        self.geometry("1100x700")
        self.minsize(800, 500)

        self._create_menu()
        self._create_layout()
        self._create_statusbar()

        self.reload_yaml_tree()

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

        self.sidebar = Sidebar(paned, on_yaml_selected=self._on_yaml_selected)
        paned.add(self.sidebar, weight=1)

        self.editor = Editor(paned)
        paned.add(self.editor, weight=3)

    def _create_statusbar(self):
        self.status = ttk.Label(
            self,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2),
        )
        self.status.pack(fill=tk.X)

    def _on_yaml_selected(self, game: str, player: str):
        self.status.config(text=f"Selected: {game} / {player}")
        self.editor.show_options(game)

    def reload_yaml_tree(self):
        status_text = self.sidebar.load_yaml_tree(Path("Players"))
        self.status.config(text=status_text)


def run():
    app = ApPlayerManager()
    app.mainloop()
