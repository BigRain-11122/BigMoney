"""E472 -- how much of the daily face output is vintages of families no reader opens?

E471 found never-opened pointer targets whose peers exist but are only ever opened by a smoke leg
or a one-off round script: a published vintage family that no production reader consumes.  Those
families are re-written every round (WIDTHLADDER-20261029 .. WIDTHLADDER-20261106 all exist).
This face asks the volume question E471 left open: of the dated files under ``results/``, how many
belong to a family that is re-emitted on many days and yet is never opened by a study that does
not write it?

Population (mechanical, no curation): every file under ``results/`` whose basename carries an
8-digit or ISO date stamp.  The family is the basename with the stamp (and any trailing tags)
removed; a family is a *vintage family* only when at least two distinct dates are on disk --
otherwise "re-emitted" is a claim about one file.

Reader channels, measured on the corpus of ``.py`` sites, per family:

  opens     an opener call (``open`` / ``read_text`` / ``read_csv`` ...) whose evidence literals
            name the family token or the family's ``_latest`` pointer.  A path composed as
            ``"results/state_tilt/" + FAMILY + "-" + cutoff + ".json"`` is exactly this case, and
            E470's basename matcher cannot see it -- that is why this face carries its own matcher.
  names     the token appears in the site's literals but no opener call uses it (a report, a
            measurement, a doc string).
  writes    the site has a write call (``open(..., "w")`` / ``write_text`` / ``json.dump``) and
            names the token -- the producer.

Token matching is case-insensitive and boundary-anchored (``WIDTHLADDER`` matches
``"WIDTHLADDER-"`` and ``"results/state_tilt/widthladder-"`` but not ``WIDTHLADDERS``), so a family
whose name is a prefix of another family's name is not silently merged into it.

Residues per vintage family:

  R_STUDY_OPENS   a study that is not the producer opens it (production reader exists)
  R_STUDY_NAMES   a study names the family but never opens it (measured, reported, not consumed)
  R_LEG_ONLY      only a smoke / runner leg or a one-off round script opens it
  R_NO_CONSUMER   nothing outside the producer names it at all

Scope limits that are published, not hidden: only ``results/`` is the population (``docs/`` dated
vintages such as the daily report are human-facing and are not counted); a producer whose write
call takes its mode from a variable is counted as a consumer unless another site writes it; and a
site that opens the family through an imported constant defined in another module is not resolved
beyond one hop of name assignment.

Run:      python scripts/e472_vintage_read.py run
Verify:   python scripts/e472_vintage_read.py verify   (re-derives from the live tree)
Check:    python scripts/e472_vintage_read.py check    (tallies re-derive from the face)
Selftest: python scripts/e472_vintage_read.py selftest
"""

import argparse  # noqa: F401  (kept for the family's CLI shape)
import ast
import datetime
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (read_text)
import e468_pointer_reach as e468  # noqa: E402  (_walk_py)
import e470_target_read as e470  # noqa: E402  (_assignments / _is_opener / _is_glob / _is_smoke)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "vintageread_latest.json"
DATED_PREFIX = "VINTAGEREAD"
CARD = "E472-HOW-MUCH-OF-THE-DAILY-FACE-OUTPUT-IS-VINTAGES-OF-FAMILIES-NO-READER-OPENS"

SELF_SKIP = tuple(e470.SELF_SKIP) + ("e471_", "e472_", "run_e471", "run_e472")
MAX_READ_BYTES = 4 * 1024 * 1024

POP_DIR = "results"
SKIP_POP_DIRS = ("_quarantine", "__pycache__")
DATE_STAMP = r"(?P<date>\d{8}|\d{4}-\d{2}-\d{2})"
NAME_RE = re.compile(
    r"^(?P<fam>.+?)[-_]" + DATE_STAMP + r"(?P<tail>(?:[-_][A-Za-z0-9]+)*)\.(?P<ext>[A-Za-z0-9]+)$"
)
VINTAGE_EXTS = ("json", "jsonl", "csv", "md", "parquet")
MIN_TOKEN_LEN = 4
WRITE_FUNCS = ("write_text", "write_bytes", "dump", "savetxt", "to_csv", "to_parquet",
               "to_json", "writerow", "writerows", "write")

# ---- residues ------------------------------------------------------------------------------
R_STUDY_OPENS = "a_study_that_is_not_the_producer_opens_it"
R_STUDY_NAMES = "a_study_names_it_but_no_opener_call_uses_the_name"
R_LEG_ONLY = "only_a_smoke_leg_or_a_one_off_round_script_opens_it"
R_NO_CONSUMER = "nothing_outside_the_producer_names_it"
RESIDUES = (R_STUDY_OPENS, R_STUDY_NAMES, R_LEG_ONLY, R_NO_CONSUMER)
UNREAD = (R_STUDY_NAMES, R_LEG_ONLY, R_NO_CONSUMER)

V_EMPTY = "the_tree_publishes_no_family_with_two_vintages"
V_ALL_READ = "every_vintage_family_is_opened_by_a_study_that_does_not_write_it"
V_SOME_UNREAD = "some_vintage_families_are_re_emitted_without_a_study_opening_them"
V_NONE_READ = "no_vintage_family_is_opened_by_a_study_that_does_not_write_it"
VERDICT_VOCAB = (V_EMPTY, V_ALL_READ, V_SOME_UNREAD, V_NONE_READ)


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _now():
    return datetime.datetime.now().astimezone()


def _norm(text):
    return str(text).replace("\\", "/").strip()


# ------------------------------------------------------------------ population


def _parse_name(basename):
    m = NAME_RE.match(basename)
    if not m:
        return None
    ext = m.group("ext").lower()
    if ext not in VINTAGE_EXTS:
        return None
    return {"family": m.group("fam"), "date": m.group("date"), "ext": ext}


def _latest_candidates(rel_dir, family):
    return ["%s_latest.json" % family, "%s-latest.json" % family,
            "%s_latest.csv" % family, "%s_latest.md" % family]


def population(root=None):
    """Every dated file under results/, grouped into families keyed by the undated stem."""
    root = root or ROOT
    by_family = {}
    singles = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, POP_DIR)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_POP_DIRS]
        for name in filenames:
            parsed = _parse_name(name)
            if not parsed:
                continue
            path = os.path.join(dirpath, name)
            rel = _norm(os.path.relpath(path, root))
            scanned += 1
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            key = (os.path.dirname(rel), parsed["family"])
            slot = by_family.setdefault(key, {
                "family": parsed["family"], "dir": os.path.dirname(rel),
                "token": parsed["family"], "members": [], "dates": [], "bytes": 0,
                "latest": None,
            })
            slot["members"].append({"path": rel, "basename": name, "date": parsed["date"],
                                    "ext": parsed["ext"], "bytes": size})
            slot["dates"].append(parsed["date"])
            slot["bytes"] += size
    families = []
    for slot in by_family.values():
        slot["dates"] = sorted(set(slot["dates"]))
        slot["members"].sort(key=lambda m: (m["date"], m["path"]))
        for cand in _latest_candidates(slot["dir"], slot["family"]):
            rel = _norm(os.path.join(slot["dir"], cand)) if slot["dir"] else cand
            if os.path.isfile(os.path.join(root, rel)):
                slot["latest"] = rel
                break
        if len(slot["dates"]) >= 2 and len(slot["token"]) >= MIN_TOKEN_LEN:
            slot["vintages"] = len(slot["members"])
            slot["first_date"] = slot["dates"][0]
            slot["last_date"] = slot["dates"][-1]
            families.append(slot)
        elif len(slot["token"]) >= MIN_TOKEN_LEN:
            singles.append(slot)
    families.sort(key=lambda f: (-f["vintages"], f["family"]))
    meta = {
        "dated_files": scanned,
        "vintage_families": len(families),
        "single_vintage_stems": len(singles),
        "single_vintage_files": sum(len(s["members"]) for s in singles),
        "single_vintage_bytes": sum(s["bytes"] for s in singles),
        "scope": "%s/ (docs/ human-facing vintages are out of scope)" % POP_DIR,
        "families_with_a_latest_pointer": sum(1 for f in families if f["latest"]),
        "min_token_len": MIN_TOKEN_LEN,
    }
    return families, meta


# ------------------------------------------------------------------ token matching


def _token_re(token):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(token) + r"(?![A-Za-z0-9])", re.IGNORECASE)


def names_token(literal, token, rx=None):
    if not literal:
        return False
    rx = rx or _token_re(token)
    return bool(rx.search(_norm(literal)))


def names_latest(literal, family):
    lit = _norm(literal).lower()
    if not names_token(lit, family["token"]):
        return False
    return "latest" in lit


def _has_write(tree):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        if name in WRITE_FUNCS:
            return True
        if name == "open":
            modes = []
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                modes.append(node.args[1].value)
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    modes.append(kw.value.value)
            for mode in modes:
                if isinstance(mode, str) and ("w" in mode or "a" in mode or "x" in mode):
                    return True
    return False


def _site_literals(tree, assigned):
    """Every literal a site carries: constants in place, plus one hop through assigned names."""
    lits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lits.append(node.value)
    for name in list(assigned):
        lits.extend(assigned[name])
    return lits


def _opener_literals(tree, assigned):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and e470._is_opener(node):
            out.extend(e470._evidence(node, assigned))
    return out


def scan_sites(families, root=None):
    """{family_key: {"opens": [...], "latest_opens": [...], "names": [...], "writes": [...]}}"""
    root = root or ROOT
    keys = [(f["dir"], f["family"]) for f in families]
    found = {k: {"opens": [], "latest_opens": [], "names": [], "writes": []} for k in keys}
    tokens = sorted({f["token"].lower() for f in families})
    prefilter = re.compile("|".join(re.escape(t) for t in tokens), re.IGNORECASE) if tokens else None
    scanned = 0
    for rel in e468._walk_py(root):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except (OSError, ValueError):
            continue
        # one cheap pass over the whole file: a site that mentions no family token cannot be a
        # reader of any of them, and the per-family work below is the expensive part
        if prefilter is None or not prefilter.search(text):
            continue
        low = text.lower()
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        scanned += 1
        assigned = e470._assignments(tree)
        all_lits = None
        opener_lits = None
        writes = None
        for fam in families:
            key = (fam["dir"], fam["family"])
            tok = fam["token"]
            if tok.lower() not in low:
                continue
            if all_lits is None:
                all_lits = _site_literals(tree, assigned)
                opener_lits = _opener_literals(tree, assigned)
                writes = _has_write(tree)
            rx = _token_re(tok)
            if not any(names_token(lit, tok, rx) for lit in all_lits):
                continue
            found[key]["names"].append({"source": rel})
            if writes:
                found[key]["writes"].append({"source": rel})
            for lit in opener_lits:
                if not names_token(lit, tok, rx):
                    continue
                if fam["latest"] and names_latest(lit, fam):
                    found[key]["latest_opens"].append({"source": rel, "literal": _norm(lit)})
                else:
                    found[key]["opens"].append({"source": rel, "literal": _norm(lit)})
    for key in found:
        for slot in ("opens", "latest_opens", "names", "writes"):
            seen, uniq = set(), []
            for rec in found[key][slot]:
                sig = (rec["source"], rec.get("literal"))
                if sig in seen:
                    continue
                seen.add(sig)
                uniq.append(rec)
            uniq.sort(key=lambda r: (r["source"], r.get("literal") or ""))
            found[key][slot] = uniq
    meta = {"sources_scanned": scanned, "families_matched_to_at_least_one_site":
            sum(1 for v in found.values() if v["names"])}
    return found, meta


def _kind(rel):
    if e470._is_smoke(rel):
        return "leg"
    if e470._is_round_script(rel):
        return "round"
    return "study"


def residue_of(family, sites):
    """Which residue this family lands in, and who did it."""
    producer = {w["source"] for w in sites.get("writes") or []}
    opener_sites = {o["source"] for o in (sites.get("opens") or [])
                    + (sites.get("latest_opens") or [])}
    name_sites = {n["source"] for n in sites.get("names") or []}
    consumers = opener_sites - producer
    studies = {s for s in consumers if _kind(s) == "study"}
    if studies:
        residue = R_STUDY_OPENS
    else:
        namers = name_sites - producer
        if any(_kind(s) == "study" for s in namers):
            residue = R_STUDY_NAMES
        elif consumers:
            residue = R_LEG_ONLY
        else:
            residue = R_NO_CONSUMER
    return residue, {
        "producers": sorted(producer),
        "consumer_sites": sorted(consumers),
        "study_consumers": sorted(studies),
        "study_namers": sorted({s for s in (name_sites - producer) if _kind(s) == "study"}),
        "leg_consumers": sorted({s for s in consumers if _kind(s) == "leg"}),
        "round_consumers": sorted({s for s in consumers if _kind(s) == "round"}),
        "writer_located": bool(producer),
    }


def verdict_for(summary):
    if not summary.get("vintage_families"):
        return V_EMPTY
    unread = summary.get("families_with_no_study_consumer") or 0
    if unread == 0:
        return V_ALL_READ
    if unread == summary["vintage_families"]:
        return V_NONE_READ
    return V_SOME_UNREAD


# ------------------------------------------------------------------ build


def build(write=True, root=None):
    root = root or ROOT
    families, pop_meta = population(root)
    site_map, site_meta = scan_sites(families, root)
    rows = []
    for fam in families:
        key = (fam["dir"], fam["family"])
        sites = site_map.get(key) or {}
        residue, who = residue_of(fam, sites)
        rows.append({
            "family": fam["family"],
            "dir": fam["dir"],
            "latest": fam["latest"],
            "vintages": fam["vintages"],
            "bytes": fam["bytes"],
            "first_date": fam["first_date"],
            "last_date": fam["last_date"],
            "dates": fam["dates"],
            "members": [m["path"] for m in fam["members"]],
            "residue": residue,
            "writer_located": who["writer_located"],
            "producers": who["producers"],
            "study_consumers": who["study_consumers"],
            "study_namers": who["study_namers"],
            "leg_consumers": who["leg_consumers"],
            "round_consumers": who["round_consumers"],
            "opener_literals": (sites.get("latest_opens") or [])[:4]
                               + (sites.get("opens") or [])[:4],
        })
    by_residue = {r: 0 for r in RESIDUES}
    for row in rows:
        by_residue[row["residue"]] += 1
    unread_rows = [r for r in rows if r["residue"] in UNREAD]
    all_dates = sorted({d for r in rows for d in r["dates"]})
    recent_dates = all_dates[-7:]
    emission = {}
    for date in recent_dates:
        emission[date] = sum(1 for r in rows for d in r["dates"] if d == date)
    emission_unread = {}
    for date in recent_dates:
        emission_unread[date] = sum(1 for r in unread_rows for d in r["dates"] if d == date)
    summary = {
        "card": CARD,
        "vintage_families": len(rows),
        "vintage_files": sum(r["vintages"] for r in rows),
        "vintage_bytes": sum(r["bytes"] for r in rows),
        "families_with_no_study_consumer": len(unread_rows),
        "files_in_unread_families": sum(r["vintages"] for r in unread_rows),
        "bytes_in_unread_families": sum(r["bytes"] for r in unread_rows),
        "unread_byte_share": (round(sum(r["bytes"] for r in unread_rows) / float(sum(r["bytes"] for r in rows)), 4)
                              if rows and sum(r["bytes"] for r in rows) else 0.0),
        "families_with_a_latest_pointer": sum(1 for r in rows if r["latest"]),
        "unread_families_with_a_latest_pointer": sum(1 for r in unread_rows if r["latest"]),
        "families_whose_writer_was_located": sum(1 for r in rows if r["writer_located"]),
        "residue_classes": by_residue,
        "emission_by_date_last_7": emission,
        "emission_of_unread_families_last_7": emission_unread,
        "single_vintage_stems": pop_meta["single_vintage_stems"],
        "single_vintage_files": pop_meta["single_vintage_files"],
    }
    face = {
        "card": CARD,
        "study": "E472_how_much_of_the_daily_face_output_is_vintages_of_families_no_reader_opens",
        "title": "how much of the daily face output is vintages of families no reader opens?",
        "evidence_cutoff": _now().strftime("%Y-%m-%d"),
        "population_source": pop_meta,
        "reader_scan": site_meta,
        "residue_classes": list(RESIDUES),
        "verdict_vocab": list(VERDICT_VOCAB),
        "verdict": verdict_for(summary),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "the population is results/ only; dated vintages under docs/ are human-facing and are "
            "not counted, so the byte share is a share of machine faces",
            "a family needs two distinct dates on disk to be called a vintage family; a single "
            "dated file is counted separately and never scored",
            "the token matcher reads literals plus one hop of name assignment; a family opened "
            "through a constant imported from another module is not resolved and would read as "
            "unopened",
            "a producer whose write mode comes from a variable is not detected as a writer, so its "
            "own opens read as a study consumer (that errs toward 'read', not toward 'dead')",
            "opening is a static claim: a site that composes the family path but runs only behind a "
            "flag is counted as a reader",
        ],
    }
    paths = None
    if write:
        stamp = _now().strftime("%Y-%m-%d")
        dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, stamp))
        latest = os.path.join(OUTDIR, FACE_NAME)
        blob = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        for p in (dated, latest):
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(blob + "\n")
        paths = [_norm(os.path.relpath(dated, root)), _norm(os.path.relpath(latest, root))]
    return face, paths


def _recompute_tallies(face):
    rows = face.get("rows") or []
    by_residue = {r: 0 for r in RESIDUES}
    for row in rows:
        if row.get("residue") in by_residue:
            by_residue[row["residue"]] += 1
    unread_rows = [r for r in rows if r.get("residue") in UNREAD]
    all_dates = sorted({d for r in rows for d in (r.get("dates") or [])})
    recent = all_dates[-7:]
    return {
        "vintage_families": len(rows),
        "vintage_files": sum(r.get("vintages") or 0 for r in rows),
        "vintage_bytes": sum(r.get("bytes") or 0 for r in rows),
        "families_with_no_study_consumer": len(unread_rows),
        "files_in_unread_families": sum(r.get("vintages") or 0 for r in unread_rows),
        "bytes_in_unread_families": sum(r.get("bytes") or 0 for r in unread_rows),
        "residue_classes": by_residue,
        "emission_by_date_last_7": {d: sum(1 for r in rows for x in (r.get("dates") or []) if x == d)
                                    for d in recent},
    }


def row_problems(face):
    problems = []
    rows = face.get("rows") or []
    for row in rows:
        if row.get("residue") not in RESIDUES:
            problems.append("row %s carries an unknown residue %r" % (row.get("family"), row.get("residue")))
        if (row.get("vintages") or 0) < 2:
            problems.append("row %s is scored with %r vintages" % (row.get("family"), row.get("vintages")))
        # A family can emit several vintages on one day (MIDSWEEP-20261020.json and
        # MIDSWEEP-20261020-burnin.json), so the file count is not the date count: the row must
        # carry one member per vintage, no repeated dates, and exactly the dates its members name.
        if (row.get("vintages") or 0) != len(row.get("members") or []):
            problems.append("row %s counts %r vintages over %d members"
                            % (row.get("family"), row.get("vintages"), len(row.get("members") or [])))
        row_dates = row.get("dates") or []
        if len(row_dates) != len(set(row_dates)):
            problems.append("row %s repeats a date" % (row.get("family"),))
        if len(row_dates) > (row.get("vintages") or 0):
            problems.append("row %s lists %d dates for %r vintages"
                            % (row.get("family"), len(row_dates), row.get("vintages")))
        member_dates = set()
        for _member in row.get("members") or []:
            _parsed = _parse_name(os.path.basename(_member))
            if _parsed:
                member_dates.add(_parsed["date"])
        if member_dates != set(row_dates):
            problems.append("row %s dates %r do not match the dates its members name %r"
                            % (row.get("family"), sorted(row_dates), sorted(member_dates)))
        if row.get("residue") == R_STUDY_OPENS and not row.get("study_consumers"):
            problems.append("row %s claims a study consumer and names none" % row.get("family"))
        if row.get("residue") == R_STUDY_NAMES and not row.get("study_namers"):
            problems.append("row %s claims a study namer and names none" % row.get("family"))
        if row.get("residue") == R_NO_CONSUMER:
            consumers = set(row.get("study_consumers") or []) | set(row.get("leg_consumers") or []) \
                | set(row.get("round_consumers") or [])
            if consumers:
                problems.append("row %s is a no-consumer residue but names %d consumer(s)"
                                % (row.get("family"), len(consumers)))
    summary = face.get("summary") or {}
    derived = _recompute_tallies(face)
    for key, val in derived.items():
        if summary.get(key) != val:
            problems.append("summary %s %r != re-derived %r" % (key, summary.get(key), val))
    if face.get("verdict") != verdict_for({"vintage_families": derived["vintage_families"],
                                           "families_with_no_study_consumer":
                                               derived["families_with_no_study_consumer"]}):
        problems.append("verdict does not re-derive from the tallies")
    return problems


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = row_problems(face)
    print(json.dumps({"face": FACE_NAME, "problems": problems, "verdict": face.get("verdict")},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify():
    """Re-derive on the live tree and compare against the published face, shape for shape."""
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    live, _ = build(write=False)
    problems = []
    if published.get("verdict") != live.get("verdict"):
        problems.append("verdict %r != live %r" % (published.get("verdict"), live.get("verdict")))
    pv = (published.get("summary") or {}).get("residue_classes") or {}
    lv = live["summary"]["residue_classes"]
    if pv != lv:
        problems.append("residue classes %r != live %r" % (pv, lv))
    pr = {r["family"]: r["residue"] for r in published.get("rows") or []}
    lr = {r["family"]: r["residue"] for r in live["rows"]}
    if pr != lr:
        diff = [f for f in sorted(set(pr) | set(lr)) if pr.get(f) != lr.get(f)]
        problems.append("rows differ on %d family(ies): %s" % (len(diff), diff[:6]))
    print(json.dumps({"verify": "identical" if not problems else "differs",
                      "problems": problems, "live_summary": live["summary"]},
                     ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest


def _write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _fixture(tmp):
    """Three families: one opened by a study, one named by a study but never opened, one dead.

    Plus a single-vintage stem that must never be scored as a vintage family.
    """
    st = os.path.join(tmp, "results", "state_tilt")
    # READ: two vintages + a latest pointer, opened by a study that does not write it
    _write_text(os.path.join(st, "READ-20260101.json"), '{"v": 1}\n')
    _write_text(os.path.join(st, "READ-20260102.json"), '{"v": 2}\n')
    _write_text(os.path.join(st, "READ_latest.json"), '{"v": 2}\n')
    # NAMED: two vintages, a study mentions the token but no opener uses it
    _write_text(os.path.join(st, "NAMED-20260101.json"), '{"v": 1}\n')
    _write_text(os.path.join(st, "NAMED-20260102.json"), '{"v": 2}\n')
    # DEAD: two vintages, nobody outside the producer mentions them
    _write_text(os.path.join(st, "DEAD-20260101.json"), '{"v": 1}\n')
    _write_text(os.path.join(st, "DEAD-20260102.json"), '{"v": 2}\n')
    # LEAF: two vintages opened only by a smoke leg
    _write_text(os.path.join(st, "LEAF-20260101.json"), '{"v": 1}\n')
    _write_text(os.path.join(st, "LEAF-20260102.json"), '{"v": 2}\n')
    # a single dated stem: scored as a stem, never as a family
    _write_text(os.path.join(st, "ONCEOK-20260101.json"), '{"v": 1}\n')
    # the producer writes all four families
    _write_text(os.path.join(tmp, "scripts", "producer_fixture.py"),
                "import json\n\n\n"
                "def build(day):\n"
                "    for name in ('READ', 'NAMED', 'DEAD', 'LEAF'):\n"
                "        with open('results/state_tilt/%s-' % name + day + '.json', 'w') as fh:\n"
                "            json.dump({}, fh)\n")
    # a study reader: opens READ_latest only
    _write_text(os.path.join(tmp, "scripts", "reader_fixture.py"),
                "import json\n\n\n"
                "def load():\n"
                "    with open('results/state_tilt/READ_latest.json', encoding='utf-8') as fh:\n"
                "        return json.load(fh)\n")
    # a study that merely names NAMED in prose
    _write_text(os.path.join(tmp, "scripts", "naming_fixture.py"),
                "DOC = 'NAMED vintages are re-emitted every round but nobody reads them'\n")
    # the only opener of LEG is a smoke leg
    _write_text(os.path.join(tmp, "scripts", "smoke_test.py"),
                "import json\n\n\n"
                "def check():\n"
                "    with open('results/state_tilt/LEAF-20260101.json', encoding='utf-8') as fh:\n"
                "        return json.load(fh)\n")
    return tmp


def selftest():
    import shutil
    import tempfile
    legs = []

    tmp = tempfile.mkdtemp(prefix="e472_")
    try:
        _fixture(tmp)
        families, meta = population(tmp)
        by = {f["family"]: f for f in families}
        legs.append(("population finds the four two-vintage families",
                     sorted(by) == ["DEAD", "LEAF", "NAMED", "READ"]))
        legs.append(("a single dated stem is not a vintage family",
                     meta["single_vintage_stems"] == 1 and "ONCEOK" not in by))
        legs.append(("a family keeps its dates sorted and unique",
                     by["READ"]["dates"] == ["20260101", "20260102"]))
        legs.append(("the latest pointer is picked up when it exists",
                     by["READ"]["latest"] == "results/state_tilt/READ_latest.json"))

        face, _ = build(write=False, root=tmp)
        rows = {r["family"]: r for r in face["rows"]}
        legs.append(("a study opener makes the family read",
                     rows["READ"]["residue"] == R_STUDY_OPENS))
        legs.append(("the reader is named and the producer is excluded from it",
                     rows["READ"]["study_consumers"] == ["scripts/reader_fixture.py"]
                     and rows["READ"]["producers"] == ["scripts/producer_fixture.py"]))
        legs.append(("a study that only names a family is not a consumer",
                     rows["NAMED"]["residue"] == R_STUDY_NAMES
                     and rows["NAMED"]["study_namers"] == ["scripts/naming_fixture.py"]))
        legs.append(("a family opened only by a smoke leg is a leg-only residue",
                     rows["LEAF"]["residue"] == R_LEG_ONLY))
        legs.append(("a family only the producer mentions has no consumer",
                     rows["DEAD"]["residue"] == R_NO_CONSUMER))
        legs.append(("the verdict says some families are unread, not all",
                     face["verdict"] == V_SOME_UNREAD))
        legs.append(("the unread volume counts only the unread families",
                     face["summary"]["families_with_no_study_consumer"] == 3
                     and face["summary"]["files_in_unread_families"] == 6))
        legs.append(("the emission table counts vintages per date",
                     face["summary"]["emission_by_date_last_7"] == {"20260101": 4, "20260102": 4}))
        legs.append(("the published face is internally consistent", row_problems(face) == []))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["families_with_no_study_consumer"] = 1
        legs.append(("a doctored tally fails the row guard", row_problems(doctored) != []))

        doctored2 = json.loads(json.dumps(face))
        doctored2["rows"][0]["dates"] = ["20260101"]
        legs.append(("a row whose dates do not match its vintages is caught",
                     row_problems(doctored2) != []))

        legs.append(("the token matcher is boundary-anchored",
                     names_token("WIDTHLADDER-20261030.json", "WIDTHLADDER")
                     and not names_token("WIDTHLADDERS", "WIDTHLADDER")))
        legs.append(("the token matcher folds case",
                     names_token("results/state_tilt/widthladder-20261030.json", "WIDTHLADDER")))
        legs.append(("no families yields the empty verdict",
                     verdict_for({"vintage_families": 0, "families_with_no_study_consumer": 0}) == V_EMPTY))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    print("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        face, paths = build(write=True)
        print(json.dumps({"wrote": paths, "summary": face["summary"], "verdict": face["verdict"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))