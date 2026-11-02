import json
from pathlib import Path

path = Path("saas_pulse/runs/20261102_2144/run_outputs/metrics.json")
with open(path, "r", encoding="utf-8") as f:
    m = json.load(f)

print("=== TASK 1: 10K MOATS ===")
t1 = m["task_1_moats"]
print("Test N:", t1.get("num_test_examples"))
for k, v in t1["methods"].items():
    acc = v["accuracy"]
    ci_a = v["accuracy_wilson_ci"]
    f1 = v["macro_f1"]
    ci_f1 = v["macro_f1_bootstrap_ci"]
    dist = v.get("pred_dist")
    print(f"{k:<25} Acc: {acc:.3f} [{ci_a[0]:.3f}, {ci_a[1]:.3f}]  F1: {f1:.3f} [{ci_f1[0]:.3f}, {ci_f1[1]:.3f}]  Dist: {dist}")

print("\n=== TASK 2: HN STANCE ===")
t2 = m["task_2_hn_stance"]
print("Test N:", t2.get("num_test_examples"))
for k in ["zero_shot", "few_shot"]:
    v = t2[k]
    acc = v["accuracy"]
    ci_a = v["accuracy_wilson_ci"]
    f1 = v["macro_f1"]
    dist = v.get("pred_dist")
    print(f"{k:<25} Acc: {acc:.3f} [{ci_a[0]:.3f}, {ci_a[1]:.3f}]  F1: {f1:.3f}  Dist: {dist}")

print("\n=== CORPUS HN SHARES ===")
print("Method:", m.get("corpus_hn_method"))
for k, v in (m.get("corpus_hn_shares") or {}).items():
    print(f"{k:<25} Share: {v['share']:.3f} [{v['ci_lo']:.3f}, {v['ci_hi']:.3f}] (n={v['count']})")

print("\n=== RQ4: ECONOMETRIC LINKAGE ===")
econ = m["econometric_linkage"]
print("RQ4 method:", m.get("rq4_method"))
print("Spearman moat vs excess return:", econ["rq4"]["spearman_moat_vs_excess_return"])
if "spearman_moat_vs_revenue_growth" in econ["rq4"]:
    print("Spearman moat vs revenue growth:", econ["rq4"]["spearman_moat_vs_revenue_growth"])
print("Category median excess return vs IGV:", econ.get("category_median_excess_return_vs_igv"))
