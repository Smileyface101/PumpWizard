"""Small native desktop shell for the local strategy library."""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __version__
from .library import StrategyLibrary
from .strategies import StrategyImportError, parse_package


class RunnerWindow:
    def __init__(self, root: tk.Tk, data_dir: Path):
        self.root = root
        self.library = StrategyLibrary(data_dir)
        self.root.title(f"PumpWizard Runner {__version__}")
        self.root.minsize(860, 500)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        outer = ttk.Frame(root, padding=20)
        outer.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)
        ttk.Label(outer, text="PumpWizard Runner", font=("TkDefaultFont", 20, "bold")).grid(
            row=0, column=0, sticky="w")
        ttk.Label(outer, text=("Local strategy library · version " + __version__ +
                               " · trading execution is not included in this build")).grid(
            row=1, column=0, sticky="w", pady=(4, 16))
        controls = ttk.Frame(outer)
        controls.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ttk.Button(controls, text="Import configuration…", command=self.import_file).pack(side="left")
        ttk.Button(controls, text="Refresh", command=self.refresh).pack(side="left", padx=8)
        self.status = ttk.Label(controls, text="")
        self.status.pack(side="right")
        columns = ("strategy", "version", "compatibility", "reason")
        self.tree = ttk.Treeview(outer, columns=columns, show="headings", selectmode="browse")
        widths = {"strategy": 230, "version": 90, "compatibility": 190, "reason": 430}
        for column in columns:
            self.tree.heading(column, text=column.replace("_", " ").title())
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.grid(row=3, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.refresh()

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.library.rows()
        for row in rows:
            version = row["strategy_version"] or "legacy"
            self.tree.insert("", "end", values=(row["label"], version, row["compatibility"], row["reason"]))
        self.status.configure(text=f"{len(rows)} imported strategy{'ies' if len(rows) != 1 else ''}")

    def import_file(self) -> None:
        filename = filedialog.askopenfilename(title="Import strategy configuration",
                                              filetypes=[("JSON", "*.json"), ("All files", "*")])
        if not filename:
            return
        try:
            imported = parse_package(Path(filename).read_text(encoding="utf-8"))
            created = self.library.import_strategy(imported)
        except (OSError, StrategyImportError) as exc:
            messagebox.showerror("Cannot import configuration", str(exc), parent=self.root)
            return
        self.refresh()
        title = "Configuration imported" if created else "Already imported"
        messagebox.showinfo(title, f"{imported.label}\n\n{imported.reason}", parent=self.root)

    def close(self) -> None:
        self.library.close()
        self.root.destroy()


def run_desktop(data_dir: Path) -> int:
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError("Desktop UI is unavailable. Use the pumpwizard CLI commands instead.") from exc
    RunnerWindow(root, data_dir)
    root.mainloop()
    return 0

