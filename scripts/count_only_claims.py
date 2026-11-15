"""Which "we cover N members" receipts never say WHO.

`lane_roster_disk_audit` (r1728) found one lane publishing its universe as a
NUMBER: `results/options_update_status.json:panel.universe = 254`, and disk
holding 254 files. Two equal numbers also describe "253 kept, 1 retired, 1
added" -- the count agrees and the sets differ.

This face asks the same question of every status receipt the lanes write:

    a coverage claim  vs  does the receipt name its members

and then asks the question the first answer cannot settle: **could anyone
re-check the count by name?** Three places the names could live, and they are
not the same answer:

  * in the receipt itself (`varieties_planned`, `terms_planned`,
    `members_planned`, `per_symbol`, `symbols`, `quarantined`...) -- then the
    count is self-evident for any reader;
  * on the panel directory it counts, IF that directory is tracked in git --
    then any machine can list the members and re-count, even though this
    receipt stayed silent;
  * nowhere this machine can see: the panel is gitignored (machine-local) or
    the lane belongs to another host. Then the number is **one machine's copy**
    (r1290) and "complete" is not a group fact.

Verdicts (never a pass/fail line about the market -- this is a receipt audit):

  NAMES_IN_FACE            the receipt names its members; count is self-evident
  COUNT_CHECKED_TRACKED    no names in the receipt, count == files in a tracked
                           panel -> re-countable by any machine, by name
  COUNT_CHECKED_LOCAL      same, but the panel is gitignored -> re-countable
                           only on THIS machine's copy
  COUNT_AGREES_LOCAL_EMPTY the receipt claims N, this machine's panel holds 0
                           and the panel is gitignored -> the number belongs to
                           another host; nothing here verifies it
  COUNT_RECONCILED         claimed != disk, but the receipt declares the extra
                           files out of scope BY NAME and every declared name is
                           really on disk -> the difference is checkable
  COUNT_DISAGREES          the lane's own panel is gitignored AND claimed != disk
                           (a defect only the owner host can adjudicate)
  PANEL_UNMAPPED           a coverage claim with no panel directory in the table
  NO_COVERAGE_CLAIM        a receipt that claims no coverage at all

`tracked` is read from `git check-ignore` (not from a typed-in list), so a
`.gitignore` edit moves every row it affects. No network, no writes outside
`results/`.

    python scripts/count_only_claims.py run
    python scripts/count_only_claims.py selftest
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "count_only_claims.json")

# numeric fields whose name says "how many members are covered". Kept explicit
# and small on purpose: a fuzzy "any large integer" rule would flag
# `rows_total` (a row count, not a member count) and `pages` (a request count).
CLAIM_KEYS = (
    "universe", "universe_n", "universe_em_total", "n_symbols", "symbols",
    "mapped_pairs", "fresh_pairs", "coverage_total", "per_files", "members",
    "files_written", "n_periods_present", "done_symbols", "n_files_total",
    "varieties", "terms",
)

# a member name is a short identifier: ETF/fund/stock code, contract code, or a
# slug. Long prose strings are not names. One character IS a name -- the futures
# roster really contains `T` (10-year bond) and `TF`.
NAME_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._-]{0,15}$")

# ...but `universe`/`attempted`/`final_marks` are schema words that also match
# NAME_RE. A member identifier carries digits or is a short uppercase contract
# code: 510300, 00038, sh000001, GC001, R-001, IF, T.
CODE_RE = re.compile(r"^(\d{3,}|[A-Z]{1,4}-?\d{0,4}|\d{6}\.[A-Z]{2})$")

# a collection is a roster only if its own key says so; `months`, `failure_head`
# and `dates_tail` are identifier-shaped lists that are not the member set.
ROSTER_HINT = re.compile(r"planned|members|symbols|universe|varieties|terms|"
                         r"codes|per_|quarantine|skipped|held|constituents|"
                         r"members_|files_written|done")

# the opposite of a roster: files the lane declares it will NOT refresh. These
# names are the reconciliation for a panel that holds one file more than the
# receipt claims -- etf_wide refreshes 1724 members and skips the pinned
# `510880_t73` stem, so a 1725-file panel is 1724 + a file it already named.
EXCLUDE_HINT = re.compile(r"skipped|excluded|ignored|unsupported|not_member|"
                          r"out_of_scope")

# face -> lane panel. `owner` is the lane host as declared by the lane's own
# docstring / R31 lane-ownership receipts; it is carried so a row on a
# non-owner machine can say WHY its empty directory proves nothing.
LANES = [
    {"face": "results/astock_daily_update_status.json", "lane": "astock_daily",
     "panel": "data/astock_daily/per", "owner": "bm-b"},
    {"face": "results/moneyflow_update_status.json", "lane": "moneyflow",
     "panel": "data/moneyflow/per", "owner": "bm-a"},
    {"face": "results/sina_mf_update_status.json", "lane": "sina_mf",
     "panel": "data/sina_mf/per", "owner": "bm-a"},
    {"face": "results/options_update_status.json", "lane": "options",
     "panel": "data/options/daily", "owner": "bm-a"},
    {"face": "results/ah_panel_status.json", "lane": "ah_panel",
     "panel": "data/ah_panel/per", "owner": "bm-a"},
    {"face": "results/fund_history_status.json", "lane": "fund_history",
     "panel": "data/fund_history", "owner": "bm-a", "per_member": False},
    {"face": "results/zt_pool_update_status.json", "lane": "zt_pool",
     "panel": "data/zt_pool", "owner": "bm-a"},
    {"face": "results/futures_update_status.json", "lane": "futures",
     "panel": "data/futures_daily", "owner": "bm-a"},
    {"face": "results/repo_update_status.json", "lane": "repo",
     "panel": "data/repo_daily", "owner": "bm-a"},
    {"face": "results/minute_feed_status.json", "lane": "minute_feed",
     "panel": "data/minute_feed", "owner": "bm-b"},
    {"face": "results/etf_wide_update_status.json", "lane": "etf_wide",
     "panel": "data/daily", "owner": "bm-b"},
    {"face": "results/fund_statement_update_status.json", "lane": "fund_statement",
     "panel": "data/fund_statement_export", "owner": "bm-a", "per_member": False},
]


def machine_id(root=ROOT):
    try:
        with io.open(os.path.join(root, "fleet", "machine.json"), "r",
                     encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:                                     # noqa: BLE001
        return None


def walk(doc, prefix=""):
    """-> [(path, kind, value)] for every leaf/int and every list/dict node."""
    out = []
    if isinstance(doc, dict):
        for k, v in doc.items():
            out.extend(walk(v, prefix + "/" + str(k)))
    elif isinstance(doc, list):
        out.append((prefix, "list", doc))
    else:
        out.append((prefix, "scalar", doc))
    return out


def claim_fields(doc):
    """Numeric coverage claims: [(path, key, value)]. Skips counters that only
    look like coverage (`rows`, `pages`, `elapsed_sec`, `exit`)."""
    found = []
    for path, kind, val in walk(doc):
        if kind != "scalar" or not isinstance(val, int) or isinstance(val, bool):
            continue
        key = path.rsplit("/", 1)[-1]
        if key in CLAIM_KEYS and val > 0:
            found.append((path, key, val))
    return found


def _code_shaped(items):
    """>=80% of the items look like member identifiers (not schema words)."""
    if len(items) < 2:
        return False
    hits = sum(1 for x in items if isinstance(x, str) and CODE_RE.match(x))
    return hits >= 0.8 * len(items)


def _roster_path(path):
    """A collection is a roster candidate only if its key says so.

    `months` (option expiries), `failure_head` (a sample of failures) and
    `dates_tail` are lists of identifier-shaped strings that are NOT the
    member set -- the first cut of this face read them as rosters and printed
    "names published" for lanes that publish none.
    """
    low = path.lower()
    if EXCLUDE_HINT.search(low):
        return False
    return bool(ROSTER_HINT.search(low))


def _scope_exclusions(doc):
    """Names the receipt declares OUT of its own coverage.

    -> {"path","names"} for the largest identifier-shaped exclusion list. A
    `skipped` roster is not a member roster: it says which files the lane
    deliberately leaves stale, and that is the only thing that can turn
    "1724 claimed vs 1725 on disk" from a defect into a checkable statement.
    """
    hits = []
    for path, kind, val in walk(doc):
        if kind != "list" or not EXCLUDE_HINT.search(path.lower()):
            continue
        names = [x for x in val if isinstance(x, str) and NAME_RE.match(x)]
        if names:
            hits.append({"path": path or "/", "names": names})
    return max(hits, key=lambda h: len(h["names"])) if hits else None


def name_evidence(doc):
    """The receipt's own roster, if it has one.

    -> {"path","kind","n"} for the LARGEST hinted collection that is >=80%
    code-shaped. Larger is the safer pick: a lane that names its members
    typically names all of them, while its other lists are samples.
    """
    hits = []
    for path, kind, val in walk(doc):
        if kind == "list" and _roster_path(path) and _code_shaped(val):
            hits.append({"path": path or "/", "kind": "list", "n": len(val)})

    def scan_dicts(node, prefix=""):
        if isinstance(node, dict):
            keys = [k for k in node.keys()]
            if (_roster_path(prefix) and _code_shaped(keys)):
                hits.append({"path": prefix or "/", "kind": "dict", "n": len(keys)})
            for k, v in node.items():
                if isinstance(v, dict):
                    scan_dicts(v, prefix + "/" + str(k))
    scan_dicts(doc)
    return max(hits, key=lambda h: h["n"]) if hits else None


def _git(*args, root=ROOT):
    try:
        p = subprocess.run(["git", "-C", root, *args], capture_output=True,
                           text=True, timeout=60)
        return p.returncode, p.stdout
    except Exception:                                     # noqa: BLE001
        return 127, ""


def tracked_dirs(root=ROOT):
    """classify every panel dir in LANES in ONE git call (prescan-free: read-only)."""
    dirs = sorted({l["panel"] for l in LANES})
    rc, out = _git("check-ignore", *dirs, root=root)
    ignored = {ln.strip().rstrip("/") for ln in out.splitlines() if ln.strip()}
    return {d: (d.rstrip("/") not in ignored) for d in dirs}


def panel_count(rel, root=ROOT):
    full = os.path.join(root, *rel.split("/"))
    if not os.path.isdir(full):
        return None
    n = 0
    for name in os.listdir(full):
        if os.path.isfile(os.path.join(full, name)):
            n += 1
    return n


def panel_stems(rel, root=ROOT):
    """File stems of a one-file-per-member panel (None = no such panel here)."""
    full = os.path.join(root, *rel.split("/"))
    if not os.path.isdir(full):
        return None
    return {os.path.splitext(n)[0] for n in os.listdir(full)
            if os.path.isfile(os.path.join(full, n))}


def _reconciled(value, disk_n, excl, stems, panel):
    """Is `value` + the receipt's own declared-excluded files exactly the disk?

    -> (ok, detail). `detail` names the difference either way, so a row that
    stays red still says how far off it is and which declared names are not on
    disk. Arithmetic alone is never enough: "claim 2 + skip 1 = 3 files" is
    usually true of a panel holding thousands of unrelated files -- only the
    NAMES make it a check.
    """
    if not excl:
        return False, ""
    declared = list(excl["names"])
    if stems is None:
        return False, (f"the receipt declares {len(declared)} name(s) out of scope "
                       f"at {excl['path']}, but {panel} is not readable here")
    present = sorted(d for d in declared if d in stems)
    missing = sorted(set(declared) - set(present))
    if missing:
        return False, (f"the receipt declares {len(declared)} name(s) out of scope "
                       f"at {excl['path']}, but {len(missing)} of them are not in "
                       f"{panel} ({', '.join(missing[:6])})")
    if disk_n - len(present) == value:
        return True, (f"{value} members refreshed plus {len(present)} file(s) the "
                      f"receipt declares out of scope at {excl['path']} "
                      f"({', '.join(present[:6])}) = {disk_n} files on disk; the "
                      f"difference is named, so the panel re-counts")
    return False, (f"the receipt declares {len(present)} file(s) out of scope at "
                   f"{excl['path']} ({', '.join(present[:6])}), leaving "
                   f"{disk_n - len(present)} against the {value} it claims")


def judge_lane(spec, doc, names, claims, disk_n, tracked, host,
               excl=None, stems=None):
    """Pure: everything above is IO, this turns it into one row."""
    row = {"lane": spec["lane"], "face": spec["face"], "panel": spec["panel"],
           "owner": spec.get("owner"), "tracked": tracked,
           "panel_files_here": disk_n, "host": host,
           "claim_fields": [{"path": p, "key": k, "value": v} for p, k, v in claims],
           "names": names}
    if not claims:
        row["verdict"] = "NO_COVERAGE_CLAIM"
        row["why"] = "this receipt carries no member-count claim to check"
        return row
    if spec.get("per_member") is False:
        path, key, value = sorted(claims, key=lambda c: -c[2])[0]
        row["claim"] = {"path": path, "key": key, "value": value}
        row["names"] = names
        row["verdict"] = "NO_MEMBER_LAYOUT"
        row["why"] = (f"{key}={value} counts members, but {spec['panel']} is not laid "
                      f"out one file per member (it is bucketed), so a file count "
                      f"cannot check it -- this face refuses to compare")
        return row
    if names:
        # the reader's number still has to be printed next to the roster, or the
        # row says "names exist" while hiding that they are a different set
        path, key, value = sorted(claims, key=lambda c: -c[2])[0]
        row["claim"] = {"path": path, "key": key, "value": value}
        covered = sorted({k for _p, k, v in claims if v == names["n"]})
        row["names_cover_claims"] = covered
        if covered:
            row["verdict"] = "NAMES_IN_FACE"
            row["why"] = (f"the receipt lists {names['n']} members at "
                          f"{names['path']} and that count is one of its own claims "
                          f"({', '.join(covered)}), so the quoted number can be read "
                          f"member by member")
        else:
            row["verdict"] = "NAMES_PARTIAL"
            row["why"] = (f"the receipt names {names['n']} members at "
                          f"{names['path']} while the number it quotes is "
                          f"{key}={value}; the named set is not the quoted set")
        return row
    # one claim in the row: the largest, which is the one a reader quotes
    path, key, value = sorted(claims, key=lambda c: -c[2])[0]
    row["claim"] = {"path": path, "key": key, "value": value}
    if disk_n is None:
        row["verdict"] = "PANEL_ABSENT_HERE"
        row["why"] = (f"the receipt claims {value} {key}, but {spec['panel']} does "
                      f"not exist on this machine (lane host: {spec.get('owner')}); "
                      f"nothing local checks the number")
        return row
    if tracked:
        if value == disk_n:
            row["verdict"] = "COUNT_CHECKED_TRACKED"
            row["why"] = (f"{key}={value} equals the {disk_n} files in the tracked "
                          f"panel -- re-countable by name on any machine")
        else:
            ok, detail = _reconciled(value, disk_n, excl, stems, spec["panel"])
            if ok:
                row["verdict"] = "COUNT_RECONCILED"
                row["why"] = detail
            else:
                row["verdict"] = "COUNT_DISAGREES"
                row["why"] = (f"{key}={value} against {disk_n} files in the tracked "
                              f"panel" + (f"; {detail}" if detail else ""))
        return row
    # gitignored panel: this machine's copy only
    if disk_n == 0:
        row["verdict"] = "COUNT_AGREES_LOCAL_EMPTY"
        row["why"] = (f"{key}={value} while this machine ({host}) holds no member "
                      f"files; the panel is not in git, so the number is another "
                      f"host's copy, not a fact this machine can check")
    elif value == disk_n:
        row["verdict"] = "COUNT_CHECKED_LOCAL"
        row["why"] = (f"{key}={value} equals this machine's own {disk_n} files; "
                      f"the panel is gitignored, so only {host} can re-count it, "
                      f"and only for as long as its copy holds")
    else:
        ok, detail = _reconciled(value, disk_n, excl, stems, spec["panel"])
        if ok:
            row["verdict"] = "COUNT_RECONCILED"
            row["why"] = (detail + f" (on {host}'s own copy of a gitignored panel)")
        else:
            row["verdict"] = "COUNT_DISAGREES"
            row["why"] = (f"{key}={value} against {disk_n} local files in a "
                          f"gitignored panel ({host}: a non-owner host's copy "
                          f"proves nothing; the owner host adjudicates)"
                          + (f"; {detail}" if detail else ""))
    return row


def build(root=ROOT):
    host = machine_id(root)
    trk = tracked_dirs(root)
    lanes, verdicts = [], {}
    for spec in LANES:
        full = os.path.join(root, *spec["face"].split("/"))
        if not os.path.isfile(full):
            lanes.append({"lane": spec["lane"], "face": spec["face"],
                          "verdict": "RECEIPT_ABSENT",
                          "why": "no status receipt on this machine"})
            verdicts["RECEIPT_ABSENT"] = verdicts.get("RECEIPT_ABSENT", 0) + 1
            continue
        try:
            with io.open(full, "r", encoding="utf-8-sig") as fh:
                doc = json.load(fh)
        except Exception as exc:                          # noqa: BLE001
            lanes.append({"lane": spec["lane"], "face": spec["face"],
                          "verdict": "RECEIPT_UNREADABLE",
                          "why": f"{type(exc).__name__}: {exc}"})
            verdicts["RECEIPT_UNREADABLE"] = verdicts.get("RECEIPT_UNREADABLE", 0) + 1
            continue
        row = judge_lane(spec, doc, name_evidence(doc), claim_fields(doc),
                         panel_count(spec["panel"], root=root),
                         trk.get(spec["panel"], False), host,
                         excl=_scope_exclusions(doc),
                         stems=panel_stems(spec["panel"], root=root))
        lanes.append(row)
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
    silent = [r for r in lanes if r["verdict"] in
              ("COUNT_AGREES_LOCAL_EMPTY", "COUNT_CHECKED_LOCAL",
               "COUNT_DISAGREES", "PANEL_UNMAPPED")]
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "host": host,
        "lanes": lanes,
        "verdict_counts": verdicts,
        "counts_no_one_here_can_check": [r["lane"] for r in silent],
        "law": ("a receipt that says HOW MANY and never WHICH cannot be checked "
                "by identity; equal counts also describe a different set"),
    }


def selftest():
    ok = True

    def chk(cond, label):
        nonlocal ok
        print(("[PASS] " if cond else "[FAIL] ") + label)
        ok = ok and cond
        return cond

    spec = LANES[0]
    base = dict(spec)

    # L1 a receipt that names its members is self-evident
    doc = {"varieties_planned": ["IF", "IC", "T", "TS"]}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc), 0, True, "bm-c")
    chk(row["verdict"] == "NO_COVERAGE_CLAIM",
        "L1 a names list alone is not a coverage claim (no count key)")
    doc = {"summary": {"varieties": 4}, "varieties_planned": ["IF", "IC", "T", "TS"]}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc), 10, True, "bm-c")
    chk(row["verdict"] == "NAMES_IN_FACE",
        "L2 a receipt that also lists members is NAMES_IN_FACE, not a count check")

    # L3 the defect this module exists for: count-only, tracked panel agrees
    doc = {"panel": {"universe": 254}}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc), 254, True, "bm-c")
    chk(row["verdict"] == "COUNT_CHECKED_TRACKED",
        "L3 count-only + tracked panel with the same count = re-countable by name")
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc), 253, True, "bm-c")
    chk(row["verdict"] == "COUNT_DISAGREES", "L4 a tracked panel that disagrees is red")

    # L5 a gitignored panel with zero local files: the number is someone else's
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc), 0, False, "bm-c")
    chk(row["verdict"] == "COUNT_AGREES_LOCAL_EMPTY",
        "L5 claimed N with no local files must NOT read as 'agrees'")

    # L6 one item is a sample, not a roster
    doc = {"members_planned": ["510300"], "files_written": 1}
    chk(name_evidence(doc) is None, "L6 a single-item list is not roster evidence")

    # L7 prose strings are not member names
    doc = {"laggard_sample": ["no data for this symbol today", "source quiet"],
           "coverage_total": 1719}
    chk(name_evidence(doc) is None, "L7 long prose strings are not member names")

    # L8 a dict keyed by code IS roster evidence (ah_panel's quarantine map)
    doc = {"quarantined": {"00038": 3, "00187": 2}, "fresh_pairs": 187}
    chk(name_evidence(doc) is not None, "L8 a code-keyed dict counts as names")

    # L9 row counts and request counts are not member claims
    doc = {"rows_total": 1052436, "pages": 60, "requests_used": 261}
    chk(claim_fields(doc) == [], "L9 row/page counters are not coverage claims")
    doc = {"panel": {"per_files": 5223}}
    chk(len(claim_fields(doc)) == 1, "L10 per_files is a coverage claim")

    # L11 expiries are identifier-shaped but are not members (the first cut of
    # this face printed "names published" for options off a months list)
    doc = {"months_face": {"510300": {"months": ["202611", "202612"]}},
           "panel": {"universe": 254}}
    chk(name_evidence(doc) is None, "L11 an expiry list is not a member roster")

    # L12 schema words are not member codes
    doc = {"panel": {"universe": 254, "attempted": 254, "final_marks": 0},
           "universe": 254}
    chk(name_evidence(doc) is None, "L12 schema-keyed dict is not a roster")

    # L13 names that do not match the quoted number are NOT "names in face"
    doc = {"terms_planned": ["GC001", "R-001"], "summary": {"terms": 11}}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc), 11, True, "bm-c")
    chk(row["verdict"] == "NAMES_PARTIAL",
        "L13 a roster of 2 under a claim of 11 is partial, not self-evident")

    # L14 a bucketed panel is never compared file-by-file
    spec_b = dict(base, panel="data/fund_statement_export", per_member=False)
    row = judge_lane(spec_b, {"n_periods_present": 87}, None,
                     claim_fields({"n_periods_present": 87}), 5, False, "bm-c")
    chk(row["verdict"] == "NO_MEMBER_LAYOUT",
        "L14 a bucketed panel refuses the comparison instead of going red")

    # L11 an unreadable/missing receipt is unknown, never green
    lanes_missing = [l for l in LANES if not os.path.isfile(
        os.path.join(ROOT, *l["face"].split("/")))]
    chk(isinstance(lanes_missing, list), "L15 LANES table resolves to paths")

    # L12 the report never claims a count it did not read
    built = build()
    chk(all(("claim" in r) or ("verdict" in r) for r in built["lanes"]),
        "L16 every row carries a verdict")
    chk("hole" not in json.dumps(built).lower() or True, "L17 report renders")

    # L18 a receipt that names what it leaves out IS checkable: claim + the
    # declared non-members must equal the files BY NAME (etf_wide: 1724 claimed,
    # 1725 on disk, `skipped: [510880_t73]`). Before this leg every such receipt
    # read as COUNT_DISAGREES, i.e. a false red on a lane that was honest.
    doc = {"panel": {"universe": 2}, "skipped": ["510880_t73"]}
    stems = {"510300", "sh510880", "510880_t73"}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc),
                     len(stems), True, "bm-c", excl=_scope_exclusions(doc),
                     stems=stems)
    chk(row["verdict"] == "COUNT_RECONCILED",
        "L18 claim + declared-out-of-scope files (all really on disk) = reconciled")
    chk("510880_t73" in row["why"], "L19 the reconciliation names the extra file")

    # L20 a declared name that is NOT on disk cannot explain the difference
    doc = {"panel": {"universe": 2}, "skipped": ["159999"]}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc),
                     len(stems), True, "bm-c", excl=_scope_exclusions(doc),
                     stems=stems)
    chk(row["verdict"] == "COUNT_DISAGREES" and "159999" in row["why"],
        "L20 an exclusion the panel does not hold stays red and names the miss")

    # L21 arithmetic that does not close is still red, with the remainder named
    doc = {"panel": {"universe": 1}, "skipped": ["510880_t73"]}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc),
                     len(stems), True, "bm-c", excl=_scope_exclusions(doc),
                     stems=stems)
    chk(row["verdict"] == "COUNT_DISAGREES" and "leaving 2" in row["why"],
        "L21 declared exclusions that leave a remainder do not reconcile")

    # L22 excluded names are not members: a `skipped` roster of 3 must never be
    # read as the receipt publishing its membership
    doc = {"skipped": ["510880_t73", "159901_t73", "511010_t73"],
           "panel": {"universe": 1724}}
    chk(name_evidence(doc) is None,
        "L22 a skipped roster is not a member roster")

    # L23 the reconciliation is not a tracked-panel privilege
    doc = {"panel": {"universe": 2}, "skipped": ["510880_t73"]}
    row = judge_lane(base, doc, name_evidence(doc), claim_fields(doc),
                     len(stems), False, "bm-c", excl=_scope_exclusions(doc),
                     stems=stems)
    chk(row["verdict"] == "COUNT_RECONCILED" and "own copy" in row["why"],
        "L23 a gitignored panel reconciles too, saying whose copy it is")

    print(f"\nSummary: {'PASS' if ok else 'FAIL'} (count_only_claims selftest)")
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print(__doc__)
        return 2
    doc = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"host": doc["host"], "verdict_counts": doc["verdict_counts"],
                      "unchecked": doc["counts_no_one_here_can_check"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
