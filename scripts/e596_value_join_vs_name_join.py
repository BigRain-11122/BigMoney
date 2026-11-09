"""E596 -- can a value join (match the DATE) replace the name join (match the KEY)?

E594/E595/E598 all priced joins that are done by NAME: a reader names a face and asks for a
spelling; the bar travels under whichever name the writer chose.  The pool card asks the other
question: if a consumer joined on the DATE the face states instead of on the key name, would it
land on the pricing bar, on the decision bar, on several dates at once (ambiguous), or on nothing?

That question only has an answer if some face states more than one bar, and the decisive case is a
face that carries BOTH a pricing-role and a decision-role bar.  Per such face the date-keyed join is
unambiguous exactly when both roles resolve to the same date; if the pricing date and the decision
date differ, one date cannot stand for both bars and the name join is load-bearing.

Read-only: opens no runner, writes no fixture, refreshes no panel.  The only write is the face.

  python scripts/e596_value_join_vs_name_join.py build
  python scripts/e596_value_join_vs_name_join.py check
  python scripts/e596_value_join_vs_name_join.py verify
  python scripts/e596_value_join_vs_name_join.py selftest

Output: results/state_tilt/VALUEJOINNAME.json (+ VALUEJOINNAME-latest.json)
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e594_bar_dialect_join as e594                                     # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "VALUEJOINNAME.json")
SELF_STEM = "VALUEJOINNAME"

# role -> key names, straight off the dialect face (E586 field lists via E594) so this study
# cannot grade a spelling the bar-dialect study does not grade
ROLE_KEYS = {fam: sorted(names) for fam, names in e594.SPELLINGS.items()}
# a name can sit in two families (``ticket_bar`` is both a pricing spelling and an as-of spelling);
# collapsing it to the family that happened to be written last would invent a role the dialect face
# does not assert, so such a name is published under every family it belongs to
KEY_ROLES = {}
for _fam, _keys in ROLE_KEYS.items():
    for _k in _keys:
        KEY_ROLES.setdefault(_k, []).append(_fam)
KEY_ROLES = {k: sorted(v) for k, v in KEY_ROLES.items()}
MULTI_ROLE_KEYS = sorted(k for k, v in KEY_ROLES.items() if len(v) > 1)

FACE_GLOBS = ("results/**/*.json", "docs/**/*.json")
READ_CAP = 1000000          # bytes; a face above this is published as too_big, not guessed at
LIST_CAP = 20               # list elements walked per level (rows are homogeneous in these faces)
DEPTH_CAP = 3
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

C_NO_BAR_KEY = "carries_no_bar_name"
C_BAR_NO_DATE = "names_a_bar_but_states_no_date"
C_ONE_DATE = "states_one_date"
C_SEVERAL_DATES = "states_several_dates"
C_UNREADABLE = "unreadable"

V_NAME_JOIN_NEEDED = ("the_pricing_bar_and_the_decision_bar_state_different_dates_on_some_face_so_"
                      "a_value_join_cannot_replace_the_name_join")
V_VALUE_JOIN_SUFFICES = ("every_face_that_states_both_a_pricing_and_a_decision_bar_states_them_on_"
                         "the_same_date")
V_NO_CASE = ("no_face_in_the_repo_states_both_a_pricing_and_a_decision_bar_so_the_two_joins_are"
             "_not_distinguishable_at_face_level")

REQUIRED_FACE_KEYS = ("class", "bar_fields", "dates", "roles_by_date")
REQUIRED_DETAIL_KEYS = ("path", "class", "bar_fields", "dates", "roles_by_date",
                        "carries_pricing", "carries_decision", "both_roles_same_date")


# --------------------------------------------------------------------------- pure helpers
def role_of(key):
    """Every dialect family a bar key belongs to, joined (``a+b``); '' outside the vocabulary."""
    return "+".join(KEY_ROLES.get(key, []))


def date_of(value):
    """The ISO date a value states, or '' when it states none."""
    if not isinstance(value, str):
        return ""
    m = DATE_RE.match(value.strip())
    return m.group(1) if m else ""


def walk_face(payload):
    """(bar fields, keys seen) for one payload; lists are walked to LIST_CAP at DEPTH_CAP levels."""
    fields = []
    keys = set()

    def walk(node, depth):
        if isinstance(node, dict):
            for k, v in node.items():
                role = role_of(k)
                if role:
                    keys.add(k)
                    fields.append({"key": k, "role": role, "date": date_of(v),
                                   "value_is_date": bool(date_of(v))})
                if depth < DEPTH_CAP:
                    walk(v, depth + 1)
        elif isinstance(node, list) and depth < DEPTH_CAP:
            for v in node[:LIST_CAP]:
                walk(v, depth + 1)

    walk(payload, 0)
    return fields, keys


def classify(fields):
    """The class of one face: no bar name / a bar with no date / one date / several dates."""
    if not fields:
        return C_NO_BAR_KEY
    dates = sorted({f["date"] for f in fields if f["date"]})
    if not dates:
        return C_BAR_NO_DATE
    return C_ONE_DATE if len(dates) == 1 else C_SEVERAL_DATES


def roles_of(field):
    """The family names one field speaks for (a multi-role name speaks for each of its families)."""
    return [r for r in field["role"].split("+") if r]


def roles_by_date(fields):
    out = {}
    for f in fields:
        if f["date"]:
            out.setdefault(f["date"], set()).update(roles_of(f))
    return {d: sorted(r) for d, r in sorted(out.items())}


def both_roles_same_date(roles_by_date_block):
    """True/False for a face carrying both roles, None when it carries only one of them."""
    pricing = {d for d, rs in roles_by_date_block.items() if "pricing" in rs}
    decision = {d for d, rs in roles_by_date_block.items() if "decision" in rs}
    if not pricing or not decision:
        return None
    return pricing == decision


def landing(fields):
    """Where a date-keyed join lands: the pricing bar, the decision bar, several dates, or nothing."""
    cls = classify(fields)
    if cls == C_BAR_NO_DATE:
        return "lands_on_nothing"
    if cls == C_SEVERAL_DATES:
        return "lands_on_several_dates_ambiguous"
    roles = sorted({r for f in fields if f["date"] for r in roles_of(f)})
    if roles == ["pricing"]:
        return "lands_on_the_pricing_bar"
    if roles == ["decision"]:
        return "lands_on_the_decision_bar"
    return "lands_on_" + "_and_".join(roles)


def detail_of(path, fields):
    rbd = roles_by_date(fields)
    return {
        "path": path,
        "class": classify(fields),
        "bar_fields": fields,
        "dates": sorted(rbd),
        "roles_by_date": rbd,
        "carries_pricing": any("pricing" in roles_of(f) for f in fields),
        "carries_decision": any("decision" in roles_of(f) for f in fields),
        "both_roles_same_date": both_roles_same_date(rbd),
        "landing": landing(fields),
    }


def summarise(details, unreadable):
    """Every count the face publishes, derived from the same detail list the reader sees."""
    by_class = {C_NO_BAR_KEY: 0, C_BAR_NO_DATE: 0, C_ONE_DATE: 0, C_SEVERAL_DATES: 0}
    landing_counts = {}
    for d in details:
        by_class[d["class"]] = by_class.get(d["class"], 0) + 1
        # a face with no bar name has no landing at all; printing it as a landing bucket with an
        # empty key would read like a fifth landing site (the E207 name-as-measure family)
        if d["class"] != C_NO_BAR_KEY:
            landing_counts[d["landing"]] = landing_counts.get(d["landing"], 0) + 1
    both = [d for d in details if d["carries_pricing"] and d["carries_decision"]]
    return {
        "faces_read": len(details) + unreadable,
        "faces_unreadable": unreadable,
        "faces_carrying_a_bar_name": len(details) - by_class.get(C_NO_BAR_KEY, 0),
        "by_class": by_class,
        "landing": dict(sorted(landing_counts.items())),
        "faces_carrying_both_roles": len(both),
        "both_roles_same_date": sorted(d["path"] for d in both if d["both_roles_same_date"]),
        "both_roles_different_dates": sorted(d["path"] for d in both
                                             if d["both_roles_same_date"] is False),
        "faces_with_several_dates": sorted(d["path"] for d in details
                                           if d["class"] == C_SEVERAL_DATES),
    }


def verdict_from(counts):
    total = counts.get("faces_carrying_both_roles", 0)
    diff = len(counts.get("both_roles_different_dates") or [])
    same = len(counts.get("both_roles_same_date") or [])
    if total == 0:
        return V_NO_CASE
    if diff > 0:
        return V_NAME_JOIN_NEEDED
    return V_VALUE_JOIN_SUFFICES if same == total else V_NO_CASE


def answer_sentence(counts, verdict):
    total = counts.get("faces_carrying_both_roles", 0)
    diff = len(counts.get("both_roles_different_dates") or [])
    amb = counts.get("by_class", {}).get(C_SEVERAL_DATES, 0)
    head = ("%d of %d faces that state both a pricing and a decision bar state them on different "
            "dates" % (diff, total)) if total else "no face states both bar roles"
    if verdict == V_NAME_JOIN_NEEDED:
        tail = ("so a join keyed on the date alone cannot tell which bar a consumer means on those "
                "faces: the name join is load-bearing there, and %d further faces state several "
                "dates without carrying both roles" % amb)
    elif verdict == V_VALUE_JOIN_SUFFICES:
        tail = ("so on every face where the choice is even visible a date-keyed join lands on the "
                "same bar the name join would")
    else:
        tail = "so this instrument cannot decide the question on this population"
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


def scan(root=None, limit=None):
    root = root or ROOT
    details, unreadable, too_big = [], 0, []
    for rel in faces_on_disk(root):
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
        fields, _keys = walk_face(payload)
        if not fields:
            # a face with no bar name is still counted, in the class, but its detail is not
            # published: 4984 such faces would triple the face size to say "nothing here"
            details.append({"path": rel, "class": C_NO_BAR_KEY, "bar_fields": [], "dates": [],
                            "roles_by_date": {}, "carries_pricing": False,
                            "carries_decision": False, "both_roles_same_date": None,
                            "landing": ""})
            if limit and len(details) >= limit:
                break
            continue
        details.append(detail_of(rel, fields))
        if limit and len(details) >= limit:
            break
    return {"details": details, "unreadable": unreadable, "too_big": sorted(too_big)}


def publish_view(details, sample=200):
    """The subset that carries a bar name (the face's own size stays publishable), plus a bounded
    sample of the plain single-date faces so a reader can see ordinary rows."""
    interesting = [d for d in details
                   if d["class"] in (C_BAR_NO_DATE, C_SEVERAL_DATES)
                   or d["carries_pricing"] and d["carries_decision"]]
    plain = [d for d in details if d["class"] == C_ONE_DATE
             and not (d["carries_pricing"] and d["carries_decision"])]
    return {"published": interesting + plain[:sample],
            "not_published": {"single_date_faces_sampled_out": max(0, len(plain) - sample),
                              "faces_without_a_bar_name": sum(
                                  1 for d in details if d["class"] == C_NO_BAR_KEY)}}


# --------------------------------------------------------------------------- face
def _cutoff(details):
    best = None
    for d in details:
        for date in d["dates"]:
            best = max(best or "", date)
    return best


def build(write=True, root=None):
    root = root or ROOT
    sc = scan(root)
    details = sc["details"]
    counts = summarise(details, sc["unreadable"])
    view = publish_view(details)
    face = {
        "study": "E596_value_join_vs_name_join",
        "evidence_cutoff": _cutoff(details),
        "role_vocabulary": {"source": "e594.SPELLINGS families (E586 field lists)",
                            "roles": ROLE_KEYS,
                            "names_in_more_than_one_family": MULTI_ROLE_KEYS},
        "faces": {d["path"]: {k: d[k] for k in REQUIRED_FACE_KEYS} for d in view["published"]},
        "details": view["published"],
        "not_published": view["not_published"],
        "too_big": sc["too_big"],
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, verdict_from(counts)),
        "limits": [
            "role is decided by the key name from the E594 dialect vocabulary; a bar stored under "
            "a name outside that vocabulary is invisible here",
            "a date is read from an ISO-8601 prefix on a string value; an epoch integer or a prose "
            "date states nothing to this instrument and is classed as no date",
            "lists are walked %d elements deep at %d levels, so a heterogeneous list longer than "
            "that contributes only its head" % (LIST_CAP, DEPTH_CAP),
            "faces above %d bytes are published as too_big rather than parsed" % READ_CAP,
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
    details = face.get("details") or []
    counts = face.get("counts") or {}
    if not details:
        p.append("no face detail is published")
    for d in details:
        missing = [k for k in REQUIRED_DETAIL_KEYS if k not in d]
        if missing:
            p.append("detail %s lacks %s" % (d.get("path"), ",".join(missing)))
            break
        if d["class"] not in (C_NO_BAR_KEY, C_BAR_NO_DATE, C_ONE_DATE, C_SEVERAL_DATES):
            p.append("detail %s carries an unknown class %r" % (d["path"], d["class"]))
            break
        for f in d["bar_fields"]:
            if f["key"] not in KEY_ROLES:
                p.append("detail %s carries a bar name outside the vocabulary: %r"
                         % (d["path"], f["key"]))
                break
            if f["role"] != "+".join(KEY_ROLES[f["key"]]):
                p.append("detail %s grades %r as %r" % (d["path"], f["key"], f["role"]))
                break
        if d["class"] == C_ONE_DATE and len(d["dates"]) != 1:
            p.append("detail %s is one_date but states %d dates" % (d["path"], len(d["dates"])))
            break
        if d["class"] == C_SEVERAL_DATES and len(d["dates"]) < 2:
            p.append("detail %s is several_dates but states %d dates"
                     % (d["path"], len(d["dates"])))
            break
        if d["both_roles_same_date"] is not None and not (
                d["carries_pricing"] and d["carries_decision"]):
            p.append("detail %s answers the both-roles question without carrying both roles"
                     % d["path"])
            break
    # the class counts must re-derive from what is published PLUS the sampled-out block: a sample is
    # legitimate only when the face says how many rows it did not print (r1261 family)
    npb = face.get("not_published") or {}
    sampled = npb.get("single_date_faces_sampled_out")
    if not isinstance(sampled, int):
        p.append("the not-published block does not state how many single-date faces were sampled out")
        sampled = None
    by_class = counts.get("by_class") or {}
    for cls in (C_BAR_NO_DATE, C_SEVERAL_DATES):
        seen = sum(1 for d in details if d["class"] == cls)
        if by_class.get(cls) != seen:
            p.append("class %s is %r but re-derives to %r from the published details"
                     % (cls, by_class.get(cls), seen))
            break
    if sampled is not None:
        seen_one = sum(1 for d in details if d["class"] == C_ONE_DATE)
        if by_class.get(C_ONE_DATE) != seen_one + sampled:
            p.append("class %s is %r but published %d + sampled-out %d = %d"
                     % (C_ONE_DATE, by_class.get(C_ONE_DATE), seen_one, sampled,
                        seen_one + sampled))
    bar_named = (counts.get("faces_read", 0) - counts.get("faces_unreadable", 0)
                 - by_class.get(C_NO_BAR_KEY, 0))
    if counts.get("faces_carrying_a_bar_name") != bar_named:
        p.append("faces_carrying_a_bar_name is %r but read-minus-unreadable-minus-no-bar-name = %d"
                 % (counts.get("faces_carrying_a_bar_name"), bar_named))
    if sampled is not None and npb.get("faces_without_a_bar_name") != by_class.get(C_NO_BAR_KEY):
        p.append("the not-published block says %r faces carry no bar name, the counts say %r"
                 % (npb.get("faces_without_a_bar_name"), by_class.get(C_NO_BAR_KEY)))
    both = sorted(d["path"] for d in details if d["carries_pricing"] and d["carries_decision"])
    if sorted(counts.get("both_roles_same_date") or []) + sorted(
            counts.get("both_roles_different_dates") or []) != both:
        p.append("the both-role lists do not partition the published both-role faces")
    if counts.get("faces_carrying_both_roles") != len(both):
        p.append("faces_carrying_both_roles is %r but %d details carry both roles"
                 % (counts.get("faces_carrying_both_roles"), len(both)))
    if npb.get("faces_without_a_bar_name") is None:
        p.append("the not-published block does not say how many faces carry no bar name")
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

    # 1-6 role vocabulary and date reading
    chk("1 role_of pricing key", role_of("pricing_bar") == "pricing")
    chk("2 role_of decision key", role_of("book_decided_at") == "decision")
    chk("3 role_of unknown name is empty", role_of("bar_of_the_day") == "")
    chk("3b a name in two families is published under both, not collapsed",
        role_of("ticket_bar") == "as_of+pricing" and MULTI_ROLE_KEYS == ["ticket_bar"],
        role_of("ticket_bar"))
    chk("4 date_of iso date", date_of("2026-11-06") == "2026-11-06")
    chk("5 date_of iso timestamp takes the day", date_of("2026-11-06T15:30:00+08:00") == "2026-11-06")
    chk("6 date_of prose/integer states nothing",
        date_of("panel 2026-10-14 (bars due)") == "" and date_of(1762344000) == "")

    # 7-11 classification on synthetic faces
    f_one = [{"key": "pricing_bar", "role": "pricing", "date": "2026-11-06", "value_is_date": True}]
    chk("7 one pricing date classifies one_date", classify(f_one) == C_ONE_DATE)
    chk("8 one pricing date lands on the pricing bar",
        landing(f_one) == "lands_on_the_pricing_bar")
    f_dec = [{"key": "book_decided_at", "role": "decision", "date": "2026-11-05",
              "value_is_date": True}]
    chk("9 one decision date lands on the decision bar",
        landing(f_dec) == "lands_on_the_decision_bar")
    f_none = [{"key": "pricing_bar", "role": "pricing", "date": "", "value_is_date": False}]
    chk("10 a bar with no date lands on nothing",
        classify(f_none) == C_BAR_NO_DATE and landing(f_none) == "lands_on_nothing")
    f_amb = [{"key": "pricing_bar", "role": "pricing", "date": "2026-11-06", "value_is_date": True},
             {"key": "evidence_cutoff", "role": "evidence_cutoff", "date": "2026-10-30",
              "value_is_date": True}]
    chk("11 two dates is ambiguous", classify(f_amb) == C_SEVERAL_DATES
        and landing(f_amb) == "lands_on_several_dates_ambiguous")

    # 12-14 the decisive case: both roles on one face
    f_same = [{"key": "pricing_bar", "role": "pricing", "date": "2026-11-06", "value_is_date": True},
              {"key": "book_decided_at", "role": "decision", "date": "2026-11-06",
               "value_is_date": True}]
    f_diff = [{"key": "pricing_bar", "role": "pricing", "date": "2026-11-06", "value_is_date": True},
              {"key": "book_decided_at", "role": "decision", "date": "2026-11-05",
               "value_is_date": True}]
    chk("12 both roles on one date is an unambiguous value join",
        both_roles_same_date(roles_by_date(f_same)) is True)
    chk("13 both roles on different dates needs the name join",
        both_roles_same_date(roles_by_date(f_diff)) is False)
    chk("14 a single-role face answers the both-roles question with None",
        both_roles_same_date(roles_by_date(f_one)) is None)

    # 15-18 summariser + verdict, including the direction of the verdict
    ds = [detail_of("a.json", f_same), detail_of("b.json", f_diff), detail_of("c.json", f_one),
          detail_of("d.json", f_amb), detail_of("e.json", f_none)]
    c = summarise(ds, 2)
    chk("15 counts re-derive by class",
        c["by_class"] == {C_NO_BAR_KEY: 0, C_BAR_NO_DATE: 1, C_ONE_DATE: 2, C_SEVERAL_DATES: 2},
        c["by_class"])
    chk("16 unreadable faces are counted but not classified",
        c["faces_read"] == 7 and c["faces_unreadable"] == 2)
    chk("17 one differing both-role face forces the name join",
        verdict_from(c) == V_NAME_JOIN_NEEDED)
    same_only = summarise([detail_of("a.json", f_same)], 0)
    chk("18 when both roles always share a date the value join suffices",
        verdict_from(same_only) == V_VALUE_JOIN_SUFFICES)
    chk("19 no both-role face means no case to decide",
        verdict_from(summarise([detail_of("c.json", f_one)], 0)) == V_NO_CASE)

    # 20-23 guard: the face must refuse drift in each direction it can drift
    good = {"study": "x", "evidence_cutoff": "2026-11-06",
            "role_vocabulary": {"roles": ROLE_KEYS},
            "details": ds,
            "not_published": {"single_date_faces_sampled_out": 0,
                              "faces_without_a_bar_name": 0},
            "counts": summarise(ds, 2), "verdict": verdict_from(summarise(ds, 2)),
            "answer": answer_sentence(summarise(ds, 2), verdict_from(summarise(ds, 2)))}
    chk("20 a clean synthetic face passes the guard", face_problems(good) == [], face_problems(good))
    sampled_only = json.loads(json.dumps(good))
    sampled_only["details"] = [d for d in sampled_only["details"] if d["class"] != C_ONE_DATE]
    sampled_only["not_published"]["single_date_faces_sampled_out"] = 2
    _seen = [d for d in sampled_only["details"] if d["class"] != C_ONE_DATE]
    sampled_only["counts"] = summarise(sampled_only["details"] + [
        {"path": "_sampled_out_%d.json" % i, "class": C_ONE_DATE, "bar_fields": [], "dates": [],
         "roles_by_date": {}, "carries_pricing": False, "carries_decision": False,
         "both_roles_same_date": None, "landing": ""} for i in range(2)], 2)
    sampled_only["verdict"] = verdict_from(sampled_only["counts"])
    sampled_only["both_roles_same_date"] = sorted(
        d["path"] for d in sampled_only["details"]
        if d["carries_pricing"] and d["carries_decision"] and d["both_roles_same_date"])
    sampled_only["both_roles_different_dates"] = sorted(
        d["path"] for d in sampled_only["details"]
        if d["carries_pricing"] and d["carries_decision"] and d["both_roles_same_date"] is False)
    chk("20b a face that samples single-date rows and says so still passes",
        face_problems(sampled_only) == [], face_problems(sampled_only))
    bad_cls = json.loads(json.dumps(good))
    bad_cls["counts"]["by_class"][C_SEVERAL_DATES] += 1
    chk("21 a class count that does not re-derive is caught",
        any("re-derives" in s for s in face_problems(bad_cls)))
    bad_v = json.loads(json.dumps(good))
    bad_v["verdict"] = V_VALUE_JOIN_SUFFICES
    chk("22 a verdict that contradicts the counts is caught",
        any("verdict" in s for s in face_problems(bad_v)))
    bad_sample = json.loads(json.dumps(good))
    bad_sample["not_published"]["single_date_faces_sampled_out"] += 1
    chk("23b a sampled-out count that does not reconcile is caught",
        any("sampled-out" in s for s in face_problems(bad_sample)))
    bad_role = json.loads(json.dumps(good))
    bad_role["details"][0]["bar_fields"][0]["role"] = "decision"
    chk("23 a role that disagrees with the vocabulary is caught",
        any("grades" in s for s in face_problems(bad_role)))

    # 24 the scan honours the self-exclusion and reports unreadable faces instead of guessing
    tmp = os.path.join(ROOT, "results", "_e596_selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    try:
        with io.open(os.path.join(tmp, "VALUEJOINNAME-x.json"), "w", encoding="utf-8") as fh:
            fh.write('{"pricing_bar": "2026-11-06"}')
        sc = scan(ROOT)
        seen_self = any(d["path"].endswith("VALUEJOINNAME-x.json") for d in sc["details"])
        chk("24 this study does not scan its own published face", not seen_self)
        chk("25 the scan reads more than one bar-carrying face", len(sc["details"]) > 100,
            len(sc["details"]))
    finally:
        for f in glob.glob(os.path.join(tmp, "*")):
            os.remove(f)
        os.rmdir(tmp)

    print("\n%d/%d PASS" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "build").lower()
    if cmd == "selftest":
        return selftest()
    face, problems = build(write=(cmd == "build"))
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("faces_read=%d unreadable=%d bar_named=%d bool" % (c["faces_read"],
                                                             c["faces_unreadable"],
                                                             c["faces_carrying_a_bar_name"]))
    print("by_class=" + json.dumps(c["by_class"], sort_keys=True))
    print("both_roles=%d same_date=%d different_dates=%d"
          % (c["faces_carrying_both_roles"], len(c["both_roles_same_date"]),
             len(c["both_roles_different_dates"])))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd == "build":
        print("wrote " + os.path.relpath(OUT_PATH, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))