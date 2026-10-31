"""E327 -- who reads a face through a pointer, and whether the parameter survives the indirection.

E326 closed with a hedge: "11 of the 20 parameterised faces are reachable through 143 *_latest
pointers whose readers never see a date in a file name" -- measured, not traversed.  This study
traverses that layer, and the first thing it finds is that most of it is not a pointer layer.

``e326.pointer_siblings`` asks one question of a sibling ``*latest*.json``: does the raw text
contain the face's basename?  Any census that lists the face under ``faces_censused`` /
``rows[].face`` / ``per_face[].face`` answers yes.  Those are *measurements of* the face, not
*pointers to* it.  So the pairs are classified before anything is read through them:

  POINTER_IDENTICAL  the pointer's parsed content equals the dated face (a copy, parameter and all)
  POINTER_SAME_STUDY the pointer is a copy of the same study at another vintage
  CITES_AS_INPUT     the face appears only in a provenance field (source_faces / upstream)
  MEASURED_SUBJECT   the face appears inside a census result -- not a pointer
  UNEXPLAINED        the basename is in the file and no key accounts for it

Only the two POINTER_* classes are read through.  For each of those, the reader side is measured
in the python corpus: who declares the pointer (its writer), who names it and surfaces the
parameter back out of it, and who names it and never does.

Everything is static tree analysis -- no panel, no engine, no network, no draws.

Usage:
    python scripts/e327_who_reads_a_face_through_a_pointer.py run|verify|selftest
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e326_template_parameter_consumers as e326  # noqa: E402  (path set above)

ROOT = e326.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "results/state_tilt/TEMPLATEPARAM-2026-10-31.json"
TODAY = "2026-11-01"
FACE = "POINTERREAD-%s.json" % TODAY
LATEST = "pointerread_latest.json"
STUDY = "E327_who_reads_a_face_through_a_pointer"

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
PARAM_READ = re.compile(r"\[\s*[\"'](evidence_cutoff|cutoff|as_of|asof|as_of_bar)[\"']\s*\]|"
                        r"\.get\(\s*[\"'](evidence_cutoff|cutoff|as_of|asof|as_of_bar)[\"']", re.I)
WRITE_HINT = re.compile(r"(json\.dump|\.write\(|utf-8[\"']?\s*,\s*[\"']w)", re.I)

PROVENANCE_LEAVES = ("source_faces", "upstream", "upstream_study", "inputs", "consumed",
                     "parent_face", "source")

P_IDENTICAL = "POINTER_IDENTICAL"
P_SAME_STUDY = "POINTER_SAME_STUDY"
P_CITES = "CITES_AS_INPUT"
P_SUBJECT = "MEASURED_SUBJECT"
P_UNEXPLAINED = "UNEXPLAINED"
PAIR_CLASSES = (P_IDENTICAL, P_SAME_STUDY, P_CITES, P_SUBJECT, P_UNEXPLAINED)
POINTER_CLASSES = (P_IDENTICAL, P_SAME_STUDY)

C_WRITER = "this_source_declares_the_pointer"
C_READS_PARAM = "consumer_surfaces_the_parameter_out_of_the_pointer"
C_READS_ONLY = "consumer_names_the_pointer_and_never_shows_the_parameter"
CONSUMER_CLASSES = (C_WRITER, C_READS_PARAM, C_READS_ONLY)

VERDICT_SURVIVES = ("the_parameter_survives_one_indirection_and_every_reader_of_a_real_pointer_"
                    "either_writes_it_or_reads_its_cutoff_back")
VERDICT_READ_ONLY = ("the_parameter_survives_one_indirection_in_content_but_some_reader_quotes_"
                     "the_pointer_without_surfacing_the_cutoff")
VERDICT_LOST = "a_reader_opens_a_pointer_whose_content_does_not_carry_the_parameter_it_names"
VERDICT_NO_POINTER = "no_parameterised_face_in_the_population_is_reached_by_a_real_pointer"


def read_json(rel_path, root=None):
    with io.open(os.path.join(root or ROOT, rel_path), encoding="utf-8") as fh:
        return json.load(fh)


def relp(path):
    return path.replace("\\", "/") if not os.path.isabs(path) else e326.relp(path)


_SRC = None


def corpus():
    """E326's python corpus minus this scanner (r1232/E204 self-inclusion trap)."""
    global _SRC
    if _SRC is None:
        own = os.path.abspath(__file__)
        _SRC = [(p, s) for p, s in e326.corpus() if os.path.abspath(p) != own]
    return _SRC


def study_of(doc):
    if not isinstance(doc, dict):
        return None
    for key in ("study", "study_id", "id"):
        if isinstance(doc.get(key), str):
            return doc[key]
    return None


def where_named(node, base, prefix="", depth=0, out=None):
    """Every key path that mentions the basename.

    No list cap, no early stop: a walk truncated for display reclassifies rows silently (the
    first draft of this study capped lists at 8 items and "found" 109 pairs with no link at all).
    """
    out = [] if out is None else out
    if depth > 12:
        return out
    if isinstance(node, dict):
        items = list(node.items())
        for key, value in items:
            path = ("%s.%s" % (prefix, key)) if prefix else str(key)
            if isinstance(value, str):
                if base in value:
                    out.append(path)
            elif isinstance(value, (dict, list)):
                where_named(value, base, path, depth + 1, out)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            path = "%s[%d]" % (prefix, index)
            if isinstance(value, str):
                if base in value:
                    out.append(path)
            elif isinstance(value, (dict, list)):
                where_named(value, base, path, depth + 1, out)
    return out


def kind_from_keys(keys):
    leaves = {k.split("[")[0].split(".")[-1] for k in keys}
    if not keys:
        return P_UNEXPLAINED
    if leaves <= set(PROVENANCE_LEAVES + ("study",)):
        return P_CITES
    return P_SUBJECT


def pointer_kind(pointer_doc, face_doc, basename):
    """Pointer, citation or measurement -- decided from parsed content, not from a substring."""
    if pointer_doc is None:
        return P_UNEXPLAINED, []
    keys = where_named(pointer_doc, basename)
    if pointer_doc == face_doc:
        return P_IDENTICAL, keys
    pstudy, fstudy = study_of(pointer_doc), study_of(face_doc)
    if pstudy and fstudy and pstudy == fstudy:
        return P_SAME_STUDY, keys
    return kind_from_keys(keys), keys


def consumers_of(pointer_rel, files=None):
    base = os.path.basename(pointer_rel)
    out = []
    for path, src in (files if files is not None else corpus()):
        rel = relp(path)
        lines = [(n, t) for n, t in e326.code_lines(src) if base in t]
        if not lines:
            continue
        # a writer is not "a source that also writes something": it binds the pointer's basename
        # to a name and then dumps that name (or opens the literal for writing).
        bound = set()
        for _n, text in lines:
            match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", text)
            if match:
                bound.add(match.group(1))
        code = e326.code_lines(src)
        writes = [t for _n, t in code
                  if any(re.search(r"\b%s\b" % re.escape(name), t) for name in bound)
                  and re.search(r"(json\.dump|\.write\(|[\"']w[\"'])", t)]
        writes += [t for _n, t in lines if re.search(r"[\"']w[\"']", t)]
        if writes:
            cls, why = C_WRITER, "this source binds the pointer's name and writes to it"
        elif any(PARAM_READ.search(t) for _n, t in code):
            cls, why = C_READS_PARAM, "the source names the pointer and subscripts a cutoff key"
        else:
            cls, why = C_READS_ONLY, "the source names the pointer and never surfaces its cutoff"
        lineno, text = lines[0]
        out.append({"source": rel, "line": lineno, "text": text[:160],
                    "class": cls, "why": why, "lines_naming_the_pointer": len(lines)})
    return sorted(out, key=lambda c: (c["class"], c["source"]))


def pair_record(face, pointer, files=None):
    base = os.path.basename(face)
    try:
        pdoc = read_json(pointer)
    except Exception:
        pdoc = None
    try:
        fdoc = read_json(face)
    except Exception:
        fdoc = None
    kind, keys = pointer_kind(pdoc, fdoc, base)
    token = DATE.search(base).group(0) if DATE.search(base) else None
    cutoff = pdoc.get("evidence_cutoff") if isinstance(pdoc, dict) else None
    rec = {
        "pointer": relp(pointer),
        "target": face,
        "kind": kind,
        "keys_naming_the_target": keys[:6],
        "keys_naming_the_target_count": len(keys),
        "pointer_study": study_of(pdoc),
        "target_study": study_of(fdoc),
        "pointer_evidence_cutoff": cutoff,
        "target_parameter_token": token,
        "pointer_carries_the_parameter": bool(cutoff) and (cutoff == token or
                                                           str(cutoff) == str(token)),
        "is_a_pointer": kind in POINTER_CLASSES,
    }
    rec["consumers"] = consumers_of(pointer, files) if rec["is_a_pointer"] else []
    counts = {}
    for c in rec["consumers"]:
        counts[c["class"]] = counts.get(c["class"], 0) + 1
    rec["consumer_classes"] = counts
    return rec


def population(upstream):
    """E326's own published face list, filtered to the faces that carry a parameter.

    Reading the published face (not re-deriving it from E325) keeps this study honest about what
    upstream actually claimed: the population is theirs, the pointer layer is mine.
    """
    out = []
    for rec in upstream.get("faces") or []:
        param = rec.get("parameter") or {}
        if param.get("kind") and param.get("kind") != "none":
            out.append(rec["face"])
    return sorted(out)


def build(outdir=None):
    upstream = read_json(INPUT)
    faces = population(upstream)
    files = corpus()
    pairs = []
    own_faces = {FACE, LATEST}
    for face in faces:
        for pointer in e326.pointer_siblings(face):
            # this study publishes a face that spells every pointer it found; keeping it in the
            # sibling scan would make the population grow with each run (E204 self-inclusion).
            if os.path.basename(pointer) in own_faces:
                continue
            pairs.append(pair_record(face, pointer, files))
    counts = {}
    for p in pairs:
        counts[p["kind"]] = counts.get(p["kind"], 0) + 1
    real = [p for p in pairs if p["is_a_pointer"]]
    pointer_files = sorted({p["pointer"] for p in real})
    faces_with_pointer = sorted({p["target"] for p in real})
    consumers = [c for p in real for c in p["consumers"]]
    ccounts = {}
    for c in consumers:
        ccounts[c["class"]] = ccounts.get(c["class"], 0) + 1
    lost = [p for p in real if not p["pointer_carries_the_parameter"]]
    silent_readers = [c for c in consumers if c["class"] == C_READS_ONLY]
    claimed = ((upstream.get("summary") or {})
               .get("faces_reachable_through_a_latest_pointer"))
    claimed_pointers = ((upstream.get("summary") or {})
                        .get("latest_pointers_naming_a_parameterised_face"))
    non_pointers = [p for p in pairs if p["kind"] in (P_CITES, P_SUBJECT, P_UNEXPLAINED)]

    if not real:
        verdict = VERDICT_NO_POINTER
        reason = ("none of the %d pairs is a pointer: %d are citations or census subjects"
                  % (len(pairs), len(non_pointers)))
    elif lost:
        verdict = VERDICT_LOST
        reason = ("%d of %d real pointers do not carry the parameter they name -- a reader of "
                  "those sees a file called latest and nothing else" % (len(lost), len(real)))
    elif silent_readers:
        verdict = VERDICT_READ_ONLY
        reason = ("all %d real pointers carry the parameter in content, but %d of %d consumer "
                  "sources name a pointer and never surface its cutoff"
                  % (len(real), len(silent_readers), len(consumers)))
    else:
        verdict = VERDICT_SURVIVES
        reason = ("all %d real pointers are full copies carrying evidence_cutoff, and all %d "
                  "consumer sources either write the pointer or read its cutoff back"
                  % (len(real), len(consumers)))

    out = {
        "study": STUDY,
        "title": ("who reads a parameterised face through a *_latest pointer, and whether the "
                  "parameter survives the indirection"),
        "evidence_cutoff": TODAY,
        "upstream": os.path.basename(INPUT),
        "corpus": {"files": len(files), "self_excluded": os.path.basename(__file__)},
        "rules": {
            "population": "every sibling *latest*.json E326's helper returns for a parameterised face",
            "pointer": ("the pointer's parsed content equals the dated face, or is a copy of the "
                        "same study at another vintage -- decided on content, never on substring"),
            "citation": "the face appears only under a provenance key (source_faces/upstream/inputs)",
            "measured_subject": "the face appears inside a census result, which measures it",
            P_UNEXPLAINED: "the basename is present and no key accounts for it (must be 0)",
            C_WRITER: "the source writes the pointer file",
            C_READS_PARAM: "the source names the pointer and subscripts a cutoff key",
            C_READS_ONLY: "the source names the pointer and never surfaces the cutoff",
        },
        "held_fixed": ("E326's population, every upstream face class and every upstream row is "
                       "read and never rewritten; only the pointer layer is measured here"),
        "limits": ("static analysis of the python corpus in scripts/Tools/live/monitor/firm, so a "
                   "reader that resolves a pointer through a computed name is not seen; a pointer "
                   "whose content diverges from its dated face in a way neither equality nor "
                   "study identity catches would land in the census classes and be under-counted"),
        "no_bill": "published faces and in-repo sources only; no draws, no panel, no engine, no network",
        "summary": {
            "faces_in_population": len(faces),
            "pairs": len(pairs),
            "pairs_by_class": {k: counts.get(k, 0) for k in PAIR_CLASSES},
            "real_pointers": len(real),
            "distinct_pointer_files": len(pointer_files),
            "faces_with_a_real_pointer": len(faces_with_pointer),
            "pairs_that_are_not_pointers": len(non_pointers),
            "overcount_factor": round(100.0 * len(pairs) / max(1, len(real)), 2),
            "real_pointers_carrying_the_parameter": len(real) - len(lost),
            "real_pointers_that_do_not_carry_it": len(lost),
            "consumers": len(consumers),
            "consumers_by_class": {k: ccounts.get(k, 0) for k in CONSUMER_CLASSES},
            "readers_that_do_not_surface_the_cutoff": len(silent_readers),
            "upstream_claimed_faces_reachable_through_a_pointer": claimed,
            "upstream_claimed_pointers_naming_a_face": claimed_pointers,
            "delta_faces_vs_upstream": (claimed - len(faces_with_pointer)
                                        if isinstance(claimed, int) else None),
            "delta_pointers_vs_upstream": (claimed_pointers - len(pairs)
                                           if isinstance(claimed_pointers, int) else None),
        },
        "faces_with_a_real_pointer": faces_with_pointer,
        "pointer_files": pointer_files,
        "pairs_that_are_not_pointers": [
            {"pointer": p["pointer"], "target": p["target"], "kind": p["kind"],
             "keys_naming_the_target": p["keys_naming_the_target"][:3]}
            for p in non_pointers],
        "pairs": pairs,
        "verdict": verdict,
        "verdict_reason": reason,
    }
    if outdir:
        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)
        body = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        for name in (FACE, LATEST):
            with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
    return out


def cmd_run():
    out = build(OUTDIR)
    s = out["summary"]
    print("E327 pointer layer of %d parameterised faces (%d in-repo sources)"
          % (s["faces_in_population"], out["corpus"]["files"]))
    print("  pairs %d -> real pointers %d (%d distinct files, %d faces) | not pointers %d"
          % (s["pairs"], s["real_pointers"], s["distinct_pointer_files"],
             s["faces_with_a_real_pointer"], s["pairs_that_are_not_pointers"]))
    print("  pairs by class:", json.dumps(s["pairs_by_class"], ensure_ascii=False))
    print("  over-count factor: %s x" % s["overcount_factor"])
    print("  real pointers carrying the parameter: %d / %d (missing %d)"
          % (s["real_pointers_carrying_the_parameter"], s["real_pointers"],
             s["real_pointers_that_do_not_carry_it"]))
    print("  consumers by class:", json.dumps(s["consumers_by_class"], ensure_ascii=False))
    print("  upstream claimed %s faces / %s pointers -> this study %d / %d (delta %s / %s)"
          % (s["upstream_claimed_faces_reachable_through_a_pointer"],
             s["upstream_claimed_pointers_naming_a_face"], s["faces_with_a_real_pointer"],
             s["pairs"], s["delta_faces_vs_upstream"], s["delta_pointers_vs_upstream"]))
    for p in out["pairs"]:
        if p["is_a_pointer"]:
            print("   - %-40s <- %s  cutoff=%s  consumers=%s"
                  % (os.path.basename(p["pointer"]), os.path.basename(p["target"]),
                     p["pointer_evidence_cutoff"],
                     json.dumps(p["consumer_classes"], ensure_ascii=False)))
    print("verdict:", out["verdict"])
    print("reason:", out["verdict_reason"])
    return 0


def cmd_verify():
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        print("verify: face missing:", FACE)
        return 2
    on_disk = read_json(os.path.join("results", "state_tilt", FACE))
    fresh = build(None)
    problems = []
    for key in ("verdict", "verdict_reason"):
        if on_disk.get(key) != fresh.get(key):
            problems.append("%s on disk %r != %r" % (key, on_disk.get(key), fresh.get(key)))
    for key, value in fresh["summary"].items():
        got = (on_disk.get("summary") or {}).get(key)
        if got != value:
            problems.append("summary.%s %r != %r" % (key, got, value))
    a = {(p["pointer"], p["target"]): p["kind"] for p in on_disk.get("pairs") or []}
    b = {(p["pointer"], p["target"]): p["kind"] for p in fresh["pairs"]}
    if a != b:
        moved = [k for k in b if a.get(k) != b[k]]
        problems.append("pair classes drifted on %d pair(s): %s" % (len(moved), moved[:3]))
    if fresh["summary"]["pairs_by_class"][P_UNEXPLAINED]:
        problems.append("%d pair(s) are unexplained by any key"
                        % fresh["summary"]["pairs_by_class"][P_UNEXPLAINED])
    if problems:
        print("verify: %d problem(s)" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("verify: problems=[] (%d pairs, %d real pointers, %d consumers)"
          % (fresh["summary"]["pairs"], fresh["summary"]["real_pointers"],
             fresh["summary"]["consumers"]))
    return 0


def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print("  %-66s %s%s" % (name, "PASS" if ok else "FAIL",
                                ("  " + detail) if (detail and not ok) else ""))

    face_doc = {"study": "E9_x", "evidence_cutoff": "2026-10-29", "rows": [{"a": 1}]}
    base = "BANDDEFLATE-2026-10-29.json"

    # L1 a census that lists the face is not a pointer to it
    census = {"study": "E281_census", "faces_censused": ["results/x/" + base]}
    kind, keys = pointer_kind(census, face_doc, base)
    check("L1 a census listing the face is not a pointer", kind == P_SUBJECT, str((kind, keys)))

    # L2 a full copy is a pointer
    kind2, _ = pointer_kind(dict(face_doc), face_doc, base)
    check("L2 a content-identical sibling is a pointer", kind2 == P_IDENTICAL, kind2)

    # L3 the same study at another vintage is a pointer
    kind3, _ = pointer_kind({"study": "E9_x", "evidence_cutoff": "2026-10-28"}, face_doc, base)
    check("L3 the same study at another vintage is a pointer", kind3 == P_SAME_STUDY, kind3)

    # L4 a provenance citation is a citation
    kind4, _ = pointer_kind({"study": "E300_other", "source_faces": [base]}, face_doc, base)
    check("L4 a source_faces citation is not a pointer", kind4 == P_CITES, kind4)

    # L5 the walk is not capped for display (the defect the first draft shipped)
    deep = {"study": "E300_other", "rows": [{"face": "f%d" % i} for i in range(39)] + [{"face": base}]}
    kind5, keys5 = pointer_kind(deep, face_doc, base)
    check("L5 a mention past any display cap is still found", kind5 == P_SUBJECT and keys5,
          str((kind5, keys5[:2])))

    # L6 a name that is genuinely absent is unexplained, not silently 'not a pointer'
    kind6, _ = pointer_kind({"study": "E300_other", "x": "nothing here"}, face_doc, base)
    check("L6 an absent name is UNEXPLAINED rather than a clean classification",
          kind6 == P_UNEXPLAINED, kind6)

    # L7 the live population leaves nothing unexplained
    live = build(None)
    check("L7 no pair in the live population is unexplained",
          live["summary"]["pairs_by_class"][P_UNEXPLAINED] == 0,
          str(live["summary"]["pairs_by_class"]))

    # L8 real pointers are exactly the POINTER_* rows, and the counts agree
    s = live["summary"]
    expect_real = (s["pairs_by_class"][P_IDENTICAL] + s["pairs_by_class"][P_SAME_STUDY])
    check("L8 real_pointers equals the pointer-class rows",
          s["real_pointers"] == expect_real and s["pairs"] == sum(s["pairs_by_class"].values()),
          str((s["real_pointers"], expect_real)))

    # L9 the over-count is published as a number, not prose
    check("L9 the non-pointer share is published as a count and a factor",
          s["pairs_that_are_not_pointers"] == s["pairs"] - s["real_pointers"]
          and s["overcount_factor"] > 0, str(s["pairs_that_are_not_pointers"]))

    # L10 upstream claims are read from the face, and the delta is published
    check("L10 the upstream claim is machine-read and a delta published",
          "upstream_claimed_pointers_naming_a_face" in s and "delta_pointers_vs_upstream" in s,
          str(list(s)[:4]))

    # L11 determinism
    a, b = build(None), build(None)
    check("L11 two builds agree on summary and verdict",
          a["summary"] == b["summary"] and a["verdict"] == b["verdict"])

    # L12 the verdict is inside the frozen set and matches the finding
    check("L12 verdict is one of the frozen four", a["verdict"] in (
        VERDICT_SURVIVES, VERDICT_READ_ONLY, VERDICT_LOST, VERDICT_NO_POINTER), a["verdict"])

    # L13 a pointer that does not carry the parameter is never called 'survives'
    saved = globals()["pair_record"]

    def fake_pair(face, pointer, files=None):
        return {"pointer": pointer, "target": face, "kind": P_IDENTICAL, "is_a_pointer": True,
                "keys_naming_the_target": [], "keys_naming_the_target_count": 0,
                "pointer_study": None, "target_study": None,
                "pointer_evidence_cutoff": None, "target_parameter_token": "2026-10-29",
                "pointer_carries_the_parameter": False, "consumers": [],
                "consumer_classes": {}}
    globals()["pair_record"] = fake_pair
    try:
        lost = build(None)
    finally:
        globals()["pair_record"] = saved
    check("L13 a pointer without the parameter cannot be called 'survives'",
          lost["verdict"] == VERDICT_LOST, lost["verdict"])

    # L14 this scanner is excluded from its own corpus
    own = os.path.abspath(__file__)
    check("L14 this scanner is excluded from its own corpus",
          all(os.path.abspath(p) != own for p, _s in corpus()))

    # L15 a writer is classified as a writer, not as a silent reader
    fixture = [("C:/fake/scripts/w.py",
                'LATEST = "banddeflate_latest.json"\njson.dump(d, open(LATEST, "w"))\n')]
    cons = consumers_of("results/state_tilt/banddeflate_latest.json", fixture)
    check("L15 a source that writes the pointer is a writer",
          len(cons) == 1 and cons[0]["class"] == C_WRITER, str(cons))

    # L16 a reader that surfaces the cutoff is not a silent reader
    fixture2 = [("C:/fake/scripts/r.py",
                 'U = "gateoperands_latest.json"\np = load(U)\nprint(p["evidence_cutoff"])\n')]
    cons2 = consumers_of("results/state_tilt/gateoperands_latest.json", fixture2)
    check("L16 a reader that shows the cutoff is not a silent reader",
          len(cons2) == 1 and cons2[0]["class"] == C_READS_PARAM, str(cons2))

    passed = sum(1 for _n, ok, _d in checks if ok)
    print("selftest: %d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


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