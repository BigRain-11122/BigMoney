#!/usr/bin/env python
"""E601 -- is a duplicated row detectable from what a face already publishes?

E597 (r1626) found that the annualisation quadruple carries a bar count and nothing else, so a
duplicated row silently changes a published CAGR.  That is a statement about a missing witness; it
never asked whether the witness exists anywhere else, or whether it would be consistent with the
count the face prints.

This study takes every published face that states a bar count and asks three questions per face:

  1. what witness does it carry?  a distinct-bar count or a dedupe flag (a duplicate is visible
     directly), a first/last bar identity (a duplicate is visible only with an outside calendar),
     or a count and nothing else (invisible);
  2. does it also publish the rows it counts?  if it does, the rows are measured here, so the
     question is no longer hypothetical -- the duplicate is either present or it is not;
  3. if both are published, does the count agree with the row count or with the distinct-row count?
     A count that happens to equal the distinct count while the rows carry duplicates is
     consistent with dedupe but does not SAY it is a distinct count, which is the worst shape: it
     looks reconciled.

Output: results/state_tilt/DUPWITNESS.json (+ -latest.json)
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e597_bar_count_arith as e597                                     # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "DUPWITNESS.json")
SELF_STEM = "DUPWITNESS"

# the population and the count vocabulary are E597's, deliberately: this study grades the same
# blocks that study counted, so the two faces can be read against each other
COUNT_KEYS = e597.COUNT_KEYS
BAR_IDENTITY_KEYS = e597.BAR_IDENTITY_KEYS
RE_WITNESS_FIELD = e597.RE_WITNESS_FIELD
FACE_GLOBS = e597.FACE_GLOBS
READ_CAP = e597.READ_CAP
is_count_value = e597.is_count_value
walk_blocks = e597.walk_blocks
witness_class = e597.witness_class

SERIES_KEY_CANDIDATES = ("bar", "date", "bar_date", "as_of", "day", "trade_date", "ts", "time")
SERIES_MIN_ROWS = 2
SERIES_PER_FACE = 6         # series measured and published per face; the cap is declared in limits
DUP_ROWS_CAP = 5000         # rows measured per series; a longer series is measured on its head
SAMPLE_DUP_ROWS = 3         # duplicated rows described per series (the count is the measure)
SIGNATURE_LEN = 60          # characters of a duplicated row kept as its own identity

# witness the face carries, strongest first
W_DEDUPE = e597.W_DEDUPE
W_IDENTITY = e597.W_IDENTITY
W_COUNT_ONLY = e597.W_COUNT_ONLY
WITNESSES = (W_DEDUPE, W_IDENTITY, W_COUNT_ONLY)

# where a duplicated row would land, per counted face
D_DIRECT = "a_distinct_count_or_dedupe_flag_would_show_a_duplicated_row_directly"
D_ROWS = "the_rows_are_published_so_a_duplicate_would_show_in_them_though_not_in_the_count"
D_ROWS_DUP = "the_rows_are_published_and_already_carry_a_duplicated_row"
D_NO_ROWS = "the_face_states_a_count_and_publishes_no_rows_so_nothing_can_contradict_it"
CLASSES = (D_DIRECT, D_ROWS, D_ROWS_DUP, D_NO_ROWS)

# how a published count lines up with the rows, when both exist
MATCH_ROWS = "count_equals_the_row_count_including_duplicates"
MATCH_DISTINCT = "count_equals_the_distinct_rows_but_the_face_never_says_it_is_distinct"
MATCH_NEITHER = "count_equals_neither_the_rows_nor_the_distinct_rows"
MATCH_NO_COUNT = "the_face_publishes_rows_beside_no_count_at_all"
MATCHES = (MATCH_ROWS, MATCH_DISTINCT, MATCH_NEITHER, MATCH_NO_COUNT)

V_MAJORITY_INVISIBLE = ("on_most_faces_that_state_a_count_the_rows_it_counts_are_not_published_so"
                        "_nothing_in_the_face_can_contradict_the_number")
V_SPLIT = ("most_counted_faces_publish_the_rows_they_count_so_a_duplicated_row_would_show_there_"
           "but_a_minority_publish_a_count_inside_no_rows_at_all")
V_ALL_VISIBLE = "every_face_that_states_a_count_publishes_the_rows_a_duplicate_would_show_in"
V_NO_POPULATION = "no_published_face_states_a_bar_count_so_the_question_has_no_population"

REQUIRED_SERIES_KEYS = ("face", "at", "rows", "rows_distinct", "duplicate_rows",
                        "count_match", "count_fields")


# --------------------------------------------------------------------------- pure helpers
def _is_scalar(v):
    return isinstance(v, (str, int, float, bool)) and not isinstance(v, bool)


def series_shape(lst):
    """(rows, rows_distinct, duplicate_rows, bar_key, distinct_bar, sample_duplicates).

    A 'duplicated row' is a repeat of the whole object, which is what a duplicated panel line
    looks like after a json round-trip; the bar key gives the weaker 'two rows for one bar' read.
    """
    rows = lst[:DUP_ROWS_CAP]
    seen = {}
    dups = []
    for r in rows:
        k = json.dumps(r, sort_keys=True, ensure_ascii=False)
        seen[k] = seen.get(k, 0) + 1
        if seen[k] > 1 and len(dups) < SAMPLE_DUP_ROWS:
            dups.append(k[:SIGNATURE_LEN])
    rows_distinct = len(seen)
    duplicate_rows = len(rows) - rows_distinct
    bar_key = ""
    if rows:
        keys = set(rows[0])
        for r in rows[1:]:
            keys &= set(r)
        for cand in SERIES_KEY_CANDIDATES:
            if cand in keys:
                bar_key = cand
                break
    distinct_bar = None
    if bar_key:
        distinct_bar = len({json.dumps(r.get(bar_key), ensure_ascii=False) for r in rows})
    return {
        "rows": len(rows),
        "rows_distinct": rows_distinct,
        "duplicate_rows": duplicate_rows,
        "bar_key": bar_key,
        "distinct_bar_values": distinct_bar,
        "sample_duplicates": dups,
    }


def count_match(rows, rows_distinct, count_value):
    """How the face's own count lines up with the rows it publishes beside it."""
    if not is_count_value(count_value):
        return MATCH_NO_COUNT
    if count_value == rows:
        return MATCH_ROWS
    if count_value == rows_distinct:
        return MATCH_DISTINCT
    return MATCH_NEITHER


def face_class(witness, has_rows, duplicate_rows):
    """Where a duplicated row would land on this face, strongest witness first.

    The count is not a witness: a face that publishes the rows the count is about can be
    contradicted by them whatever else it prints, and a face that publishes only the count cannot
    be contradicted by anything it prints.
    """
    if not has_rows:
        return D_NO_ROWS
    if witness == W_DEDUPE:
        return D_DIRECT
    if duplicate_rows > 0:
        return D_ROWS_DUP
    return D_ROWS


def witness_of_blocks(blocks):
    """The strongest witness any block of this face carries."""
    names = [witness_class(b) for b in blocks]
    for w in WITNESSES:
        if w in names:
            return w
    return W_COUNT_ONLY


# --------------------------------------------------------------------------- scan
def faces_on_disk(root):
    out = []
    for pattern in FACE_GLOBS:
        for p in glob.glob(os.path.join(root, pattern), recursive=True):
            rel = os.path.relpath(p, root).replace("\\", "/")
            if os.path.basename(rel).startswith(SELF_STEM):
                continue
            out.append(rel)
    return sorted(set(out))


def walk_series(node, at="", depth=0):
    """Every published list of >=2 objects, with the dict that holds it (for its count keys)."""
    out = []
    if depth > e597.DEPTH_CAP:
        return out
    if isinstance(node, dict):
        for k, v in node.items():
            here = (at or "") + "/" + str(k)
            if isinstance(v, list) and len(v) >= SERIES_MIN_ROWS \
                    and all(isinstance(x, dict) for x in v[:SERIES_MIN_ROWS]):
                out.append((here, node, v))
            out.extend(walk_series(v, here, depth + 1))
    elif isinstance(node, list):
        for i, v in enumerate(node[:e597.LIST_CAP]):
            out.extend(walk_series(v, (at or "") + "[%d]" % i, depth + 1))
    return out


def series_row(face, at, holder, lst):
    sh = series_shape(lst)
    counts = {k: holder.get(k) for k in COUNT_KEYS if is_count_value(holder.get(k))}
    count_value = None
    for k in COUNT_KEYS:
        if k in counts:
            count_value = counts[k]
            break
    row = {
        "face": face,
        "at": at,
        "rows": sh["rows"],
        "rows_distinct": sh["rows_distinct"],
        "duplicate_rows": sh["duplicate_rows"],
        "bar_key": sh["bar_key"],
        "distinct_bar_values": sh["distinct_bar_values"],
        "count_fields": sorted(counts),
        "count_value": count_value,
        "count_match": count_match(sh["rows"], sh["rows_distinct"], count_value),
        "sample_duplicates": sh["sample_duplicates"],
    }
    return row


def scan(root=None):
    """Faces that state a bar count, with the series they publish beside it.

    The population is deliberately the COUNT-CARRYING faces: the question is whether the count a
    face prints can fail, so a face with no count is not a reading here.  Series beyond
    SERIES_PER_FACE per face are not measured, and the cap is declared on the face.
    """
    root = root or ROOT
    faces, unreadable, too_big = [], 0, []
    all_paths = faces_on_disk(root)
    for rel in all_paths:
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > READ_CAP:
                too_big.append(rel)
                unreadable += 1
                continue
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                payload = json.load(fh)
        except (ValueError, OSError):
            unreadable += 1
            continue
        blocks = [node for _at, node in walk_blocks(payload)]
        if not blocks:
            continue
        face_rows = []
        for at, holder, lst in walk_series(payload)[:SERIES_PER_FACE]:
            face_rows.append(series_row(rel, at, holder, lst))
        witness = witness_of_blocks(blocks)
        dup = max([r["duplicate_rows"] for r in face_rows] or [0])
        faces.append({
            "face": rel,
            "blocks": len(blocks),
            "count_keys_published": sorted({k for b in blocks for k in COUNT_KEYS
                                            if is_count_value(b.get(k))}),
            "witness": witness,
            "series": face_rows,
            "series_rows": len(face_rows),
            "class": face_class(witness, bool(face_rows), dup),
            "duplicate_rows_published": dup,
        })
    return {"faces": faces, "unreadable": unreadable, "too_big": sorted(too_big),
            "faces_read": len(all_paths)}


def summarise(sc):
    faces = sc["faces"]
    by_witness = {w: 0 for w in WITNESSES}
    by_class = {c: 0 for c in CLASSES}
    by_match = {m: 0 for m in MATCHES}
    for f in faces:
        if f["witness"]:
            by_witness[f["witness"]] += 1
        by_class[f["class"]] += 1
        for s in f["series"]:
            by_match[s["count_match"]] += 1
    counted = sum(1 for f in faces if f["blocks"])
    invisible = by_class[D_NO_ROWS]
    return {
        "faces_read": sc["faces_read"],
        "faces_unreadable": sc["unreadable"],
        "faces_published_too_big": len(sc["too_big"]),
        "faces_with_a_count": counted,
        "faces_with_a_series": sum(1 for f in faces if f["series_rows"]),
        "faces_with_a_count_beside_the_rows_it_counts":
            sum(1 for f in faces if f["blocks"] and f["series_rows"]),
        "blocks_total": sum(f["blocks"] for f in faces),
        "series_total": sum(f["series_rows"] for f in faces),
        "by_witness": by_witness,
        "by_class": by_class,
        "by_count_match": by_match,
        "faces_whose_count_nothing_can_contradict": invisible,
        "faces_publishing_a_duplicate_row_right_now":
            sum(1 for f in faces if f["duplicate_rows_published"] > 0),
        "duplicate_rows_published_total": sum(f["duplicate_rows_published"] for f in faces),
        "share_of_count_faces_where_a_duplicate_is_invisible":
            round(float(invisible) / float(counted) if counted else 0.0, 4),
    }


def verdict_from(counts):
    if counts.get("faces_with_a_count", 0) == 0:
        return V_NO_POPULATION
    share = counts.get("share_of_count_faces_where_a_duplicate_is_invisible") or 0.0
    if share > 0.5:
        return V_MAJORITY_INVISIBLE
    if share > 0:
        return V_SPLIT
    return V_ALL_VISIBLE


def answer_sentence(counts, verdict):
    c = counts or {}
    head = ("%d of the %d faces that state a bar count (%s) also publish the rows that count is "
            "about, so a duplicated row would show in them; the other %d publish a number no "
            "published data can contradict, and %d counted faces already publish a duplicated "
            "row (%d rows)"
            % (c.get("faces_with_a_count_beside_the_rows_it_counts", 0),
               c.get("faces_with_a_count", 0),
               _share_text(1.0 - float(
                   c.get("share_of_count_faces_where_a_duplicate_is_invisible") or 0.0)),
               c.get("faces_whose_count_nothing_can_contradict", 0),
               c.get("faces_publishing_a_duplicate_row_right_now", 0),
               c.get("duplicate_rows_published_total", 0)))
    if verdict == V_MAJORITY_INVISIBLE:
        tail = ("-- the count is a receipt that cannot fail: %d faces print one and no row anywhere"
                % (c.get("by_witness") or {}).get(W_COUNT_ONLY, 0))
    elif verdict == V_SPLIT:
        tail = ("-- and only %d of the counted faces print a dedupe field or a distinct count, so "
                "even where the rows exist the count itself is not what would catch a duplicate"
                % ((c.get("by_class") or {}).get(D_DIRECT, 0)))
    elif verdict == V_ALL_VISIBLE:
        tail = "-- every counted face publishes the rows a duplicate would show in"
    else:
        tail = "-- this instrument has nothing to decide"
    return head + " " + tail


def _share_text(x):
    return "%s%%" % round(100.0 * float(x or 0.0), 1)


# --------------------------------------------------------------------------- face
def build(write=True, root=None):
    root = root or ROOT
    sc = scan(root)
    counts = summarise(sc)
    faces = sorted(sc["faces"], key=lambda f: (f["class"], f["face"]))
    face = {
        "study": "E601_dup_witness",
        "evidence_cutoff": _cutoff(faces),
        "witness_vocabulary": {
            "source": "e597.witness_class (E597 r1626 count-block vocabulary)",
            "witnesses": list(WITNESSES),
            "identity_keys": list(BAR_IDENTITY_KEYS),
            "distinct_or_dedupe_pattern": RE_WITNESS_FIELD.pattern,
        },
        "class_vocabulary": list(CLASSES),
        "count_match_vocabulary": list(MATCHES),
        "counts": counts,
        "faces": faces,
        "too_big": sc["too_big"],
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, verdict_from(counts)),
        "limits": [
            "the count vocabulary and the count-block walker are e597's; a face that states a bar "
            "count under a name outside that vocabulary is not in this population",
            "a 'duplicated row' is a repeat of the whole object after a json round-trip; two rows "
            "that differ in any field are two rows even if they describe one bar",
            "the distinct-bar read is only published when the series carries one of %s as a key"
            % (list(SERIES_KEY_CANDIDATES),),
            "a series longer than %d rows is measured on its head; duplicates past that point are "
            "not counted" % DUP_ROWS_CAP,
            "at most %d series per face are measured, so a face with more than that is graded on "
            "its first %d" % (SERIES_PER_FACE, SERIES_PER_FACE),
            "faces above %d bytes are counted as unreadable rather than parsed" % READ_CAP,
            "this study reads results/** and docs/** and excludes its own two published files",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def _cutoff(faces):
    """The newest date a counted face states anywhere in the payload it publishes."""
    import re as _re
    best = ""
    for f in faces:
        for s in f["series"]:
            for sig in s.get("sample_duplicates") or []:
                for m in _re.finditer(r"\d{4}-\d{2}-\d{2}", sig or ""):
                    if m.group(0) > best:
                        best = m.group(0)
    return best


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, SELF_STEM + "-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face.get("counts") or {}
    faces = face.get("faces") or []
    if not faces:
        p.append("the face publishes no per-face rows")
    by_witness = {w: 0 for w in WITNESSES}
    by_class = {c: 0 for c in CLASSES}
    by_match = {m: 0 for m in MATCHES}
    for f in faces:
        for k in ("face", "blocks", "witness", "series", "class", "duplicate_rows_published"):
            if k not in f:
                p.append("face row %s lacks %s" % (f.get("face"), k))
                break
        if f.get("witness"):
            if f["witness"] not in WITNESSES:
                p.append("face %s carries an unknown witness %r" % (f.get("face"), f["witness"]))
                break
            by_witness[f["witness"]] += 1
        if f.get("class") not in CLASSES:
            p.append("face %s carries an unknown class %r" % (f.get("face"), f.get("class")))
            break
        by_class[f["class"]] += 1
        expected_class = face_class(f.get("witness"), bool(f.get("series")),
                                    f.get("duplicate_rows_published") or 0)
        if f["class"] != expected_class:
            p.append("face %s grades itself %r, the rule says %r"
                     % (f.get("face"), f["class"], expected_class))
            break
        for s in f.get("series") or []:
            missing = [k for k in REQUIRED_SERIES_KEYS if k not in s]
            if missing:
                p.append("series %s%s lacks %s" % (f.get("face"), s.get("at"), ",".join(missing)))
                break
            if s["rows"] - s["rows_distinct"] != s["duplicate_rows"]:
                p.append("series %s%s says %d duplicate rows but %d rows minus %d distinct"
                         % (f.get("face"), s.get("at"), s["duplicate_rows"], s["rows"],
                            s["rows_distinct"]))
                break
            if s["count_match"] not in MATCHES:
                p.append("series %s%s carries an unknown count match %r"
                         % (f.get("face"), s.get("at"), s["count_match"]))
                break
            if s["count_match"] != count_match(s["rows"], s["rows_distinct"], s["count_value"]):
                p.append("series %s%s says %r against rows=%r distinct=%r count=%r"
                         % (f.get("face"), s.get("at"), s["count_match"], s["rows"],
                            s["rows_distinct"], s["count_value"]))
                break
            by_match[s["count_match"]] += 1
    for w in WITNESSES:
        if (counts.get("by_witness") or {}).get(w) != by_witness[w]:
            p.append("witness %s is %r but the face rows say %d"
                     % (w, (counts.get("by_witness") or {}).get(w), by_witness[w]))
            break
    for c in CLASSES:
        if (counts.get("by_class") or {}).get(c) != by_class[c]:
            p.append("class %s is %r but the face rows say %d"
                     % (c, (counts.get("by_class") or {}).get(c), by_class[c]))
            break
    for m in MATCHES:
        if (counts.get("by_count_match") or {}).get(m) != by_match[m]:
            p.append("count match %s is %r but the series rows say %d"
                     % (m, (counts.get("by_count_match") or {}).get(m), by_match[m]))
            break
    invisible = by_class[D_NO_ROWS]
    if counts.get("faces_whose_count_nothing_can_contradict") != invisible:
        p.append("faces_whose_count_nothing_can_contradict is %r but the classes say %d"
                 % (counts.get("faces_whose_count_nothing_can_contradict"), invisible))
    counted = sum(1 for f in faces if f.get("blocks"))
    if counts.get("faces_with_a_count") != counted:
        p.append("faces_with_a_count is %r but %d faces carry a block"
                 % (counts.get("faces_with_a_count"), counted))
    if counts.get("blocks_total") != sum(f.get("blocks") or 0 for f in faces):
        p.append("blocks_total is %r but the rows sum to %d"
                 % (counts.get("blocks_total"),
                    sum(f.get("blocks") or 0 for f in faces)))
    if counts.get("series_total") != sum(len(f.get("series") or []) for f in faces):
        p.append("series_total is %r but the rows sum to %d"
                 % (counts.get("series_total"),
                    sum(len(f.get("series") or []) for f in faces)))
    if counts.get("faces_with_a_series") != sum(1 for f in faces if f.get("series")):
        p.append("faces_with_a_series is %r but %d faces publish a series"
                 % (counts.get("faces_with_a_series"),
                    sum(1 for f in faces if f.get("series"))))
    dup_total = sum(f.get("duplicate_rows_published") or 0 for f in faces)
    if counts.get("duplicate_rows_published_total") != dup_total:
        p.append("duplicate_rows_published_total is %r but the rows sum to %d"
                 % (counts.get("duplicate_rows_published_total"), dup_total))
    if counts.get("faces_publishing_a_duplicate_row_right_now") != sum(
            1 for f in faces if (f.get("duplicate_rows_published") or 0) > 0):
        p.append("faces_publishing_a_duplicate_row_right_now does not re-derive from the rows")
    share = (round(float(invisible) / float(counted), 4) if counted else 0.0)
    if counts.get("share_of_count_faces_where_a_duplicate_is_invisible") != share:
        p.append("the invisible share is %r but %d/%d = %r"
                 % (counts.get("share_of_count_faces_where_a_duplicate_is_invisible"),
                    invisible, counted, share))
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    if not (face.get("witness_vocabulary") or {}).get("witnesses"):
        p.append("the witness vocabulary is not published")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    # 1-4 the vocabulary this study inherits from E597 is the one it says it inherits
    chk("1 the count vocabulary is E597's", COUNT_KEYS == e597.COUNT_KEYS)
    chk("2 the witness classes are E597's", WITNESSES == (e597.W_DEDUPE, e597.W_IDENTITY,
                                                          e597.W_COUNT_ONLY))
    chk("3 the identity keys are E597's", BAR_IDENTITY_KEYS == e597.BAR_IDENTITY_KEYS)
    chk("4 a count-only block is graded as count-only",
        witness_of_blocks([{"bars": 10}]) == W_COUNT_ONLY)

    # 5-9 series measurement
    rows = [{"bar": "2026-11-06", "v": 1}, {"bar": "2026-11-05", "v": 2}]
    sh = series_shape(rows)
    chk("5 distinct rows are counted", sh["rows"] == 2 and sh["rows_distinct"] == 2
        and sh["duplicate_rows"] == 0, sh)
    dupped = rows + [dict(rows[0])]
    sh2 = series_shape(dupped)
    chk("6 a repeated row is a duplicate", sh2["duplicate_rows"] == 1, sh2)
    chk("7 the bar key is found by name", sh2["bar_key"] == "bar"
        and sh2["distinct_bar_values"] == 2, sh2)
    chk("8 two rows for one bar are not a duplicated row",
        series_shape([{"bar": "d", "v": 1}, {"bar": "d", "v": 2}])["duplicate_rows"] == 0)
    chk("9 a series with no bar key publishes no distinct-bar read",
        series_shape([{"a": 1}, {"a": 2}])["distinct_bar_values"] is None)

    # 10-13 how a count lines up with the rows
    chk("10 a count equal to the rows says so",
        count_match(3, 2, 3) == MATCH_ROWS)
    chk("11 a count equal to the distinct rows has its own class",
        count_match(3, 2, 2) == MATCH_DISTINCT)
    chk("12 a count equal to neither has its own class",
        count_match(3, 2, 9) == MATCH_NEITHER)
    chk("13 no count is not a match of zero", count_match(3, 2, None) == MATCH_NO_COUNT)

    # 14-18 where a duplicated row lands
    chk("14 a count with no rows can be contradicted by nothing",
        face_class(W_COUNT_ONLY, False, 0) == D_NO_ROWS)
    chk("15 a dedupe field shows it directly", face_class(W_DEDUPE, True, 1) == D_DIRECT)
    chk("16 a count-only witness still shows it if the rows are published",
        face_class(W_COUNT_ONLY, True, 0) == D_ROWS)
    chk("17 an identity pair beside present duplicates is still the rows that show them",
        face_class(W_IDENTITY, True, 2) == D_ROWS_DUP)
    chk("18 a dedupe field wins over duplicate rows already present",
        face_class(W_DEDUPE, True, 2) == D_DIRECT)

    # 19-21 summariser and verdict, in both directions
    def srow(face, rows, distinct, dup, count):
        return {"face": face, "at": "/rows", "rows": rows, "rows_distinct": distinct,
                "duplicate_rows": dup, "count_fields": ["bars"], "count_value": count,
                "count_match": count_match(rows, distinct, count)}
    faces = [
        {"face": "a.json", "blocks": 1, "witness": W_COUNT_ONLY,
         "series": [srow("a.json", 3, 2, 1, 3)],
         "series_rows": 1, "class": D_ROWS_DUP, "duplicate_rows_published": 1},
        {"face": "b.json", "blocks": 1, "witness": W_DEDUPE,
         "series": [srow("b.json", 2, 2, 0, 2)],
         "series_rows": 1, "class": D_DIRECT, "duplicate_rows_published": 0},
        {"face": "c.json", "blocks": 1, "witness": W_COUNT_ONLY, "series": [],
         "series_rows": 0, "class": D_NO_ROWS, "duplicate_rows_published": 0},
    ]
    c = summarise({"faces": faces, "faces_read": 3, "unreadable": 0, "too_big": []})
    chk("19 the summariser counts the classes", c["by_class"][D_ROWS_DUP] == 1
        and c["by_class"][D_NO_ROWS] == 1 and c["by_class"][D_DIRECT] == 1, c["by_class"])
    chk("20 one of three counted faces cannot be contradicted and the share says so",
        c["faces_whose_count_nothing_can_contradict"] == 1
        and c["share_of_count_faces_where_a_duplicate_is_invisible"] == 0.3333, c)
    chk("21 a minority-invisible board forces the split verdict",
        verdict_from(c) == V_SPLIT)
    good_scan = {"faces": [{"face": "d.json", "blocks": 1, "witness": W_DEDUPE,
                            "series": [{"rows": 2, "rows_distinct": 2, "duplicate_rows": 0,
                                        "count_value": 2, "count_match": MATCH_ROWS}],
                            "series_rows": 1, "class": D_DIRECT,
                            "duplicate_rows_published": 0}],
                 "faces_read": 1, "unreadable": 0, "too_big": []}
    cg = summarise(good_scan)
    chk("22 a fully visible board forces the all-visible verdict",
        verdict_from(cg) == V_ALL_VISIBLE, cg)

    # 23-27 the guard refuses drift in each direction it can drift
    def synth(counts_block, face_rows):
        return {"study": "x", "witness_vocabulary": {"witnesses": list(WITNESSES)},
                "counts": counts_block, "faces": face_rows,
                "verdict": verdict_from(counts_block),
                "answer": answer_sentence(counts_block, verdict_from(counts_block))}

    good = synth(c, faces)
    chk("23 a clean synthetic face passes the guard", face_problems(good) == [],
        face_problems(good))
    bad = json.loads(json.dumps(good))
    bad["counts"]["by_class"][D_NO_ROWS] += 1
    chk("24 a class count that does not re-derive is caught",
        any("but the face rows say" in s for s in face_problems(bad)))
    bad = json.loads(json.dumps(good))
    bad["faces"][1]["class"] = D_NO_ROWS
    chk("25 a face that grades itself against the rule is caught",
        any("the rule says" in s for s in face_problems(bad)))
    bad = json.loads(json.dumps(good))
    bad["faces"][0]["series"][0]["duplicate_rows"] = 0
    chk("26 a duplicate count that does not re-derive from rows is caught",
        any("rows minus" in s for s in face_problems(bad)))
    bad = json.loads(json.dumps(good))
    bad["verdict"] = V_ALL_VISIBLE
    chk("27 a verdict that contradicts the counts is caught",
        any("verdict" in s for s in face_problems(bad)))

    # 28-30 the scan reads a real population and excludes its own face
    tmp = os.path.join(ROOT, "results", "_e601_selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        with io.open(os.path.join(tmp, "DUPWITNESS-x.json"), "w", encoding="utf-8") as fh:
            fh.write('{"bars": 3, "rows": [{"bar": "2026-11-06"}, {"bar": "2026-11-06"}]}')
        sc = scan(ROOT)
        seen_self = [f["face"] for f in sc["faces"] if "DUPWITNESS-x.json" in f["face"]]
        chk("28 this study does not scan its own published face", not seen_self, seen_self)
        chk("29 the scan finds faces carrying a count",
            len([f for f in sc["faces"] if f["blocks"]]) > 50,
            len([f for f in sc["faces"] if f["blocks"]]))
        chk("30 the scan finds faces that publish a series",
            len([f for f in sc["faces"] if f["series"]]) > 20,
            len([f for f in sc["faces"] if f["series"]]))
    finally:
        for f2 in glob.glob(os.path.join(tmp, "*")):
            os.remove(f2)
        os.rmdir(tmp)

    print("\n%d/%d PASS" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "build").lower()
    if cmd == "selftest":
        return selftest()
    face, problems = build(write=(cmd in ("build", "run")))
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("faces_read=%d unreadable=%d count_faces=%d count_beside_rows=%d series=%d"
          % (c["faces_read"], c["faces_unreadable"], c["faces_with_a_count"],
             c["faces_with_a_count_beside_the_rows_it_counts"], c["series_total"]))
    print("by_witness=" + json.dumps(c["by_witness"], sort_keys=True))
    print("by_class=" + json.dumps(c["by_class"], sort_keys=True))
    print("by_count_match=" + json.dumps(c["by_count_match"], sort_keys=True))
    print("invisible=%d share=%s duplicates_now=%d/%d rows"
          % (c["faces_whose_count_nothing_can_contradict"],
             _share_text(c["share_of_count_faces_where_a_duplicate_is_invisible"]),
             c["faces_publishing_a_duplicate_row_right_now"],
             c["duplicate_rows_published_total"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd in ("check", "verify"):
        try:
            with io.open(OUT_PATH, encoding="utf-8") as fh:
                published = json.load(fh)
        except (OSError, ValueError) as exc:
            print("PROBLEMS: cannot read the published face: %s" % exc)
            return 1
        drift = [k for k in ("counts", "verdict", "faces", "witness_vocabulary",
                             "class_vocabulary", "count_match_vocabulary")
                 if published.get(k) != face.get(k)]
        print("problems=[]" if not drift else "DRIFT: " + ",".join(drift))
        if drift:
            return 1
        if cmd == "verify":
            print("verify=identical")
        return 0
    if cmd in ("build", "run"):
        print("wrote " + os.path.relpath(OUT_PATH, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))