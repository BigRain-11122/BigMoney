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


# ================================================================ P2 (M4/M5)
# G2_OVERLAP_CENSUS_P2 (prereg research/G2_OVERLAP_CENSUS_P2.md, FROZEN
# before this extension landed -- freeze commit e6953e67d). 237 rows:
# M4 initial-d/ml-quant-trading 213 registered faces + M5 JunQHuang 24
# honest-downgrade faces. Zero backtest/network/engine; measurement face.
M4_FEATURES_DIR = os.path.join(TOOLSTACK_REPOS, "ml-quant-trading",
                               "src", "mlquant", "features")
M5_FACTORS_FILE = os.path.join(TOOLSTACK_REPOS,
                               "Machine_Learning-Quant-Stock-Selection",
                               "multifactor_demo", "factors.py")
OUT_JSON_P2 = os.path.join(ROOT, "results", "g2_overlap_census_p2.json")
P2_EVIDENCE_CUTOFF = "2026-09-30"
P2_MINE_ANCHORS = {                    # r494 install anchors, prereg sec.2
    "M4_ml-quant-trading": "a770825f841504e41581f057b4d94160e6a50c2e",
    "M5_Machine_Learning-Quant-Stock-Selection": "b3e3712935deb909d143334942edb2ca438c3a26",
}
# prereg sec.0 frozen family census (bit-exact gate, != -> VOID refuse)
P2_M4_FAMILY_BUDGET = {"add": 30, "alpha": 9, "best": 21, "better": 28,
                       "change": 5, "extra": 14, "cs": 6, "old": 50,
                       "original": 28, "stock": 22}
P2_TIME_BUDGET_S = 180                 # prereg sec.0 cap

_ATOM_RE = re.compile(r"[a-z_][a-z0-9_]*|\d+(?:\.\d+)?")


def _strip_redundant_parens(t):
    """norm_v2 bracket prescreen (prereg sec.3, frozen): strip ONLY
    single-atom / single-number wrapper layers ((x))->x, (2.)->2 -- iterated
    to fixpoint; never strips call-argument parens (preceded by ident char)
    or explicit precedence structures (content not a single atom)."""
    prev = None
    while prev != t:
        prev = t
        out = []
        i, n = 0, len(t)
        while i < n:
            c = t[i]
            if c == "(" and (i == 0
                              or not (t[i - 1].isalnum() or t[i - 1] == "_")):
                depth, j = 0, i
                while j < n:
                    if t[j] == "(":
                        depth += 1
                    elif t[j] == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                if j < n and (j + 1 >= n or t[j + 1] != "("):
                    inner = t[i + 1:j]
                    if _ATOM_RE.fullmatch(inner):
                        out.append(inner)
                        i = j + 1
                        continue
            out.append(c)
            i += 1
        t = "".join(out)
    return t


def norm_formula_v2(s):
    """Frozen P2 normalizer = P1 norm_formula superset + bracket prescreen.
    P1 DRIFT faces keep their P1-book DRIFT verdict (no retro-flip; prereg
    sec.0) -- v2 only judges THIS slice's M4/M5 equivalence legs."""
    t = norm_formula(s)
    t = re.sub(r"(\d)\.(?!\d)", r"\1", t)   # '(2.)'->'2' (frozen sec.3 example)
    return _strip_redundant_parens(t)


# P2 extractor vocabulary: OHLCV/derived variable words allowed in symbolic
# formula faces (frozen in runner, observed-token audit trail: mine dump
# results/_r499bma_m4_doclines.json). Function-position identifiers (directly
# followed by '(') are exempt; any other >=3-char word outside this vocab
# marks the line as prose (no machine-readable formula face).
_P2_FORMULA_VOCAB = {"close", "open", "high", "low", "volume", "vol", "vwap",
                     "amount", "amt", "ret", "rets", "returns", "range", "eps",
                     "loc", "location", "delta", "sign", "alpha",
                     "log", "log2", "sqrt", "abs"}


def _is_prose_line(line):
    # [A-Za-z]+ tokenization (NOT [A-Za-z_]+): compound variables like
    # close_loc / vwap_loc decompose into vocab parts; snake_case function
    # names keep their function-position exemption via the final part.
    for m in re.finditer(r"[A-Za-z]+", line):
        tok = m.group(0).lower()
        if (len(tok) >= 3 and line[m.end():m.end() + 1] != "("
                and tok not in _P2_FORMULA_VOCAB):
            return True
    return False


def _matching_open(s, close_idx):
    depth = 0
    for j in range(close_idx, -1, -1):
        if s[j] == ")":
            depth += 1
        elif s[j] == "(":
            depth -= 1
            if depth == 0:
                return j
    return None


def _m4_formula_from_docstring(doc):
    """M4 docstring first line = formula face (single-source leg -- M4 has no
    formula_latex dual write). Frozen extraction fidelity (eng-fix trail,
    r493 P1 precedent): em-dash prose tail cut; multi-word prose head label
    before ':' stripped; trailing annotation paren-groups (non-call, >=2
    alpha words) stripped; ' vs ' dual-construction and '...' placeholder
    lines rejected as ambiguous/abbreviated (frozen sec.4 state-4 lineage);
    prose lines (vocab rule) yield '' -- honest absent face."""
    if not doc:
        return ""
    first = doc.strip().splitlines()[0].strip()
    if "\u2014" in first:                # em-dash prose separator
        first = first.split("\u2014")[0].strip()
    first = first.rstrip(".").strip()
    if ":" in first and "(" not in first.split(":")[0]:
        # multi-word prose head label (never a ternary head -- guard: no
        # call parens in head)
        head, _, rest = first.partition(":")
        if " " in head.strip():
            first = rest.strip()
    while first.endswith(")"):           # trailing annotation paren-groups
        first = first.rstrip(".").strip()
        i = _matching_open(first, len(first) - 1)
        if i is None:
            break
        if i > 0 and (first[i - 1].isalnum() or first[i - 1] == "_"):
            break                        # call-argument group, keep
        inner = first[i + 1:-1]
        if _is_prose_line(inner):        # prose annotation (e.g. '(deviation
            first = first[:i].strip()    # from 20-day MA)'); arithmetic
        else:                            # groups (e.g. '/ (4*close)') keep
            break
    first = first.rstrip(".").strip()
    if not first:
        return ""
    if " vs " in " %s " % first:
        return ""                        # ambiguous dual construction
    if "..." in first:
        return ""                        # abbreviated placeholder
    if ("(" in first and ")" in first) or ("[" in first and "]" in first):
        candidate = first                # call-paren or bracket-index notation
    else:                                # paren-less symbolic shorthand
        toks = first.split()
        if not (1 < len(toks) <= 3 and re.search(r"[/+^]", first)):
            return ""
        candidate = first
    if _is_prose_line(candidate):
        return ""
    return candidate


def export_m4_faces():
    """Walk M4 _factors_*.py; ast-extract @register_*("name") functions ->
    (registered name, docstring formula, subfamily by name prefix, file)."""
    out = []
    for fn in sorted(os.listdir(M4_FEATURES_DIR)):
        if not (fn.startswith("_factors_") and fn.endswith(".py")):
            continue
        path = os.path.join(M4_FEATURES_DIR, fn)
        tree = ast.parse(_read_text(path))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            reg_name = None
            for dec in node.decorator_list:
                if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name)
                        and dec.func.id.startswith("register_")
                        and dec.args and isinstance(dec.args[0], ast.Constant)
                        and isinstance(dec.args[0].value, str)):
                    reg_name = dec.args[0].value
                    break
            if reg_name is None:
                continue
            out.append({
                "file": fn,
                "func": node.name,
                "meta_id": reg_name,
                "subfamily": reg_name.split("_")[0],
                "doc_formula": _m4_formula_from_docstring(ast.get_docstring(node)),
                "body_node": node,
            })
    return out


def export_m5_faces():
    """M5 AlphaFactorEngine.alpha_NNN methods (code-as-formula leg) +
    DEMO_FACTORS == method-set assertion (prereg sec.2 gate)."""
    tree = ast.parse(_read_text(M5_FACTORS_FILE))
    methods = []
    demo = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AlphaFactorEngine":
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    if re.match(r"alpha_\d+$", sub.name):
                        methods.append(sub)
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "DEMO_FACTORS":
                    try:
                        demo = ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        demo = None
    names = sorted(m.name for m in methods)
    demo_ok = demo is not None and sorted(demo) == names
    faces = [{"meta_id": m.name, "number": int(m.name.split("_")[1]),
              "body_node": m} for m in methods]
    return faces, names, demo_ok


def _op_sequence(func_node):
    """Source-order operator/constant sequence from a function body AST
    (prereg sec.3 M5 leg: operator-name + constant + window sequence,
    normalized). Attribute calls -> base name (self.ts_mean -> ts_mean,
    np.log -> log). Numbers keep sign via unary-op wrapping."""
    seq = []

    def visit(node, neg=False):
        if isinstance(node, ast.Call):
            f = node.func
            name = None
            if isinstance(f, ast.Name):
                name = f.id
            elif isinstance(f, ast.Attribute):
                name = f.attr
            seq.append(("op", name.lower() if name else "?"))
            for a in node.args:
                visit(a)
            for k in node.keywords:
                visit(k.value)
            return
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            v = node.value
            seq.append(("num", -v if neg else v))
            return
        if isinstance(node, ast.UnaryOp):
            visit(node.operand, neg=(node.op.__class__.__name__ == "USub"))
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.expr,)):
                visit(child)
            else:
                visit(child)

    for stmt in func_node.body:
        visit(stmt)
    return seq


def _ops_view(seq):
    return [s[1] for s in seq if s[0] == "op"]


def _nums_view(seq):
    return sorted(s[1] for s in seq if s[0] == "num")


def _registry_row_names():
    """Registry A-H table row first-cell names (kinship pool member per
    prereg sec.3 leg-2). Parse-only, no science semantics."""
    names = set()
    if not os.path.exists(REGISTRY_MD):
        return names
    for line in _read_text(REGISTRY_MD).splitlines():
        m = re.match(r"\|\s*([a-z0-9_]+)\s*\|", line)
        if m and m.group(1) not in ("面", "---", "---|"):
            names.add(m.group(1))
    return names


def _p2_row(face, leg, verdict, number_hit, formula_ok, corpus_hit, kin_hit,
            inrepo_status, note=""):
    return {
        "face": face.get("meta_id", ""),
        "file": face.get("file", "factors.py"),
        "leg": leg,
        "number": face.get("number"),
        "subfamily": face.get("subfamily", ""),
        "doc_formula": face.get("doc_formula", ""),
        "number_hit": number_hit,
        "formula_ok": formula_ok,
        "corpus_hit": corpus_hit,          # {"family","number","status"} or None
        "kin_hit": kin_hit,                # in-repo name or None
        "verdict": verdict,
        "inrepo_verdict_status": inrepo_status,
        "note": note,
    }


def classify_p2_m4_wq101_leg(m4, m1_a101_by_num, wq_verd):
    rows = []
    for face in m4:
        if face["subfamily"] != "alpha":
            continue
        m = re.match(r"alpha_(\d+)$", face["meta_id"])
        n = int(m.group(1)) if m else None
        number_hit = n in wq_verd
        formula_ok = None
        ref = m1_a101_by_num.get(n) if n is not None else None
        if face["doc_formula"] and ref is not None:
            a = norm_formula_v2(face["doc_formula"])
            b = norm_formula_v2(ref["formula_latex"] or ref["doc_formula"])
            formula_ok = (a == b) if (a and b) else None
            if a and "\u0394" in face["doc_formula"]:
                face_note = "delta-symbol variant in mine docstring (U+0394) -- identity leg honest miss disclosed"
            else:
                face_note = ""
        else:
            face_note = "no machine-readable formula face" if not face["doc_formula"] else "no M1 same-number ref"
        if not number_hit:
            verdict = "NEW-FACE"
        elif formula_ok is None:
            verdict = "UNVERIFIABLE"
        elif formula_ok:
            verdict = "DUP-NUMBER-VERIFIED"
        else:
            verdict = "DUP-FAMILY-DRIFT"
        rows.append(_p2_row(face, "M4-WQ101", verdict, number_hit, formula_ok,
                            None, None, wq_verd.get(n, ""), face_note))
    return rows


def classify_p2_m4_formula_leg(m4, corpus, engine_names, wq_verd, gtja_verd):
    """Legs 2+3 (frozen): formula-identity primary vs in-repo WQ-syntax corpus
    -> DUP-FORMULA-VERIFIED; else name kinship (engine+zoo+registry rows)
    -> DUP-FAMILY-DRIFT; else NEW-FACE."""
    rows = []
    for face in m4:
        sub = face["subfamily"]
        if sub == "alpha":                # leg-1 territory
            continue
        leg = "M4-MARKET" if sub == "cs" else "M4-NAMEKEY"
        fml = face["doc_formula"]
        corpus_hit = None
        formula_ok = None
        if fml:
            a = norm_formula_v2(fml)
            if a:
                for key, rec in corpus.items():
                    if a == rec["norm"]:
                        corpus_hit = rec
                        formula_ok = True
                        break
        kin = _kinship_hit(face["meta_id"], engine_names)
        if corpus_hit is not None:
            verdict = "DUP-FORMULA-VERIFIED"
            status = corpus_hit["status"]
            note = "corpus: %s#%s" % (corpus_hit["family"], corpus_hit["number"])
            if sub == "old" and corpus_hit["family"] == "gtja191":
                note += " (GTJA-renumber suspicion adjudicated by formula identity)"
        elif formula_ok is None and not fml:
            # no machine-readable formula face (prose-only docstring):
            # kin hit -> DUP-FAMILY-DRIFT (leg-3/leg-2 chain); zero kin ->
            # UNVERIFIABLE per frozen sec.4 state-4 (公式源缺 -> 不入池不烧)
            if kin:
                verdict = "DUP-FAMILY-DRIFT"
                status = ""
                note = "kin=%s (name-level; formula face absent in mine docstring)" % kin
            else:
                verdict = "UNVERIFIABLE"
                status = ""
                note = "prose-only docstring: no machine-readable formula face (frozen sec.4 state-4)"
        elif kin:
            verdict = "DUP-FAMILY-DRIFT"
            status = ""
            note = "kin=%s (name-level; construction verdict deferred to SLOT prereg)" % kin
            if fml and "\u0394" in fml:
                note += " + delta-symbol variant disclosed"
        else:
            verdict = "NEW-FACE"
            status = ""
            note = ""
            if fml and "\u0394" in fml:
                note = "delta-symbol variant in mine docstring -- identity miss disclosed"
        rows.append(_p2_row(face, leg, verdict, False, formula_ok, corpus_hit,
                            kin, status, note))
    return rows


def _m1_compute_bodies():
    """M1 alpha_NNN.py compute() function nodes (M5 code-face comparison
    leg needs the implementation body, not just formula fields)."""
    out = {}
    d = os.path.join(M1_ZOO, "alpha101")
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        m = re.match(r"alpha_(\d+)\.py$", fn)
        if not m:
            continue
        try:
            tree = ast.parse(_read_text(os.path.join(d, fn)))
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "compute":
                out[int(m.group(1))] = node
                break
    return out


def classify_p2_m5_leg(m5_faces, m1_compute_bodies, wq_verd):
    rows = []
    for face in m5_faces:
        n = face["number"]
        number_hit = n in wq_verd
        ref = m1_compute_bodies.get(n)
        code_ok = None
        if ref is not None:
            a_seq = _op_sequence(face["body_node"])
            b_seq = _op_sequence(ref)
            if _ops_view(a_seq) and _ops_view(b_seq):
                code_ok = (_ops_view(a_seq) == _ops_view(b_seq)
                           and _nums_view(a_seq) == _nums_view(b_seq))
        if not number_hit:
            verdict = "NEW-FACE"
            note = ""
        elif code_ok is None:
            verdict = "DUP-FAMILY-DRIFT"
            note = "code-face-limit: operator sequence not extractable both sides"
        elif code_ok:
            verdict = "DUP-NUMBER-VERIFIED"
            note = "operator+window sequence identical (code-face verified)"
        else:
            verdict = "DUP-FAMILY-DRIFT"
            note = "code-face-unverified: same number, different construction (M5 generic demo set -- README honest-downgrade lineage)"
        rows.append(_p2_row(face, "M5-WQ101", verdict, number_hit, None,
                            None, None, wq_verd.get(n, ""), note))
    return rows


def run_p2():
    t0 = time.time()
    if os.path.exists(OUT_JSON_P2):
        print(json.dumps({"status": "REFUSED",
                          "why": "results/g2_overlap_census_p2.json exists; "
                                 "prereg forbids re-run (engineering re-run "
                                 "needs dual-run trail)"}, indent=1))
        return 2
    gate_fail = []
    m4 = export_m4_faces()
    fam_counts = {}
    for f in m4:
        fam_counts[f["subfamily"]] = fam_counts.get(f["subfamily"], 0) + 1
    if fam_counts != P2_M4_FAMILY_BUDGET:
        gate_fail.append("M4 family census mismatch: %s" % fam_counts)
    m5_faces, m5_names, demo_ok = export_m5_faces()
    if not (len(m5_names) == 24 and demo_ok):
        gate_fail.append("M5 gate: n=%s demo_ok=%s" % (len(m5_names), demo_ok))
    for p in (M4_FEATURES_DIR, M5_FACTORS_FILE, WQ101_CSV, GTJA191_CSV,
              REGISTRY_MD):
        if not os.path.exists(p):
            gate_fail.append("missing source: %s" % p)
    if gate_fail:
        print(json.dumps({"status": "GATE-FAIL", "failures": gate_fail},
                         ensure_ascii=False, indent=1))
        return 2

    m1 = export_m1()
    wq_verd = load_wq101_verdicts()      # skip set merged here (single source)
    gtja_verd = load_gtja191_verdicts()
    a158_names = load_a158_names()
    engine_names = load_engine_face_names()
    registry_rows = _registry_row_names()
    kin_pool = engine_names | a158_names | registry_rows
    m1_a101_by_num = {f["number"]: f for f in m1["alpha101"]}

    # in-repo WQ-syntax formula corpus (frozen leg-2 sources). A158 probe and
    # registry rows carry no machine-readable WQ-syntax formula strings
    # (code-as-formula / prose constructions) -> disclosed, contribute zero
    # string identities (cross-formal identity unprovable, M5-leg lineage).
    corpus = {}
    for face in m1["alpha101"]:
        s = norm_formula_v2(face["formula_latex"] or face["doc_formula"])
        if s:
            corpus.setdefault(s, {"family": "wq101", "number": face["number"],
                                  "status": wq_verd.get(face["number"], ""),
                                  "norm": s})
    for face in m1["gtja191"]:
        s = norm_formula_v2(face["formula_latex"] or face["doc_formula"])
        if s:
            corpus.setdefault(s, {"family": "gtja191", "number": face["number"],
                                  "status": gtja_verd.get(face["number"], ""),
                                  "norm": s})

    rows = []
    rows += classify_p2_m4_wq101_leg(m4, m1_a101_by_num, wq_verd)
    rows += classify_p2_m4_formula_leg(m4, corpus, kin_pool, wq_verd, gtja_verd)
    rows += classify_p2_m5_leg(m5_faces, _m1_compute_bodies(), wq_verd)
    expected_total = (sum(P2_M4_FAMILY_BUDGET.values()) + 24)
    if len(rows) != expected_total:
        print(json.dumps({"status": "GATE-FAIL",
                          "failures": ["row count %d != expected %d"
                                       % (len(rows), expected_total)]}))
        return 2

    tally, by_leg = {}, {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
        by_leg.setdefault(r["leg"], {})
        by_leg[r["leg"]][r["verdict"]] = by_leg[r["leg"]].get(r["verdict"], 0) + 1

    elapsed = round(time.time() - t0, 2)
    doc = {
        "artifact": "G2_OVERLAP_CENSUS_P2",
        "prereg": "research/G2_OVERLAP_CENSUS_P2.md (FROZEN before run)",
        "evidence_cutoff": P2_EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": {"cutoff": P2_EVIDENCE_CUTOFF}},
        "mine_anchors": P2_MINE_ANCHORS,
        "m4_family_counts": fam_counts,
        "m5_demo_assertion": "DEMO_FACTORS == alpha_NNN method set, n=24 PASS",
        "corpus_disclosure": {
            "wq101_formulas": sum(1 for v in corpus.values() if v["family"] == "wq101"),
            "gtja191_formulas": sum(1 for v in corpus.values() if v["family"] == "gtja191"),
            "a158_formula_face": "not machine-readable as WQ-syntax strings (code-as-formula) -- zero string identities, name-level kinship only",
            "registry_rows_formula_face": "prose constructions, not WQ syntax -- name-level kinship only",
        },
        "total_faces": len(rows),
        "tally": tally,
        "by_leg": by_leg,
        "notes": {
            "zero_backtest": True, "zero_network": True, "zero_nulls": True,
            "trials_ledger_append": 0, "marks": "+0", "seeds": "+0",
            "p1_verdicts_not_retroflipped": True,
            "norm_v2_bracket_prescreen_is_p2_slice_only": True,
            "m5_readme_honest_downgrade": "claimed 120 vs installed 24 (prereg sec.2)",
        },
        "audit": {
            "elapsed_s": elapsed,
            "budget_cap_s": P2_TIME_BUDGET_S,
            "within_budget": elapsed <= P2_TIME_BUDGET_S,
            "rows_classified": len(rows),
            "expected_rows": expected_total,
            "eng_fix_trail": "extraction fidelity iterated to convergence "
                             "(runs 1-3 preserved as "
                             "results/g2_overlap_census_p2_run{1,2,3}.json "
                             "trails; canonical = final convergence run; r493 "
                             "P1 dual-run-trail precedent): r1->r2 shorthand "
                             "rule + UNVERIFIABLE state for absent faces; "
                             "r2->r3 prose-head strip + trailing-annotation "
                             "strip + 'vs'/'...' ambiguity reject + vocabulary "
                             "prose gate; r3->final annotation prose-inner "
                             "criterion (arithmetic groups keep) + "
                             "compound-variable decomposition (close_loc) + "
                             "bracket-index notation. All rules frozen in "
                             "runner; observed-token dump "
                             "results/_r499bma_m4_doclines.json",
        },
        "rows": rows,
    }
    with io.open(OUT_JSON_P2, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    print(json.dumps({
        "status": "OK", "total_faces": len(rows), "tally": tally,
        "by_leg": by_leg, "elapsed_s": elapsed, "out": OUT_JSON_P2,
    }, ensure_ascii=False, indent=1))
    return 0


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
    # ---- P2 fixtures (offline, synthetic only) ----
    ok.append(("v2_wrap_single", norm_formula_v2("((x)) + (y)") == "x+y"))
    ok.append(("v2_wrap_num", norm_formula_v2("(2.)") == "2"))
    ok.append(("v2_call_parens_kept",
               norm_formula_v2("signedpower((x), 2.)") == "signedpower(x,2)"))
    ok.append(("v2_precedence_kept",
               norm_formula_v2("(a + b) * c") == "(a+b)*c"))
    ok.append(("v2_absorbs_p1_drift",
               norm_formula_v2("signedpower((x), 2.)")
               == norm_formula_v2("signedpower(x, 2)")))
    ok.append(("v2_no_func_destructure",
               norm_formula_v2("rank(x)") != "rankx"))
    doc = "rank(volume) * rank(vwap - close) — legacy port."
    ok.append(("m4_doc_cut", _m4_formula_from_docstring(doc)
               == "rank(volume) * rank(vwap - close)"))
    ok.append(("m4_doc_desc_none",
               _m4_formula_from_docstring("Cross-sectional rank of close return.") == ""))
    ok.append(("m4_doc_parenless_shorthand",
               _m4_formula_from_docstring("high / open.") == "high / open"))
    ok.append(("m4_doc_prose_rejected",
               _m4_formula_from_docstring("Deviation from 20-day mean, cross-sectionally z-scored.") == ""))
    ok.append(("m4_doc_head_strip",
               _m4_formula_from_docstring("Amount surge: amount / ts_mean(amount, 20) - 1")
               == "amount / ts_mean(amount, 20) - 1"))
    ok.append(("m4_doc_annotation_strip",
               _m4_formula_from_docstring("close - ts_mean(close, 20) (deviation from 20-day MA).")
               == "close - ts_mean(close, 20)"))
    ok.append(("m4_doc_annotation_keeps_callgroup",
               _m4_formula_from_docstring("EWMA(open / delay(close, 1) - 1, alpha=1/5)")
               == "EWMA(open / delay(close, 1) - 1, alpha=1/5)"))
    ok.append(("m4_doc_annotation_keeps_arithgroup",
               _m4_formula_from_docstring("(mean(close,3)+mean(close,6)) / (4*close).")
               == "(mean(close,3)+mean(close,6)) / (4*close)"))
    ok.append(("m4_doc_annotation_keeps_divisor",
               _m4_formula_from_docstring("(close - open) / (high - low + 1e-9).")
               == "(close - open) / (high - low + 1e-9)"))
    ok.append(("m4_doc_vs_rejected",
               _m4_formula_from_docstring("rank(a, 5) vs rank(b, 5)") == ""))
    ok.append(("m4_doc_ellipsis_rejected",
               _m4_formula_from_docstring("ewma(std(close,20), 1/5) - ewma(..., 1/20)") == ""))
    ok.append(("m4_doc_prose_scaled_by",
               _m4_formula_from_docstring("ts_max(high, 5) - ts_min(low, 5) scaled by close.") == ""))
    ok.append(("m4_doc_conditional_rejected",
               _m4_formula_from_docstring("Conditional sum: if vwap < close: |vwap/close-1|, window=20.") == ""))
    m4_src = '''
@register_legacy_factor("alpha_001")
def alpha_001(panel):
    """cs_rank(ts_rank(close, 5)) - 0.5 — momentum."""
    return None
'''
    import tempfile
    tmpdir = tempfile.mkdtemp()
    fake = os.path.join(tmpdir, "_factors_x.py")
    with io.open(fake, "w", encoding="utf-8") as fh:
        fh.write(m4_src)
    tree = ast.parse(_read_text(fake))
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef)][0]
    ok.append(("m4_extract", _m4_formula_from_docstring(ast.get_docstring(fn))
               == "cs_rank(ts_rank(close, 5)) - 0.5"))
    ok.append(("m4_reg_name", fn.name == "alpha_001"))
    m5_src = '''
class AlphaFactorEngine:
    def alpha_002(self):
        a = self.ts_mean(self.volume, 5)
        return -(a - self.volume)
'''
    tree2 = ast.parse(m5_src)
    cls = [n for n in tree2.body if isinstance(n, ast.ClassDef)][0]
    meth = [n for n in cls.body if isinstance(n, ast.FunctionDef)][0]
    ok.append(("m5_ops", _ops_view(_op_sequence(meth)) == ["ts_mean"]))
    ok.append(("m5_nums", _nums_view(_op_sequence(meth)) == [5]))
    a1 = ast.parse("def f():\n    return ts_corr(rank(x), y, 6)\n")
    a2 = ast.parse("def g():\n    return ts_corr(rank(x), y, 5)\n")
    ok.append(("m5_seq_differs", _ops_view(_op_sequence(a1.body[0]))
               == _ops_view(_op_sequence(a2.body[0]))
               and _nums_view(_op_sequence(a1.body[0]))
               != _nums_view(_op_sequence(a2.body[0]))))
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)
    fails = [name for name, passed in ok if not passed]
    print("g2_overlap_census selftest: %d/%d PASS %s"
          % (len(ok) - len(fails), len(ok),
             ("FAIL:" + ",".join(fails)) if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd in ("run-p2", "run_p2"):
        sys.exit(run_p2())
    sys.exit(run())
