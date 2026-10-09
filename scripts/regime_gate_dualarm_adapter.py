"""REGIME_STYLE_MATRIX_V1 sec.1 upstream contract adapter (tech queue T16).

MATRIX sec.1 (frozen contract line): "upstream shape non-compliant -> write
an adapter at wiring time (the contract itself must never be changed)".
This module IS that adapter for the regime_gate_dualarm exit-3 blocked path
(scripts/regime_gate_dualarm.py exits 3 when the latest
results/regime5_labels/*.json violates the frozen sec.1 input contract).

Legal-shell generation = LOSSLESS, spec-sanctioned transformations only:

  A1 sort     labels ascending by date          (fixes the sorted clause)
  A2 dedupe    byte-equal duplicate entries     (fixes the dup-date clause;
              a pick between differing duplicates is judgment -> blocked)
  A3 alias     five-key relabeling ONLY, per the MATRIX sec.1 wu-tai-key
              definition line (BULL=niu-shi, CHOP=zhen-dang, GRIND=yin-die,
              BEAR=xiong-shi, SUPPORT=hu-pan-qi): 1:1 case/alias folding,
              zero criteria invention

Everything else stays BLOCKED (data absent or a judgment pick required):
  B0 internal  adapted shell still fails the frozen validator (fail-closed)
  B1 top-level cutoff/source missing or ill-typed, labels not a list
               (cannot be synthesized without inventing data)
  B2 empty     labels list empty
  B3 shape     entry non-dict / date or state missing or non-str
  B4 enum      state not one of the five keys after A3 folding
  B5 conflict  same-date entries differ beyond byte-equality (pick needed)

Honesty laws (frozen with the T-2026-10-10-180 wiring):
- zero upstream writes: adapted shells land ONLY under
  results/regime_gate_dualarm/adapted/ (namespaced, never consumed by the
  upstream pick); the dualarm artifact carries the full adaptation
  disclosure (original file sha, failed checks, transformation log)
- single-source law (r271): STATES5 + the frozen validator are imported
  from regime_gate_dualarm; this module NEVER re-declares the contract
- deterministic: no clocks, no randomness; identical input -> identical shell

CLI:
  python scripts/regime_gate_dualarm_adapter.py probe     read-only
      classification of every labels file (diagnostics, no writes)
  python scripts/regime_gate_dualarm_adapter.py selftest  offline battery
Exit codes: probe 0 (diagnostics face), selftest 0/1.
"""

import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# single-source law (r271): the five-key set and the frozen sec.1 validator
# live in the dualarm wiring module; the adapter re-declares nothing.
from regime_gate_dualarm import STATES5, validate_contract  # noqa: E402

# MATRIX sec.1 wu-tai-key definition line (frozen) defines each of the five
# keys 1:1 with its Chinese name, so the fold below is spec-sanctioned
# relabeling, not judgment. ASCII source law (r847 kin): CJK literals ride
# as \uXXXX escapes.
#   \u725b\u5e02 = niu shi (bull market)      -> BULL
#   \u9707\u8361 = zhen dang (chop/range)     -> CHOP
#   \u9634\u8dcc = yin die (grind lower)      -> GRIND
#   \u718a\u5e02 = xiong shi (bear market)    -> BEAR
#   \u62a4\u76d8\u671f = hu pan qi (support)  -> SUPPORT
STATE_ALIAS_KEYS = {
    "bull": "BULL",
    "chop": "CHOP",
    "grind": "GRIND",
    "bear": "BEAR",
    "support": "SUPPORT",
    "\u725b\u5e02": "BULL",
    "\u9707\u8361": "CHOP",
    "\u9634\u8dcc": "GRIND",
    "\u718a\u5e02": "BEAR",
    "\u62a4\u76d8\u671f": "SUPPORT",
}


def _entry_bytes(ent):
    """Stable byte view of one entry for exact-equality dedupe (A2)."""
    return json.dumps(ent, sort_keys=True, ensure_ascii=False)


def classify(doc):
    """Clause-mapped violation report via the frozen validator (read-only)."""
    receipt = validate_contract(doc)
    failed = {k: v for k, v in receipt["checks"].items() if v is False}
    return {"pass": receipt["pass"], "failed_checks": failed,
            "contract": receipt["contract"]}


def adapt(doc):
    """Generate a legal shell from a non-compliant labels doc.

    Returns a result dict (never raises):
      ok            True only when an adapted doc passes the frozen validator
      adapted       the legal shell (contract-compliant view), else None
      log           list of lossless ops actually applied
      blocked       list of {clause, detail} reasons when ok is False
      n_labels_in/out, violations (failed frozen checks on the input)
    """
    res = {"ok": False, "adapted": None, "log": [], "blocked": [],
           "n_labels_in": None, "n_labels_out": None, "violations": None}

    def blocked(clause, detail):
        res["blocked"].append({"clause": clause, "detail": detail})
        return res

    res["violations"] = classify(doc)["failed_checks"]

    # B1 top-level: keys cannot be synthesized without inventing data
    if not isinstance(doc, dict):
        return blocked("B1", "doc is not a JSON object")
    if not (isinstance(doc.get("cutoff"), str) and doc.get("cutoff")
            and isinstance(doc.get("source"), str) and doc.get("source")):
        return blocked("B1", "cutoff/source missing or ill-typed "
                             "(cannot synthesize top-level keys)")
    labels = doc.get("labels")
    if not isinstance(labels, list):
        return blocked("B1", "labels is not a list")
    res["n_labels_in"] = len(labels)
    if not labels:
        return blocked("B2", "labels list is empty")

    # B3 entry shape: date/state must be non-empty str
    for ent in labels:
        if not (isinstance(ent, dict) and isinstance(ent.get("date"), str)
                and ent.get("date")
                and isinstance(ent.get("state"), str)):
            return blocked("B3", "entry shape bad (non-dict, or date/state "
                                 "missing/non-str): "
                                 + json.dumps(ent, ensure_ascii=False,
                                              default=str)[:96])

    # A3 alias fold (spec-sanctioned 1:1 five-key relabeling only, B4 inline)
    alias_hits = {}
    mapped_labels = []
    for ent in labels:
        raw = ent["state"]
        folded = STATE_ALIAS_KEYS.get(raw.strip().lower(), raw)
        if folded not in STATES5:
            return blocked("B4", "state %r not one of the five keys after "
                                 "alias folding" % (raw,))
        if folded != raw:
            alias_hits[raw] = folded
        mapped_labels.append(dict(ent, state=folded))
    if alias_hits:
        res["log"].append({"op": "alias",
                           "map": {k: alias_hits[k] for k in sorted(alias_hits)},
                           "law": "MATRIX sec.1 five-key 1:1 definition line"})

    # A1 sort ascending by date
    ordered = sorted(mapped_labels, key=lambda e: e["date"])
    if [e["date"] for e in ordered] != [e["date"] for e in mapped_labels]:
        res["log"].append({"op": "sort", "by": "date ascending"})

    # A2 dedupe byte-equal duplicates; B5 on any same-date difference
    kept = []
    seen = {}
    dropped = 0
    for ent in ordered:
        d = ent["date"]
        if d in seen:
            if _entry_bytes(ent) != _entry_bytes(seen[d]):
                return blocked("B5", "same-date entries differ beyond "
                                      "byte-equality (a pick = judgment): "
                                      + d)
            dropped += 1
            continue
        seen[d] = ent
        kept.append(ent)
    if dropped:
        res["log"].append({"op": "dedupe", "dropped": dropped,
                           "policy": "byte-equal entries only"})

    adapted = dict(doc)
    adapted["labels"] = kept
    res["n_labels_out"] = len(kept)

    # B0 fail-closed: the shell must pass the frozen validator unchanged
    receipt = validate_contract(adapted)
    if not receipt["pass"]:
        return blocked("B0", "internal: adapted shell still fails the "
                             "frozen validator: "
                             + json.dumps(receipt["checks"], sort_keys=True))
    res["ok"] = True
    res["adapted"] = adapted
    return res


def probe(labels_dir=None):
    """Read-only per-file classification of the labels dir (no writes)."""
    from regime_gate_dualarm import LABELS_DIR
    d = labels_dir if labels_dir is not None else LABELS_DIR
    if not os.path.isdir(d):
        print("adapter probe: labels dir absent (%s)" % d)
        return 0
    n = 0
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        p = os.path.join(d, name)
        try:
            with io.open(p, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception as e:
            print("[UNREADABLE] %s (%s)" % (name, e))
            continue
        rep = classify(doc)
        tag = "PASS" if rep["pass"] else "VIOLATION " + json.dumps(
            sorted(rep["failed_checks"]), sort_keys=True)
        print("[%s] %s" % (tag, name))
        n += 1
    print("adapter probe: %d files classified (read-only, zero writes)" % n)
    return 0


def _selftest():
    import shutil
    import tempfile

    results = []

    def check(name, cond):
        results.append((name, bool(cond)))

    good_doc = {"cutoff": "2026-09-30", "source": "REGIME-5 (bm-a)",
                "labels": [{"date": "2026-09-29", "state": "BEAR"},
                           {"date": "2026-09-30", "state": "BEAR"}]}

    # classify: clean doc
    check("classify_clean_pass", classify(good_doc)["pass"] is True)

    # A1 sort fix: unsorted input -> sorted legal shell
    unsorted_doc = {"cutoff": "x", "source": "y",
                   "labels": [{"date": "2026-01-05", "state": "CHOP"},
                              {"date": "2026-01-02", "state": "BULL"},
                              {"date": "2026-01-03", "state": "GRIND"}]}
    r = adapt(unsorted_doc)
    check("sort_fix_ok", r["ok"] is True)
    check("sort_fix_order",
          [e["date"] for e in r["adapted"]["labels"]]
          == ["2026-01-02", "2026-01-03", "2026-01-05"])
    check("sort_fix_logged",
          any(e["op"] == "sort" for e in r["log"]))

    # A2 dedupe: byte-equal duplicates dropped, differing stay blocked
    dup_doc = {"cutoff": "x", "source": "y",
               "labels": [{"date": "2026-01-02", "state": "BULL"},
                          {"date": "2026-01-02", "state": "BULL"},
                          {"date": "2026-01-03", "state": "CHOP"}]}
    r = adapt(dup_doc)
    check("dedupe_ok", r["ok"] is True and r["n_labels_out"] == 2
          and r["n_labels_in"] == 3)
    conflict_doc = {"cutoff": "x", "source": "y",
                    "labels": [{"date": "2026-01-02", "state": "BULL"},
                               {"date": "2026-01-02", "state": "BULL",
                                "conf": 1},
                               {"date": "2026-01-03", "state": "CHOP"}]}
    r = adapt(conflict_doc)
    check("dedupe_conflict_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B5")
    two_state_doc = {"cutoff": "x", "source": "y",
                     "labels": [{"date": "2026-01-02", "state": "BULL"},
                                {"date": "2026-01-02", "state": "BEAR"}]}
    r = adapt(two_state_doc)
    check("same_date_two_states_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B5")

    # A3 alias fold: case + the five spec Chinese names
    alias_doc = {"cutoff": "x", "source": "y",
                 "labels": [{"date": "2026-01-02", "state": "bull"},
                            {"date": "2026-01-03", "state":
                             "\u725b\u5e02"},
                            {"date": "2026-01-04", "state":
                             "\u9707\u8361"},
                            {"date": "2026-01-05", "state":
                             "\u9634\u8dcc"},
                            {"date": "2026-01-06", "state":
                             "\u718a\u5e02"},
                            {"date": "2026-01-07", "state":
                             "\u62a4\u76d8\u671f"}]}
    r = adapt(alias_doc)
    check("alias_fold_ok", r["ok"] is True)
    check("alias_fold_values",
          [e["state"] for e in r["adapted"]["labels"]]
          == ["BULL", "BULL", "CHOP", "GRIND", "BEAR", "SUPPORT"])
    check("alias_fold_logged",
          any(e["op"] == "alias" for e in r["log"]))

    # B4 unknown state after folding stays blocked
    r = adapt({"cutoff": "x", "source": "y",
               "labels": [{"date": "2026-01-02", "state": "MARS"}]})
    check("unknown_state_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B4")

    # B1/B2/B3 blocked classes
    r = adapt({"labels": []})
    check("missing_keys_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B1")
    r = adapt({"cutoff": "x", "source": "y", "labels": []})
    check("empty_labels_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B2")
    r = adapt({"cutoff": "x", "source": "y", "labels": "nope"})
    check("labels_not_list_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B1")
    r = adapt({"cutoff": "x", "source": "y",
               "labels": [{"date": "2026-01-02"}]})
    check("entry_missing_state_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B3")
    r = adapt({"cutoff": "x", "source": "y",
               "labels": [["2026-01-02", "BULL"]]})
    check("entry_not_dict_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B3")
    r = adapt({"cutoff": "x", "source": "y",
               "labels": [{"date": 20260102, "state": "BULL"}]})
    check("non_str_date_blocked",
          r["ok"] is False and r["blocked"][0]["clause"] == "B3")

    # verbatim preservation: extra top-level key + entry extras ride through
    rich = {"cutoff": "x", "source": "y", "extra_top": {"keep": [1, 2]},
            "labels": [{"date": "2026-01-03", "state": "CHOP", "z": 7},
                       {"date": "2026-01-02", "state": "BULL", "z": 3}]}
    r = adapt(rich)
    check("extras_preserved",
          r["ok"] is True and r["adapted"]["extra_top"] == {"keep": [1, 2]}
          and all("z" in e for e in r["adapted"]["labels"]))

    # violations face: failed frozen checks ride into the result
    r = adapt({"cutoff": "x", "source": "y", "labels": []})
    check("violations_face_carried",
          "labels_nonempty" in (r["violations"] or {}))

    # determinism: identical input -> identical shell bytes
    td = tempfile.mkdtemp(prefix="adapter_st_")
    try:
        doc = {"cutoff": "x", "source": "y",
               "labels": [{"date": "2026-01-0%d" % i, "state": s}
                          for i, s in ((2, "BULL"), (3, "bull"),
                                        (1, "\u725b\u5e02"))]
               + [{"date": "2026-01-03", "state": "BULL"}]}
        a1 = adapt(doc)["adapted"]
        a2 = adapt(doc)["adapted"]
        b1 = json.dumps(a1, sort_keys=True, ensure_ascii=False)
        b2 = json.dumps(a2, sort_keys=True, ensure_ascii=False)
        check("adapt_deterministic", b1 == b2)
        # combined fixture: alias + sort + dedupe in one pass
        r = adapt(doc)
        check("combined_ops_ok", r["ok"] is True and r["n_labels_out"] == 3)
        check("combined_ops_log",
              {e["op"] for e in r["log"]} == {"alias", "sort", "dedupe"})
        # probe leg on a temp dir (read-only)
        ldir = os.path.join(td, "labels")
        os.makedirs(ldir)
        with io.open(os.path.join(ldir, "A.json"), "w",
                     encoding="utf-8") as f:
            json.dump({"cutoff": "x", "source": "y",
                       "labels": [{"date": "2026-01-02",
                                   "state": "MARS"}]}, f)
        import io as _io
        from contextlib import redirect_stdout
        buf = _io.StringIO()
        with redirect_stdout(buf):
            rc = probe(ldir)
        check("probe_read_only_rc0", rc == 0 and "VIOLATION" in buf.getvalue())
    finally:
        shutil.rmtree(td, ignore_errors=True)

    n_pass = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print("[%s] adapter selftest: %s" % ("PASS" if ok else "FAIL", name))
    print("Summary: %d/%d PASS, %d FAIL" % (
        n_pass, len(results), len(results) - n_pass))
    return n_pass == len(results)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "probe":
        return probe()
    if argv and argv[0] == "selftest":
        return 0 if _selftest() else 1
    print("usage: regime_gate_dualarm_adapter.py [probe|selftest]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
