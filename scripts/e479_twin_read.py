"""E479 -- is the twin an unread vintage family would leave behind read by anyone?

E472 published 97 vintage families under results/ that no study opens (571 files, 28.55 MB) and
E477 priced what a retirement would actually cost: 40 files / 3,190,685 B are exact copies of a
``*_latest.json`` twin, 531 files / 25,362,319 B have no byte-identical partner.  E477 therefore
implies a retention policy ("keep the twin, drop the dated members") -- but every one of the 36
families that carries a latest pointer is part of a family that no study opens, so the twin
inherits the same status unless something actually reads it.  This study asks that question
per twin, with the reader scan of E470 (opener calls, not name hits: E207/E466/E436).

Every twin in this population is spelled ``<FAMILY>_latest.json`` -- 36 distinct basenames, none
of them a plain ``latest.json`` -- so a basename is family-specific but still does not prove the
directory the program opens.  Three evidence tiers are published apart and only two of them count:

  PATH     the opener names the twin path, or a tail of it that ends with the family directory
  NAME     the opener names only the basename, which carries the family name (ADDOS_latest.json)
           -- enough to attribute the read to a family, not enough to prove the path
  GENERIC  the opener names a spelling that carries no family token; counted and published,
           never credited to a family

Residue per twin, most-proving first: a source that writes neither this twin nor its family >
a smoke/runner leg > a one-off round script > the script that writes it > a glob only > never.

Writers are resolved through three published channels because e464's stem map cannot name a
twin whose writer composes ``NAME + '_latest.json'`` at runtime (E473 family):
``literal_write_site`` (a literal reaching a write call spells the twin) >
``composed_latest_write`` (a ``*_latest.json`` write literal plus the family directory) >
``e464_stem`` (the shared stem map) > ``no_write_site_found``.

Run:      python scripts/e479_twin_read.py run
Verify:   python scripts/e479_twin_read.py verify   (re-derives from the live tree)
Check:    python scripts/e479_twin_read.py check    (tallies re-derive from the face)
Selftest: python scripts/e479_twin_read.py selftest
"""

import argparse
import ast
import io
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402
import e464_producer_intent as e464_producer_intent  # noqa: E402
import e468_pointer_reach as e468  # noqa: E402
import e470_target_read as e470  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "twinread_latest.json"
DATED_PREFIX = "TWINREAD"
CARD = ("E479-ARE-THE-LATEST-TWINS-OF-THE-UNREAD-VINTAGE-FAMILIES-READ-BY-ANY-SITE")

PARENT_FACE = "vintageread_latest.json"      # E472: the unread vintage families
BYTES_FACE = "vintageretire_latest.json"     # E477: what a retirement would cost, per family
TWIN_FACE = "vintageclock_latest.json"       # E478: which vintages differ from their twin

# own outputs and their runners are excluded so the census cannot count itself (E180/E207 family)
SELF_PREFIX = ("e479_", "run_e479", "e480_", "e481_")

# ---- evidence tiers ---------------------------------------------------------------------------
E_PATH = "the_opener_names_the_twin_path_or_a_tail_of_it"
E_NAME = "the_opener_names_only_the_basename_which_carries_the_family_name"
EVIDENCE_VOCAB = (E_PATH, E_NAME)
COUNTING_TIERS = (E_PATH, E_NAME)

# ---- residue classes ---------------------------------------------------------------------------
C_STUDY = "opened_by_a_source_that_writes_neither_this_twin_nor_its_family"
C_SMOKE = "opened_only_by_a_smoke_or_runner_leg"
C_ROUND = "opened_only_by_a_one_off_round_script"
C_PRODUCER = "opened_only_by_the_script_that_writes_it"
C_GLOB = "reached_only_through_a_glob_and_no_site_opens_it"
C_NEVER = "never_opened_by_any_site_in_the_corpus"
C_UNREAD = "the_named_twin_is_not_on_disk"
RESIDUE_VOCAB = (C_STUDY, C_SMOKE, C_ROUND, C_PRODUCER, C_GLOB, C_NEVER, C_UNREAD)

# a family whose twin is only ever opened by its own writer, a glob, a round script or nobody
# can still be retired whole: nothing that survives the retirement would break.  A smoke leg is
# NOT in this set -- a leg that reads the face breaks when the face is deleted.
RETIRABLE_WHOLE = (C_NEVER, C_PRODUCER, C_GLOB, C_ROUND)

# e470's residue vocabulary, re-spelled for this population (its R_OTHER names a *pointing face*;
# here the thing that is or is not written is a family directory)
RESIDUE_MAP = {
    e470.R_OTHER: C_STUDY,
    e470.R_SMOKE: C_SMOKE,
    e470.R_ROUND: C_ROUND,
    e470.R_PRODUCER: C_PRODUCER,
    e470.R_GLOB: C_GLOB,
    e470.R_NEVER: C_NEVER,
}

# ---- verdicts ----------------------------------------------------------------------------------
V_EMPTY = "no_unread_vintage_family_carries_a_latest_twin"
V_STUDY = "some_twins_are_opened_by_a_source_that_writes_neither_them_nor_their_family"
V_LEG_ONLY = "every_twin_that_is_opened_at_all_is_opened_only_by_a_smoke_leg_or_a_round_script"
V_NO_CONSUMER = "no_twin_is_opened_by_a_source_that_does_not_write_it"
VERDICT_VOCAB = (V_EMPTY, V_STUDY, V_LEG_ONLY, V_NO_CONSUMER)

MAX_READ_BYTES = 2 * 1024 * 1024


def _norm(text):
    return str(text or "").replace("\\", "/").strip()


_TEXT_CACHE = {}
_WRITE_CACHE = {}
_CONST_CACHE = {}


def _tree_of(root, rel):
    key = os.path.normcase(os.path.abspath(os.path.join(root, rel)))
    if key not in _CONST_CACHE:
        try:
            _CONST_CACHE[key] = ast.parse(_source_text(os.path.join(root, rel)))
        except SyntaxError:
            _CONST_CACHE[key] = None
    return _CONST_CACHE[key]


def _module_constant_values(root, rel):
    """Module-level string constants: the spelling writers usually keep their face name in."""
    tree = _tree_of(root, rel)
    if tree is None:
        return []
    try:
        return list(e464_producer_intent.module_constants(tree).values())
    except Exception:
        return []


def _expr_lits(node, assigned):
    """String literals in an expression plus the literals of the names it mentions."""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.add(n.value)
        elif isinstance(n, ast.Name) and n.id in assigned:
            out.update(assigned[n.id])
    return out


def _write_literals(tree):
    """Every literal that reaches a write call: open(mode=w/a/x/+), write_text/bytes, dump.

    e464's stem channel (e468.producer_map) cannot name most of these twins: writers compose
    ``NAME + '_latest.json'`` at runtime, so the stem the map keys on never appears as a literal
    (E473 family).  This rule reads the write call directly and publishes the channel it found.
    """
    assigned = e470._assignments(tree)
    out = set()

    def is_write_mode(call):
        mode = ""
        if len(call.args) > 1 and isinstance(call.args[1], ast.Constant) \
                and isinstance(call.args[1].value, str):
            mode = call.args[1].value
        for kw in call.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant) \
                    and isinstance(kw.value.value, str):
                mode = kw.value.value
        return bool(mode) and any(c in mode for c in "wax+")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            fname = f.attr if isinstance(f, ast.Attribute) else (
                f.id if isinstance(f, ast.Name) else "")
            if fname in ("write_text", "write_bytes") and isinstance(f, ast.Attribute):
                out.update(_expr_lits(f.value, assigned))
            elif fname == "open" and node.args and is_write_mode(node):
                out.update(_expr_lits(node.args[0], assigned))
            elif fname in ("to_csv", "to_json", "savefig", "dump", "savetxt"):
                for a in node.args:
                    out.update(_expr_lits(a, assigned))
        elif isinstance(node, ast.With):
            for item in node.items:
                call = item.context_expr
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) \
                        and call.func.id == "open" and call.args and is_write_mode(call):
                    out.update(_expr_lits(call.args[0], assigned))
    return out


def _write_lits_of(root, rel):
    key = os.path.normcase(os.path.abspath(os.path.join(root, rel)))
    if key not in _WRITE_CACHE:
        try:
            tree = ast.parse(_source_text(os.path.join(root, rel)))
            _WRITE_CACHE[key] = _write_literals(tree)
        except SyntaxError:
            _WRITE_CACHE[key] = set()
    return _WRITE_CACHE[key]


def _source_text(path):
    """Read a source once per process: the family join reads the same writers 36 times."""
    key = os.path.normcase(os.path.abspath(path))
    if key not in _TEXT_CACHE:
        _TEXT_CACHE[key] = e451.read_text(path)
    return _TEXT_CACHE[key]


def _is_self(rel):
    return os.path.basename(rel).startswith(SELF_PREFIX)


# ------------------------------------------------------------------ population


def population(root=None):
    """The 36 families E472 published that carry a latest pointer, one row per twin path."""
    root = root or ROOT
    face = json.load(io.open(os.path.join(root, "results", "state_tilt", PARENT_FACE),
                             "r", encoding="utf-8"))
    by_twin = {}
    families_without_a_twin = []
    for row in face.get("rows") or []:
        twin = _norm(row.get("latest"))
        if not twin:
            families_without_a_twin.append("%s/%s" % (row.get("dir"), row.get("family")))
            continue
        slot = by_twin.setdefault(twin, {
            "twin": twin,
            "basename": os.path.basename(twin),
            "family_dir": os.path.dirname(twin),
            "families": [],
            "members": 0,
            "bytes": 0,
            "first_date": row.get("first_date"),
            "last_date": row.get("last_date"),
        })
        slot["families"].append("%s/%s" % (row.get("dir"), row.get("family")))
        slot.setdefault("family_tokens", []).append(str(row.get("family") or ""))
        slot["members"] += len(row.get("members") or [])
        slot["bytes"] += int(row.get("bytes") or 0)
    pop = sorted(by_twin.values(), key=lambda r: r["twin"])
    return pop, {"source_face": PARENT_FACE,
                 "source_face_verdict": face.get("verdict"),
                 "source_face_cutoff": face.get("evidence_cutoff"),
                 "families_total": len(face.get("rows") or []),
                 "families_without_a_latest_pointer": len(families_without_a_twin)}


def producer_sources(twin, family_dir, root=None, sources=None, pm=None, family_tokens=None):
    """Sources that write this twin, by three published channels.

    Channel A (literal_write_site): a literal that reaches a write call spells the twin -- path
    level, or basename level when the same source names the family directory.
    Channel B (composed_latest_write): the source writes a literal ending in ``_latest.json`` and
    names this family directory -- the runtime-composed writers e464's stem map cannot see
    (E473 family).
    Channel C (e464_stem): the stem map from e468.producer_map names this family -- kept as the
    third channel because it is the only one that can prove a writer with no directory literal.

    A row publishes which channel named it; a row with none of them says so rather than being
    silently treated as "no producer", which is what turned the first build's every cross-read
    into a 'study' (the count is only meaningful beside its producer evidence).
    """
    root = root or ROOT
    sources = sources if sources is not None else e468._walk_py(root)

    hits = {"literal_write_site": [], "module_constant_write": [],
            "composed_latest_write": [], "e464_stem": []}
    twin_base = os.path.basename(twin).lower()
    for rel in sources:
        if _is_self(rel) or e470._is_smoke(rel):
            # a smoke leg writes fixtures in temp dirs and names families to do it; it is a
            # consumer of the face, never its producer
            continue
        low = _source_text(os.path.join(root, rel)).lower()
        if twin_base not in low and "_latest.json" not in low:
            continue
        lits = _write_lits_of(root, rel)
        if not lits:
            continue
        if any(match_kind(l, twin) is not None for l in lits):
            hits["literal_write_site"].append(rel)
            continue
        if any(os.path.basename(_norm(v)).lower() == twin_base
               for v in _module_constant_values(root, rel)):
            hits["module_constant_write"].append(rel)
            continue
        if "_latest.json" in low and _names_a_family_token(root, rel, family_tokens):
            hits["composed_latest_write"].append(rel)
    for rel in ((pm or {}).get(e464_face_stem(twin)) or []):
        if not _is_self(rel):
            hits["e464_stem"].append(rel)
    for k in hits:
        hits[k] = sorted(set(hits[k]))
    producers = sorted({r for v in hits.values() for r in v})
    if hits["literal_write_site"]:
        evidence = "literal_write_site"
    elif hits["module_constant_write"]:
        evidence = "module_constant_write"
    elif hits["composed_latest_write"]:
        evidence = "composed_latest_write"
    elif hits["e464_stem"]:
        evidence = "e464_stem"
    else:
        evidence = "no_write_site_found"
    return producers, evidence, hits


def e464_face_stem(path):
    try:
        return e464_producer_intent.face_stem(path)
    except Exception:
        return ""


# ------------------------------------------------------------------ scan


def match_kind(literal, target):
    """How a literal spells the twin.  A TAIL must carry the family directory.

    e470.match_kind treats any literal ending in ``/basename`` as a tail, which is right when the
    targets have distinct basenames.  Here all 36 twins are spelled ``latest.json``, so that rule
    would let famD's path 'tail-match' famA's twin: the family directory has to be part of the
    evidence or the tier is meaningless (this is E366's one-address-form law at the matcher).
    """
    lit = _norm(literal).lower()
    tgt = _norm(target).lower()
    if not lit:
        return None
    if lit == tgt:
        return e470.M_EXACT
    if lit.endswith("/" + tgt):
        return e470.M_TAIL
    if lit == os.path.basename(tgt):
        return e470.M_BASENAME
    return None


def family_specific(rec):
    """Does the twin's own file name carry the family's name?

    ``results/state_tilt/ADDOS_latest.json`` does (ADDOS), ``.../latest.json`` does not.  This is
    what separates a family-specific basename -- medium evidence, the directory is not proven --
    from a shared spelling that cannot be attributed to any family at all.
    """
    base = os.path.basename(rec["twin"]).lower()
    for tok in rec.get("family_tokens") or []:
        tok = str(tok).strip().lower()
        if len(tok) >= 3 and tok in base:
            return True
    return False


def _names_a_family_token(root, rel, family_tokens):
    """Does this source carry the family's own name as a literal anywhere?

    A writer that composes ``OUT_STEM + '_latest.json'`` names the family in its constant
    (e303's ``OUT_STEM = 'BASISRECOVERY'``).  Requiring the family token, and not merely "the
    directory is mentioned", is what stops a study that writes its own face in the same
    directory from being read as the producer of every twin beside it (E236 was exactly that).
    """
    body = _norm(_source_text(os.path.join(root, rel))).lower()
    consts = [str(v).lower() for v in _module_constant_values(root, rel)]
    toks = [str(t).lower() for t in family_tokens or [] if len(str(t)) >= 3]
    if not toks:
        return False
    return any(tok in c for c in consts for tok in toks)


def scan(pop, root=None):
    """Openers/globs per twin, self-excluded, with the three evidence tiers resolved."""
    root = root or ROOT
    targets = {}
    for rec in pop:
        targets.setdefault(rec["basename"].lower(), []).append(rec["twin"])
    found = {rec["twin"]: {"openers": [], "globs": []} for rec in pop}
    # opener sites naming a *_latest.json that belongs to NO family in this population: they
    # prove the scan is not blind, and they are never credited to a family (E444's rule --
    # a zero has to say whether nothing was found or nothing could be looked at)
    unmatched = []
    scanned = 0
    for rel in e468._walk_py(root):
        if _is_self(rel):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except OSError:
            continue
        low = text.lower()
        if not any(b in low for b in targets) and "_latest.json" not in low:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        scanned += 1
        assigned = e470._assignments(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if e470._is_opener(node):
                for lit in e470._evidence(node, assigned):
                    base = os.path.basename(_norm(lit)).lower()
                    cands = targets.get(base) or []
                    if not cands:
                        if base.endswith("_latest.json"):
                            unmatched.append({"source": rel,
                                              "line": getattr(node, "lineno", 0),
                                              "literal": lit})
                        continue
                    for twin in cands:
                        kind = match_kind(lit, twin)
                        if kind is None:
                            continue
                        found[twin]["openers"].append({
                            "source": rel, "line": getattr(node, "lineno", 0),
                            "literal": lit, "match": kind})
                        if kind != e470.M_BASENAME:
                            # an exact/tail literal names one twin and the search is over; a
                            # basename literal names the shared spelling, so it stays attached
                            # to every candidate until the family-literal test can rule
                            break
            elif e470._is_glob(node):
                for lit in e470._evidence(node, assigned):
                    pat = _norm(lit)
                    if not any(ch in pat for ch in "*?["):
                        continue
                    if not e470.literal_segments(pat):
                        continue
                    for twin in found:
                        score = e470.glob_score(twin, pat)
                        if score is None:
                            continue
                        found[twin]["globs"].append({
                            "source": rel, "line": getattr(node, "lineno", 0),
                            "pattern": lit, "literal_segments": score})
    sites = {}
    for twin in found:
        clean = {}
        for key in ("openers", "globs"):
            seen, uniq = set(), []
            for s in found[twin][key]:
                sig = (s["source"], s["line"], s.get("literal") or s.get("pattern"))
                if sig in seen or _is_self(s["source"]):
                    continue
                seen.add(sig)
                uniq.append(s)
            uniq.sort(key=lambda s: (s["source"], s["line"]))
            clean[key] = uniq
        sites[twin] = clean
    meta = {"sources_scanned_with_a_candidate": scanned,
            "distinct_basenames": len({t for twins in targets.values() for t in twins}),
            "unmatched_latest_sites": len(unmatched),
            "unmatched_latest_sources": len({u["source"] for u in unmatched}),
            "unmatched_latest_examples": sorted({u["literal"] for u in unmatched})[:10]}

    specific = {rec["twin"]: family_specific(rec) for rec in pop}
    for twin in sites:
        for s in sites[twin]["openers"]:
            if s["match"] in (e470.M_EXACT, e470.M_TAIL):
                s["evidence"] = E_PATH
            elif specific.get(twin):
                # the file name itself carries the family (ADDOS_latest.json) even though the
                # directory is not proven in this call
                s["evidence"] = E_NAME
            else:
                s["evidence"] = None
    return sites, meta


def classify(pop, sites, root=None):
    root = root or ROOT
    sources = e468._walk_py(root)
    pm = e468.producer_map(root)
    rows = []
    for rec in pop:
        twin = rec["twin"]
        s = sites.get(twin) or {"openers": [], "globs": []}
        producers, producer_evidence, producer_hits = producer_sources(
            twin, rec["family_dir"], root, sources, pm, rec["family_tokens"])
        counting = [o for o in s["openers"] if o["evidence"] in COUNTING_TIERS]
        unattributed = [o for o in s["openers"] if o["evidence"] is None]
        on_disk = os.path.exists(os.path.join(root, twin))
        if not on_disk:
            residue = C_UNREAD
        else:
            residue = class_of(counting, s["globs"], producers)
        rows.append({
            "twin": twin,
            "families": rec["families"],
            "family_dir": rec["family_dir"],
            "members": rec["members"],
            "bytes": rec["bytes"],
            "first_date": rec["first_date"],
            "last_date": rec["last_date"],
            "twin_on_disk": on_disk,
            "residue": residue,
            "opener_sites": len(counting),
            "path_level_sites": sum(1 for o in s["openers"] if o["evidence"] == E_PATH),
            "name_level_sites": sum(1 for o in s["openers"] if o["evidence"] == E_NAME),
            "unattributed_spelling_sites": len(unattributed),
            "glob_sites": len(s["globs"]),
            "producer_evidence": producer_evidence,
            "producers": producers,
            "producer_hits": producer_hits,
            "counting_openers": [{"source": o["source"], "line": o["line"],
                                  "literal": o["literal"], "match": o["match"],
                                  "evidence": o["evidence"]} for o in counting],
            "sites_naming_an_unattributable_spelling": sorted({o["source"] for o in unattributed}),
        })
    return rows


def _verdict(rows, counts):
    if not rows:
        return V_EMPTY
    if counts.get(C_STUDY):
        return V_STUDY
    if counts.get(C_SMOKE) or counts.get(C_ROUND):
        return V_LEG_ONLY
    return V_NO_CONSUMER


def _resolve_residue(counting, globs, producers, on_disk):
    if not on_disk:
        return C_UNREAD
    return class_of(counting, globs, producers)


def class_of(openers, globs, producers):
    """Which family opens the twin, in the order that decides whether it can be retired.

    e470.residue_of falls through to "producer" when a non-producer opener is neither smoke nor a
    round script, which misreads a twin opened by a smoke LEG plus a scratch script as writer-only
    (LEADCOUNTER: smoke_test.py + _tmp_r1275_smoke_leg.py).  The precedence here is explicit:
    an outsider first, then the leg classes, then the writer, then a glob, then nobody.
    """
    outsider = [o for o in openers
                if o["source"] not in producers and not e470._is_smoke(o["source"])
                and not e470._is_round_script(o["source"])]
    if outsider:
        return C_STUDY
    if any(e470._is_smoke(o["source"]) and o["source"] not in producers for o in openers):
        return C_SMOKE
    if any(e470._is_round_script(o["source"]) and o["source"] not in producers
           for o in openers):
        return C_ROUND
    if openers:
        return C_PRODUCER
    if globs:
        return C_GLOB
    return C_NEVER


# ------------------------------------------------------------------ build


def build(root=None, write=True):
    root = root or ROOT
    pop, meta = population(root)
    sites, site_meta = scan(pop, root)
    rows = classify(pop, sites, root)

    counts = {}
    for r in rows:
        counts[r["residue"]] = counts.get(r["residue"], 0) + 1
    counts = {k: counts.get(k, 0) for k in RESIDUE_VOCAB}
    retirable = [r for r in rows if r["residue"] in RETIRABLE_WHOLE]
    keep = [r for r in rows if r["residue"] not in RETIRABLE_WHOLE]
    unattributed_sources = sorted({s for r in rows
                                  for s in r["sites_naming_an_unattributable_spelling"]})

    sibling = None
    sib = os.path.join(root, "results", "state_tilt", BYTES_FACE)
    if os.path.exists(sib):
        try:
            sibling = json.load(io.open(sib, "r", encoding="utf-8"))
        except (OSError, ValueError):
            sibling = None
    twin_face = None
    tpath = os.path.join(root, "results", "state_tilt", TWIN_FACE)
    if os.path.exists(tpath):
        try:
            twin_face = json.load(io.open(tpath, "r", encoding="utf-8"))
        except (OSError, ValueError):
            twin_face = None

    verdict = _verdict(rows, counts)
    summary = {
        "families_with_a_latest_pointer": len(rows),
        "distinct_twin_paths": len({r["twin"] for r in rows}),
        "distinct_twin_basenames": len({os.path.basename(r["twin"]) for r in rows}),
        "twins_present_on_disk": sum(1 for r in rows if r["twin_on_disk"]),
        "twins_missing_on_disk": sum(1 for r in rows if not r["twin_on_disk"]),
        "residue_counts": counts,
        "families_that_can_retire_whole": len(retirable),
        "families_that_need_the_twin_kept_or_a_leg_decision": len(keep),
        "members_behind_the_retirable_families": sum(r["members"] for r in retirable),
        "bytes_behind_the_retirable_families": sum(r["bytes"] for r in retirable),
        "members_behind_the_kept_families": sum(r["members"] for r in keep),
        "bytes_behind_the_kept_families": sum(r["bytes"] for r in keep),
        "twins_with_an_attributable_opener": sum(1 for r in rows if r["opener_sites"]),
        "twins_with_a_path_level_opener": sum(1 for r in rows if r["path_level_sites"]),
        "twins_with_a_name_level_opener_only": sum(
            1 for r in rows if r["name_level_sites"] and not r["path_level_sites"]),
        "sources_naming_a_latest_spelling_outside_this_population": site_meta[
            "unmatched_latest_sources"],
        "opener_sites_naming_a_latest_spelling_outside_this_population": site_meta[
            "unmatched_latest_sites"],
        "examples_of_latest_spellings_outside_this_population": site_meta[
            "unmatched_latest_examples"],
        "producer_evidence_counts": {
            k: sum(1 for r in rows if r["producer_evidence"] == k)
            for k in ("literal_write_site", "module_constant_write", "composed_latest_write",
                      "e464_stem", "no_write_site_found")},
        "twins_with_no_writer_named": sum(
            1 for r in rows if r["producer_evidence"] == "no_write_site_found"),
        "e477_bytes_lost_if_retired": ((sibling or {}).get("summary") or {}).get(
            "bytes_lost_if_retired"),
        "e478_vintages_identical_after_clock_strip": ((twin_face or {}).get("summary") or {}).get(
            "vintage_files_identical_after_clock_strip"),
        "e478_comparable_files": ((twin_face or {}).get("summary") or {}).get(
            "comparable_files",
            ((twin_face or {}).get("summary") or {}).get("vintage_files_differing_after_clock_"
                                                         "strip")),
    }

    face = {
        "card": CARD,
        "study": "E479_are_the_latest_twins_of_the_unread_vintage_families_read_by_any_site",
        "title": "are the *_latest twins of the unread vintage families read by any site?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "population_source": {
            "face": PARENT_FACE,
            "face_evidence_cutoff": meta["source_face_cutoff"],
            "face_verdict": meta["source_face_verdict"],
            "families_total_in_the_face": meta["families_total"],
            "families_without_a_latest_pointer": meta["families_without_a_latest_pointer"],
            "sibling_face": BYTES_FACE,
            "twin_face": TWIN_FACE,
            "sources_scanned_with_a_candidate": site_meta[
                "sources_scanned_with_a_candidate"],
        },
        "evidence_definition": {
            E_PATH: "the opener call carries a literal that is the twin path or ends with the "
                    "family directory and the basename",
            E_NAME: "the opener call carries only the basename, and that basename contains the "
                    "family's own name -- the family is attributed, the directory is not proven",
            "unattributed": "an opener names a spelling that carries no family token; it is "
                            "listed on the row and never counted (no such row exists in this "
                            "population: all 36 twins are family-named)",
        },
        "class_definition": {
            C_STUDY: "the only sources that open it also write neither the twin nor a family face",
            C_SMOKE: "every non-producer opener is a smoke_test.py / run_e* leg",
            C_ROUND: "every non-producer opener is a one-off round script (leading underscore)",
            C_PRODUCER: "every opener is in the set of sources that write a latest.json for this "
                        "family directory",
            C_GLOB: "no opener names it; a glob with a literal segment reaches it",
            C_NEVER: "no opener and no bounded glob reaches it",
            C_UNREAD: "the pointer names a twin that is not on disk: unmeasured, not a negative",
        },
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "method_limits": [
            "all 36 twins are family-named (36 distinct basenames, no plain latest.json), so a "
            "basename-level read is attributable to a family but never proves the directory; "
            "sites that name a spelling with no family token are published and never counted",
            "writers are resolved through three channels and every row publishes which one named "
            "it; a row with no_write_site_found is one whose writer this corpus cannot see, and "
            "any cross-reader of such a twin is only as trustworthy as that gap is small",
            "opener evidence is one AST hop from the call plus the name-resolution e470 applies "
            "(4 rounds); a path composed through an argument or an environment variable is not "
            "seen, so 'never opened' means 'no opener in this corpus spells it'",
            "the scan reads files that mention latest.json only, so a reader that builds the "
            "path from the family directory alone (never the word latest) is invisible",
            "a glob counts only when it carries at least one literal segment (E273's bare '*')",
            "the population is E472's published rows; a family that appeared since is not scanned",
            "reading a twin is not the same as needing its DATED members -- this face prices the "
            "twin only, and E478/E481 own the difference between a twin and its vintages",
        ],
    }
    if write:
        _write(face, root)
    return face


def _write(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(outdir, FACE_NAME)
    body = json.dumps(face, indent=1, ensure_ascii=False)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return dated, latest


# ------------------------------------------------------------------ check / verify / run


def _recompute(face):
    rows = face.get("rows") or []
    counts = {}
    for r in rows:
        counts[r.get("residue")] = counts.get(r.get("residue"), 0) + 1
    counts = {k: counts.get(k, 0) for k in RESIDUE_VOCAB}
    retirable = [r for r in rows if r.get("residue") in RETIRABLE_WHOLE]
    return {
        "residue_counts": counts,
        "families_with_a_latest_pointer": len(rows),
        "families_that_can_retire_whole": len(retirable),
        "families_that_need_the_twin_kept_or_a_leg_decision": len(rows) - len(retirable),
        "members_behind_the_retirable_families": sum(int(r.get("members") or 0)
                                                     for r in retirable),
        "bytes_behind_the_retirable_families": sum(int(r.get("bytes") or 0) for r in retirable),
    }


def row_problems(face):
    """Every published tally must re-derive, and no row may contradict its own class."""
    problems = []
    summary = face.get("summary") or {}
    derived = _recompute(face)
    for key, value in derived.items():
        if summary.get(key) != value:
            problems.append("%s: published %r, re-derives %r" % (key, summary.get(key), value))
    for r in face.get("rows") or []:
        if r.get("residue") not in RESIDUE_VOCAB:
            problems.append("%s: unknown residue %r" % (r.get("twin"), r.get("residue")))
        counting = r.get("counting_openers") or []
        if r.get("opener_sites") != len(counting):
            problems.append("%s: opener_sites %r but %d counting openers"
                            % (r.get("twin"), r.get("opener_sites"), len(counting)))
        if r.get("path_level_sites", 0) + r.get("name_level_sites", 0) != len(counting):
            problems.append("%s: tier counts do not sum to the counting openers"
                            % (r.get("twin"),))
        if r.get("residue") in (C_NEVER, C_GLOB) and counting:
            problems.append("%s: class %r beside %d attributable openers"
                            % (r.get("twin"), r.get("residue"), len(counting)))
        if r.get("residue") == C_UNREAD and r.get("twin_on_disk"):
            problems.append("%s: unread class on a twin that is on disk" % (r.get("twin"),))
        if r.get("residue") not in (C_NEVER, C_GLOB, C_UNREAD) and not counting:
            problems.append("%s: class %r with no attributable opener"
                            % (r.get("twin"), r.get("residue")))
    return problems


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    for p in problems:
        print("  PROBLEM %s" % p)
    print("check: %d problems" % len(problems))
    return 0 if not problems else 1


def verify():
    live = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    rebuilt = build(write=False)
    problems = []
    for key in ("summary", "verdict", "rows"):
        if json.dumps(live.get(key), sort_keys=True) != json.dumps(rebuilt.get(key),
                                                                  sort_keys=True):
            problems.append("%s differs between the published face and a live rebuild" % key)
    for p in problems:
        print("  PROBLEM %s" % p)
    print("verify: %d problems (rows %d)" % (len(problems), len(rebuilt.get("rows") or [])))
    return 0 if not problems else 1


def run():
    face = build(write=True)
    s = face["summary"]
    print("E479 %s" % face["verdict"])
    print("  families %(families_with_a_latest_pointer)d / twin basenames "
          "%(distinct_twin_basenames)d" % s)
    for k in RESIDUE_VOCAB:
        print("  %-70s %d" % (k, s["residue_counts"][k]))
    print("  retirable whole %(families_that_can_retire_whole)d "
          "(%(members_behind_the_retirable_families)d members, "
          "%(bytes_behind_the_retirable_families)d B)" % s)
    print("  attributable openers %(twins_with_an_attributable_opener)d, of which "
          "path-level %(twins_with_a_path_level_opener)d" % s)
    print("  latest spellings outside this population: %(sources_naming_a_latest_spelling_outside_"
          "this_population)d sources / %(opener_sites_naming_a_latest_spelling_outside_this_"
          "population)d sites" % s)
    return 0


# ------------------------------------------------------------------ selftest


def _fixture(tmp):
    """A root where each evidence tier is reachable exactly once and only one way.

    The twins are family-named (FAMA_latest.json), which is what the real population looks like:
    36 distinct basenames, no plain latest.json.
    """
    st = os.path.join(tmp, "results", "state_tilt")
    os.makedirs(st)
    fam = ["results/famA", "results/famB", "results/famC", "results/famD", "results/famE",
           "results/famF"]
    rows = []
    for d in fam:
        os.makedirs(os.path.join(tmp, d))
        name = os.path.basename(d).upper()
        io.open(os.path.join(tmp, d, name + "_latest.json"), "w", encoding="utf-8",
                newline="\n").write('{"verdict": "x"}')
        rows.append({"dir": d, "family": name, "latest": "%s/%s_latest.json" % (d, name),
                     "members": ["%s/%s-20260101.json" % (d, name)], "bytes": 11,
                     "first_date": "2026-01-01", "last_date": "2026-01-01"})
    io.open(os.path.join(st, PARENT_FACE), "w", encoding="utf-8", newline="\n").write(
        json.dumps({"verdict": "fixture", "evidence_cutoff": "2026-01-01", "rows": rows}))

    def src(name, body):
        io.open(os.path.join(tmp, name), "w", encoding="utf-8", newline="\n").write(body)

    # famA: only its own writer opens it (path level) -> C_PRODUCER
    src("src_famA_producer.py", (
        "import json\n"
        "def write():\n"
        "    with open('results/famA/FAMA_latest.json', 'w') as fh:\n"
        "        json.dump({}, fh)\n"
        "def read():\n"
        "    with open('results/famA/FAMA_latest.json') as fh:\n"
        "        return json.load(fh)\n"))
    # famB: an unrelated study opens the exact path -> C_STUDY
    src("src_studyB.py", (
        "import json\n"
        "def read():\n"
        "    with open('results/famB/FAMB_latest.json') as fh:\n"
        "        return json.load(fh)\n"))
    # famC: only a smoke leg opens it -> C_SMOKE
    src("smoke_test.py", (
        "import json\n"
        "def leg():\n"
        "    with open('results/famC/FAMC_latest.json') as fh:\n"
        "        return json.load(fh)\n"))
    # famD: only a one-off round script opens it -> C_ROUND
    src("_r999_probe.py", (
        "import json\n"
        "def read():\n"
        "    with open('results/famD/FAMD_latest.json') as fh:\n"
        "        return json.load(fh)\n"))
    # famE: nobody path-names it; one site opens the family-named basename -> E_NAME -> C_STUDY
    src("src_studyE.py", (
        "import json\n"
        "def read():\n"
        "    with open('FAME_latest.json') as fh:\n"
        "        return json.load(fh)\n"))
    # famF: nobody opens it; one site opens a latest spelling that belongs to no family here
    src("src_generic.py", (
        "import json\n"
        "def peek():\n"
        "    with open('OTHER_latest.json') as fh:\n"
        "        return json.load(fh)\n"))
    return tmp


def selftest():
    failures = []

    def ok(cond, label):
        if not cond:
            failures.append(label)

    tmp = _fixture(tempfile.mkdtemp(prefix="e479_"))
    face = build(root=tmp, write=False)
    by = {r["twin"]: r for r in face["rows"]}
    A, B, C, D, E, F = ("results/fam%s/FAM%s_latest.json" % (k, k) for k in "ABCDEF")
    ok(len(face["rows"]) == 6, "fixture population is six twins")
    ok(by[A]["residue"] == C_PRODUCER, "famA producer-only")
    ok(by[B]["residue"] == C_STUDY, "famB study-opened")
    ok(by[C]["residue"] == C_SMOKE, "famC smoke-only")
    ok(by[D]["residue"] == C_ROUND, "famD round-script-only")
    ok(by[E]["residue"] == C_STUDY, "famE name-level counts")
    ok(by[E]["name_level_sites"] == 1, "famE one name-level site")
    ok(by[E]["path_level_sites"] == 0, "famE no path-level site")
    ok(by[F]["residue"] == C_NEVER, "famF never opened")
    ok(by[F]["opener_sites"] == 0 and by[F]["unattributed_spelling_sites"] == 0,
       "a spelling outside the population is never credited to a family")
    ok(face["summary"]["opener_sites_naming_a_latest_spelling_outside_this_population"] >= 1,
       "latest spellings outside the population are published")
    ok(face["verdict"] == V_STUDY, "fixture verdict is the study class")
    ok(face["summary"]["families_that_can_retire_whole"] == 3,
       "three families retire whole (producer/round/never)")
    ok(row_problems(face) == [], "fixture face has no check problem")

    # a twin named but absent is unmeasured, never a negative
    tmp2 = _fixture(tempfile.mkdtemp(prefix="e479b_"))
    os.remove(os.path.join(tmp2, "results", "famF", "FAMF_latest.json"))
    face2 = build(root=tmp2, write=False)
    by2 = {r["twin"]: r for r in face2["rows"]}
    ok(by2[F]["residue"] == C_UNREAD, "missing twin is unread class")
    ok(face2["summary"]["twins_missing_on_disk"] == 1, "missing twin counted")

    # one contradicted tally must be refused
    bad = json.loads(json.dumps(face))
    bad["summary"]["families_that_can_retire_whole"] += 1
    ok(row_problems(bad) != [], "a doctored retirable count is refused")
    bad2 = json.loads(json.dumps(face))
    bad2["rows"][0]["opener_sites"] += 1
    ok(row_problems(bad2) != [], "a doctored opener count is refused")
    bad3 = json.loads(json.dumps(face))
    bad3["rows"][0]["residue"] = C_NEVER
    ok(row_problems(bad3) != [], "a class beside counting openers is refused")
    bad4 = json.loads(json.dumps(face))
    for r in bad4["rows"]:
        if r["residue"] == C_STUDY:
            r["path_level_sites"] = 0
            r["name_level_sites"] = 0
            break
    ok(row_problems(bad4) != [], "a study class with no tier behind it is refused")

    for f in failures:
        print("  FAIL %s" % f)
    print("selftest: %d legs, %d failures" % (16, len(failures)))
    return 0 if not failures else 1


def main(argv):
    ap = argparse.ArgumentParser(description="E479 -- who reads the unread families' latest twins")
    ap.add_argument("mode", nargs="?", default="run",
                    choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv[1:])
    return {"run": run, "check": check, "verify": verify, "selftest": selftest}[args.mode]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))