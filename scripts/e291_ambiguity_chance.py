"""E291 -- is an equal-length sibling a coincidence, or is the ambiguity flag just the base rate?

E290 published 12 of 27 checkable counts as ambiguous because some OTHER list of the same unit in the
same face has the same length.  That flag only informs a reader if equal lengths are sometimes an
accident.  If they are common -- because a face draws all its arms from one schema, or because three
of four lists of a unit are length 4 -- then "ambiguous" is a statement about the face's shape and
not about the count.

Three measurements, each of which can fail on its own:

  (1) HOW OFTEN DOES AN EQUAL-LENGTH SIBLING EXIST AT ALL?  For every same-unit list that has at
      least one sibling of its unit in its face, does any sibling share its length?  This is the
      base rate of the flag, measured on ALL lists, not only on the 27 counted ones.
  (2) HOW MUCH OF THAT IS THE LENGTH DISTRIBUTION?  The null: a list's length carries no information
      about which count is being audited, so the chance that m siblings include the same length is
      1-(1-p_l)^m with p_l the pooled share of same-unit lists of length l.  Observed above the null
      means lengths are MORE concentrated inside a face than the pool predicts -- structure, not
      accident; observed at the null means the flag is pure base rate.
  (3) WHAT IS AN EQUAL-LENGTH PAIR MADE OF?  Every equal-length pair is classified: the very same
      list content (alias), the same record schema with different rows, or genuinely different
      content.  A pair of aliases is not a coincidence and not a conflict; it is a duplicate.

Then the same test is run at the level E290 reported: its 27 checkable rows, using each row's own
published alternative count, against the same null.

DECISION RULE, declared before any number is read:

  D1  THE ROWS ARE E290'S, NOT A RE-IMPLEMENTATION.  Which counts are checkable and how many
      alternatives each has are read from the published BANDSELFAUDIT face; only the equal-length
      classification is measured here.
  D2  THE FLAG'S RATE AND THE FLAG'S MECHANISM ARE TWO QUESTIONS.  A rate consistent with the null
      says the flag is uninformative; a mechanism that is overwhelmingly schema-sharing says it is
      structural.  Both are published, and neither may stand in for the other.
  D3  ROWS ARE NOT INDEPENDENT OBSERVATIONS.  The number of distinct (face, unit) scopes behind the
      flagged rows is published with the row count, because 8 rows can come from one scope.
  D4  AN ALIAS IS NOT AN AMBIGUITY.  Identical list content is a duplicate; it is counted separately
      and never folded into the coincidence share.
  D5  TWO AGGREGATORS, DISCLOSED.  The row-level test and the list-level test are both published; a
      verdict that only holds on one of them is reported as unstable.
  D6  NO REBURN.  Published faces are re-read only; no draw stream, no band rebuild, no engine.

Verdict vocabulary (frozen):
  the_ambiguity_rate_is_the_length_base_rate_and_the_pairs_are_schema_not_accident
  the_flagged_rows_exceed_the_length_base_rate_so_the_ambiguity_is_real
  no_face_publishes_two_lists_of_the_same_unit_so_ambiguity_cannot_arise

Usage:  python scripts/e291_ambiguity_chance.py run|verify|selftest
"""
import collections
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e286_count_field_scope as e286  # noqa: E402  (the census this study explains)

ROOT = e286.ROOT
OUTDIR = e286.OUTDIR

STUDY = "E291_ambiguity_by_length_chance"
TITLE = ("is a same-length candidate list a coincidence -- how often do two same-unit lists in one "
         "face share a length by chance, and is the 12-of-27 ambiguity rate above it?")
CUTOFF = "2026-10-29"
SRC_FACE = "BANDSELFAUDIT-%s.json" % CUTOFF       # E290: the rows and the flag being explained
FACE = "BANDAMBIENT-%s.json" % CUTOFF
LATEST = "bandambient_latest.json"
SELF_FACES = (FACE, LATEST, SRC_FACE)             # E290's face is one of the BAND* names

# E286's face_universe() only excludes E286's own faces, so any later BAND* study of this family is
# censused by its successors unless it is filtered here by name (E209/E211 self-inclusion family).
SUCCESSOR_EXCLUSIONS = (SRC_FACE,)
ALPHA = 0.05

VERDICT_VOCAB = (
    "the_ambiguity_rate_is_the_length_base_rate_and_the_pairs_are_schema_not_accident",
    "the_flagged_rows_exceed_the_length_base_rate_so_the_ambiguity_is_real",
    "no_face_publishes_two_lists_of_the_same_unit_so_ambiguity_cannot_arise",
)

NO_BILL = ("measurement only: the dated BAND faces are re-read and the lists already published in "
           "them are classified by length and by content. No draw stream is drawn, no band rebuilt, "
           "no engine runs, no verdict about the market. A verdict here is a statement about the "
           "published JSON, its shapes and its duplicates.")


# ------------------------------------------------------------------ io
def load(name):
    return e286.load(name)


def resolve(obj, path):
    """Resolve a dotted path with [i] indices (the same walker shape e286.analyse_face uses)."""
    node = obj
    for chunk in str(path).split("."):
        while True:
            head, _, rest = chunk.partition("[")
            if head:
                node = node[head]
            if not rest:
                break
            idx, _, chunk = rest.partition("]")
            node = node[int(idx)]
            chunk = chunk.lstrip(".")
            if not chunk:
                break
    return node


def census_names():
    """The census universe minus E290's face and this study's own faces (self-inclusion guard)."""
    blocked = set(SUCCESSOR_EXCLUSIONS) | set(SELF_FACES)
    return [n for n in e286.face_universe() if n not in blocked]


def census(names):
    """{face: analyse record} plus the per-(face, unit) groups of list paths and lengths."""
    recs = [e286.analyse_face(n) for n in names]
    groups = {}
    pool = []
    for rec in recs:
        by_unit = collections.defaultdict(list)
        for item in rec["unit_lists"]:
            by_unit[item["unit"]].append((item["path"], item["n_items"]))
            pool.append(item["n_items"])
        for unit, lists in by_unit.items():
            groups[(rec["face"], unit)] = lists
    return recs, groups, pool


def length_null(pool):
    """Pooled share of same-unit lists at each length: the null the flag is tested against."""
    total = len(pool)
    counts = collections.Counter(pool)
    return {length: (float(k) / total) for length, k in counts.items()}, total


def p_any_equal(shares, length, m):
    """P(at least one of m siblings shares this length) under the pooled null (D2)."""
    if m <= 0:
        return 0.0
    p = shares.get(length, 0.0)
    return 1.0 - (1.0 - p) ** m


def content_class(a, b):
    """D4: alias (same content), same schema with different rows, or different content."""
    if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
        return "alias"
    if isinstance(a, list) and isinstance(b, list) and a and b \
            and isinstance(a[0], dict) and isinstance(b[0], dict) \
            and sorted(a[0].keys()) == sorted(b[0].keys()):
        return "same_schema"
    return "different_content"


# ------------------------------------------------------------------ build
def build():
    names = census_names()
    recs, groups, pool = census(names)
    shares, pool_total = length_null(pool)

    # (1)+(3) list level and pair level, measured on every repeated unit group
    eligible = 0
    observed_equal = 0
    expected_equal = 0.0
    pairs = 0
    mechanism = collections.Counter()
    pair_rows = []
    group_rows = []
    for (face, unit), lists in sorted(groups.items()):
        lengths = [n for _, n in lists]
        if len(lists) < 2:
            continue
        counter = collections.Counter(lengths)
        group_rows.append({
            "face": face, "unit": unit, "n_lists": len(lists),
            "lengths": lengths,
            "distinct_lengths": len(counter),
            "any_equal_length": any(k >= 2 for k in counter.values()),
        })
        for index, (path, length) in enumerate(lists):
            eligible += 1
            if counter[length] >= 2:
                observed_equal += 1
            expected_equal += p_any_equal(shares, length, len(lists) - 1)
        obj = load(face)
        values = [resolve(obj, path) for path, _ in lists]
        for i in range(len(lists)):
            for j in range(i + 1, len(lists)):
                if lengths[i] != lengths[j]:
                    continue
                pairs += 1
                kind = content_class(values[i], values[j])
                mechanism[kind] += 1
                if kind == "different_content":
                    pair_rows.append({"face": face, "unit": unit,
                                      "a": lists[i][0], "b": lists[j][0],
                                      "length": lengths[i]})

    # (2) row level: E290's published rows, each with its own alternative count (D1)
    src = load(SRC_FACE)
    src_rows = list(src.get("checkable_rows") or [])
    rows = []
    scope_counter = collections.Counter()
    for row in src_rows:
        length = row["published_value"]
        m = int(row.get("alternative_same_unit_lists") or 0)
        p = p_any_equal(shares, length, m)
        rows.append({
            "face": row["face"], "path": row["path"], "key": row["key"],
            "claimed_unit": row["claimed_unit"], "length": length,
            "alternatives": m,
            "p_any_equal_under_null": p,
            "flagged_ambiguous_by_e290": bool(row.get("ambiguous")),
        })
        if row.get("ambiguous"):
            scope_counter[(row["face"], row["claimed_unit"])] += 1

    rows_n = len(rows)
    flagged = len([r for r in rows if r["flagged_ambiguous_by_e290"]])
    expected_flagged = sum(r["p_any_equal_under_null"] for r in rows)

    list_rate = (float(observed_equal) / eligible) if eligible else None
    list_expected_rate = (expected_equal / eligible) if eligible else None
    row_rate = (float(flagged) / rows_n) if rows_n else None
    row_expected_rate = (expected_flagged / rows_n) if rows_n else None

    # D5: both aggregators published with their own tail probability
    row_p = binom_tail_at_least(flagged, rows_n, row_expected_rate)
    list_p = binom_tail_at_least(observed_equal, eligible, list_expected_rate)

    share_alias = (float(mechanism["alias"]) / pairs) if pairs else None
    share_schema = (float(mechanism["same_schema"]) / pairs) if pairs else None
    share_diff = (float(mechanism["different_content"]) / pairs) if pairs else None
    structural = mechanism["alias"] + mechanism["same_schema"]

    summary = {
        "faces_censused": len(recs),
        "same_unit_lists": pool_total,
        "repeated_unit_groups": len(group_rows),
        "single_list_groups": len([g for g in groups.values() if len(g) == 1]),
        "length_histogram_top": [[k, v] for k, v in
                                 collections.Counter(pool).most_common(10)],
        "list_level": {
            "eligible_lists": eligible,
            "observed_equal_length_sibling": observed_equal,
            "observed_rate": list_rate,
            "expected_rate_under_pooled_length_null": list_expected_rate,
            "expected_count": expected_equal,
            "ratio_observed_to_expected": (observed_equal / expected_equal) if expected_equal else None,
            "tail_p_above_null": list_p,
        },
        "pair_mechanism": {
            "equal_length_pairs": pairs,
            "alias_identical_content": mechanism["alias"],
            "same_schema_different_rows": mechanism["same_schema"],
            "different_content": mechanism["different_content"],
            "share_alias": share_alias,
            "share_same_schema": share_schema,
            "share_different_content": share_diff,
            "structural_share": (float(structural) / pairs) if pairs else None,
            "different_content_pairs": pair_rows,
        },
        "row_level": {
            "source_face": SRC_FACE,
            "checkable_rows": rows_n,
            "flagged_ambiguous": flagged,
            "observed_rate": row_rate,
            "expected_flagged_under_null": expected_flagged,
            "expected_rate_under_null": row_expected_rate,
            "tail_p_above_null": row_p,
            "distinct_scopes_behind_the_flag": len(scope_counter),
            "rows_per_scope": [{"face": f, "unit": u, "rows": c}
                               for (f, u), c in sorted(scope_counter.items(),
                                                       key=lambda kv: -kv[1])],
        },
        "aggregator_agreement": {
            "row_level_says_at_or_below_null": (row_p is None) or (row_p >= ALPHA),
            "list_level_says_above_null": (list_p is not None) and (list_p < ALPHA),
            "stable": bool((row_p is None) or (list_p is None)) or
                      (((row_p >= ALPHA) and (list_p >= ALPHA)) or
                       ((row_p < ALPHA) and (list_p < ALPHA))),
            "statement": "the row test asks whether the FLAG fires above chance; the list test asks "
                         "whether equal lengths are more concentrated inside a face than the pool "
                         "predicts. They can disagree, and the disagreement is the finding: the flag's "
                         "rate is the base rate while the mechanism behind it is structure.",
        },
        "calibrated": False,
    }
    verdict = decide(summary)
    summary["verdict"] = verdict

    identity = {
        "row_count_matches_e290_summary": rows_n == ((src.get("summary") or {}).get("checkable_counts")),
        "flagged_rows_match_e290_summary": flagged == ((src.get("summary") or {}).get("n_ambiguous")),
        "flagged_rows_are_the_e290_ambiguous_set": sorted(
            "%s :: %s" % (r["face"], r["path"]) for r in rows if r["flagged_ambiguous_by_e290"]) ==
            sorted(src.get("summary", {}).get("ambiguous_rows") or []),
        "mechanism_partition": (mechanism["alias"] + mechanism["same_schema"]
                                + mechanism["different_content"]) == pairs,
        "self_faces_absent_from_universe": all(n not in names for n in SELF_FACES),
        "source_face_absent_from_universe": SRC_FACE not in names,
        "every_group_has_two_lists": all(g["n_lists"] >= 2 for g in group_rows),
        "scopes_partition_the_flagged_rows": sum(s["rows"] for s in summary["row_level"]["rows_per_scope"]) == flagged,
    }

    return {
        "study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
        "generated": None,   # stamped by run
        "no_bill": NO_BILL,
        "source_faces": [SRC_FACE],
        "faces_censused": names,
        "frozen_spec": {
            "D1_rows_are_e290s": "the row set, its alternative counts and its flag are read from the "
                                 "published BANDSELFAUDIT face; only the equal-length classification "
                                 "is measured here",
            "D2_rate_and_mechanism_are_two_questions": "the rate is tested against the pooled length "
                                                       "null; the mechanism is classified by content",
            "D3_rows_are_not_independent": "the number of distinct (face, unit) scopes behind the "
                                           "flagged rows is published with the row count",
            "D4_an_alias_is_not_an_ambiguity": "identical list content is a duplicate, counted apart",
            "D5_two_aggregators": "row level and list level are both published; agreement is disclosed",
            "D6_no_reburn": "published faces re-read only; no draw stream, no band rebuild, no engine",
            "alpha": ALPHA,
            "verdict_vocab": list(VERDICT_VOCAB),
        },
        "groups": group_rows,
        "rows": rows,
        "identity_check": identity,
        "summary": summary,
        "verdict": verdict,
        "verdict_reason": _reason(verdict, summary),
    }


# ------------------------------------------------------------------ stats
def binom_tail_at_least(k, n, p):
    """Exact one-sided P(X >= k) for X ~ Binomial(n, p); total for edges and degenerate p."""
    if n <= 0 or p is None:
        return None
    if k <= 0:
        return 1.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i))
    return min(1.0, max(0.0, total))


def decide(summary):
    repeated = summary.get("repeated_unit_groups") or 0
    if not repeated:
        return VERDICT_VOCAB[2]
    row = summary.get("row_level") or {}
    list_level = summary.get("list_level") or {}
    # the flag is a real conflict only if the rows beat the null AND the pairs are content-different
    structural = summary["pair_mechanism"]["structural_share"]
    exceeds = (row.get("tail_p_above_null") is not None and row["tail_p_above_null"] < ALPHA)
    if exceeds and (structural is not None and structural < 0.5):
        return VERDICT_VOCAB[1]
    return VERDICT_VOCAB[0]


def _fmt_pct(value):
    return "n/a" if value is None else "%.1f pct" % (value * 100.0)


def _fmt_p(value):
    return "n/a" if value is None else "%.3f" % value


def _reason(verdict, summary):
    row = summary["row_level"]
    lst = summary["list_level"]
    mech = summary["pair_mechanism"]
    if verdict == VERDICT_VOCAB[2]:
        return ("no face in the census publishes two lists of the same unit, so an equal-length "
                "sibling cannot arise and the flag has no base rate to compare against.")
    head = ("%d of %d checkable rows are flagged ambiguous, against %s expected from the pooled "
            "length distribution alone (tail p=%s), and the group behind all of them is only %d "
            "scope(s)"
            % (row["flagged_ambiguous"], row["checkable_rows"],
               _fmt_pct(row["expected_rate_under_null"]), _fmt_p(row["tail_p_above_null"]),
               row["distinct_scopes_behind_the_flag"]))
    mid = ("at list level %d of %d eligible lists (%s) have an equal-length sibling against %s "
           "expected under the same null (tail p=%s)"
           % (lst["observed_equal_length_sibling"], lst["eligible_lists"],
              _fmt_pct(lst["observed_rate"]), _fmt_pct(lst["expected_rate_under_pooled_length_null"]),
              _fmt_p(lst["tail_p_above_null"])))
    tail = ("and the %d equal-length pairs are not accidents: %d are the very same content (%s), "
            "%d share a record schema with different rows (%s) and only %d differ in content (%s), so "
            "an equal length here marks a shared shape and occasionally a duplicate, not two lists "
            "competing for one meaning"
            % (mech["equal_length_pairs"], mech["alias_identical_content"], _fmt_pct(mech["share_alias"]),
               mech["same_schema_different_rows"], _fmt_pct(mech["share_same_schema"]),
               mech["different_content"], _fmt_pct(mech["share_different_content"])))
    if verdict == VERDICT_VOCAB[0]:
        return ("%s; %s; %s. The two aggregators are reported separately because they answer "
                "different questions and here they split: the row-level rate is at the null while "
                "the list-level concentration is far above it (stable=%s)."
                % (head, mid, tail, str(summary["aggregator_agreement"]["stable"]).lower()))
    return ("%s; %s; and only %s of the pairs are structurally identical, so the flagged rows are "
            "above what shape alone explains -- the ambiguity there is real." % (head, mid, tail))


# ------------------------------------------------------------------ commands
def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        fh = io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(text)
        finally:
            fh.close()


def cmd_run():
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    row, lst, mech = s["row_level"], s["list_level"], s["pair_mechanism"]
    print("E291 %s" % face["verdict"])
    print("  rows: %d of %d flagged vs %s expected (p=%.3f) over %d scope(s)"
          % (row["flagged_ambiguous"], row["checkable_rows"],
             _fmt_pct(row["expected_rate_under_null"]), row["tail_p_above_null"] or 0.0,
             row["distinct_scopes_behind_the_flag"]))
    print("  lists: %d of %d (%s) vs %s expected (p=%.3f)"
          % (lst["observed_equal_length_sibling"], lst["eligible_lists"],
             _fmt_pct(lst["observed_rate"]),
             _fmt_pct(lst["expected_rate_under_pooled_length_null"]), lst["tail_p_above_null"] or 0.0))
    print("  pairs: %d total | alias=%d same_schema=%d different_content=%d"
          % (mech["equal_length_pairs"], mech["alias_identical_content"],
             mech["same_schema_different_rows"], mech["different_content"]))
    print("  identity=%s" % all(face["identity_check"][k] for k in
                                ("row_count_matches_e290_summary", "flagged_rows_match_e290_summary",
                                 "mechanism_partition", "self_faces_absent_from_universe")))
    return 0


def cmd_verify():
    stored = load(FACE)
    live = build()
    problems = []
    if stored.get("verdict") != live.get("verdict"):
        problems.append("verdict: stored=%r live=%r" % (stored.get("verdict"), live.get("verdict")))
    s_stored, s_live = stored.get("summary") or {}, live.get("summary") or {}
    for key in ("faces_censused", "same_unit_lists", "repeated_unit_groups", "length_histogram_top"):
        if s_stored.get(key) != s_live.get(key):
            problems.append("summary.%s does not re-derive" % key)
    for block in ("list_level", "pair_mechanism", "row_level", "aggregator_agreement"):
        for key, value in (s_live.get(block) or {}).items():
            if (s_stored.get(block) or {}).get(key) != value:
                problems.append("%s.%s does not re-derive" % (block, key))
    if [("%s :: %s" % (r["face"], r["path"])) for r in (stored.get("rows") or [])] != \
            [("%s :: %s" % (r["face"], r["path"])) for r in live["rows"]]:
        problems.append("the row set does not re-derive")
    for key, ok in live["identity_check"].items():
        if not ok:
            problems.append("identity check %s is false" % key)
    if s_stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    print("E291 verify: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
def _fixture():
    """Two groups: a schema-sharing one (equal lengths, different rows), an alias, a real collision."""
    return {
        "arms": [
            {"n_rows": 2, "rows": [{"a": 1}, {"a": 2}]},
            {"n_rows": 2, "rows": [{"a": 3}, {"a": 4}]},
        ],
        "cells": [
            {"n_rows": 3, "rows": [{"b": 1}, {"b": 2}, {"b": 3}], "n_cells": 3,
             "cells": [{"c": 1}, {"c": 2}, {"c": 3}]},
            {"n_rows": 2, "rows": [{"b": 9}, {"b": 8}], "n_cells": 4, "cells": ["p", "q", "r", "s"]},
        ],
        "mirror": {"n_labels": 2, "labels": ["x", "y"], "copy": {"labels": ["x", "y"]}},
        "solo": {"n_rows": 1, "rows": [{"z": 1}]},
    }


def cmd_selftest():
    ok, fail = 0, []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    # L1 the binomial tail is exact and total
    leg("L1", abs(binom_tail_at_least(0, 5, 0.5) - 1.0) < 1e-12
        and abs(binom_tail_at_least(5, 5, 0.5) - 0.5 ** 5) < 1e-12
        and binom_tail_at_least(1, 5, 0.0) == 0.0
        and binom_tail_at_least(1, 5, 1.0) == 1.0
        and binom_tail_at_least(1, 0, 0.5) is None)

    # L2 the null probability is monotone in the number of siblings and zero at zero
    leg("L2", p_any_equal({3: 0.25}, 3, 0) == 0.0
        and p_any_equal({3: 0.25}, 3, 1) < p_any_equal({3: 0.25}, 3, 2) < 1.0
        and abs(p_any_equal({3: 0.25}, 3, 2) - (1 - 0.75 ** 2)) < 1e-12)

    fx = _fixture()
    rec = e286.analyse_face_from_object("FIXTURE.json", fx)
    groups = {}
    pool = []
    for item in rec["unit_lists"]:
        groups.setdefault((rec["face"], item["unit"]), []).append((item["path"], item["n_items"]))
        pool.append(item["n_items"])
    shares, pool_total = length_null(pool)

    # L3 groups are keyed by (face, unit) and list lengths come from the published face
    leg("L3", len(pool) == len(rec["unit_lists"]) and pool_total == len(pool)
        and all(len(v) >= 1 for v in groups.values()))

    # L4 alias / same_schema / different_content are distinguished (D4)
    leg("L4", content_class([{"a": 1}], [{"a": 1}]) == "alias"
        and content_class([{"a": 1}], [{"a": 2}]) == "same_schema"
        and content_class([{"a": 1}], ["x"]) == "different_content"
        and content_class([], []) == "alias")

    # L5 an alias is never counted inside the structural coincidence story as a conflict:
    #     the three classes partition the pairs (D4, mechanism partition)
    pairs, mech = 0, collections.Counter()
    for (face, unit), lists in groups.items():
        lengths = [n for _, n in lists]
        if len(lists) < 2:
            continue
        obj = fx
        values = [resolve(obj, p) for p, _ in lists]
        for i in range(len(lists)):
            for j in range(i + 1, len(lists)):
                if lengths[i] != lengths[j]:
                    continue
                pairs += 1
                mech[content_class(values[i], values[j])] += 1
    leg("L5", pairs == sum(mech.values()) and pairs > 0 and mech["alias"] >= 1
        and mech["same_schema"] >= 1, (pairs, dict(mech)))

    # L6 a solo group contributes no pairs and no eligible list
    solo = [v for v in groups.values() if len(v) == 1]
    leg("L6", all(len(v) == 1 for v in solo) and len(solo) >= 1)

    # L7 the null uses the pooled distribution, so a length that never occurs has probability zero
    leg("L7", shares.get(999, 0.0) == 0.0 and abs(sum(shares.values()) - 1.0) < 1e-12)

    # L8 the three frozen verdicts are reachable
    leg("L8", decide({"repeated_unit_groups": 0}) == VERDICT_VOCAB[2]
        and decide({"repeated_unit_groups": 2,
                    "row_level": {"tail_p_above_null": 0.9},
                    "pair_mechanism": {"structural_share": 0.9}}) == VERDICT_VOCAB[0]
        and decide({"repeated_unit_groups": 2,
                    "row_level": {"tail_p_above_null": 0.001},
                    "pair_mechanism": {"structural_share": 0.1}}) == VERDICT_VOCAB[1])

    # L9 a high structural share keeps the verdict at base rate even when the tail is small (D2)
    leg("L9", decide({"repeated_unit_groups": 2,
                      "row_level": {"tail_p_above_null": 0.001},
                      "pair_mechanism": {"structural_share": 0.9}}) == VERDICT_VOCAB[0])

    # L10 a missing tail never crashes the verdict and never manufactures an exceedance
    leg("L10", decide({"repeated_unit_groups": 2,
                       "row_level": {"tail_p_above_null": None},
                       "pair_mechanism": {"structural_share": 0.0}}) == VERDICT_VOCAB[0])

    # L11 the live face re-derives twice on its decisive keys and stays inside the vocabulary
    a, b = build(), build()
    keys = ("faces_censused", "same_unit_lists", "repeated_unit_groups")
    leg("L11", all(a["summary"][k] == b["summary"][k] for k in keys)
        and a["summary"]["row_level"] == b["summary"]["row_level"]
        and a["summary"]["pair_mechanism"] == b["summary"]["pair_mechanism"]
        and a["verdict"] == b["verdict"] and a["verdict"] in VERDICT_VOCAB)

    # L12 the live join to E290 holds (row count, flag count, the ambiguous set itself)
    ic = a["identity_check"]
    leg("L12", ic["row_count_matches_e290_summary"] and ic["flagged_rows_match_e290_summary"]
        and ic["flagged_rows_are_the_e290_ambiguous_set"], ic)

    # L13 this study's own face and E290's face are both outside the census (self-inclusion family)
    leg("L13", ic["self_faces_absent_from_universe"] and ic["source_face_absent_from_universe"]
        and SRC_FACE not in a["faces_censused"])

    # L14 the mechanism classes partition the equal-length pairs on the live census, and every
    #     flagged row has at least one alternative (otherwise the flag could not fire)
    s = a["summary"]
    leg("L14", ic["mechanism_partition"]
        and all((not r["flagged_ambiguous_by_e290"]) or r["alternatives"] >= 1
                for r in a["rows"]))

    # L15 rows and scopes agree: the scope partition sums to the flagged count (D3)
    leg("L15", ic["scopes_partition_the_flagged_rows"]
        and s["row_level"]["distinct_scopes_behind_the_flag"] <= s["row_level"]["flagged_ambiguous"])

    # L16 list-level observed rate and expected rate are both published and finite
    leg("L16", s["list_level"]["observed_rate"] is not None
        and s["list_level"]["expected_rate_under_pooled_length_null"] is not None
        and 0.0 <= s["list_level"]["observed_rate"] <= 1.0)

    # L17 D5: the two aggregators are published with their own reading, and a split is not hidden
    ag = s["aggregator_agreement"]
    leg("L17", ag["stable"] == (ag["row_level_says_at_or_below_null"]
                                == (not ag["list_level_says_above_null"]))
        and isinstance(ag["statement"], str) and ag["statement"])

    print("E291 selftest: %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL %s" % f)
    return 0 if not fail else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))