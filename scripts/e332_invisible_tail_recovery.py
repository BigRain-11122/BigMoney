"""E332 -- what lives in the text the corpus helper cannot see, and which published E3xx count
moves once that text is read.

``e326.code_lines`` walks a source line by line and flips an ``in_doc`` flag whenever a stripped
line *starts* with a triple quote and carries an odd number of triple-quote marks.  A multi-line
literal whose closing delimiter begins a continuation line -- the ``TEXT = (\"\"\"...\"\"\".split())``
idiom -- therefore opens a docstring that does not exist, and the flag re-synchronises one literal
later, in the wrong phase: real code leaves the corpus and docstring prose enters it.  E331 published
that 22 of 2,284 sources lose their tail to this; this study recovers the hidden text with the real
tokenizer, classifies what is in it, and re-prices E331's own counts against the recovered corpus.

    python scripts/e332_invisible_tail_recovery.py run|verify|selftest
"""
import io
import json
import os
import re
import sys
import tempfile
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)
import e331_pointer_only_readers as e331  # noqa: E402

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "INVISIBLETAIL-%s.json" % TODAY
LATEST = "invisibletail_latest.json"
STUDY = "E332_invisible_tail_recovery"

NOT_CODE = (tokenize.STRING, tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
            tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER)

DEF = re.compile(r"^(?:async\s+)?def\s+[A-Za-z_]\w*\s*\(")
CLS = re.compile(r"^class\s+[A-Za-z_]\w*")
FACE_HANDLE = re.compile(r"[\w./\\-]*results/[\w./\\-]+\.(?:json|md|csv)\b")
LATEST_HANDLE = re.compile(r"[\"'][\w./\\-]*_latest\.json[\"']")
LOAD = re.compile(r"\b(?:io\.)?open\s*\(|json\.load\s*\(|\.read_text\s*\(")
LEG = re.compile(r"selftest|_leg\b|\bleg\(|legs\b")

K_DEF = "definitions"
K_CLASS = "classes"
K_FACE = "face_handles"
K_LOAD = "load_sites"
K_LEG = "selftest_legs"
KINDS = (K_DEF, K_CLASS, K_FACE, K_LOAD, K_LEG)

V_FLOOR = "the_published_reader_count_is_a_floor_over_a_corpus_that_hides_its_own_code"
V_PAIRS = "the_helper_hides_pairs_but_no_published_reader_classification_moves"
V_CLEAN = "the_helper_hides_no_line_a_published_count_depends_on"
VERDICTS = (V_FLOOR, V_PAIRS, V_CLEAN)

MAX_ROWS = 400
MAX_EXAMPLES = 3


# ---------------------------------------------------------------------------------- primitives

def token_code_lines(src):
    """Line numbers carrying real code, decided by the language's own tokenizer.

    ``TokenError`` is not a failure here: a literal that really is unterminated stops the stream,
    and every line yielded before that point was still read exactly.
    """
    lines = set()
    stream_ended_early = False
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src or "").readline):
            if tok.type in NOT_CODE:
                continue
            lines.add(tok.start[0])
    except (tokenize.TokenError, IndentationError, SyntaxError):
        stream_ended_early = True
    return lines, stream_ended_early


def true_lines(src):
    """The corpus helper's contract, honoured: code lines as ``(lineno, stripped)``."""
    keep, _early = token_code_lines(src)
    out = []
    for lineno, line in enumerate((src or "").splitlines(), 1):
        if lineno in keep:
            stripped = line.strip()
            if stripped:
                out.append((lineno, stripped))
    return out


def classify(text):
    """What a recovered line is, in the terms the card asks for (a line can be more than one)."""
    kinds = []
    if DEF.match(text):
        kinds.append(K_DEF)
    if CLS.match(text):
        kinds.append(K_CLASS)
    if FACE_HANDLE.search(text) or LATEST_HANDLE.search(text):
        kinds.append(K_FACE)
    if LOAD.search(text):
        kinds.append(K_LOAD)
    if LEG.search(text):
        kinds.append(K_LEG)
    return kinds


def helper_blind_spans(src, visible_lines):
    """Contiguous runs of real code the helper does not show, as ``(first, last, n)``."""
    keep, _early = token_code_lines(src)
    hidden = sorted(n for n in keep if n not in visible_lines)
    spans = []
    for n in hidden:
        if spans and n == spans[-1][1] + 1:
            spans[-1][1] = n
            spans[-1][2] += 1
        else:
            spans.append([n, n, 1])
    return spans


def tail_is_invisible(src, lines):
    """E331's own metric, kept so the two readings can be compared rather than conflated."""
    raw = (src or "").splitlines()
    if not raw or not lines:
        return 0
    last_raw = len(raw)
    while last_raw > 0 and not raw[last_raw - 1].strip():
        last_raw -= 1
    return max(0, last_raw - lines[-1][0])


def first_hidden_code_line(src):
    """The first line carrying real code that the helper does not show, or None.

    Deliberately one-sided: the helper also *shows* prose (a one-line docstring is appended as
    code because the stripped line counts two triple marks and the odd-count branch never fires),
    but that direction loses nothing and is not what this study prices.
    """
    keep, _early = token_code_lines(src)
    shown = {n for n, _t in e326.code_lines(src)}
    raw = (src or "").splitlines()
    for lineno in range(1, len(raw) + 1):
        if lineno not in keep:
            continue
        if not raw[lineno - 1].strip():
            continue
        if lineno not in shown:
            return lineno
    return None


# -------------------------------------------------------------------------------------- build

def scan(files):
    """Per-source recovery rows, independent of every E3xx consumer."""
    rows = []
    for path, src in files:
        rel = e326.relp(path)
        shown = e326.code_lines(src)
        shown_lines = {n for n, _t in shown}
        keep, stream_ended_early = token_code_lines(src)
        raw = (src or "").splitlines()
        recovered = []
        kinds_total = {k: 0 for k in KINDS}
        for lineno in sorted(n for n in keep if n not in shown_lines):
            text = raw[lineno - 1].strip()
            kinds = classify(text)
            for k in kinds:
                kinds_total[k] += 1
            recovered.append({"line": lineno, "text": text[:140], "kinds": kinds})
        spans = helper_blind_spans(src, shown_lines)
        if not recovered:
            continue
        rows.append({
            "source": rel,
            "raw_lines": len(raw),
            "lines_the_helper_shows": len(shown),
            "real_code_lines": len(keep),
            "recovered_code_lines": len(recovered),
            "spans": spans[:6],
            "span_count": len(spans),
            "first_hidden_code_line": first_hidden_code_line(src),
            "dropped_from_the_end": tail_is_invisible(src, shown),
            "stream_ended_early": stream_ended_early,
            "kinds": kinds_total,
            "examples": recovered[:MAX_EXAMPLES],
        })
    return sorted(rows, key=lambda r: -r["recovered_code_lines"])


def reprice(files, root):
    """E331's published summary, computed twice: with the shipped helper and with a correct one."""
    scratch = [tempfile.mkdtemp(prefix="e332_base_"), tempfile.mkdtemp(prefix="e332_fix_")]
    baseline = e331.build(root=root, outdir=scratch[0], files=files)
    shipped = e326.code_lines
    try:
        e326.code_lines = true_lines
        fixed = e331.build(root=root, outdir=scratch[1], files=files)
    finally:
        e326.code_lines = shipped
        if e326.code_lines is not shipped:
            raise AssertionError("the corpus helper was not restored")
    keys = ("sources_scanned", "families_referenced_only_through_a_pointer", "pairs",
            "pointer_only_readers", "distinct_families_read",
            "readers_guarded_before_they_use_the_value",
            "readers_whose_helper_turns_a_miss_into_None",
            "readers_that_raise_at_the_file",
            "sources_whose_tail_the_scanner_cannot_see",
            "prose_literals_rejected_as_notes")
    base_s = baseline["summary"]
    fix_s = fixed["summary"]
    delta = {k: (fix_s.get(k, 0) - base_s.get(k, 0)) for k in keys}
    handling = {}
    for k, v in (fix_s.get("handling_by_class") or {}).items():
        was = (base_s.get("handling_by_class") or {}).get(k, 0)
        if v != was:
            handling[k] = {"with_helper": was, "recovered": v, "delta": v - was}
    base_pairs = {(r["source"], r["family"]) for r in baseline["rows"]}
    fix_pairs = {(r["source"], r["family"]) for r in fixed["rows"]}
    base_class = {(r["source"], r["family"]): r["class"] for r in baseline["rows"]}
    fix_class = {(r["source"], r["family"]): r["class"] for r in fixed["rows"]}
    reclassified = [{"source": s, "family": f, "with_helper": base_class[(s, f)],
                     "recovered": fix_class[(s, f)]}
                    for s, f in sorted(set(base_class) & set(fix_class))
                    if base_class[(s, f)] != fix_class[(s, f)]]
    new_readers = sorted({(r["source"], r["family"]) for r in fixed["rows"]
                          if r["class"] == "pointer_only_reader"}
                         - {(r["source"], r["family"]) for r in baseline["rows"]
                            if r["class"] == "pointer_only_reader"})
    return {
        "with_shipped_helper": {k: base_s.get(k) for k in keys},
        "with_recovered_corpus": {k: fix_s.get(k) for k in keys},
        "delta": delta,
        "handling_by_class": handling,
        "verdict_with_shipped_helper": baseline["verdict"],
        "verdict_with_recovered_corpus": fixed["verdict"],
        "verdict_moved": baseline["verdict"] != fixed["verdict"],
        "readers_visible_only_in_the_recovered_text": [
            {"source": s, "family": f} for s, f in new_readers[:40]],
        "pairs_reclassified_when_the_corpus_is_read": reclassified[:40],
        "pairs_only_with_the_shipped_helper": len(base_pairs - fix_pairs),
        "pairs_only_with_the_recovered_corpus": len(fix_pairs - base_pairs),
    }


def build(root=None, outdir=None, files=None):
    root = root or ROOT
    files = files if files is not None else e326.corpus()
    rows = scan(files)
    pricing = reprice(files, root)

    total = {k: sum(r["kinds"][k] for r in rows) for k in KINDS}
    recovered_lines = sum(r["recovered_code_lines"] for r in rows)
    d = pricing["delta"]
    if d.get("pointer_only_readers"):
        verdict, reason = V_FLOOR, (
            "%d sources carry %d lines of real code the corpus helper does not show, and reading "
            "them moves E331's pointer-only reader count by %+d (pairs %+d, sources %+d): the "
            "published count is a floor, not a count"
            % (len(rows), recovered_lines, d["pointer_only_readers"], d.get("pairs", 0),
               d.get("sources_scanned", 0)))
    elif any(v for v in d.values()):
        verdict, reason = V_PAIRS, (
            "%d sources carry %d hidden lines and reading them moves a published count "
            "(pairs %+d) but no pointer-only reader class"
            % (len(rows), recovered_lines, d.get("pairs", 0)))
    else:
        verdict, reason = V_CLEAN, (
            "%d sources carry %d hidden lines yet no count E331 published moves when they are read"
            % (len(rows), recovered_lines))

    summary = {
        "sources_scanned": len(files),
        "sources_the_helper_blinds": len(rows),
        "recovered_code_lines": recovered_lines,
        "recovered_by_kind": total,
        "sources_whose_tail_is_invisible": sum(1 for r in rows if r["dropped_from_the_end"] > 10),
        "sources_blinded_before_their_last_line": sum(
            1 for r in rows if r["spans"] and r["spans"][0][0] < r["raw_lines"] - 1),
        "spans_per_source_median": (sorted(r["span_count"] for r in rows)[len(rows) // 2]
                                    if rows else 0),
        "sources_with_more_than_one_span": sum(1 for r in rows if r["span_count"] > 1),
        "sources_whose_stream_ended_early": sum(1 for r in rows if r["stream_ended_early"]),
        "repricing_delta": pricing["delta"],
        "verdict_moved": pricing["verdict_moved"],
        "pointer_only_readers_visible_only_in_the_recovered_text":
            len(pricing["readers_visible_only_in_the_recovered_text"]),
        "pairs_reclassified_when_the_corpus_is_read":
            len(pricing["pairs_reclassified_when_the_corpus_is_read"]),
        "rows_published": min(len(rows), MAX_ROWS),
        "rows_truncated": max(0, len(rows) - MAX_ROWS),
    }
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "verdict_reason": reason,
        "summary": summary,
        "rules": {
            "recovery": "a line is recovered when the real tokenizer finds a token on it that is "
                        "not STRING/COMMENT/NL/NEWLINE/INDENT/DEDENT/ENCODING/ENDMARKER and the "
                        "corpus helper does not show that line number",
            "helper_failure": "the helper flips into doc mode on a line that *starts* with a triple "
                              "quote and carries an odd count of them; a continuation line that "
                              "opens with a closing delimiter is read as an opener, and the flag "
                              "re-synchronises one literal later in the wrong phase",
            "reprice": "E331's own build() is run twice over the same file list, once with the "
                       "shipped helper and once with a tokenizer-backed one; the patched helper is "
                       "restored in a finally block and the restore is asserted",
            "no_silent_substitution": "the recovered text is never used to overwrite a published "
                                      "face; the delta is reported beside the shipped numbers",
        },
        "limits": {
            "tokenizer_truth": "the tokenizer answers 'is this line code', not 'would this module "
                               "import'; a file with a genuinely unterminated literal stops the "
                               "stream and is disclosed as stream_ended_early",
            "single_consumer": "only E331 is re-priced.  E326/E328/E329/E330 read the same helper, "
                               "so their counts are floors of the same shape but are not re-derived "
                               "here",
            "face_level": "the recovery classifies lines by shape (def / class / path literal / "
                          "load call / selftest mention); it does not execute them",
        },
        "repricing": pricing,
        "sources": rows[:MAX_ROWS],
    }
    target = outdir or OUTDIR
    os.makedirs(target, exist_ok=True)
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE, LATEST):
        with io.open(os.path.join(target, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return doc


# ------------------------------------------------------------------------------------- verify

def verify(root=None, files=None):
    root = root or ROOT
    fresh = build(root=root, outdir=tempfile.mkdtemp(prefix="e332_verify_"), files=files)
    path = os.path.join(root, "results", "state_tilt", FACE)
    try:
        with io.open(path, encoding="utf-8") as fh:
            disk = json.load(fh)
    except Exception as exc:
        return ["the face does not read: %r" % (exc,)]
    problems = []
    if disk.get("verdict") != fresh["verdict"]:
        problems.append("the verdict does not re-derive")
    if disk.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (disk.get("verdict"),))
    for key, value in fresh["summary"].items():
        if (disk.get("summary") or {}).get(key) != value:
            problems.append("summary.%s does not re-derive" % key)
    if (disk.get("summary") or {}).get("recovered_code_lines", 0) <= 0:
        problems.append("the recovery found nothing, which is a broken measurement not a clean tree")
    published = [(r["source"], r["recovered_code_lines"], r["first_hidden_code_line"])
                 for r in disk.get("sources") or []]
    recomputed = [(r["source"], r["recovered_code_lines"], r["first_hidden_code_line"])
                  for r in fresh["sources"]]
    if published != recomputed:
        problems.append("a published source row does not re-derive")
    for row in disk.get("sources") or []:
        if row["recovered_code_lines"] <= 0:
            problems.append("a source is published with no recovered line")
            break
        if not row["spans"]:
            problems.append("a published source carries no hidden span")
            break
    if not (disk.get("repricing") or {}).get("with_shipped_helper"):
        problems.append("the re-pricing half is missing")
    elif disk.get("repricing") != fresh["repricing"]:
        problems.append("the published re-pricing does not re-derive")
    return problems


# ----------------------------------------------------------------------------------- selftest

def _fx(body, name="mod.py"):
    root = tempfile.mkdtemp(prefix="e332_fx_")
    path = os.path.join(root, name)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    return root, [(path, body)]


SWALLOWING = (
    '"""A study with a parenthesized literal."""\n'
    'import json\n'
    '\n'
    'PROSE = ("""\n'
    '第一行\n'
    '第二行\n'
    '""".split())\n'
    '\n'
    'def load_a_pointer():\n'
    '    with open("results/x/FOO-2026-11-01.json", encoding="utf-8") as fh:\n'
    '        return json.load(fh)\n'
    '\n'
    'def selftest():\n'
    '    pass\n'
)

# A loss in the MIDDLE of a file: the helper re-synchronises on the next `X = ("""` line, so the
# file ends on a line it does show.  E331's tail metric therefore reads 0 while a def is missing.
MIDFILE = (
    'A = ("""\n'
    'one\n'
    '""".split())\n'
    'def load_mid():\n'
    '    return json.load(open("results/x/mid_latest.json"))\n'
    'B = ("""\n'
    'def shown_again():\n'
    '    pass\n'
)

CLEAN = (
    '"""A study with a closed single-line docstring."""\n'
    'import json\n'
    '\n'
    'def load_b():\n'
    '    return json.load(open("results/x/BAR-2026-11-01.json"))\n'
)


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # L1/L2: the opener is a line that *starts* with a closing delimiter
    keep_sw, early_sw = token_code_lines(SWALLOWING)
    shown_sw = {n for n, _t in e326.code_lines(SWALLOWING)}
    raw = SWALLOWING.splitlines()
    hidden = sorted(n for n in keep_sw if n not in shown_sw)
    check("L1 the tokenizer sees the def the helper drops",
          any(raw[n - 1].strip().startswith("def load_a_pointer") for n in hidden), str(hidden))
    check("L2 the first hidden code line is the closing-delimiter line",
          first_hidden_code_line(SWALLOWING) == 7, str(first_hidden_code_line(SWALLOWING)))
    check("L3 a swallowed literal is not reported as an unterminated stream",
          early_sw is False, str(early_sw))

    # L4/L5: classification of what the tail holds
    kinds = {k: 0 for k in KINDS}
    for n in hidden:
        for k in classify(raw[n - 1].strip()):
            kinds[k] += 1
    check("L4 the hidden region holds two defs, two load-site lines and one selftest mention",
          (kinds[K_DEF], kinds[K_LOAD], kinds[K_LEG]) == (2, 2, 1), json.dumps(kinds))
    check("L5 a path literal inside the hidden def is a face handle",
          kinds[K_FACE] == 1, json.dumps(kinds))

    # L6: a file whose docstring closes on its own line recovers nothing
    root_c, files_c = _fx(CLEAN, "clean.py")
    rows_c = scan(files_c)
    check("L6 a single-line docstring recovers no code line", rows_c == [], str(rows_c)[:200])

    # L7: spans are contiguous runs, and this fixture has three of them
    spans = helper_blind_spans(SWALLOWING, shown_sw)
    check("L7 the hidden region is reported as contiguous spans",
          len(spans) == 3 and sum(s[2] for s in spans) == len(hidden), str(spans))

    # L8/L9: E331's tail metric cannot see a loss that the file's own end hides
    mid_shown = {n for n, _t in e326.code_lines(MIDFILE)}
    mid_tail = tail_is_invisible(MIDFILE, e326.code_lines(MIDFILE))
    keep_mid, _e = token_code_lines(MIDFILE)
    mid_hidden = sorted(n for n in keep_mid if n not in mid_shown)
    check("L8 the E331 tail metric reads zero on a mid-file loss",
          mid_tail == 0 and len(mid_hidden) > 0,
          "tail=%s hidden=%s" % (mid_tail, mid_hidden))
    check("L9 the mid-file recovery names the hidden def",
          any(MIDFILE.splitlines()[n - 1].strip().startswith("def load_mid") for n in mid_hidden),
          str(mid_hidden))

    # L10-L12: the re-pricing mechanism, on a corpus whose only pointer reader is hidden
    root_r = tempfile.mkdtemp(prefix="e332_fx_price_")
    mixed = SWALLOWING.replace("results/x/FOO-2026-11-01.json", "results/x/foo_latest.json")
    files_r = [(os.path.join(root_r, "tail.py"), mixed)]
    priced = reprice(files_r, root_r)
    check("L10 the re-pricing sees a reader that only exists in the recovered text",
          priced["delta"].get("pointer_only_readers") == 1,
          json.dumps(priced["delta"], ensure_ascii=False))
    check("L11 the re-pricing restores the shipped helper",
          e326.code_lines.__module__ == "e326_template_parameter_consumers",
          repr(e326.code_lines))
    check("L12 the shipped half of the same corpus reports zero readers",
          priced["with_shipped_helper"].get("pointer_only_readers") == 0,
          json.dumps(priced["with_shipped_helper"], ensure_ascii=False))

    # L13/L14: verdict rules fire on their own evidence
    doc_tail = build(root=root_r, outdir=tempfile.mkdtemp(prefix="e332_fx_v_"), files=files_r)
    check("L13 a corpus with a hidden reader yields the floor verdict",
          doc_tail["verdict"] == V_FLOOR, doc_tail["verdict"])
    doc_clean = build(root=root_c, outdir=tempfile.mkdtemp(prefix="e332_fx_v2_"), files=files_c)
    check("L14 a corpus with nothing hidden yields the clean verdict",
          doc_clean["verdict"] == V_CLEAN and doc_clean["summary"]["sources_the_helper_blinds"] == 0,
          "%s %s" % (doc_clean["verdict"],
                     doc_clean["summary"]["sources_the_helper_blinds"]))

    # L15/L16: verify() rejects a zeroed count and accepts a fresh face
    out = tempfile.mkdtemp(prefix="e332_fx_pub_")
    pub = os.path.join(out, "results", "state_tilt")
    build(root=out, outdir=pub, files=files_r)
    path = os.path.join(pub, FACE)
    with io.open(path, encoding="utf-8") as fh:
        bad = json.load(fh)
    bad["summary"]["recovered_code_lines"] = 0
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(bad, fh, ensure_ascii=False)
    problems = verify(root=out, files=files_r)
    check("L15 verify catches a zeroed recovery count",
          any("broken measurement" in p for p in problems), str(problems)[:200])

    out2 = tempfile.mkdtemp(prefix="e332_fx_pub2_")
    build(root=out2, outdir=os.path.join(out2, "results", "state_tilt"), files=files_r)
    fresh_problems = verify(root=out2, files=files_r)
    check("L16 verify accepts a freshly built face", fresh_problems == [], str(fresh_problems)[:200])

    bads = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        if not ok:
            print("FAIL %s :: %s" % (name, detail))
    print("\n%d/%d passed" % (len(checks) - len(bads), len(checks)))
    return 0 if not bads else 1


# ---------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s = doc["summary"]
    print("%s | %s" % (doc["verdict"], STUDY))
    print("sources %(sources_scanned)s / blinded %(sources_the_helper_blinds)s / recovered lines "
          "%(recovered_code_lines)s" % s)
    print("by kind:", json.dumps(s["recovered_by_kind"], ensure_ascii=False))
    print("tails E331 counted: %(sources_whose_tail_is_invisible)s / blinded before their last "
          "line: %(sources_blinded_before_their_last_line)s / multi-span sources: "
          "%(sources_with_more_than_one_span)s" % s)
    print("re-pricing delta:", json.dumps(s["repricing_delta"], ensure_ascii=False))
    for row in doc["sources"][:12]:
        print("   - %-46s hidden=%4d spans=%d first_hidden=%s off_end=%d"
              % (row["source"], row["recovered_code_lines"], row["span_count"],
                 row["first_hidden_code_line"], row["dropped_from_the_end"]))
    for r in doc["repricing"]["readers_visible_only_in_the_recovered_text"][:10]:
        print("   + reader only in the tail: %s / %s" % (r["source"], r["family"]))
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        print("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    print("verify: 0 problems")
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))