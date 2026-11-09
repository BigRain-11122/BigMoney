# -*- coding: utf-8 -*-
"""E588 -- does any consumer of the forward ledger take its ROW COUNT as a denominator?

E584 (r1614) found the class of fault: a run that both rebased and appended published six
bars twice, so ``results/etf_book_forward/LEDGER.json`` held 17 rows over 11 bars and the
significance block was fed all 17 (+54.55% on the bar count).  The record was repaired, but
the *consumers* were never enumerated.  Any reader that uses ``len(bars)`` as a count --
per-bar averages, "trading days since inception", bars-needed tables -- inherits whatever
the file happens to hold; any reader that keys by ``bar`` collapses duplicate rows and never
sees the fault at all.

This study publishes, per in-repo consumer of that one file:

  usage            which of five roles its own source lines play -- ``row_count`` (a len()
                   over the bars/rows list, split into arithmetic vs plain), ``endpoint_key``
                   (bars[0]/bars[-1]), ``bar_key`` (a dict keyed by "bar" or a "bar" read),
                   ``dedupe_guard`` (a unique/rows_equal_bars style guard), with the literal
                   line number and code for each hit;
  duplicate_effect what a 17-row/11-bar ledger would do to it -- ``guarded``, ``blind_row_count``,
                   ``immune_keyed_or_endpoint`` or ``names_the_path_but_reads_no_bars``.

Three empirical arms run in a temp directory against the real ledger and a copy of it with the
last six rows appended again (the shape E584 actually published): a per-row rate mean taken
from ``e592.published_rate_series`` (blind), ``etf_book_order._ledger_book`` (endpoint-keyed),
and ``etf_book_ceo_page.build``'s own ``forward`` block (count-fed, CEO-facing).

Read-only: nothing in the repo is written except this study's own face.

Honest limits (published in the face):
  * role detection is line-level on the module's own literals -- it can see ``len(bars)`` and
    cannot see a count that arrives through five helper frames (the census is a lower bound);
  * a module that names the ledger path but hands it to another module is graded on its own
    lines only, so a relay module reads as ``names_the_path_but_reads_no_bars``;
  * ``blind`` is a statement about a published number, not about a defect: a row count that is
    merely printed is still wrong by 54% on a duplicated file;
  * the six-row duplication reproduces E584's shape, not its exact row objects.

  python scripts/e588_ledger_rowcount.py build
  python scripts/e588_ledger_rowcount.py check
  python scripts/e588_ledger_rowcount.py verify
  python scripts/e588_ledger_rowcount.py selftest

Output: results/state_tilt/LEDGERROWCOUNT.json (+ LEDGERROWCOUNT-latest.json)
"""
from __future__ import annotations

import copy
import io
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "LEDGERROWCOUNT.json")
LATEST_PATH = os.path.join(OUTDIR, "LEDGERROWCOUNT-latest.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
SELF_NAME = "e588_ledger_rowcount.py"

SCAN_DIRS = ["scripts", "Tools", "firm", "live", "monitor", "."]
SKIP_DIRS = {"__pycache__", ".git", "results", "data", "research", "knowledge", "docs",
             "content", "fleet", "legacy", "Money02", ".codely-cli"}
# one-shot round helpers and smoke mirrors: they address the ledger as harness, not as consumer
EXCLUDE_NAME = re.compile(r"^(_r\d|_tmp|_dbg|run_e\d+_smoke_leg|e588_|_e\d+_run)")
EXCLUDE_REASON = {
    "one_shot_round_helper": "round-local closeout/pool/report helper, not a standing consumer",
    "smoke_mirror": "standalone mirror of a study's smoke block; it reads the study, not the catalogue",
    "self": "this study",
}

V_SOME_BLIND = "some_consumer_publishes_the_row_count_and_would_have_reported_17_bars_for_11"
V_ALL_GUARDED = "every_consumer_is_either_guarded_or_keys_by_bar"
V_NO_CONSUMER = "no_in_repo_module_addresses_the_forward_ledger"

ROLES = ("row_count", "row_count_in_arithmetic", "row_count_presence_only",
         "endpoint_key", "bar_key", "dedupe_guard")

RE_ENDPOINT = re.compile(r"bars\s*\[\s*(?:0|-1)\s*\]")
RE_BARKEY = re.compile(r"[\"']bar[\"']\s*:\s|\[\s*[\"']bar[\"']\s*\]|\.get\(\s*[\"']bar[\"']")
RE_DEDUPE = re.compile(
    r"dedupe|uniq|rows_equal_bars|accrued_bars_on_disk|set\(\s*[^)]*\bbar\b"
    r"|\{[^}]*for\s+\w+\s+in\s+[^}]*\bbars\b", re.I)
RE_ARITH = re.compile(r"[/\*]|\*\*|sqrt")
# a count compared only to 0/1/2 is an emptiness test: it reads the same on 11 and 17 rows
RE_PRESENCE = re.compile(r"(?:<=|>=|<|>|==|!=)\s*[012](?!\d)")


# --------------------------------------------------------------------------- pure helpers
def len_spans(line):
    """Every ``len(...)`` call on the line as (outer_start, inner_text)."""
    out = []
    for m in re.finditer(r"\blen\s*\(", line):
        i = m.end() - 1
        depth = 0
        for j in range(i, len(line)):
            if line[j] == "(":
                depth += 1
            elif line[j] == ")":
                depth -= 1
                if depth == 0:
                    out.append((m.start(), j + 1, line[i + 1:j]))
                    break
    return out


def classify_line(line):
    """Which roles this single source line plays. Pure; the only classifier the face trusts."""
    roles = set()
    spans = len_spans(line)
    for start, end, inner in spans:
        if not re.search(r"\bbars\b", inner):
            continue
        rest = line[:start] + line[end:]
        if RE_ARITH.search(rest):
            roles.add("row_count")
            roles.add("row_count_in_arithmetic")
        elif RE_PRESENCE.search(rest):
            roles.add("row_count_presence_only")
        else:
            roles.add("row_count")
    if RE_ENDPOINT.search(line):
        roles.add("endpoint_key")
    if re.search(r"\bbars\b", line) and RE_BARKEY.search(line):
        roles.add("bar_key")
    if RE_DEDUPE.search(line):
        roles.add("dedupe_guard")
    return sorted(roles)


def module_usage(text):
    """All role evidence in a module's source: {role: [{line, code}]}."""
    usage = {r: [] for r in ROLES}
    for i, line in enumerate(text.splitlines(), 1):
        for r in classify_line(line):
            usage[r].append({"line": i, "code": line.strip()[:200]})
    return usage


def duplicate_effect(usage):
    if usage.get("dedupe_guard"):
        return "guarded"
    if usage.get("row_count"):
        return "blind_row_count"
    if usage.get("endpoint_key") or usage.get("bar_key"):
        return "immune_keyed_or_endpoint"
    return "names_the_path_but_reads_no_bars"


def module_kind(text, name):
    if re.search(r"^LEDGER\s*=\s*os\.path\.join", text, re.M) and "def _indexed" in text:
        return "writer"
    if re.search(r"^\"\"\"E\d+", text):
        return "study"
    return "reader"


def count_modules(rows):
    c = {"modules_addressing_the_ledger": len(rows),
         "modules_blind_to_a_duplicated_row": 0,
         "modules_guarded": 0,
         "modules_immune_by_keying": 0,
         "modules_reading_no_bars": 0,
         "modules_where_the_row_count_feeds_arithmetic": 0,
         "modules_with_a_presence_only_count": 0,
         "blind_modules": [], "guarded_modules": [], "numeric_blind_modules": [],
         "presence_only_modules": []}
    for r in rows:
        eff = r["duplicate_effect"]
        if r["usage"].get("row_count_presence_only"):
            c["modules_with_a_presence_only_count"] += 1
            c["presence_only_modules"].append(r["module"])
        if eff == "blind_row_count":
            c["modules_blind_to_a_duplicated_row"] += 1
            c["blind_modules"].append(r["module"])
        elif eff == "guarded":
            c["modules_guarded"] += 1
            c["guarded_modules"].append(r["module"])
        elif eff == "immune_keyed_or_endpoint":
            c["modules_immune_by_keying"] += 1
        else:
            c["modules_reading_no_bars"] += 1
        if r["usage"].get("row_count_in_arithmetic"):
            c["modules_where_the_row_count_feeds_arithmetic"] += 1
            c["numeric_blind_modules"].append(r["module"])
    return c


def verdict_from(counts):
    if not counts.get("modules_addressing_the_ledger"):
        return V_NO_CONSUMER
    if counts.get("modules_blind_to_a_duplicated_row"):
        return V_SOME_BLIND
    return V_ALL_GUARDED


def answer_sentence(counts, arms):
    blind = counts["blind_modules"]
    arm1 = arms.get("per_row_mean") or {}
    if not blind:
        return ("no consumer of the forward ledger publishes its row count; %d of %d guard or "
                "key by bar" % (counts["modules_guarded"],
                                counts["modules_addressing_the_ledger"]))
    txt = ("%d of %d consumers of results/etf_book_forward/LEDGER.json publish its row count and "
           "would have reported 17 bars for 11 (%s); %d guard it and %d key by bar and are immune"
           % (len(blind), counts["modules_addressing_the_ledger"], ", ".join(sorted(blind)),
              counts["modules_guarded"], counts["modules_immune_by_keying"]))
    if arm1.get("available"):
        txt += ("; on a six-row duplication the per-row rate mean moves from %.6f%% to %.6f%% "
                "because six bars are weighted twice" % (arm1["mean_pct_clean"],
                                                         arm1["mean_pct_dup"]))
    return txt


# --------------------------------------------------------------------------- population
def candidates():
    seen, out = [], []
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        if d == ".":
            walker = [(ROOT, [f for f in os.listdir(ROOT) if f.endswith(".py")])]
            for dp, files in walker:
                for f in files:
                    p = os.path.join(dp, f)
                    if p not in seen:
                        seen.append(p)
                        out.append(p)
            continue
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [x for x in dn if x not in SKIP_DIRS and not x.startswith("_r")]
            for f in fn:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dp, f)
                if p not in seen:
                    seen.append(p)
                    out.append(p)
    return sorted(out)


def exclusion_reason(name):
    if name == SELF_NAME:
        return "self", EXCLUDE_REASON["self"]
    if EXCLUDE_NAME.match(name):
        if name.startswith("run_e"):
            return "smoke_mirror", EXCLUDE_REASON["smoke_mirror"]
        return "one_shot_round_helper", EXCLUDE_REASON["one_shot_round_helper"]
    return None, None


def build_population():
    rows, excluded = [], []
    for p in candidates():
        name = os.path.basename(p)
        try:
            text = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if "LEDGER" not in text or "etf_book_forward" not in text:
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        code, why = exclusion_reason(name)
        if code:
            excluded.append({"module": rel, "class": code, "reason": why})
            continue
        usage = module_usage(text)
        rows.append({"module": rel, "kind": module_kind(text, name), "usage": usage,
                     "duplicate_effect": duplicate_effect(usage),
                     "roles_present": [r for r in ROLES if usage.get(r)]})
    return rows, excluded


# --------------------------------------------------------------------------- empirical arms
def duplicated_ledger(led):
    """The shape E584 published: the last six rows appended a second time."""
    dup = copy.deepcopy(led)
    bars = list(dup.get("bars") or [])
    dup["bars"] = bars + [copy.deepcopy(b) for b in bars[-6:]]
    return dup


def _mean_rate(series):
    vals = [r["rate"] for r in series if r.get("rate") is not None]
    return (sum(vals) / len(vals) * 100.0) if vals else None


def run_arms(led):
    arms = {}
    tmp = tempfile.mkdtemp(prefix="e588_")
    clean_p = os.path.join(tmp, "LEDGER.json")
    dup_p = os.path.join(tmp, "LEDGER-dup.json")
    with io.open(clean_p, "w", encoding="utf-8") as f:
        json.dump(led, f, ensure_ascii=False)
    dup = duplicated_ledger(led)
    with io.open(dup_p, "w", encoding="utf-8") as f:
        json.dump(dup, f, ensure_ascii=False)

    # arm 1: per-row rate series (e592) -- a mean over rows is a denominator over rows
    try:
        import e592_carry_phase as e592
        s_c, s_d = e592.published_rate_series(led), e592.published_rate_series(dup)
        arms["per_row_mean"] = {
            "available": True, "module": "scripts/e592_carry_phase.py",
            "function": "published_rate_series",
            "rows_clean": len(s_c), "rows_dup": len(s_d),
            "mean_pct_clean": round(_mean_rate(s_c) or 0.0, 6),
            "mean_pct_dup": round(_mean_rate(s_d) or 0.0, 6),
            "effect": "blind: the six repeated bars are weighted twice in a per-row mean"}
    except Exception as exc:                                        # pragma: no cover
        arms["per_row_mean"] = {"available": False, "reason": repr(exc)[:200]}

    # arm 2: endpoint-keyed reader (etf_book_order._ledger_book)
    try:
        import etf_book_order as order
        a = order._ledger_book(clean_p) or {}
        b = order._ledger_book(dup_p) or {}
        a.pop("source", None)
        b.pop("source", None)
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        arms["endpoint_reader"] = {
            "available": True, "module": "scripts/etf_book_order.py",
            "function": "_ledger_book", "fields_changed": diff,
            "effect": ("immune: it reads bars[-1] and the book_in_force block, so appended "
                       "dupes change no field" if not diff else "changed")}
    except Exception as exc:                                        # pragma: no cover
        arms["endpoint_reader"] = {"available": False, "reason": repr(exc)[:200]}

    # arm 3: the CEO page's own forward block, fed through its module-level LEDGER constant
    try:
        import etf_book_ceo_page as page
        orig = page.LEDGER
        try:
            page.LEDGER = clean_p
            clean_page = page.build()
            page.LEDGER = dup_p
            dup_page = page.build()
        finally:
            page.LEDGER = orig
        f1 = (clean_page[0] if isinstance(clean_page, tuple) else clean_page) or {}
        f2 = (dup_page[0] if isinstance(dup_page, tuple) else dup_page) or {}
        f1 = f1.get("forward") or {}
        f2 = f2.get("forward") or {}
        diff = sorted(k for k in set(f1) | set(f2) if f1.get(k) != f2.get(k))
        arms["ceo_page_forward"] = {
            "available": bool(f1),
            "module": "scripts/etf_book_ceo_page.py", "function": "build",
            "forward_clean": f1, "forward_dup": f2, "fields_changed": diff,
            "effect": ("blind: it publishes len(bars) as the forward bar count"
                       if "bars" in diff else "no change")}
    except Exception as exc:                                        # pragma: no cover
        arms["ceo_page_forward"] = {"available": False, "reason": repr(exc)[:200]}

    for p in (clean_p, dup_p):
        try:
            os.remove(p)
        except OSError:
            pass
    try:
        os.rmdir(tmp)
    except OSError:
        pass
    return arms


# --------------------------------------------------------------------------- face
def build(write=True):
    rows, excluded = build_population()
    counts = count_modules(rows)
    with io.open(LEDGER, encoding="utf-8") as f:
        led = json.load(f)
    bars = list(led.get("bars") or [])
    arms = run_arms(led)
    face = {
        "schema": "e588.ledger_rowcount.v1",
        "study": "E588",
        "evidence_cutoff": "2026-11-06",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "question": ("For every in-repo consumer of results/etf_book_forward/LEDGER.json, does it "
                     "use the row count as a count (a denominator) or key by bar, and would it "
                     "have noticed E584's six duplicated rows?"),
        "ledger_today": {"path": "results/etf_book_forward/LEDGER.json",
                         "rows": len(bars), "bars": len({b.get("bar") for b in bars}),
                         "rows_equal_bars": len(bars) == len({b.get("bar") for b in bars}),
                         "first": bars[0].get("bar") if bars else None,
                         "last": bars[-1].get("bar") if bars else None},
        "population": {
            "definition": ("every .py under scripts/, Tools/, firm/, live/, monitor/ and repo "
                           "root whose own text names both 'etf_book_forward' and 'LEDGER'; "
                           "one-shot round helpers and smoke mirrors are published as excluded"),
            "candidates_addressing_the_ledger": len(rows) + len(excluded),
            "consumers_graded": len(rows),
            "excluded": excluded,
        },
        "role_definitions": {
            "row_count": "a len() over the bars list used as a value (published, stored, fed on)",
            "row_count_in_arithmetic": "that len() sits on a line that also divides/multiplies",
            "row_count_presence_only": ("a len() over bars compared only to 0/1/2 -- an emptiness "
                                        "test that reads the same on 11 and 17 rows"),
            "endpoint_key": "bars[0] / bars[-1]",
            "bar_key": "a dict keyed by 'bar' or a 'bar' field read",
            "dedupe_guard": "a unique/rows_equal_bars/accrued_bars_on_disk style guard",
        },
        "modules": rows,
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, arms),
        "empirical_arms": arms,
        "limits": [
            "role detection is line-level on each module's own literals; a count relayed through "
            "helper frames is invisible, so the blind count is a lower bound",
            "a relay module that only passes the path to another module is graded "
            "names_the_path_but_reads_no_bars, which is not evidence of a reader defect",
            "the six-row duplication reproduces E584's shape (17 rows over 11 bars), not its "
            "exact row objects",
            "arm 3 patches the module-level LEDGER constant of etf_book_ceo_page and calls its "
            "pure build(); run() (the writer) is never touched",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        body = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
        with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        with io.open(LATEST_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    return face


def face_problems(face):
    p = []
    rows = face.get("modules") or []
    counts = face.get("counts") or {}
    want = count_modules(rows)
    for k, v in want.items():
        if counts.get(k) != v:
            p.append("count %s is %r but re-derives to %r" % (k, counts.get(k), v))
            break
    for r in rows:
        eff = r.get("duplicate_effect")
        if eff != duplicate_effect(r.get("usage") or {}):
            p.append("%s: duplicate_effect does not follow its own usage" % r.get("module"))
            break
        if not r.get("usage"):
            p.append("%s carries no usage block" % r.get("module"))
            break
        # every evidence line must still exist and still match a role pattern
        rel = r["module"]
        path = os.path.join(ROOT, rel.replace("/", os.sep))
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read().splitlines()
        except Exception:
            p.append("%s: not readable on disk" % rel)
            break
        bad = None
        for role, evs in (r.get("usage") or {}).items():
            for ev in evs or []:
                ln = ev.get("line") or 0
                if ln < 1 or ln > len(text):
                    bad = "%s: evidence line %s is out of range" % (rel, ln)
                    break
                if role not in classify_line(text[ln - 1]):
                    bad = "%s:%s no longer plays role %s" % (rel, ln, role)
                    break
            if bad:
                break
        if bad:
            p.append(bad)
            break
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    lt = face.get("ledger_today") or {}
    if lt.get("rows_equal_bars") != (lt.get("rows") == lt.get("bars")):
        p.append("ledger_today rows_equal_bars disagrees with its own two counts")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    # leg1 the classifier reads the role off the line, not a name list
    chk("leg1 len(bars) is a row count",
        "row_count" in classify_line("fwd = {'bars': len(bars)}"))
    chk("leg1b a count used as a count in arithmetic is flagged",
        "row_count_in_arithmetic" in classify_line("hist = (g ** (252 / len(bars)) - 1) * 100"))
    chk("leg1c a bare row count is not called arithmetic",
        "row_count_in_arithmetic" not in classify_line("n = len(bars)"))
    chk("leg1d len(names) is not a row count of bars",
        "row_count" not in classify_line("n = len(names)"))
    chk("leg1e an emptiness test is presence, not a count",
        "row_count_presence_only" in classify_line("if not names or len(bars) < 1:")
        and "row_count" not in classify_line("if not names or len(bars) < 1:"))
    chk("leg1f a comparison against a real threshold is still a count",
        "row_count" in classify_line("if len(bars) > 250:"))

    # leg2 the key arms
    chk("leg2 bars[-1] is an endpoint key",
        "endpoint_key" in classify_line("last = bars[-1] if bars else {}"))
    chk("leg2b a dict keyed by 'bar' is a bar key",
        "bar_key" in classify_line("book = {b['bar']: b['nav'] for b in bars}"))
    chk("leg2c a title line with the word 'bar' is not a bar key",
        "bar_key" not in classify_line('print("one row per bar")'))

    # leg3 the dedupe guard
    chk("leg3 a uniqueness guard is seen",
        "dedupe_guard" in classify_line("dup = len({b['bar'] for b in bars}) != len(bars)"))
    chk("leg3b rows_equal_bars is a guard",
        "dedupe_guard" in classify_line('"rows_equal_bars": len(dates) == len(uniq),'))

    # leg4 duplicate_effect ordering: a guard outranks a count
    chk("leg4 a guard wins over a count",
        duplicate_effect({"dedupe_guard": [1], "row_count": [1]}) == "guarded")
    chk("leg4b a count with no guard is blind",
        duplicate_effect({"row_count": [1]}) == "blind_row_count")
    chk("leg4c endpoint-only is immune",
        duplicate_effect({"endpoint_key": [1]}) == "immune_keyed_or_endpoint")
    chk("leg4d nothing is its own class",
        duplicate_effect({}) == "names_the_path_but_reads_no_bars")

    # leg5 counts and verdict
    rows = [{"module": "a.py", "usage": {"row_count": [1]}, "duplicate_effect": "blind_row_count"},
            {"module": "b.py", "usage": {"dedupe_guard": [1]}, "duplicate_effect": "guarded"}]
    c = count_modules(rows)
    chk("leg5 counts follow the rows",
        c["modules_blind_to_a_duplicated_row"] == 1 and c["modules_guarded"] == 1
        and c["blind_modules"] == ["a.py"], c)
    chk("leg5b one blind module makes the verdict SOME_BLIND", verdict_from(c) == V_SOME_BLIND)
    c2 = count_modules([rows[1]])
    chk("leg5c no blind module makes it ALL_GUARDED", verdict_from(c2) == V_ALL_GUARDED)
    chk("leg5d an empty population has its own verdict",
        verdict_from(count_modules([])) == V_NO_CONSUMER)

    # leg6 the guard re-derives counts and evidence (fixture taken from the live population)
    rows_live, _ex = build_population()
    pick = next((r for r in rows_live
                 if r["usage"].get("row_count") and r["duplicate_effect"] == "blind_row_count"),
                None)
    chk("leg6 the live population offers a blind row_count module to grade",
        pick is not None, [r["module"] for r in rows_live][:5])
    pick = pick or {"module": "scripts/e592_carry_phase.py",
                    "usage": {"row_count": [{"line": 127, "code": "x"}]},
                    "duplicate_effect": "blind_row_count"}
    one = count_modules([pick])
    face = {"modules": [pick], "counts": one, "verdict": verdict_from(one), "answer": "x",
            "ledger_today": {"rows": 11, "bars": 11, "rows_equal_bars": True}}
    pr = face_problems(face)
    chk("leg6 the guard accepts a face whose counts and evidence re-derive", pr == [], pr)
    bad = json.loads(json.dumps(face))
    bad["counts"]["modules_blind_to_a_duplicated_row"] = 0
    chk("leg6b the guard refuses a count that does not re-derive",
        any("modules_blind_to_a_duplicated_row" in s for s in face_problems(bad)),
        face_problems(bad))
    src = io.open(os.path.join(ROOT, pick["module"].replace("/", os.sep)),
                  encoding="utf-8", errors="replace").read().splitlines()
    blank = next((i for i, l in enumerate(src, 1) if "row_count" not in classify_line(l)), 1)
    bad2 = json.loads(json.dumps(face))
    bad2["modules"][0]["usage"]["row_count"][0] = {"line": blank, "code": "not a count"}
    chk("leg6c the guard refuses evidence that no longer plays the role",
        any("no longer plays role" in s for s in face_problems(bad2)), face_problems(bad2))
    bad3 = json.loads(json.dumps(face))
    bad3["verdict"] = V_ALL_GUARDED
    chk("leg6d the guard refuses a verdict that contradicts the counts",
        any("verdict does not follow" in s for s in face_problems(bad3)), face_problems(bad3))

    # leg7 the duplication arm has the shape E584 published
    led = {"bars": [{"bar": "d%d" % i, "nav": 1.0 + i / 100.0} for i in range(11)]}
    dup = duplicated_ledger(led)
    chk("leg7 the arm publishes 17 rows over 11 bars",
        len(dup["bars"]) == 17 and len({b["bar"] for b in dup["bars"]}) == 11, len(dup["bars"]))
    chk("leg7b the clean ledger is untouched by the arm", len(led["bars"]) == 11)
    chk("leg7c the duplication is a copy, not a shared reference",
        dup["bars"][0] is not led["bars"][0])

    # leg8 an empty bars list does not crash the arm or the mean
    chk("leg8 an empty per-row series has no mean", _mean_rate([]) is None)
    chk("leg8b a duplicated empty ledger still has zero rows",
        len(duplicated_ledger({"bars": []})["bars"]) == 0)

    n_ok = sum(1 for x in ok if x)
    print("\nselftest %d/%d" % (n_ok, len(ok)))
    return 0 if n_ok == len(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    mode = (argv[1] if len(argv) > 1 else "build").lower()
    if mode == "selftest":
        return selftest()
    if mode == "build":
        face = build(write=True)
        pr = face_problems(face)
        print("built %s | verdict=%s"
              % (os.path.relpath(OUT_PATH, ROOT), face.get("verdict")))
        print("answer:", face.get("answer"))
        if pr:
            print("problems:", pr)
            return 2
        return 0
    if mode == "check":
        face = build(write=False)
        pr = face_problems(face)
        print("problems=%s" % pr)
        return 0 if not pr else 2
    if mode == "verify":
        if not os.path.exists(OUT_PATH):
            print("no face on disk")
            return 2
        with io.open(OUT_PATH, encoding="utf-8") as f:
            on_disk = json.load(f)
        fresh = build(write=False)
        keys = ("modules", "counts", "verdict", "empirical_arms", "ledger_today",
                "population", "answer")
        diff = [k for k in keys if on_disk.get(k) != fresh.get(k)]
        print("problems=%s" % (["field does not re-derive: %s" % k for k in diff] or []))
        return 0 if not diff else 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))