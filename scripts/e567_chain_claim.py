"""E567 (r1595 bm-b): do the printed chain sentences understate the table of their own round?

E566 priced the blindness on the reader side: a closeout printed a 39-row receipt as
"39/39 rc0" while its round's legs table held 61.  The denominator in that sentence came from
the receipt, and the receipt was a subset.  E563 showed a receipt cannot say what it selected,
so the only recoverable witness is E561's join: receipt name -> round -> runner blob at that
round -> table size.  This study asks the same question of the *prose*:

  * which sentences in the round reports state a chain leg count at all (the parse);
  * for each one, recover the round and the machine from its own row, then join to the
    receipt of that round (E561) and to the table that receipt was built from;
  * publish three counts -- equal to the table, below it (a green sentence over a subset), and
    not judgeable (no receipt / no table / no round in the row);
  * split "below it" by whether the sentence itself says it is a subset.  A sentence that
    prints "S6 7/7 rc=0 via --only" is honest and is not a defect; a sentence that prints
    "S6 chain 39/39 rc0" over a 58-leg round reads as the whole chain.

The parse rule is data in the face (regexes, windows, exclusions) so a reader can refute it,
and the sentences that carry a pair *far* from any chain word are counted and published
separately rather than silently folded into "no claim".

  python scripts/e567_chain_claim.py build      # write the dated face + latest
  python scripts/e567_chain_claim.py check      # re-derive from live reports, compare
  python scripts/e567_chain_claim.py verify     # re-derive, print problems
  python scripts/e567_chain_claim.py selftest   # fixtures only
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVIDENCE_CUTOFF = "2026-11-08"
DATED_PREFIX = "CHAINCLAIM"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "chainclaim_latest.json")
DATED = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
E561_FACE = os.path.join(STATE_TILT, "RECEIPTTABLE-2026-11-08.json")

# legacy bm-b lane keeps the un-suffixed file name (fleet/README.md §6)
REPORTS = [
    ("logs/iteration-loop/round_reports.md", "b"),
    ("logs/iteration-loop/round_reports-bm-a.md", "a"),
    ("logs/iteration-loop/round_reports-bm-c.md", "c"),
]

# ---- the parse rule (echoed verbatim into the face) -------------------------------
A_SIX = r"(?i)\bS6\b[^0-9\n]{0,45}?(\d{1,4})\s*/\s*(\d{1,4})"
B_CHAIN = r"(?i)\bchain\b[^0-9\n]{0,30}?(\d{1,4})\s*/\s*(\d{1,4})"
C_TAIL = r"(?i)\b(\d{1,4})\s*/\s*(\d{1,4})\b\s*,?\s*(?:legs?\b|rc0\b|rc=0\b)"
SMOKE_WINDOW = 45          # chars either side of the match used for the smoke-suite exclusion
REJECT_TAIL = r"(?i)py face|orphan|\d\.?\d*%"   # "S6: orphan 0/7 py faces" is not a leg count
REJECT_PREFIX = r"(?i)streak\s*\Z"              # "dualrun ZERO-DRIFT streak 17/3" is a counter
ROUND_HEAD = 180           # the row prefix that names the round
LABEL_WINDOW = 160         # chars either side used to see whether the sentence says "subset"

PATTERNS = [re.compile(A_SIX), re.compile(B_CHAIN), re.compile(C_TAIL)]
REJECT = re.compile(REJECT_TAIL)
REJECT_PRE = re.compile(REJECT_PREFIX)
PAIR = re.compile(r"(\d{1,4})\s*/\s*(\d{1,4})")
VOCAB = re.compile(r"(?i)\b(s6|chain|legs?)\b")
ROUND_PATTERNS = [
    re.compile(r"\bR(\d{1,4})\b"),
    re.compile(r"\br(\d{1,4})\b"),
    re.compile(r"\bround\s+(\d{1,4})\b"),
    re.compile(r"\|\s*(\d{3,4})\s*\|"),
]
SUBSET_LABEL = re.compile(
    r"(?i)(--only|\bsubset\b|\bpartial\b|was not run|not the full|only [^;\n]{0,24}legs?"
    r"|前 \d+ 腿|部分腿)")

# ---- claim classes ---------------------------------------------------------------
CNT_EQUALS = "the_denominator_equals_the_table_of_its_round"
CNT_LABELLED = "the_denominator_is_below_the_table_and_the_sentence_says_it_is_a_subset"
CNT_SILENT = "the_denominator_is_below_the_table_and_the_sentence_reads_as_the_whole_chain"
CNT_ABOVE = "the_denominator_is_larger_than_the_table_of_its_round"
CNT_NO_RECEIPT = "the_round_carries_no_receipt_in_the_corpus"
CNT_NO_TABLE = "the_receipt_of_that_round_cannot_be_joined_to_a_table"
CNT_NO_ROUND = "the_row_does_not_state_a_round"
CLAIM_CLASSES = (CNT_EQUALS, CNT_LABELLED, CNT_SILENT, CNT_ABOVE,
                 CNT_NO_RECEIPT, CNT_NO_TABLE, CNT_NO_ROUND)
JUDGED = (CNT_EQUALS, CNT_LABELLED, CNT_SILENT, CNT_ABOVE)
DIAG_TOTALS = ("excluded_smoke_context", "excluded_not_a_chain_count",
               "excluded_a_streak_counter", "excluded_numerator_above_denominator",
               "pair_and_vocabulary_far_not_counted")
UNJUDGED = (CNT_NO_RECEIPT, CNT_NO_TABLE, CNT_NO_ROUND)

V_SILENT_EXISTS = ("green_chain_sentences_do_name_the_table_of_their_round_but_a_few_print_a_"
                   "subset_as_the_whole_chain")
V_LABELLED_ONLY = ("every_judgeable_green_chain_sentence_below_its_table_says_so_and_none_reads_"
                   "as_the_whole_chain")
V_ALL_NAME_TABLE = "every_judgeable_green_chain_sentence_names_the_whole_table_of_its_round"
V_BLIND = "the_claim_population_could_not_be_judged_so_nothing_is_concluded"


# ---- physics: pure functions (fixtures drive the selftest) -----------------------
def derive_class(round_no, receipt, table, numerator, denominator, subset_label):
    """The class of a claim, re-derivable from what the face stores."""
    if round_no is None:
        return CNT_NO_ROUND
    if receipt is None:
        return CNT_NO_RECEIPT
    if table is None:
        return CNT_NO_TABLE
    if denominator == table:
        return CNT_EQUALS
    if denominator < table:
        return CNT_LABELLED if subset_label else CNT_SILENT
    return CNT_ABOVE


def extract_round(head):
    for pat in ROUND_PATTERNS:
        m = pat.search(head)
        if m:
            return int(m.group(1))
    return None


def extract_claims(text, machine):
    """Every adjacent chain-count claim in a report body, plus the parse diagnostics."""
    claims = []
    diag = {"claims": 0, "excluded_smoke_context": 0, "excluded_not_a_chain_count": 0,
            "excluded_a_streak_counter": 0, "excluded_numerator_above_denominator": 0,
            "pair_and_vocabulary_far_not_counted": 0}
    for lineno, line in enumerate(text.splitlines(), 1):
        seen = set()
        anchored = False
        for pat in PATTERNS:
            for m in pat.finditer(line):
                anchored = True
                lo = max(0, m.start() - SMOKE_WINDOW)
                hi = min(len(line), m.end() + SMOKE_WINDOW)
                ctx = line[lo:hi]
                if "smoke" in ctx.lower():
                    diag["excluded_smoke_context"] += 1
                    continue
                tail = line[m.end():m.end() + 18]
                if REJECT.search(tail):
                    diag["excluded_not_a_chain_count"] += 1
                    continue
                inner = PAIR.search(m.group(0))
                num_pos = m.start() + (inner.start() if inner else 0)
                prefix = line[max(0, num_pos - 24):num_pos]
                if REJECT_PRE.search(prefix):
                    diag["excluded_a_streak_counter"] += 1
                    continue
                pair = (int(m.group(1)), int(m.group(2)))
                if pair[0] > pair[1]:      # a leg count cannot have more legs than it has
                    diag["excluded_numerator_above_denominator"] += 1
                    continue
                if pair in seen:
                    continue
                seen.add(pair)
                lw = max(0, m.start() - LABEL_WINDOW)
                rw = min(len(line), m.end() + LABEL_WINDOW)
                window = line[lw:rw]
                claims.append({
                    "report": None,
                    "line": lineno,
                    "machine": machine,
                    "round": extract_round(line[:ROUND_HEAD]),
                    "numerator": pair[0],
                    "denominator": pair[1],
                    "subset_label": bool(SUBSET_LABEL.search(window)),
                    "sentence": line[max(0, m.start() - 60):m.end() + 40].strip()[:240],
                })
        if PAIR.search(line) and VOCAB.search(line) and not anchored:
            diag["pair_and_vocabulary_far_not_counted"] += 1
    diag["claims"] = len(claims)
    return claims, diag


def _verdict(summary):
    s = summary
    if s.get(CNT_SILENT):
        v = V_SILENT_EXISTS
    elif s.get(CNT_LABELLED):
        v = V_LABELLED_ONLY
    elif sum(s.get(c, 0) for c in JUDGED):
        v = V_ALL_NAME_TABLE
    else:
        v = V_BLIND
    line = ("%d of %d claims are judgeable: %d name the whole table, %d are below it and say so, "
            "%d are below it and read as the whole chain, %d are above it; %d cannot be judged "
            "(%d no receipt, %d no table, %d no round); of the %d below the table, %d state their "
            "own receipt's row count and %d understate even that"
            % (sum(s.get(c, 0) for c in JUDGED), s.get("claims_total", 0),
               s.get(CNT_EQUALS, 0), s.get(CNT_LABELLED, 0), s.get(CNT_SILENT, 0),
               s.get(CNT_ABOVE, 0), sum(s.get(c, 0) for c in UNJUDGED),
               s.get(CNT_NO_RECEIPT, 0), s.get(CNT_NO_TABLE, 0), s.get(CNT_NO_ROUND, 0),
               s.get("below_the_table", 0),
               s.get("below_the_table_whose_denominator_matches_their_receipt", 0),
               s.get("below_the_table_whose_denominator_is_below_their_own_receipt", 0)))
    return v, line


# ---- build ----------------------------------------------------------------------
def _read_report(relpath):
    path = os.path.join(ROOT, relpath)
    raw = open(path, "rb").read()
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace"), "gbk (lossy: undecodable bytes replaced)"


def _receipt_index():
    with io.open(E561_FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    idx = {}
    for r in face.get("rows") or []:
        rnd, mach = r.get("name_round"), r.get("machine")
        if not isinstance(rnd, int) or not mach:
            continue
        cur = idx.get((rnd, mach))
        # several receipts can share a round; prefer the one that carries a table
        if cur is None or (cur.get("table_at_its_round") is None
                           and r.get("table_at_its_round") is not None):
            idx[(rnd, mach)] = r
    blob = open(E561_FACE, "rb").read()
    return idx, hashlib.sha256(blob).hexdigest()[:16], face


def build(write=False):
    idx, face_sha16, _face = _receipt_index()
    claims = []
    sources = []
    for relpath, machine in REPORTS:
        text, enc = _read_report(relpath)
        found, diag = extract_claims(text, machine)
        for c in found:
            c["report"] = relpath
            row = idx.get((c["round"], machine)) if c["round"] is not None else None
            c["receipt"] = row.get("file") if row else None
            c["receipt_rows"] = row.get("rows") if row else None
            c["receipt_class"] = row.get("class") if row else None
            c["receipt_nonzero_rows"] = row.get("nonzero_rows") if row else None
            c["table_at_its_round"] = (row.get("table_at_its_round") if row else None)
            rows, nz = c["receipt_rows"], c["receipt_nonzero_rows"]
            c["receipt_rc0_rows"] = (rows - nz) if isinstance(rows, int) and isinstance(nz, int) \
                else None
            c["denominator_equals_receipt_rows"] = (
                c["denominator"] == rows if isinstance(rows, int) else None)
            c["numerator_equals_receipt_rc0_rows"] = (
                c["numerator"] == c["receipt_rc0_rows"]
                if c["receipt_rc0_rows"] is not None else None)
            c["class"] = derive_class(c["round"], c["receipt"], c["table_at_its_round"],
                                      c["numerator"], c["denominator"], c["subset_label"])
            claims.append(c)
        sources.append({
            "file": relpath,
            "machine": machine,
            "encoding": enc,
            "lines": len(text.splitlines()),
            "claims": diag["claims"],
            "excluded_smoke_context": diag["excluded_smoke_context"],
            "excluded_not_a_chain_count": diag["excluded_not_a_chain_count"],
            "excluded_a_streak_counter": diag["excluded_a_streak_counter"],
            "excluded_numerator_above_denominator":
                diag["excluded_numerator_above_denominator"],
            "pair_and_vocabulary_far_not_counted": diag["pair_and_vocabulary_far_not_counted"],
        })

    summary = {"claims_total": len(claims)}
    for cls in CLAIM_CLASSES:
        summary[cls] = sum(1 for c in claims if c["class"] == cls)
    summary["judgeable"] = sum(summary[c] for c in JUDGED)
    below = [c for c in claims if c["class"] in (CNT_LABELLED, CNT_SILENT)]
    summary["below_the_table"] = len(below)
    summary["below_the_table_whose_denominator_matches_their_receipt"] = sum(
        1 for c in below if c["denominator_equals_receipt_rows"] is True)
    summary["below_the_table_whose_denominator_is_below_their_own_receipt"] = sum(
        1 for c in below if c["denominator_equals_receipt_rows"] is False)
    summary["below_the_table_whose_numerator_is_below_the_receipt_rc0_rows"] = sum(
        1 for c in below if c["numerator_equals_receipt_rc0_rows"] is False)
    summary["unjudgeable"] = sum(summary[c] for c in UNJUDGED)
    summary["sources"] = len(sources)
    summary["rounds_distinct"] = len({c["round"] for c in claims if c["round"] is not None})
    summary["machines_distinct"] = len({c["machine"] for c in claims})
    summary["claims_on_the_legacy_bm_b_file"] = sum(1 for c in claims if c["machine"] == "b")
    for key in DIAG_TOTALS:
        summary[key] = sum(s[key] for s in sources)
    summary["sources_with_claims"] = sum(1 for s in sources if s["claims"])
    summary["sentences_stating_a_round"] = sum(1 for c in claims if c["round"] is not None)

    verdict, verdict_line = _verdict(summary)

    keys = sorted("%s|%s|%s|%d|%d|%s" % (c["report"], c["machine"], c["round"],
                                         c["numerator"], c["denominator"], c["class"])
                  for c in claims)
    pin = hashlib.sha256("\n".join(keys).encode("utf-8")).hexdigest()

    face = {
        "study": "E567",
        "card": "E567",
        "round": "r1595",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "note": ("the round reports are append-only, so a claim's line moves only when text is "
                 "inserted above it; the gate therefore re-derives the claim key multiset "
                 "(report, machine, round, numerator, denominator, class) and not line numbers"),
        "parse_rule": {
            "s6_anchored": A_SIX,
            "chain_anchored": B_CHAIN,
            "pair_followed_by_legs_or_rc0": C_TAIL,
            "smoke_exclusion_window_chars": SMOKE_WINDOW,
            "non_chain_tail_rejected": REJECT_TAIL,
            "streak_prefix_rejected": REJECT_PREFIX,
            "numerator_above_denominator_rejected": True,
            "round_prefix_chars": ROUND_HEAD,
            "subset_label_window_chars": LABEL_WINDOW,
            "round_patterns": [p.pattern for p in ROUND_PATTERNS],
            "subset_label": SUBSET_LABEL.pattern,
            "reports": [{"file": f, "machine": m} for f, m in REPORTS],
            "join": ("claim (round, machine) -> E561 receipt row -> table_at_its_round; a round "
                     "with no receipt row on disk is published as unjudged, never as a match"),
        },
        "control_arms": _control_arms(),
        "sources": sources,
        "claims": claims,
        "summary": summary,
        "population_source": {
            "sha16": pin[:16],
            "share_of_the_full_sha": pin,
            "receipt_face": os.path.relpath(E561_FACE, ROOT).replace(os.sep, "/"),
            "receipt_face_sha16": face_sha16,
            "parts": len(keys),
        },
        "verdict": verdict,
        "verdict_line": verdict_line,
    }
    if write:
        _write(DATED, face)
        _write(LATEST, face)
    return face


# ---- control arms (fixtures: pure functions, no disk) ----------------------------
FIX_SIX = "| 2026-09-26 21:40 | R298 | S6 30/30 legs rc=0 (audit CLEAN)"
FIX_CHAIN = "| 2026-11-08 23:2x | 1204 | S6 chain 39/39 rc0 in 363.2s"
FIX_TAIL = "| 2026-11-08 23:2x | 1246 | S6 25/25 rc=0 (machine_health 8/8)"
FIX_SMOKE = "| 2026-11-08 22:00 | 1200 | S1 smoke 426/428 PASS, S6 30/30 rc0 covered above"
FIX_ORPHAN = "| 2026-11-08 23:00 | 1299 | S6: orphan 0/7 py faces | dualrun ZERO-DRIFT"
FIX_LABEL = "| 2026-11-08 22:00 | 1285 | S6 star/band leg family 7/7 rc=0 via --only"
FIX_STREAK = "| 2026-09-30 06:31 | r448 | S6: pool_dualrun ZERO-DRIFT streak 39/40 all green"
FIX_FRACTION = "| 2026-09-29 15:55 | r431 | S6 chain fine; AMP 73/55 homes were empty"
FIX_FAR = ("| 2026-11-08 22:00 | 1300 | S6 ran mostly clean this window, with every leg "
           "green and quiet, and 412/428 rows were read")

DIAG_KEYS = ("claims", "excluded_smoke_context", "excluded_not_a_chain_count",
             "excluded_a_streak_counter", "excluded_numerator_above_denominator",
             "pair_and_vocabulary_far_not_counted")


def _arms(claims, machine="b"):
    out = {}
    for name, src in (("six_anchored_pair_is_a_claim", FIX_SIX),
                      ("chain_anchored_pair_is_a_claim", FIX_CHAIN),
                      ("pair_before_rc0_is_a_claim", FIX_TAIL),
                      ("a_smoke_suite_pair_is_excluded", FIX_SMOKE),
                      ("an_orphan_face_pair_is_not_a_chain_count", FIX_ORPHAN),
                      ("a_streak_counter_is_not_a_chain_count", FIX_STREAK),
                      ("a_fraction_above_one_is_not_a_leg_count", FIX_FRACTION),
                      ("a_pair_far_from_a_chain_word_is_counted_not_claimed", FIX_FAR)):
        found, diag = extract_claims(src, machine)
        out[name] = {"claims": [[c["numerator"], c["denominator"]] for c in found],
                     "diag": {k: diag[k] for k in DIAG_KEYS}}
    found, _ = extract_claims(FIX_SIX, machine)
    out["the_row_round_is_recovered"] = found[0]["round"] if found else None
    lab, _ = extract_claims(FIX_LABEL, machine)
    out["a_subset_label_is_seen"] = lab[0]["subset_label"] if lab else None
    out["a_silent_subset_over_a_58_leg_table"] = derive_class(1204, "x.json", 58, 39, 39, False)
    out["a_labelled_subset_over_a_65_leg_table"] = derive_class(1285, "x.json", 65, 7, 7, True)
    out["an_equal_claim_over_a_30_leg_table"] = derive_class(298, "x.json", 30, 30, 30, False)
    out["an_above_claim_over_a_30_leg_table"] = derive_class(298, "x.json", 30, 40, 40, False)
    out["a_round_without_a_receipt"] = derive_class(298, None, None, 30, 30, False)
    out["a_receipt_without_a_table"] = derive_class(298, "x.json", None, 30, 30, False)
    out["a_row_without_a_round"] = derive_class(None, None, None, 30, 30, False)
    return out


def _control_arms():
    return _arms([])


def _diag(claims, **over):
    d = {k: 0 for k in DIAG_KEYS}
    d["claims"] = len(claims)
    d.update(over)
    return d


def _check_arms():
    arms = _control_arms()
    want = {
        "six_anchored_pair_is_a_claim": {"claims": [[30, 30]], "diag": _diag([[30, 30]])},
        "chain_anchored_pair_is_a_claim": {"claims": [[39, 39]], "diag": _diag([[39, 39]])},
        "pair_before_rc0_is_a_claim": {"claims": [[25, 25]], "diag": _diag([[25, 25]])},
        # both the S6 anchor and the pair+rc0 anchor see the smoke word, and neither is a claim
        "a_smoke_suite_pair_is_excluded": {"claims": [],
                                           "diag": _diag([], excluded_smoke_context=2)},
        "an_orphan_face_pair_is_not_a_chain_count": {
            "claims": [], "diag": _diag([], excluded_not_a_chain_count=1)},
        "a_streak_counter_is_not_a_chain_count": {
            "claims": [], "diag": _diag([], excluded_a_streak_counter=1)},
        "a_fraction_above_one_is_not_a_leg_count": {
            "claims": [], "diag": _diag([], excluded_numerator_above_denominator=2)},
        "a_pair_far_from_a_chain_word_is_counted_not_claimed": {
            "claims": [], "diag": _diag([], pair_and_vocabulary_far_not_counted=1)},
        "the_row_round_is_recovered": 298,
        "a_subset_label_is_seen": True,
        "a_silent_subset_over_a_58_leg_table": CNT_SILENT,
        "a_labelled_subset_over_a_65_leg_table": CNT_LABELLED,
        "an_equal_claim_over_a_30_leg_table": CNT_EQUALS,
        "an_above_claim_over_a_30_leg_table": CNT_ABOVE,
        "a_round_without_a_receipt": CNT_NO_RECEIPT,
        "a_receipt_without_a_table": CNT_NO_TABLE,
        "a_row_without_a_round": CNT_NO_ROUND,
    }
    return ["%s -> %r (want %r)" % (k, arms.get(k), v) for k, v in want.items()
            if arms.get(k) != v]


# ---- persistence -----------------------------------------------------------------
def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


# ---- face validation -------------------------------------------------------------
def face_problems(face):
    problems = []
    claims = face.get("claims") or []
    s = face.get("summary") or {}
    if s.get("claims_total") != len(claims):
        problems.append("summary.claims_total %r != %d rows" % (s.get("claims_total"), len(claims)))
    for cls in CLAIM_CLASSES:
        got = sum(1 for c in claims if c.get("class") == cls)
        if s.get(cls) != got:
            problems.append("summary.%s %r != %d in claims" % (cls, s.get(cls), got))
    if sum(s.get(c, 0) for c in CLAIM_CLASSES) != len(claims):
        problems.append("a claim is in no class or in two")
    if s.get("judgeable") != sum(s.get(c, 0) for c in JUDGED):
        problems.append("summary.judgeable does not re-derive")
    if s.get("unjudgeable") != sum(s.get(c, 0) for c in UNJUDGED):
        problems.append("summary.unjudgeable does not re-derive")
    sources = face.get("sources") or []
    if s.get("sources") != len(sources):
        problems.append("summary.sources %r != %d sources" % (s.get("sources"), len(sources)))
    if s.get("sources_with_claims") != sum(1 for x in sources if x.get("claims")):
        problems.append("summary.sources_with_claims does not re-derive")
    if sum(x.get("claims", 0) for x in sources) != len(claims):
        problems.append("the per-source claim counts do not sum to the claim list")
    for key in DIAG_TOTALS:
        if s.get(key) != sum(x.get(key, 0) for x in sources):
            problems.append("summary.%s does not sum over the sources" % key)
    if s.get("sentences_stating_a_round") != sum(1 for c in claims if c.get("round") is not None):
        problems.append("summary.sentences_stating_a_round does not re-derive")
    if s.get("machines_distinct") != len({c.get("machine") for c in claims}):
        problems.append("summary.machines_distinct does not re-derive")
    below = [c for c in claims if c.get("class") in (CNT_LABELLED, CNT_SILENT)]
    if s.get("below_the_table") != len(below):
        problems.append("summary.below_the_table does not re-derive")
    for key, want in (
            ("below_the_table_whose_denominator_matches_their_receipt",
             sum(1 for c in below if c.get("denominator_equals_receipt_rows") is True)),
            ("below_the_table_whose_denominator_is_below_their_own_receipt",
             sum(1 for c in below if c.get("denominator_equals_receipt_rows") is False)),
            ("below_the_table_whose_numerator_is_below_the_receipt_rc0_rows",
             sum(1 for c in below if c.get("numerator_equals_receipt_rc0_rows") is False))):
        if s.get(key) != want:
            problems.append("summary.%s %r != %d" % (key, s.get(key), want))

    for c in claims:
        for key in ("report", "machine", "numerator", "denominator", "subset_label",
                    "class", "sentence"):
            if key not in c:
                problems.append("a claim is missing %s" % key)
        if not isinstance(c.get("line"), int) or c["line"] < 1:
            problems.append("%s: a claim carries no line" % c.get("report"))
        if not isinstance(c.get("numerator"), int) or not isinstance(c.get("denominator"), int):
            problems.append("%s:%r: a claim carries no numeric pair" % (c.get("report"),
                                                                       c.get("line")))
            continue
        if c["denominator"] < c["numerator"]:
            problems.append("%s:%r: the numerator exceeds the denominator"
                            % (c.get("report"), c.get("line")))
        want = derive_class(c.get("round"), c.get("receipt"), c.get("table_at_its_round"),
                            c["numerator"], c["denominator"], c.get("subset_label"))
        if c.get("class") != want:
            problems.append("%s:%r: class %r != re-derived %r"
                            % (c.get("report"), c.get("line"), c.get("class"), want))
        if c.get("class") == CNT_NO_ROUND and c.get("round") is not None:
            problems.append("%s:%r: a no-round claim carries a round" % (c.get("report"),
                                                                        c.get("line")))
        if c.get("class") in (CNT_EQUALS, CNT_LABELLED, CNT_SILENT, CNT_ABOVE):
            if c.get("receipt") is None or c.get("table_at_its_round") is None:
                problems.append("%s:%r: a judged claim carries no receipt/table"
                                % (c.get("report"), c.get("line")))
            rows = c.get("receipt_rows")
            if isinstance(rows, int):
                if c.get("denominator_equals_receipt_rows") != (c["denominator"] == rows):
                    problems.append("%s:%r: the receipt-rows flag does not re-derive"
                                    % (c.get("report"), c.get("line")))
                nz = c.get("receipt_nonzero_rows")
                if isinstance(nz, int):
                    if c.get("receipt_rc0_rows") != rows - nz:
                        problems.append("%s:%r: the receipt rc0 count does not re-derive"
                                        % (c.get("report"), c.get("line")))
                    if c.get("numerator_equals_receipt_rc0_rows") != (c["numerator"] == rows - nz):
                        problems.append("%s:%r: the rc0 flag does not re-derive"
                                        % (c.get("report"), c.get("line")))
        if c.get("subset_label") and c.get("class") == CNT_SILENT:
            problems.append("%s:%r: a labelled subset was classed silent"
                            % (c.get("report"), c.get("line")))

    exp_verdict, exp_line = _verdict(s)
    if face.get("verdict") != exp_verdict:
        problems.append("verdict %r != re-derived %r" % (face.get("verdict"), exp_verdict))
    if face.get("verdict_line") != exp_line:
        problems.append("verdict_line does not re-derive")
    if face.get("control_arms") != _control_arms():
        problems.append("control arms do not re-derive")
    if not (face.get("population_source") or {}).get("sha16"):
        problems.append("the population is not pinned to a vintage")
    if (face.get("parse_rule") or {}).get("s6_anchored") != A_SIX:
        problems.append("the echoed parse rule is not the rule this module runs")
    return problems


def selftest():
    bad = list(_check_arms())
    face = build(write=False)
    bad.extend(face_problems(face))
    doc = json.loads(json.dumps(face))
    for c in doc.get("claims") or []:
        if c.get("class") == CNT_SILENT:
            c["class"] = CNT_EQUALS
            break
    if not face_problems(doc):
        bad.append("a silent subset relabelled as the whole table was accepted")
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    if not face_problems(doc):
        bad.append("a hand-written verdict was accepted")
    doc = json.loads(json.dumps(face))
    doc["summary"]["claims_total"] = doc["summary"]["claims_total"] + 1
    if not face_problems(doc):
        bad.append("an inflated claim count was accepted")
    doc = json.loads(json.dumps(face))
    for c in doc.get("claims") or []:
        if c.get("class") == CNT_NO_RECEIPT:
            c["table_at_its_round"] = c["denominator"]
            c["receipt"] = "results/_r0bmx_s6_chain.json"
            c["class"] = CNT_EQUALS
            break
    if not face_problems(doc):
        bad.append("an unjudged claim was accepted as judged")
    doc = json.loads(json.dumps(face))
    if doc.get("claims"):
        doc["claims"][0]["numerator"] = doc["claims"][0]["denominator"] + 5
        if not face_problems(doc):
            bad.append("a numerator above its denominator was accepted")
    doc = json.loads(json.dumps(face))
    doc["population_source"]["sha16"] = ""
    if not face_problems(doc):
        bad.append("an unpinned population was accepted")
    if bad:
        print("SELFTEST FAIL %d problems" % len(bad))
        for x in bad[:8]:
            print("  -", x[:220])
        return 1
    s = face["summary"]
    print("SELFTEST PASS: %d arms + %d claims (equals=%d labelled=%d silent=%d above=%d | "
          "no_receipt=%d no_table=%d no_round=%d)"
          % (len(_control_arms()), len(face["claims"]), s[CNT_EQUALS], s[CNT_LABELLED],
             s[CNT_SILENT], s[CNT_ABOVE], s[CNT_NO_RECEIPT], s[CNT_NO_TABLE], s[CNT_NO_ROUND]))
    return 0


def _key(c):
    rnd = c.get("round")
    return (c.get("report") or "", c.get("machine") or "", -1 if rnd is None else int(rnd),
            c.get("numerator"), c.get("denominator"), c.get("class"))


def check():
    """Re-derive from the live reports and compare with the published face.

    Line numbers are published as evidence but are not gated: a sentence inserted above a
    claim moves every number below it.  What is gated is the claim-key multiset and every
    summary counter.
    """
    fresh = build(write=False)
    try:
        with io.open(LATEST, encoding="utf-8") as fh:
            published = json.load(fh)
    except Exception as exc:
        print("CHECK FAIL: the face cannot be read: %s" % exc)
        return 1
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "summary", "card", "parse_rule", "sources"):
        if fresh.get(key) != published.get(key):
            problems.append("live %s disagrees with the published face" % key)
    fresh_keys = sorted(_key(c) for c in fresh.get("claims") or [])
    pub_keys = sorted(_key(c) for c in published.get("claims") or [])
    if fresh_keys != pub_keys:
        only_fresh = [k for k in fresh_keys if k not in pub_keys][:3]
        only_pub = [k for k in pub_keys if k not in fresh_keys][:3]
        problems.append("the claim multiset moved (live-only=%r published-only=%r)"
                        % (only_fresh, only_pub))
    if problems:
        print("CHECK FAIL: %d problems; first=%s" % (len(problems), str(problems[0])[:300]))
        return 1
    print("CHECK PASS: %d claims re-derive over %d sources, verdict=%s"
          % (len(pub_keys), len(published.get("sources") or []), published.get("verdict")))
    return 0


def verify():
    problems = face_problems(build(write=False))
    print(json.dumps({"problems": problems[:10], "n": len(problems)}, ensure_ascii=False))
    return 0 if not problems else 1


def main(argv=None):
    action = (list(sys.argv[1:] if argv is None else argv) or ["build"])[0]
    if action == "build":
        face = build(write=True)
        s = face["summary"]
        print("BUILT %s: %d claims over %d sources | equals=%d labelled=%d silent=%d above=%d | "
              "unjudged: no_receipt=%d no_table=%d no_round=%d"
              % (os.path.relpath(LATEST, ROOT), s["claims_total"], s["sources"],
                 s[CNT_EQUALS], s[CNT_LABELLED], s[CNT_SILENT], s[CNT_ABOVE],
                 s[CNT_NO_RECEIPT], s[CNT_NO_TABLE], s[CNT_NO_ROUND]))
        print("EXCLUDED: smoke_context=%d not_a_chain_count=%d far_from_a_chain_word=%d"
              % (s["excluded_smoke_context"], s["excluded_not_a_chain_count"],
                 s["pair_and_vocabulary_far_not_counted"]))
        print("VERDICT: %s" % face["verdict"])
        print("LINE: %s" % face["verdict_line"])
        return 0
    if action == "check":
        return check()
    if action == "verify":
        return verify()
    if action == "selftest":
        return selftest()
    print("usage: e567_chain_claim.py build|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())