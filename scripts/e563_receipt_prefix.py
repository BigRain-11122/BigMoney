"""E563 (r1590 bm-b): is a short chain receipt a PREFIX of its own round's leg table?

E561 joined 159 short receipts to the LEGS table of their own round and published "a stopped run
and an --only run look identical".  E562 settled that the stopped run is not possible (all
runners close the receipt after the leg loop), which leaves filtering.  But "filtering" and
"stopping" are only indistinguishable if the receipt never lines up with the head of the table.
This study asks the shape question directly:

  * ``exact_prefix``       -- the receipt's leg names are table[0..n-1] verbatim.  This is the
                              only shape an ordered stop could take, so an exact prefix means the
                              file alone still cannot separate the two stories.
  * ``prefix_with_a_gap``  -- names are an ordered subsequence starting at table[0] but skipping
                              a leg in the middle: an ordered run that dropped a leg, not a
                              filtered head.
  * ``arbitrary_subset``   -- names run through the table in order but start after table[0].
                              Only a filter explains this: no ordered stop begins at leg #4.
  * ``out_of_order``       -- every name is in the table but they were run out of table order
                              (the --only list was not sorted, or the runner reorders).
  * ``foreign_name``       -- at least one name is absent from the table at that commit.
  * ``repeated_name``      -- a name appears twice in the receipt.
  * ``table_unreadable`` / ``receipt_unreadable`` -- honest unknowns, published as such.

Everything is static: no runner is executed, no receipt is rewritten.  The per-row evidence is
the index of each leg name inside its own round's table, so the class can be re-derived from the
published row without re-reading any blob.

  python scripts/e563_receipt_prefix.py build      # write the dated face + latest
  python scripts/e563_receipt_prefix.py check      # re-derive from live sources, compare
  python scripts/e563_receipt_prefix.py verify     # re-derive, print problems
  python scripts/e563_receipt_prefix.py selftest   # fixtures only, no git
"""
from __future__ import annotations

import ast
import glob
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVIDENCE_CUTOFF = "2026-11-08"
DATED_PREFIX = "RECEIPTPREFIX"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "receiptprefix_latest.json")
E561_FACE = os.path.join(STATE_TILT, "RECEIPTTABLE-2026-11-08.json")

RECEIPT_RE = __import__("re").compile(r"^_r(\d+)bm([abc])_s6_chain\.json$")

C_EXACT_PREFIX = "an_exact_prefix_of_the_table"
C_PREFIX_GAP = "a_prefix_that_skips_a_leg_in_the_middle"
C_SUBSET = "a_subset_in_table_order_that_starts_after_the_first_leg"
C_OUT_OF_ORDER = "the_same_legs_in_a_different_order"
C_FOREIGN = "at_least_one_leg_name_is_not_in_the_table"
C_REPEATED = "a_leg_is_named_twice_in_the_receipt"
C_TABLE_UNREADABLE = "the_table_of_its_own_round_could_not_be_read"
C_RECEIPT_UNREADABLE = "the_receipt_names_could_not_be_read"

ORDER_CLASSES = (C_EXACT_PREFIX, C_PREFIX_GAP, C_SUBSET, C_OUT_OF_ORDER, C_FOREIGN,
                 C_REPEATED, C_TABLE_UNREADABLE, C_RECEIPT_UNREADABLE)

VERDICT_PREFIX_UNKNOWN = "a_short_receipt_can_be_an_exact_prefix_so_the_file_still_cannot_tell_an_ordered_stop_from_a_filtered_head"
VERDICT_FILTER_ONLY = "no_short_receipt_is_a_prefix_of_its_table_so_filtering_is_the_only_story_left"
VERDICT_BLIND = "the_tables_could_not_be_read_so_nothing_is_concluded"


# ---- git ------------------------------------------------------------------------
def _git(args, timeout=180):
    import subprocess
    try:
        p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, timeout=timeout)
    except Exception:
        return None
    if p.returncode != 0:
        return None
    return p.stdout


def _blobs(specs):
    """{spec: text} through ONE cat-file process; a missing object is an honest answer."""
    import subprocess
    specs = [s for s in dict.fromkeys(specs) if s]
    if not specs:
        return {}
    payload = ("\n".join(specs) + "\n").encode("utf-8")
    try:
        p = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=payload,
                           capture_output=True, timeout=240)
    except Exception:
        return {}
    if p.returncode != 0:
        return {}
    out, i, found = p.stdout, 0, {}
    for spec in specs:
        nl = out.find(b"\n", i)
        if nl < 0:
            break
        header = out[i:nl].decode("utf-8", "replace").strip()
        i = nl + 1
        parts = header.rsplit(" ", 2)
        if len(parts) != 3 or not parts[2].isdigit():
            continue
        size = int(parts[2])
        body = out[i:i + size]
        i += size + 1
        found[spec] = body.decode("utf-8-sig", "replace")
    return found


# ---- reading the table -----------------------------------------------------------
def _legs_names(src):
    """Ordered leg names from a runner source, or (None, reason)."""
    try:
        tree = ast.parse(src)
    except Exception as exc:
        return None, "the runner source does not parse: %s" % str(exc)[:80]
    value, alias = None, None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "LEGS":
                    value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == "LEGS":
            value = node.value
    if value is None:
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(a.name == "LEGS" for a in node.names):
                return None, "LEGS is imported from %s" % (node.module or "?")
        return None, "no LEGS table in the runner"
    if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name):
        alias = value.value.id
        return None, "LEGS is an alias of %s.LEGS" % alias
    if not isinstance(value, (ast.List, ast.Tuple)):
        return None, "LEGS is not a literal list"
    names = []
    for elt in value.elts:
        if isinstance(elt, (ast.Tuple, ast.List)) and elt.elts \
                and isinstance(elt.elts[0], ast.Constant) \
                and isinstance(elt.elts[0].value, str):
            names.append(elt.elts[0].value)
        else:
            return None, "a LEGS row does not start with a string constant"
    if not names:
        return None, "the LEGS table is empty"
    return names, None


def _module_alias_path(src, alias):
    """Tools/<module>.py for a runner that does ``import <module>`` and reuses its LEGS."""
    try:
        tree = ast.parse(src)
    except Exception:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if (a.asname or a.name.split(".")[-1]) == alias:
                    return os.path.join("Tools", a.name.split(".")[-1] + ".py")
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[-1] == alias:
                return os.path.join("Tools", node.module.split(".")[-1] + ".py")
    return None


# ---- reading a receipt -----------------------------------------------------------
_LIVE_CACHE = {}


def _live_table(machine):
    """The LEGS table of ``Tools/s6_chain_bm<X>.py`` as it is on disk NOW (drift, never a gate)."""
    if not machine:
        return None
    if machine in _LIVE_CACHE:
        return _LIVE_CACHE[machine]
    path = os.path.join(ROOT, "Tools", "s6_chain_bm%s.py" % machine)
    table = None
    if os.path.isfile(path):
        try:
            with io.open(path, encoding="utf-8-sig") as fh:
                table, _why = _legs_names(fh.read())
        except Exception:
            table = None
    _LIVE_CACHE[machine] = table
    return table
def _leg_names_of(payload):
    """The receipt's leg names in file order, or None when the shape does not carry them."""
    rows = None
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("legs"), list):
        rows = payload["legs"]
    if rows is None:
        return None
    names = []
    for r in rows:
        if not isinstance(r, dict) or not isinstance(r.get("leg"), str):
            return None
        names.append(r["leg"])
    return names


# ---- the classifier --------------------------------------------------------------
def classify(names, table):
    """Class from the receipt's names and its own round's table.  Pure function."""
    if table is None:
        return C_TABLE_UNREADABLE, None
    if names is None:
        return C_RECEIPT_UNREADABLE, None
    idx = []
    for n in names:
        idx.append(table.index(n) if n in table else None)
    return classify_idx(idx), idx


def classify_idx(idx):
    if idx is None:
        return C_RECEIPT_UNREADABLE
    if any(i is None for i in idx):
        return C_FOREIGN
    if len(set(idx)) != len(idx):
        return C_REPEATED
    if idx != sorted(idx):
        return C_OUT_OF_ORDER
    if idx == list(range(len(idx))):
        return C_EXACT_PREFIX
    if idx and idx[0] == 0:
        return C_PREFIX_GAP
    return C_SUBSET


# ---- population ------------------------------------------------------------------
def _sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def read_population():
    """E561's short rows, re-derived locally as rows < table_at_its_round."""
    with io.open(E561_FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    rows, local_short = [], 0
    for r in face.get("rows") or []:
        if not isinstance(r, dict) or r.get("unparsed"):
            continue
        n, table = r.get("rows"), r.get("table_at_its_round")
        if isinstance(n, int) and isinstance(table, int) and n < table:
            local_short += 1
            rows.append({
                "file": r.get("file"),
                "machine": r.get("machine"),
                "name_round": r.get("name_round"),
                "rows": n,
                "table_at_its_round": table,
                "join_commit": r.get("join_commit"),
                "committed": bool(r.get("committed")),
            })
    return rows, local_short, face


def build(write=True):
    rows, local_short, e561_face = read_population()

    runner_specs, receipt_specs = [], []
    for r in rows:
        if r.get("machine") and r.get("join_commit"):
            runner_specs.append("%s:Tools/s6_chain_bm%s.py" % (r["join_commit"], r["machine"]))
            receipt_specs.append("%s:results/%s" % (r["join_commit"], r["file"]))
    blobs = _blobs(runner_specs + receipt_specs)

    table_cache, table_reason = {}, {}
    for r in rows:
        spec = runner_specs and ("%s:Tools/s6_chain_bm%s.py" % (r["join_commit"], r["machine"]))
        if not spec:
            continue
        if spec in table_cache or spec in table_reason:
            continue
        src = blobs.get(spec)
        if src is None:
            table_reason[spec] = "no runner blob at that commit"
            continue
        names, why = _legs_names(src)
        if names is None:
            alias_path = _module_alias_path(src, (why or "").split(" ")[0]) if why else None
            if alias_path:
                sib = _blobs(["%s:%s" % (r["join_commit"], alias_path.replace("\\", "/"))])
                for key, text in sib.items():
                    names, why2 = _legs_names(text)
                    if names is None:
                        why = why + " / sibling: " + (why2 or "unreadable")
            if names is None:
                table_reason[spec] = why
                continue
        table_cache[spec] = names

    for r in rows:
        spec = ("%s:Tools/s6_chain_bm%s.py" % (r["join_commit"], r["machine"])
                if r.get("machine") and r.get("join_commit") else None)
        table = table_cache.get(spec)
        r["runner_spec"] = spec
        r["table_size"] = len(table) if table else None
        r["table_reason"] = table_reason.get(spec)
        names = None
        path = os.path.join(ROOT, "results", r["file"] or "")
        payload = None
        if r.get("file") and os.path.isfile(path):
            try:
                with io.open(path, encoding="utf-8-sig") as fh:
                    payload = json.load(fh)
            except Exception:
                payload = None
        if payload is None and spec:
            text = blobs.get("%s:results/%s" % (r["join_commit"], r["file"]))
            if text:
                try:
                    payload = json.loads(text)
                except Exception:
                    payload = None
        names = _leg_names_of(payload)
        r["leg_names"] = names
        cls, idx = classify(names, table)
        r["class"] = cls
        r["leg_indices"] = idx
        r["names_in_table_order"] = bool(idx is not None and None not in idx
                                         and len(set(idx)) == len(idx))
        r["first_leg_is_the_table_head"] = bool(idx and idx[0] == 0)
        # a name absent from the table AT THE JOIN COMMIT can mean the leg was added after that
        # commit (the receipt was produced by a runner newer than the commit it joins to) or that
        # the receipt came from another program / a renamed leg.  Today's table separates them.
        r["foreign_names_in_today_s_table"] = None
        if cls == C_FOREIGN:
            live = _live_table(r.get("machine"))
            r["foreign_names_in_today_s_table"] = [
                {"leg": n, "in_today_s_table": bool(live and n in live)}
                for n in names if n not in (table or [])]
    rows.sort(key=lambda x: (x.get("machine") or "", int(x.get("name_round") or 0)))

    s = {"short_receipts": len(rows)}
    for cls in ORDER_CLASSES:
        s[cls] = sum(1 for r in rows if r.get("class") == cls)
    s["names_in_table_order"] = sum(1 for r in rows if r.get("names_in_table_order"))
    s["first_leg_is_the_table_head"] = sum(1 for r in rows if r.get("first_leg_is_the_table_head"))
    s["single_leg_receipts"] = sum(1 for r in rows if r.get("rows") == 1)
    s["single_leg_that_is_the_table_head"] = sum(
        1 for r in rows if r.get("rows") == 1 and r.get("first_leg_is_the_table_head"))
    s["tables_read"] = sum(1 for r in rows if r.get("table_size"))
    s["receipts_whose_names_were_recovered"] = sum(1 for r in rows if r.get("leg_names"))
    s["tables_unreadable_reasons"] = sorted({r["table_reason"] for r in rows
                                             if r.get("table_reason")})
    s["foreign_rows"] = sum(1 for r in rows if r.get("class") == C_FOREIGN)
    s["foreign_names_that_exist_in_today_s_table"] = sum(
        1 for r in rows for f in (r.get("foreign_names_in_today_s_table") or [])
        if f["in_today_s_table"])
    s["foreign_names_that_exist_in_no_current_table"] = sum(
        1 for r in rows for f in (r.get("foreign_names_in_today_s_table") or [])
        if not f["in_today_s_table"])
    s["_class_sum"] = sum(s[c] for c in ORDER_CLASSES)

    verdict, line = _verdict(s)
    face = {
        "card": "E563",
        "study": "E563",
        "dept": "research+engineering",
        "machine": "bm-b",
        "round": "r1590",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {
            "face": os.path.relpath(E561_FACE, ROOT).replace("\\", "/"),
            "sha16": _sha16(E561_FACE),
            "short_rows_in_that_face": local_short,
            "note": "read as a vintage (E369): the receipt directory is live, so this face answers "
                    "for the short receipts E561 had classified on 2026-11-08; the short class "
                    "is re-derived from rows < table_at_its_round rather than trusted",
        },
        "summary": s,
        "rows": rows,
        "control_arms": _control_arms(),
        "verdict": verdict,
        "verdict_line": line,
        "note": "static only: no runner is executed and no receipt is rewritten; each row carries "
                "the index of its leg names inside its own round's LEGS table, so the class can "
                "be recomputed from the published row (classify_idx) without any blob",
        "producers": {
            "script": "scripts/e563_receipt_prefix.py",
            "selftest": "python scripts/e563_receipt_prefix.py selftest",
            "card": "knowledge/METHODOLOGY_ASSETS.md E563",
        },
    }
    if write:
        _write(LATEST, face)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
    return face


def _verdict(s):
    s = {"short_receipts": 0, "tables_read": 0, "receipts_whose_names_were_recovered": 0,
         "single_leg_receipts": 0, "single_leg_that_is_the_table_head": 0,
         "names_in_table_order": 0, "first_leg_is_the_table_head": 0,
         "foreign_names_that_exist_in_today_s_table": 0,
         "foreign_names_that_exist_in_no_current_table": 0,
         **s}
    if not s["tables_read"] or not s["receipts_whose_names_were_recovered"]:
        return VERDICT_BLIND, ("none of the %d short receipts could be paired with the leg names "
                               "of its own table and itself, so nothing is concluded"
                               % s["short_receipts"])
    line = ("%d short receipts; %d read against the LEGS table of their own round: "
            "%d are an exact prefix, %d a prefix that skips a leg, %d a subset in table order "
            "that starts after the first leg, %d the same legs in another order, %d name a leg "
            "the table does not contain (of those names %d do exist in today's table, i.e. they "
            "postdate the join commit, and %d exist in no current table), %d repeat a leg; "
            "%d of the %d single-leg receipts ran the head of the table and %d receipts are "
            "entirely in table order.  %d tables and %d receipts were unreadable and are "
            "published as such."
            % (s["short_receipts"], s["tables_read"],
               s[C_EXACT_PREFIX], s[C_PREFIX_GAP], s[C_SUBSET], s[C_OUT_OF_ORDER],
               s[C_FOREIGN], s["foreign_names_that_exist_in_today_s_table"],
               s["foreign_names_that_exist_in_no_current_table"], s[C_REPEATED],
               s["single_leg_that_is_the_table_head"], s["single_leg_receipts"],
               s["names_in_table_order"],
               s[C_TABLE_UNREADABLE], s[C_RECEIPT_UNREADABLE]))
    if s[C_EXACT_PREFIX]:
        return VERDICT_PREFIX_UNKNOWN, line
    if s[C_TABLE_UNREADABLE] and s[C_SUBSET] == 0 and s[C_PREFIX_GAP] == 0:
        return VERDICT_BLIND, line
    return VERDICT_FILTER_ONLY, line


# ---- control arms ----------------------------------------------------------------
TABLE = ["dualrun", "compute_audit", "py_watermark", "update_daily", "market_regime"]


def _control_arms():
    def case(names, table=TABLE):
        cls, idx = classify(names, table)
        return {"class": cls, "leg_indices": idx}

    return {
        "an_exact_prefix_is_recognised": case(["dualrun", "compute_audit", "py_watermark"]),
        "a_gap_after_the_head_is_not_an_exact_prefix":
            case(["dualrun", "py_watermark", "update_daily"]),
        "a_filtered_head_is_its_own_class": case(["update_daily", "market_regime"]),
        "another_order_is_published_not_folded":
            case(["compute_audit", "dualrun"]),
        "a_name_absent_from_the_table_is_foreign": case(["dualrun", "ghost_leg"]),
        "a_repeated_leg_is_not_a_prefix": case(["dualrun", "dualrun"]),
        "an_unreadable_table_is_its_own_class": case(["dualrun"], None),
        "an_unreadable_receipt_is_its_own_class": case(None, TABLE),
        "an_empty_receipt_is_not_a_prefix": case([], TABLE),
        "idx_classifier_round_trips": {
            "class": classify_idx([0, 1, 3]),
            "same_as_names": classify(["dualrun", "compute_audit", "update_daily"], TABLE)[0],
        },
    }


# ---- face validation -------------------------------------------------------------
def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def face_problems(face):
    """Every claim in the face re-derived from the face's own rows.  Never touches git."""
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if s.get("short_receipts") != len(rows):
        problems.append("summary.short_receipts %r != %d rows"
                        % (s.get("short_receipts"), len(rows)))
    for cls in ORDER_CLASSES:
        got = sum(1 for r in rows if r.get("class") == cls)
        if s.get(cls) != got:
            problems.append("summary.%s %r != %d in rows" % (cls, s.get(cls), got))
    if sum(s.get(c, 0) for c in ORDER_CLASSES) != len(rows):
        problems.append("a row is in no class or in two")
    for r in rows:
        recomputed = classify_idx(r.get("leg_indices"))
        if r.get("class") != recomputed:
            problems.append("%s: class %r does not re-derive (%r)"
                            % (r.get("file"), r.get("class"), recomputed))
        names = r.get("leg_names")
        idx = r.get("leg_indices")
        if names is not None and idx is not None and len(names) != len(idx):
            problems.append("%s: %d names but %d indices"
                            % (r.get("file"), len(names), len(idx)))
        if r.get("class") in (C_TABLE_UNREADABLE, C_RECEIPT_UNREADABLE) and idx is not None:
            problems.append("%s: an unreadable row carries indices" % r.get("file"))
        if r.get("class") not in (C_TABLE_UNREADABLE, C_RECEIPT_UNREADABLE) and idx is None:
            problems.append("%s: a readable row carries no indices" % r.get("file"))
    exp_verdict, exp_line = _verdict(s)
    if face.get("verdict") != exp_verdict:
        problems.append("verdict %r != re-derived %r" % (face.get("verdict"), exp_verdict))
    if face.get("verdict_line") != exp_line:
        problems.append("verdict_line does not re-derive")
    if not (face.get("population_source") or {}).get("sha16"):
        problems.append("the population is not pinned to a vintage")
    got_foreign = sum(1 for r in rows if r.get("class") == C_FOREIGN)
    if s.get("foreign_rows") != got_foreign:
        problems.append("summary.foreign_rows %r != %d" % (s.get("foreign_rows"), got_foreign))
    big = sum(1 for r in rows for f in (r.get("foreign_names_in_today_s_table") or [])
              if f["in_today_s_table"])
    small = sum(1 for r in rows for f in (r.get("foreign_names_in_today_s_table") or [])
                if not f["in_today_s_table"])
    if s.get("foreign_names_that_exist_in_today_s_table") != big:
        problems.append("foreign-name counters do not re-derive (today's table)")
    if s.get("foreign_names_that_exist_in_no_current_table") != small:
        problems.append("foreign-name counters do not re-derive (no current table)")
    if got_foreign and big + small == 0:
        problems.append("a foreign row carries no name classification")
    for r in rows:
        if r.get("class") != C_FOREIGN and r.get("foreign_names_in_today_s_table") is not None:
            problems.append("%s: a non-foreign row carries a foreign classification"
                            % r.get("file"))
    arms = face.get("control_arms") or {}
    live = _control_arms()
    if arms != live:
        problems.append("control arms do not re-derive")
    return problems


def _check_arms():
    arms = _control_arms()
    bad = []
    if arms["an_exact_prefix_is_recognised"]["class"] != C_EXACT_PREFIX:
        bad.append("exact prefix no longer recognised")
    if arms["a_gap_after_the_head_is_not_an_exact_prefix"]["class"] != C_PREFIX_GAP:
        bad.append("a gap is no longer its own class")
    if arms["a_filtered_head_is_its_own_class"]["class"] != C_SUBSET:
        bad.append("a filtered head is no longer its own class")
    if arms["another_order_is_published_not_folded"]["class"] != C_OUT_OF_ORDER:
        bad.append("an out-of-order run is no longer published")
    if arms["a_name_absent_from_the_table_is_foreign"]["class"] != C_FOREIGN:
        bad.append("a foreign name is no longer caught")
    if arms["a_repeated_leg_is_not_a_prefix"]["class"] != C_REPEATED:
        bad.append("a repeated leg is no longer caught")
    if arms["an_unreadable_table_is_its_own_class"]["class"] != C_TABLE_UNREADABLE:
        bad.append("an unreadable table is no longer honest")
    if arms["an_unreadable_receipt_is_its_own_class"]["class"] != C_RECEIPT_UNREADABLE:
        bad.append("an unreadable receipt is no longer honest")
    if arms["an_empty_receipt_is_not_a_prefix"]["class"] != C_EXACT_PREFIX:
        bad.append("an empty receipt is not classified")
    if arms["idx_classifier_round_trips"]["class"] != arms["idx_classifier_round_trips"][
            "same_as_names"]:
        bad.append("the index classifier disagrees with the name classifier")
    return bad


def selftest():
    bad = list(_check_arms())
    face = build(write=False)
    bad.extend(face_problems(face))
    # doctor: a doctored class must be refused
    doc = json.loads(json.dumps(face))
    if doc["rows"]:
        doc["rows"][0]["leg_indices"] = [0, 1, 2]
        doc["rows"][0]["class"] = C_EXACT_PREFIX
        if not face_problems(doc):
            bad.append("a hand-written class was accepted")
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    if not face_problems(doc):
        bad.append("a hand-written verdict was accepted")
    doc = json.loads(json.dumps(face))
    doc["summary"][C_EXACT_PREFIX] = doc["summary"].get(C_EXACT_PREFIX, 0) + 1
    if not face_problems(doc):
        bad.append("an inflated prefix count was accepted")
    if bad:
        print("SELFTEST FAIL: " + "; ".join(bad)[:600])
        return 1
    s = face["summary"]
    print("SELFTEST PASS: %d arms + %d rows; exact=%d gap=%d subset=%d order=%d foreign=%d "
          "repeat=%d table_unreadable=%d receipt_unreadable=%d"
          % (len(_control_arms()), len(face["rows"]), s[C_EXACT_PREFIX], s[C_PREFIX_GAP],
             s[C_SUBSET], s[C_OUT_OF_ORDER], s[C_FOREIGN], s[C_REPEATED],
             s[C_TABLE_UNREADABLE], s[C_RECEIPT_UNREADABLE]))
    return 0


def check():
    """Re-derive from live sources and compare with the published face."""
    fresh = build(write=False)
    try:
        with io.open(LATEST, encoding="utf-8") as fh:
            published = json.load(fh)
    except Exception as exc:
        print("CHECK FAIL: the face cannot be read: %s" % exc)
        return 1
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "summary", "card"):
        if fresh.get(key) != published.get(key):
            problems.append("live %s disagrees with the published face" % key)
    if fresh.get("rows") != published.get("rows"):
        problems.append("the live population disagrees with the published rows")
    if problems:
        print("CHECK FAIL: %d problems; first=%s" % (len(problems), problems[0][:300]))
        return 1
    print("CHECK PASS: %d rows re-derive, verdict=%s"
          % (len(published.get("rows") or []), published.get("verdict")))
    return 0


def verify():
    problems = face_problems(build(write=False))
    print(json.dumps({"problems": problems[:10], "n": len(problems)}, ensure_ascii=False))
    return 0 if not problems else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    action = argv[0] if argv else "build"
    if action == "build":
        face = build(write=True)
        s = face["summary"]
        print("BUILT %s: %d rows | exact=%d gap=%d subset=%d order=%d foreign=%d repeat=%d "
              "unreadable=%d/%d"
              % (os.path.relpath(LATEST, ROOT), len(face["rows"]), s[C_EXACT_PREFIX],
                 s[C_PREFIX_GAP], s[C_SUBSET], s[C_OUT_OF_ORDER], s[C_FOREIGN], s[C_REPEATED],
                 s[C_TABLE_UNREADABLE], s[C_RECEIPT_UNREADABLE]))
        print("VERDICT: %s" % face["verdict"])
        return 0
    if action == "check":
        return check()
    if action == "verify":
        return verify()
    if action == "selftest":
        return selftest()
    print("unknown action %r (build|check|verify|selftest)" % action)
    return 2


if __name__ == "__main__":
    sys.exit(main())