from pathlib import Path

path = Path("saas_pulse/saas_pulse_nb_cells_v2.py")
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

# Find 'def sanity_gate'
for i, l in enumerate(lines):
    if "def sanity_gate" in l:
        print(f"Found sanity_gate at line {i}")
        # Search for lines 292-298
        for j in range(i, i + 30):
            if "if not passed:" in lines[j]:
                print(f"Found 'if not passed:' at line {j}")
                # Replace lines j to j+8
                new_block = [
                    '    if not passed:\n',
                    '        msg = f"SANITY GATE WARNING [{name}]: Mode collapse detected! " + ", ".join([f"\'{l}\'={f:.1%} > {threshold:.0%}" for l, f in violating])\n',
                    '        print("=" * 70)\n',
                    '        print(msg)\n',
                    '        print(f"Distribution: {dict(c)}")\n',
                    '        print("=" * 70)\n',
                ]
                # Find where 'else:' starts
                else_idx = None
                for k in range(j, j + 15):
                    if "else:" in lines[k]:
                        else_idx = k
                        break
                print(f"Replacing lines {j} to {else_idx}")
                lines = lines[:j] + new_block + lines[else_idx:]
                break
        break

path.write_text("".join(lines), encoding="utf-8")
print("Saved fixed lines!")
