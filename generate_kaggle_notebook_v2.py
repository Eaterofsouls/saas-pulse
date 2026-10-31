#!/usr/bin/env python3
"""
generate_kaggle_notebook_v2.py
Generates the SaaS-Pulse v2 Kaggle notebook from saas_pulse_nb_cells_v2.py
"""

import json, os, ast, textwrap

CELLS_FILE     = "saas_pulse_nb_cells_v2.py"
NOTEBOOK_PATH  = "kaggle_kernel_staging/saas_pulse_v2.ipynb"


def load_cells_from_py(path):
    """
    Reads the cell template file.  Every top-level string literal that is
    preceded by a comment of the form  # CELL: <type> <title>
    becomes one notebook cell.

    The file uses a cell-marker convention:
      # CELL:code  Cell N — Title
      # CELL:md    ## Heading
    followed by an UNINDENTED triple-quoted string (the cell source).
    """
    src = open(path, encoding="utf-8").read()
    lines = src.splitlines(keepends=True)

    cells = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("# CELL:"):
            rest  = stripped[len("# CELL:"):].strip()
            ctype = rest.split()[0]          # "code" or "md"
            # Collect source lines until next # CELL: or end-of-file
            i += 1
            src_lines = []
            while i < len(lines) and not lines[i].strip().startswith("# CELL:"):
                src_lines.append(lines[i])
                i += 1
            cell_src = "".join(src_lines).strip()
            cells.append({"type": ctype, "source": cell_src})
        else:
            i += 1

    return cells


def make_nb(cells):
    nb_cells = []
    for c in cells:
        if c["type"] == "code":
            nb_cells.append({
                "cell_type": "code",
                "source": c["source"],
                "metadata": {},
                "outputs": [],
                "execution_count": None,
            })
        else:
            nb_cells.append({
                "cell_type": "markdown",
                "source": c["source"],
                "metadata": {},
            })
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "cells": nb_cells,
    }


if __name__ == "__main__":
    cells = load_cells_from_py(CELLS_FILE)
    print(f"Loaded {len(cells)} cells from {CELLS_FILE}")
    nb = make_nb(cells)
    os.makedirs(os.path.dirname(NOTEBOOK_PATH), exist_ok=True)
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Notebook written to: {NOTEBOOK_PATH}  ({len(cells)} cells)")
