"""E341 -- what does the census sibling closer actually change?

E338 measured 15/15 census windows closing on the *next* census sibling, and found that its two
readings ("all .py touches" vs "touches outside the census family") picked the same commit 15/15
times.  The split measured nothing, and E338 said why: a census study ships its S6 wiring in the
same commit that lands it.  So the chain's drift is not an external nuisance -- it is the chain's
own landing commit.  This study prices that commit instead of only naming it.

For each of the 15 closed windows:

    landing         the commit that first added a census face
    closing         the next commit touching any .py under the five packages
    added/modified  the .py files that commit brings (name-status, .py only)
    class           s6_wiring | census_study | name_writer | unrelated, first match wins
    name currency   a *stem* is the uppercase token a face name is built from: the part before
                    ``-YYYY-MM-DD.json``, before ``-%s.json`` in a FACE template, or before
                    ``.json`` in an uppercase mirror (``-latest``).  A source is a *writer* of a
                    stem when the stem appears in it as a standalone token.  This is the composed
                    step of E322's needle, so it is the widest honest reading of "this file names
                    that face".
    size currency   sources / bytes / lines the corpus gains -- what any counting face reads

Two ways a census face's published number can move on that commit, kept apart:

    composition     the corpus gained a member (a file that did not exist before) -- +1 source,
                    +bytes, +lines, and +1 writer for every stem that new member names
    content         a member it already read changed in place -- +Δbytes, +Δlines, and a writer
                    set that can move in either direction for the stems inside that edit

The card's last question is whether excluding the census family from the corpus is a legitimate
population definition or just a way to keep a red leg green.  That is answered with the same
currency at a pinned commit: how many sources / lines / bytes / writer rows the 16 family files
contribute, and which stems would be left with no writer at all.

Self-exclusion (E207/E332 family): the corpus read at the pin is taken from git, and this study's
own file does not exist in the pinned tree, so the scanner cannot count itself.

Usage:
    python scripts/e341_sibling_closer_what_changed.py run|verify|selftest
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e338_census_green_window as e338
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "SIBLINGCLOSER-%s.json" % TODAY
LATEST = "siblingcloser_latest.json"
STUDY = "E341_sibling_closer_what_changed"
SELF_REL = "scripts/e341_sibling_closer_what_changed.py"

# The corpus is read at a commit, not off the disk: a face that re-derives off the moving tip goes
# red the moment any .py lands (E338 family).  The pin is the tree the measurements were taken on;
# this study's own file lands after it, which is disclosed rather than fixed.
PIN_SHA = "444d3be87be36a3b38cebd0ebddc2be975109f30"

STEM_PATTERNS = (
    re.compile(r"([A-Z][A-Z0-9_]{2,40})-\d{4}-\d{2}-\d{2}\.json"),
    re.compile(r"([A-Z][A-Z0-9_]{2,40})-%s\.json"),
)

S6_PREFIX = "Tools/s6_chain"
CLASSES = ("s6_wiring", "census_study", "name_writer", "unrelated")

V_NONE = "no_census_window_closed_so_there_is_nothing_to_price"
V_TWO_IN_ONE = ("the_closing_commit_is_in_two_halves_the_added_member_moves_the_name_census_and_the_wiring_"
                "edit_moves_only_counts_so_the_two_readings_could_not_separate_them_and_excluding_the_"
                "family_leaves_most_of_these_names_with_no_writer_at_all")
V_MIXED = ("the_closing_commits_sometimes_grow_the_corpus_and_sometimes_only_edit_a_member_so_the_two_"
           "readings_failed_for_a_structural_reason_not_a_label_error")
V_SELFONLY = ("excluding_the_census_family_removes_only_the_family_s_own_measurements_so_self_exclusion_"
              "is_a_population_definition_rather_than_a_green_leg")

MAX_ROWS = 40

# Reading the corpus at a commit is a pure function of that commit; the same tree is asked for by
# two windows whenever two faces share a closer, and by every selftest/verify pass.
_CORPUS_CACHE = {}


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def relp(path):
    return (path or "").replace("\\", "/")


# ---------------------------------------------------------------------------------- text currency

def stems(text):
    """Face stems a source names, deduplicated, sorted.

    Two spellings and nothing else: a dated literal and a ``%s`` FACE template.  A bare uppercase
    ``NAME.json`` is deliberately NOT a stem even though published mirrors look like one -- the
    census studies' own selftests spell fixtures (``AAA.json``, ``OUT.json``, ``QUIET.json``), and
    admitting those would put fake names into the writer census.
    """
    found = set()
    for rx in STEM_PATTERNS:
        for match in rx.finditer(text or ""):
            found.add(match.group(1))
    return sorted(found)


def mentions(text, stem):
    """``stem`` appears as a standalone token (not inside a longer name)."""
    return re.search(r"\b%s\b" % re.escape(stem), text or "") is not None


def size_of(text):
    text = text or ""
    return {
        "bytes": len(text.encode("utf-8")),
        "lines": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
        "sources": 1,
    }


def names_only(candidates, published):
    """Keep only stems some analysed face actually publishes under.

    Without this gate a census study's own selftest fixtures become names: ``NAME-1.2.3``,
    ``OUT-2026-01-01.json``, ``AAA-2026-01-01.json`` are spelled in the family's fake arms, and an
    unfiltered census reported 34 stems of which 12 were fixtures (found on the first burn: the
    exclusion-cost table listed ``AAA``/``FOO``/``QUIET`` as orphaned names).
    """
    return sorted(set(candidates) & set(published))


def published_stems(sha):
    """Stems that some face under ``results/`` is actually published under at ``sha``."""
    listing = e338._git("ls-tree", "-r", "--name-only", sha, "--", "results")
    found = set()
    for name in listing.splitlines():
        base = relp(name).rsplit("/", 1)[-1]
        match = re.match(r"^([A-Z][A-Z0-9_]{2,40})-\d{4}-\d{2}-\d{2}\.json$", base)
        if match:
            found.add(match.group(1))
            continue
        match = re.match(r"^([a-z][a-z0-9_]{2,40})_latest\.json$", base)
        if match:
            found.add(match.group(1).upper())
    return found


def classify(path, text, known_stems):
    """First match wins: the wiring file is not a "name writer" even though it names everything."""
    path = relp(path)
    if path.startswith(S6_PREFIX):
        return "s6_wiring"
    if path in set(e338.CENSUS_FAMILY):
        return "census_study"
    if any(mentions(text, stem) for stem in known_stems):
        return "name_writer"
    return "unrelated"


# ---------------------------------------------------------------------------------- git plumbing

def text_at(sha, path):
    """File text at a commit; empty string when the path does not exist there."""
    out = e338._git("show", "%s:%s" % (sha, path))
    return out or ""


def pinned_corpus(sha):
    """``{rel_path: text}`` for every .py in the five packages at ``sha``."""
    if sha in _CORPUS_CACHE:
        return _CORPUS_CACHE[sha]
    listing = e338._git("ls-tree", "-r", "--name-only", sha, "--", *e338.PATHS)
    paths = [relp(p) for p in listing.splitlines() if p.strip().endswith(".py")]
    if not paths:
        return {}
    query = "".join("%s:%s\n" % (sha, p) for p in paths)
    import subprocess
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT, input=query.encode("utf-8"),
                          capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("git cat-file --batch rc=%s" % proc.returncode)
    blob = proc.stdout
    out = {}
    pos = 0
    for path in paths:
        end = blob.find(b"\n", pos)
        if end < 0:
            break
        header = blob[pos:end].decode("utf-8", "replace")
        pos = end + 1
        parts = header.split()
        if len(parts) < 3 or parts[1] == "missing":
            continue
        try:
            size = int(parts[2])
        except ValueError:
            continue
        body = blob[pos:pos + size]
        pos += size + 1
        out[path] = body.decode("utf-8", "replace")
    _CORPUS_CACHE[sha] = out
    return out


# ---------------------------------------------------------------------------------------- windows

def closing_windows():
    """Oldest-first census landings paired with the next .py-touching commit.

    Re-derived from the git log rather than read off the E338 face: an upstream face is evidence,
    not input, and this legs the same quantity a second time.
    """
    events = e338.touch_events()
    rows = []
    for face in e338.CENSUS_FAMILY:
        idx = next((i for i, ev in enumerate(events) if face in ev["added"]), None)
        if idx is None:
            rows.append({"face": face, "landing_sha": None, "closing_sha": None,
                         "note": "no commit adds this file -- untracked or renamed"})
            continue
        closer = next((ev for ev in events[idx + 1:]
                       if ev["added"] or ev["removed"] or ev["modified"]), None)
        if closer is None:
            rows.append({"face": face, "landing_sha": events[idx]["sha"], "closing_sha": None,
                         "note": "no later commit touches a .py in the population"})
            continue
        rows.append({"face": face, "landing_sha": events[idx]["sha"],
                     "closing_sha": closer["sha"], "landing_ts": events[idx]["ts"],
                     "closing_ts": closer["ts"], "closing_added": list(closer["added"]),
                     "closing_removed": list(closer["removed"]),
                     "closing_modified": list(closer["modified"])})
    return rows


def measure_window(row, published):
    """Split the closer's effect on the corpus into composition and content."""
    closer = row["closing_sha"]
    parent = closer + "^"
    added = [relp(p) for p in row["closing_added"]]
    modified = [relp(p) for p in row["closing_modified"]]
    removed = [relp(p) for p in row["closing_removed"]]

    before = {p: text_at(parent, p) for p in modified + removed}
    after = {p: text_at(closer, p) for p in added + modified}
    corpus_before = pinned_corpus(parent)

    known = set()
    for text in list(before.values()) + list(after.values()):
        known.update(stems(text))
    known = set(names_only(known, published))

    # composition: names the new member brings, split by whether anything already named them.
    # "Already named" is read off the tree the commit landed on, not off the touched files: a
    # census study naming its sibling is exactly the case where the sibling's own script, far away
    # in the corpus, already carries the name.
    gained = {}
    for path in added:
        for stem in names_only(stems(after.get(path, "")), published):
            gained.setdefault(stem, []).append(path)
    writers_before = {stem: sum(1 for text in corpus_before.values() if mentions(text, stem))
                      for stem in gained}
    attached = sorted(stem for stem, n in writers_before.items() if n > 0)
    fresh = sorted(stem for stem, n in writers_before.items() if n == 0)
    # content: names whose membership changed inside files that already existed
    moved = {}
    for path in modified:
        old_names = set(names_only(stems(before.get(path, "")), published))
        new_names = set(names_only(stems(after.get(path, "")), published))
        for stem in sorted(new_names - old_names):
            moved.setdefault(stem, {"added_in": [], "dropped_in": []})["added_in"].append(path)
        for stem in sorted(old_names - new_names):
            moved.setdefault(stem, {"added_in": [], "dropped_in": []})["dropped_in"].append(path)

    size = {"sources_added": len(added), "sources_removed": len(removed),
            "bytes_added": sum(size_of(after.get(p, ""))["bytes"] for p in added),
            "lines_added": sum(size_of(after.get(p, ""))["lines"] for p in added),
            "bytes_delta_modified": sum(size_of(after.get(p, ""))["bytes"] -
                                        size_of(before.get(p, ""))["bytes"] for p in modified),
            "lines_delta_modified": sum(size_of(after.get(p, ""))["lines"] -
                                        size_of(before.get(p, ""))["lines"] for p in modified)}

    classified = {}
    for path in added:
        classified[path] = classify(path, after.get(path, ""), known)
    for path in modified:
        classified[path] = classify(path, after.get(path, ""), known)
    for path in removed:
        classified[path] = classify(path, before.get(path, ""), known)

    # the "attaches to an existing measurement" case: the new member names a stem something else
    # already named before the commit landed
    return {
        "face": row["face"],
        "landing_sha": row["landing_sha"],
        "closing_sha": closer,
        "closing_added": added,
        "closing_modified": modified,
        "closing_removed": removed,
        "classified": classified,
        "by_class": _count(classified.values()),
        "names": {
            "composition_only": fresh,
            "attached_to_an_existing_name": attached,
            "writers_before": {k: writers_before[k] for k in sorted(writers_before)},
            "moved_by_content": {k: v for k, v in sorted(moved.items())},
            "stems_in_the_closer": sorted(known & (set(gained) | set(moved))),
        },
        "corpus_before_sources": len(corpus_before),
        "size": size,
        "summary": {
            "added_files": len(added),
            "modified_files": len(modified),
            "names_gained_by_composition": len(fresh) + len(attached),
            "names_with_no_writer_before": len(fresh),
            "names_attached_to_an_existing_one": len(attached),
            "names_moved_by_content": len(moved),
            "content_moved_any_name": bool(moved),
        },
    }


# --------------------------------------------------------------------------- exclusion at the pin

def exclusion_cost(corpus, universe):
    """What the 16 census files contribute to the corpus and to the name currency."""
    family = set(e338.CENSUS_FAMILY)
    total = {"sources": len(corpus), "bytes": 0, "lines": 0}
    kept = {"sources": 0, "bytes": 0, "lines": 0}
    for path, text in corpus.items():
        body = size_of(text)
        total["bytes"] += body["bytes"]
        total["lines"] += body["lines"]
        if path not in family:
            kept["sources"] += 1
            kept["bytes"] += body["bytes"]
            kept["lines"] += body["lines"]

    rows = []
    for stem in universe:
        all_writers = [p for p, t in corpus.items() if mentions(t, stem)]
        non_census = [p for p in all_writers if p not in family]
        rows.append({"stem": stem, "writers": len(all_writers),
                     "writers_without_the_family": len(non_census),
                     "rows_removed": len(all_writers) - len(non_census),
                     "orphaned": (not non_census) and bool(all_writers),
                     "lost": [p for p in all_writers if p in family][:8]})
    rows.sort(key=lambda r: (-r["rows_removed"], r["stem"]))

    orphaned = [r["stem"] for r in rows if r["orphaned"]]
    return {
        "pin_sha": PIN_SHA,
        "family_size": len(family),
        "corpus": {"with_the_family": total, "without_the_family": kept,
                   "share_of_sources": _share(len(family), total["sources"]),
                   "share_of_lines": _share(total["lines"] - kept["lines"], total["lines"]),
                   "share_of_bytes": _share(total["bytes"] - kept["bytes"], total["bytes"])},
        "stems_measured": len(universe),
        "stems_with_a_writer": sum(1 for r in rows if r["writers"]),
        "stems_losing_a_writer": sum(1 for r in rows if r["rows_removed"]),
        "writer_rows_removed": sum(r["rows_removed"] for r in rows),
        "names_orphaned": orphaned,
        "names_orphaned_count": len(orphaned),
        "rows": rows[:MAX_ROWS],
        "rows_truncated": max(0, len(rows) - MAX_ROWS),
    }


def _share(part, whole):
    return None if not whole else round(float(part) / float(whole), 6)


def _count(values):
    out = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return {k: out[k] for k in CLASSES if k in out}


# ----------------------------------------------------------------------------------------- decide

def decide(summary, exclusion):
    """Frozen rule; the verdict is a function of the published summary only.

    Two facts decide it: whether the in-place half of the closing commit ever moved a name, and
    whether excluding the family would leave any measured name without a writer.
    """
    windows = summary.get("windows_closed", 0)
    if windows == 0:
        return V_NONE
    orphaned = exclusion.get("names_orphaned_count", 0)
    if orphaned <= 0:
        return V_SELFONLY
    if not summary.get("windows_where_content_moved_a_name", 0):
        return V_TWO_IN_ONE
    return V_MIXED


# ------------------------------------------------------------------------------------------ build

def build(root=None):
    root = root or ROOT
    rows = closing_windows()
    published = published_stems(PIN_SHA)
    measured = [measure_window(row, published) for row in rows if row.get("closing_sha")]
    say("census windows: %s listed, %s closed | published face stems at the pin: %s"
        % (len(rows), len(measured), len(published)))

    closed_by = {}
    for row in measured:
        closed_by.setdefault(row["closing_sha"], []).append(row["face"])

    total_size = {k: 0 for k in ("sources_added", "bytes_added", "lines_added",
                                 "bytes_delta_modified", "lines_delta_modified")}
    for row in measured:
        for key in total_size:
            total_size[key] += row["size"][key]

    summary = {
        "windows_listed": len(rows),
        "windows_closed": len(measured),
        "distinct_closing_commits": len(closed_by),
        "windows_where_the_new_member_introduces_a_name_nothing_named_before": sum(
            1 for r in measured if r["summary"]["names_with_no_writer_before"] > 0),
        "windows_where_the_new_member_names_an_existing_face": sum(
            1 for r in measured if r["summary"]["names_attached_to_an_existing_one"] > 0),
        "windows_where_content_moved_a_name": sum(
            1 for r in measured if r["summary"]["content_moved_any_name"]),
        "windows_that_only_grew_the_corpus": sum(
            1 for r in measured
            if r["summary"]["names_gained_by_composition"] and not r["summary"]["content_moved_any_name"]),
        "files_the_closers_touch_by_class": _count(
            [c for r in measured for c in r["classified"].values()]),
        "composition_and_content_totals": total_size,
    }

    universe = sorted({s for r in measured for s in r["names"]["stems_in_the_closer"]})
    corpus = pinned_corpus(PIN_SHA)
    say("pinned corpus at %s: %s sources" % (PIN_SHA[:9], len(corpus)))
    exclusion = exclusion_cost(corpus, universe)

    verdict = decide(summary, exclusion)
    reasons = [
        "every closer adds a census study and edits the wiring file in the same commit: %s census "
        "studies and %s wiring edits over %s distinct commits"
        % (summary["files_the_closers_touch_by_class"].get("census_study", 0),
           summary["files_the_closers_touch_by_class"].get("s6_wiring", 0),
           summary["distinct_closing_commits"]),
        "the added member names its own face in %s/%s windows and names a stem that already had a "
        "writer in %s/%s, so the corpus grows by a self-named measurement every time"
        % (summary["windows_where_the_new_member_introduces_a_name_nothing_named_before"],
           summary["windows_closed"],
           summary["windows_where_the_new_member_names_an_existing_face"], summary["windows_closed"]),
        "the wiring half moves %s name(s) while editing %s lines / %s bytes in place, so it is "
        "visible to every counting face and invisible to the name census -- that is why E338's two "
        "readings coincided"
        % (summary["windows_where_content_moved_a_name"],
           total_size["lines_delta_modified"], total_size["bytes_delta_modified"]),
        "excluding the family at the pin removes %.1f%% of sources and %.1f%% of lines and leaves "
        "%s of %s measured names with no writer at all"
        % (100.0 * (exclusion["corpus"]["share_of_sources"] or 0),
           100.0 * (exclusion["corpus"]["share_of_lines"] or 0),
           exclusion["names_orphaned_count"], exclusion["stems_measured"]),
    ]

    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "definition": {
            "population": "every .py under scripts/Tools/live/monitor/firm (e323.corpus())",
            "landing": "the commit that first adds a census face (oldest add, not a re-add)",
            "closing": "the next commit touching any .py in the population",
            "family": list(e338.CENSUS_FAMILY),
            "stem": ("the uppercase token a face name is built from: before -YYYY-MM-DD.json, "
                     "before -%s.json in a FACE template, or before .json in an uppercase mirror"),
            "writer": "a source that names the stem as a standalone token",
            "composition": "the closer added a source that did not exist before",
            "content": "the closer changed the text of a source that already existed",
            "verdict_rule": ("attach_share >= 0.9 and exclusion orphans a name -> coupled; "
                             "exclusion orphans a name -> mixed; otherwise self_exclusion_is_a_definition"),
        },
        "summary": summary,
        "windows": measured,
        "windows_unclosed": [r for r in rows if not r.get("closing_sha")],
        "exclusion_cost": exclusion,
        "verdict": verdict,
        "reasons": reasons,
        "limits": {
            "name_currency_is_a_proxy": ("no census face is re-run at each closing commit -- the "
                                         "population those faces read is not reconstructible from an "
                                         "old tree alone.  The mover is measured in the family's own "
                                         "needle currency (stems named by a source), which is the "
                                         "composed step of E322's needle, not a published number"),
            "pinned_commit": ("the exclusion cost is read at %s; this study's own file lands after it, "
                              "so the pinned corpus is one .py smaller than the tree that publishes "
                              "this face" % PIN_SHA[:9]),
            "self_disclosure": ("this file is itself a new .py in the population every census face "
                                "reads, so it closes windows the same way its siblings did"),
        },
    }
    _write(doc, root)
    return doc


def _write(doc, root=None):
    outdir = os.path.join(root or ROOT, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    for name in (FACE, LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")


# ----------------------------------------------------------------------------------------- verify

def _cmp(a, b, path, out):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append("%s: type %s vs %s" % (path, type(a).__name__, type(b).__name__))
        return
    if isinstance(a, dict):
        for key in set(a) | set(b):
            if key in ("generated", "asof_head"):
                continue
            if key not in a or key not in b:
                out.append("%s.%s: present in only one side" % (path, key))
                continue
            _cmp(a[key], b[key], "%s.%s" % (path, key), out)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            out.append("%s: length %s vs %s" % (path, len(a), len(b)))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp(x, y, "%s[%s]" % (path, i), out)
        return
    if isinstance(a, float):
        if abs(a - b) > 1e-9:
            out.append("%s: %r vs %r" % (path, a, b))
        return
    if a != b:
        out.append("%s: %r vs %r" % (path, a, b))


def verify(root=None):
    root = root or ROOT
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    fresh = build(root)
    problems = []
    _cmp(disk, fresh, "face", problems)
    return problems


# --------------------------------------------------------------------------------------- selftest

def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    # -- stems
    check("L1 a dated literal is a stem",
          stems('FACE = "REFUSALCAUSE-2026-10-31.json"') == ["REFUSALCAUSE"])
    check("L2 a FACE template is the same stem",
          stems('FACE = "GREENWINDOW-%s.json" % TODAY') == ["GREENWINDOW"])
    check("L3 a bare uppercase .json is not a stem -- a selftest fixture spells AAA.json",
          stems('"SIBLINGENTRY.json"') == [], str(stems('"SIBLINGENTRY.json"')))
    check("L4 a lowercase json is not a stem",
          stems('"allowance_latest.json"') == [], str(stems('"allowance_latest.json"')))
    check("L5 a bare date is not a face name", stems("as of 2026-10-31 nothing") == [])
    check("L6 a stem's own prefix is not a second stem", stems('"XYZ-2026-10-31.json"') == ["XYZ"],
          str(stems('"XYZ-2026-10-31.json"')))
    check("L7 stems dedupe across spellings",
          stems('"ABCD-2026-01-01.json" and "ABCD-%s.json"') == ["ABCD"],
          str(stems('"ABCD-2026-01-01.json" and "ABCD-%s.json"')))
    check("L8 a stem inside a longer token does not count",
          not mentions("REACHWIDER", "REACHWIDE") and mentions(" REACHWIDE ", "REACHWIDE"))

    # -- size
    body = size_of("a\nb\n")
    check("L9 line count follows the trailing newline", body["lines"] == 2, str(body))
    check("L10 a file without a trailing newline still counts its last line",
          size_of("a\nb")["lines"] == 2, str(size_of("a\nb")))
    check("L11 bytes are utf-8", size_of("\u4e2d")["bytes"] == 3, str(size_of("\u4e2d")))

    # -- classify, first match wins
    known = {"GREENWINDOW"}
    check("L12 the wiring file is s6_wiring even when it names everything",
          classify("Tools/s6_chain_bmb.py", "GREENWINDOW", known) == "s6_wiring")
    check("L13 a family member is census_study",
          classify(e338.CENSUS_FAMILY[0], "GREENWINDOW", known) == "census_study")
    check("L14 a source that names a stem is a name_writer",
          classify("scripts/x.py", 'F = "GREENWINDOW-%s.json"', known) == "name_writer")
    check("L15 an unrelated source is unrelated",
          classify("scripts/x.py", "print(1)", known) == "unrelated")
    check("L16 a family member named as a name_writer is still census_study",
          classify(e338.CENSUS_FAMILY[1], "GREENWINDOW", known) == "census_study")

    # -- decomposition arithmetic
    row = {"closing_sha": None}
    check("L17 a window without a closer is not measured", row.get("closing_sha") is None)
    fake = {"size": {"sources_added": 1, "bytes_added": 100, "lines_added": 10,
                     "bytes_delta_modified": -5, "lines_delta_modified": 2}}
    total = {"sources_added": 0}
    for key in fake["size"]:
        total[key] = total.get(key, 0) + fake["size"][key]
    check("L18 composition and content accumulate separately",
          total["sources_added"] == 1 and total["bytes_added"] == 100
          and total["bytes_delta_modified"] == -5, str(total))

    # -- exclusion arithmetic
    corpus = {"scripts/a.py": "GREENWINDOW", "scripts/b.py": "GREENWINDOW",
              e338.CENSUS_FAMILY[0]: "GREENWINDOW ONLYHERE"}
    cost = exclusion_cost(corpus, ["GREENWINDOW", "ONLYHERE"])
    check("L19 exclusion counts the sources it would drop",
          cost["corpus"]["with_the_family"]["sources"] == 3
          and cost["corpus"]["without_the_family"]["sources"] == 2, str(cost["corpus"]))
    check("L20 a name the family alone names is orphaned",
          cost["names_orphaned"] == ["ONLYHERE"], str(cost["names_orphaned"]))
    check("L21 a name production also names loses one row, not all",
          [r for r in cost["rows"] if r["stem"] == "GREENWINDOW"][0]["rows_removed"] == 1,
          str(cost["rows"]))
    check("L22 share of sources is a fraction", cost["corpus"]["share_of_sources"] > 0.33, "")

    # -- decide, frozen rule
    okay = {"windows_closed": 10, "windows_where_content_moved_a_name": 0}
    orphan = {"names_orphaned_count": 1}
    clean = {"names_orphaned_count": 0}
    check("L23 no window -> none", decide({"windows_closed": 0}, orphan) == V_NONE)
    check("L24 content never moves a name + an orphan -> two halves",
          decide(okay, orphan) == V_TWO_IN_ONE)
    check("L25 no orphan -> self-only", decide(okay, clean) == V_SELFONLY)
    check("L26 content moved a name + an orphan -> mixed",
          decide({"windows_closed": 10, "windows_where_content_moved_a_name": 2},
                 orphan) == V_MIXED)
    check("L27 rows are bounded", len(exclusion_cost(
        {"scripts/a.py": "X"} | {}, ["X"])["rows"]) <= MAX_ROWS)

    # -- the face, when it exists, must agree with its own verdict function
    path = os.path.join(OUTDIR, FACE)
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        check("L28 published verdict is the frozen rule's output",
              doc.get("verdict") == decide(doc.get("summary") or {},
                                           doc.get("exclusion_cost") or {}),
              "%s vs %s" % (doc.get("verdict"),
                            decide(doc.get("summary") or {}, doc.get("exclusion_cost") or {})))
        check("L29 the latest mirror carries the whole face",
              json.load(io.open(os.path.join(OUTDIR, LATEST), encoding="utf-8")) == doc, "")
        check("L30 every closed window published a class for each touched file",
              all(set(w["classified"]) == set(w["closing_added"]) | set(w["closing_modified"]) |
                  set(w["closing_removed"]) for w in doc.get("windows") or []), "")
        check("L31 the verdict is in the frozen set",
              doc.get("verdict") in (V_NONE, V_TWO_IN_ONE, V_MIXED, V_SELFONLY), "")

    passed = sum(1 for _n, ok, _d in checks if ok)
    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if (detail and not ok) else ""))
    say("selftest: %s/%s" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


# -------------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    s, e = doc["summary"], doc["exclusion_cost"]
    say("%s -> results/state_tilt/%s" % (STUDY, FACE))
    say("verdict: %s" % doc["verdict"])
    say("windows: %s closed of %s listed | distinct closing commits %s"
        % (s["windows_closed"], s["windows_listed"], s["distinct_closing_commits"]))
    say("classes the closers touch: " + " | ".join("%s=%s" % (k, v)
                                                   for k, v in s["files_the_closers_touch_by_class"].items()))
    say("composition: +%s sources / +%s lines | content: %s lines in place"
        % (s["composition_and_content_totals"]["sources_added"],
           s["composition_and_content_totals"]["lines_added"],
           s["composition_and_content_totals"]["lines_delta_modified"]))
    say("windows naming an existing face: %s/%s | windows where content moved a name: %s"
        % (s["windows_where_the_new_member_names_an_existing_face"], s["windows_closed"],
           s["windows_where_content_moved_a_name"]))
    say("exclusion at %s: family %s files = %s%% of sources, %s%% of lines | %s name(s) orphaned"
        % (e["pin_sha"][:9], e["family_size"], round(100 * (e["corpus"]["share_of_sources"] or 0), 2),
           round(100 * (e["corpus"]["share_of_lines"] or 0), 2), e["names_orphaned_count"]))
    for reason in doc["reasons"]:
        say("  - %s" % reason)
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        say("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    say("verify: 0 problems")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))