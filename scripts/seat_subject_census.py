"""Are the 252 out-of-scope ADMIT faces seats, or books wearing a seat shape?

event_exec_gate.audit already keeps a book out of the seat pile by looking for book
words.  r1741 left the obvious hole open: a word list is a claim about vocabulary, not
about subject, so a face that spells its holdings "holdings" instead of "positions"
rides a seat shape straight past the audit.  This face asks the same 252 the question
that cannot be answered by renaming a field -- does a seat shape actually exist (integer
ledger + wave tail + a band that parses as two ordered numbers) and does any shape that
can only belong to a book exist (a price series, or per-name rows spelled outside seat
vocabulary) -- and then answers, per face, on the shapes.

It also publishes the falsifier: four synthetic faces that carry every seat mark and a
book, on which the word list is blind (0/4) and the shape test is not (4/4).  A gate
whose evidence is a word list cannot show that number; this one can.

Reuse, not rewrite: the seat marks, the ADMIT reader and the shape readers all come
from event_exec_gate (import), so the audit and this census cannot disagree about what a
seat looks like.

    python scripts\\seat_subject_census.py run       census + page
    python scripts\\seat_subject_census.py selftest  offline fixtures
"""

import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import event_exec_gate as EG  # noqa: E402  seat marks + shape readers, one implementation

ROOT = EG.ROOT
OUT = os.path.join(ROOT, "results", "seat_subject_census.json")
MD = os.path.join(ROOT, "research", "SEAT_SUBJECT_CENSUS.md")
AUDIT = EG.AUDIT_OUT


def _faces(rdir=None):
    rdir = rdir or os.path.join(ROOT, "results")
    for name in sorted(os.listdir(rdir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(rdir, name)
        try:
            if os.path.getsize(path) > 8 * 1024 * 1024:
                continue
            with io.open(path, encoding="utf-8") as f:
                face = json.load(f)
        except Exception:
            continue
        if isinstance(face, dict):
            yield path, face


def census(rdir=None):
    """Every unpriced ADMIT face, sorted into seat / registration / book by shape."""
    seat, lookalike, registration, book = [], [], [], []
    conf = {"shape_book_words_seat": [], "words_book_shape_seat": []}
    scanned = admits = priced = 0
    for path, face in _faces(rdir):
        scanned += 1
        if not EG._claims_admission(face):
            continue
        admits += 1
        # A face that already shows its next-open entry and both sides of cost is not a
        # subject question: the audit's gate is about admissions that never priced.
        if EG._priced(face):
            priced += 1
            continue
        txt = json.dumps(face, ensure_ascii=False).lower()
        words = any(k in txt for k in EG.BOOK_KEYS)
        subj = EG.seat_subject(face)
        marks = EG._is_protocol_seat_face(face)
        row = {"file": EG._display_path(path), "verdict": face.get("verdict"),
               "subject": EG._subject_brief(subj), "why": subj["why"]}
        if subj["verdict"] == "seat":
            seat.append(row)
            if words:
                conf["words_book_shape_seat"].append(row["file"])
        elif marks:
            lookalike.append(dict(row, marks=marks))
            if not words:
                conf["shape_book_words_seat"].append(row["file"])
        elif any(k in face for k in EG.REGISTRATION_KEYS):
            # A seed entering a trial is not a book and not a seat; the audit names it
            # apart (published_registration), so this census does too.
            registration.append(row)
        else:
            book.append(row)
            if not words:
                conf["shape_book_words_seat"].append(row["file"])
    seat_bands = [r["subject"]["band_edges_ordered"] for r in seat]
    tiers = {"probe": sum(1 for r in seat if os.path.basename(r["file"]).startswith("_")),
             "published": sum(1 for r in seat
                              if not os.path.basename(r["file"]).startswith("_"))}
    audit_view = {}
    try:
        with io.open(AUDIT, encoding="utf-8") as f:
            rep = json.load(f)
        audit_view = {
            "protocol_seats": (rep.get("out_of_scope") or {}).get("protocol_seats"),
            "protocol_seats_subject_confirmed": (rep.get("out_of_scope") or {}).get(
                "protocol_seats_subject_confirmed"),
            "seat_shapes_reported_as_trading": (rep.get("out_of_scope") or {}).get(
                "seat_shapes_reported_as_trading"),
            "asof": rep.get("asof"),
        }
    except Exception:
        audit_view = {"error": "results/event_exec_gate_audit.json unreadable"}
    return {
        "face": "seat_subject_census",
        "scanned": scanned,
        "claiming_admission": admits,
        "admissions_already_priced": priced,
        "seat_classified": len(seat),
        "seat_by_tier": tiers,
        "seat_subject_confirmed": len(seat),
        "seat_lookalikes": len(lookalike),
        "registration_gates": len(registration),
        "book_faces": len(book),
        "seat_band_edges": {"min": min(seat_bands) if seat_bands else 0,
                            "max": max(seat_bands) if seat_bands else 0,
                            "faces_with_ordered_band": sum(1 for b in seat_bands if b)},
        "seat_curves": sum(r["subject"]["curves"] for r in seat),
        "seat_row_lists_not_seat": sum(r["subject"]["row_lists_not_seat"] for r in seat),
        "seat_ledger_present": sum(1 for r in seat if r["subject"]["ledger"]),
        "word_list_vs_shape": {
            # Where the two readings disagree, the shape reading is the one that can be
            # checked without knowing what the field was called.
            "shape_book_words_seat": conf["shape_book_words_seat"],
            "words_book_shape_seat": conf["words_book_shape_seat"],
            "disagreements": len(conf["shape_book_words_seat"])
                             + len(conf["words_book_shape_seat"]),
        },
        "lookalikes": lookalike[:12],
        "book_detail": book[:12],
        "registration_detail": registration[:12],
        "audit_face": audit_view,
        "rule": {
            "seat_needs": "integer ledger rows + wave tail, >=1 ordered band edge",
            "book_shapes_veto": "a %d-point numeric series, or >=3 rows whose keys are "
                                "not seat words" % EG.CURVE_MIN_POINTS,
            "seat_vocabulary_is_a_boundary_not_a_proof": True,
        },
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def _md(rep, falsifier):
    L = []
    L.append("# Seat faces: is \"not a position\" a measurement, or a word list?")
    L.append("")
    L.append("Evidence: `results/` as it stands, generated %s by "
             "`scripts\\seat_subject_census.py`." % rep["asof"])
    L.append("")
    L.append("## Verdict")
    L.append("")
    verdict = ("**SEAT_SUBJECT_CONFIRMED**" if not rep["seat_lookalikes"]
               else "**SEAT_SHAPES_FOUND_AMONG_SEATS**")
    L.append("%s -- %d of %d seat-classified ADMIT faces carry the shapes of a seat and "
             "none of the shapes of a book; %d wear a seat shape while describing a book."
             % (verdict, rep["seat_subject_confirmed"], rep["seat_classified"],
                rep["seat_lookalikes"]))
    L.append("")
    L.append("## What was asked, and what came back")
    L.append("")
    L.append("| question | evidence the face had to show | faces that showed it |")
    L.append("|---|---|---|")
    L.append("| is there a seat ledger? | integer `rows` + a `W<n>` wave tail | %d / %d |"
             % (rep["seat_ledger_present"], rep["seat_classified"]))
    L.append("| is there a band? | a `lo..hi` pair that parses as two numbers, lo <= hi "
             "(the thinnest face carries %d, the widest %d) | %d / %d |"
             % (rep["seat_band_edges"]["min"], rep["seat_band_edges"]["max"],
                rep["seat_band_edges"]["faces_with_ordered_band"], rep["seat_classified"]))
    L.append("| does anything carry a price series? | a >=%d-point numeric list under any "
             "field name | %d found |" % (EG.CURVE_MIN_POINTS, rep["seat_curves"]))
    L.append("| do any rows describe names rather than seats? | >=3 rows whose keys are "
             "not seat words | %d found |" % rep["seat_row_lists_not_seat"])
    L.append("")
    L.append("The %d unpriced admissions split by shape into %d seats (all %d probe-tier, "
             "%d published), %d registration gates, %d book claims and %d face(s) that wear "
             "a seat shape while describing a book."
             % (rep["claiming_admission"] - rep["admissions_already_priced"],
                rep["seat_classified"], rep["seat_by_tier"]["probe"],
                rep["seat_by_tier"]["published"], rep["registration_gates"],
                rep["book_faces"], rep["seat_lookalikes"]))
    L.append("")
    L.append("## The word list is not the proof")
    L.append("")
    L.append("Four synthetic faces carry every seat mark **and** a book -- one spelled "
             "`holdings`, one as a 30-point `book_path`, one whose band is prose instead "
             "of numbers, one whose band runs backwards. The word list `BOOK_KEYS` sees "
             "**%d/%d** of them; the shape test sees **%d/%d** "
             "(`scripts\\event_exec_gate.py selftest-audit`, legs L20-L23)."
             % (falsifier["words_caught"], falsifier["n"], falsifier["shapes_caught"],
                falsifier["n"]))
    L.append("")
    w = rep["word_list_vs_shape"]
    L.append("On this tree's own unpriced admissions the two readings disagree on **%d** "
             "face(s): %d where the shape test finds a book the word list never sees, %d "
             "the other way. %s"
             % (w["disagreements"], len(w["shape_book_words_seat"]),
                len(w["words_book_shape_seat"]),
                "That is the whole claim: the seats are out of scope because their shapes "
                "say so, not because nobody wrote `positions`." if not w["disagreements"]
                else "Named: " + ", ".join(os.path.basename(p) for p in
                                           (w["shape_book_words_seat"] + w["words_book_shape_seat"])[:6])))
    L.append("")
    L.append("## Honest")
    L.append("")
    L.append("- The test is shape-level, not semantic. A book that held only a four-name "
             "list spelled with seat words (`{\"hop\": ...}`) would still pass; today no "
             "face does, but the vocabulary is a boundary, not a proof.")
    L.append("- \"No curve\" cannot see a book whose price series is stored as one scalar "
             "per bar in separate fields; nothing in this tree does that today.")
    L.append("- The seat family is %d probe faces and %d published faces: these are "
             "research waves admitting a parameter band, not products."
             % (rep["seat_by_tier"]["probe"], rep["seat_by_tier"]["published"]))
    L.append("- `seat_lookalikes` counts faces the audit's marks call a seat and this "
             "census reads as a book; it is the disagreement number, not a second opinion "
             "on the same question.")
    L.append("- The census reads the same live `results/` the audit walks, so the two "
             "numbers move together by construction; the agreement is reported, not "
             "counted as independent confirmation.")
    return "\n".join(L) + "\n"


def run(write=True):
    rep = census()
    falsifier = _falsifier_tally()
    rep["falsifier"] = falsifier
    if write:
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rep, ensure_ascii=False, indent=2))
        with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(_md(rep, falsifier))
    print(json.dumps({"claiming_admission": rep["claiming_admission"],
                      "seat_classified": rep["seat_classified"],
                      "seat_lookalikes": rep["seat_lookalikes"],
                      "registration_gates": rep["registration_gates"],
                      "book_faces": rep["book_faces"],
                      "word_list_disagreements":
                          rep["word_list_vs_shape"]["disagreements"],
                      "falsifier": falsifier}, ensure_ascii=False))
    return 0


def _falsifier_tally():
    """The numbers the page quotes, taken from the gate's own selftest, not typed here."""
    import subprocess
    out = subprocess.run([sys.executable, os.path.join(HERE, "event_exec_gate.py"),
                          "selftest-audit"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    line = [l for l in (out.stdout or "").splitlines() if "seat-subject selftest" in l]
    tally = {"words_caught": None, "shapes_caught": None, "n": None, "rc": out.returncode}
    if line:
        import re
        m = re.search(r"words (\d+)/(\d+), shapes (\d+)/(\d+)", line[0])
        if m:
            tally.update(words_caught=int(m.group(1)), n=int(m.group(2)),
                         shapes_caught=int(m.group(3)))
    return tally


def selftest():
    import tempfile
    ok = total = 0

    def chk(cond, name):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL", name)

    seat = {"face": "s", "verdict": "ADMIT", "legs": {
        "leg0": {"rows": 10, "tail": "W9", "ordinal": 9},
        "leg1": {"A": "1_000..1_199"},
        "leg2": {"conflicts": [], "vacant_on_origin": True}}}
    hidden = {"face": "h", "verdict": "ADMIT", "legs": seat["legs"],
              "holdings": [{"ticker": "x", "qty": 1, "px": 2}] * 3}
    priced = {"face": "p", "verdict": "TRADABLE",
              "execution": {"entry_convention": "next_open"}}
    with tempfile.TemporaryDirectory() as d:
        for name, payload in (("a_seat.json", seat), ("b_hidden.json", hidden),
                              ("c_priced.json", priced)):
            with io.open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(json.dumps(payload))
        rep = census(d)
    chk(rep["claiming_admission"] == 3 and rep["admissions_already_priced"] == 1,
        "L1 admissions are read, and the one that already priced is named apart")
    chk(rep["seat_classified"] == 1, "L1 an honest seat is counted as a seat")
    chk(rep["seat_lookalikes"] == 1, "L2 a renamed holdings block is a lookalike, not a seat")
    chk([os.path.basename(p)
         for p in rep["word_list_vs_shape"]["shape_book_words_seat"]]
        == ["b_hidden.json"],
        "L2 the word list is blind to it and the census says so by name")
    chk(rep["seat_curves"] == 0 and rep["seat_row_lists_not_seat"] == 0,
        "L3 the seat pile contributes no book shapes")
    falsifier = _falsifier_tally()
    chk(falsifier["words_caught"] == 0 and falsifier["shapes_caught"] == falsifier["n"]
        and falsifier["n"], "L4 the falsifier tally is read from the gate, not typed")
    print("seat-subject census selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
