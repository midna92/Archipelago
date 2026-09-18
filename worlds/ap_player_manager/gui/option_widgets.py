"""Maps an AP Option class to a fitting Tkinter input widget.

Each ``_build_*`` helper creates and packs its widget(s) directly into the
given parent frame. The created ``tk.Variable`` is stashed on the widget
itself (``widget.variable``) purely to keep a Python reference alive for as
long as the widget exists.
"""
import tkinter as tk
from tkinter import ttk
from typing import Any

import Options as ap_options


def build_option_widget(parent: ttk.Frame, option_class: type, default: Any) -> None:
    """Create the most fitting input widget for the given AP Option class.

    Some worlds' Option classes resolve class attributes (e.g. `options`)
    through descriptors that expect a live World/settings context, which
    isn't available during standalone introspection. Fall back to a plain
    display for that field rather than taking the whole panel down.
    """

    try:
        if issubclass(option_class, ap_options.Toggle):
            _build_toggle(parent, default)
        elif issubclass(option_class, ap_options.TextChoice):
            _build_choice(parent, option_class, default, editable=True)
        elif issubclass(option_class, ap_options.Choice):
            _build_choice(parent, option_class, default, editable=False)
        elif issubclass(option_class, ap_options.NamedRange):
            _build_named_range(parent, option_class, default)
        elif issubclass(option_class, ap_options.Range):
            _build_range(parent, option_class, default)
        elif issubclass(option_class, (ap_options.OptionSet, ap_options.OptionList)):
            _build_multi_value(parent, option_class, default)
        elif issubclass(option_class, ap_options.OptionDict):
            _build_dict(parent, default)
        elif issubclass(option_class, ap_options.FreeText):
            _build_text(parent, default)
        else:
            _build_fallback(parent, default)
    except Exception:
        _build_fallback(parent, default)


def _build_toggle(parent: ttk.Frame, default: Any) -> None:
    var = tk.BooleanVar(value=bool(default))
    widget = ttk.Checkbutton(parent, variable=var)
    widget.variable = var
    widget.pack(anchor="w")


def _build_choice(parent: ttk.Frame, option_class: type, default: Any, editable: bool) -> None:
    names = sorted(option_class.options.keys())
    default_name = option_class.name_lookup.get(default, str(default))

    var = tk.StringVar(value=default_name)
    widget = ttk.Combobox(
        parent,
        textvariable=var,
        values=names,
        state="normal" if editable else "readonly",
    )
    widget.variable = var
    widget.pack(fill="x")


def _build_range(parent: ttk.Frame, option_class: type, default: Any) -> None:
    var = tk.IntVar(value=default if isinstance(default, int) else option_class.range_start)
    widget = ttk.Spinbox(
        parent,
        from_=option_class.range_start,
        to=option_class.range_end,
        textvariable=var,
    )
    widget.variable = var
    widget.pack(fill="x")


def _build_named_range(parent: ttk.Frame, option_class: type, default: Any) -> None:
    row = ttk.Frame(parent)
    row.pack(fill="x")

    var = tk.IntVar(value=default if isinstance(default, int) else option_class.range_start)
    spinbox = ttk.Spinbox(
        row,
        from_=option_class.range_start,
        to=option_class.range_end,
        textvariable=var,
        width=10,
    )
    spinbox.pack(side="left")
    spinbox.variable = var

    special_range_names = option_class.special_range_names
    if special_range_names:
        default_name = next(
            (name for name, value in special_range_names.items() if value == default),
            "",
        )
        name_var = tk.StringVar(value=default_name)

        def apply_special_name(_event=None):
            selected = special_range_names.get(name_var.get())
            if selected is not None:
                var.set(selected)

        combo = ttk.Combobox(
            row,
            textvariable=name_var,
            values=sorted(special_range_names.keys()),
            state="readonly",
            width=18,
        )
        combo.bind("<<ComboboxSelected>>", apply_special_name)
        combo.variable = name_var
        combo.pack(side="left", padx=(6, 0))


def _build_multi_value(parent: ttk.Frame, option_class: type, default: Any) -> None:
    valid_keys = sorted(getattr(option_class, "_valid_keys", None) or ())

    if valid_keys:
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="x")

        listbox = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            height=min(6, len(valid_keys)),
        )
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side="left", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        default_values = set(default) if default else set()
        for index, key in enumerate(valid_keys):
            listbox.insert(tk.END, key)
            if key in default_values:
                listbox.selection_set(index)
    else:
        var = tk.StringVar(value=", ".join(str(v) for v in default) if default else "")
        widget = ttk.Entry(parent, textvariable=var)
        widget.variable = var
        widget.pack(fill="x")


def _build_dict(parent: ttk.Frame, default: Any) -> None:
    entries = list((default or {}).items())

    tree = ttk.Treeview(
        parent,
        columns=("key", "value"),
        show="headings",
        height=min(6, max(2, len(entries))),
    )
    tree.heading("key", text="Key")
    tree.heading("value", text="Value")
    tree.column("value", anchor="center", width=80)
    tree.pack(fill="x")

    for key, value in entries:
        tree.insert("", tk.END, values=(key, value))


def _build_text(parent: ttk.Frame, default: Any) -> None:
    var = tk.StringVar(value=str(default))
    widget = ttk.Entry(parent, textvariable=var)
    widget.variable = var
    widget.pack(fill="x")


def _build_fallback(parent: ttk.Frame, default: Any) -> None:
    ttk.Label(parent, text=str(default), foreground="gray").pack(anchor="w")
