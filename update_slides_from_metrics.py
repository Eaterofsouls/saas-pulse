#!/usr/bin/env python3
"""
update_slides_from_metrics.py

Regenerates the benchmark tables, per-class F1 scores, confidence intervals,
and McNemar test statistics in PRESENTATION_SLIDES.md and presentation.html
directly from the executed metrics.json output.

Usage:
    python update_slides_from_metrics.py [path_to_metrics_json]
"""

import sys
import json
import re
from pathlib import Path

def find_latest_metrics_json():
    runs_dir = Path("runs")
    if not runs_dir.exists():
        runs_dir = Path("saas_pulse/runs")
    
    candidates = sorted(list(runs_dir.glob("**/metrics.json")), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    return None

def main():
    if len(sys.argv) > 1:
        metrics_path = Path(sys.argv[1])
    else:
        metrics_path = find_latest_metrics_json()
        
    if not metrics_path or not metrics_path.exists():
        print(f"Error: Could not find metrics.json. Checked: {metrics_path}")
        sys.exit(1)
        
    print(f"Loading metrics from: {metrics_path.resolve()}")
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    # Extract overall metrics
    zs = metrics.get("zero_shot", {})
    fs = metrics.get("few_shot", {})
    lora = metrics.get("lora", {})
    
    zs_acc = zs.get("accuracy", 0.0)
    zs_w_low, zs_w_high = zs.get("wilson_ci_95", [0.0, 0.0])
    zs_prec = zs.get("macro_precision", 0.0)
    zs_rec = zs.get("macro_recall", 0.0)
    zs_f1 = zs.get("macro_f1", 0.0)
    zs_b_low, zs_b_high = zs.get("bootstrap_macro_f1_ci_95", [0.0, 0.0])
    
    fs_acc = fs.get("accuracy", 0.0)
    fs_w_low, fs_w_high = fs.get("wilson_ci_95", [0.0, 0.0])
    fs_prec = fs.get("macro_precision", 0.0)
    fs_rec = fs.get("macro_recall", 0.0)
    fs_f1 = fs.get("macro_f1", 0.0)
    fs_b_low, fs_b_high = fs.get("bootstrap_macro_f1_ci_95", [0.0, 0.0])
    
    lora_acc = lora.get("accuracy", 0.0)
    lora_w_low, lora_w_high = lora.get("wilson_ci_95", [0.0, 0.0])
    lora_prec = lora.get("macro_precision", 0.0)
    lora_rec = lora.get("macro_recall", 0.0)
    lora_f1 = lora.get("macro_f1", 0.0)
    lora_b_low, lora_b_high = lora.get("bootstrap_macro_f1_ci_95", [0.0, 0.0])
    
    # Statistical significance
    mcnemar = metrics.get("mcnemar_tests", {})
    p_zs_lora = mcnemar.get("zero_shot_vs_lora", {}).get("p_value", 1.0)
    p_fs_lora = mcnemar.get("few_shot_vs_lora", {}).get("p_value", 1.0)
    p_zs_fs = mcnemar.get("zero_shot_vs_few_shot", {}).get("p_value", 1.0)
    
    # Per-class LoRA F1
    lora_per_class = lora.get("per_class", {})
    
    gain_over_zs = (lora_f1 - zs_f1) * 100
    gain_over_fs = (lora_f1 - fs_f1) * 100
    
    print("=== SUMMARY METRICS ===")
    print(f"Zero-Shot: Acc={zs_acc:.3f}, F1={zs_f1:.3f}")
    print(f"Few-Shot:  Acc={fs_acc:.3f}, F1={fs_f1:.3f}")
    print(f"LoRA:      Acc={lora_acc:.3f}, F1={lora_f1:.3f}")
    print(f"LoRA gain over Zero-Shot: +{gain_over_zs:.1f}%")
    print(f"LoRA gain over Few-Shot:  +{gain_over_fs:.1f}%")
    print(f"McNemar Zero-Shot vs LoRA p-value: {p_zs_lora:.4e}")
    print(f"McNemar Few-Shot vs LoRA p-value:  {p_fs_lora:.4e}")
    
    # Locate markdown slides
    slides_paths = [
        Path("PRESENTATION_SLIDES.md"),
        Path("saas_pulse/PRESENTATION_SLIDES.md")
    ]
    slides_file = None
    for sp in slides_paths:
        if sp.exists():
            slides_file = sp
            break
            
    if slides_file:
        content = slides_file.read_text(encoding="utf-8")
        
        # Build replacement table for Slide 8
        new_table = f"""| Method | Accuracy | Wilson 95% CI | Macro-Precision | Macro-Recall | Macro-F1 | Bootstrap 95% CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Zero-Shot Prompting** | {zs_acc:.3f} | [{zs_w_low:.3f}, {zs_w_high:.3f}] | {zs_prec:.3f} | {zs_rec:.3f} | {zs_f1:.3f} | [{zs_b_low:.3f}, {zs_b_high:.3f}] |
| **Few-Shot CoT** | {fs_acc:.3f} | [{fs_w_low:.3f}, {fs_w_high:.3f}] | {fs_prec:.3f} | {fs_rec:.3f} | {fs_f1:.3f} | [{fs_b_low:.3f}, {fs_b_high:.3f}] |
| **LoRA Fine-Tuned (Qwen)**| **{lora_acc:.3f}** | **[{lora_w_low:.3f}, {lora_w_high:.3f}]**| **{lora_prec:.3f}** | **{lora_rec:.3f}** | **{lora_f1:.3f}** | **[{lora_b_low:.3f}, {lora_b_high:.3f}]** |"""
        
        # Regex replace table
        table_pattern = re.compile(
            r"\| Method \| Accuracy \| Wilson 95% CI.*?\| \*\*LoRA Fine-Tuned \(Qwen\)\*\*\|.*?\n",
            re.DOTALL
        )
        if table_pattern.search(content):
            content = table_pattern.sub(new_table + "\n", content)
            print("Updated Slide 8 table in PRESENTATION_SLIDES.md")
            
        # Per class F1 scores
        def get_cls_f1(cls_name):
            return lora_per_class.get(cls_name, {}).get("f1", 0.0)
            
        per_class_block = f"""- `compliance_security`: **{get_cls_f1('compliance_security'):.2f}** (Clear regulatory language: FedRAMP, HIPAA, SOC2)
- `system_of_record`: **{get_cls_f1('system_of_record'):.2f}** (Transactional databases, core ERP/CRM language)
- `data_gravity`: **{get_cls_f1('data_gravity'):.2f}** (Data volume, petabyte scale, lakehouse architectures)
- `switching_costs_integrations`: **{get_cls_f1('switching_costs_integrations'):.2f}** (Complex API integrations, business process lock-in)
- `network_effects_ecosystem`: **{get_cls_f1('network_effects_ecosystem'):.2f}** (Multi-sided marketplaces, app developer ecosystems)
- `none_or_commodity`: **{get_cls_f1('none_or_commodity'):.2f}** (Boilerplate risk factors, marketing descriptions)"""

        per_class_pattern = re.compile(
            r"- `compliance_security`:.*?`none_or_commodity`:.*?\)",
            re.DOTALL
        )
        if per_class_pattern.search(content):
            content = per_class_pattern.sub(per_class_block, content)
            print("Updated per-class F1 scores in PRESENTATION_SLIDES.md")
            
        # Update gain string
        gain_pattern = re.compile(r"yielding a \+\d+\.?\d* percentage point gain in Macro-F1")
        content = gain_pattern.sub(f"yielding a +{gain_over_zs:.1f} percentage point gain in Macro-F1", content)
        
        # Update speaker notes mentions of Macro-F1 and Accuracy
        notes_pattern = re.compile(r"reaches \*\*\d+\.?\d* Macro-F1\*\* and \d+% accuracy!")
        content = notes_pattern.sub(f"reaches **{lora_f1:.3f} Macro-F1** and {int(lora_acc*100)}% accuracy!", content)
        
        zs_notes_pattern = re.compile(r"Zero-shot achieves only \d+\.?\d* Macro-F1\.")
        content = zs_notes_pattern.sub(f"Zero-shot achieves only {zs_f1:.3f} Macro-F1.", content)
        
        fs_notes_pattern = re.compile(r"Few-Shot CoT lifts Macro-F1 to \d+\.?\d*")
        content = fs_notes_pattern.sub(f"Few-Shot CoT lifts Macro-F1 to {fs_f1:.3f}", content)
        
        ci_notes_pattern = re.compile(r"The 95% confidence interval for LoRA's Macro-F1 is \[\d+\.?\d*,\s*\d+\.?\d*\]")
        content = ci_notes_pattern.sub(f"The 95% confidence interval for LoRA's Macro-F1 is [{lora_b_low:.3f}, {lora_b_high:.3f}]", content)
        
        slides_file.write_text(content, encoding="utf-8")
        print(f"Successfully saved updated {slides_file}")

    # Now update presentation.html if present
    html_paths = [
        Path("presentation.html"),
        Path("saas_pulse/presentation.html")
    ]
    html_file = None
    for hp in html_paths:
        if hp.exists():
            html_file = hp
            break
            
    if html_file:
        html_content = html_file.read_text(encoding="utf-8")
        
        # HTML Table replacement
        new_html_tbody = f"""        <tbody>
          <tr>
            <td><strong>Zero-Shot Prompting</strong></td>
            <td>{zs_acc:.3f}</td>
            <td>[{zs_w_low:.3f}, {zs_w_high:.3f}]</td>
            <td>{zs_prec:.3f}</td>
            <td>{zs_rec:.3f}</td>
            <td>{zs_f1:.3f}</td>
            <td>[{zs_b_low:.3f}, {zs_b_high:.3f}]</td>
          </tr>
          <tr>
            <td><strong>Few-Shot CoT</strong></td>
            <td>{fs_acc:.3f}</td>
            <td>[{fs_w_low:.3f}, {fs_w_high:.3f}]</td>
            <td>{fs_prec:.3f}</td>
            <td>{fs_rec:.3f}</td>
            <td>{fs_f1:.3f}</td>
            <td>[{fs_b_low:.3f}, {fs_b_high:.3f}]</td>
          </tr>
          <tr style="background: rgba(16, 185, 129, 0.15); border-left: 4px solid var(--success);">
            <td><strong>LoRA Fine-Tuned (Qwen 1.5B)</strong></td>
            <td><strong>{lora_acc:.3f}</strong></td>
            <td><strong>[{lora_w_low:.3f}, {lora_w_high:.3f}]</strong></td>
            <td><strong>{lora_prec:.3f}</strong></td>
            <td><strong>{lora_rec:.3f}</strong></td>
            <td><strong>{lora_f1:.3f}</strong></td>
            <td><strong>[{lora_b_low:.3f}, {lora_b_high:.3f}]</strong></td>
          </tr>
        </tbody>"""
        
        tbody_pattern = re.compile(r"<tbody>\s*<tr>\s*<td><strong>Zero-Shot Prompting</strong></td>.*?</tbody>", re.DOTALL)
        if tbody_pattern.search(html_content):
            html_content = tbody_pattern.sub(new_html_tbody, html_content)
            print("Updated HTML table in presentation.html")
            
        # Top defended classes in HTML
        html_classes_block = f"""          <ul>
            <li><code>compliance_security</code>: <strong>{get_cls_f1('compliance_security'):.2f} F1</strong> (Explicit regulatory language)</li>
            <li><code>system_of_record</code>: <strong>{get_cls_f1('system_of_record'):.2f} F1</strong> (High transactional specificity)</li>
            <li><code>none_or_commodity</code>: <strong>{get_cls_f1('none_or_commodity'):.2f} F1</strong> (Generic boilerplate rejection)</li>
          </ul>"""
        html_cls_pattern = re.compile(r"<ul>\s*<li><code>compliance_security</code>:.*?</ul>", re.DOTALL)
        if html_cls_pattern.search(html_content):
            html_content = html_cls_pattern.sub(html_classes_block, html_content)
            print("Updated top classes in presentation.html")
            
        # Statistical conclusion in HTML
        html_stat_pattern = re.compile(r"LoRA provides a <strong>\+\d+\.?\d* percentage point gain</strong> in Macro-F1 over Zero-Shot\.")
        html_content = html_stat_pattern.sub(f"LoRA provides a <strong>+{gain_over_zs:.1f} percentage point gain</strong> in Macro-F1 over Zero-Shot.", html_content)
        
        # HTML speaker notes
        html_notes_pattern = re.compile(r"data-notes=\"Here is our headline GenAI result\. Zero-shot achieved only \d+\.?\d* Macro-F1.*?LoRA fine-tuning jumped to \d+\.?\d* Macro-F1 with \d+% accuracy\.")
        new_html_notes = f'data-notes="Here is our headline GenAI result. Zero-shot achieved only {zs_f1:.3f} Macro-F1 because 10-K legalese confuses small models. Few-shot CoT improved this to {fs_f1:.3f}. But LoRA fine-tuning jumped to {lora_f1:.3f} Macro-F1 with {int(lora_acc*100)}% accuracy.'
        html_content = html_notes_pattern.sub(new_html_notes, html_content)
        
        html_file.write_text(html_content, encoding="utf-8")
        print(f"Successfully saved updated {html_file}")
        
    print("Slide update script finished successfully.")

if __name__ == "__main__":
    main()
