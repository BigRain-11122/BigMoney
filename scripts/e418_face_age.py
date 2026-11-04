"""E418 - how old are the faces nothing can turn red on, and does their green sentence decay?

E416 published 45 faces with no reader that can go red on age and no writer on the round
chain. This study prices each of them:

  * the stamp field the face carries and its age in trading bars against
    data/exchange_calendar.csv,
  * every leg that reads it, and the sentence that leg prints when green,
  * whether that sentence names a number that could only have been true at one cutoff
    (a frozen headline) or a property of the check (a tautology / recomputed at read).

Read-only: no reader is edited, no face is refreshed. The population comes from E411's
published rows (one row is added from E416's reclassification, and each row says which).

Usage:
    python scripts/e418_face_age.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "results", "state_tilt")
E411 = os.path.join(ST, "readertiers_latest.json")
E416 = os.path.join(ST, "freshaim_latest.json")
CAL = os.path.join(ROOT, "data", "exchange_calendar.csv")
SUITE = os.path.join(ROOT, "smoke_test.py")
OUTDIR = ST

STAMP_KEYS = [
    "evidence_cutoff", "as_of_bar", "as_of", "cutoff", "data_cutoff", "panel_cutoff",
    "session_open", "generated", "ts", "timestamp", "updated_at", "updated", "date",
]

# Frozen vocabularies: the smoke leg refuses a published value outside them.
V_DECAY = "decayed claim printed as green"
V_CLEAN = "no claim that decays"
V_NO_STAMP = "stamp absent so age is unknowable"
V_NO_DATE = "stamp present but not a readable date so age is unknowable"
VERDICT_VOCAB = {V_DECAY, V_CLEAN, V_NO_STAMP, V_NO_DATE}
C_FROZEN = "frozen_literal_number"
C_RECOMPUTED = "recomputed_at_read"
C_NONE = "no_number"
CLASS_VOCAB = {C_FROZEN, C_RECOMPUTED, C_NONE, "unresolved"}
# A digit run that is part of an identifier or a date is not a claim about a count.
NOT_A_NUMBER = re.compile(r"[A-Za-z_]\d+|\d{4}-\d{2}-\d{2}")


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_calendar() -> list[str]:
    out = []
    with io.open(CAL, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line or i == 0:
                continue
            out.append(line)
    return sorted(out)


def _as_date(value) -> str | None:
    if not isinstance(value, str):
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", value.strip())
    return m.group(0) if m else None


def stamp_of(obj, depth: int = 0) -> tuple[str, object] | tuple[None, None]:
    """First stamp-looking field, top level first, then one nested level (meta/summary)."""
    if not isinstance(obj, dict) or depth > 1:
        return (None, None)
    for key in STAMP_KEYS:
        if key in obj:
            return (key, obj[key])
    for key, val in obj.items():
        if isinstance(val, dict):
            found = stamp_of(val, depth + 1)
            if found[0]:
                return found
    return (None, None)


def age_bars(stamp: str | None, cutoff: str, bars: list[str]) -> int | None:
    if not stamp or stamp > cutoff:
        return None
    return sum(1 for b in bars if stamp < b <= cutoff)


def _call_text(lines: list[str], idx: int, back: int = 40, fwd: int = 60) -> tuple[int, str] | None:
    """The nearest check(...) call that contains/encloses line idx (0-based)."""
    start = None
    for i in range(idx, max(-1, idx - back) - 1, -1):
        if "check(" in lines[i]:
            start = i
            break
    if start is None:
        for i in range(idx, min(len(lines), idx + back)):
            if "check(" in lines[i]:
                start = i
                break
    if start is None:
        return None
    chunk = []
    bal = 0
    for i in range(start, min(len(lines), start + fwd)):
        line = lines[i]
        chunk.append(line)
        bal += line.count("(") - line.count(")")
        if bal <= 0 and i > start:
            break
    return (start + 1, "\n".join(chunk))


def sentence_class(text: str) -> str:
    """'frozen_literal_number' | 'recomputed_at_read' | 'no_number'.

    A number is recomputed at read when the sentence interpolates it: an f-string brace,
    or a %-placeholder filled by the call's tuple. A bare digit run in the literal is a
    frozen number - it can only have been true at the cutoff the author wrote it for.
    """
    literals = [a or b for a, b in re.findall(r"f\"([^\"]*)\"|f'([^']*)'", text)]
    if any("{" in lit or "%" in lit and re.search(r"%[sdrfi]", lit) for lit in literals):
        return "recomputed_at_read"
    plain = [a or b for a, b in re.findall(r"\"([^\"]*)\"|'([^']*)'", text)]
    if any(re.search(r"%[sdrfi]", lit) for lit in plain):
        return "recomputed_at_read"
    for cand in plain:
        masked = NOT_A_NUMBER.sub("", cand)
        if re.search(r"\d", masked):
            return "frozen_literal_number"
    return "no_number"


def green_sentence(face: str, row: dict, lines: list[str]) -> list[dict]:
    out = []
    for reader in row.get("readers") or []:
        block = (reader.get("evidence") or {}).get("block") or []
        if not block:
            continue
        idx = max(0, int(block[0]) - 1)
        hit = _call_text(lines, idx)
        if not hit:
            out.append({"leg_line": int(block[0]), "site": reader.get("site"),
                        "sentence": None, "class": "unresolved"})
            continue
        line_no, text = hit
        out.append({
            "leg_line": line_no,
            "site": reader.get("site"),
            "sentence": " ".join(text.split())[:300],
            "class": sentence_class(text),
        })
    return out


def population() -> tuple[list[dict], list[str]]:
    e411 = _load(E411)
    e416 = _load(E416) if os.path.exists(E416) else {"blind_ranking": []}
    rows, notes = [], []
    for f in e411.get("faces") or []:
        if f.get("no_reader_that_can_go_red") and not (f.get("writer_runs_per_round") or 0):
            rows.append(dict(f, population_source="e411_row"))
    seen = {r["face"] for r in rows}
    for r in e416.get("blind_ranking") or []:
        if r["face"] in seen or (r.get("writer_runs_per_round") or 0):
            continue
        rows.append({"face": r["face"], "on_disk": r.get("on_disk"),
                     "reader_sites": r.get("reader_sites"),
                     "readers": r.get("readers") or [],
                     "population_source": "e416_reclassification"})
        notes.append(r["face"])
    return rows, notes


def _stamp_of_face(rel: str) -> tuple[str, object, str | None]:
    if "%s" in rel or "*" in rel:
        return (None, None, None)
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return (None, None, None)
    if not rel.endswith(".json"):
        return (None, None, None)
    try:
        obj = _load(path)
    except Exception:
        return (None, None, None)
    field, value = stamp_of(obj)
    return (field, value, _as_date(value))


def build(cutoff: str | None = None, now_iso: str | None = None) -> dict:
    bars = load_calendar()
    cutoff = cutoff or (bars[-2] if bars and bars[-1] > "2026-11-04" else bars[-1])
    cutoff = min(cutoff, "2026-11-04")
    with io.open(SUITE, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()

    rows, reclassified = population()
    out_rows = []
    for row in rows:
        face = row["face"]
        field, value, stamp = _stamp_of_face(face)
        age = age_bars(stamp, cutoff, bars)
        sentences = green_sentence(face, row, lines)
        classes = [s["class"] for s in sentences]
        if stamp is None:
            verdict = V_NO_STAMP if field is None else V_NO_DATE
        elif any(c == C_FROZEN for c in classes):
            verdict = V_DECAY
        else:
            verdict = V_CLEAN
        out_rows.append({
            "face": face,
            "on_disk": bool(row.get("on_disk")),
            "population_source": row.get("population_source"),
            "reader_sites": row.get("reader_sites"),
            "reader_tiers": row.get("reader_tiers"),
            "stamp_field": field,
            "stamp_value": value if isinstance(value, str) else (str(value) if value is not None else None),
            "stamp_date": stamp,
            "age_bars": age,
            "sentences": sentences,
            "sentence_classes": classes,
            "verdict": verdict,
        })
    out_rows.sort(key=lambda r: (-(r["age_bars"] if r["age_bars"] is not None else -1), r["face"]))

    by_verdict: dict[str, int] = {}
    by_class: dict[str, int] = {}
    for r in out_rows:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
        for c in r["sentence_classes"]:
            by_class[c] = by_class.get(c, 0) + 1

    summary = {
        "faces_in_population": len(out_rows),
        "faces_from_e411_rows": sum(1 for r in out_rows if r["population_source"] == "e411_row"),
        "faces_from_e416_reclassification": len(reclassified),
        "faces_on_disk": sum(1 for r in out_rows if r["on_disk"]),
        "faces_with_a_stamp": sum(1 for r in out_rows if r["stamp_date"]),
        "faces_with_an_age": sum(1 for r in out_rows if r["age_bars"] is not None),
        "median_age_bars": _median([r["age_bars"] for r in out_rows if r["age_bars"] is not None]),
        "max_age_bars": max([r["age_bars"] for r in out_rows if r["age_bars"] is not None], default=None),
        "faces_older_than_5_bars": sum(1 for r in out_rows if (r["age_bars"] or 0) > 5),
        "sentences_read": sum(len(r["sentences"]) for r in out_rows),
        "by_sentence_class": by_class,
        "by_verdict": by_verdict,
        "verdict_is_green": by_verdict.get("decayed claim printed as green", 0) == 0,
    }
    verdict = ("no_blind_face_prints_a_frozen_number_as_green"
               if summary["verdict_is_green"] else
               "some_blind_face_prints_a_number_that_only_held_at_one_cutoff")
    return {
        "study": "E418_how_old_are_the_unprotected_faces_right_now",
        "card": "E418-HOW-OLD-ARE-THE-UNPROTECTED-FACES-RIGHT-NOW",
        "title": "the 45 blind faces, priced by stamp age in bars and by the sentence their legs print when green",
        "generated": now_iso or "",
        "evidence_cutoff": cutoff,
        "verdict": verdict,
        "summary": summary,
        "rows": out_rows,
        "method_limits": [
            "population = E411's published rows (blind = no reader that can go red AND no writer run per round) plus the one face E416 reclassified in; each row names its source.",
            "age is measured in trading bars from the face's own stamp to the cutoff, using data/exchange_calendar.csv; a face without a date-bearing stamp is published as unknowable rather than as age 0.",
            "the green sentence is taken from the nearest check(...) call enclosing the line E411 published as the read site; a leg whose call could not be delimited is published unresolved.",
            "sentence class is a text rule: a literal digit run that is not part of a date or identifier is a frozen number; an f-string interpolating a value is recomputed at read; anything else is no number. The rule prices the sentence, not the face's numbers.",
            "no reader was edited and no face was refreshed relative to this campaign.",
        ],
    }


def _median(values: list[int]) -> float | None:
    if not values:
        return None
    vals = sorted(values)
    n = len(vals)
    return float(vals[n // 2]) if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0


def verify() -> list[str]:
    problems = []
    path = os.path.join(OUTDIR, "FACEAGE-2026-11-04.json")
    if not os.path.exists(path):
        return [f"face missing: {_rel(path)}"]
    face = _load(path)
    rows = face["rows"]
    s = face["summary"]
    if s["faces_in_population"] != len(rows):
        problems.append("population count does not re-derive from rows")
    if s["faces_from_e411_rows"] + s["faces_from_e416_reclassification"] != len(rows):
        problems.append("population sources do not add up")
    recomputed: dict[str, int] = {}
    for r in rows:
        recomputed[r["verdict"]] = recomputed.get(r["verdict"], 0) + 1
    if recomputed != s["by_verdict"]:
        problems.append(f"by_verdict does not re-derive: {recomputed} != {s['by_verdict']}")
    classes: dict[str, int] = {}
    for r in rows:
        for c in r["sentence_classes"]:
            classes[c] = classes.get(c, 0) + 1
    if classes != s["by_sentence_class"]:
        problems.append("by_sentence_class does not re-derive")
    if s["verdict_is_green"] != (recomputed.get("decayed claim printed as green", 0) == 0):
        problems.append("verdict_is_green does not follow from the row verdicts")
    stated = face["verdict"] == "no_blind_face_prints_a_frozen_number_as_green"
    if stated != s["verdict_is_green"]:
        problems.append("published verdict does not follow from the recomputed one")
    for r in rows:
        if r["age_bars"] is not None and r["stamp_date"] is None:
            problems.append(f"{r['face']}: age without stamp")
    return problems


def selftest() -> int:
    bars = ["2026-10-28", "2026-10-29", "2026-10-30", "2026-11-02", "2026-11-03", "2026-11-04"]
    bad = 0
    checks = [
        ("age counts only bars after the stamp", age_bars("2026-10-30", "2026-11-04", bars), 3),
        ("stamp today is age 0", age_bars("2026-11-04", "2026-11-04", bars), 0),
        ("a future stamp is unknowable", age_bars("2026-12-01", "2026-11-04", bars), None),
        ("no stamp is unknowable", age_bars(None, "2026-11-04", bars), None),
        ("literal count is a frozen number", sentence_class('check("5 of 5 rows", True)'), "frozen_literal_number"),
        ("identifier digits are not a number", sentence_class('check("E418 leg green", True)'), "no_number"),
        ("a date is not a count", sentence_class('check("face @ 2026-11-04 ok", True)'), "no_number"),
        ("interpolated value is recomputed", sentence_class('check(f"{n} rows read", True)'), "recomputed_at_read"),
        ("empty sentence has no number", sentence_class('check("", True)'), "no_number"),
        ("stamp prefers the top-level field", stamp_of({"evidence_cutoff": "2026-11-01", "ts": "2026-11-04"})[0], "evidence_cutoff"),
        ("stamp falls back one level", stamp_of({"meta": {"generated": "2026-11-02"}})[0], "generated"),
        ("median of even list", _median([1, 3]), 2.0),
        ("median of odd list", _median([5]), 5.0),
    ]
    for label, got, want in checks:
        if got != want:
            bad += 1
            print(f"FAIL: {label}: {got!r} != {want!r}")
    print(f"selftest {len(checks) - bad}/{len(checks)}")
    return 0 if bad == 0 else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print(f"verify problems={len(problems)}")
        return 0 if not problems else 1
    face = build(now_iso=date.today().isoformat())
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, f"FACEAGE-{face['evidence_cutoff']}.json")
    for target in (out, os.path.join(OUTDIR, "faceage_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print(f"population={s['faces_in_population']} stamped={s['faces_with_a_stamp']} "
          f"aged>{5}={s['faces_older_than_5_bars']} max_age={s['max_age_bars']} "
          f"median={s['median_age_bars']}")
    print(f"by_verdict={s['by_verdict']}")
    print(f"by_sentence_class={s['by_sentence_class']}")
    print(f"verdict={face['verdict']}")
    print(f"face={_rel(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))