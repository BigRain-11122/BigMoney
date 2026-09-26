"""Governance audit s2 -- conflict/duplication/dead-face detector (O-20260926-1355 / T-83 s2).

Mechanical detection face of the CEO governance-audit order, slice 2. Ten
detectors D1-D10 map one-to-one onto the ten s2 observations frozen in
research/AUDIT-20260926-FULL.md "s2 输入汇总" table (r267). Every detector is
deterministic, zero-network, zero-mutation: this script NEVER edits any canon
file -- findings are facts plus candidates; adjudication and landing belong to
the GM s3 faces (discipline 1 of O-20260926-1355).

Output artifact results/governance_s2_<asof>.json; rerun byte-identical for a
fixed --as-of (no wall clock, no mtime, no git subprocess in output).

Usage:
  python scripts/governance_audit_s2.py run [--as-of 2026-09-26]
  python scripts/governance_audit_s2.py selftest
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "governance_s2_20260926.json")

SUPERSEDE_WORDS = re.compile(
    r"取代|supersede[d]?|作废|废止|废除|收回|撤回|让路|让位|让号|收回令|已废|废除令", re.I)
OID_PAT = re.compile(r"O-\d{8}-\d{4}(?:-[a-z0-9]+)?")
PATH_PAT = re.compile(
    r"(?:research|firm|scripts|results|Tools|fleet|engine|strategies|data|live|logs|screening|knowledge|docs|monitor)/"
    r"[A-Za-z0-9_\-./]*[A-Za-z0-9_\-]+\.(?:md|py|jsonl|json|ps1|txt|csv|yml|yaml|vbs)(?![A-Za-z0-9])")
GLYPHS = set("\u2705\U0001F7E1\u2B1C\U0001F534")  # green / yellow / white / red squares
LINE_TS_PAT = re.compile(r"(\d{4}-\d{2}-\d{2})[ T]?(\d{2}:\d{2})?")

CORPUS_DIRS = ["firm", "research", "scripts", "Tools", "fleet", "docs", "logs",
               "monitor", "engine", "strategies", "live", "results"]
CORPUS_EXT = {".md", ".py", ".json", ".ps1", ".txt", ".vbs"}
CORPUS_SKIP = {"__pycache__", ".git", ".codely-cli", "bin", "skills"}
CORPUS_MAX_BYTES = 2 * 1024 * 1024

# ---------------------------------------------------------------- helpers

def _p(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _read(rel, errors="replace"):
    try:
        with io.open(_p(rel), encoding="utf-8", errors=errors) as fh:
            return fh.read()
    except OSError:
        return ""


def _exists(rel):
    return os.path.exists(_p(rel))


def _md_files(*subdirs):
    out = []
    for sub in subdirs:
        d = _p(sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(".md") and os.path.isfile(os.path.join(d, f)):
                out.append(sub.rstrip("/") + "/" + f)
    return out


def _corpus():
    """All trackable text files under governance dirs (read-only, capped)."""
    files = []
    for sub in CORPUS_DIRS:
        base = _p(sub)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in CORPUS_SKIP]
            for f in sorted(filenames):
                if os.path.splitext(f)[1].lower() not in CORPUS_EXT:
                    continue
                full = os.path.join(dirpath, f)
                try:
                    if os.path.getsize(full) > CORPUS_MAX_BYTES:
                        continue
                    files.append(full)
                except OSError:
                    continue
    for f in sorted(os.listdir(ROOT)):
        full = os.path.join(ROOT, f)
        if os.path.isfile(full) and os.path.splitext(f)[1].lower() in CORPUS_EXT:
            files.append(full)
    return files


def _corpus_texts():
    for full in _corpus():
        try:
            with io.open(full, encoding="utf-8", errors="replace") as fh:
                yield os.path.relpath(full, ROOT).replace(os.sep, "/"), fh.read()
        except OSError:
            continue


def _glyphs(text):
    return sorted(ch for ch in text if ch in GLYPHS)


# ---------------------------------------------------------------- D1..D10

JUDGMENT_FACES = [
    ("BACKTEST_SCIENCE", re.compile(r"BACKTEST_SCIENCE")),
    ("science_gates", re.compile(r"science_gates")),
    ("g1_prime_v2/g2_registration_v2", re.compile(r"g1_prime_v2|g2_registration_v2")),
    ("G1'/G2/G3 chain", re.compile(r"G1'|G2[ _-]?(?:门禁|gate)|G3[ _-]?(?:门禁|gate)")),
    ("J1-J5 SPM", re.compile(r"\bJ[1-5]\b")),
    ("hr.py appraisal", re.compile(r"hr\.py")),
    ("anchor gate", re.compile(r"锚定门|anchor gate|ANCHOR")),
    ("POST_REVIEW", re.compile(r"POST_REVIEW|post_review")),
    ("SELF_REVIEW", re.compile(r"SELF_REVIEW|self_review")),
    ("SCIENCE_AUDIT", re.compile(r"SCIENCE_AUDIT|science_audit")),
]


def d1_judgment_face_matrix():
    """Observation 1 (L1): per judgment carrier, which judgment faces it cites."""
    carriers = _md_files("research", "research/shortline", "research/market_call")
    rows = {}
    prereg_zero_face = []
    for rel in carriers:
        text = _read(rel)
        faces = [name for name, pat in JUDGMENT_FACES if pat.search(text)]
        rows[rel] = faces
        fname = os.path.basename(rel)
        if "PREREG" in fname.upper() and not faces:
            prereg_zero_face.append(rel)
    return {"n_carriers": len(rows),
            "matrix": rows,
            "prereg_with_zero_judgment_face_ref": sorted(prereg_zero_face)}


def d2_dead_pointers():
    """Observation 2 (L2): canon-doc inter-pointer integrity (existence probe).
    Missing targets are triaged: template placeholders, inbox processed-moves
    (benign per fleet inbox protocol), relocated candidates (same basename
    exists elsewhere -> wrong-dir pointer candidate), true missing."""
    canon = ["README.md", "PLAN.md"] + _md_files("firm", "docs") + \
        ["research/" + os.path.basename(x) for x in _md_files("research")]
    seen = set()
    n_refs = 0
    raw_missing = {}
    for rel in sorted(set(canon)):
        text = _read(rel)
        for m in PATH_PAT.finditer(text):
            target = m.group(0)
            if target.endswith(".") or "{" in target or "*" in target:
                continue
            if (rel, target) in seen:
                continue
            seen.add((rel, target))
            n_refs += 1
            if not _exists(target):
                raw_missing.setdefault(target, []).append(rel)
    basenames = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [x for x in dirnames
                       if x not in {".git", "__pycache__", ".codely-cli"}]
        for f in filenames:
            basenames.setdefault(f, []).append(
                os.path.relpath(os.path.join(dirpath, f), ROOT).replace(os.sep, "/"))
    classified = {"template_placeholder": {}, "inbox_processed_move": {},
                  "relocated_candidate": {}, "true_missing": {}}
    for target, srcs in sorted(raw_missing.items()):
        if "YYYY" in target or ".." in target or "xxx" in target:
            classified["template_placeholder"][target] = sorted(srcs)
            continue
        if target.startswith("fleet/inbox/") and \
                _exists("fleet/inbox/processed/" + os.path.basename(target)):
            classified["inbox_processed_move"][target] = sorted(srcs)
            continue
        base = os.path.basename(target)
        found = sorted(set(basenames.get(base, [])))[:3]
        if found:
            classified["relocated_candidate"][target] = {
                "cited_by": sorted(srcs), "same_basename_at": found}
        else:
            classified["true_missing"][target] = sorted(srcs)
    return {"n_pointer_refs_checked": n_refs,
            "n_missing_raw": len(raw_missing),
            "missing": classified}


def d3_handover_census():
    """Observation 3 (L2): HANDOVER.md volume/reference-face census."""
    rel = "research/HANDOVER.md"
    text = _read(rel)
    refs = 0
    citing = []
    for crel, ctext in _corpus_texts():
        if crel == rel:
            continue
        if "HANDOVER" in ctext:
            refs += 1
            citing.append(crel)
    return {"bytes": len(text.encode("utf-8")),
            "lines": text.count("\n"),
            "headings": len(re.findall(r"(?m)^#", text)),
            "files_citing_it": refs,
            "citing_sample": sorted(citing)[:12]}


KPI_LINE_TOKENS = ["交易线", "配置线", "激进线", "CN", "野路子", "组合", "期权", "债券",
                   "事件", "龙虎榜", "短线", "回放", "战报", "研究", "外调"]


def _cell_after(text, marker):
    i = text.find(marker)
    if i < 0:
        return ""
    return text[i:i + 400]


def d4_kpi_lag_diff():
    """Observation 4 (L3): mandate vs KPI column token diff (mechanical face).
    Row-level match on the org_chart department table (| 部门 | mandate | 域 |
    KPI | 钩子 | 升级线 |) -- ASCII tree art is not a table row."""
    text = _read("firm/org_chart.md")
    out = {}
    for dept in ("研究部", "总经办"):
        row = None
        for line in text.split("\n"):
            s = line.strip()
            if s.startswith("|") and re.match(r"^\|\s*" + dept + r"\s*\|", s):
                row = s
                break
        if row is None:
            out[dept] = {"row_found": False}
            continue
        parts = [p.strip() for p in row.split("|") if p.strip()]
        mandate_seg = parts[1] if len(parts) > 1 else ""
        kpi_seg = parts[3] if len(parts) > 3 else ""
        in_mandate_not_kpi = [t for t in KPI_LINE_TOKENS
                              if t in mandate_seg and t not in kpi_seg]
        out[dept] = {"row_found": True, "mandate_len": len(mandate_seg),
                     "kpi_len": len(kpi_seg),
                     "tokens_in_mandate_absent_kpi": in_mandate_not_kpi}
    return out


STATUS_TOKENS = ["交易线", "配置线", "激进线", "CN", "野路子", "期权", "转债",
                 "商品期货", "金融期货", "PROSPECT", "GRID", "动量", "债券", "事件驱动"]


def d5_status_contradiction_candidates():
    """Observation 5 (L4/L7): same line-token with different status glyphs
    across PRODUCT_MATRIX / PROFIT_MODEL_MAP / STRATEGY_LIBRARY."""
    docs = ["firm/PRODUCT_MATRIX.md", "research/PROFIT_MODEL_MAP.md",
            "research/STRATEGY_LIBRARY.md"]
    per_doc = {}
    for rel in docs:
        lines = _read(rel).split("\n")
        hit = {}
        for line in lines:
            g = _glyphs(line)
            if not g:
                continue
            for tok in STATUS_TOKENS:
                if tok in line:
                    hit.setdefault(tok, set()).update(g)
        per_doc[rel] = {t: sorted(g) for t, g in hit.items()}
    candidates = []
    for tok in STATUS_TOKENS:
        faces = [(rel, per_doc[rel][tok]) for rel in docs if tok in per_doc[rel]]
        if len(faces) < 2:
            continue
        glyphsets = [frozenset(g) for _, g in faces]
        if len(set(map(frozenset, [frozenset(x) for x in glyphsets]))) > 1 and \
                all(g for _, g in faces):
            # differing non-empty glyph sets across >=2 docs = candidate
            candidates.append({"token": tok,
                               "faces": {rel: g for rel, g in faces},
                               "note": "glyph sets differ across docs; candidate for GM adjudication"})
    return {"per_doc": per_doc, "candidates": candidates}


D6_STAGES = [
    ("judgment_constitution", "research/BACKTEST_SCIENCE.md"),
    ("judgment_shared_lib", "scripts/science_gates.py"),
    ("paper_engine", "live/paper.py"),
    ("hr_appraisal", "firm/hr.py"),
    ("admission_intake", "scripts/ce_admission_intake.py"),
    ("ceo_approval_ledger", "docs/CEO_APPROVALS.md"),
    ("live_sim_gateway", "live/gateway.py"),
    ("rules_top_law", "firm/RULES.md"),
]


def d6_lifecycle_carrier_presence():
    """Observation 6 (L5): five-stage lifecycle carrier presence probe."""
    return [{"stage": s, "carrier": p, "present": _exists(p)} for s, p in D6_STAGES]


D7_FAMILIES = [
    ("traders_registered", "firm/traders"),
    ("paper_core", "results/paper"),
    ("prospect_paper", "results/prospect_paper"),
    ("prospect_g2", "results/prospect_g2"),
    ("prospect_promotion", "results/prospect_promotion"),
    ("aggr_paper", "results/aggr_paper"),
    ("alloc_paper", "results/alloc_paper"),
    ("grid_paper", "results/grid_paper"),
    ("paper_export", "results/paper_export"),
    ("retro_paper_2026", "results/retro_paper_2026"),
    ("g25_battalion", "results/g25"),
]


def d7_account_family_census():
    """Observation 7 (L6): paper-account family registry census (existence+n)."""
    rows = []
    for name, rel in D7_FAMILIES:
        p = _p(rel)
        if os.path.isdir(p):
            n = len(os.listdir(p))
            rows.append({"family": name, "dir": rel, "present": True, "entries": n})
        else:
            rows.append({"family": name, "dir": rel, "present": False, "entries": 0})
    return rows


def d8_oneshot_resolver_parking():
    """Observation 8 (L8): one-shot resolvers parked in Tools/ canon position.
    Detection only -- archive-not-delete (R1 live-ledger law) is a GM s3 face."""
    parked = []
    d = _p("Tools")
    pat = re.compile(r"^_r\d+.*\.py$|^resolve_.*\.py$")
    for f in sorted(os.listdir(d)):
        if pat.match(f):
            parked.append(f)
    corpus = list(_corpus_texts())
    unreferenced = []
    for f in parked:
        hits = [rel for rel, text in corpus
                if f in text and rel != "Tools/" + f]
        if not hits:
            unreferenced.append(f)
    results_shots = [f for f in os.listdir(_p("results"))
                     if re.match(r"^_r\d+.*\.py$", f)]
    return {"tools_oneshot_parked": sorted(parked),
            "tools_oneshot_unreferenced_elsewhere": sorted(unreferenced),
            "results_oneshot_count": len(results_shots)}


def _order_files():
    d = _p("fleet/orders")
    return sorted(f for f in os.listdir(d)
                  if f.startswith("O-") and f.endswith(".md"))


def d9_supersession_chain_map():
    """Observation 9 (L9): supersession chain edges from order full text.
    Keyword lines are triaged: order-to-order (explicit O-id target),
    mechanism-amendment candidate (carrier named, no order id), prose hit."""
    files = _order_files()
    ids = {f[:-3] for f in files}
    edges = []
    triage = []
    for f in files:
        oid = f[:-3]
        text = _read("fleet/orders/" + f)
        for line in text.split("\n"):
            if not SUPERSEDE_WORDS.search(line):
                continue
            s = line.strip()
            targets = {m.group(0) for m in OID_PAT.finditer(s)} - {oid}
            if targets:
                kind = "order_to_order"
                for tgt in sorted(targets):
                    edges.append({"superseder": oid, "target": tgt, "line": s[:120]})
            elif PATH_PAT.search(s) or re.search(r"[「【]", s):
                kind = "mechanism_amendment_candidate"
            else:
                kind = "prose_hit"
            triage.append({"order": oid, "kind": kind, "line": s[:120]})
    seen, uniq = set(), []
    for e in edges:
        k = (e["superseder"], e["target"], e["line"])
        if k not in seen:
            seen.add(k)
            uniq.append(e)
    dangling = sorted({e["target"] for e in uniq if e["target"] not in ids})
    superseded = sorted({e["target"] for e in uniq})
    void_orders = sorted({t["order"] for t in triage})
    return {"n_orders": len(files),
            "edges": uniq,
            "superseded_ids": superseded,
            "void_language_orders": void_orders,
            "keyword_line_triage": triage,
            "dangling_targets": dangling}


def d10_stale_citation_exposure(chain):
    """Observation 10 (L9): citations of superseded ids AFTER supersession date
    in round reports (line-timestamp filtered) + canon-doc citation faces."""
    reports = ["logs/iteration-loop/round_reports.md",
               "logs/iteration-loop/round_reports-bm-a.md",
               "logs/iteration-loop/round_reports-bm-c.md"]
    canon_docs = _md_files("research", "firm", "docs")
    superseder_date = {}
    for e in chain["edges"]:
        d = e["superseder"].split("-")[1]  # O-YYYYMMDD-...
        superseder_date[e["target"]] = min(
            d, superseder_date.get(e["target"], "99999999"))
    stale_hits = []
    for rel in reports:
        text = _read(rel, errors="replace")
        if not text:
            continue
        for i, line in enumerate(text.split("\n"), 1):
            m = LINE_TS_PAT.search(line[:24])
            if not m:
                continue
            ldate = m.group(1)
            for m2 in OID_PAT.finditer(line):
                oid = m2.group(0)
                if oid in superseder_date and ldate >= superseder_date[oid]:
                    stale_hits.append({"file": rel, "line_no": i,
                                       "order": oid,
                                       "superseded_since": superseder_date[oid],
                                       "line": line.strip()[:120]})
    canon_cites = {}
    for rel in canon_docs:
        text = _read(rel)
        for m2 in OID_PAT.finditer(text):
            oid = m2.group(0)
            if oid in superseder_date:
                canon_cites.setdefault(oid, []).append(rel)
    return {"n_superseded_ids": len(superseder_date),
            "round_report_stale_hits": stale_hits,
            "canon_doc_citations_of_superseded": {k: sorted(set(v)) for k, v
                                                  in sorted(canon_cites.items())}}


# ---------------------------------------------------------------- run/selftest

def run(as_of):
    d9 = d9_supersession_chain_map()
    out = {
        "as_of": as_of,
        "ticket": "T-2026-09-26-83 s2 (O-20260926-1355 discipline 2: detection only, zero canon edits)",
        "generator": "scripts/governance_audit_s2.py",
        "D1_judgment_face_matrix": d1_judgment_face_matrix(),
        "D2_dead_pointers": d2_dead_pointers(),
        "D3_handover_census": d3_handover_census(),
        "D4_kpi_lag_diff": d4_kpi_lag_diff(),
        "D5_status_contradiction_candidates": d5_status_contradiction_candidates(),
        "D6_lifecycle_carrier_presence": d6_lifecycle_carrier_presence(),
        "D7_account_family_census": d7_account_family_census(),
        "D8_oneshot_resolver_parking": d8_oneshot_resolver_parking(),
        "D9_supersession_chains": d9,
        "D10_stale_citation_exposure": d10_stale_citation_exposure(d9),
    }
    out["summary_counts"] = {
        "D1_carriers": out["D1_judgment_face_matrix"]["n_carriers"],
        "D1_prereg_zero_face": len(out["D1_judgment_face_matrix"]["prereg_with_zero_judgment_face_ref"]),
        "D2_missing_raw": out["D2_dead_pointers"]["n_missing_raw"],
        "D2_template": len(out["D2_dead_pointers"]["missing"]["template_placeholder"]),
        "D2_inbox_moved": len(out["D2_dead_pointers"]["missing"]["inbox_processed_move"]),
        "D2_relocated": len(out["D2_dead_pointers"]["missing"]["relocated_candidate"]),
        "D2_true_missing": len(out["D2_dead_pointers"]["missing"]["true_missing"]),
        "D5_candidates": len(out["D5_status_contradiction_candidates"]["candidates"]),
        "D6_absent_stages": sum(1 for r in out["D6_lifecycle_carrier_presence"] if not r["present"]),
        "D7_absent_families": sum(1 for r in out["D7_account_family_census"] if not r["present"]),
        "D8_parked": len(out["D8_oneshot_resolver_parking"]["tools_oneshot_parked"]),
        "D8_unreferenced": len(out["D8_oneshot_resolver_parking"]["tools_oneshot_unreferenced_elsewhere"]),
        "D9_edges": len(d9["edges"]),
        "D9_void_orders": len(d9["void_language_orders"]),
        "D10_stale_hits": len(out["D10_stale_citation_exposure"]["round_report_stale_hits"]),
    }
    path = OUT.replace("20260926", as_of.replace("-", ""))
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    sys.stdout.write("wrote %s\nsummary %s\n" %
                     (os.path.relpath(path, ROOT), json.dumps(out["summary_counts"], ensure_ascii=False)))
    return 0


def selftest():
    """Hermetic pure-function fixtures (serialized-form inputs per r253 law)
    + repo-integration invariants that must hold on every run."""
    ok = 0
    # [1] path extraction: real path found, glob/placeholder excluded,
    # .jsonl not truncated to .json (detector self-guard)
    text = "see research/FOO.md and bar/*.py and {tpl}.json plus scripts/zz.py " \
           "plus results/post_review.jsonl tail"
    got = [m.group(0) for m in PATH_PAT.finditer(text)]
    assert got == ["research/FOO.md", "scripts/zz.py", "results/post_review.jsonl"], got
    ok += 1
    # [2] supersede line parsing: target extracted, self excluded
    line = "本令取代 O-20260924-1136 全部内容；O-20260924-1136 与旧 O-20260923-2210 无关"
    assert SUPERSEDE_WORDS.search(line)
    tgts = [m.group(0) for m in OID_PAT.finditer(line)]
    assert tgts == ["O-20260924-1136", "O-20260924-1136", "O-20260923-2210"], tgts
    ok += 1
    # [3] glyph extraction
    assert _glyphs("✅ 在产 🟡 半空白") == ["\u2705", "\U0001F7E1"]
    ok += 1
    # [4] line-timestamp parsing for stale-citation filter
    m = LINE_TS_PAT.search("2026-09-26 19:00 | r267 | ...")
    assert m and m.group(1) == "2026-09-26", m and m.groups()
    ok += 1
    # [5] judgment-face fixture
    fx = "判据面引用 science_gates 与 BACKTEST_SCIENCE §D6"
    faces = [n for n, pat in JUDGMENT_FACES if pat.search(fx)]
    assert "BACKTEST_SCIENCE" in faces and "science_gates" in faces, faces
    ok += 1
    # [6] KPI token diff fixture
    mandate, kpi = "交易线 配置线 激进线 CN 野路子", "新知识入库量"
    diff = [t for t in KPI_LINE_TOKENS if t in mandate and t not in kpi]
    assert "交易线" in diff and "野路子" in diff, diff
    ok += 1
    # [7] integration: repo faces the detectors assume
    assert len(_order_files()) >= 83, "orders dir shrank"
    assert _exists("firm/org_chart.md") and _exists("research/BACKTEST_SCIENCE.md")
    ok += 1
    # [8] integration: D9 edges reference real order ids (dangling recorded, not crashed)
    chain = d9_supersession_chain_map()
    assert isinstance(chain["edges"], list) and chain["n_orders"] >= 83
    ok += 1
    # [9] corpus reachable and non-trivial
    n = sum(1 for _ in _corpus_texts())
    assert n > 100, n
    ok += 1
    print("governance_audit_s2 selftest: %d/9 PASS" % ok)
    return 0


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(__doc__)
        return 2
    if argv[1] == "selftest":
        return selftest()
    if argv[1] == "run":
        as_of = "2026-09-26"
        if "--as-of" in argv:
            as_of = argv[argv.index("--as-of") + 1]
        return run(as_of)
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
