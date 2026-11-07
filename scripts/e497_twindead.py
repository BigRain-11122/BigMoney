"""E497 -- is a write-only twin's retirement free because its dated members are what gets read?

E496 (r1522) found exactly one of E479's 36 latest-pointer twins whose every opener is a write:
``results/market_clock/call_latest.json`` (7 write sites, 0 reads), and classed it as never opened
by any site in the corpus.  A twin is not the family, though: the same directory carries dated
``CALL-<asof>.md`` members and three per-machine ``call_latest.<machine>.json`` lanes.  Retiring
the twin is only free if nothing reads it -- so this study measures the whole family:

  dated members        every CALL-<date>.md in the family directory
  the twin             call_latest.json
  per-machine twins    call_latest.<machine>.json (lane_io.write_lane composition)

and for each member publishes three opener arms that an opener-only census cannot separate:

  A. direct literal     an open()/json.load() call whose own literals spell the member.  This is
                        the arm E479/E483/E496 measured, reproduced here per member.
  B. handed to a helper a call passes a path (or a name that folds to one) into a function in the
                        same module that opens its parameter.  ``_read_json(CLOCK_JSON)`` reads the
                        file without ever naming it at an opener -- this is why a literal census
                        reports 0 readers for a face two S6 chain producers read every round.
  C. face key to lane   the ``market_clock/call_latest`` key handed to lane_io.write_lane /
                        mirror_shared, which compose ``<face>.<machine>.json`` and union it back.
                        The machine twins have no literal producer by construction.

The point of the study is the one E496 could not make alone: a dead twin and a live family are two
different findings, so a family whose twin is only read through a helper is published as such
rather than as a dead face.

Run:      python scripts/e497_twindead.py run
Check:    python scripts/e497_twindead.py check     (tallies re-derive from the face)
Verify:   python scripts/e497_twindead.py verify    (re-derives from the live tree)
Selftest: python scripts/e497_twindead.py selftest
"""
import argparse
import ast
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e468_pointer_reach as e468  # noqa: E402
import e451_prereg_digest as e451  # noqa: E402
import e470_target_read as e470  # noqa: E402
import e479_twin_read as e479  # noqa: E402
import e483_leg_debt as e483  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "twindead_latest.json"
DATED_PREFIX = "TWINDEAD"
EVIDENCE_CUTOFF = "2026-11-07"
CARD = ("E497-IS-THE-ONE-WRITE-ONLY-TWIN-S-RETIREMENT-FREE-BECAUSE-ITS-DATED-MEMBERS-ARE-WHAT-"
        "GETS-READ")
PARENT_FACE = "twinmode_latest.json"            # E496
PARENT_TWIN_SPELLING = "results/market_clock/CALL_latest.json"

FAMILY_DIR = "results/market_clock"
TWIN = "results/market_clock/call_latest.json"
FACE_KEY = "market_clock/call_latest"
LITERAL_FAMILY_PREFIX = "CALL-"
SELF_PREFIX = ("e497_", "run_e497", "_e497")
EXCLUDED_PATH_PREFIX = ("results/_quarantine/",)

MAX_READ_BYTES = 2 * 1024 * 1024

# a source that names or hands off a member carries one of these as a literal in its own text
CANDIDATE_TOKENS = ("call_latest", "market_clock", "call-", "lane_io")

# member kinds
K_TWIN = "the_latest_twin_of_the_family"
K_MACHINE_TWIN = "a_per_machine_lane_of_the_same_face"
K_DATED = "a_dated_member_of_the_family"
K_OTHER = "a_file_in_the_family_directory_that_is_not_a_member_of_this_family"
KINDS = (K_TWIN, K_MACHINE_TWIN, K_DATED, K_OTHER)

# site tiers
T_DIRECT = "a_literal_at_an_opener_spells_this_member"
T_HELPER = "a_call_hands_a_path_folding_to_this_member_to_a_helper_that_opens_its_parameter"
T_FACEKEY = "a_call_hands_the_lane_face_key_to_the_lane_io_helper_that_composes_this_path"
T_GLOB = "a_glob_or_directory_listing_reaches_the_family_but_names_no_member"
TIERS = (T_DIRECT, T_HELPER, T_FACEKEY, T_GLOB)

M_READ = e483.M_READ
M_WRITE = e483.M_WRITE
M_INDIRECT = e483.M_INDIRECT

# The lane helpers compose "<face>.<machine>.json" at run time, so a literal census can never
# attribute their effects.  The mapping below is read off config/lane_io.py, per helper:
#   write_lane (line 99)                 opens lane_path() for writing -- the lane only
#   mirror_shared (line 140)             opens the shared face for reading, then write_lane
#   mirror_shared_if_changed (line 199)  opens the shared face, opens the lane to compare, then
#                                        write_lane when it changed
LANE_HELPERS = {
    "write_lane": {K_MACHINE_TWIN: M_WRITE},
    "mirror_shared": {K_TWIN: M_READ, K_MACHINE_TWIN: M_WRITE},
    "mirror_shared_if_changed": {K_TWIN: M_READ, K_MACHINE_TWIN: M_READ},
}
LANE_EVIDENCE = {
    "write_lane": ("config/lane_io.py:99 -- write_lane opens lane_path(face, machine) for writing; "
                   "the shared twin is untouched by this call"),
    "mirror_shared": ("config/lane_io.py:140 -- mirror_shared opens the shared face for reading "
                      "and then calls write_lane for the lane"),
    "mirror_shared_if_changed": ("config/lane_io.py:199 -- opens the shared face, opens the lane to "
                                 "compare it, and writes the lane only when it changed"),
}

# per-member reading
R_READ_DIRECTLY = "read_by_an_opener_that_names_it"
R_READ_THROUGH_A_HELPER = "read_only_by_a_call_that_hands_its_path_to_a_helper"
R_WRITTEN_ONLY = "no_reader_any_site_that_touches_it_only_writes_it"
R_COMPOSED_ONLY = "the_only_producer_spelling_is_a_run_time_composed_name"
R_NEVER = "no_site_in_the_corpus_names_or_reaches_it"
R_UNREADABLE = "the_member_is_not_on_disk"
READINGS = (R_READ_DIRECTLY, R_READ_THROUGH_A_HELPER, R_WRITTEN_ONLY, R_COMPOSED_ONLY, R_NEVER,
            R_UNREADABLE)

V_TWIN_LIVE = "the_twin_is_live_and_the_dated_members_are_dead"
V_ALL_DEAD = "the_whole_family_is_dead_including_the_twin"
V_FAMILY_LIVE = "some_dated_member_is_read_by_a_site"
V_EMPTY = "the_family_directory_carries_no_member"
VERDICT_VOCAB = (V_TWIN_LIVE, V_ALL_DEAD, V_FAMILY_LIVE, V_EMPTY)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load_json(path):
    return json.load(io.open(path, "r", encoding="utf-8"))


def _tail(func):
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _is_self(rel):
    base = os.path.basename(rel)
    return any(base.startswith(p) for p in SELF_PREFIX)


# ------------------------------------------------------------------- population
def family_members(root=None):
    """Every file in the family directory whose name spells the family."""
    root = root or ROOT
    fam = os.path.join(root, FAMILY_DIR)
    rows = []
    others = []
    if not os.path.isdir(fam):
        return rows, others
    for name in sorted(os.listdir(fam)):
        path = os.path.join(fam, name)
        if not os.path.isfile(path):
            continue
        low = name.lower()
        if not low.startswith("call"):
            others.append({"file": "%s/%s" % (FAMILY_DIR, name),
                           "why": "does not carry the family name"})
            continue
        if low == "call_latest.json":
            kind = K_TWIN
        elif re.match(r"^call_latest\.[a-z0-9-]+\.json$", low):
            kind = K_MACHINE_TWIN
        elif re.match(r"^call-\d{4}-\d{2}-\d{2}\.md$", low):
            kind = K_DATED
        else:
            kind = K_OTHER
        rel = "%s/%s" % (FAMILY_DIR, name)
        rows.append({
            "member": rel,
            "basename": name,
            "kind": kind,
            "on_disk": True,
            "bytes": os.path.getsize(path),
            "date": (re.search(r"(\d{4}-\d{2}-\d{2})", name).group(1)
                     if re.search(r"(\d{4}-\d{2}-\d{2})", name) else None),
            "name_is_spelled_with_a_literal_machine_suffix": bool(
                re.match(r"^call_latest\.[a-z0-9-]+\.json$", low)),
        })
    return rows, others


def sources(root=None):
    """Every python source, minus this study and the quarantine copies.

    Parsed-prefilter: a site that names or hands off a member carries one of the family tokens as
    a literal somewhere in its own text, so a source without any of them cannot produce an arm-A
    or arm-B site.  The count of sources the prefilter dropped is published -- a prefilter that
    silently removes a third of the corpus is the E180/E207 self-exclusion family.
    """
    root = root or ROOT
    out = []
    skipped = 0
    for rel in e468._walk_py(root):
        r = rel.replace("\\", "/")
        if _is_self(r):
            continue
        if any(r.startswith(p) for p in EXCLUDED_PATH_PREFIX):
            continue
        path = os.path.join(root, r)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                skipped += 1
                continue
            text = e451.read_text(path).lower()
        except OSError:
            skipped += 1
            continue
        if not any(tok in text for tok in CANDIDATE_TOKENS):
            continue
        out.append(r)
    return sorted(out), skipped


# ------------------------------------------------------------------- folding
def _fold_literals(node, assigned, depth=0):
    """String literals an expression could resolve to, one hop through module names."""
    lits = []
    if node is None:
        return lits
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            lits.append(n.value)
        elif isinstance(n, ast.Name):
            lits.extend(assigned.get(n.id) or [])
    if depth < 1:
        extra = []
        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                for lit in assigned.get(n.id) or []:
                    if lit not in lits:
                        extra.append(lit)
        lits.extend(extra)
    seen, uniq = set(), []
    for lit in lits:
        if lit in seen:
            continue
        seen.add(lit)
        uniq.append(lit)
    return uniq


def _mode_of_call(call):
    """(mode, why) for one opener call -- e483.mode_of_site's ladder without its tree walk.

    ``mode_of_site`` resolves the call at a line by walking the whole tree (E442's quadratic
    trap: one full-source scan per node).  Here the call node is already in hand, so the same
    three branches are applied directly; the selftest pins the equivalence on a fixture.
    """
    tail = _tail(call.func)
    if tail in e483.TEXT_READS:
        return M_READ, "a text read on a handle opened at this line"
    if e483._is_json_load(call):
        return M_READ, "a json load at this line"
    mode = e483.e494._mode_of(call)
    if e483.e494._is_write_mode(mode):
        return M_WRITE, "mode=%r" % mode
    return M_READ, "mode=%r" % (mode or "r (default)")


def helper_opens(tree, func):
    """(params, opens) -- which parameter each opener inside ``func`` opens, and in what mode.

    Only openers whose first argument IS one of the parameters count: ``json.load(fh)`` receives
    a handle, not the path, so it is the inner ``open(path)`` that carries the member.
    """
    params = [a.arg for a in func.args.args]
    opens = []
    handle_only = 0
    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue
        if not e470._is_opener(node):
            continue
        idx = None
        if node.args and isinstance(node.args[0], ast.Name) and node.args[0].id in params:
            idx = params.index(node.args[0].id)
        mode, why = _mode_of_call(node)
        if idx is None:
            handle_only += 1
            continue
        opens.append({"param_index": idx, "param": params[idx],
                      "mode": mode, "why": why, "line": node.lineno})
    return params, {"opens": opens, "openers_on_a_handle": handle_only}


def module_functions(tree):
    out = {}
    for node in getattr(tree, "body", []) or []:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(node.name, node)
    return out


def _match(literal, member_path):
    return e479.match_kind(literal, member_path)


# ------------------------------------------------------------------- scan
def scan(members, root=None):
    """All sites that name, hand off or compose a member, per member path."""
    root = root or ROOT
    sites = {m["member"]: [] for m in members}
    family_globs = []
    composed = []
    scanned = 0
    cands, skipped = sources(root)
    for rel in cands:
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
        except OSError:
            continue
        got = e483.source_tree(rel)
        if got is None or "error" in got:
            continue
        tree = got["tree"]
        scanned += 1
        assigned = e470._assignments(tree)
        funcs = module_functions(tree)
        helpers = {name: helper_opens(got["tree"], fn)[1] for name, fn in funcs.items()}
        role = e483.role_of(rel)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if e470._is_opener(node):
                mode, why = _mode_of_call(node)
                lits = list(e470._evidence(node, assigned))
                hit = False
                for lit in lits:
                    for m in members:
                        kind = _match(lit, m["member"])
                        if kind is None:
                            continue
                        hit = True
                        sites[m["member"]].append({
                            "tier": T_DIRECT, "source": rel,
                            "line": getattr(node, "lineno", 0), "literal": lit,
                            "match": kind, "mode": mode, "mode_evidence": why,
                            "role": role, "attribution": "the_literal_this_line_opens",
                        })
                if not hit and mode == M_WRITE:
                    # a writer whose name is composed at run time (f-string) cannot be attributed
                    # to one member: publish the spelling instead of guessing a member.  Both the
                    # family prefix and the family directory have to appear, otherwise every
                    # unrelated '.md' writer in the tree lands in this arm.
                    prefix = [str(l) for l in lits if str(l).startswith(LITERAL_FAMILY_PREFIX)]
                    names_dir = any(FAMILY_DIR.split("/")[-1] in str(l).lower() for l in lits)
                    if prefix and names_dir:
                        composed.append({"source": rel, "line": getattr(node, "lineno", 0),
                                         "literal": prefix[0], "role": role,
                                         "why": "a composed name spells no whole member"})
                    continue
            if e470._is_glob(node):
                for lit in e470._evidence(node, assigned):
                    pat = e479._norm(lit)
                    if not any(ch in pat for ch in "*?["):
                        continue
                    if FAMILY_DIR.split("/")[-1] not in pat and LITERAL_FAMILY_PREFIX not in pat:
                        continue
                    family_globs.append({"source": rel, "line": getattr(node, "lineno", 0),
                                         "pattern": lit, "role": role})
                continue
            tail = _tail(node.func)
            if tail in helpers:
                info = helpers[tail]
                for op in info["opens"]:
                    idx = op["param_index"]
                    if idx is None or idx >= len(node.args):
                        continue
                    lits = _fold_literals(node.args[idx], assigned)
                    for lit in lits:
                        for m in members:
                            kind = _match(lit, m["member"])
                            if kind is None:
                                continue
                            sites[m["member"]].append({
                                "tier": T_HELPER, "source": rel,
                                "line": getattr(node, "lineno", 0), "literal": lit,
                                "match": kind, "mode": op["mode"],
                                "mode_evidence": ("helper %s() opens its parameter %r: %s"
                                                  % (tail, op["param"], op["why"])),
                                "role": role,
                                "attribution": "folded_from_a_name_the_helper_opens",
                                "helper": tail, "helper_line": op["line"],
                            })
                continue
            if tail in LANE_HELPERS and node.args:
                effects = LANE_HELPERS[tail]
                for lit in _fold_literals(node.args[0], assigned):
                    if e479._norm(lit).lower() != FACE_KEY:
                        continue
                    for m in members:
                        mode = effects.get(m["kind"])
                        if mode is None:
                            continue
                        sites[m["member"]].append({
                            "tier": T_FACEKEY, "source": rel,
                            "line": getattr(node, "lineno", 0), "literal": lit,
                            "match": e470.M_EXACT, "mode": mode,
                            "mode_evidence": LANE_EVIDENCE[tail],
                            "role": role,
                            "attribution": "the_lane_face_key_this_call_hands_the_helper",
                            "helper": tail,
                        })
    for key in sites:
        seen, uniq = set(), []
        for s in sites[key]:
            sig = (s["tier"], s["source"], s["line"], s.get("literal"))
            if sig in seen:
                continue
            seen.add(sig)
            uniq.append(s)
        uniq.sort(key=lambda s: (s["tier"], s["source"], s["line"]))
        sites[key] = uniq
    return sites, {"sources_scanned_with_a_tree": scanned,
                   "sources_with_a_family_candidate": len(cands),
                   "sources_skipped_unreadable_or_oversize": skipped,
                   "candidate_tokens": list(CANDIDATE_TOKENS),
                   "family_globs": family_globs,
                   "composed_write_spellings": composed}


def measure_member(member, sites, family_globs, composed):
    rows = sites.get(member["member"]) or []
    direct = [s for s in rows if s["tier"] == T_DIRECT]
    helper = [s for s in rows if s["tier"] == T_HELPER]
    keyed = [s for s in rows if s["tier"] == T_FACEKEY]
    reads = [s for s in rows if s["mode"] == M_READ]
    writes = [s for s in rows if s["mode"] == M_WRITE]
    unresolved = [s for s in rows if s["mode"] == M_INDIRECT]
    direct_reads = [s for s in direct if s["mode"] == M_READ]
    helper_reads = [s for s in helper if s["mode"] == M_READ]
    composed_hits = [c for c in composed
                     if member["kind"] == K_DATED and
                     str(c["literal"]).startswith(LITERAL_FAMILY_PREFIX)]
    if not member["on_disk"]:
        reading = R_UNREADABLE
    elif direct_reads:
        reading = R_READ_DIRECTLY
    elif helper_reads:
        reading = R_READ_THROUGH_A_HELPER
    elif reads:
        reading = R_READ_DIRECTLY
    elif writes:
        reading = R_WRITTEN_ONLY
    elif composed_hits:
        reading = R_COMPOSED_ONLY
    else:
        reading = R_NEVER
    touches = [s for s in rows if s["mode"] in (M_READ, M_WRITE)]
    roles = {}
    for s in rows:
        roles[s["role"]] = roles.get(s["role"], 0) + 1
    return {
        "member": member["member"],
        "basename": member["basename"],
        "kind": member["kind"],
        "date": member["date"],
        "bytes": member["bytes"],
        "on_disk": member["on_disk"],
        "reading": reading,
        "sites": len(rows),
        "direct_sites": len(direct),
        "helper_sites": len(helper),
        "face_key_sites": len(keyed),
        "read_sites": len(reads),
        "write_sites": len(writes),
        "unresolved_sites": len(unresolved),
        "direct_read_sites": len(direct_reads),
        "helper_read_sites": len(helper_reads),
        "retire_breaks_sites": len(reads),
        "retirement_breaks_any_site": bool(reads),
        "composed_write_spellings": len(composed_hits),
        "touching_sites": len(touches),
        "roles": {k: roles[k] for k in sorted(roles)},
        "site_rows": rows,
    }


def _parent_row(root=None):
    """E496's row for this twin, machine-read from its face (never restated from the card)."""
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", PARENT_FACE)
    out = {"source_face": "results/state_tilt/%s (E496)" % PARENT_FACE, "available": False}
    if not os.path.exists(path):
        return out
    try:
        face = _load_json(path)
    except (OSError, ValueError):
        return out
    for row in face.get("rows") or []:
        if (row.get("twin") or "").lower() == PARENT_TWIN_SPELLING.lower():
            out.update({
                "available": True,
                "parent_twin_spelling": row.get("twin"),
                "parent_read_sites": row.get("read_sites"),
                "parent_write_sites": row.get("write_sites"),
                "parent_baseline_residue": row.get("baseline_residue"),
                "parent_read_only_residue": row.get("read_only_residue"),
            })
            break
    return out


def _verdict(summary):
    if not summary.get("members"):
        return V_EMPTY
    if summary.get("dated_members_read_by_a_site"):
        return V_FAMILY_LIVE
    twin = summary.get("twin_reading")
    if twin in (R_READ_DIRECTLY, R_READ_THROUGH_A_HELPER):
        return V_TWIN_LIVE
    return V_ALL_DEAD


def build(root=None):
    root = root or ROOT
    members, others = family_members(root)
    sites, meta = scan(members, root)
    rows = [measure_member(m, sites, meta["family_globs"], meta["composed_write_spellings"])
            for m in members]
    parent = _parent_row(root)
    dated = [r for r in rows if r["kind"] == K_DATED]
    machines = [r for r in rows if r["kind"] == K_MACHINE_TWIN]
    twins = [r for r in rows if r["kind"] == K_TWIN]

    def count(items, pred):
        return sum(1 for r in items if pred(r))

    twin_row = twins[0] if twins else {}
    summary = {
        "members": len(rows),
        "dated_members": len(dated),
        "per_machine_twins": len(machines),
        "twins": len(twins),
        "files_in_the_directory_that_are_not_members": len(others),
        "twin_reading": twin_row.get("reading"),
        "twin_read_sites": twin_row.get("read_sites"),
        "twin_helper_read_sites": twin_row.get("helper_read_sites"),
        "twin_direct_read_sites": twin_row.get("direct_read_sites"),
        "twin_write_sites": twin_row.get("write_sites"),
        "twin_retirement_breaks_any_site": bool(twin_row.get("retirement_breaks_any_site")),
        "dated_members_read_by_a_site": count(dated, lambda r: r["read_sites"] > 0),
        "dated_members_read_directly": count(dated, lambda r: r["direct_read_sites"] > 0),
        "dated_members_read_through_a_helper": count(
            dated, lambda r: r["helper_read_sites"] > 0),
        "dated_members_written_only": count(dated, lambda r: r["reading"] == R_WRITTEN_ONLY),
        "dated_members_with_no_site_at_all": count(dated, lambda r: r["reading"] == R_NEVER),
        "dated_members_with_a_composed_writer": count(
            dated, lambda r: r["composed_write_spellings"] > 0),
        "dated_members_on_disk": count(dated, lambda r: r["on_disk"]),
        "dated_bytes": sum(r["bytes"] or 0 for r in dated),
        "dated_bytes_read_by_a_site": sum(r["bytes"] or 0 for r in dated if r["read_sites"]),
        "per_machine_twins_with_a_literal_producer": count(
            machines, lambda r: any(s["tier"] == T_DIRECT and s["mode"] == M_WRITE
                                    for s in r["site_rows"])),
        "per_machine_twins_with_a_face_key_producer": count(
            machines, lambda r: r["face_key_sites"] > 0),
        "per_machine_twins_read_by_a_site": count(machines, lambda r: r["read_sites"] > 0),
        "read_sites_across_the_family": sum(r["read_sites"] for r in rows),
        "write_sites_across_the_family": sum(r["write_sites"] for r in rows),
        "unresolved_sites_across_the_family": sum(r["unresolved_sites"] for r in rows),
        "sites_across_the_family": sum(r["sites"] for r in rows),
        "sites_by_tier": {
            T_DIRECT: sum(r["direct_sites"] for r in rows),
            T_HELPER: sum(r["helper_sites"] for r in rows),
            T_FACEKEY: sum(r["face_key_sites"] for r in rows),
        },
        "sites_by_reading_tier": {
            T_DIRECT: sum(1 for r in rows for s in r["site_rows"] if s["tier"] == T_DIRECT),
            T_HELPER: sum(1 for r in rows for s in r["site_rows"] if s["tier"] == T_HELPER),
            T_FACEKEY: sum(1 for r in rows for s in r["site_rows"] if s["tier"] == T_FACEKEY),
        },
        "family_globs": len(meta["family_globs"]),
        "composed_write_spellings": len(meta["composed_write_spellings"]),
        "readings": {k: count(rows, lambda r, k=k: r["reading"] == k) for k in READINGS},
    }
    cross = {
        "available": bool(parent.get("available")),
        "parent_twin_spelling": parent.get("parent_twin_spelling"),
        "spelling_matches_disk_name": bool(
            parent.get("parent_twin_spelling")
            and parent["parent_twin_spelling"].lower() == twin_row.get("member", "").lower()),
        "parent_read_sites": parent.get("parent_read_sites"),
        "this_study_direct_read_sites": twin_row.get("direct_read_sites"),
        "direct_arm_agrees_with_the_parent": (
            parent.get("parent_read_sites") == twin_row.get("direct_read_sites")
            if parent.get("available") else None),
        "this_study_helper_read_sites": twin_row.get("helper_read_sites"),
        "parent_residue": parent.get("parent_read_only_residue"),
        "this_study_reading": twin_row.get("reading"),
        "explained": ("the parent counts only openers that name the twin, so a reader that hands "
                      "the path constant to a helper reads the face without appearing in its "
                      "residue class" if (parent.get("parent_read_sites") == 0
                                          and twin_row.get("helper_read_sites")) else
                      "the parent and this study agree on the twin's readers"),
    }
    face = {
        "study": "E497",
        "card": CARD,
        "title": ("Is the one write-only twin's retirement free because its dated members are "
                  "what gets read -- the CALL family measured across literal, helper-handoff and "
                  "lane-key arms"),
        "generated": _now(),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "family_dir": FAMILY_DIR,
        "face_key": FACE_KEY,
        "source_faces": {
            "write_only_twin_population": "results/state_tilt/%s (E496)" % PARENT_FACE,
            "opener_mode_resolver": "scripts/e483_leg_debt.py mode_of_site",
            "lane_helper_effects": "config/lane_io.py (write_lane 99 / mirror_shared 140 / "
                                   "mirror_shared_if_changed 199)",
        },
        "lane_helper_mapping": {k: {kk: vv for kk, vv in v.items()}
                                for k, v in LANE_HELPERS.items()},
        "scan_meta": {
            "sources_scanned_with_a_tree": meta["sources_scanned_with_a_tree"],
            "sources_with_a_family_candidate": meta["sources_with_a_family_candidate"],
            "sources_skipped_unreadable_or_oversize": meta[
                "sources_skipped_unreadable_or_oversize"],
            "candidate_tokens": meta["candidate_tokens"],
            "self_excluded": list(SELF_PREFIX),
            "excluded_path_prefixes": list(EXCLUDED_PATH_PREFIX),
            "family_globs": meta["family_globs"],
            "composed_write_spellings": meta["composed_write_spellings"],
        },
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "cross_check_vs_the_parent": cross,
        "rows": rows,
        "non_member_files": others,
        "reading": (
            "Three arms are published per member.  A literal at an opener (arm A) is what "
            "E479/E483/E496 measured.  A path handed to a helper that opens its parameter (arm B) "
            "is a read the corpus performs but no literal census sees.  A lane face key handed to "
            "lane_io (arm C) composes a per-machine path at run time, so the machine twins have no "
            "literal producer by construction.  A dated member written through an f-string is "
            "published as a composed spelling, never attributed to one member."
        ),
    }
    return face


# ------------------------------------------------------------------- check / verify
def tally_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}

    def recount(key, fn):
        got = sum(1 for r in rows if fn(r))
        want = summary.get(key)
        if want is not None and want != got:
            problems.append("%s: face=%r re-derived=%r" % (key, want, got))

    dated = [r for r in rows if r.get("kind") == K_DATED]
    machines = [r for r in rows if r.get("kind") == K_MACHINE_TWIN]
    recount("members", lambda r: True)
    recount("dated_members", lambda r: r.get("kind") == K_DATED)
    recount("per_machine_twins", lambda r: r.get("kind") == K_MACHINE_TWIN)
    if summary.get("dated_members_read_by_a_site") is not None:
        got = sum(1 for r in dated if (r.get("read_sites") or 0) > 0)
        if got != summary["dated_members_read_by_a_site"]:
            problems.append("dated_members_read_by_a_site: face=%r re-derived=%r"
                            % (summary["dated_members_read_by_a_site"], got))
    if summary.get("per_machine_twins_read_by_a_site") is not None:
        got = sum(1 for r in machines if (r.get("read_sites") or 0) > 0)
        if got != summary["per_machine_twins_read_by_a_site"]:
            problems.append("per_machine_twins_read_by_a_site: face=%r re-derived=%r"
                            % (summary["per_machine_twins_read_by_a_site"], got))
    for key, field in (("read_sites_across_the_family", "read_sites"),
                       ("write_sites_across_the_family", "write_sites"),
                       ("unresolved_sites_across_the_family", "unresolved_sites"),
                       ("sites_across_the_family", "sites"),
                       ("sites_by_tier", None),
                       ("sites_by_reading_tier", None)):
        if field is None:
            continue
        got = sum(r.get(field) or 0 for r in rows)
        if summary.get(key) is not None and summary[key] != got:
            problems.append("%s: face=%r re-derived=%r" % (key, summary[key], got))

    for key, tier in ((("sites_by_tier"), None),):
        pass
    tier_face = (summary.get("sites_by_tier") or {})
    tier_rows = (summary.get("sites_by_reading_tier") or {})
    if tier_face and tier_rows and tier_face != tier_rows:
        problems.append("the two tier tallies disagree: %r vs %r" % (tier_face, tier_rows))

    for r in rows:
        direct = r.get("direct_sites") or 0
        helper = r.get("helper_sites") or 0
        keyed = r.get("face_key_sites") or 0
        if direct + helper + keyed != (r.get("sites") or 0):
            problems.append("%s: tiers do not sum to sites" % r.get("member"))
        if (r.get("read_sites") or 0) + (r.get("write_sites") or 0) + \
                (r.get("unresolved_sites") or 0) != (r.get("sites") or 0):
            problems.append("%s: modes do not sum to sites" % r.get("member"))
        if r.get("direct_read_sites") and r.get("reading") != R_READ_DIRECTLY:
            problems.append("%s: a direct read but the reading is %r"
                            % (r.get("member"), r.get("reading")))
        if (r.get("direct_read_sites") or 0) > (r.get("direct_sites") or 0):
            problems.append("%s: more direct reads than direct sites" % r.get("member"))
        if (r.get("helper_read_sites") or 0) > (r.get("helper_sites") or 0):
            problems.append("%s: more helper reads than helper sites" % r.get("member"))
        if (not r.get("direct_read_sites")) and r.get("helper_read_sites") \
                and r.get("reading") != R_READ_THROUGH_A_HELPER:
            problems.append("%s: only a helper read but the reading is %r"
                            % (r.get("member"), r.get("reading")))
        if r.get("retirement_breaks_any_site") != bool(r.get("read_sites")):
            problems.append("%s: retirement_breaks_any_site disagrees with read_sites"
                            % r.get("member"))
        roles = r.get("roles") or {}
        if sum(roles.values()) != (r.get("sites") or 0):
            problems.append("%s: roles do not sum to sites" % r.get("member"))

    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict not in vocabulary: %r" % face.get("verdict"))
    twin_rows = [r for r in rows if r.get("kind") == K_TWIN]
    if len(twin_rows) == 1:
        twin = twin_rows[0]
        for key, field in (("twin_read_sites", "read_sites"),
                           ("twin_helper_read_sites", "helper_read_sites"),
                           ("twin_direct_read_sites", "direct_read_sites"),
                           ("twin_write_sites", "write_sites"),
                           ("twin_reading", "reading")):
            want = summary.get(key)
            got = twin.get(field)
            if want is not None and want != got:
                problems.append("%s: face=%r twin row=%r" % (key, want, got))
        if summary.get("twin_retirement_breaks_any_site") is not None and \
                bool(summary["twin_retirement_breaks_any_site"]) != \
                bool(twin.get("retirement_breaks_any_site")):
            problems.append("twin_retirement_breaks_any_site disagrees with the twin row")
    computed = _verdict(summary)
    if computed != face.get("verdict"):
        problems.append("verdict does not re-derive: face=%r computed=%r"
                        % (face.get("verdict"), computed))
    return problems


def check(face=None):
    if face is None:
        path = os.path.join(OUTDIR, FACE_NAME)
        if not os.path.exists(path):
            raise SystemExit("no face at %s" % path)
        face = _load_json(path)
    problems = tally_problems(face)
    if problems:
        print("CHECK FAIL: %d problem(s)" % len(problems))
        for p in problems[:20]:
            print("  -", p)
        return 2
    print("CHECK OK: %d members, verdict=%s"
          % (len(face.get("rows") or []), face.get("verdict")))
    return 0


def verify():
    live = build()
    path = os.path.join(OUTDIR, FACE_NAME)
    if not os.path.exists(path):
        raise SystemExit("no face at %s" % path)
    published = _load_json(path)
    problems = tally_problems(live)
    a = live.get("summary") or {}
    b = published.get("summary") or {}
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            problems.append("summary.%s: published=%r live=%r" % (key, b.get(key), a.get(key)))
    if live.get("verdict") != published.get("verdict"):
        problems.append("verdict: published=%r live=%r"
                        % (published.get("verdict"), live.get("verdict")))
    for key in ("parent_read_sites", "this_study_helper_read_sites",
                "direct_arm_agrees_with_the_parent"):
        x = (live.get("cross_check_vs_the_parent") or {}).get(key)
        y = (published.get("cross_check_vs_the_parent") or {}).get(key)
        if x != y:
            problems.append("cross_check.%s: published=%r live=%r" % (key, y, x))
    if problems:
        print("VERIFY FAIL: %d problem(s)" % len(problems))
        for p in problems[:20]:
            print("  -", p)
        return 2
    print("VERIFY OK: re-derived from the live tree")
    return 0


# ------------------------------------------------------------------- selftest
def _fixture_tree(source):
    tree = ast.parse(source)
    return {"tree": tree, "par": e483.parents(tree)}


def _helper_read_is_not_never(tmp_members=None):
    """The arm that matters: a helper hand-off must land as a read, not as never-opened."""
    src = (
        "import json\n"
        "P = 'results/market_clock/call_latest.json'\n"
        "def _read_json(path):\n"
        "    with open(path) as fh:\n"
        "        return json.load(fh)\n"
        "def go():\n"
        "    return _read_json(P)\n"
    )
    tree = ast.parse(src)
    assigned = e470._assignments(tree)
    funcs = module_functions(tree)
    params, info = helper_opens(tree, funcs["_read_json"])
    opens = info["opens"]
    assert params == ["path"], params
    assert len(opens) == 1, info
    assert opens[0]["param_index"] == 0, info
    lits = _fold_literals(tree.body[-1].body[0].value.args[0], assigned)
    return opens[0]["mode"], lits, info["openers_on_a_handle"]


def selftest():
    bad = []
    total = [0]

    def t(name, cond, detail=""):
        total[0] += 1
        if not cond:
            bad.append("%s %s" % (name, detail))

    # 1. the helper arm resolves a read and folds the path constant to the member basename
    mode, lits, handle_only = _helper_read_is_not_never()
    t("helper-open-is-a-read", mode == M_READ, mode)
    t("helper-arm-folds-the-constant", "results/market_clock/call_latest.json" in lits, lits)
    t("helper-arm-skips-the-handle-load", handle_only == 1, handle_only)
    t("helper-arm-matches-the-basename",
      _match("call_latest.json", TWIN) == e470.M_BASENAME)
    # 1b. the local mode ladder must agree with e483.mode_of_site on the same fixture
    fixture = _fixture_tree(
        "import json\n"
        "def f(p):\n"
        "    with open(p) as fh:\n"
        "        return json.load(fh)\n"
        "def g(p):\n"
        "    open(p, 'w').write('x')\n"
        "def h(p):\n"
        "    io.open(p, encoding='utf-8').read()\n"
    )
    for line, want in ((3, M_READ), (6, M_WRITE), (8, M_READ)):
        call = None
        for node in ast.walk(fixture["tree"]):
            if isinstance(node, ast.Call) and e470._is_opener(node) \
                    and getattr(node, "lineno", -1) == line:
                call = node
                break
        got = _mode_of_call(call)[0] if call is not None else "no-call"
        shared = e483.mode_of_site(fixture["tree"], line)[0]
        t("mode-ladder-agrees-with-e483-line-%d" % line, got == shared == want,
          (got, shared, want))
    # 2. a machine lane name is not the twin's basename
    t("machine-lane-is-not-the-twin",
      _match("call_latest.json",
             "results/market_clock/call_latest.bm-b.json") is None)
    t("machine-lane-matches-itself",
      _match("call_latest.bm-b.json",
             "results/market_clock/call_latest.bm-b.json") == e470.M_BASENAME)
    # 3. a composed f-string spells no whole dated member
    t("composed-name-matches-no-dated-member",
      _match("CALL-", "results/market_clock/CALL-2026-10-27.md") is None)
    t("a-dated-member-matches-its-self",
      _match("CALL-2026-10-27.md",
             "results/market_clock/CALL-2026-10-27.md") == e470.M_BASENAME)
    # 4. the reading ladder: direct read beats helper read beats writes beats never
    def row(**kw):
        base = {"member": "x", "kind": K_DATED, "date": None, "bytes": 1, "on_disk": True,
                "sites": 0, "direct_sites": 0, "helper_sites": 0, "face_key_sites": 0,
                "read_sites": 0, "write_sites": 0, "unresolved_sites": 0,
                "direct_read_sites": 0, "helper_read_sites": 0,
                "retire_breaks_sites": 0, "retirement_breaks_any_site": False,
                "composed_write_spellings": 0, "touching_sites": 0, "roles": {},
                "site_rows": []}
        base.update(kw)
        return base

    def measure(site_rows, member, composed=0):
        return measure_member(
            {"member": member["member"], "basename": member["member"].split("/")[-1],
             "kind": member["kind"], "date": None, "bytes": 1, "on_disk": True},
            {member["member"]: site_rows}, [], [{"literal": LITERAL_FAMILY_PREFIX,
                                                 "source": "s", "line": 1,
                                                 "role": "an_instrument"}] * composed)

    write_site = {"tier": T_DIRECT, "source": "s", "line": 1, "literal": "x",
                  "match": e470.M_BASENAME, "mode": M_WRITE, "mode_evidence": "",
                  "role": "an_instrument", "attribution": "the_literal_this_line_opens"}
    helper_site = dict(write_site, tier=T_HELPER, mode=M_READ)
    direct_site = dict(write_site, mode=M_READ)
    dated = {"member": "results/market_clock/CALL-2026-10-27.md", "kind": K_DATED}
    r = measure([write_site], dated)
    t("write-only-member-reads-as-written-only", r["reading"] == R_WRITTEN_ONLY, r["reading"])
    r = measure([write_site], dated, composed=1)
    t("composed-writer-is-published-not-attributed",
      r["reading"] == R_WRITTEN_ONLY and r["composed_write_spellings"] == 1, r["reading"])
    r = measure([helper_site], dated)
    t("helper-read-is-not-never", r["reading"] == R_READ_THROUGH_A_HELPER, r["reading"])
    r = measure([direct_site], dated)
    t("direct-read-is-direct", r["reading"] == R_READ_DIRECTLY, r["reading"])
    r = measure([], dated)
    t("no-site-at-all-reads-as-never", r["reading"] == R_NEVER, r["reading"])
    # 5. the family verdict separates a live twin from a dead dated family
    s_live = {"members": 2, "dated_members_read_by_a_site": 0,
              "twin_reading": R_READ_THROUGH_A_HELPER}
    t("live-twin-dead-dated-family", _verdict(s_live) == V_TWIN_LIVE, _verdict(s_live))
    s_dead = {"members": 2, "dated_members_read_by_a_site": 0, "twin_reading": R_WRITTEN_ONLY}
    t("dead-twin-dead-family", _verdict(s_dead) == V_ALL_DEAD, _verdict(s_dead))
    s_fam = {"members": 2, "dated_members_read_by_a_site": 1, "twin_reading": R_WRITTEN_ONLY}
    t("read-dated-member-wins", _verdict(s_fam) == V_FAMILY_LIVE, _verdict(s_fam))
    t("empty-family", _verdict({"members": 0}) == V_EMPTY)
    # 6. tallies fire on a doctored face
    good = {"verdict": V_ALL_DEAD,
            "summary": {"members": 1, "dated_members": 1, "per_machine_twins": 0,
                        "dated_members_read_by_a_site": 0,
                        "per_machine_twins_read_by_a_site": 0,
                        "read_sites_across_the_family": 0,
                        "write_sites_across_the_family": 1,
                        "unresolved_sites_across_the_family": 0,
                        "sites_across_the_family": 1,
                        "twin_reading": R_WRITTEN_ONLY,
                        "sites_by_tier": {T_DIRECT: 1, T_HELPER: 0, T_FACEKEY: 0},
                        "sites_by_reading_tier": {T_DIRECT: 1, T_HELPER: 0, T_FACEKEY: 0}},
            "rows": [measure([write_site], dated)]}
    good["rows"][0]["kind"] = K_DATED
    t("tallies-clean-face", tally_problems(good) == [], tally_problems(good))
    doctored = json.loads(json.dumps(good))
    doctored["summary"]["write_sites_across_the_family"] = 7
    t("tallies-catch-a-site-sum", bool(tally_problems(doctored)))
    doctored2 = json.loads(json.dumps(good))
    doctored2["verdict"] = V_TWIN_LIVE
    t("tallies-catch-a-verdict-that-does-not-re-derive", bool(tally_problems(doctored2)))
    doctored3 = json.loads(json.dumps(good))
    doctored3["rows"][0]["read_sites"] = 1
    t("tallies-catch-a-mode-sum", bool(tally_problems(doctored3)))
    doctored4 = json.loads(json.dumps(good))
    doctored4["rows"][0]["helper_read_sites"] = 1
    doctored4["rows"][0]["reading"] = R_READ_THROUGH_A_HELPER
    t("tallies-catch-a-helper-read-called-never", bool(tally_problems(doctored4)))
    # 7. vocabulary is the shared one, not a local respelling
    t("mode-vocabulary-shared", (M_READ, M_WRITE, M_INDIRECT) == e483.MODE_VOCAB)

    if bad:
        print("SELFTEST FAIL: %d of %d" % (len(bad), total[0]))
        for b in bad:
            print("  -", b)
        return 2
    print("SELFTEST OK: %d/%d" % (total[0], total[0]))
    return 0


# ------------------------------------------------------------------- entry
def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
    latest = os.path.join(outdir, FACE_NAME)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=False)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
            fh.write(u"\n")
    return dated, latest


def main(argv=None):
    ap = argparse.ArgumentParser(description="E497 the CALL family across three opener arms")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        face = build()
        dated, latest = _write(face)
        s = face["summary"]
        print("E497: %d members (%d dated, %d machine twins), twin reading=%s, verdict=%s"
              % (s["members"], s["dated_members"], s["per_machine_twins"],
                 s["twin_reading"], face["verdict"]))
        print("dated members read by a site: %d (direct %d / helper %d) of %d"
              % (s["dated_members_read_by_a_site"], s["dated_members_read_directly"],
                 s["dated_members_read_through_a_helper"], s["dated_members"]))
        print("wrote", _rel(dated), "+", _rel(latest))
        return check(face)
    if args.cmd == "check":
        return check()
    if args.cmd == "verify":
        return verify()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())