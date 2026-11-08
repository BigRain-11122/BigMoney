# -*- coding: utf-8 -*-
"""E573 -- do the sentences that print less than their round's legs table say so elsewhere?

E568 recovered the legs table for 192 rounds from git and found 22 printed chain sentences
whose denominator is below that table while the sentence reads as the whole chain (1 more
labels itself a subset and is counted separately).  The open question is not arithmetic but
provenance: a round may have run a *subset* -- a deliberate `--only`, a checkpoint, a resumed
window -- and then the sentence is honest and merely quoted from a second run.

This study asks, for each of the 22, whether anything in that round's own report row (or in a
sibling row of the same round: closeout/postscript/addendum) declares a scope narrower than the
recovered table.  Three arms, all mechanical, the gate re-derives every one:

  naive_marker_words   the bare words a subset declaration would use ('family', 'subset',
                       'partial', '--only') anywhere in the row -- published because it is the
                       trap: in this population most of them are about research families and
                       leg *seeds*, not about the legs scope, so a marker-only reading would
                       call eight of the twenty-two declared.
  chain_scoped_declaration  a marker word AND a chain-vocabulary word within the same window of
                       the row (CHAIN_VOCAB x SUBSET_WORDS, max distance WINDOW chars) -- this is
                       the arm that decides.
  git_witness_arm      the round's own chain script, read out of git at the commit E568 named:
                       its legs table is re-counted (so the published table is not inherited on
                       faith) and its body is scanned for a narrowing token.  A script with a
                       narrowing token is a *mechanism* by which a round could run a subset; it
                       is published beside the prose arm and never substituted for it.

Classification (first match wins, witness published):
  the_sentence_s_own_row_declares_a_subset
  another_row_of_the_same_round_declares_a_subset
  no_row_of_that_round_declares_a_subset        <- the prose reads as the whole chain
  no_row_but_the_round_s_script_can_narrow      <- neither arm 2 nor 3 fires, but the script
                                                   carries the mechanism, so the scope is
                                                   unrecoverable from the report alone

Usage: python scripts/e573_silent_chain.py [build|check|check-fast|verify|selftest]
"""
import importlib.util
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
E568_FACE = os.path.join(OUTDIR, "oldchaintable_latest.json")
CUTOFF = "2026-11-08"
SILENT = "the_denominator_is_below_the_table_and_the_sentence_reads_as_the_whole_chain"

C_OWN = "the_sentence_s_own_row_declares_a_subset"
C_SIBLING = "another_row_of_the_same_round_declares_a_subset"
C_MECHANISM = "no_row_but_the_round_s_script_can_narrow"
C_SILENT = "no_row_of_that_round_declares_a_subset"
CLASSES = (C_OWN, C_SIBLING, C_MECHANISM, C_SILENT)

SUBSET_WORDS = ("--only", "only the", "only ran", "subset", "partial", "checkpoint",
                "resumed", "not the whole", "fewer legs", "family")
# A declaration of scope is a *phrase about a run*, not a bare word near chain vocabulary:
# r1544 says "remaining s6 chain legs" and "e206/e207 family" in one row, so proximity alone
# would call a research-family mention a scope declaration.  The patterns below are the arm
# that decides; SUBSET_WORDS is published beside them as the naive reading.
DECL_PATTERNS = (
    r"--only\s+\S+",
    r"labell?ed\s+(?:a\s+)?subset",
    r"is\s+a\s+subset",
    r"ran\s+a\s+subset",
    r"partial\s+(?:run|chain)",
    r"checkpoint(?:ed)?\s+(?:at|after)\s+leg",
    r"resumed\s+(?:the\s+)?(?:chain|run)",
    r"not\s+the\s+whole\s+chain",
    r"only\s+the\s+(?:new\s+)?\S+\s+legs?",
    r"subset\s+receipt",
)
CHAIN_VOCAB = ("chain", "legs", "leg ", "receipt", "s6", "rc0", "legs table", "leg table")
NARROWING_TOKENS = ("--only", "-only", "select-object -first", "-first ", "| select ",
                    "[0..", "$legs = $legs", "where-object", "-le ", "prefix")
# A *scope switch* is a flag the run itself can carry (--only X); a *slicing token* only shows
# that the script can cut a list somewhere.  Published apart, because "the script contains
# `prefix`" is far weaker evidence than "the script takes --only".
SCOPE_SWITCH_TOKENS = ("--only", "-only")
WINDOW = 200
ROUND_TOK = re.compile(r"\br(\d{1,4})(?!\d)", re.I)
ROW_TS = re.compile(r"^\|\s*\d{4}-\d{2}-\d{2}")


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _git(args, timeout=240):
    try:
        out = subprocess.run(["git"] + args, cwd=ROOT, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, timeout=timeout)
    except Exception:
        return ""
    return out.stdout.decode("utf-8", "replace")


def _e568():
    """Reuse E568's leg-counting so this study never re-implements it (and can re-derive it)."""
    path = os.path.join(HERE, "e568_old_chain_table.py")
    spec = importlib.util.spec_from_file_location("e568_old_chain_table", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_LINES = {}


def lines_of(path):
    if path not in _LINES:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            _LINES[path] = []
        else:
            _LINES[path] = io.open(full, encoding="utf-8", errors="replace").read().splitlines()
    return _LINES[path]


def round_of_row(line):
    """The round a report row belongs to, read only from a row that starts with a timestamp."""
    if not ROW_TS.match(line):
        return None
    parts = [x.strip() for x in line.split("|")]
    if len(parts) < 3:
        return None
    m = ROUND_TOK.search(parts[2])
    return int(m.group(1)) if m else None


def scoped_declaration(text):
    """A phrase that states the run's own scope; the witness carries the matched phrase."""
    low = (text or "").lower()
    hits = []
    for pat in DECL_PATTERNS:
        m = re.search(pat, low)
        if m:
            hits.append({"marker": m.group(0).strip(), "chain_word": next(
                (v for v in CHAIN_VOCAB if v in low), None),
                "at": m.start(),
                "snippet": (text or "")[max(0, m.start() - 90): m.end() + 110]})
    return hits


def naive_markers(text):
    low = (text or "").lower()
    return [w for w in SUBSET_WORDS if w in low]


def witness_blob(row):
    """The round's own chain script as it stood at E568's witness commit, plus a re-count."""
    path, sha = row.get("witness_path"), row.get("witness_commit")
    entry = {"path": path, "commit": sha, "read": False}
    if not path or not sha:
        return entry
    out = _git(["show", "%s:%s" % (sha, path)])
    if not out:
        entry["missing_object"] = True
        return entry
    entry["read"] = True
    entry["bytes"] = len(out.encode("utf-8"))
    try:
        entry["table_rederived"] = _e568().leg_count(path, out)
    except Exception:
        entry["table_rederived"] = None
    low = out.lower()
    hits = [t for t in NARROWING_TOKENS if t in low]
    entry["narrowing_tokens"] = hits
    entry["scope_switch_tokens"] = [t for t in hits if t in SCOPE_SWITCH_TOKENS]
    entry["slicing_tokens"] = [t for t in hits if t not in SCOPE_SWITCH_TOKENS]
    entry["can_narrow"] = bool(hits)
    return entry


def row_for(silent_row):
    report = silent_row["report"]
    lines = lines_of(report)
    own = lines[silent_row["line"] - 1] if silent_row["line"] - 1 < len(lines) else ""
    siblings = []
    for i, line in enumerate(lines):
        if i + 1 == silent_row["line"]:
            continue
        if round_of_row(line) == silent_row["round"]:
            decl = scoped_declaration(line)
            siblings.append({"line": i + 1, "chars": len(line),
                             "declares_a_subset": bool(decl),
                             "declaration": decl[0] if decl else None,
                             "head": line[:160]})
    own_decl = scoped_declaration(own)
    script = witness_blob(silent_row)
    row = {
        "report": report,
        "line": silent_row["line"],
        "machine": silent_row["machine"],
        "round": silent_row["round"],
        "printed": {"numerator": silent_row["numerator"],
                    "denominator": silent_row["denominator"]},
        "table_from_E568": silent_row["table"],
        "table_rederived_from_git": script.get("table_rederived"),
        "denominator_below_table_by": (
            None if silent_row.get("table") is None else
            silent_row["table"] - (silent_row["denominator"] or 0)),
        "chars_in_own_row": len(own),
        "naive_markers_in_own_row": naive_markers(own),
        "own_row_declaration": own_decl[0] if own_decl else None,
        "sibling_rows": siblings,
        "script": script,
        "sentence": own[:300],
    }
    row["class"], row["decided_by"] = classify(row)
    return row


def classify(w):
    if w.get("own_row_declaration"):
        d = w["own_row_declaration"]
        return C_OWN, ("the row names a chain-scoped subset (marker %r beside %r): %r"
                       % (d["marker"], d["chain_word"], d["snippet"]))
    declared = [s for s in (w.get("sibling_rows") or []) if s.get("declares_a_subset")]
    if declared:
        s = declared[0]
        d = s["declaration"]
        return C_SIBLING, ("a sibling row of the same round (line %d) declares a subset "
                           "(marker %r beside %r)" % (s["line"], d["marker"], d["chain_word"]))
    if (w.get("script") or {}).get("can_narrow"):
        return C_MECHANISM, ("no row of the round says it, but the round's own script carries a "
                             "narrowing token %r, so the scope is not recoverable from the "
                             "report alone" % ",".join(w["script"]["narrowing_tokens"][:3]))
    return C_SILENT, "no row of that round declares a subset and the script carries no narrowing token"


def _verdict(summary):
    c = summary.get("by_class") or {}
    n = c.get("rows", 0)
    if not n:
        return "no_silent_sentence_to_price"
    if c.get(C_OWN) or c.get(C_SIBLING):
        return ("%d_of_the_%d_silent_sentences_are_declared_subset_runs_elsewhere_in_the_round"
                % (c.get(C_OWN, 0) + c.get(C_SIBLING, 0), n))
    if c.get(C_MECHANISM):
        return ("no_row_declares_a_subset_but_%d_of_the_%d_round_s_scripts_carry_the_mechanism"
                % (c.get(C_MECHANISM, 0), n))
    return ("none_of_the_%d_silent_sentences_is_a_declared_subset_run_by_its_own_round" % n)


def _verdict_line(s):
    c = s.get("by_class") or {}
    return ("rows=%d own_row=%d sibling_row=%d mechanism_only=%d silent=%d "
            "| naive_marker_rows=%d scoped_declaration_rows=%d "
            "| tables_rederived=%d tables_disagree_with_E568=%d"
            % (c.get("rows", 0), c.get(C_OWN, 0), c.get(C_SIBLING, 0), c.get(C_MECHANISM, 0),
               c.get(C_SILENT, 0), s.get("rows_with_a_naive_marker", 0),
               s.get("rows_with_a_scoped_declaration", 0),
               s.get("tables_rederived", 0), s.get("tables_that_disagree_with_E568", 0)))


def build(write=True):
    face = _read_json(E568_FACE)
    population = [r for r in face.get("rows") or [] if r.get("class") == SILENT]
    rows = [row_for(r) for r in population]
    by_class = {k: sum(1 for r in rows if r["class"] == k) for k in CLASSES}
    by_class["rows"] = len(rows)
    scoped = [r for r in rows if r["own_row_declaration"]
              or any(s["declares_a_subset"] for s in r["sibling_rows"])]
    summary = {
        "population_from_E568": len(population),
        "by_class": by_class,
        "rows_with_a_naive_marker": sum(1 for r in rows if r["naive_markers_in_own_row"]),
        "rows_with_a_scoped_declaration": len(scoped),
        "rows_where_the_naive_marker_is_not_a_scope": sum(
            1 for r in rows if r["naive_markers_in_own_row"] and not (
                r["own_row_declaration"]
                or any(s["declares_a_subset"] for s in r["sibling_rows"]))),
        "rows_with_a_sibling_row": sum(1 for r in rows if r["sibling_rows"]),
        "sibling_rows_seen": sum(len(r["sibling_rows"]) for r in rows),
        "tables_rederived": sum(1 for r in rows
                                if (r["script"] or {}).get("table_rederived") is not None),
        "tables_that_disagree_with_E568": sum(
            1 for r in rows
            if (r["script"] or {}).get("table_rederived") is not None
            and r["script"]["table_rederived"] != r["table_from_E568"]),
        "scripts_read_from_git": sum(1 for r in rows if (r["script"] or {}).get("read")),
        "scripts_that_can_narrow": sum(1 for r in rows if (r["script"] or {}).get("can_narrow")),
        "scripts_with_a_scope_switch": sum(
            1 for r in rows if (r["script"] or {}).get("scope_switch_tokens")),
        "scripts_with_only_a_slicing_token": sum(
            1 for r in rows if (r["script"] or {}).get("slicing_tokens")
            and not (r["script"] or {}).get("scope_switch_tokens")),
        "denominator_gap_total": sum(r["denominator_below_table_by"] or 0 for r in rows),
        "unnamed_witnesses": ["whether_the_round_actually_passed_a_flag_at_run_time"],
    }
    out = {
        "study": "E573_silent_chain",
        "card": "E573",
        "dept": "research+engineering",
        "machine": "bm-b",
        "evidence_cutoff": CUTOFF,
        "population": ("every E568 row classed %r (machine-read from oldchaintable_latest.json)"
                       % SILENT),
        "rule": ("own row scoped declaration -> own; else a sibling row of the same round -> "
                 "sibling; else a narrowing token in the round's script -> mechanism; else silent"),
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "rows": rows,
    }
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        for path in (os.path.join(OUTDIR, "SILENTCHAIN-%s.json" % CUTOFF),
                     os.path.join(OUTDIR, "silentchain_latest.json")):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return out


def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if face.get("verdict") != _verdict(s):
        problems.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(s):
        problems.append("the verdict line does not re-derive from the summary")
    if s.get("population_from_E568") != len(rows):
        problems.append("the population count does not equal the rows")
    counts = {k: sum(1 for r in rows if r.get("class") == k) for k in CLASSES}
    for k, v in counts.items():
        if (s.get("by_class") or {}).get(k) != v:
            problems.append("by_class.%s does not re-derive from the rows" % k)
    if (s.get("by_class") or {}).get("rows") != len(rows):
        problems.append("by_class.rows does not equal the rows")
    scoped = sum(1 for r in rows if r.get("own_row_declaration")
                 or any(x.get("declares_a_subset") for x in r.get("sibling_rows") or []))
    if s.get("rows_with_a_scoped_declaration") != scoped:
        problems.append("rows_with_a_scoped_declaration does not re-derive from the rows")
    if s.get("rows_with_a_naive_marker") != sum(
            1 for r in rows if r.get("naive_markers_in_own_row")):
        problems.append("rows_with_a_naive_marker does not re-derive from the rows")
    if s.get("scripts_with_a_scope_switch") != sum(
            1 for r in rows if (r.get("script") or {}).get("scope_switch_tokens")):
        problems.append("scripts_with_a_scope_switch does not re-derive from the rows")
    if s.get("tables_rederived") != sum(
            1 for r in rows if (r.get("script") or {}).get("table_rederived") is not None):
        problems.append("tables_rederived does not re-derive from the rows")
    for r in rows:
        if r.get("class") not in CLASSES:
            problems.append("%s r%s: class %r is not one this study declares"
                            % (r.get("report"), r.get("round"), r.get("class")))
            break
        if not r.get("decided_by"):
            problems.append("%s r%s: no witness is named" % (r.get("report"), r.get("round")))
            break
        if r.get("class") == C_OWN and not r.get("own_row_declaration"):
            problems.append("%s r%s: own_row class without a declaration"
                            % (r.get("report"), r.get("round")))
            break
        if r.get("class") == C_SIBLING and not any(
                x.get("declares_a_subset") for x in r.get("sibling_rows") or []):
            problems.append("%s r%s: sibling class without a declaring sibling row"
                            % (r.get("report"), r.get("round")))
            break
        if r.get("class") == C_MECHANISM and not (r.get("script") or {}).get("can_narrow"):
            problems.append("%s r%s: mechanism class without a narrowing token"
                            % (r.get("report"), r.get("round")))
            break
        if r.get("class") == C_SILENT and (
                r.get("own_row_declaration")
                or any(x.get("declares_a_subset") for x in r.get("sibling_rows") or [])
                or (r.get("script") or {}).get("can_narrow")):
            problems.append("%s r%s: silent class with a witness that should have fired"
                            % (r.get("report"), r.get("round")))
            break
    return problems


def _fixture(klass):
    row = {
        "report": "logs/iteration-loop/round_reports.md", "line": 10, "machine": "b",
        "round": 100, "printed": {"numerator": 25, "denominator": 25},
        "table_from_E568": 37, "table_rederived_from_git": 37,
        "denominator_below_table_by": 12, "chars_in_own_row": 500,
        "naive_markers_in_own_row": [], "own_row_declaration": None, "sibling_rows": [],
        "script": {"read": True, "table_rederived": 37, "can_narrow": False,
                   "narrowing_tokens": []},
        "sentence": "S6 25/25 rc=0",
    }
    if klass == C_OWN:
        row["own_row_declaration"] = {"marker": "--only", "chain_word": "legs",
                                      "snippet": "ran --only star legs"}
    elif klass == C_SIBLING:
        row["sibling_rows"] = [{"line": 11, "declares_a_subset": True,
                                "declaration": {"marker": "subset", "chain_word": "chain"}}]
    elif klass == C_MECHANISM:
        row["script"]["can_narrow"] = True
        row["script"]["narrowing_tokens"] = ["--only"]
    row["class"] = klass
    row["decided_by"] = "fixture"
    return row


def selftest():
    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "%r != %r" % (got, want) if got != want else ""))

    eq("an_own_row_declaration_decides_first", classify(_fixture(C_OWN))[0], C_OWN)
    eq("a_declaring_sibling_row_decides_next", classify(_fixture(C_SIBLING))[0], C_SIBLING)
    eq("a_narrowing_script_is_published_as_a_mechanism",
       classify(_fixture(C_MECHANISM))[0], C_MECHANISM)
    eq("nothing_firing_is_silent", classify(_fixture(C_SILENT))[0], C_SILENT)
    eq("a_research_family_word_beside_chain_vocabulary_is_not_a_scope",
       scoped_declaration("not run: remaining s6 chain legs, collector family"), [])
    eq("a_scope_phrase_is_a_declaration",
       bool(scoped_declaration("ran the chain with --only two legs")), True)
    eq("a_bare_family_mention_is_still_a_naive_marker",
       naive_markers("the four-gate family closed"), ["family"])
    eq("a_timestamp_and_round_row_is_attributed",
       round_of_row("| 2026-11-09T01:21 | r1600 postscript | x |"), 1600)
    eq("a_continuation_line_is_not_a_row",
       round_of_row("  - r1285 delivery gate: push abc"), None)
    fx = {"summary": {"population_from_E568": 1,
                      "by_class": {"rows": 1, C_OWN: 1, C_SIBLING: 0, C_MECHANISM: 0,
                                   C_SILENT: 0},
                      "rows_with_a_scoped_declaration": 1,
                      "rows_with_a_naive_marker": 0, "tables_rederived": 1,
                      "tables_that_disagree_with_E568": 0},
          "rows": [_fixture(C_OWN)]}
    fx["verdict"] = _verdict(fx["summary"])
    fx["verdict_line"] = _verdict_line(fx["summary"])
    eq("a_consistent_fixture_face_has_no_problems", face_problems(fx), [])
    bad = json.loads(json.dumps(fx))
    bad["verdict"] = "a_verdict_this_study_never_publishes"
    eq("a_hand_written_verdict_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["rows"][0]["class"] = C_SIBLING
    eq("a_class_without_its_witness_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["rows"][0]["class"] = "reads_like_a_subset"
    eq("an_invented_class_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["rows"][0]["class"] = C_SILENT
    eq("a_silent_row_hiding_a_declaration_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["summary"]["rows_with_a_scoped_declaration"] = 0
    eq("a_count_that_does_not_re_derive_is_refused", bool(face_problems(bad)), True)
    failed = [n for n, good, _ in ok if not good]
    for n, good, detail in ok:
        print("  %s %s%s" % ("PASS" if good else "FAIL", n, "" if good else "  <- " + detail))
    print("selftest %d/%d" % (len(ok) - len(failed), len(ok)))
    return 0 if not failed else 1


def _check(face, label):
    problems = face_problems(face)
    if problems:
        for p in problems:
            print("%s FAIL %s" % (label, p))
        return 1
    print("%s PASS %s" % (label, face.get("verdict_line")))
    return 0


def check():
    return _check(_read_json(os.path.join(OUTDIR, "silentchain_latest.json")), "CHECK")


def check_fast():
    """What verify adds on top of check is the live re-derivation; this is the cheap arm."""
    return check()


def verify():
    fresh = build(write=False)
    published = _read_json(os.path.join(OUTDIR, "silentchain_latest.json"))
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "summary"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    if [(r.get("class"), r.get("round"), r.get("machine")) for r in fresh.get("rows") or []] != \
            [(r.get("class"), r.get("round"), r.get("machine"))
             for r in published.get("rows") or []]:
        problems.append("a row's class changed between the published face and a live rebuild")
    for p in problems:
        print("VERIFY FAIL %s" % p)
    if not problems:
        print("VERIFY PASS %d rows re-derived" % len(published.get("rows") or []))
    return 0 if not problems else 1


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "build"
    if cmd == "selftest":
        return selftest()
    if cmd == "build":
        face = build(write=True)
        print("BUILT %s | %s" % (face["verdict"], face["verdict_line"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "check-fast":
        return check_fast()
    if cmd == "verify":
        return verify()
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())