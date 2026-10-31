"""Vintage freeze for the BAND family studies.

Every study in the `results/state_tilt/BAND*` family censuses the family's own published faces, so the
universe it reads GROWS by one face each time a sibling study publishes.  A face that re-derived its
summary over the live directory therefore drifted on every new publication and stopped matching what
it published -- the reason smoke legs 81/82/86/87 went red on 2026-10-31 while nothing was actually
wrong with the numbers (E286 32 -> 34 faces, E281 27 -> 34, E282 55 -> 67).

A published face is a VINTAGE: re-deriving it must use the faces that existed when it published.  A
study only widens its universe by running again, which publishes a new generated stamp and therefore
a new vintage.  The rule is mechanical -- each face carries its own `generated` stamp, so the universe
at publish time is "the faces whose own stamp is not later than mine".

The freeze is disclosed on the face, never silent: `universe_vintage` names the faces it dropped and
how many the live directory now holds, so a reader can see that the directory grew and that this
number is the older reading rather than a wider one.
"""
import io
import json
import os

STAMP_LEN = 19   # 'YYYY-MM-DDTHH:MM:SS'


def _parse(stamp):
    """Normalise the several stamp spellings the family uses; None when unparseable."""
    if not isinstance(stamp, str):
        return None
    text = stamp.strip().replace("/", "-").replace(" ", "T")
    if len(text) < STAMP_LEN:
        return None
    return text[:STAMP_LEN]


def _face_stamp(path):
    """The face's own generated stamp, falling back to the file's mtime (never to 'now')."""
    try:
        with io.open(path, encoding="utf-8") as fh:
            face = json.load(fh)
    except Exception:
        face = None
    if isinstance(face, dict):
        stamp = _parse(face.get("generated"))
        if stamp:
            return stamp
    try:
        import datetime
        return datetime.datetime.utcfromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None


def published_names(outdir, face_names, keys):
    """The universe this face already published, read from the face itself.

    Authoritative when the face stores its census as a name list: a face that is re-generated in
    place keeps the same name but a later stamp, so a stamp rule cannot tell "published after this
    study" from "re-run after this study" (BANDPATH-2026-10-30 was already in E286's 07:35 universe
    and was rewritten at 07:44).  A stored list has no such ambiguity.
    """
    for name in face_names:
        try:
            with io.open(os.path.join(outdir, name), encoding="utf-8") as fh:
                face = json.load(fh)
        except Exception:
            continue
        if not isinstance(face, dict):
            continue
        for key in keys:
            value = face.get(key)
            if isinstance(value, list) and value and all(isinstance(x, str) for x in value):
                return list(value), name
    return None, None


def vintage_names(outdir, names, cutoff):
    """Split `names` into (kept, dropped) by each face's own stamp against `cutoff`."""
    if not cutoff:
        return list(names), []
    kept, dropped = [], []
    for name in names:
        stamp = _face_stamp(os.path.join(outdir, name))
        if stamp is None or stamp <= cutoff:
            kept.append(name)   # an undated face cannot be shown to postdate the study: keep it
        else:
            dropped.append(name)
    return kept, dropped


def note(used, dropped, live_total, frozen_from, cutoff):
    """The disclosure block a face carries so the freeze is visible instead of silent."""
    return {
        "frozen_from": frozen_from,
        "generated": cutoff,
        "faces_used": len(used),
        "faces_in_directory_now": live_total,
        "faces_excluded_as_later": sorted(dropped),
        "rule": "a face re-derives against the universe that existed when it published; only a new "
                "run widens it, and that run publishes a new stamp",
    }


def selftest():
    """Legs for the freeze rule; the caller folds them into its own selftest."""
    import tempfile
    legs = []

    def leg(name, cond, detail=""):
        legs.append((bool(cond), name, detail))

    leg("V1 a stamp is normalised across the spellings the family uses",
        _parse("2026-10-31T06:31:08") == "2026-10-31T06:31:08"
        and _parse("2026-10-31 06:31:08") == "2026-10-31T06:31:08"
        and _parse("2026-10-31") is None and _parse(None) is None)

    tmp = tempfile.mkdtemp(prefix="vintage-")
    def write(name, stamp, payload=None):
        body = payload if payload is not None else {"generated": stamp}
        with io.open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(body))

    write("OLD.json", "2026-10-30T10:00:00")
    write("NEW.json", "2026-10-31T09:00:00")
    write("UNDATED.json", None, payload={"study": "x"})

    kept, dropped = vintage_names(tmp, ["OLD.json", "NEW.json", "UNDATED.json"], "2026-10-31T06:31:08")
    leg("V2 a later stamp is dropped and an undated face is kept (never dropped on a guess)",
        kept == ["OLD.json", "UNDATED.json"] and dropped == ["NEW.json"], (kept, dropped))

    kept_all, dropped_all = vintage_names(tmp, ["OLD.json", "NEW.json"], None)
    leg("V3 no cutoff keeps everything -- an unpublished study has no vintage to honour",
        kept_all == ["OLD.json", "NEW.json"] and dropped_all == [])

    write("HASLIST.json", None, payload={"faces_censused": ["A.json", "B.json"]})
    names, src = published_names(tmp, ("HASLIST.json",), ("faces_censused",))
    leg("V4 a stored name list is preferred and names its source",
        names == ["A.json", "B.json"] and src == "HASLIST.json")

    missing, src2 = published_names(tmp, ("OLD.json",), ("faces_censused",))
    leg("V5 a face without a name list yields nothing (the caller falls back to stamps)",
        missing is None and src2 is None)

    n = note(["A.json"], ["B.json"], 3, "FACE.json", "2026-10-31T06:31:08")
    leg("V6 the note carries every count a reader needs to see the freeze",
        n["faces_used"] == 1 and n["faces_in_directory_now"] == 3
        and n["faces_excluded_as_later"] == ["B.json"] and n["frozen_from"] == "FACE.json")
    return legs