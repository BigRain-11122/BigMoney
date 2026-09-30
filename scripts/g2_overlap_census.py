# -*- coding: utf-8 -*-
"""G2_OVERLAP_CENSUS_P1 -- G2 three-mine factor faces x in-repo adjudicated
families: formula-level overlap census (cheap census gate paradigm).

Prereg (frozen BEFORE this run): research/G2_OVERLAP_CENSUS_P1.md
  -- O-20260930-2054 supply-face window <=48h; GITHUB_MINING_SUPPLY_G2.md sec.4.1
Zero backtest / zero network / zero engine / zero nulls / zero seeds.
Census/verify precedent (TSGATE-P1 / GATE-RECHECK-A158): measurement face,
NOT registration; trials_ledger +0; marks +0.

Four-state classification per face (prereg sec.4, frozen):
  DUP-NUMBER-VERIFIED : number-space collision + formula dual-write consistent
                        -> cite in-repo verdict, NO re-burn
  DUP-FAMILY-DRIFT    : name/number collision but formula legs disagree
  NEW-FACE            : zero collision -> FACTOR_CENSUS_REGISTRY candidate (H rows)
  UNVERIFIABLE        : formula sources missing/unparseable -> parked, no pool

Formula verification legs (prereg sec.3):
  WQ101   : M1 alpha101 formula_latex vs docstring vs CN-header (internal
            dual-write) + M3 alphas.py same-number docstring (independent
            third-party cross, 15 overlaps expected).
  GTJA191 : M1 gtja191 three-source internal dual-write (M2 PDF not machine-
            readable; honest leg = internal consistency + number-space).
  A158    : name-root+window -> uppercase vs Qlib-verbatim 157-name set from
            scripts/a158_tsgate_probe.alpha158_factors (single-source import,
            tiny synthetic df call -- no anchor-gate side effects); dual-write
            via meta formula_latex vs docstring; qlib_semantics_drift_risk
            flag is a DISCLOSURE face (beta10 precedent), not a classifier.
  ACADEMIC/FUNDAMENTAL : frozen token-substring kinship rule vs ENGINE_FACES 28
            (+ZOO builder names); whitelist exemptions with reasons.

Usage:
  python scripts/g2_overlap_census.py run       # the census
  python scripts/g8_overlap_census.py selftest  # (typo-safe alias below)
  python scripts/g2_overlap_census.py selftest
"""
import ast
import csv
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

TOOLSTACK_REPOS = os.path.abspath(os.path.join(
    ROOT, "..", "toolstack", "repos"))
M1_ZOO = os.path.join(TOOLSTACK_REPOS, "Vibe-Trading",
                      "agent", "src", "factors", "zoo")
M3_ALPHAS = os.path.join(TOOLSTACK_REPOS, "Multi-factor-Model-for-Stock-Selection",
                         "src", "alphas.py")
WQ101_CSV = os.path.join(ROOT, "research", "shortline", "wq101_ic_results.csv")
GTJA191_CSV = os.path.join(ROOT, "research", "shortline", "gtja191_ic_results.csv")
A158_CELLS_CSV = os.path.join(ROOT, "research", "shortline", "a158_truegap_ic_cells.csv")
REGISTRY_MD = os.path.join(ROOT, "research", "FACTOR_CENSUS_REGISTRY.md")
OUT_JSON = os.path.join(ROOT, "results", "g2_overlap_census_p1.json")

EVIDENCE_CUTOFF = "2026-09-30"          # prereg sec.2 (mine install state + verdict files)
M1_ANCHORS = {                          # r492 ls-remote verified
    "M1_Vibe-Trading": "18027a0c2b97bd41ac38a0e269799e485bb457d3",
    "M3_Multi-factor-Model-for-Stock-Selection": "ad6927bce30f04f6dea5bc214c209d36ef22ac40",
}
TIME_BUDGET_S = 180                     # prereg sec.0 cap (O-1901 item-3 lawful stop)

# ---------------------------------------------------------------- helpers
_FUNC_ALIASES = [
    (r"ts_argmax", "argmax"), (r"ts_argmin", "argmin"), (r"ts_rank", "tsrank"),
    (r"ts_corr", "corr"), (r"ts_cov", "cov"), (r"ts_max", "max"),
    (r"ts_min", "min"), (r"ts_mean", "mean"), (r"ts_std", "std"),
    (r"ts_sum", "sum"), (r"ts_delta", "delta"), (r"decay_linear", "decay"),
    (r"signed_power", "signedpower"), (r"safe_div", "div"),
    (r"stddev", "std"), (r"correlation", "corr"), (r"covariance", "cov"),
]
_VAR_ALIASES = [
    (r"market_cap", "cap"), (r"adv\d*", "adv"),
]


def norm_formula(s):
    """Frozen formula normalizer (prereg sec.3): lowercase, strip whitespace,
    alias-unify operator/variable names, normalize numeric constants."""
    if not s:
        return ""
    t = s.strip().rstrip("。").rstrip(".")
    t = re.sub(r"\s+", "", t)
    t = t.lower()
    for pat, rep in _FUNC_ALIASES + _VAR_ALIASES:
        t = re.sub(pat, rep, t)
    t = re.sub(r"(\d)\.0\b", r"\1", t)
    t = re.sub(r"\.0(\D)", r"\1", t)
    return t


def _read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _parse_meta_dict(text):
    """Extract __alpha_meta__ dict literal via ast (no import, no exec)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "__alpha_meta__":
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        return None
    return None


def _docstring_formula(text):
    """'Formula (paper appendix): X' or 'Formula: X' from module docstring."""
    m = re.search(r"Formula\s*\(paper appendix\)\s*:\s*([^\n]+)", text)
    if not m:
        m = re.search(r"Formula:\s*([^\n]+)", text)
    if not m:
        m = re.search(r"formula\s*=\s*([^\n]+)", text)
    return m.group(1).strip() if m else ""


def _cn_header_formula(text):
    """Chinese header '# 简要说明: <formula>，...' -> formula body."""
    m = re.search(r"简要说明:\s*([^，。\n]+)", text)
    return m.group(1).strip() if m else ""


def _face_from_file(path, family, number=None):
    text = _read_text(path)
    meta = _parse_meta_dict(text) or {}
    return {
        "file": os.path.basename(path),
        "family_dir": family,
        "number": number,
        "meta_id": meta.get("id", ""),
        "formula_latex": (meta.get("formula_latex") or "").strip(),
        "doc_formula": _docstring_formula(text),
        "cn_formula": _cn_header_formula(text),
    }


def _dual_write_consistent(face, sources):
    """All non-empty formula sources normalize to the same string."""
    vals = []
    for key in sources:
        v = norm_formula(face.get(key, ""))
        if v:
            vals.append(v)
    if len(vals) < 2:
        return None                       # cannot verify (unverifiable leg)
    return all(v == vals[0] for v in vals)


def _dual_write_agreement(face, sources):
    vals = [norm_formula(face.get(k, "")) for k in sources]
    vals = [v for v in vals if v]
    if len(vals) < 2:
        return None
    return sum(1 for v in vals if v == vals[0]), len(vals)


# ---------------------------------------------------------------- exporters
def export_m1():
    """Walk M1 zoo; return dict family -> list of face dicts."""
    out = {"alpha101": [], "gtja191": [], "qlib158": [],
           "academic": [], "fundamental": []}
    for sub in out:
        d = os.path.join(M1_ZOO, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py") or fn.startswith("__"):
                continue
            path = os.path.join(d, fn)
            mnum = re.match(r"alpha_(\d+)\.py$", fn)
            number = int(mnum.group(1)) if mnum else None
            out[sub].append(_face_from_file(path, sub, number))
    return out


_M3_DOC = r"Alpha#(\d+)\s*:\s*(.+?)(?=\n\s*Alpha#|\n\s*Alpha_|\nConventions)"


def export_m3():
    """Module docstring ONLY (ast-extracted) -- per-alpha function docstrings
    repeat 'Alpha#N' and the earlier regex swallowed trailing English prose
    (run-1 engineering bug: 31 rows for 16 alphas, cross legs polluted)."""
    text = _read_text(M3_ALPHAS)
    tree = ast.parse(text)
    doc = ast.get_docstring(tree) or ""
    faces = []
    for m in re.finditer(_M3_DOC, doc, re.S):
        num = int(m.group(1))
        formula = re.sub(r"\s+", "", m.group(2))
        formula = formula.rstrip(")") if formula.count(")") > formula.count("(") else formula
        faces.append({"number": num, "doc_formula": formula.strip(),
                     "meta_id": "m3_alpha%d" % num, "family_dir": "m3"})
    m5 = re.search(r"Alpha_5_day_reversal:\s*([^\n]+)", doc)
    if m5:
        faces.append({"number": None,
                      "doc_formula": m5.group(1).strip(),
                      "meta_id": "m3_alpha_5_day_reversal",
                      "family_dir": "m3"})
    return faces


# ---------------------------------------------------------------- in-repo sources
WQ101_VENDORED = os.path.join(ROOT, "research", "shortline", "external",
                              "worldquant101_alpha101.py")


def _load_wq101_skip_numbers():
    """Single-source: vendored module's _NEUTRALIZED_ALPHAS set literal via ast
    (no import/exec) + alpha056 cap exclusion (P1 prereg s2, 82/101 computable).
    These 19 numbers ARE part of the in-repo verdict space (skip=adjudicated
    not-computable on the ETF panel), NOT new faces."""
    nums = set()
    try:
        tree = ast.parse(_read_text(WQ101_VENDORED))
    except (OSError, SyntaxError):
        return nums
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "_NEUTRALIZED_ALPHAS":
                    try:
                        val = ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        continue
                    for item in val:
                        if isinstance(item, tuple) and item:
                            nums.add(int(item[0]))
                        elif isinstance(item, int):
                            nums.add(item)
    nums.add(56)                       # alpha056 cap exclusion, P1 prereg s2
    return nums


def load_wq101_verdicts():
    rows = list(csv.DictReader(io.open(WQ101_CSV, encoding="utf-8-sig")))
    out = {}
    for r in rows:
        m = re.match(r"alpha(\d+)$", r["factor"].strip())
        if m:
            out[int(m.group(1))] = r["status"].strip()
    for n in _load_wq101_skip_numbers():
        out.setdefault(n, "skip(neutralized_or_cap)")
    return out


def load_gtja191_verdicts():
    rows = list(csv.DictReader(io.open(GTJA191_CSV, encoding="utf-8-sig")))
    out = {}
    for r in rows:
        m = re.match(r"alpha191_(\d+)$", r["factor"].strip())
        if m:
            out[int(m.group(1))] = r["status"].strip()
    return out


def load_a158_names():
    """Single-source: import a158_tsgate_probe and call alpha158_factors on a
    tiny synthetic df (module __main__-guarded; anchor gates live in the batch
    runner functions, not here). Returns the 157-name set."""
    import pandas as pd
    import a158_tsgate_probe as probe
    n = 300
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    rng = pd.date_range("2020-01-01", periods=n, freq="D")
    df = pd.DataFrame({
        "open": [100.0 + (i % 7) for i in range(n)],
        "high": [101.0 + (i % 5) for i in range(n)],
        "low": [99.0 - (i % 3) for i in range(n)],
        "close": [100.0 + ((i * 13) % 11) - 5 for i in range(n)],
        "volume": [1000.0 * (1 + (i % 4)) for i in range(n)],
    }, index=rng)
    facs = probe.alpha158_factors(df)
    assert len(facs) == probe.N_FACTORS, "a158 single-source N mismatch"
    return set(facs.keys())


def load_engine_face_names():
    from factor_registry import ENGINE_FACES, ZOO_FAMILIES
    names = set()
    for f in ENGINE_FACES:
        names.add(f if isinstance(f, str) else str(f))
    if isinstance(ZOO_FAMILIES, dict):
        for k in ZOO_FAMILIES:
            names.add(str(k))
    return names


def _tokens(name):
    t = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
    return [w for w in t.split() if len(w) >= 3]


def _kinship_hit(face_name, in_repo_names):
    """Frozen token-substring kinship rule (prereg sec.3 leg-4): any in-repo
    token (>=3 chars) is a substring of the normalized face name, or any face
    token is a substring of an in-repo face name."""
    fname = re.sub(r"[^a-z0-9]", "", face_name.lower())
    for iname in in_repo_names:
        rname = re.sub(r"[^a-z0-9]", "", iname.lower())
        if not rname:
            continue
        for itok in _tokens(iname):
            if itok in fname:
                return iname
        for ftok in _tokens(face_name):
            if ftok in rname:
                return iname
    return None


# Whitelist exemptions: token collision but construction is heterodox
# (frozen in runner -- reasons auditable).
KINSHIP_EXEMPT = {
    "corr_rewire": "token 'corr' collides with engine vol_price_corr but the "
                   "construction (event-window vs calm-baseline corr-row "
                   "rewiring score) is heterodox vs price-volume corr",
}

FUNDAMENTAL_DATA_GATE_DIRS = {"fundamental"}
FUNDAMENTAL_DATA_GATE_IDS = {"cma", "hml", "rmw", "smb",
                             "asset_growth", "earnings_yield",
                             "gross_profitability", "roe"}


# ---------------------------------------------------------------- legs
def classify_alpha101_leg(m1, m3_by_num, wq_verd):
    rows = []
    for face in m1["alpha101"]:
        n = face["number"]
        agr = _dual_write_agreement(face, ("formula_latex", "doc_formula", "cn_formula"))
        cross = None
        if n in m3_by_num:
            a = norm_formula(face["formula_latex"] or face["doc_formula"])
            b = norm_formula(m3_by_num[n]["doc_formula"])
            cross = (a == b) if (a and b) else None
        number_hit = n in wq_verd
        if not number_hit:
            verdict = "NEW-FACE"
        elif agr is None and cross is None:
            verdict = "UNVERIFIABLE"
        elif (agr is None or agr) and (cross is None or cross):
            verdict = "DUP-NUMBER-VERIFIED"
        else:
            verdict = "DUP-FAMILY-DRIFT"
        rows.append(_row(face, "WQ101", verdict, number_hit, agr, cross,
                         wq_verd.get(n, "")))
    return rows


def classify_gtja191_leg(m1, gtja_verd):
    rows = []
    for face in m1["gtja191"]:
        n = face["number"]
        agr = _dual_write_agreement(face, ("formula_latex", "doc_formula", "cn_formula"))
        number_hit = n in gtja_verd
        if not number_hit:
            verdict = "NEW-FACE"
        elif agr is None:
            verdict = "UNVERIFIABLE"
        elif agr:
            verdict = "DUP-NUMBER-VERIFIED"
        else:
            verdict = "DUP-FAMILY-DRIFT"
        rows.append(_row(face, "GTJA191", verdict, number_hit, agr, None,
                         gtja_verd.get(n, "")))
    return rows


_QLIB_DRIFT_HINT = re.compile(r"delta|t-?\{?\d|/ *\d+ *close|shift")


def classify_a158_leg(m1, a158_names):
    rows = []
    for face in m1["qlib158"]:
        stem = re.sub(r"\.py$", "", face["file"])
        m = re.match(r"([a-z]+?)(\d+)$", stem)
        if m:
            root, win = m.group(1), int(m.group(2))
            qlib_name = "%s%d" % (root.upper(), win)
        else:
            root, win, qlib_name = stem, None, stem.upper()
        number_hit = qlib_name in a158_names
        agr = _dual_write_agreement(face, ("formula_latex", "doc_formula", "cn_formula"))
        drift_risk = bool(_QLIB_DRIFT_HINT.search(face["formula_latex"] or "")) \
            and root.upper() in {"BETA", "RSQR", "RESI", "CORR", "MA", "STD",
                                  "QTLU", "QTLD", "RANK", "RSV"}
        if not number_hit:
            verdict = "NEW-FACE"
        elif agr is None:
            verdict = "UNVERIFIABLE"
        elif agr:
            verdict = "DUP-NUMBER-VERIFIED"
        else:
            verdict = "DUP-FAMILY-DRIFT"
        r = _row(face, "A158", verdict, number_hit, agr, None, "")
        r["qlib_name"] = qlib_name
        r["qlib_semantics_drift_risk"] = drift_risk
        rows.append(r)
    return rows


def classify_academic_leg(m1, engine_names):
    rows = []
    for face in m1["academic"] + m1["fundamental"]:
        stem = re.sub(r"\.py$", "", face["file"])
        kin = _kinship_hit(stem, engine_names)
        if stem in KINSHIP_EXEMPT:
            verdict = "NEW-FACE"
            kin_note = "EXEMPT: " + KINSHIP_EXEMPT[stem]
        elif kin:
            verdict = "DUP-FAMILY-DRIFT"
            kin_note = "kin=%s (name-level; construction verdict deferred to SLOT prereg)" % kin
        else:
            verdict = "NEW-FACE"
            kin_note = ""
        r = _row(face, face["family_dir"].upper(), verdict, bool(kin), None, None, "")
        r["kin_note"] = kin_note
        r["data_gate"] = (face["family_dir"] in FUNDAMENTAL_DATA_GATE_DIRS
                          or stem in FUNDAMENTAL_DATA_GATE_IDS)
        rows.append(r)
    return rows


def classify_m3_leg(m3, m1_alpha101_by_num, wq_verd, engine_names):
    rows = []
    for face in m3:
        n = face["number"]
        if n is not None:
            number_hit = n in wq_verd
            ref = m1_alpha101_by_num.get(n)
            cross = None
            if ref is not None:
                a = norm_formula(face["doc_formula"])
                b = norm_formula(ref["formula_latex"] or ref["doc_formula"])
                cross = (a == b) if (a and b) else None
            if not number_hit:
                verdict = "NEW-FACE"
            elif cross is None or cross:
                verdict = "DUP-NUMBER-VERIFIED"
            else:
                verdict = "DUP-FAMILY-DRIFT"
            rows.append(_row(face, "M3-WQ101", verdict, number_hit, None, cross,
                             wq_verd.get(n, "")))
        else:
            kin = _kinship_hit("5_day_reversal", engine_names)
            verdict = "DUP-FAMILY-DRIFT" if kin else "NEW-FACE"
            r = _row(face, "M3-EXTRA", verdict, bool(kin), None, None, "")
            r["kin_note"] = "kin=%s" % kin if kin else ""
            rows.append(r)
    return rows


def _row(face, leg, verdict, number_hit, agreement, cross, inrepo_status):
    return {
        "face": face.get("meta_id") or face.get("file", ""),
        "file": face.get("file", ""),
        "leg": leg,
        "number": face.get("number"),
        "formula_latex": face.get("formula_latex", ""),
        "doc_formula": face.get("doc_formula", ""),
        "cn_formula": face.get("cn_formula", ""),
        "number_hit": number_hit,
        "dual_write_agreement": agreement,        # (agree,total) or None
        "cross_ok": cross,                        # True/False/None
        "verdict": verdict,
        "inrepo_verdict_status": inrepo_status,
    }


# ---------------------------------------------------------------- main
def run():
    t0 = time.time()
    # completeness gates (prereg sec.2, fail-closed)
    gate_fail = []
    m1 = export_m1()
    counts = {k: len(v) for k, v in m1.items()}
    if not (counts["alpha101"] == 101 and counts["gtja191"] == 191):
        gate_fail.append("M1 alpha_NNN count mismatch: %s" % counts)
    if not (140 <= counts["qlib158"] <= 160):
        gate_fail.append("M1 qlib158 count out of band: %d" % counts["qlib158"])
    if counts["academic"] < 10 or counts["fundamental"] < 3:
        gate_fail.append("M1 academic/fundamental short: %s" % counts)
    for p in (M3_ALPHAS, WQ101_CSV, GTJA191_CSV, A158_CELLS_CSV, REGISTRY_MD):
        if not os.path.exists(p):
            gate_fail.append("missing source: %s" % p)
    if gate_fail:
        print(json.dumps({"status": "GATE-FAIL", "failures": gate_fail},
                         ensure_ascii=False, indent=1))
        return 2

    m3 = export_m3()
    if len(m3) < 15:
        print(json.dumps({"status": "GATE-FAIL",
                          "failures": ["M3 alphas parsed: %d" % len(m3)]}))
        return 2
    wq_verd = load_wq101_verdicts()
    gtja_verd = load_gtja191_verdicts()
    a158_names = load_a158_names()
    engine_names = load_engine_face_names()
    m3_by_num = {f["number"]: f for f in m3 if f["number"] is not None}
    m1_a101_by_num = {f["number"]: f for f in m1["alpha101"]}

    rows = []
    rows += classify_alpha101_leg(m1, m3_by_num, wq_verd)
    rows += classify_gtja191_leg(m1, gtja_verd)
    rows += classify_a158_leg(m1, a158_names)
    rows += classify_academic_leg(m1, engine_names)
    rows += classify_m3_leg(m3, m1_a101_by_num, wq_verd, engine_names)

    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    by_leg = {}
    for r in rows:
        k = r["leg"]
        by_leg.setdefault(k, {})
        by_leg[k][r["verdict"]] = by_leg[k].get(r["verdict"], 0) + 1

    elapsed = round(time.time() - t0, 2)
    doc = {
        "artifact": "G2_OVERLAP_CENSUS_P1",
        "prereg": "research/G2_OVERLAP_CENSUS_P1.md (FROZEN before run)",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {"cutoff": EVIDENCE_CUTOFF}},
        "mine_anchors": M1_ANCHORS,
        "inrepo_verdict_sources": {
            "wq101": "research/shortline/wq101_ic_results.csv (%d rows, 82 ok/19 skip lineage)" % len(wq_verd),
            "gtja191": "research/shortline/gtja191_ic_results.csv (%d rows)" % len(gtja_verd),
            "a158": "scripts/a158_tsgate_probe.py::alpha158_factors single-source (%d names)" % len(a158_names),
        },
        "face_counts": counts,
        "total_faces": len(rows),
        "tally": tally,
        "by_leg": by_leg,
        "notes": {
            "zero_backtest": True, "zero_network": True, "zero_nulls": True,
            "trials_ledger_append": 0, "marks": "+0", "seeds": "+0",
            "qlib_drift_flag_is_disclosure_only": True,
            "kinship_is_name_level_only": True,
        },
        "audit": {
            "elapsed_s": elapsed,
            "budget_cap_s": TIME_BUDGET_S,
            "within_budget": elapsed <= TIME_BUDGET_S,
            "rows_classified": len(rows),
            "a158_single_source_n": len(a158_names),
        },
        "rows": rows,
    }
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    print(json.dumps({
        "status": "OK", "total_faces": len(rows), "tally": tally,
        "by_leg": by_leg, "elapsed_s": elapsed,
        "out": OUT_JSON,
    }, ensure_ascii=False, indent=1))
    return 0


def selftest():
    """Offline self-checks (no mine reads, no writes)."""
    ok = []
    ok.append(("norm_basic", norm_formula("Rank(Ts_ArgMax(x, 5)) - 0.5")
               == norm_formula("rank(ts_argmax(x,5))-0.5")))
    ok.append(("norm_strip", norm_formula("a + b") == "a+b"))
    t = '# ==== \n# 简要说明: (-1 * CORR(RANK(X), 6))，说明文字。\n'
    ok.append(("cn_header", _cn_header_formula(t) == "(-1 * CORR(RANK(X), 6))"))
    meta_src = '__alpha_meta__ = {"id": "x", "formula_latex": "a+b"}\n'
    ok.append(("meta_parse", (_parse_meta_dict(meta_src) or {}).get("id") == "x"))
    ok.append(("kinship", _kinship_hit("strev", {"rev_5"}) == "rev_5"))
    ok.append(("kinship_illiq", _kinship_hit("illiq", {"amihud_illiq"}) == "amihud_illiq"))
    ok.append(("kinship_none", _kinship_hit("cma", {"mom_20", "rev_5"}) is None))
    fails = [name for name, passed in ok if not passed]
    print("g2_overlap_census selftest: %d/%d PASS %s"
          % (len(ok) - len(fails), len(ok),
             ("FAIL:" + ",".join(fails)) if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    sys.exit(run())
