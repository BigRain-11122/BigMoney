"""E453 -- a guard tests existence and says nothing about age.

E452 (results/state_tilt/abandonedguard_latest.json) took the read sites that sit under a base no
write site produces in the corpus, and published per site whether the open is guarded and whether
the artifact is on disk.  Eight of twelve were guarded, eleven of twelve present, and the face
stopped there: a guard announces a *missing* artifact and is silent about an artifact nobody has
produced for months.

This face takes exactly the E452 sites whose artifact is present and publishes, per site:

  * the target mtime and its age in days at the face cutoff,
  * the age of the newest member of the site's base (what the base still looks like alive),
  * whether the enclosing reading function performs any age/mtime check of its own
    (a clock read, an st_mtime comparison, or a max-age/staleness constant),
  * the class fresh_artifact / stale_artifact_with_an_age_check /
    stale_artifact_with_no_age_check,
  * the consumer split (smoke suite vs lane host).

The staleness threshold is a named constant (STALE_DAYS), not an implicit 30 or 90 chosen after
looking at the data.  Nothing is executed: this is os.stat on the E452 targets plus a static AST
reading of the enclosing functions.

    python scripts/e453_abandoned_stale.py run        # build and publish the face
    python scripts/e453_abandoned_stale.py check      # re-derive every tally from the published rows
    python scripts/e453_abandoned_stale.py verify     # re-derive from the live tree and the disk
    python scripts/e453_abandoned_stale.py selftest   # offline legs
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
import time
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import e452_abandoned_guard as e452  # noqa: E402  (the site population is the upstream measurement)

ROOT = e452.ROOT
OUTDIR = e452.OUTDIR
DATED_PREFIX = "ABANDONEDSTALE"
FACE_NAME = DATED_PREFIX.lower() + "_latest.json"
SOURCE_FACE = e452.FACE_NAME

# The threshold is named before the measurement, not fitted to it.  Half a year: long enough that
# a live pipeline cannot miss it, short enough that a face nobody re-derives shows up.
STALE_DAYS = 180

C_FRESH = "fresh_artifact"
C_STALE_CHECKED = "stale_artifact_with_an_age_check"
C_STALE_NO_CHECK = "stale_artifact_with_no_age_check"
CLASSES = (C_FRESH, C_STALE_CHECKED, C_STALE_NO_CHECK)

K_CLOCK = "reads_the_clock"
K_MTIME = "compares_an_mtime"
K_CONST = "names_a_max_age_constant"
AGE_FORMS = (K_CLOCK, K_MTIME, K_CONST)

CONSUMER_SMOKE = "smoke_suite"
CONSUMER_LANE = "lane_host"

UNIDENTIFIABLE_VERDICT = (
    "mtime_age_cannot_exceed_the_checkout_floor_so_staleness_is_not_identifiable_here"
    "_and_every_fresh_reading_is_an_artifact_of_materialisation")

CLOCK_CALLS = {
    "time.time", "time.time_ns", "time.monotonic",
    "datetime.now", "datetime.utcnow", "datetime.today",
    "date.today", "arrow.now", "pendulum.now",
}
AGE_WORDS = re.compile(
    r"(max_?age|stale|stale_?days|fresh_?days|freshness|ttl|max_?days|age_?days)",
    re.IGNORECASE,
)


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel: str) -> bool:
    name = os.path.basename(rel)
    if name == FACE_NAME:
        return True
    return name.startswith(DATED_PREFIX + "-") and name.endswith(".json")


# ----------------------------------------------------------------------------- ages


def age_days(path: str, cutoff: date) -> int | None:
    """Whole days between the file's mtime date and the cutoff date (never negative-clamped)."""
    try:
        mtime = os.stat(path).st_mtime
    except OSError:
        return None
    return (cutoff - datetime.fromtimestamp(mtime).date()).days


def base_newest_age(base_rel: str, cutoff: date, root: str | None = None) -> dict:
    """The newest file still sitting under the site's (abandoned) base."""
    root = root or ROOT
    base = os.path.join(root, base_rel.replace("/", os.sep))
    newest = None
    newest_age = None
    members = 0
    if not os.path.isdir(base):
        return {"newest_member": None, "newest_age_days": None, "member_count": 0}
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in {"__pycache__", ".git"}]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            a = age_days(full, cutoff)
            if a is None:
                continue
            members += 1
            if newest_age is None or a < newest_age:
                newest, newest_age = _rel(full), a
    return {"newest_member": newest, "newest_age_days": newest_age, "member_count": members}


# ----------------------------------------------------------------------------- age checks


def enclosing_function(tree: ast.AST, line: int) -> ast.AST | None:
    """The innermost function that contains this line (module itself when there is none)."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            start = getattr(node, "lineno", 10 ** 9)
            end = getattr(node, "end_lineno", 0) or 0
            if start <= line <= end:
                if best is None or start >= getattr(best, "lineno", 0):
                    best = node
    return best


def _dotted(node: ast.AST) -> str | None:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def age_check_forms(scope: ast.AST | None) -> list[str]:
    """Which of the three age-check forms this reading scope carries."""
    if scope is None:
        return []
    found: set[str] = set()
    for node in ast.walk(scope):
        if isinstance(node, ast.Call):
            name = _dotted(node.func)
            base = name.rsplit(".", 1)[-1] if name else None
            if name in CLOCK_CALLS or base in {"now", "utcnow", "today", "monotonic", "time"}:
                found.add(K_CLOCK)
        elif isinstance(node, ast.Attribute):
            if node.attr in {"st_mtime", "st_ctime", "st_atime"}:
                found.add(K_MTIME)
        elif isinstance(node, ast.Name):
            if AGE_WORDS.search(node.id):
                found.add(K_CONST)
        elif isinstance(node, ast.keyword):
            if AGE_WORDS.search(node.arg or ""):
                found.add(K_CONST)
        elif isinstance(node, ast.arg):
            if AGE_WORDS.search(node.arg or ""):
                found.add(K_CONST)
    return [f for f in AGE_FORMS if f in found]


def classify(age_days_value: int | None, forms: list[str]) -> str:
    if age_days_value is None:
        return C_FRESH  # never claimed: an unmeasurable target is reported as such by its row
    if age_days_value <= STALE_DAYS:
        return C_FRESH
    return C_STALE_CHECKED if forms else C_STALE_NO_CHECK


def consumer_of(face_rel: str) -> str:
    return CONSUMER_SMOKE if os.path.basename(face_rel) == "smoke_test.py" else CONSUMER_LANE


# ----------------------------------------------------------------------------- identifiability

# A checkout sets every mtime to the materialisation moment, so an mtime-derived age cannot exceed
# the age of the clone it is read on.  If the floor is younger than the staleness threshold, "fresh"
# is not evidence of freshness and the whole measurement is not identifiable here.
SKIP_WALK = {".git", "Money02", "legacy", "node_modules", "_quarantine", "__pycache__", ".codely-cli"}
FLOOR_WALK_CAP = 60000


def mtime_floor(cutoff: date, root: str | None = None) -> dict:
    root = root or ROOT
    oldest = None
    oldest_rel = None
    by_date: dict[str, int] = {}
    walked = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_WALK)
        for fn in filenames:
            if walked >= FLOOR_WALK_CAP:
                break
            full = os.path.join(dirpath, fn)
            try:
                m = os.stat(full).st_mtime
            except OSError:
                continue
            walked += 1
            d = datetime.fromtimestamp(m).date().isoformat()
            by_date[d] = by_date.get(d, 0) + 1
            if oldest is None or m < oldest:
                oldest, oldest_rel = m, _rel(full)
        if walked >= FLOOR_WALK_CAP:
            break
    if oldest is None:
        return {"walked": 0, "oldest_mtime_date": None, "max_identifiable_age_days": None,
                "modal_date": None, "modal_date_count": 0}
    floor_date = datetime.fromtimestamp(oldest).date()
    modal_date, modal_count = max(by_date.items(), key=lambda kv: kv[1])
    return {
        "walked": walked,
        "walk_cap": FLOOR_WALK_CAP,
        "oldest_file": oldest_rel,
        "oldest_mtime_date": floor_date.isoformat(),
        "max_identifiable_age_days": (cutoff - floor_date).days,
        "modal_date": modal_date,
        "modal_date_count": modal_count,
        "distinct_mtime_dates": len(by_date),
    }


def identifiability(cutoff: date, root: str | None = None) -> dict:
    floor = mtime_floor(cutoff, root)
    max_age = floor["max_identifiable_age_days"]
    ok = max_age is not None and max_age >= STALE_DAYS
    return {
        "threshold_days": STALE_DAYS,
        "mtime_floor": floor,
        "mtime_age_is_identifiable_above_the_threshold": ok,
        "reason": ("an mtime-derived age cannot exceed the age of the materialisation that set it"
                   if not ok else "the checkout floor is older than the threshold"),
    }


def verdict_for(sites: list[dict], ident: dict | None = None) -> str:
    if not sites:
        return "empty_population"
    if ident is not None and not ident["mtime_age_is_identifiable_above_the_threshold"]:
        return UNIDENTIFIABLE_VERDICT
    stale = [s for s in sites if s["class"] != C_FRESH]
    if not stale:
        return "every_present_target_under_an_abandoned_base_is_younger_than_the_staleness_threshold"
    unchecked = [s for s in stale if s["class"] == C_STALE_NO_CHECK]
    if not unchecked:
        return "stale_targets_exists_but_every_one_of_them_is_read_by_code_that_checks_its_age"
    if len(unchecked) == len(stale):
        return "every_stale_target_is_read_by_code_that_never_looks_at_its_age"
    return "stale_targets_split_between_readers_that_check_an_age_and_readers_that_do_not"


# ----------------------------------------------------------------------------- build


def build(cutoff: str | None = None, root: str | None = None,
          source_face: dict | None = None) -> dict:
    root = root or ROOT
    cutoff = cutoff or date.today().isoformat()
    cutoff_date = date.fromisoformat(cutoff)
    face = source_face if source_face is not None else _load(
        os.path.join(root, OUTDIR, SOURCE_FACE))

    cache: dict = {}
    rows_out: list[dict] = []
    for row in face["rows"]:
        base = row["base"]
        base_info = base_newest_age(base, cutoff_date, root=root)
        sites_out: list[dict] = []
        for site in row["sites"]:
            if site.get("artifact_present") is not True:
                continue
            resolved = site.get("resolved_path")
            target = os.path.join(root, resolved.replace("/", os.sep)) if resolved else None
            a = age_days(target, cutoff_date) if target else None
            scope = None
            src_tree = e452._module_source(site["face"], cache)[1]
            if src_tree is not None:
                scope = enclosing_function(src_tree, site["line"])
            forms = age_check_forms(scope)
            sites_out.append({
                "base": base,
                "face": site["face"],
                "line": site["line"],
                "kind": site.get("kind"),
                "resolved_path": resolved,
                "target_age_days_at_cutoff": a,
                "base_newest_member": base_info["newest_member"],
                "base_newest_age_days": base_info["newest_age_days"],
                "reading_scope": (getattr(scope, "name", None) or "<module>") if scope is not None else None,
                "age_check_forms": forms,
                "has_an_age_check": bool(forms),
                "consumer": consumer_of(site["face"]),
                "class": classify(a, forms),
            })
        if not sites_out:
            continue
        rows_out.append({
            "base": base,
            "member_count_at_base": base_info["member_count"],
            "base_newest_member": base_info["newest_member"],
            "base_newest_age_days": base_info["newest_age_days"],
            "site_count": len(sites_out),
            "class_counts": {c: sum(1 for s in sites_out if s["class"] == c) for c in CLASSES},
            "sites": sites_out,
        })

    sites = [s for r in rows_out for s in r["sites"]]
    measured = [s for s in sites if s["target_age_days_at_cutoff"] is not None]
    ident = identifiability(cutoff_date, root)
    for s in sites:
        s["age_is_identifiable_above_the_threshold"] = \
            ident["mtime_age_is_identifiable_above_the_threshold"]
    summary = {
        "sites_graded": len(sites),
        "sites_with_a_measured_target": len(measured),
        "bases_graded": len(rows_out),
        "class_counts": {c: sum(1 for s in sites if s["class"] == c) for c in CLASSES},
        "consumer_counts": {
            c: sum(1 for s in sites if s["consumer"] == c)
            for c in (CONSUMER_SMOKE, CONSUMER_LANE)
        },
        "stale_by_consumer": {
            c: sum(1 for s in sites if s["consumer"] == c and s["class"] != C_FRESH)
            for c in (CONSUMER_SMOKE, CONSUMER_LANE)
        },
        "age_check_form_counts": {f: sum(1 for s in sites if f in s["age_check_forms"])
                                  for f in AGE_FORMS},
        "sites_with_an_age_check": sum(1 for s in sites if s["has_an_age_check"]),
        "max_target_age_days": max((s["target_age_days_at_cutoff"] for s in measured), default=None),
        "min_target_age_days": min((s["target_age_days_at_cutoff"] for s in measured), default=None),
        "staleness_threshold_days": STALE_DAYS,
        "stale_sites": ["%s:%d" % (s["face"], s["line"])
                        for s in sites if s["class"] != C_FRESH],
        "unmeasured_sites": ["%s:%d" % (s["face"], s["line"])
                             for s in sites if s["target_age_days_at_cutoff"] is None],
    }
    return {
        "study": "E453_abandoned_stale",
        "title": "a guard tests existence and says nothing about age",
        "evidence_cutoff": cutoff,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_face": SOURCE_FACE,
        "staleness_threshold_days": STALE_DAYS,
        "core_question": ("of the E452 present targets under a base no write site produces, how "
                          "many are older than %d days at the cutoff and how many of their "
                          "readers check an age at all" % STALE_DAYS),
        "identification": ident,
        "rows": rows_out,
        "summary": summary,
        "verdict": verdict_for(sites, ident),
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return dated


# ----------------------------------------------------------------------------- check / verify


def _sites_of(face: dict) -> list[dict]:
    return [s for r in face["rows"] for s in r["sites"]]


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    sites = _sites_of(face)
    s = face["summary"]
    if len(sites) != s["sites_graded"]:
        problems.append("site rows %d != summary %d" % (len(sites), s["sites_graded"]))
    recounted = {c: sum(1 for x in sites if x["class"] == c) for c in CLASSES}
    if recounted != s["class_counts"]:
        problems.append("class_counts %s != recomputed %s" % (s["class_counts"], recounted))
    for x in sites:
        want = classify(x["target_age_days_at_cutoff"], x["age_check_forms"])
        if x["class"] != want:
            problems.append("%s:%s class %r does not re-derive (%r)"
                            % (x["face"], x["line"], x["class"], want))
        if bool(x["age_check_forms"]) != bool(x["has_an_age_check"]):
            problems.append("%s:%s has_an_age_check disagrees with its forms" % (x["face"], x["line"]))
        if x["consumer"] != consumer_of(x["face"]):
            problems.append("%s:%s consumer %r does not re-derive" % (x["face"], x["line"], x["consumer"]))
        if x["class"] == C_FRESH and x["target_age_days_at_cutoff"] is not None \
                and x["target_age_days_at_cutoff"] > face["staleness_threshold_days"]:
            problems.append("%s:%s graded fresh above the threshold" % (x["face"], x["line"]))
        if x["class"] != C_FRESH and not x["age_check_forms"] and x["class"] != C_STALE_NO_CHECK:
            problems.append("%s:%s unchecked stale target graded %r" % (x["face"], x["line"], x["class"]))
    for c, n in s["consumer_counts"].items():
        if sum(1 for x in sites if x["consumer"] == c) != n:
            problems.append("consumer_counts[%s] does not re-add" % c)
    for c, n in s["stale_by_consumer"].items():
        got = sum(1 for x in sites if x["consumer"] == c and x["class"] != C_FRESH)
        if got != n:
            problems.append("stale_by_consumer[%s] %d != %d" % (c, n, got))
    for f, n in s["age_check_form_counts"].items():
        if sum(1 for x in sites if f in x["age_check_forms"]) != n:
            problems.append("age_check_form_counts[%s] does not re-add" % f)
    measured = [x for x in sites if x["target_age_days_at_cutoff"] is not None]
    if len(measured) != s["sites_with_a_measured_target"]:
        problems.append("sites_with_a_measured_target does not re-add")
    if (max((x["target_age_days_at_cutoff"] for x in measured), default=None)
            != s["max_target_age_days"]):
        problems.append("max_target_age_days does not re-derive")
    if (min((x["target_age_days_at_cutoff"] for x in measured), default=None)
            != s["min_target_age_days"]):
        problems.append("min_target_age_days does not re-derive")
    want_stale = ["%s:%d" % (x["face"], x["line"]) for x in sites if x["class"] != C_FRESH]
    if want_stale != s["stale_sites"]:
        problems.append("stale_sites does not re-add")
    if face["staleness_threshold_days"] != STALE_DAYS:
        problems.append("the face publishes a threshold the code no longer uses")
    ident = face.get("identification") or {}
    floor = ident.get("mtime_floor") or {}
    max_age = floor.get("max_identifiable_age_days")
    if max_age is None:
        problems.append("the face publishes no checkout floor, so its ages cannot be bounded")
    else:
        over = [x for x in sites
                if x["target_age_days_at_cutoff"] is not None
                and x["target_age_days_at_cutoff"] > max_age]
        if over:
            problems.append("%d target(s) measure older than the checkout floor"
                            % len(over))
        want_ident = max_age >= face["staleness_threshold_days"]
        if bool(ident.get("mtime_age_is_identifiable_above_the_threshold")) != want_ident:
            problems.append("the identifiability flag disagrees with the floor")
        said_unidentifiable = face["verdict"] == UNIDENTIFIABLE_VERDICT
        if said_unidentifiable == want_ident:
            problems.append("verdict and identifiability disagree")
    flagged = {x["age_is_identifiable_above_the_threshold"] for x in sites}
    if len(flagged) > 1:
        problems.append("sites disagree on whether their age is identifiable")
    for row in face["rows"]:
        rc = {c: sum(1 for x in row["sites"] if x["class"] == c) for c in CLASSES}
        if rc != row["class_counts"]:
            problems.append("row %s class_counts does not re-add" % row["base"])
        if row["site_count"] != len(row["sites"]):
            problems.append("row %s site_count %d != %d" % (row["base"], row["site_count"], len(row["sites"])))
    if face["verdict"] != verdict_for(sites, face.get("identification")):
        problems.append("verdict %r does not re-derive (%r)"
                        % (face["verdict"], verdict_for(sites, face.get("identification"))))
    return problems


def verify(face: dict | None = None, root: str | None = None) -> list[str]:
    face = face if face is not None else _load(os.path.join(OUTDIR, FACE_NAME))
    fresh = build(cutoff=face["evidence_cutoff"], root=root)
    problems = tally_problems(fresh)
    old = {(s["face"], s["line"]): s for s in _sites_of(face)}
    new = {(s["face"], s["line"]): s for s in _sites_of(fresh)}
    if set(old) != set(new):
        problems.append("site population moved: -%s +%s"
                        % (sorted(set(old) - set(new))[:5], sorted(set(new) - set(old))[:5]))
    for key in sorted(set(old) & set(new)):
        a, b = old[key], new[key]
        for field in ("class", "resolved_path", "target_age_days_at_cutoff",
                      "age_check_forms", "consumer"):
            if a[field] != b[field]:
                problems.append("%s:%s %s %r -> %r" % (key[0], key[1], field, a[field], b[field]))
    if face["verdict"] != fresh["verdict"]:
        problems.append("verdict moved %r -> %r" % (face["verdict"], fresh["verdict"]))
    return problems


# ----------------------------------------------------------------------------- selftest


def selftest() -> int:
    bad: list[str] = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            bad.append(name)

    base = date(2026, 11, 6)

    # 1 a fresh file is graded fresh, a file past the threshold is not
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        fresh_p = os.path.join(tmp, "fresh.json")
        old_p = os.path.join(tmp, "old.json")
        for p in (fresh_p, old_p):
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("{}")
        now = time.time()
        os.utime(fresh_p, (now, now))
        os.utime(old_p, (now - (STALE_DAYS + 10) * 86400, now - (STALE_DAYS + 10) * 86400))
        check("a file touched today is 0 days old", age_days(fresh_p, base) == 0)
        check("a file older than the threshold measures past it",
              (age_days(old_p, base) or 0) > STALE_DAYS)
        check("a missing file has no age", age_days(os.path.join(tmp, "nope"), base) is None)

        # 2 the base walk reports the newest member, not the base directory's own mtime
        sub = os.path.join(tmp, "b")
        os.makedirs(sub)
        with open(os.path.join(sub, "a.json"), "w", encoding="utf-8") as fh:
            fh.write("{}")
        os.utime(os.path.join(sub, "a.json"), (now - 400 * 86400, now - 400 * 86400))
        info = base_newest_age(sub, base, root=tmp)
        check("the base walk counts its members", info["member_count"] == 1)
        check("the base walk takes the member age, not the directory's",
              info["newest_age_days"] is not None and info["newest_age_days"] > 300)

    # 3 classification: fresh / stale checked / stale unchecked
    check("young target is fresh", classify(10, []) == C_FRESH)
    check("stale target with a clock read is checked", classify(STALE_DAYS + 1, [K_CLOCK]) == C_STALE_CHECKED)
    check("stale target with no form is unchecked", classify(STALE_DAYS + 1, []) == C_STALE_NO_CHECK)
    check("the threshold itself is fresh (boundary is inclusive)", classify(STALE_DAYS, []) == C_FRESH)

    # 4 age-check forms are found in the enclosing function and nowhere else
    src = (
        "import time\n"
        "def reader(p):\n"
        "    with open(p) as fh:\n"
        "        return fh.read()\n"
        "def timed_reader(p):\n"
        "    if time.time() - 3600 > 0:\n"
        "        pass\n"
        "    with open(p) as fh:\n"
        "        return fh.read()\n"
        "def mtime_reader(p):\n"
        "    import os\n"
        "    return os.stat(p).st_mtime\n"
        "def const_reader(p, MAX_AGE_DAYS=30):\n"
        "    with open(p) as fh:\n"
        "        return fh.read()\n"
    )
    tree = ast.parse(src)
    plain = enclosing_function(tree, 3)
    timed = enclosing_function(tree, 7)
    mtimed = enclosing_function(tree, 12)
    consted = enclosing_function(tree, 14)
    check("the plain reader is located", getattr(plain, "name", None) == "reader")
    check("a plain reader carries no age form", age_check_forms(plain) == [])
    check("a clock read is found", K_CLOCK in age_check_forms(timed))
    check("an st_mtime comparison is found", K_MTIME in age_check_forms(mtimed))
    check("a max-age constant is found", K_CONST in age_check_forms(consted))
    check("the module scope is not mistaken for a reader",
          age_check_forms(enclosing_function(tree, 1)) == [])

    # 5 the consumer split
    check("the smoke suite is its own consumer", consumer_of("smoke_test.py") == CONSUMER_SMOKE)
    check("a lane script is a lane host", consumer_of("scripts/alphagen_beam_w18.py") == CONSUMER_LANE)

    # 6 verdicts re-derive from the classes alone
    fresh_site = {"class": C_FRESH}
    stale_checked = {"class": C_STALE_CHECKED}
    stale_bare = {"class": C_STALE_NO_CHECK}
    check("empty population", verdict_for([]) == "empty_population")
    check("all fresh",
          verdict_for([fresh_site, fresh_site])
          == "every_present_target_under_an_abandoned_base_is_younger_than_the_staleness_threshold")
    check("all stale checked",
          verdict_for([stale_checked, stale_checked])
          == "stale_targets_exists_but_every_one_of_them_is_read_by_code_that_checks_its_age")
    check("all stale unchecked",
          verdict_for([stale_bare]) == "every_stale_target_is_read_by_code_that_never_looks_at_its_age")
    check("mixed",
          verdict_for([stale_checked, stale_bare])
          == "stale_targets_split_between_readers_that_check_an_age_and_readers_that_do_not")

    # 7 the study's own faces are never population
    check("own latest face is excluded", is_own_output("results/state_tilt/" + FACE_NAME))
    check("own dated face is excluded",
          is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    check("the upstream face is not excluded", not is_own_output("results/state_tilt/" + SOURCE_FACE))

    total = 25
    if bad:
        print("selftest FAIL %d/%d" % (len(bad), total))
        for b in bad:
            print("  -", b)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


# ----------------------------------------------------------------------------- cli


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        print("wrote %s" % _rel(path))
        print("bases %d | sites %d | measured %d | threshold %d days"
              % (s["bases_graded"], s["sites_graded"], s["sites_with_a_measured_target"], STALE_DAYS))
        print("class %s" % json.dumps(s["class_counts"]))
        print("stale by consumer %s | age forms %s"
              % (json.dumps(s["stale_by_consumer"]), json.dumps(s["age_check_form_counts"])))
        print("target age days min=%s max=%s"
              % (s["min_target_age_days"], s["max_target_age_days"]))
        print("verdict: %s" % face["verdict"])
        return 0
    if cmd == "check":
        face = _load(os.path.join(OUTDIR, FACE_NAME))
        problems = tally_problems(face)
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))