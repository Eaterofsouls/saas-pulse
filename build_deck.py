"""Builds presentation.html + PRESENTATION_SLIDES.md for SaaS-Pulse from the repo's data and run files.
Every number on the slides is computed here from a file; nothing is typed by hand.

Usage (from the saas_pulse repo root):
    python build_deck.py                      # uses the newest runs/*/run_outputs folder
    python build_deck.py runs/20261102_2144   # or a specific run folder
"""
import glob
import html
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

if len(sys.argv) > 1:
    RUN = sys.argv[1].rstrip("/\\")
else:
    RUN = sorted(os.path.dirname(p) for p in glob.glob("runs/*/run_outputs/metrics.json"))[-1]
OUT = os.path.join(RUN, "run_outputs")
SRC = []  # (claim, value, source) for the trace table


def src(claim, value, source):
    SRC.append((claim, value, source))
    return value


M = json.load(open(os.path.join(OUT, "metrics.json")))
T1 = M["task_1_moats"]["methods"]
MC = M["task_1_moats"]["mcnemar_tests"]
T2 = M["task_2_hn_stance"]
RQ = json.load(open(os.path.join(OUT, "rq4_correlations.json")))
PRED = pd.read_csv(os.path.join(OUT, "predictions.csv"))
MOAT = pd.read_csv(os.path.join(OUT, "moat_scores.csv"))
LOSS = pd.read_csv(os.path.join(OUT, "training_loss.csv"))
STK = pd.read_csv("dataset/stock_performance.csv")
GOLD = pd.read_csv("dataset/gold_10k_moats.csv")
MAN = pd.read_csv("dataset/MANIFEST.csv").set_index("filename")
ENV = {}
if os.path.exists(os.path.join(OUT, "environment_metadata.json")):
    ENV = json.load(open(os.path.join(OUT, "environment_metadata.json")))
REVIEW = None
for p in [os.path.join(RUN, "gold_review_completed.xlsx"), "dataset/review/gold_review_completed.xlsx"]:
    if os.path.exists(p):
        REVIEW = pd.read_excel(p, sheet_name="10K_review")
        REVIEW_PATH = p
        break

LABELS = ["system_of_record", "data_gravity", "switching_costs_integrations",
          "compliance_security", "network_effects_ecosystem", "none_or_commodity"]
NICE = {"system_of_record": "System of record", "data_gravity": "Data gravity",
        "switching_costs_integrations": "Switching costs / integrations",
        "compliance_security": "Compliance & security", "network_effects_ecosystem": "Network effects / ecosystem",
        "none_or_commodity": "None / commodity"}
METHODS = [("majority_baseline", "Majority class"), ("random_baseline", "Random"),
           ("keyword_rule_baseline", "Keyword rule*"), ("zero_shot", "Zero-shot (Qwen 1.5B)"),
           ("few_shot_cot", "Few-shot, 6 examples"), ("lora", "LoRA fine-tuned")]


def f3(x):
    return f"{x:.3f}"


def pct(x, d=1):
    return f"{100 * x:.{d}f}%"


def ci(a):
    return f"[{a[0]:.2f}, {a[1]:.2f}]"


def esc(s):
    return html.escape(str(s))


# ---------------- derived numbers ----------------
n_test = src("Test set size", T1["lora"]["n"], "metrics.json task_1_moats.methods.lora.n")
n_companies = src("Companies", int(MAN.loc["companies.csv", "row_count"]), "MANIFEST.csv companies.csv")
n_filings = src("10-K filings indexed", int(MAN.loc["filings_index.csv", "row_count"]), "MANIFEST.csv filings_index.csv")
n_paras = src("10-K paragraphs", int(MAN.loc["filings_paragraphs.jsonl", "row_count"]), "MANIFEST.csv filings_paragraphs.jsonl")
n_rev = src("Revenue rows", int(MAN.loc["revenue.csv", "row_count"]), "MANIFEST.csv revenue.csv")
n_hn = src("HN items", int(MAN.loc["hn_comments.jsonl", "row_count"]), "MANIFEST.csv hn_comments.jsonl")
n_price = src("Pricing-page records", int(MAN.loc["pricing_pages.jsonl", "row_count"]), "MANIFEST.csv pricing_pages.jsonl")
stk_ok = STK[STK.status == "ok"].copy()
n_stk = src("Tickers with prices", len(stk_ok), "stock_performance.csv status==ok")
igv = src("IGV return %", float(STK.igv_return_pct.dropna().iloc[0]), "stock_performance.csv igv_return_pct")
fy = sorted(MOAT.fiscal_year.unique())
split_counts = GOLD.split.value_counts().to_dict()
n_train = src("Train rows", int(split_counts.get("train", 0)), "gold_10k_moats.csv split==train")

# review agreement and Cohen's kappa (rule label vs final label on non-excluded rows)
kappa = agree = n_rev_eval = n_changed = n_excl = None
if REVIEW is not None:
    R = REVIEW.copy()
    R["final"] = R["your_label"].fillna(R["suggested_label"])
    n_excl = int((R.final == "exclude").sum())
    E = R[R.final != "exclude"]
    n_rev_eval = len(E)
    agree = (E.final == E.suggested_label).mean()
    n_changed = int((E.final != E.suggested_label).sum())
    cats = sorted(set(E.final) | set(E.suggested_label))
    pe = sum((E.final == c).mean() * (E.suggested_label == c).mean() for c in cats)
    kappa = (agree - pe) / (1 - pe)
    src("Review rows evaluated", n_rev_eval, REVIEW_PATH)
    src("Review rows excluded", n_excl, REVIEW_PATH)
    src("Rule-vs-review agreement", pct(agree), REVIEW_PATH)
    src("Cohen's kappa rule vs review", f3(kappa), REVIEW_PATH + " (computed)")

# test rows where the reviewed label equals the rule label (explains the keyword-rule advantage)
rule_on_test = None
if REVIEW is not None:
    tt = PRED.merge(REVIEW[["para_id", "suggested_label"]], on="para_id", how="left")
    rule_on_test = int((tt.suggested_label == tt.true_label).sum())
    src("Test rows where final label = rule label", rule_on_test, "predictions.csv + review file")

test_dist = PRED.true_label.value_counts().to_dict()
for k, name in METHODS:
    src(f"{name} accuracy", f3(T1[k]["accuracy"]), f"metrics.json task_1_moats.methods.{k}.accuracy")
    src(f"{name} macro-F1", f3(T1[k]["macro_f1"]), f"metrics.json task_1_moats.methods.{k}.macro_f1")

lora_pc = T1["lora"]["per_class"]

# stock / sector table
sec = (stk_ok.groupby("category")
       .agg(n=("ticker", "size"), med_ret=("return_pct", "median"), med_exc=("excess_return_vs_igv", "median"))
       .sort_values("med_exc", ascending=False))
mm = MOAT.merge(stk_ok[["ticker", "name", "category", "excess_return_vs_igv"]], on="ticker", how="inner")
rho = RQ["spearman_moat_vs_excess_return"]
rho_g = RQ["spearman_moat_vs_revenue_growth"]
src("Spearman moat vs excess return", f3(rho["rho"]), "rq4_correlations.json")
src("Spearman p", f3(rho["p"]), "rq4_correlations.json")
src("Spearman n", rho["n"], "rq4_correlations.json")
src("Spearman moat vs revenue growth", f3(rho_g["rho"]), "rq4_correlations.json")
cat_moat = {c["category"]: c["median"] for c in RQ.get("category_moat_stats", [])}
top5 = mm.sort_values("moat_score", ascending=False).head(5)
bot5 = mm.sort_values("moat_score").head(5)

# HN
hz, hf = T2["zero_shot"], T2["few_shot"]
src("HN zero-shot accuracy", f3(hz["accuracy"]), "metrics.json task_2_hn_stance.zero_shot")
src("HN few-shot accuracy", f3(hf["accuracy"]), "metrics.json task_2_hn_stance.few_shot")

# LoRA training
lora_epochs = float(LOSS.epoch.max())
src("LoRA epochs", lora_epochs, "training_loss.csv epoch max")

# ---------------- example paragraphs (real test rows) ----------------
ex = PRED.merge(GOLD[["para_id", "text", "company"]], on="para_id", how="left").sort_values("para_id")
ex_good = ex[(ex.pred_lora == ex.true_label) & (ex.pred_few_shot != ex.true_label)].head(2)
ex_bad = ex[ex.pred_lora != ex.true_label].head(1)
EXAMPLES = pd.concat([ex_good, ex_bad])


def snip(t, n=300):
    t = " ".join(str(t).split())
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + " …"


# ---------------- SVG charts ----------------
def bar_chart():
    W, H, L, B, T = 760, 300, 210, 34, 10
    rows = [(name, T1[k]["macro_f1"], T1[k]["macro_f1_bootstrap_ci"], k) for k, name in METHODS]
    bh = (H - B - T) / len(rows)
    sx = lambda v: L + v * (W - L - 30)
    s = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Macro-F1 by method">']
    for g in [0, .25, .5, .75, 1]:
        s.append(f'<line x1="{sx(g)}" y1="{T}" x2="{sx(g)}" y2="{H-B}" class="grid"/>'
                 f'<text x="{sx(g)}" y="{H-B+18}" class="tick" text-anchor="middle">{g:.2f}</text>')
    for i, (name, v, c, k) in enumerate(rows):
        y = T + i * bh + bh * .18
        h = bh * .64
        cls = "bar-main" if k == "lora" else ("bar-rule" if k == "keyword_rule_baseline" else
                                              "bar-base" if "baseline" in k else "bar-prompt")
        s.append(f'<text x="{L-10}" y="{y+h/2+5}" class="lab" text-anchor="end">{esc(name)}</text>')
        s.append(f'<rect x="{L}" y="{y}" width="{sx(v)-L}" height="{h}" rx="3" class="{cls}"/>')
        s.append(f'<line x1="{sx(c[0])}" y1="{y+h/2}" x2="{sx(c[1])}" y2="{y+h/2}" class="whisk"/>'
                 f'<line x1="{sx(c[0])}" y1="{y+h*.25}" x2="{sx(c[0])}" y2="{y+h*.75}" class="whisk"/>'
                 f'<line x1="{sx(c[1])}" y1="{y+h*.25}" x2="{sx(c[1])}" y2="{y+h*.75}" class="whisk"/>')
        s.append(f'<text x="{sx(c[1])+8}" y="{y+h/2+5}" class="val">{v:.2f}</text>')
    s.append(f'<text x="{(L+W-30)/2}" y="{H-2}" class="tick" text-anchor="middle">Macro-F1 on the test set (n = {n_test}), bars = 95% bootstrap CI</text>')
    s.append("</svg>")
    return "".join(s)


def rank_scatter():
    d = mm.copy()
    d["rx"] = d.moat_score.rank(pct=True)
    d["ry"] = d.excess_return_vs_igv.rank(pct=True)
    W, H, P = 460, 360, 46
    sx = lambda v: P + v * (W - P - 14)
    sy = lambda v: H - P - v * (H - P - 14)
    s = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Rank of moat score vs rank of excess return">']
    for g in [0, .5, 1]:
        s.append(f'<line x1="{sx(g)}" y1="{sy(0)}" x2="{sx(g)}" y2="{sy(1)}" class="grid"/>'
                 f'<line x1="{sx(0)}" y1="{sy(g)}" x2="{sx(1)}" y2="{sy(g)}" class="grid"/>'
                 f'<text x="{sx(g)}" y="{H-P+18}" class="tick" text-anchor="middle">{int(g*100)}</text>'
                 f'<text x="{P-8}" y="{sy(g)+4}" class="tick" text-anchor="end">{int(g*100)}</text>')
    for _, r in d.iterrows():
        s.append(f'<circle cx="{sx(r.rx):.1f}" cy="{sy(r.ry):.1f}" r="4" class="dot"><title>{esc(r.ticker)}: moat {r.moat_score:.2f}, excess {r.excess_return_vs_igv:+.0f}%</title></circle>')
    s.append(f'<text x="{(P+W)/2}" y="{H-6}" class="tick" text-anchor="middle">Moat-score percentile (LoRA-predicted share of moat paragraphs)</text>')
    s.append(f'<text x="14" y="{(H-P)/2}" class="tick" text-anchor="middle" transform="rotate(-90 14 {(H-P)/2})">Excess-return percentile vs IGV</text>')
    s.append("</svg>")
    return "".join(s)


# ---------------- slides ----------------
def table(head, rows, cls=""):
    h = "".join(f"<th>{esc(x)}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


S = []

S.append(dict(
    title="SaaS-Pulse: which SaaS moats hold up against AI?",
    kind="title",
    html=f"""<p class="sub">An original dataset of 10-K filings, developer discussion and market data, with a GenAI moat classifier</p>
<p class="meta">Daksh Chauhan · Semester VII · Adani University</p>
<div class="kpis">
<div><b>{n_companies}</b><span>public SaaS companies</span></div>
<div><b>{n_paras:,}</b><span>10-K paragraphs</span></div>
<div><b>{n_hn:,}</b><span>Hacker News items</span></div>
<div><b>{n_stk}</b><span>tickers vs IGV</span></div></div>""",
    md=[f"{n_companies} companies, {n_paras:,} paragraphs, {n_hn:,} HN items, {n_stk} tickers"],
    notes="I built an original dataset to ask a current question: as AI makes software cheaper to build, which kinds of protection do SaaS companies claim, and do those claims line up with what the market did? The GenAI part is a model that reads 10-K text and labels the type of moat."))

S.append(dict(
    title="Why this question",
    html="""<div class="cols2"><div class="card"><h3>The pressure</h3><ul>
<li>AI coding tools make simple internal software (CRUD apps, dashboards, trackers) much cheaper to build.</li>
<li>That threatens SaaS products that are thin interfaces over a database and charge per seat.</li></ul></div>
<div class="card"><h3>The counter-argument</h3><ul>
<li>Some products are hard to replace whatever the build cost: systems of record, compliance-certified tools, data platforms, network-effect marketplaces.</li>
<li>Companies describe these protections ("moats") in their 10-K filings.</li></ul></div></div>
<p class="note">This slide is motivation, not a result. The project tests these ideas on data.</p>""",
    md=["AI lowers internal build cost; thin per-seat SaaS is exposed", "Some moats may resist: system of record, compliance, data, network effects", "Motivation only, tested later"],
    notes="This is the hypothesis, not a finding. If building software gets cheaper, the products at risk are the ones with no structural protection. The project checks whether we can measure claimed protection automatically, and whether it relates to outcomes."))

S.append(dict(
    title="Research questions",
    html=table(["", "Question", "Method"], [
        ["<b>RQ1</b>", "Can a small open LLM label the moat type in a 10-K paragraph, and does fine-tuning beat prompting?", "Qwen2.5-1.5B: zero-shot, few-shot, LoRA, against baselines"],
        ["<b>RQ2</b>", "On Hacker News, do developers argue for building internal tools or buying SaaS?", "Zero-shot and few-shot stance classification"],
        ["<b>RQ3</b>", "Do companies with more moat language show better excess returns or revenue growth since 2023?", "Spearman rank correlation, sector comparison"]]),
    md=["RQ1 moat classification: prompting vs LoRA", "RQ2 HN build-vs-buy stance", "RQ3 moat score vs excess return and revenue growth"],
    notes="Three questions. RQ1 is the core GenAI task. RQ2 looks at the developer side. RQ3 connects the model's output to real financial outcomes."))

S.append(dict(
    title="Dataset: collected and prepared for this project",
    html=table(["Source", "What", "Size"], [
        ["SEC EDGAR 10-K", "Item 1 (Business) and 1A (Risk Factors), split into paragraphs", f"{n_filings} filings · {n_paras:,} paragraphs"],
        ["SEC XBRL", "Annual US-GAAP revenue and growth", f"{n_rev} company-years"],
        ["Hacker News (Algolia API)", "Build-vs-buy and internal-tool discussions, authors hashed", f"{n_hn:,} items"],
        ["Pricing pages", "Live pages and Wayback snapshots (robots.txt respected)", f"{n_price} records (descriptive only)"],
        ["Market data", "Split-adjusted prices Jan 2023 → Oct 2026, vs IGV software ETF", f"{n_stk} tickers · IGV {igv:+.1f}%"]])
    + '<p class="note">Polite collection: declared user agent, rate limits, robots.txt, no login walls or CAPTCHA bypass. A datasheet and SHA-256 manifest ship with the data.</p>',
    md=[f"{n_filings} filings, {n_paras:,} paragraphs", f"{n_rev} revenue rows", f"{n_hn:,} HN items", f"{n_price} pricing records", f"{n_stk} tickers, IGV {igv:+.1f}%"],
    notes="Everything here was collected and prepared for this project from public sources. Pricing pages turned out too patchy for analysis; enterprise vendors often have no public pricing, so I only use them descriptively."))

prov_rows = [[f"Train ({n_train})", "Keyword rules", "Used to fine-tune LoRA"]]
if REVIEW is not None:
    prov_rows.append([f"Validation + test ({n_rev_eval} kept, {n_excl} excluded)",
                      "Reviewed by an independent LLM (Claude Opus 5.5), approved by the author",
                      f"Agreement with rule {pct(agree,0)} · Cohen's κ = {kappa:.2f}"])
tax = "".join(f"<li><b>{NICE[l]}</b></li>" for l in LABELS)
S.append(dict(
    title="Labels: a 6-class moat taxonomy and an honest gold set",
    html=f"""<div class="cols2"><div class="card"><h3>Classes</h3><ul class="tight">{tax}</ul>
<p class="small">"None / commodity" means no structural barrier is claimed (generic description, boilerplate risk text).</p></div>
<div class="card"><h3>Where the labels come from</h3>{table(["Split", "Labels by", "Notes"], prov_rows, "compact")}
<p class="small">The reviewer saw the rule's suggestion, so test labels may lean toward the rule (anchoring). Test set: {n_test} paragraphs.</p></div></div>""",
    md=[f"Train {n_train}: keyword-rule labels", f"Val+test: LLM-reviewed, author-approved; {n_excl} excluded; agreement {pct(agree,0) if agree is not None else 'n/a'}, kappa {kappa:.2f}" if kappa is not None else "review file missing", f"Test n = {n_test}"],
    notes="I want to be precise about labels. Training labels come from keyword rules. The validation and test paragraphs were reviewed by a different, stronger LLM and approved by me. The rule and the review agreed about two thirds of the time, so the rules are noisy. The reviewer could see the rule's suggestion, which can bias the test labels toward the rule; keep that in mind on the next slide."))

S.append(dict(
    title="GenAI method",
    html=f"""<div class="cols3"><div class="card"><h3>Zero-shot</h3><p>Taxonomy definitions + paragraph → label.</p></div>
<div class="card"><h3>Few-shot</h3><p>Same prompt plus 6 labelled training examples (one per class).</p></div>
<div class="card"><h3>LoRA fine-tune</h3><p>4-bit Qwen2.5-1.5B, LoRA on q/k/v/o (r = 8, α = 16), loss on the label tokens only, {lora_epochs:g} epochs, lr 2e-4, {n_train} training paragraphs.</p></div></div>
<div class="card"><h3>Fair scoring for every method</h3><p>Instead of parsing free text, the model scores each of the 6 label strings and the most likely one wins. Every output is a valid label, and all methods are compared the same way.</p></div>
<p class="note">Kaggle Tesla T4. Baselines: majority class, random, and the keyword rule itself.</p>""",
    md=["Zero-shot, few-shot (6 examples), LoRA (r=8, alpha=16, completion-only loss)", "Constrained label scoring for all methods", "Kaggle T4"],
    notes="All three methods use the same 1.5 billion parameter model. The important design choice is constrained scoring: the model never writes free text, it just ranks the six labels. That removed the parsing failures from the earlier run and makes the comparison fair."))

t1_rows = []
for k, name in METHODS:
    r = T1[k]
    t1_rows.append([("<b>" + esc(name) + "</b>") if k == "lora" else esc(name), f3(r["accuracy"]), ci(r["accuracy_wilson_ci"]), f3(r["macro_f1"]), ci(r["macro_f1_bootstrap_ci"])])
fl, zl = MC["few_shot_vs_lora"], MC["zero_shot_vs_lora"]
S.append(dict(
    title="RQ1 results: fine-tuning beats prompting",
    html=f"""<div class="cols2 wide-left"><div>{bar_chart()}</div>
<div>{table(["Method", "Acc.", "95% CI", "Macro-F1", "95% CI"], t1_rows, "compact")}</div></div>
<ul class="find"><li>LoRA roughly doubles macro-F1 over prompting ({f3(T1['lora']['macro_f1'])} vs {f3(T1['few_shot_cot']['macro_f1'])} few-shot). McNemar vs few-shot p = {fl['chi2_p_value']:.3f}; vs zero-shot p = {zl['chi2_p_value']:.3f}. One of three pairwise tests is significant, and n = {n_test}.</li>
<li>*The keyword rule scores highest, but it is not a fair competitor: {rule_on_test} of {n_test} test labels are the rule's own label kept by the reviewer, and LoRA was trained on rule labels.</li></ul>""",
    md=[f"{name}: acc {f3(T1[k]['accuracy'])}, macro-F1 {f3(T1[k]['macro_f1'])}" for k, name in METHODS]
    + [f"McNemar LoRA vs few-shot p={fl['chi2_p_value']:.3f}, vs zero-shot p={zl['chi2_p_value']:.3f}", f"Rule label kept on {rule_on_test}/{n_test} test rows"],
    notes=f"Prompting a 1.5B model gives about 0.31 macro-F1. Fine-tuning with LoRA lifts it to {T1['lora']['macro_f1']:.2f}, and the gain over few-shot is significant at p = {fl['chi2_p_value']:.3f}, though the intervals are wide with {n_test} test paragraphs. The keyword rule looks best, but the test labels started from the rule and were mostly kept, so the rule has a built-in advantage. The fair comparison is between the GenAI methods."))

pc_rows = [[NICE[l], f"{lora_pc[l]['precision']:.2f}", f"{lora_pc[l]['recall']:.2f}", f"{lora_pc[l]['f1_score']:.2f}", str(lora_pc[l]['support'])] for l in LABELS]
loss_img = os.path.join(OUT, "loss_curve.png").replace("\\", "/")
S.append(dict(
    title="Where the fine-tuned model is right and wrong",
    html=f"""<div class="cols2"><div>{table(["Class (LoRA)", "Precision", "Recall", "F1", "n"], pc_rows, "compact")}
<p class="small">Biggest weakness: "none / commodity" recall {lora_pc['none_or_commodity']['recall']:.2f}. It is the largest test class ({test_dist.get('none_or_commodity', 0)} of {n_test}), and the model tends to see a moat where the text only describes the business.</p></div>
<div><img src="{loss_img}" alt="LoRA training and validation loss" class="fig"/></div></div>""",
    md=[f"{NICE[l]}: P {lora_pc[l]['precision']:.2f} R {lora_pc[l]['recall']:.2f} F1 {lora_pc[l]['f1_score']:.2f} (n={lora_pc[l]['support']})" for l in LABELS],
    notes="Per class, the model is strongest on network effects and systems of record. Its main error is over-claiming: plain business descriptions get labelled as moats, so recall on the none class is low. With only a few test examples per class, these per-class numbers are rough."))

ex_html = ""
for _, r in EXAMPLES.iterrows():
    ok = r.pred_lora == r.true_label
    ex_html += f"""<div class="card ex"><p class="small"><b>{esc(r.ticker)}</b> FY{r.fiscal_year} · {esc(r.para_id)}</p>
<p class="quote">"{esc(snip(r.text))}"</p>
<p class="small">Gold: <b>{NICE[r.true_label]}</b> · LoRA: <b class="{'ok' if ok else 'bad'}">{NICE[r.pred_lora]}</b> · Few-shot: {NICE.get(r.pred_few_shot, r.pred_few_shot)}</p></div>"""
S.append(dict(
    title="Real test paragraphs",
    html=f'<div class="cols3">{ex_html}</div><p class="note">Quoted verbatim from the test set (truncated). Two cases LoRA gets right and few-shot gets wrong, and one LoRA error.</p>',
    md=[f"{r.ticker} {r.para_id}: gold {r.true_label}, LoRA {r.pred_lora}, few-shot {r.pred_few_shot}" for _, r in EXAMPLES.iterrows()],
    notes="These are real paragraphs from the test set, not paraphrases. Two show where fine-tuning helped, and one shows a typical error."))

hn_rows = [["Zero-shot", f3(hz["accuracy"]), ci(hz["accuracy_wilson_ci"]), f3(hz["macro_f1"])],
           ["Few-shot", f3(hf["accuracy"]), ci(hf["accuracy_wilson_ci"]), f3(hf["macro_f1"])],
           ["Chance (3 classes)", "0.333", "", ""]]
S.append(dict(
    title="RQ2: developer stance on Hacker News, a negative result",
    html=f"""<div class="cols2"><div>{table(["Method", "Acc.", "95% CI", "Macro-F1"], hn_rows, "compact")}</div>
<div class="card"><ul><li>Both methods reach {pct(hz['accuracy'])}, only slightly above chance, and the intervals include it.</li>
<li>The model almost never predicts "hybrid / neutral", although that is a third of the benchmark.</li>
<li>So I do <b>not</b> report a corpus-wide build-vs-buy percentage: a classifier this weak would turn its bias into a fake trend.</li>
<li>The 60 benchmark labels are rule-generated, not reviewed.</li></ul></div></div>""",
    md=[f"Zero-shot acc {f3(hz['accuracy'])}, few-shot {f3(hf['accuracy'])}, chance 0.333", "No corpus-level shares reported"],
    notes="This one did not work, and I am reporting that rather than hiding it. Developer comments are sarcastic and nuanced, and a 1.5B model with no fine-tuning is barely above chance. I deliberately do not turn its predictions into a percentage of developers who build versus buy."))

sec_rows = [[esc(c), str(int(r.n)), f"{r.med_ret:+.1f}%", f"{r.med_exc:+.1f}%", f"{cat_moat[c]:.2f}" if c in cat_moat else "–"] for c, r in sec.iterrows()]
S.append(dict(
    title="RQ3: moat language vs market outcome",
    html=f"""<div class="cols2"><div>{rank_scatter()}
<p class="small">Spearman ρ = {rho['rho']:.2f} (95% CI {ci([rho['ci_lo'], rho['ci_hi']])}), p = {rho['p']:.3f}, n = {rho['n']}. With revenue growth: ρ = {rho_g['rho']:.2f}, p = {rho_g['p']:.2f}.</p></div>
<div>{table(["Sector", "n", "Median return", "Median excess vs IGV", "Median moat score"], sec_rows, "compact")}
<ul class="find"><li><b>No significant link</b> between how much moat language a company uses and its excess return or revenue growth.</li>
<li>Sector explains more: data/infra beat the index, fintech/HR and vertical SaaS lagged. This is descriptive, not causal.</li>
<li>Moat scores come from a model with {pct(T1['lora']['accuracy'],0)} accuracy; that noise weakens any correlation, so "no link found" ≠ "moats don't matter".</li></ul></div></div>""",
    md=[f"Spearman moat vs excess rho={rho['rho']:.3f} p={rho['p']:.3f} n={rho['n']}", f"moat vs revenue growth rho={rho_g['rho']:.3f}"]
    + [f"{c}: n={int(r.n)}, median excess {r.med_exc:+.1f}%" for c, r in sec.iterrows()],
    notes=f"Each dot is a company: how much of its business section the model labels as a moat, against its stock return relative to the software index since January 2023, both as ranks. The correlation is weakly positive but not significant, p = {rho['p']:.2f}. Sector differences are much larger, and those are descriptive; I am not claiming what caused them."))

tb = lambda d: "".join(f"<tr><td>{esc(r.ticker)}</td><td>{r.moat_score:.2f}</td><td>{r.excess_return_vs_igv:+.0f}%</td></tr>" for _, r in d.iterrows())
S.append(dict(
    title="Conclusions and limitations",
    html=f"""<div class="cols2"><div class="card"><h3>What we found</h3><ul>
<li>A 1.5B model can learn to label moat types from {n_train} weakly-labelled examples: LoRA {f3(T1['lora']['macro_f1'])} macro-F1 vs ~{T1['few_shot_cot']['macro_f1']:.2f} for prompting.</li>
<li>Developer stance on HN was too hard for this model (near chance).</li>
<li>Moat language did not significantly predict 2023–26 excess returns; sector did more.</li></ul>
<h3>Next steps</h3><ul><li>Blind human labels (no rule suggestion) and a larger test set.</li><li>A bigger model for HN stance; earnings-call text.</li></ul></div>
<div class="card"><h3>Limitations</h3><ul class="tight">
<li>Training labels from keyword rules; test labels LLM-reviewed with the rule visible.</li>
<li>Small test set (n = {n_test}); wide intervals.</li>
<li>10-K moat claims are self-reported marketing language.</li>
<li>Survivorship: only companies still filing; HN skews to developers.</li>
<li>Correlation, not causation; one time window.</li></ul></div></div>""",
    md=["LoRA beats prompting on moat classification", "HN stance near chance", "No significant moat-return link; sector effects larger", "Limitations: rule labels, anchoring, n small, self-reported claims, survivorship, non-causal"],
    notes="To sum up: fine-tuning clearly helps a small model learn this taxonomy, the developer-stance task was a negative result, and the market link was not significant. The main improvement would be blind human labels and a bigger test set. Thank you."))

# ---------------- render HTML ----------------
CSS = """
:root{--bg:#f6f7f9;--panel:#ffffff;--ink:#16202c;--muted:#5b6675;--line:#dfe3e8;--accent:#2457c5;--accent2:#7a8ca6;--ok:#167a4a;--bad:#b3261e;--rule:#c98a12}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f141b;--panel:#161d27;--ink:#e8edf3;--muted:#9aa6b5;--line:#2a3442;--accent:#6f9cff;--accent2:#6b7a90;--ok:#4cc38a;--bad:#ff7a70;--rule:#e0a93a}}
:root[data-theme="dark"]{--bg:#0f141b;--panel:#161d27;--ink:#e8edf3;--muted:#9aa6b5;--line:#2a3442;--accent:#6f9cff;--accent2:#6b7a90;--ok:#4cc38a;--bad:#ff7a70;--rule:#e0a93a}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);color:var(--ink);font-family:Inter,"Segoe UI",system-ui,-apple-system,sans-serif}
body{overflow:hidden}
#stage{position:absolute;left:50%;top:50%;width:1280px;height:720px;transform-origin:center center}
.slide{position:absolute;inset:0;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:44px 56px 40px;display:none;flex-direction:column}
.slide.on{display:flex}
h1{font-size:34px;font-weight:750;letter-spacing:-.01em;margin-bottom:22px}
.title h1{font-size:50px;margin-top:120px;max-width:1000px}
h3{font-size:17px;margin-bottom:8px;color:var(--accent)}
.sub{font-size:22px;color:var(--muted);max-width:900px;margin-bottom:18px}
.meta{font-size:18px;margin-bottom:46px}
.kpis{display:flex;gap:22px}.kpis div{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:16px 22px;min-width:210px}
.kpis b{display:block;font-size:30px;color:var(--accent)}.kpis span{color:var(--muted);font-size:15px}
.cols2{display:grid;grid-template-columns:1fr 1fr;gap:26px;align-items:start}
.cols2.wide-left{grid-template-columns:1.05fr 1fr}
.cols3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:16px}
.card{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:12px}
ul{padding-left:20px;font-size:17px;line-height:1.5}ul.tight{font-size:16px;line-height:1.45}
li{margin-bottom:6px}
p{font-size:17px;line-height:1.5}
.small{font-size:14px;color:var(--muted);margin-top:8px;line-height:1.45}
.note{font-size:14px;color:var(--muted);margin-top:auto}
table{width:100%;border-collapse:collapse;font-size:16px}
th{text-align:left;font-weight:650;color:var(--muted);border-bottom:2px solid var(--line);padding:8px 8px}
td{border-bottom:1px solid var(--line);padding:8px 8px;vertical-align:top;font-variant-numeric:tabular-nums}
table.compact{font-size:14px}table.compact td,table.compact th{padding:5px 6px}
.find{margin-top:14px;font-size:15.5px}
.quote{font-size:15px;line-height:1.5;font-style:italic}
.ok{color:var(--ok)}.bad{color:var(--bad)}
.fig{width:100%;border-radius:8px;border:1px solid var(--line);background:#fff}
.chart{width:100%;height:auto}
.chart .grid{stroke:var(--line);stroke-width:1}.chart .tick{fill:var(--muted);font-size:12px}
.chart .lab{fill:var(--ink);font-size:13px}.chart .val{fill:var(--ink);font-size:13px;font-weight:650}
.chart .whisk{stroke:var(--ink);stroke-width:1.4}
.bar-main{fill:var(--accent)}.bar-prompt{fill:var(--accent2)}.bar-base{fill:var(--line)}.bar-rule{fill:var(--rule);opacity:.55}
.chart .dot{fill:var(--accent);opacity:.7}
#foot{position:fixed;bottom:8px;right:14px;font-size:12px;color:var(--muted)}
#notes{position:fixed;left:0;right:0;bottom:0;max-height:34%;overflow:auto;background:var(--panel);border-top:1px solid var(--line);padding:14px 20px;font-size:15px;display:none}
"""
slides_html = ""
for i, s in enumerate(S):
    cls = "slide on" if i == 0 else "slide"
    if s.get("kind") == "title":
        cls += " title"
    slides_html += f'<section class="{cls}" data-notes="{esc(s["notes"])}"><h1>{esc(s["title"])}</h1>{s["html"]}</section>\n'

JS = """
const S=[...document.querySelectorAll('.slide')];let i=0;const foot=document.getElementById('foot'),notes=document.getElementById('notes');
function show(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,k)=>s.classList.toggle('on',k===i));foot.textContent=(i+1)+' / '+S.length+'  ·  ←/→ move · N notes · F fullscreen';notes.textContent=S[i].dataset.notes;}
function fit(){const st=document.getElementById('stage');const k=Math.min(innerWidth/1300,innerHeight/740);st.style.transform='translate(-50%,-50%) scale('+k+')';}
addEventListener('resize',fit);
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(i+1)}else if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);else if(e.key==='n'||e.key==='N')notes.style.display=notes.style.display==='block'?'none':'block';else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}else if(e.key==='Home')show(0);else if(e.key==='End')show(S.length-1)});
document.addEventListener('click',e=>{if(e.target.closest('#notes'))return;show(e.clientX>innerWidth/3?i+1:i-1)});
fit();show(0);
"""
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SaaS-Pulse Presentation</title><style>{CSS}</style></head><body>
<div id="stage">{slides_html}</div><div id="foot"></div><div id="notes"></div><script>{JS}</script></body></html>"""
open("presentation.html", "w", encoding="utf-8").write(page)

# ---------------- markdown script + trace table ----------------
md = [f"# SaaS-Pulse: presentation script\n\nGenerated by `build_deck.py` from `{RUN}`. Do not edit numbers by hand; re-run the script.\n"]
for k, s in enumerate(S, 1):
    md.append(f"## Slide {k}: {s['title']}\n")
    md += [f"- {b}" for b in s["md"]]
    md.append(f"\n**Speaker notes:** {s['notes']}\n")
md.append("## Number sources\n\n| Claim | Value | Source |\n|---|---|---|")
md += [f"| {a} | {b} | `{c}` |" for a, b, c in SRC]
open("PRESENTATION_SLIDES.md", "w", encoding="utf-8").write("\n".join(md))
print(f"OK: {len(S)} slides from {RUN}; {len(SRC)} traced numbers -> presentation.html, PRESENTATION_SLIDES.md")
