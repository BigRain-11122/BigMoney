#!/usr/bin/env python
"""E600 -- does a bar date pick out one face, or does it return a set?

E596 (r1627) showed that on the 18 faces stating both a pricing and a decision bar the two roles
state different dates, so a name join is load-bearing there.  That argument only bites if the
consumer could otherwise join on the date at all.  This study asks the other half of the question:
take every date a face states next to a bar name and count how many distinct faces state it, and
under which roles.

Per date the lookup lands on one of three things:
  picks_out_one_face                      -- exactly one face states the date
  picks_out_several_faces_under_one_role   -- several faces, but they all call it the same role
                                             (you can still say which bar you mean, not which face)
  picks_out_several_faces_under_several_roles -- several faces and several roles: the date tells you
                                             neither the face nor the bar

A face that carries a bar name but states no ISO date is unreachable by a date-keyed join at all
(the "nothing" arm) and is published by name.

Output: results/state_tilt/DATEFACEUNIQUE.json (+ -latest.json)
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

import e596_value_join_vs_name_join as e596                                     # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "DATEFACEUNIQUE.json")
SELF_STEM = "DATEFACEUNIQUE"

# the bar vocabulary is the one the dialect face asserts (E586 field lists via E594/E596); this
# study does not grade a spelling the dialect study does not grade
KEY_ROLES = e596.KEY_ROLES
MULTI_ROLE_KEYS = e596.MULTI_ROLE_KEYS
FACE_GLOBS = e596.FACE_GLOBS
READ_CAP = e596.READ_CAP
date_of = e596.date_of
roles_of = e596.roles_of
walk_face = e596.walk_face

PATHS_PER_ROW = 10          # sample face paths per date row (the count is the measure, not the list)
ONE_FACE_SAMPLE = 50        # one-face dates printed as ordinary rows
COLLISION_TOP = 20          # date rows ranked by face count, published as the head of the table

C_ONE_FACE = "picks_out_one_face"
C_MANY_ONE_ROLE = "picks_out_several_faces_under_one_role"
C_MANY_MANY_ROLES = "picks_out_several_faces_under_several_roles"
CLASSES = (C_ONE_FACE, C_MANY_ONE_ROLE, C_MANY_MANY_ROLES)

V_DATE_RETURNS_A_SET = ("some_date_is_stated_by_more_than_one_face_so_a_date_keyed_lookup_returns_a"
                        "_set_and_the_name_join_is_still_required")
V_DATE_IDENTIFIES_A_FACE = ("every_date_a_face_states_is_stated_by_exactly_one_face_so_a_date_keyed"
                            "_lookup_identifies_the_face_on_this_population")
V_NO_DATES = "no_face_states_a_bar_date_so_the_question_has_no_population"

REQUIRED_ROW_KEYS = ("date", "face_count", "role_count", "roles", "class", "sample_paths")


# --------------------------------------------------------------------------- pure helpers
def date_roles(fields):
    """{date: {role: set(paths)}} is not knowable from one face alone; this is the per-face shape."""
    out = {}
    for f in fields:
        if not f["date"]:
            continue
        for role in roles_of(f):
            out.setdefault(f["date"], set()).add(role)
    return {d: sorted(r) for d, r in sorted(out.items())}


def classify_date(face_count, role_count):
    """Where a date-keyed lookup lands: the face, a role only, or a set of both."""
    if face_count <= 1:
        return C_ONE_FACE
    return C_MANY_ONE_ROLE if role_count <= 1 else C_MANY_MANY_ROLES


def row_of(date, faces_by_role, roles_global):
    """One published date row.  faces_by_role is {role: set(paths)} for this date."""
    faces = set()
    for paths in faces_by_role.values():
        faces |= paths
    roles = sorted(r for r in faces_by_role if faces_by_role[r])
    return {
        "date": date,
        "face_count": len(faces),
        "role_count": len(roles),
        "roles": roles,
        "class": classify_date(len(faces), len(roles)),
        "sample_paths": sorted(faces)[:PATHS_PER_ROW],
        "faces_per_role": {r: len(faces_by_role[r]) for r in roles},
        "roles_outside_the_vocabulary": sorted(r for r in roles if r not in roles_global),
    }


def summarise(index, rows, no_date_faces, unreadable, faces_read):
    """Every count the face publishes, derived from the same objects the reader sees."""
    by_class = {c: 0 for c in CLASSES}
    for date, count in index.items():
        by_class[classify_date(count, len(rows.get(date, {}).get("roles", [])))] += 1
    several = [d for d, n in index.items() if n > 1]
    one = [d for d, n in index.items() if n == 1]
    role_counts = {}
    for r in rows.values():
        for role in r["roles"]:
            role_counts[role] = role_counts.get(role, 0) + 1
    ranked = sorted(((n, d) for d, n in index.items()), reverse=True)
    return {
        "faces_read": faces_read,
        "faces_unreadable": unreadable,
        "faces_carrying_a_bar_name": faces_read - unreadable,
        "faces_stating_a_date": faces_read - unreadable - len(no_date_faces),
        "faces_with_a_bar_and_no_date": len(no_date_faces),
        "dates_total": len(index),
        "by_class": by_class,
        "dates_stated_by_more_than_one_face": len(several),
        "dates_stated_by_exactly_one_face": len(one),
        "dates_per_role": dict(sorted(role_counts.items())),
        "busiest_dates": [{"date": d, "face_count": n} for n, d in ranked[:COLLISION_TOP]],
        "max_faces_on_one_date": ranked[0][0] if ranked else 0,
        "max_faces_on_one_date_at": ranked[0][1] if ranked else "",
    }


def verdict_from(counts):
    if counts.get("dates_total", 0) == 0:
        return V_NO_DATES
    if counts.get("dates_stated_by_more_than_one_face", 0) > 0:
        return V_DATE_RETURNS_A_SET
    return V_DATE_IDENTIFIES_A_FACE


def answer_sentence(counts, verdict):
    total = counts.get("dates_total", 0)
    many = counts.get("dates_stated_by_more_than_one_face", 0)
    bc = counts.get("by_class", {})
    head = ("%d of %d dates a face states next to a bar name are stated by more than one face "
            "(busiest: %s by %d faces)"
            % (many, total, counts.get("max_faces_on_one_date_at", "-"),
               counts.get("max_faces_on_one_date", 0))) if total else "no face states a bar date"
    if verdict == V_DATE_RETURNS_A_SET:
        tail = ("so a date-keyed lookup returns a set on those dates -- %d of them do not even agree "
                "on the role -- and the name join remains the only way to say which face and which "
                "bar a consumer means; %d dates do identify a single face, and %d faces carry a bar "
                "name with no date at all, so a date-keyed join cannot reach them"
                % (bc.get(C_MANY_MANY_ROLES, 0), bc.get(C_ONE_FACE, 0),
                   counts.get("faces_with_a_bar_and_no_date", 0)))
    elif verdict == V_DATE_IDENTIFIES_A_FACE:
        tail = "so on this population the date alone is a sufficient key"
    else:
        tail = "so this instrument has nothing to decide"
    return head + "; " + tail


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


def scan(root=None):
    """{date: {role: {paths}}}, faces with a bar and no date, unreadable count, faces read."""
    root = root or ROOT
    index = {}
    no_date_faces = []
    unreadable = 0
    paths = faces_on_disk(root)
    for rel in paths:
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > READ_CAP:
                unreadable += 1
                continue
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                payload = json.load(fh)
        except (ValueError, OSError):
            unreadable += 1
            continue
        fields, _keys = walk_face(payload)
        if not fields:
            continue
        per_face = date_roles(fields)
        if not per_face:
            no_date_faces.append(rel)
            continue
        for date, roles in per_face.items():
            block = index.setdefault(date, {})
            for role in roles:
                block.setdefault(role, set()).add(rel)
    return {"index": index, "no_date_faces": sorted(no_date_faces),
            "unreadable": unreadable, "faces_read": len(paths)}


def rows_from(index, roles_global):
    rows = {}
    for date, roles_block in index.items():
        row = row_of(date, roles_block, roles_global)
        rows[date] = row
    return rows


def publish_rows(rows):
    """Every date stated by more than one face, plus a bounded sample of the single-face dates.

    The date index carries the face count of every date (small, and it is what the class arithmetic
    re-derives from); the rows carry the role detail for the dates where a collision is possible.
    """
    several = [rows[d] for d in sorted(rows) if rows[d]["face_count"] > 1]
    one = [rows[d] for d in sorted(rows) if rows[d]["face_count"] == 1]
    several_ranked = sorted(several, key=lambda r: (-r["face_count"], r["date"]))
    return {
        "published": several_ranked + one[:ONE_FACE_SAMPLE],
        "not_published": {
            "single_face_dates_sampled_out": max(0, len(one) - ONE_FACE_SAMPLE),
            "dates_with_more_than_one_face": len(several),
        },
        "date_index": {d: rows[d]["face_count"] for d in sorted(rows)},
    }


def _cutoff(index):
    return max(index) if index else ""


# --------------------------------------------------------------------------- face
def build(write=True, root=None):
    root = root or ROOT
    sc = scan(root)
    roles_global = set(KEY_ROLES.values() and [r for rs in KEY_ROLES.values() for r in rs])
    index = sc["index"]
    rows = rows_from(index, roles_global)
    view = publish_rows(rows)
    counts = summarise(view["date_index"], rows, sc["no_date_faces"], sc["unreadable"],
                       sc["faces_read"])
    face = {
        "study": "E600_date_face_unique",
        "evidence_cutoff": _cutoff(index),
        "role_vocabulary": {"source": "e594.SPELLINGS families (E586 field lists)",
                            "roles": sorted(roles_global),
                            "names": {k: KEY_ROLES[k] for k in sorted(KEY_ROLES)},
                            "names_in_more_than_one_family": MULTI_ROLE_KEYS},
        "date_index": view["date_index"],
        "date_rows": view["published"],
        "not_published": view["not_published"],
        "faces_with_a_bar_and_no_date": sc["no_date_faces"],
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, verdict_from(counts)),
        "limits": [
            "a date is read from an ISO-8601 prefix on a string value; an epoch integer or a prose "
            "date states nothing to this instrument and puts the face in the no-date list",
            "a role is decided by the key name from the E594 dialect vocabulary; a bar stored under "
            "a name outside that vocabulary is invisible here",
            "date rows publish at most %d sample paths per date; the count is the measure"
            % PATHS_PER_ROW,
            "faces above %d bytes are counted as unreadable rather than parsed" % READ_CAP,
            "this study reads the same population as E596 and excludes its own two published files",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


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
    index = face.get("date_index") or {}
    rows = face.get("date_rows") or []
    npb = face.get("not_published") or {}
    if not index:
        p.append("the face publishes no date index")
    if not rows:
        p.append("the face publishes no date rows")
    rows_by_date = {r["date"]: r for r in rows}
    for r in rows:
        missing = [k for k in REQUIRED_ROW_KEYS if k not in r]
        if missing:
            p.append("date row %s lacks %s" % (r.get("date"), ",".join(missing)))
            break
        if r["class"] != classify_date(r["face_count"], r["role_count"]):
            p.append("date row %s grades itself %r against %d faces / %d roles"
                     % (r["date"], r["class"], r["face_count"], r["role_count"]))
            break
        if len(r["roles"]) != r["role_count"]:
            p.append("date row %s publishes %d roles but says %d"
                     % (r["date"], len(r["roles"]), r["role_count"]))
            break
        if r["face_count"] != index.get(r["date"]):
            p.append("date row %s states %d faces but the index says %r"
                     % (r["date"], r["face_count"], index.get(r["date"])))
            break
        if len(r["sample_paths"]) != min(PATHS_PER_ROW, r["face_count"]):
            p.append("date row %s prints %d sample paths for %d faces"
                     % (r["date"], len(r["sample_paths"]), r["face_count"]))
            break
    # the class counts must re-derive from the index the face publishes, with the sampled-out rows
    # counted back in (a sample is legitimate only when the face says how many rows it did not print)
    sampled = npb.get("single_face_dates_sampled_out")
    if not isinstance(sampled, int):
        p.append("the not-published block does not state how many single-face dates were sampled out")
        sampled = None
    by_class = {c: 0 for c in CLASSES}
    for date, count in index.items():
        row = rows_by_date.get(date)
        roles = row["roles"] if row else []
        by_class[classify_date(count, len(roles))] += 1
    published_one = sum(1 for r in rows if r["face_count"] == 1)
    if sampled is not None:
        by_class[C_ONE_FACE] = published_one + sampled
    for c in CLASSES:
        if (counts.get("by_class") or {}).get(c) != by_class[c]:
            p.append("class %s is %r but re-derives to %r from the published index"
                     % (c, (counts.get("by_class") or {}).get(c), by_class[c]))
            break
    if npb.get("dates_with_more_than_one_face") != by_class[C_MANY_ONE_ROLE] \
            + by_class[C_MANY_MANY_ROLES]:
        p.append("the not-published block says %r dates carry more than one face, the index says %d"
                 % (npb.get("dates_with_more_than_one_face"),
                    by_class[C_MANY_ONE_ROLE] + by_class[C_MANY_MANY_ROLES]))
    if counts.get("dates_total") != len(index):
        p.append("dates_total is %r but the index holds %d" % (counts.get("dates_total"),
                                                               len(index)))
    if counts.get("dates_stated_by_more_than_one_face") != by_class[C_MANY_ONE_ROLE] \
            + by_class[C_MANY_MANY_ROLES]:
        p.append("dates_stated_by_more_than_one_face is %r but the class split says %d"
                 % (counts.get("dates_stated_by_more_than_one_face"),
                    by_class[C_MANY_ONE_ROLE] + by_class[C_MANY_MANY_ROLES]))
    if counts.get("faces_carrying_a_bar_name") != counts.get("faces_read", 0) - counts.get(
            "faces_unreadable", 0):
        p.append("faces_carrying_a_bar_name is %r but read-minus-unreadable is %d"
                 % (counts.get("faces_carrying_a_bar_name"),
                    counts.get("faces_read", 0) - counts.get("faces_unreadable", 0)))
    if counts.get("faces_stating_a_date") != counts.get("faces_carrying_a_bar_name", 0) \
            - counts.get("faces_with_a_bar_and_no_date", 0):
        p.append("faces_stating_a_date is %r but bar-named minus no-date is %d"
                 % (counts.get("faces_stating_a_date"),
                    counts.get("faces_carrying_a_bar_name", 0)
                    - counts.get("faces_with_a_bar_and_no_date", 0)))
    if counts.get("dates_stated_by_exactly_one_face") != by_class[C_ONE_FACE]:
        p.append("dates_stated_by_exactly_one_face is %r but the class split says %d"
                 % (counts.get("dates_stated_by_exactly_one_face"), by_class[C_ONE_FACE]))
    no_date = face.get("faces_with_a_bar_and_no_date") or []
    if counts.get("faces_with_a_bar_and_no_date") != len(no_date):
        p.append("faces_with_a_bar_and_no_date is %r but %d are listed"
                 % (counts.get("faces_with_a_bar_and_no_date"), len(no_date)))
    if counts.get("dates_per_role"):
        recounted = {}
        for r in rows:
            for role in r["roles"]:
                recounted[role] = recounted.get(role, 0) + 1
        for role, n in recounted.items():
            if (counts["dates_per_role"] or {}).get(role, 0) < n:
                p.append("dates_per_role says %r for %r but the published rows carry %d"
                         % ((counts["dates_per_role"] or {}).get(role), role, n))
                break
    if counts.get("max_faces_on_one_date") != max(index.values() or [0]):
        p.append("max_faces_on_one_date is %r but the index peaks at %r"
                 % (counts.get("max_faces_on_one_date"), max(index.values() or [0])))
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    if not (face.get("role_vocabulary") or {}).get("roles"):
        p.append("the role vocabulary is not published")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    # 1-4 the shared vocabulary and date reader are inherited, not re-implemented
    chk("1 role vocabulary is the dialect face's", KEY_ROLES.get("pricing_bar") == ["pricing"])
    chk("2 a multi-family name is published under every family",
        KEY_ROLES.get("ticket_bar") == ["as_of", "pricing"], KEY_ROLES.get("ticket_bar"))
    chk("3 date_of takes the day from an ISO timestamp",
        date_of("2026-11-06T15:30:00+08:00") == "2026-11-06")
    chk("4 date_of refuses prose and integers",
        date_of("panel 2026-10-14 (bars due)") == "" and date_of(1762344000) == "")

    # 5-8 per-face date/role extraction
    f = [{"key": "pricing_bar", "role": "pricing", "date": "2026-11-06", "value_is_date": True},
         {"key": "book_decided_at", "role": "decision", "date": "2026-11-05",
          "value_is_date": True},
         {"key": "evidence_cutoff", "role": "evidence_cutoff", "date": "", "value_is_date": False}]
    dr = date_roles(f)
    chk("5 one face's dates and roles come out sorted",
        dr == {"2026-11-05": ["decision"], "2026-11-06": ["pricing"]}, dr)
    chk("6 a bar with no date contributes no date key", "" not in dr)
    multi = [{"key": "ticket_bar", "role": "as_of+pricing", "date": "2026-11-06",
              "value_is_date": True}]
    chk("7 a multi-family name speaks for both roles on its date",
        date_roles(multi) == {"2026-11-06": ["as_of", "pricing"]}, date_roles(multi))
    chk("8 the same date twice on one face is one key",
        len(date_roles(f + f)) == 2)

    # 9-12 the three landing classes
    chk("9 one face is a unique pick",
        classify_date(1, 1) == C_ONE_FACE)
    chk("10 several faces under one role is a role-only pick",
        classify_date(3, 1) == C_MANY_ONE_ROLE)
    chk("11 several faces under several roles is a set of both",
        classify_date(3, 2) == C_MANY_MANY_ROLES)
    row = row_of("2026-11-06", {"pricing": {"a.json", "b.json"}, "decision": {"c.json"}},
                 {"pricing", "decision"})
    chk("12 a row counts faces once and roles separately",
        row["face_count"] == 3 and row["role_count"] == 2
        and row["roles"] == ["decision", "pricing"]
        and row["faces_per_role"] == {"decision": 1, "pricing": 2}, row)

    # 13-17 summariser + verdict, in both directions
    idx = {"2026-11-06": 3, "2026-11-05": 1, "2026-11-04": 2}
    rows = {d: row_of(d, {"pricing": {"x%d.json" % i for i in range(n)}}, {"pricing"})
            for d, n in idx.items()}
    c = summarise(idx, rows, ["nodate.json"], 2, 6)
    chk("13 classes re-derive from the index",
        c["by_class"] == {C_ONE_FACE: 1, C_MANY_ONE_ROLE: 2, C_MANY_MANY_ROLES: 0}, c["by_class"])
    chk("14 the busiest date and its count are published",
        c["max_faces_on_one_date"] == 3 and c["max_faces_on_one_date_at"] == "2026-11-06", c)
    chk("15 a bar with no date is counted and listed",
        c["faces_with_a_bar_and_no_date"] == 1 and c["dates_per_role"] == {"pricing": 3},
        c["dates_per_role"])
    chk("16 a shared date forces the set verdict", verdict_from(c) == V_DATE_RETURNS_A_SET)
    one_only = summarise({"2026-11-06": 1},
                         {"2026-11-06": row_of("2026-11-06", {"pricing": {"a.json"}},
                                               {"pricing"})}, [], 0, 1)
    chk("17 unique dates give the identifying verdict",
        verdict_from(one_only) == V_DATE_IDENTIFIES_A_FACE)
    chk("18 no dates means no population",
        verdict_from(summarise({}, {}, [], 0, 0)) == V_NO_DATES)

    # 19-24 guard: the face must refuse drift in each direction it can drift
    view = publish_rows(rows)
    good = {"study": "x", "evidence_cutoff": "2026-11-06",
            "role_vocabulary": {"roles": ["pricing", "decision"]},
            "date_index": view["date_index"], "date_rows": view["published"],
            "not_published": view["not_published"],
            "faces_with_a_bar_and_no_date": ["nodate.json"],
            "counts": c, "verdict": verdict_from(c), "answer": answer_sentence(c, verdict_from(c))}
    chk("19 a clean synthetic face passes the guard", face_problems(good) == [], face_problems(good))
    bad = json.loads(json.dumps(good))
    bad["counts"]["by_class"][C_MANY_ONE_ROLE] += 1
    chk("20 a class count that does not re-derive is caught",
        any("re-derives" in s for s in face_problems(bad)))
    bad = json.loads(json.dumps(good))
    bad["date_rows"][0]["face_count"] += 1
    chk("21 a row count that disagrees with the index is caught",
        any("the index says" in s for s in face_problems(bad)))
    bad = json.loads(json.dumps(good))
    bad["verdict"] = V_DATE_IDENTIFIES_A_FACE
    chk("22 a verdict that contradicts the counts is caught",
        any("verdict" in s for s in face_problems(bad)))
    bad = json.loads(json.dumps(good))
    bad["not_published"]["single_face_dates_sampled_out"] += 1
    chk("23 a sampled-out count that does not reconcile is caught",
        any("re-derives" in s for s in face_problems(bad)))
    bad = json.loads(json.dumps(good))
    bad["faces_with_a_bar_and_no_date"] = []
    chk("24 a no-date list that does not match its count is caught",
        any("faces_with_a_bar_and_no_date" in s for s in face_problems(bad)))

    # 25-26 the scan excludes this study's own face and reads a real population
    tmp = os.path.join(ROOT, "results", "_e600_selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        with io.open(os.path.join(tmp, "DATEFACEUNIQUE-x.json"), "w", encoding="utf-8") as fh:
            fh.write('{"pricing_bar": "2026-11-06"}')
        sc = scan(ROOT)
        seen_self = [d for d, roles in sc["index"].items()
                     if any(n.endswith("DATEFACEUNIQUE-x.json")
                            for p in roles.values() for n in p)]
        chk("25 this study does not scan its own published face", not seen_self, seen_self)
        chk("26 the scan finds a populated date index", len(sc["index"]) > 10, len(sc["index"]))
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
    print("faces_read=%d unreadable=%d bar_named=%d no_date=%d dates=%d"
          % (c["faces_read"], c["faces_unreadable"], c["faces_carrying_a_bar_name"],
             c["faces_with_a_bar_and_no_date"], c["dates_total"]))
    print("by_class=" + json.dumps(c["by_class"], sort_keys=True))
    print("more_than_one_face=%d max=%d@%s"
          % (c["dates_stated_by_more_than_one_face"], c["max_faces_on_one_date"],
             c["max_faces_on_one_date_at"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd in ("check", "verify"):
        try:
            with io.open(OUT_PATH, encoding="utf-8") as fh:
                published = json.load(fh)
        except (OSError, ValueError) as exc:
            print("PROBLEMS: cannot read the published face: %s" % exc)
            return 1
        drift = [k for k in ("counts", "verdict", "date_index", "date_rows", "not_published")
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