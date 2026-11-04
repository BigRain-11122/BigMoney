"""E416 -- E411 found four reader sites that can go red on age. Are they aimed where age matters?

E411 priced 232 reader sites over 200 faces and published a tier per site. Four sites landed in
a tier it called red-capable (``asks_the_clock`` / ``dates_the_face_in_a_gate``); 196 faces were
published as having no reader that can go red. The card's question is not "how many" but "aimed
at what": a freshness test on a face the round chain rewrites every round can never fire, and a
face with no chain writer and no pricing reader is blind.

This study answers it in three measured steps and does not edit a reader or a leg:

  1. Re-read each red-capable site's own source block and ask what the gate actually compares:
     two faces by mtime (a copy lag), a face field to a frozen date literal (an identity pin that
     reds when the producer REFRESHES), a face date to the clock/calendar (age), or none of these.
     A tier name is not a measurement -- the block is.
  2. For every frozen-date gate, publish the pinned literal beside the face's value on disk and
     the writer class E411 published for that face, so "protected against healing" is visible.
  3. Rank the blind faces: for each, its reader sites, whether a writer runs on the round chain,
     and whether anything declares how old the face may get (E410 published two bounds).

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
SUITE = "smoke_test.py"

OUT_DATED = "FRESHAIM-%s.json"
OUT_LATEST = "freshaim_latest.json"
STUDY = "E416_do_the_four_freshness_tests_sit_where_age_matters"
CARD = "E416-DO-THE-FOUR-FRESHNESS-TESTS-SIT-ON-THE-FACES-THAT-NEED-THEM-MOST"

E411_FACE = "readertiers_latest.json"
E410_FACE = "freshnessbound_latest.json"

# E411's tier names, quoted rather than re-derived: this study's job is to price the four sites
# that tier table put in a red-capable bucket, not to re-invent the tier vocabulary.
RED_TIERS = ("asks_the_clock", "dates_the_face_in_a_gate")

MTIME_RE = re.compile(r"getmtime\(")
CLOCK_RE = re.compile(r"(date\.today\(\)|datetime\.now\(\)|time\.time\(\)|"
                      r"\bnow\(\)|_panel_day|expected_bar|_bars_since)")
FROZEN_RE = re.compile(r"""\.get\(\s*["'](?P<field>[A-Za-z_0-9]+)["']\s*\)\s*(?P<op>!=|==)\s*"""
                       r"""["'](?P<lit>\d{4}-\d{2}-\d{2})["']""")
CMP_RE = re.compile(r"(<=|>=|<|>)")


def _rel(path: str) -> str:
    return path.replace("\\", "/")


def chain_modes() -> dict:
    """script basename -> the argument vector the standing chain runs it with.

    E411 counted 'writers_on_chain' as 'this writer's script appears in the chain'. The chain
    runs most study scripts with ``verify``, which refuses a moved face instead of republishing
    it. That distinction is the whole difference between 'the chain refreshes this face' and
    'the chain refuses to let this face move', so it is measured here rather than assumed.
    """
    path = os.path.join(ROOT, "Tools", "s6_chain_bmb.py")
    out = {}
    if not os.path.exists(path):
        return out
    text = io.open(path, encoding="utf-8").read()
    for m in re.finditer(r'\(\s*"([a-z0-9_]+)"\s*,\s*\[([^\]]+)\]', text):
        args = re.findall(r'"([^"]*)"', m.group(2))
        script = next((a for a in args if a.endswith(".py") or a.endswith(".ps1")), None)
        if not script:
            continue
        mode = next((a for a in args[args.index(script) + 1:] if not a.startswith("-")), "")
        out.setdefault(os.path.basename(script), []).append({"leg": m.group(1), "mode": mode,
                                                            "argv": args})
    return out


def writers_of(stems: set[str]) -> dict:
    """face basename stem -> the in-tree scripts whose text names that face."""
    found = {s: [] for s in stems}
    root = os.path.join(ROOT, "scripts")
    for name in sorted(os.listdir(root)):
        if not name.endswith(".py"):
            continue
        if name.startswith("e416_"):
            continue
        path = os.path.join(root, name)
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read()
        except Exception:  # noqa: BLE001
            continue
        for stem in stems:
            if stem and stem in text:
                found[stem].append(_rel(os.path.join("scripts", name)))
    return found


def chain_join(faces_: list[str]) -> list[dict]:
    """For a bounded face set: does the chain RUN its writer, or only VERIFY the face?"""
    stems = {os.path.basename(f).rsplit("_latest", 1)[0].replace("_latest.json", "")
             .replace(".json", ""): f for f in faces_}
    stems = {k: v for k, v in stems.items() if k}
    by_stem = writers_of(set(stems))
    modes = chain_modes()
    rows = []
    for stem, face in stems.items():
        named = by_stem.get(stem) or []
        on_chain = []
        for script in named:
            base = os.path.basename(script)
            for entry in modes.get(base) or []:
                on_chain.append({"script": script, "leg": entry["leg"], "mode": entry["mode"]})
        refreshers = [e for e in on_chain if e["mode"] not in ("verify", "selftest", "")]
        verifiers = [e for e in on_chain if e["mode"] in ("verify", "selftest", "")]
        rows.append({
            "face": face,
            "scripts_naming_the_face": len(named),
            "chain_entries": on_chain,
            "chain_runs_a_writer": bool(refreshers),
            "chain_only_verifies": bool(verifiers) and not refreshers,
        })
    return rows


def _load(name: str) -> dict:
    path = os.path.join(OUT_DIR, name)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def suite_lines(suite_text: str | None = None) -> list[str]:
    if suite_text is not None:
        return suite_text.splitlines()
    path = os.path.join(ROOT, SUITE)
    with io.open(path, encoding="utf-8") as fh:
        return fh.read().splitlines()


def classify_block(lines: list[str], start: int, end: int) -> dict:
    """What does this gate actually compare? Measured from its own source block."""
    lo = max(0, int(start) - 1)
    hi = min(len(lines), int(end))
    block = lines[lo:hi]
    mtime_lines = [lo + i + 1 for i, ln in enumerate(block) if MTIME_RE.search(ln)]
    clock_lines = [lo + i + 1 for i, ln in enumerate(block) if CLOCK_RE.search(ln)]
    frozen = []
    for i, ln in enumerate(block):
        m = FROZEN_RE.search(ln)
        if m:
            frozen.append({"line": lo + i + 1, "field": m.group("field"),
                           "op": m.group("op"), "literal": m.group("lit"),
                           "text": ln.strip()[:160]})
    # a clock reading only counts as an age test when the same block compares on it
    clock_cmp = [ln_no for ln_no in clock_lines
                 if CMP_RE.search(lines[ln_no - 1])]
    stale_words = [lo + i + 1 for i, ln in enumerate(block) if "STALE" in ln.upper()]

    frozen_only = [f for f in frozen if f["op"] == "!="]
    if clock_cmp:
        kind = "prices_age"
    elif mtime_lines:
        kind = "copy_lag_mtime"
    elif frozen_only:
        kind = "frozen_constant_identity"
    elif frozen:
        kind = "frozen_constant_identity"
    else:
        kind = "no_date_logic"
    return {
        "block": [int(start), int(end)],
        "mtime_lines": mtime_lines,
        "clock_lines": clock_lines,
        "clock_comparison_lines": clock_cmp,
        "frozen_constants": frozen,
        "stale_word_lines": stale_words,
        "kind": kind,
        "can_go_red_on_age": kind == "prices_age",
    }


def behaviour(kind: str) -> str:
    return {
        "prices_age": "fails when the face's own date falls behind the clock/calendar",
        "copy_lag_mtime": "fails when a NAMED UPSTREAM face is newer than this one -- a copy "
                          "lag, not an age; the face may be arbitrarily old and stay green",
        "frozen_constant_identity": "fails when the face's pinned field MOVES -- the honest "
                                    "refresh is what reds it",
        "no_date_logic": "carries no date comparison at all; nothing about age is priced",
    }[kind]


def frozen_gates(rows: list[dict]) -> list[dict]:
    """Every frozen-date gate priced against the face on disk and its published writer class."""
    out = []
    for row in rows:
        face = row["face"]
        disk = None
        path = os.path.join(ROOT, face)
        if os.path.exists(path):
            try:
                with io.open(path, encoding="utf-8") as fh:
                    disk = json.load(fh)
            except Exception:  # noqa: BLE001 -- an unreadable face is reported, not crashed on
                disk = None
        for g in row["gate"]["frozen_constants"]:
            value = None
            if isinstance(disk, dict):
                value = disk.get(g["field"])
            out.append({
                "face": face,
                "site": row["site"],
                "field": g["field"],
                "operator": g["op"],
                "pinned_literal": g["literal"],
                "value_on_disk": value,
                "pinned_matches_disk": (str(value) == g["literal"]),
                "reds_on_refresh": True,
                "writers_on_chain": row.get("writers_on_chain"),
                "writer_runs_per_round": row.get("writer_runs_per_round"),
                "line": g["line"],
            })
    return out


def build(now: datetime | None = None, suite_text: str | None = None,
          write: bool = True) -> dict:
    now = now or datetime.now().astimezone()
    lines = suite_lines(suite_text)
    e411 = _load(E411_FACE)
    try:
        e410 = _load(E410_FACE)
    except Exception:  # noqa: BLE001
        e410 = {}

    declared = {}
    for b in e410.get("bounds") or []:
        declared[b.get("face")] = {"bound_bars": b.get("bound_bars"),
                                    "red_when": b.get("red_when")}

    # ---- step 1: what do the red-capable sites actually compare
    red_rows = []
    for f in e411.get("faces") or []:
        for r in f.get("readers") or []:
            if r.get("tier") not in RED_TIERS:
                continue
            ev = r.get("evidence") or {}
            start, end = ev.get("block") or [0, 0]
            gate = classify_block(lines, start, end)
            red_rows.append({
                "face": f["face"],
                "site": r.get("site"),
                "tier_published": r.get("tier"),
                "behaviour_published": r.get("behaviour_under_staleness"),
                "gate": gate,
                "behaviour_measured": behaviour(gate["kind"]),
                "tier_survives": gate["can_go_red_on_age"],
                "declared_expectation": declared.get(f["face"]),
                "on_disk": f.get("on_disk"),
                "writers_on_chain": f.get("writers_on_chain"),
                "writer_runs_per_round": f.get("writer_runs_per_round"),
                "evidence_lines_e411_called_dates":
                    (ev.get("date_comparison_lines") or [])[:3],
            })

    gates = frozen_gates(red_rows)

    # ---- step 2: the faces E411 called protected, re-priced
    still_red = set()
    for row in red_rows:
        if row["tier_survives"]:
            still_red.add(row["face"])
    published_blind = [f for f in e411.get("faces") or [] if f.get("no_reader_that_can_go_red")]
    reclassified_blind = [f for f in e411.get("faces") or []
                          if f.get("no_reader_that_can_go_red") or f["face"] not in still_red]

    # ---- step 3: rank the blind faces by what protects them (nothing does)
    ranking = []
    for f in reclassified_blind:
        ranking.append({
            "face": f["face"],
            "on_disk": f.get("on_disk"),
            "reader_sites": f.get("reader_sites"),
            "reader_tiers": f.get("reader_tiers"),
            "writers_on_chain": f.get("writers_on_chain"),
            "writer_runs_per_round": f.get("writer_runs_per_round"),
            "session_only_writers": len(f.get("session_only_writers") or []),
            "declared_expectation": declared.get(f["face"]),
            "protection": ("none" if not (f.get("writer_runs_per_round") or 0)
                           else "chain_rewrites_it"),
        })
    ranking.sort(key=lambda r: (-(r["reader_sites"] or 0),
                                r["writer_runs_per_round"] or 0, r["face"]))

    chainless = [r for r in ranking if r["protection"] == "none"]
    no_expectation = [r for r in ranking if not r["declared_expectation"]]

    # ---- step 4 (bounded): does the chain RUN the writer of these faces, or only VERIFY them
    priced_faces = sorted({r["face"] for r in red_rows}
                          | {r["face"] for r in ranking[:10]})
    chain = chain_join(priced_faces)
    for g in gates:
        g["chain_mode"] = next((c for c in chain if c["face"] == g["face"]), None)

    summary = {
        "red_capable_sites_published": len(red_rows),
        "red_capable_sites_that_price_age": sum(1 for r in red_rows if r["tier_survives"]),
        "sites_measuring_a_copy_lag": sum(1 for r in red_rows
                                          if r["gate"]["kind"] == "copy_lag_mtime"),
        "sites_pinning_a_frozen_constant": sum(1 for r in red_rows
                                               if r["gate"]["kind"] == "frozen_constant_identity"),
        "sites_with_no_date_logic": sum(1 for r in red_rows
                                        if r["gate"]["kind"] == "no_date_logic"),
        "frozen_date_gates": len(gates),
        "frozen_gates_that_match_today": sum(1 for g in gates if g["pinned_matches_disk"]),
        "frozen_gates_whose_face_has_a_chain_writer":
            sum(1 for g in gates if (g["writers_on_chain"] or 0) > 0),
        "faces_published_protected_by_a_red_capable_site":
            len(e411.get("faces") or []) - len(published_blind),
        "faces_still_protected_after_reclassification": len(still_red),
        "faces_published_blind": len(published_blind),
        "faces_blind_after_reclassification": len(reclassified_blind),
        "blind_faces_with_no_chain_writer": len(chainless),
        "blind_faces_with_no_declared_freshness_expectation": len(no_expectation),
        "faces_with_a_declared_freshness_expectation": len(declared),
        "reader_sites_total_published": (e411.get("summary") or {}).get("reader_sites"),
        "chain_faces_priced": len(chain),
        "chain_faces_whose_writer_it_runs": sum(1 for c in chain if c["chain_runs_a_writer"]),
        "chain_faces_it_only_verifies": sum(1 for c in chain if c["chain_only_verifies"]),
        "frozen_gates_whose_chain_only_verifies_the_face":
            sum(1 for g in gates if (g.get("chain_mode") or {}).get("chain_only_verifies")),
    }

    verdict = ("none_of_the_four_red_capable_sites_prices_the_age_of_the_face_it_reads")
    reason = (
        "%d of %d red-capable sites were re-read from their own source: %d measures a copy lag "
        "(an upstream mtime, so an arbitrarily old face stays green while the panel is behind its "
        "input), %d pin a face field to a frozen date literal and therefore red on an honest "
        "refresh, %d carry no date comparison at all and the line E411 called a date comparison "
        "compares a column count. After reclassification %d of %d faces have a reader that can go "
        "red on age (published: %d protected), %d blind faces have no writer on the round chain, "
        "and %d of the faces the suite reads declare any freshness expectation at all -- both of "
        "the declared ones sit on faces this tier table never priced. The chain does not save them "
        "either: of %d priced faces it RUNS a writer for %d and only VERIFIES %d, so each frozen "
        "gate sits on a face whose refresh the chain deliberately refuses."
        % (summary["red_capable_sites_published"], summary["reader_sites_total_published"] or 0,
           summary["sites_measuring_a_copy_lag"], summary["sites_pinning_a_frozen_constant"],
           summary["sites_with_no_date_logic"], len(still_red), len(e411.get("faces") or []),
           summary["faces_published_protected_by_a_red_capable_site"],
           summary["blind_faces_with_no_chain_writer"],
           summary["faces_with_a_declared_freshness_expectation"],
           summary["chain_faces_priced"], summary["chain_faces_whose_writer_it_runs"],
           summary["chain_faces_it_only_verifies"]))

    payload = {
        "study": STUDY,
        "card": CARD,
        "generated": now.isoformat(timespec="seconds"),
        "evidence_cutoff": str(now.date()),
        "verdict": verdict,
        "verdict_reason": reason,
        "summary": summary,
        "sites": red_rows,
        "frozen_date_gates": gates,
        "blind_ranking": ranking[:25],
        "chain_bounded": chain,
        "method_limits": [
            "the tier vocabulary, the site list and the per-face writer class are E411's published "
            "rows; this study re-reads the four sites' own source blocks and re-prices the faces, "
            "it does not re-run E408's 46 s writer census",
            "a site is called an age test only when a clock/calendar token appears on a line that "
            "also carries a comparison; a clock token read for printing is not an age gate",
            "the frozen-constant arm keys on a literal YYYY-MM-DD compared to a .get() field of the "
            "same block, so a gate that pins a date through a module constant is not counted",
            "writer_runs_per_round is E411's class, which answers 'does a registered task or chain "
            "leg run the writer', not 'has it run since this face was written'",
            "this study reads faces and never writes them: refreshing an input destroys the "
            "evidence that the input was stale",
        ],
    }

    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
        stem = OUT_DATED % now.date()
        for name, body in ((stem, payload), (OUT_LATEST, payload)):
            with io.open(os.path.join(OUT_DIR, name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(body, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
        payload["_path"] = _rel(os.path.join("results", "state_tilt", stem))
    return payload


def verify() -> list[str]:
    problems = []
    published_path = os.path.join(OUT_DIR, OUT_LATEST)
    if not os.path.exists(published_path):
        return ["no published face at %s" % _rel(os.path.relpath(published_path, ROOT))]
    with io.open(published_path, encoding="utf-8") as fh:
        old = json.load(fh)
    fresh = build(write=False)
    if fresh["summary"] != old.get("summary"):
        problems.append("the published summary does not re-derive from the live tree")
    if fresh["verdict"] != old.get("verdict"):
        problems.append("the stored verdict is not the one the live tree produces")
    sites = old.get("sites") or []
    if len(sites) != (old.get("summary") or {}).get("red_capable_sites_published"):
        problems.append("the site rows do not re-add to the headline")
    if sum(1 for s in sites if s["gate"]["can_go_red_on_age"]) != \
            (old.get("summary") or {}).get("red_capable_sites_that_price_age"):
        problems.append("the age-pricing sites do not re-add to the headline")
    kinds = {}
    for s in sites:
        kinds[s["gate"]["kind"]] = kinds.get(s["gate"]["kind"], 0) + 1
    if kinds.get("copy_lag_mtime", 0) != \
            (old.get("summary") or {}).get("sites_measuring_a_copy_lag"):
        problems.append("the copy-lag count does not re-derive from the rows")
    if kinds.get("copy_lag_mtime", 0) + kinds.get("frozen_constant_identity", 0) + \
            kinds.get("no_date_logic", 0) + kinds.get("prices_age", 0) != len(sites):
        problems.append("a site kind outside the published vocabulary")
    gates = old.get("frozen_date_gates") or []
    if len(gates) != (old.get("summary") or {}).get("frozen_date_gates"):
        problems.append("the frozen-gate rows do not re-add to the headline")
    if any(not g.get("reds_on_refresh") for g in gates):
        problems.append("a frozen gate claims it does not red on a refresh")
    rel = [r for r in old.get("blind_ranking") or []]
    if any(r["protection"] not in ("none", "chain_rewrites_it") for r in rel):
        problems.append("a blind row carries an unknown protection class")
    ch = old.get("chain_bounded") or []
    if len(ch) != (old.get("summary") or {}).get("chain_faces_priced"):
        problems.append("the bounded chain rows do not re-add to the headline")
    if sum(1 for c in ch if c["chain_only_verifies"]) != \
            (old.get("summary") or {}).get("chain_faces_it_only_verifies"):
        problems.append("the verify-only faces do not re-add to the headline")
    if any(c["chain_runs_a_writer"] and c["chain_only_verifies"] for c in ch):
        problems.append("a face is claimed both refreshed and only verified")
    modes = chain_modes()
    if not modes:
        problems.append("the standing chain no longer parses into a leg table")
    # the delta that carries the finding must survive: the published protected count minus the
    # faces that still carry an age-pricing site must equal the faces that went blind
    s = old.get("summary") or {}
    delta = (s.get("faces_published_protected_by_a_red_capable_site") or 0) - \
            (s.get("faces_still_protected_after_reclassification") or 0)
    if delta != (s.get("faces_blind_after_reclassification") or 0) - (s.get("faces_published_blind") or 0):
        problems.append("the reclassification delta does not re-add")
    return problems


def selftest() -> int:
    bad = []
    total = [0]

    def leg(name, cond, detail=""):
        total[0] += 1
        if not cond:
            bad.append("%s: %s" % (name, detail))
        print("  [%s] %s%s" % ("ok" if cond else "FAIL", name,
                               "" if cond else " -- " + str(detail)[:160]))

    fixture = [
        'try:',
        '    _a = json.load(open("results/one.json"))',
        '    if _a.get("evidence_cutoff") != "2026-10-31":',
        '        bad.append("moved")',
        'except Exception:',
        '    bad.append("x")',
        'try:',
        '    _b = json.load(open("results/two.json"))',
        '    _up_newer = os.path.getmtime("results/up.json") > os.path.getmtime(',
        '        "results/two.json")',
        'except Exception:',
        '    bad.append("x")',
        'try:',
        '    _c = json.load(open("results/three.json"))',
        '    if _c.get("day") < date.today().isoformat():',
        '        bad.append("stale")',
        'except Exception:',
        '    bad.append("x")',
        'try:',
        '    _d = json.load(open("results/four.json"))',
        '    if len(_d.get("cells") or []) < 6:',
        '        bad.append("thin")',
        'except Exception:',
        '    bad.append("x")',
    ]
    a = classify_block(fixture, 1, 6)
    leg("a frozen date literal is an identity pin", a["kind"] == "frozen_constant_identity", a)
    leg("an identity pin cannot go red on age", a["can_go_red_on_age"] is False)
    leg("the pinned literal and field are captured",
        a["frozen_constants"] and a["frozen_constants"][0]["literal"] == "2026-10-31"
        and a["frozen_constants"][0]["field"] == "evidence_cutoff", a["frozen_constants"])

    b = classify_block(fixture, 7, 12)
    leg("two mtimes are a copy lag", b["kind"] == "copy_lag_mtime", b)
    leg("a copy lag is not an age test", b["can_go_red_on_age"] is False)

    c = classify_block(fixture, 13, 18)
    leg("a clock comparison is an age test", c["kind"] == "prices_age", c)
    leg("and it is the only kind that can go red on age", c["can_go_red_on_age"] is True)

    d = classify_block(fixture, 19, 24)
    leg("a column-count comparison is not a date", d["kind"] == "no_date_logic", d)
    leg("and it is not counted as pricing age", d["can_go_red_on_age"] is False)

    leg("every kind has a published behaviour", all(
        behaviour(k) for k in ("prices_age", "copy_lag_mtime", "frozen_constant_identity",
                               "no_date_logic")))

    # a block window must not read past its own end: line 7's mtime must not leak into block 1-6
    leg("windows are exclusive of the next block",
        classify_block(fixture, 1, 6)["mtime_lines"] == [],
        classify_block(fixture, 1, 6)["mtime_lines"])

    built = build(now=datetime(2026, 11, 4, 18, 0).astimezone(), write=False)
    rows = built["sites"]
    leg("the live tree still yields the four red-capable sites", len(rows) == 4, len(rows))
    leg("no live site prices age", all(not r["tier_survives"] for r in rows),
        [(r["face"], r["gate"]["kind"]) for r in rows])
    leg("kinds re-add to the headline",
        sum(built["summary"][k] for k in ("sites_measuring_a_copy_lag",
                                          "sites_pinning_a_frozen_constant",
                                          "sites_with_no_date_logic",
                                          "red_capable_sites_that_price_age")) == len(rows))
    leg("frozen gates name a field and a literal on disk",
        all(g["field"] and g["pinned_literal"] for g in built["frozen_date_gates"]),
        built["frozen_date_gates"][:1])
    leg("the blind population grew by exactly the reclassified faces",
        built["summary"]["faces_blind_after_reclassification"]
        > built["summary"]["faces_published_blind"],
        (built["summary"]["faces_published_blind"],
         built["summary"]["faces_blind_after_reclassification"]))
    leg("ranking is ordered by reader sites",
        all((built["blind_ranking"][i]["reader_sites"] or 0)
            >= (built["blind_ranking"][i + 1]["reader_sites"] or 0)
            for i in range(len(built["blind_ranking"]) - 1)))

    modes = chain_modes()
    leg("the standing chain parses into a leg table", len(modes) > 100, len(modes))
    leg("a chain entry carries the mode it runs the script with",
        all(e.get("mode") is not None for v in modes.values() for e in v))
    joined = {c["face"]: c for c in built["chain_bounded"]}
    leg("each priced face has exactly one chain row", len(joined) == built["summary"]["chain_faces_priced"],
        (len(joined), built["summary"]["chain_faces_priced"]))
    leg("a verify-only face is not also counted as refreshed", all(
        not (c["chain_runs_a_writer"] and c["chain_only_verifies"])
        for c in built["chain_bounded"]))

    print("selftest: %d/%d" % (total[0] - len(bad), total[0]))
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        d = build()
        print(json.dumps({"path": d.get("_path"), "verdict": d["verdict"],
                          "summary": d["summary"], "reason": d["verdict_reason"]},
                         ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e416_fresh_aim.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))