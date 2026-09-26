"""Governance audit s1 -- nine-layer full inventory enumerator (O-20260926-1355 / T-83 s1).

Mechanical sweep face of the CEO governance-audit order: deterministic,
zero-network, zero-mutation enumeration of every mechanism carrier across the
nine layers defined in fleet/orders/O-20260926-1355-bm-a.md. Output artifact
results/governance_audit_20260926.json is the machine-verifiable snapshot the
hand-curated inventory doc research/AUDIT-20260926-FULL.md builds on.

Discipline (order section 二): measurement FIRST -- this script only counts and
classifies carriers; it never edits any canon file. Rerun byte-identical for a
fixed --as-of date (no wall clock in output). Roles/judgments live in the doc;
here only verifiable facts: paths, sizes, headings, statuses read from
git-tracked state.

Usage:
  python scripts/governance_audit_s1.py run [--as-of 2026-09-26]
  python scripts/governance_audit_s1.py selftest
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "governance_audit_20260926.json")

SUPERSEDE_PAT = re.compile(r"取代|supersede|让号|让位|让路|作废|废止|废除|收回|superseded", re.I)


def _p(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _first_heading(path):
    """First markdown H1/H2 heading line, or first non-empty line fallback."""
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                if s.startswith("#"):
                    return s.lstrip("#").strip()
                return s[:80]
    except OSError:
        return None
    return None


def _md_items(relpaths):
    items = []
    for rel in relpaths:
        p = _p(rel)
        items.append({
            "path": rel,
            "bytes": os.path.getsize(p) if os.path.isfile(p) else 0,
            "title": _first_heading(p) if os.path.isfile(p) else None,
        })
    return items


def _glob_sorted(pattern):
    d = _p(os.path.dirname(pattern))
    pat = os.path.basename(pattern)
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(os.path.dirname(pattern), f).replace(os.sep, "/")
                  for f in os.listdir(d)
                  if os.path.isfile(os.path.join(d, f)) and re.match(pat.replace(".", r"\.").replace("*", "[^/]*"), f))


def layer_l1_judgment():
    faces = [f for f in _glob_sorted("research/*.md") if any(
        k in f for k in ("BACKTEST_SCIENCE", "SCIENCE_AUDIT", "PREREG_TEMPLATE", "QUEUE_BANDIT",
                         "STRATEGY_EVALUATION", "SAMPLE_SCIENCE", "NULL_CALIBRATION"))]
    faces += ["firm/RULES.md", "firm/SELF_REVIEW.md", "firm/POST_REVIEW.md"]
    gates_path = _p("scripts/science_gates.py")
    gate_fns = []
    if os.path.isfile(gates_path):
        with io.open(gates_path, encoding="utf-8", errors="replace") as fh:
            gate_fns = sorted(re.findall(r"^def ([a-zA-Z0-9_]+)\(", fh.read(), re.M))
    return {"carriers": _md_items(faces), "science_gates_functions": gate_fns}


def layer_l2_canon_docs():
    canon = ["README.md", "PLAN.md", "CODELY.md",
            "firm/RULES.md", "firm/OPERATING_PLAN.md", "firm/org_chart.md",
            "firm/SPM_REGISTER.md", "firm/STABLE_PROFIT_MODEL.md",
            "firm/PRODUCT_MATRIX.md", "research/PROFIT_MODEL_MAP.md",
            "research/STRATEGY_LIBRARY.md", "research/HANDOVER.md",
            "research/BACKTEST_SCIENCE.md", "research/BACKTEST_PLAN.md",
            "research/CEO_HANDBOOK.md", "research/RESEARCH_MECHANISM.md",
            "research/SYSTEM_LOGIC.md", "research/COMPUTE_AUDIT.md",
            "firm/DEV_AUTOMATION.md", "firm/TECH.md", "firm/LOCAL_FIRST.md"]
    return {"carriers": _md_items(canon)}


def layer_l3_org():
    p = _p("firm/org_chart.md")
    depts = []
    if os.path.isfile(p):
        with io.open(p, encoding="utf-8", errors="replace") as fh:
            depts = [l.strip().lstrip("#").strip() for l in fh
                     if re.match(r"^#{2,3} ", l.strip())]
    return {"org_chart_sections": depts}


def layer_l4_product_lines():
    p = _p("firm/PRODUCT_MATRIX.md")
    rows = []
    if os.path.isfile(p):
        with io.open(p, encoding="utf-8", errors="replace") as fh:
            for l in fh:
                if l.strip().startswith("|") and not set(l.strip()) <= set("|-: "):
                    rows.append(" ".join(x.strip() for x in l.strip().strip("|").split("|") if x.strip())[:120])
    return {"matrix_rows": rows, "carriers": _md_items(["firm/PRODUCT_MATRIX.md", "firm/STABLE_PROFIT_MODEL.md", "research/PROFIT_MODEL_MAP.md"])}


def layer_l5_lifecycle():
    cand = [f for f in _glob_sorted("research/*.md") + _glob_sorted("firm/*.md") if any(
        k in f for k in ("PROMOTION", "ADMISSION", "L3_ACTIVATION", "LANDING_HOOKS",
                         "PAPER_GUARD", "RETRO_PAPER", "PROFILE_CARDS", "hr"))]
    cand += ["firm/hr.py", "docs/CEO_APPROVALS.md"]
    return {"carriers": _md_items(cand),
            "live_faces": [f for f in _glob_sorted("live/*.py")]}


def layer_l6_account_families():
    fams = {}
    res = _p("results")
    if os.path.isdir(res):
        for d in sorted(os.listdir(res)):
            dp = os.path.join(res, d)
            if os.path.isdir(dp) and any(k in d for k in
                    ("paper", "prospect", "aggr", "alloc", "grid", "retro")):
                fams[d] = sorted(f for f in os.listdir(dp)
                                 if os.path.isfile(os.path.join(dp, f)))[:12]
    return {"family_dirs": {k: {"n_files": len(v), "sample": v} for k, v in fams.items()},
            "carriers": _md_items([f for f in _glob_sorted("research/*.md") if any(
                k in f for k in ("AGGR", "ALLOC", "GRID", "PROSPECT", "PROFILE"))])}


def layer_l7_pipeline():
    pool = []
    pp = _p("results/runnable_pool.json")
    if os.path.isfile(pp):
        d = json.load(io.open(pp, encoding="utf-8-sig"))
        pool = [{"id": e.get("id"), "status": e.get("status")} for e in d.get("entries", [])]
    preregs = [f for f in _glob_sorted("research/*.md") if "PREREG" in f]
    bandit = "results/bandit_queue.json"
    return {"pool_entries": pool,
            "prereg_docs": len(preregs),
            "bandit_queue_present": os.path.isfile(_p(bandit)),
            "carriers": _md_items(["research/BACKTEST_PLAN.md", "research/QUEUE_BANDIT.md",
                                   "research/POOL_AUDIT.md", "research/COMPUTE_AUDIT.md",
                                   "research/PREREG_TEMPLATE.md", "research/RESEARCH_MECHANISM.md"])}


def layer_l8_fleet():
    tools = sorted(f.replace(os.sep, "/") for f in os.listdir(_p("Tools"))
                   if f.lower().endswith((".ps1", ".py", ".txt", ".bat"))) if os.path.isdir(_p("Tools")) else []
    fleet_md = _glob_sorted("fleet/*.md")
    machines = _glob_sorted("fleet/machines/*.json")
    inbox = len([f for f in os.listdir(_p("fleet/inbox")) if f.endswith(".md")]) if os.path.isdir(_p("fleet/inbox")) else 0
    scripts_n = len([f for f in os.listdir(_p("scripts")) if f.endswith(".py")]) if os.path.isdir(_p("scripts")) else 0
    return {"tools_files": tools, "fleet_md": _md_items(fleet_md),
            "machine_heartbeats": machines, "inbox_open_msgs": inbox,
            "scripts_py_count": scripts_n}


def layer_l9_orders():
    od = _p("fleet/orders")
    orders = []
    for f in sorted(os.listdir(od)):
        if not f.endswith(".md") or f == "README.md":
            continue
        rel = "fleet/orders/" + f
        p = _p(rel)
        sup = None
        with io.open(p, encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
        m = SUPERSEDE_PAT.search(txt)
        if m:
            sup = m.group(0)
        orders.append({"file": f, "bytes": os.path.getsize(p), "title": _first_heading(p),
                       "supersession_face": sup})
    return {"orders": orders, "n_orders": len(orders)}


def run(as_of):
    data = {
        "as_of": as_of,
        "ticket": "T-2026-09-26-83 s1",
        "order": "O-20260926-1355",
        "L1_judgment": layer_l1_judgment(),
        "L2_canon_docs": layer_l2_canon_docs(),
        "L3_org": layer_l3_org(),
        "L4_product_lines": layer_l4_product_lines(),
        "L5_lifecycle": layer_l5_lifecycle(),
        "L6_account_families": layer_l6_account_families(),
        "L7_pipeline": layer_l7_pipeline(),
        "L8_fleet": layer_l8_fleet(),
        "L9_orders": layer_l9_orders(),
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("written", OUT)
    print("L9 orders:", data["L9_orders"]["n_orders"],
          "| research md:", len(_glob_sorted("research/*.md")),
          "| pool entries:", len(data["L7_pipeline"]["pool_entries"]))
    return data


def selftest():
    import tempfile
    ok = []
    # [1] first-heading extractor on hermetic fixture
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "x.md")
        with io.open(fp, "w", encoding="utf-8") as fh:
            fh.write("\n# 标题甲\n\n正文\n")
        ok.append(_first_heading(fp) == "标题甲")
    # [2] supersede pattern hits hermetic text, misses plain
    ok.append(bool(SUPERSEDE_PAT.search("本令取代 O-123")))
    ok.append(not SUPERSEDE_PAT.search("正常文本无关键词"))
    # [3] nine layers present + structural invariants
    d = json.load(io.open(OUT, encoding="utf-8-sig"))
    keys = [k for k in d if k.startswith("L")]
    ok.append(len(keys) == 9)
    od = _p("fleet/orders")
    real = len([f for f in os.listdir(od) if f.endswith(".md") and f != "README.md"])
    ok.append(d["L9_orders"]["n_orders"] == real)
    ok.append(d["L7_pipeline"]["prereg_docs"] >= 14)  # measured 2026-09-26: 14 PREREG docs
    # [4] determinism: rerun byte-identical (same as_of)
    before = io.open(OUT, "rb").read()
    run(d["as_of"])
    after = io.open(OUT, "rb").read()
    ok.append(before == after)
    print("selftest:", "ALL PASS" if all(ok) else "FAIL", "(%d legs)" % len(ok))
    if not all(ok):
        print("legs:", ok)
        sys.exit(1)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    as_of = "2026-09-26"
    if "--as-of" in sys.argv:
        as_of = sys.argv[sys.argv.index("--as-of") + 1]
    if cmd == "run":
        run(as_of)
    elif cmd == "selftest":
        if not os.path.isfile(OUT):
            run(as_of)
        selftest()
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
