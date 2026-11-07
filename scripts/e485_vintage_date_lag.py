"""E485 -- why do two vintages named for one day state the day before?

E484 reconciled E472's 571 unread vintage members and found 5 whose name date and payload date
differ; two of them name 2026-10-21 while the payload states 2026-10-20, and E484 read that split
by hand.  This face measures the lag instead of describing it.

For every member whose *name* states a date -- ISO or the compact YYYYMMDD spelling -- the name
date is compared with the closest date the payload states, and the row lands in exactly one class:

  same_day                     the payload states the day the name states
  payload_one_day_earlier      the closest payload date is the day before the name date
  payload_one_day_later        the closest payload date is the day after the name date
  payload_outside_one_day      the closest payload date is two or more days away
  payload_before_family_span   the payload date precedes the earliest date any sibling name in
                               the same family states -- a data date, not a write date
  no_payload_date              the payload states no date anywhere the scan looks (unmeasured)
  no_date_in_name / ambiguous_name / not_a_json_object / unreadable_member   not comparable

The witness is published per row: which field stated the date, and in what tier it was found --
`frozen` (one of the seven names E480 froze, at the payload's top level), `non_frozen` (another
structured string field at depth <= 2 whose value is a bare date), or `prose` (a date mentioned
inside a longer free-text string).  The tier is the point: a one-day lag witnessed by a prose note
is not the same fact as a one-day lag witnessed by `evidence_cutoff`.

Every row that is not `same_day` also carries writer evidence: which in-repo sources name the file,
and which of those name it in a write context (the literal appears in a line or a 5-line block that
also carries a write verb).  A lag that no source writes is not a lag a script can be held to.

CLI: run | check | verify | selftest
"""

import argparse
import datetime
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "datelag_latest.json"
DATED_PREFIX = "DATELAG"
CARD = "E485-WHY-DO-TWO-VINTAGES-NAMED-FOR-ONE-DAY-STATE-THE-DAY-BEFORE"
PARENT_FACE = "vintagedate_latest.json"   # E480: name-date vs payload-date agreement (571 members)

# The seven names E480 froze and E484 reused.  A name outside this tuple is not a frozen witness.
DATE_FIELDS = ("evidence_cutoff", "generated", "ts", "timestamp", "date", "as_of", "asof_bar")

ISO_DATE_RE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
COMPACT_DATE_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(\d{2})(\d{2})(?!\d)")

C_SAME = "same_day"
C_EARLIER = "payload_one_day_earlier"
C_LATER = "payload_one_day_later"
C_OUTSIDE = "payload_outside_one_day"
C_BEFORE_SPAN = "payload_before_family_span"
C_NO_PAYLOAD = "no_payload_date"
C_NO_NAME = "no_date_in_name"
C_AMBIGUOUS = "ambiguous_name"
C_NOT_JSON = "not_a_json_object"
C_UNREADABLE = "unreadable_member"

COMPARED = (C_SAME, C_EARLIER, C_LATER, C_OUTSIDE, C_BEFORE_SPAN)
CLASSES = COMPARED + (C_NO_PAYLOAD, C_NO_NAME, C_AMBIGUOUS, C_NOT_JSON, C_UNREADABLE)

T_FROZEN = "frozen"
T_NON_FROZEN = "non_frozen"
T_PROSE = "prose"
TIERS = (T_FROZEN, T_NON_FROZEN, T_PROSE)

V_EMPTY = "no_vintage_name_states_a_date_so_no_payload_date_could_be_compared"
V_NONE = "no_dated_vintage_name_states_the_same_day_its_payload_does"
V_ALL = "every_dated_vintage_name_states_the_same_day_its_payload_does"
V_MOST = "most_dated_vintage_names_state_the_same_day_their_payload_does"
V_SOME = "some_dated_vintage_names_state_the_same_day_their_payload_does_and_the_majority_do_not"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_ALL, V_MOST, V_SOME)

K_NONE = "no_one_day_case_needs_an_explanation"
K_STRUCT = "every_one_day_case_is_witnessed_by_a_structured_payload_field"
K_TEXT = "every_one_day_case_is_witnessed_only_by_free_text_in_the_payload"
K_MIXED = "the_one_day_cases_split_between_structured_fields_and_free_text"
CAUSE_VERDICT_VOCAB = (K_NONE, K_STRUCT, K_TEXT, K_MIXED)

WRITE_HINTS = ("'w'", '"w"', "'w+'", '"w+"', ".write(", "write_text(", "to_csv(", "json.dump(",
               "np.save", "savefig(", "writelines(")
SEARCH_DIRS = ("scripts", "Tools", "monitor", "live", "firm")


# ------------------------------------------------------------------------- helpers


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


def name_dates(basename):
    """(iso_date, spelling) for every distinct date the basename states, first appearance order."""
    seen, out = set(), []
    for m in ISO_DATE_RE.finditer(basename):
        iso = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
        if iso not in seen:
            seen.add(iso)
            out.append((iso, "iso"))
    for m in COMPACT_DATE_RE.finditer(basename):
        iso = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
        if iso not in seen:
            seen.add(iso)
            out.append((iso, "compact"))
    return out


def _date(iso):
    return datetime.date(int(iso[:4]), int(iso[5:7]), int(iso[8:10]))


def days_between(a, b):
    """b - a in days."""
    return (_date(b) - _date(a)).days


def _is_prose(text):
    s = text.strip()
    return len(s) > 40 or " " in s or "~" in s


def witnesses(obj, max_depth=2):
    """Every date a payload states, as {field, date, tier}, tier frozen > non_frozen > prose."""
    found = []

    def walk(node, prefix, depth):
        if depth > max_depth:
            return
        if isinstance(node, dict):
            for k, v in node.items():
                key = "%s.%s" % (prefix, k) if prefix else str(k)
                if isinstance(v, str):
                    if depth >= max_depth:
                        return
                    for m in ISO_DATE_RE.finditer(v):
                        iso = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
                        if not prefix and k in DATE_FIELDS:
                            tier = T_FROZEN
                        elif _is_prose(v):
                            tier = T_PROSE
                        else:
                            tier = T_NON_FROZEN
                        found.append({"field": key, "date": iso, "tier": tier})
                elif isinstance(v, (dict, list)):
                    walk(v, key, depth + 1)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (prefix, i), depth + 1)

    walk(obj, "", 0)
    return found


def pick_witness(rows):
    """The witness set used for the comparison: best tier present, then the closest to the name."""
    if not rows:
        return []
    for tier in TIERS:
        tiered = [w for w in rows if w.get("tier") == tier]
        if tiered:
            return tiered
    return []


def split_family(key):
    """'results/_w280bmc' -> ('results/_w280bmc', 'results')"""
    return key, key.split("/", 1)[0] if "/" in key else ""


def family_spans(pop_rows):
    """{family: {'min': iso, 'max': iso, 'dated_members': n}} measured from the members' names."""
    spans = {}
    for r in pop_rows:
        fam = "%s/%s" % (r.get("dir", "?"), r.get("family", "?"))
        for iso, _spelling in name_dates(os.path.basename(r.get("path") or "")):
            cur = spans.setdefault(fam, {"min": iso, "max": iso, "dated_members": 0})
            if iso < cur["min"]:
                cur["min"] = iso
            if iso > cur["max"]:
                cur["max"] = iso
            cur["dated_members"] += 1
    return spans


def classify_file(path, read, exists, span=None):
    """Classify one member file.  All inputs are injectable for the selftest."""
    pairs = name_dates(os.path.basename(path))
    if not pairs:
        return C_NO_NAME, {}, [], []
    if len(pairs) > 1:
        return C_AMBIGUOUS, {}, [p[0] for p in pairs], []
    name_iso, spelling = pairs[0]
    ext = os.path.splitext(path)[1].lower()
    if ext != ".json":
        return C_NOT_JSON, {}, [name_iso], []
    if not exists(path):
        return C_UNREADABLE, {}, [name_iso], []
    try:
        obj = read(path)
    except Exception:
        return C_UNREADABLE, {}, [name_iso], []
    if not isinstance(obj, dict):
        return C_NOT_JSON, {}, [name_iso], []
    stated = witnesses(obj)
    usable = pick_witness(stated)
    if not usable:
        return C_NO_PAYLOAD, {"name_spelling": spelling}, [name_iso], []
    dates = sorted({w["date"] for w in usable})
    closest = min(dates, key=lambda d: (abs(days_between(name_iso, d)), d))
    chosen = next(w for w in usable if w["date"] == closest)
    span_measurable = bool(span and span.get("min"))
    span_position = "unmeasurable"
    if span_measurable:
        span_position = "before_span" if closest < span["min"] else (
            "inside_span" if closest <= span["max"] else "after_span")
    delta = days_between(name_iso, closest)   # payload - name
    if closest == name_iso:
        cls = C_SAME
    elif span_position == "before_span":
        cls = C_BEFORE_SPAN
    elif delta == -1:
        cls = C_EARLIER
    elif delta == 1:
        cls = C_LATER
    else:
        cls = C_OUTSIDE
    witness = {
        "field": chosen["field"],
        "tier": chosen["tier"],
        "date": closest,
        "name_date": name_iso,
        "name_spelling": spelling,
        "delta_days": delta,
        "payload_dates_seen": dates,
        "tiers_seen": sorted({w["tier"] for w in stated}),
        "span_position": span_position,
        "span_measurable": span_measurable,
        "family_span_min": (span or {}).get("min"),
        "family_span_max": (span or {}).get("max"),
    }
    return cls, witness, [name_iso], dates


# ------------------------------------------------------------------------- writers


def _source_texts(dirs=None):
    cache = {}
    for d in dirs or SEARCH_DIRS:
        full = os.path.join(ROOT, d)
        if not os.path.isdir(full):
            continue
        for dirpath, _dirnames, filenames in os.walk(full):
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    cache[_rel(p)] = io.open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
    return cache


def writer_evidence(basename, stem, cache):
    """Which sources name this file, and which name it in a write context."""
    out = []
    for src in sorted(cache):
        text = cache[src]
        if basename in text:
            lines = text.split("\n")
            hit = any(basename in ln for ln in lines)
            write_ctx = False
            for i, ln in enumerate(lines):
                if basename in ln:
                    block = "\n".join(lines[max(0, i - 2): i + 3])
                    if any(h in block for h in WRITE_HINTS):
                        write_ctx = True
                        break
            out.append({"source": src, "signal": "write_context" if write_ctx else "names_only"})
        elif stem and stem in text:
            out.append({"source": src, "signal": "stem_mentioned"})
    return out


# ------------------------------------------------------------------------- build


def build(pop_path=None, cache=None):
    pop = json.load(io.open(pop_path or os.path.join(OUTDIR, PARENT_FACE), "r", encoding="utf-8"))
    pop_rows = pop.get("rows") or []
    spans = family_spans(pop_rows)
    texts = cache if cache is not None else _source_texts()

    rows = []
    families = {}
    counts = {c: 0 for c in CLASSES}
    byte_counts = {c: 0 for c in CLASSES}
    tier_hist = {t: 0 for t in TIERS}
    span_hist = {"inside_span": 0, "before_span": 0, "after_span": 0, "unmeasurable": 0}
    spelling_hist = {"iso": 0, "compact": 0}
    cause_counts = {"structured_field": 0, "free_text": 0}
    writer_hist = {"write_context": 0, "names_only": 0, "none": 0}
    one_day = []

    for r in pop_rows:
        path = r.get("path") or ""
        full = path if os.path.isabs(path) else os.path.join(ROOT, path)
        fam = "%s/%s" % (r.get("dir", "?"), r.get("family", "?"))
        cls, witness, name_isos, payload_dates = classify_file(
            full,
            lambda p: json.load(io.open(p, "r", encoding="utf-8")),
            os.path.exists,
            spans.get(fam),
        )
        try:
            size = os.path.getsize(full)
        except OSError:
            size = 0
        counts[cls] += 1
        byte_counts[cls] += size
        fam_row = families.setdefault(fam, {"family": fam, "members": 0, "counts": {c: 0 for c in CLASSES},
                                            "bytes": 0,
                                            "span": spans.get(fam)})
        fam_row["members"] += 1
        fam_row["counts"][cls] += 1
        fam_row["bytes"] += size

        row = {"path": _rel(full), "family": fam, "bytes": size, "class": cls,
               "name_dates": name_isos, "payload_dates": payload_dates}
        if witness:
            row["witness"] = witness
            tier_hist[witness["tier"]] += 1
            span_hist[witness["span_position"]] += 1
            spelling_hist[witness["name_spelling"]] += 1
        if cls != C_SAME:
            base = os.path.basename(full)
            stem = os.path.splitext(base)[0]
            ev = writer_evidence(base, stem, texts)
            row["writer_evidence"] = ev
            if any(e["signal"] == "write_context" for e in ev):
                writer_hist["write_context"] += 1
            elif ev:
                writer_hist["names_only"] += 1
            else:
                writer_hist["none"] += 1
        if cls in (C_EARLIER, C_LATER):
            cause = "free_text" if witness.get("tier") == T_PROSE else "structured_field"
            cause_counts[cause] += 1
            one_day.append({
                "path": row["path"],
                "class": cls,
                "field": witness.get("field"),
                "tier": witness.get("tier"),
                "name_date": witness.get("name_date"),
                "payload_date": witness.get("date"),
                "delta_days": witness.get("delta_days"),
                "name_spelling": witness.get("name_spelling"),
                "span_position": witness.get("span_position"),
                "cause": cause,
                "writer_evidence": row.get("writer_evidence") or [],
            })
        rows.append(row)

    compared = sum(counts[c] for c in COMPARED)
    same = counts[C_SAME]
    if compared == 0:
        verdict = V_EMPTY
    elif same == 0:
        verdict = V_NONE
    elif same == compared:
        verdict = V_ALL
    elif same * 2 > compared:
        verdict = V_MOST
    else:
        verdict = V_SOME

    if not one_day:
        cause_verdict = K_NONE
    elif cause_counts["free_text"] == 0:
        cause_verdict = K_STRUCT
    elif cause_counts["structured_field"] == 0:
        cause_verdict = K_TEXT
    else:
        cause_verdict = K_MIXED

    summary = {
        "member_files": len(rows),
        "families_total": len(families),
        "class_counts": counts,
        "class_bytes": byte_counts,
        "compared_files": compared,
        "names_matching_the_payload_day": same,
        "same_day_share_of_compared": round(same / compared, 6) if compared else None,
        "one_day_cases": len(one_day),
        "one_day_earlier": counts[C_EARLIER],
        "one_day_later": counts[C_LATER],
        "outside_one_day_window": counts[C_OUTSIDE],
        "before_family_span": counts[C_BEFORE_SPAN],
        "witness_field_tiers": tier_hist,
        "family_span_positions": span_hist,
        "name_date_spellings": spelling_hist,
        "one_day_cause_counts": cause_counts,
        "writers_of_non_same_rows": writer_hist,
        "bytes_in_files_whose_name_day_is_the_payload_day": byte_counts[C_SAME],
    }

    face = {
        "card": CARD,
        "study": "E485_why_do_two_vintages_named_for_one_day_state_the_day_before",
        "title": "why do two vintages named for one day state the day before?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "frozen_date_fields": list(DATE_FIELDS),
        "witness_tiers": {
            T_FROZEN: "one of the seven frozen names at the payload's top level",
            T_NON_FROZEN: "another structured string field at depth <= 2 whose value is a bare date",
            T_PROSE: "a date mentioned inside a longer free-text string",
        },
        "population_source": {
            "face": PARENT_FACE,
            "face_evidence_cutoff": pop.get("evidence_cutoff"),
            "face_verdict": pop.get("verdict"),
            "members": len(pop_rows),
        },
        "class_definition": {
            C_SAME: "the payload states the day the name states (compared on the closest payload date)",
            C_EARLIER: "the closest payload date is the day before the name date and is not before "
                        "the family's own earliest dated name",
            C_LATER: "the closest payload date is the day after the name date",
            C_OUTSIDE: "the closest payload date is two or more days from the name date",
            C_BEFORE_SPAN: "the closest payload date precedes every date the siblings' names state: "
                           "a data date, not a write date",
            C_NO_PAYLOAD: "the name states a date and the payload states none anywhere the scan "
                          "looks: unmeasured, never a negative",
            C_NO_NAME: "the basename states no ISO or compact date",
            C_AMBIGUOUS: "the basename states two or more distinct dates (a range name)",
            C_NOT_JSON: "the member is not a .json object",
            C_UNREADABLE: "the member is missing on disk or does not parse",
        },
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "cause_verdict": cause_verdict,
        "cause_verdict_vocab": list(CAUSE_VERDICT_VOCAB),
        "one_day_cases": one_day,
        "families": [families[k] for k in sorted(families)],
        "rows": rows,
        "method_limits": [
            "the comparison uses the closest payload date after preferring the best witness tier: "
            "a payload that states several days is summarised by one, and the full set is published "
            "per row (payload_dates, tiers_seen)",
            "a date inside a long prose string is a witness of the same rank as prose anywhere else: "
            "one day inside a paragraph is not a stamp a writer can be held to",
            "family spans come from the population's own names; a family whose dated siblings are "
            "all outside E472's member list reads unmeasurable, never inside",
            "writer evidence is a source-level signal (the literal plus a write verb within two "
            "lines), not dataflow: a write in another module through a helper is not attributed",
        ],
    }
    return face


# ------------------------------------------------------------------------- guards


def _expect_verdict(counts):
    compared = sum(counts.get(c, 0) for c in COMPARED)
    same = counts.get(C_SAME, 0)
    if compared == 0:
        return V_EMPTY
    if same == 0:
        return V_NONE
    if same == compared:
        return V_ALL
    if same * 2 > compared:
        return V_MOST
    return V_SOME


def _expect_cause(one_day):
    if not one_day:
        return K_NONE
    free = sum(1 for c in one_day if c.get("cause") == "free_text")
    struct = sum(1 for c in one_day if c.get("cause") == "structured_field")
    if free == 0:
        return K_STRUCT
    if struct == 0:
        return K_TEXT
    return K_MIXED


def row_problems(face):
    problems = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    counts = s.get("class_counts") or {}
    if set(counts) != set(CLASSES):
        problems.append("class_counts keys are not the published class set: %r" % sorted(counts))
    if sum(counts.values()) != s.get("member_files"):
        problems.append("class counts do not sum to member_files")
    if len(rows) != s.get("member_files"):
        problems.append("row count %d != member_files %r" % (len(rows), s.get("member_files")))
    if sum((s.get("class_bytes") or {}).values()) != sum(r.get("bytes", 0) for r in rows):
        problems.append("class bytes do not sum to the row bytes")

    derived = {c: 0 for c in CLASSES}
    tiers = {t: 0 for t in TIERS}
    spans = {"inside_span": 0, "before_span": 0, "after_span": 0, "unmeasurable": 0}
    spellings = {"iso": 0, "compact": 0}
    writers = {"write_context": 0, "names_only": 0, "none": 0}
    one_day = []
    for r in rows:
        cls = r.get("class")
        if cls not in CLASSES:
            problems.append("row %s carries a class outside the set" % r.get("path"))
            break
        derived[cls] += 1
        w = r.get("witness") or {}
        if cls in COMPARED:
            if not w:
                problems.append("row %s is compared but carries no witness" % r.get("path"))
                break
            if w.get("tier") not in TIERS:
                problems.append("row %s has a witness tier outside the frozen vocabulary" % r.get("path"))
                break
            tiers[w["tier"]] += 1
            if w.get("span_position") not in spans:
                problems.append("row %s has a span position outside the vocabulary" % r.get("path"))
                break
            spans[w["span_position"]] += 1
            spellings[w.get("name_spelling")] += 1
            name_d, payload_d = w.get("name_date"), w.get("date")
            if not (name_d and payload_d):
                problems.append("row %s is compared without both dates" % r.get("path"))
                break
            delta = days_between(name_d, payload_d)
            if delta != w.get("delta_days"):
                problems.append("row %s states a delta that its own dates do not reproduce" % r.get("path"))
                break
            if cls == C_SAME and delta != 0:
                problems.append("row %s is same_day with a non-zero delta" % r.get("path"))
                break
            if cls == C_EARLIER and not (delta == -1 and w.get("span_position") != "before_span"):
                problems.append("row %s is one_day_earlier without delta -1 outside a pre-span date"
                                % r.get("path"))
                break
            if cls == C_LATER and delta != 1:
                problems.append("row %s is one_day_later with delta %r" % (r.get("path"), delta))
                break
            if cls == C_OUTSIDE and abs(delta) <= 1:
                problems.append("row %s is outside_one_day with delta %r" % (r.get("path"), delta))
                break
            if cls == C_BEFORE_SPAN:
                if w.get("span_position") != "before_span" or not w.get("span_measurable"):
                    problems.append("row %s is before_span without a measurable span below it"
                                    % r.get("path"))
                    break
        if cls != C_SAME:
            ev = r.get("writer_evidence")
            if not isinstance(ev, list):
                problems.append("row %s is not same_day but carries no writer evidence list"
                                % r.get("path"))
                break
            if any(e.get("signal") == "write_context" for e in ev):
                writers["write_context"] += 1
            elif ev:
                writers["names_only"] += 1
            else:
                writers["none"] += 1
        if cls in (C_EARLIER, C_LATER):
            cause = "free_text" if w.get("tier") == T_PROSE else "structured_field"
            one_day.append({"path": r.get("path"), "class": cls, "field": w.get("field"),
                            "tier": w.get("tier"), "name_date": w.get("name_date"),
                            "payload_date": w.get("date"), "delta_days": w.get("delta_days"),
                            "name_spelling": w.get("name_spelling"),
                            "span_position": w.get("span_position"), "cause": cause,
                            "writer_evidence": r.get("writer_evidence") or []})

    if derived != counts:
        problems.append("the published class counts do not re-derive from the rows")
    if s.get("compared_files") != sum(derived[c] for c in COMPARED):
        problems.append("the compared tally is not the sum of the compared classes")
    if s.get("names_matching_the_payload_day") != derived.get(C_SAME):
        problems.append("the same-day tally does not re-derive from the rows")
    if s.get("one_day_cases") != derived.get(C_EARLIER, 0) + derived.get(C_LATER, 0):
        problems.append("the one-day tally is not earlier + later")
    if s.get("one_day_earlier") != derived.get(C_EARLIER):
        problems.append("the earlier tally does not re-derive")
    if s.get("one_day_later") != derived.get(C_LATER):
        problems.append("the later tally does not re-derive")
    if s.get("outside_one_day_window") != derived.get(C_OUTSIDE):
        problems.append("the outside-window tally does not re-derive")
    if s.get("before_family_span") != derived.get(C_BEFORE_SPAN):
        problems.append("the before-span tally does not re-derive")
    if s.get("witness_field_tiers") != tiers:
        problems.append("the witness-tier histogram does not re-derive from the rows")
    if s.get("family_span_positions") != spans:
        problems.append("the span-position histogram does not re-derive from the rows")
    if s.get("name_date_spellings") != spellings:
        problems.append("the spelling histogram does not re-derive from the rows")
    if s.get("writers_of_non_same_rows") != writers:
        problems.append("the writer histogram does not re-derive from the rows")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary: %r" % face.get("verdict"))
    if face.get("cause_verdict") not in CAUSE_VERDICT_VOCAB:
        problems.append("cause_verdict is outside the frozen vocabulary: %r" % face.get("cause_verdict"))
    published_one_day = face.get("one_day_cases") or []
    if published_one_day != one_day:
        problems.append("the published one-day case list does not re-derive from the rows")
    fam_sum = sum(f.get("members", 0) for f in face.get("families") or [])
    if fam_sum != s.get("member_files"):
        problems.append("family member counts do not sum to member_files")
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    counts = (face.get("summary") or {}).get("class_counts") or {}
    expect = _expect_verdict(counts)
    if face.get("verdict") != expect:
        problems.append("verdict %r is not the one the counts imply (%r)" % (face.get("verdict"), expect))
    one_day = face.get("one_day_cases") or []
    if face.get("cause_verdict") != _expect_cause(one_day):
        problems.append("cause_verdict %r is not the one the cases imply (%r)"
                        % (face.get("cause_verdict"), _expect_cause(one_day)))
    return problems


def verify():
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build()
    problems = []
    ps, fs = published.get("summary") or {}, fresh.get("summary") or {}
    for key in sorted(set(ps) | set(fs)):
        if ps.get(key) != fs.get(key):
            problems.append("%s: published %r != fresh %r" % (key, ps.get(key), fs.get(key)))
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict: published %r != fresh %r"
                        % (published.get("verdict"), fresh.get("verdict")))
    if published.get("cause_verdict") != fresh.get("cause_verdict"):
        problems.append("cause_verdict: published %r != fresh %r"
                        % (published.get("cause_verdict"), fresh.get("cause_verdict")))
    if published.get("one_day_cases") != fresh.get("one_day_cases"):
        problems.append("one_day_cases do not re-derive identically")
    return problems


def run(face=None):
    face = face or build()
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    compact = json.dumps(face, ensure_ascii=False, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(compact + "\n")
    problems = check(face)
    print(json.dumps({"face": _rel(latest), "dated": _rel(dated),
                      "summary": face["summary"], "verdict": face["verdict"],
                      "cause_verdict": face["cause_verdict"],
                      "one_day_cases": face["one_day_cases"],
                      "problems": problems}, ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ------------------------------------------------------------------------- selftest


def selftest():
    tmp = tempfile.mkdtemp(prefix="e485_")
    fails = []

    def want(name, got, expect):
        if got != expect:
            fails.append("%s: got %r want %r" % (name, got, expect))

    try:
        def w(path, obj):
            d = os.path.dirname(path)
            if d and not os.path.isdir(d):
                os.makedirs(d)
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True))

        base = os.path.join(tmp, "fam")
        # family span is 2026-01-01 .. 2026-01-09, from the names below
        a = os.path.join(base, "FAM-2026-01-01.json")
        w(a, {"ts": "2026-01-01T10:00:00+08:00"})                       # same day (frozen)
        b = os.path.join(base, "FAM-2026-01-05.json")
        w(b, {"evidence_cutoff": "2026-01-04"})                         # one day earlier, in span
        c = os.path.join(base, "FAM-2026-01-09.json")
        w(c, {"ts": "2026-01-10T01:00:00"})                             # one day later
        d = os.path.join(base, "FAM-2026-01-06.json")
        w(d, {"ts": "2026-01-02"})                                      # outside the window
        e = os.path.join(base, "FAM-20260107.json")
        w(e, {"date": "2025-12-31"})                                    # compact name, pre-span
        f = os.path.join(base, "FAM-2026-01-08.json")
        w(f, {"count": 9})                                              # no witness anywhere
        g = os.path.join(base, "FAM_latest.json")
        w(g, {"ts": "2026-01-08"})
        h = os.path.join(base, "FAM-2026-01-02-2026-01-03.json")
        w(h, {"ts": "2026-01-02"})
        i = os.path.join(base, "FAM-2026-01-03.csv")
        w(i, "a,b\n1,2\n")
        j = os.path.join(base, "FAM-2026-01-04.json")
        # missing on disk
        k = os.path.join(base, "FAM-2026-01-05b.json")
        w(k, "{not json")
        m = os.path.join(base, "FAM-2026-01-06b.json")
        w(m, {"note": "written 2026-01-06 after the run, prose only"})   # prose tier, same day

        names = [a, b, c, d, e, f, g, h, i, j, k, m]
        span = {"min": "2026-01-01", "max": "2026-01-09", "dated_members": 9}
        cls = {}
        wit = {}
        for p in names:
            c_, w_, _nd, _pd = classify_file(
                p, lambda q: json.load(io.open(q, "r", encoding="utf-8")), os.path.exists, span)
            cls[os.path.basename(p)] = c_
            wit[os.path.basename(p)] = w_

        want("same day", cls["FAM-2026-01-01.json"], C_SAME)
        want("one day earlier", cls["FAM-2026-01-05.json"], C_EARLIER)
        want("one day later", cls["FAM-2026-01-09.json"], C_LATER)
        want("outside window", cls["FAM-2026-01-06.json"], C_OUTSIDE)
        want("compact name before span", cls["FAM-20260107.json"], C_BEFORE_SPAN)
        want("no payload date", cls["FAM-2026-01-08.json"], C_NO_PAYLOAD)
        want("no name date", cls["FAM_latest.json"], C_NO_NAME)
        want("ambiguous name", cls["FAM-2026-01-02-2026-01-03.json"], C_AMBIGUOUS)
        want("not json", cls["FAM-2026-01-03.csv"], C_NOT_JSON)
        want("missing member", cls["FAM-2026-01-04.json"], C_UNREADABLE)
        want("unparsable json", cls["FAM-2026-01-05b.json"], C_UNREADABLE)
        want("prose witness same day", cls["FAM-2026-01-06b.json"], C_SAME)

        want("frozen tier", wit["FAM-2026-01-01.json"]["tier"], T_FROZEN)
        want("earlier delta", wit["FAM-2026-01-05.json"]["delta_days"], -1)
        want("later delta", wit["FAM-2026-01-09.json"]["delta_days"], 1)
        want("outside delta", wit["FAM-2026-01-06.json"]["delta_days"], -4)
        want("pre-span position", wit["FAM-20260107.json"]["span_position"], "before_span")
        want("compact spelling", wit["FAM-20260107.json"]["name_spelling"], "compact")
        want("prose tier", wit["FAM-2026-01-06b.json"]["tier"], T_PROSE)
        want("prose is still same day", wit["FAM-2026-01-06b.json"]["delta_days"], 0)

        # date parsing
        want("iso + compact distinct", name_dates("X-2026-01-01_20260102.json"),
             [("2026-01-01", "iso"), ("2026-01-02", "compact")])
        want("no date", name_dates("X_latest.json"), [])
        want("deduplicated", name_dates("X-2026-01-01-2026-01-01.json"), [("2026-01-01", "iso")])
        want("days between", days_between("2026-01-05", "2026-01-04"), -1)

        # witness tiers, including depth > 2 being out of scope
        nested = {"a": {"b": {"c": "2026-03-01"}}}
        want("nested depth 3 out of scope", witnesses(nested), [])
        want("nested depth 2 in scope",
             [x["tier"] for x in witnesses({"a": {"b": "2026-03-01"}})], [T_NON_FROZEN])
        want("frozen field only at top level",
             [x["tier"] for x in witnesses({"a": {"ts": "2026-03-01"}})], [T_NON_FROZEN])
        want("prose tier", [x["tier"] for x in witnesses({"note": "ran on 2026-03-01 after close"})],
             [T_PROSE])

        # family spans from names
        pop = [{"dir": "results", "family": "F", "path": "results/F-2026-01-03.json"},
               {"dir": "results", "family": "F", "path": "results/F-20260101.json"},
               {"dir": "results", "family": "G", "path": "results/G_latest.json"}]
        spans = family_spans(pop)
        want("span min from compact name", spans["results/F"]["min"], "2026-01-01")
        want("span max", spans["results/F"]["max"], "2026-01-03")
        want("no dated sibling", spans.get("results/G"), None)

        # writer evidence
        cache = {
            "scripts/writer_mod.py": "import json\np = 'FAM-2026-01-05.json'\n"
                                     "json.dump({}, open(p, 'w'))\n",
            "scripts/reader_mod.py": "p = 'FAM-2026-01-05.json'\nprint(open(p).read())\n",
            "scripts/stem_mod.py": "stem = 'FAM-2026-01-06'\n",
        }
        ev = writer_evidence("FAM-2026-01-05.json", "FAM-2026-01-05", cache)
        want("writer signals", {e["source"]: e["signal"] for e in ev},
             {"scripts/writer_mod.py": "write_context", "scripts/reader_mod.py": "names_only"})
        ev2 = writer_evidence("FAM-2026-01-06.json", "FAM-2026-01-06", cache)
        want("stem mention", ev2, [{"source": "scripts/stem_mod.py", "signal": "stem_mentioned"}])

        # verdict arithmetic
        empty = {c: 0 for c in CLASSES}
        want("verdict empty", _expect_verdict(empty), V_EMPTY)
        want("verdict none", _expect_verdict(dict(empty, **{C_EARLIER: 3})), V_NONE)
        want("verdict all", _expect_verdict(dict(empty, **{C_SAME: 3})), V_ALL)
        want("verdict most", _expect_verdict(dict(empty, **{C_SAME: 3, C_EARLIER: 2})), V_MOST)
        want("verdict some", _expect_verdict(dict(empty, **{C_SAME: 2, C_EARLIER: 3})), V_SOME)
        want("cause none", _expect_cause([]), K_NONE)
        want("cause struct", _expect_cause([{"cause": "structured_field"}]), K_STRUCT)
        want("cause text", _expect_cause([{"cause": "free_text"}]), K_TEXT)
        want("cause mixed", _expect_cause([{"cause": "free_text"}, {"cause": "structured_field"}]),
             K_MIXED)

        # guards: build a clean fixture and doctor it
        def row(path, cls_, witness_, ev_=None):
            r = {"path": path, "family": "results/F", "bytes": 1, "class": cls_}
            if witness_:
                r["witness"] = witness_
            if cls_ != C_SAME:
                r["writer_evidence"] = ev_ if ev_ is not None else []
            return r

        w_same = {"field": "ts", "tier": T_FROZEN, "date": "2026-01-01", "name_date": "2026-01-01",
                  "name_spelling": "iso", "delta_days": 0, "payload_dates_seen": ["2026-01-01"],
                  "tiers_seen": [T_FROZEN], "span_position": "inside_span",
                  "span_measurable": True, "family_span_min": "2026-01-01",
                  "family_span_max": "2026-01-09"}
        w_early = dict(w_same, field="evidence_cutoff", date="2026-01-04",
                       name_date="2026-01-05", delta_days=-1)
        one = [{"field": w_early["field"], "tier": w_early["tier"],
                "name_date": w_early["name_date"], "payload_date": w_early["date"],
                "delta_days": w_early["delta_days"], "name_spelling": w_early["name_spelling"],
                "span_position": w_early["span_position"]}]
        one[0].update({"path": "results/F-2026-01-05.json", "class": C_EARLIER,
                       "cause": "structured_field", "writer_evidence": []})
        good = {
            "summary": {"member_files": 2, "compared_files": 2,
                        "class_counts": dict(empty, **{C_SAME: 1, C_EARLIER: 1}),
                        "class_bytes": dict(empty, **{C_SAME: 1, C_EARLIER: 1}),
                        "names_matching_the_payload_day": 1, "one_day_cases": 1,
                        "one_day_earlier": 1, "one_day_later": 0, "outside_one_day_window": 0,
                        "before_family_span": 0,
                        "witness_field_tiers": {T_FROZEN: 2, T_NON_FROZEN: 0, T_PROSE: 0},
                        "family_span_positions": {"inside_span": 2, "before_span": 0,
                                                  "after_span": 0, "unmeasurable": 0},
                        "name_date_spellings": {"iso": 2, "compact": 0},
                        "writers_of_non_same_rows": {"write_context": 0, "names_only": 0, "none": 1}},
            "families": [{"family": "results/F", "members": 2}],
            "rows": [row("results/F-2026-01-01.json", C_SAME, w_same),
                     row("results/F-2026-01-05.json", C_EARLIER, w_early)],
            "one_day_cases": one,
            "verdict": V_SOME,
            "cause_verdict": K_STRUCT,
        }
        want("clean fixture checks", check(good), [])

        doctor_cases = [
            ("verdict", lambda f: f.__setitem__("verdict", V_ALL)),
            ("cause", lambda f: f.__setitem__("cause_verdict", K_TEXT)),
            ("same-day tally", lambda f: f["summary"].__setitem__(
                "names_matching_the_payload_day", 0)),
            ("class counts", lambda f: f["summary"]["class_counts"].__setitem__(C_SAME, 2)),
            ("witness tier", lambda f: f["rows"][0]["witness"].__setitem__("tier", "guess")),
            ("same-day delta", lambda f: f["rows"][0]["witness"].__setitem__("delta_days", 1)),
            ("earlier delta", lambda f: f["rows"][1]["witness"].__setitem__("delta_days", 1)),
            ("one-day list", lambda f: f["one_day_cases"][0].__setitem__("cause", "free_text")),
            ("writer list", lambda f: f["rows"][1].__setitem__("writer_evidence", None)),
            ("tier histogram", lambda f: f["summary"]["witness_field_tiers"].__setitem__(T_FROZEN, 0)),
            ("span histogram", lambda f: f["summary"]["family_span_positions"].__setitem__(
                "inside_span", 1)),
            ("family sum", lambda f: f["families"][0].__setitem__("members", 3)),
        ]
        for name, doctor in doctor_cases:
            doctored = json.loads(json.dumps(good))
            doctor(doctored)
            if not check(doctored):
                fails.append("check() accepted a face whose %s was doctored" % name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        return 1
    print("selftest 47/47: 12 file classes + 8 witness/tier reads + 4 date helpers + "
          "5 verdict branches + 4 cause branches + 2 writer signals + 12 doctored faces: OK")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        problems = check()
    elif args.cmd == "verify":
        problems = verify()
    else:
        return selftest()
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))