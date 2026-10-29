import json
import html
import sys
from pathlib import Path

def convert_nb_to_html(nb_path, out_path=None):
    nb_p = Path(nb_path)
    if out_path is None:
        out_p = nb_p.with_suffix(".html")
    else:
        out_p = Path(out_path)
        
    with open(nb_p, "r", encoding="utf-8") as f:
        nb = json.load(f)
        
    html_parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>{nb_p.stem}</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 950px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1e293b; background: #f8fafc; }",
        ".cell { margin-bottom: 24px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }",
        ".markdown-cell { background: #ffffff; }",
        ".code-cell { background: #f8fafc; }",
        "pre { background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 6px; overflow-x: auto; font-size: 0.88rem; }",
        ".output { margin-top: 12px; padding: 12px; background: #f1f5f9; border-left: 4px solid #38bdf8; font-family: monospace; font-size: 0.85rem; white-space: pre-wrap; }",
        "h1, h2, h3 { color: #0f172a; }",
        "</style></head><body>"
    ]
    
    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type", "")
        src = "".join(cell.get("source", []))
        if cell_type == "markdown":
            html_parts.append(f"<div class='cell markdown-cell'><div>{html.escape(src).replace(chr(10), '<br>')}</div></div>")
        elif cell_type == "code":
            html_parts.append(f"<div class='cell code-cell'><pre><code>{html.escape(src)}</code></pre>")
            for out in cell.get("outputs", []):
                out_type = out.get("output_type", "")
                if out_type == "stream":
                    txt = "".join(out.get("text", []))
                    html_parts.append(f"<div class='output'>{html.escape(txt)}</div>")
                elif out_type in ["execute_result", "display_data"]:
                    data = out.get("data", {})
                    if "text/plain" in data:
                        txt = "".join(data["text/plain"])
                        html_parts.append(f"<div class='output'>{html.escape(txt)}</div>")
            html_parts.append("</div>")
            
    html_parts.append("</body></html>")
    out_p.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"Exported HTML to {out_p.resolve()}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        convert_nb_to_html(sys.argv[1])
    else:
        print("Usage: python nb_to_html.py <notebook.ipynb>")
