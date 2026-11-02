import ast
from pathlib import Path

content = Path("saas_pulse/saas_pulse_nb_cells_v2.py").read_text(encoding="utf-8")
raw_cells = content.split("# CELL:")

print(f"Total cells to verify: {len(raw_cells)}")
errors = 0
for i, cell in enumerate(raw_cells):
    cell = cell.strip()
    if not cell:
        continue
    lines = cell.split("\n", 1)
    cell_type = lines[0].strip().lower()
    cell_body = lines[1] if len(lines) > 1 else ""
    
    if cell_type.startswith("code"):
        try:
            ast.parse(cell_body)
            print(f"Cell {i} (code): SYNTAX VALID")
        except SyntaxError as e:
            print(f"Cell {i} (code): SYNTAX ERROR: {e}")
            errors += 1

if errors == 0:
    print("\nALL CODE CELLS PASS AST PARSING WITH ZERO SYNTAX ERRORS!")
else:
    print(f"\n{errors} cells had syntax errors.")
