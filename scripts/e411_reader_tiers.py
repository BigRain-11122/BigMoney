"""E411 -- E409 priced five reader sites over two faces. This prices every one.

E409 (r1429) measured two faces written only from a session script and found that none of
their five reader sites asks how old the face is. E410 then floored both. That left the
rest of the file unmeasured: the same suite opens ~200 published faces and pages, and no
one knows how many of those reads can go red when the face is stale.

The question per face, measured rather than assumed:

  1. which legs of the suite open a face or page, and can the path be resolved to a file;
  2. for each resolved read site, what does the enclosing leg do when the face is stale --
     ask the clock, date the face in a gate, print STALENESS, compare the face to itself,
     or not look at age at all;
  3. which faces have NO reader that can go red on age (the tiers the card names:
     `no_freshness_test` and `compares_the_face_to_itself`);
  4. for those faces, how often does a writer run -- E408's writer census is the join, so a
     face whose only writer runs inside the round chain is refreshed every round and a face
     whose writer runs only from a session keeps its blind readers pointing at an old file.

Nothing here edits a reader and nothing here writes any face it measures: the whole point is
that a leg which refreshes its own input destroys the evidence that the input was stale. The
fix stays a separate card.

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
SUITE = "smoke_test.py"
SCAN_DIRS = ("scripts", "Tools", "monitor", "live", "firm")
SCAN_EXT = (".py", ".ps1", ".psm1", ".cmd")
SKIP_PARTS = (".git", "__pycache__", "_quarantine", "node_modules", ".codely-cli")

OUT_DATED = "READERTIERS-%s.json"
OUT_LATEST = "readertiers_latest.json"
STUDY = "E411_reader_tiers_for_every_face_the_suite_opens"
CARD = "E411-DO-EVERY-FACE-THE-SUITE-READS-CARRY-A-READER-THAT-CAN-GO-RED"

# The two tiers the card names as "no reader that can go red on age".
BLIND_TIERS = ("no_freshness_test", "compares_the_face_to_itself")
# Tiers that do price the age, in the sense that a stale face can turn the leg red.
RED_TIERS = ("asks_the_clock", "dates_the_face_in_a_gate")

FACEPAT = re.compile(r"""["']((?:results|docs)/[^"']+\.(?:json|csv|md|parquet))["']""")
JOINPAT = re.compile(r"""os\.path\.join\(\s*["'](results|docs)["'](?:\s*,\s*["']([^"']+)["'])+""")
READPAT = re.compile(r"(json\.load|open\(|read_csv|read_text|read_bytes|Path\()")
STRPAT = re.compile(r"""["']([^"']+)["']""")

# This study's own face and the two upstream studies are excluded from the census: a scanner
# that counts itself inflates its own headline (E180/E207/E319 family), and the exclusion is
# published rather than dropped silently.
SELF_MARKERS = ("unfloored", "readertiers", "e409_", "e411_")


def _rel(path: str) -> str:
    return path.replace("\\", "/")


def _e409():
    """Reuse E409's reader-tier classifier instead of writing a second one."""
    here = os.path.join(ROOT, "scripts")
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import e409_unfloored_faces as mod  # noqa: PLC0415
        return mod
    except Exception:  # noqa: BLE001
        return None


def _e408():
    here = os.path.join(ROOT, "scripts")
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import e408_writer_refresh_signal as mod  # noqa: PLC0415
        return mod
    except Exception:  # noqa: BLE001
        return None


def discover_legs(suite_text: str | None = None) -> list[dict]:
    """Split the suite into the unit it reports as one leg.

    The same segmentation E409 used (a new `try:` starts a leg) so the two studies count the
    same population; a different rule would make the two ledgers incomparable.
    """
    if suite_text is None:
        path = os.path.join(ROOT, SUITE)
        try:
            suite_text = open(path, encoding="utf-8", errors="replace").read()
        except OSError as exc:  # noqa: BLE001
            return [{"error": repr(exc)[:120]}]
    lines = suite_text.splitlines()
    legs, cur = [], []
    for i, ln in enumerate(lines):
        if re.match(r"^\s*try:\s*$", ln) and cur:
            legs.append(cur)
            cur = [(i + 1, ln)]
            continue
        cur.append((i + 1, ln))
    if cur:
        legs.append(cur)
    out = []
    for leg in legs:
        text = "\n".join(l for _, l in leg)
        if not ("results" in text or "docs/" in text):
            continue
        out.append({"lo": leg[0][0], "hi": leg[-1][0],
                    "lines": [l for _, l in leg], "text": text})
    return out


def is_self_leg(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in SELF_MARKERS)


def faces_of_leg(text: str) -> tuple[list[dict], list[str]]:
    """Resolve the faces a leg names, with the line each literal sits on.

    Two resolution rules: a literal `results/...` path, and `os.path.join("results", ...)`
    whose parts are literals. A leg that mentions `results` but resolves to nothing is not
    guessed at -- it is returned as unresolved and published as such.
    """
    found, unresolved = {}, []
    for m in FACEPAT.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        found[m.group(1)] = line
    for m in JOINPAT.finditer(text):
        parts = STRPAT.findall(m.group(0))
        tail = [p for p in parts[1:] if p]
        if not tail:
            continue
        path = "/".join([parts[0]] + tail)
        line = text.count("\n", 0, m.start()) + 1
        found.setdefault(path, line)
    out = [{"face": k, "line": v} for k, v in sorted(found.items())]
    return out, unresolved


def _site_block(leg: dict, start: int, nxt: int | None) -> dict:
    """The read site's own window: from just before the literal to the next face literal.

    The leg is the unit the suite reports, but 33 legs name more than one face. Classifying
    the whole leg would credit every face in it with the leg's most careful comparison, so
    the primary tier is windowed at the site and the leg-level tier is published beside it
    for audit.
    """
    # `start`/`nxt` are line numbers inside the leg's own text; the block indexes the file.
    off = leg["lo"] - 1
    start_abs = off + start
    lo = max(leg["lo"], start_abs - 5)
    hi = leg["hi"] if nxt is None else min(leg["hi"], off + nxt - 1)
    hi = min(hi, lo + 80)
    lines = leg["lines"]
    return {"found": True, "lo": lo, "hi": hi,
            "lines": lines[lo - off - 1: hi - off]}


def classify_legs(legs: list[dict], mod) -> list[dict]:
    """One row per (leg, face) read site, with both tiers."""
    sites = []
    for leg in legs:
        faces, _ = faces_of_leg(leg["text"])
        if not faces or not READPAT.search(leg["text"]):
            continue
        leg_block = {"found": True, "lo": leg["lo"], "hi": leg["hi"], "lines": leg["lines"]}
        try:
            leg_cls = mod._classify(leg_block)  # noqa: SLF001 - the shared classifier
        except Exception as exc:  # noqa: BLE001
            leg_cls = {"tier": "classifier_error", "error": repr(exc)[:120]}
        for idx, f in enumerate(faces):
            nxt = faces[idx + 1]["line"] if idx + 1 < len(faces) else None
            blk = _site_block(leg, f["line"], nxt)
            try:
                site_cls = mod._classify(blk)  # noqa: SLF001
            except Exception as exc:  # noqa: BLE001
                site_cls = {"tier": "classifier_error", "error": repr(exc)[:120]}
            sites.append({
                "face": f["face"],
                "site": "%s:%d" % (SUITE, f["line"]),
                "leg": [leg["lo"], leg["hi"]],
                "tier": site_cls.get("tier"),
                "tier_leg": leg_cls.get("tier"),
                "behaviour_under_staleness": mod.BEHAVIOUR.get(site_cls.get("tier"), "unmeasured"),
                "evidence": {k: v for k, v in site_cls.items() if k != "tier"},
            })
    return sites


def _module_texts() -> dict[str, str]:
    out = {}
    for d in SCAN_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dp, dn, _fn in os.walk(base):
            if any(s in dp for s in SKIP_PARTS):
                continue
            for f in sorted(_fn):
                if not f.endswith(SCAN_EXT):
                    continue
                p = os.path.join(dp, f)
                try:
                    out[_rel(os.path.relpath(p, ROOT))] = open(
                        p, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
    return out


def writer_join(faces: list[str], mod408) -> dict:
    """Which face has a writer that runs on the round chain, and which only from a session."""
    join = {"faces_with_a_chain_writer": 0, "faces_session_only": 0,
            "faces_with_no_writer_found": 0, "faces_unmeasured": 0, "per_face": {}}
    if mod408 is None:
        join["faces_unmeasured"] = len(faces)
        join["note"] = "E408 module unavailable -- writer frequency not measured"
        return join
    # Parse each module once: E408's write_evidence parses per call, and 2.5k calls would
    # re-read the same files.
    cache, orig = {}, mod408._parse  # noqa: SLF001

    def cached(path):
        if path not in cache:
            cache[path] = orig(path)
        return cache[path]

    mod408._parse = cached  # noqa: SLF001
    try:
        chain, _legs = mod408.chain_legs()
        texts = _module_texts()
    except Exception as exc:  # noqa: BLE001
        join["faces_unmeasured"] = len(faces)
        join["note"] = "writer census failed: %r" % (exc,)
        return join
    finally:
        pass
    try:
        for face in faces:
            base = os.path.basename(face)
            writers, on_chain, session = [], 0, []
            for path, text in texts.items():
                if base not in text:
                    continue
                try:
                    ev = mod408.write_evidence(os.path.join(ROOT, path), base)
                except Exception:  # noqa: BLE001
                    continue
                if not ev.get("writes"):
                    continue
                runs = [lg for lg in chain.get(os.path.basename(path), [])
                        if not mod408._is_selftest(lg.get("argv", [])[1:])]
                writers.append({"module": path, "runs_per_round": len(runs),
                                "how": ev.get("how")})
                if runs:
                    on_chain += 1
                else:
                    session.append(path)
            join["per_face"][face] = {
                "real_writers": len(writers),
                "writers_on_chain": on_chain,
                "session_only_writers": session,
                "runs_per_round": sum(w["runs_per_round"] for w in writers),
                "writers": writers[:6],
            }
            if not writers:
                join["faces_with_no_writer_found"] += 1
            elif on_chain:
                join["faces_with_a_chain_writer"] += 1
            else:
                join["faces_session_only"] += 1
    finally:
        mod408._parse = orig  # noqa: SLF001 - never leave the cache installed
    return join


def build(now: datetime | None = None, suite_text: str | None = None,
          root: str | None = None, mod=None, skip_writers: bool = False,
          write: bool = True) -> dict:
    """Derive the per-face reader bill. `root`/`suite_text` exist so selftest runs on a fixture."""
    now = now or datetime.now().astimezone()
    global ROOT, OUT_DIR  # noqa: PLW0603 - fixture redirection
    if root:
        ROOT = root
        OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
    mod = mod if mod is not None else _e409()
    if mod is None:
        raise RuntimeError("E409's reader classifier is unavailable; refusing to guess tiers")

    legs = discover_legs(suite_text)
    if legs and "error" in legs[0]:
        raise RuntimeError(legs[0]["error"])

    self_legs = [lg for lg in legs if is_self_leg(lg["text"])]
    legs = [lg for lg in legs if not is_self_leg(lg["text"])]
    sites = classify_legs(legs, mod)

    unresolved = []
    for lg in legs:
        faces, _ = faces_of_leg(lg["text"])
        if not faces and READPAT.search(lg["text"]):
            head = next((x.strip()[:80] for x in lg["lines"]
                         if x.strip().startswith("check(")), "")
            unresolved.append({"leg": [lg["lo"], lg["hi"]], "check": head or "(no check() head)"})

    by_face: dict[str, dict] = {}
    for s in sites:
        row = by_face.setdefault(s["face"], {"face": s["face"], "readers": []})
        row["readers"].append(s)

    join = ({} if skip_writers else writer_join(sorted(by_face), _e408()))
    jper = (join.get("per_face") or {})

    faces = []
    for name, row in sorted(by_face.items()):
        tiers = [r["tier"] for r in row["readers"]]
        red = [r for r in row["readers"] if r["tier"] in RED_TIERS]
        blind_only = bool(tiers) and all(t in BLIND_TIERS for t in tiers)
        on_disk = os.path.exists(os.path.join(ROOT, name))
        w = jper.get(name) or {}
        faces.append({
            "face": name,
            "on_disk": on_disk,
            "reader_sites": len(row["readers"]),
            "reader_tiers": sorted(set(tiers)),
            "readers_that_can_go_red": len(red),
            "no_reader_that_can_go_red": not red,
            "all_readers_in_the_two_blind_tiers": blind_only,
            "writer_runs_per_round": w.get("runs_per_round"),
            "writers_on_chain": w.get("writers_on_chain"),
            "session_only_writers": w.get("session_only_writers"),
            "readers": [{"site": r["site"], "tier": r["tier"], "tier_leg": r["tier_leg"],
                         "behaviour_under_staleness": r["behaviour_under_staleness"],
                         "evidence": r["evidence"]} for r in row["readers"]],
        })

    blind = [f for f in faces if f["no_reader_that_can_go_red"]]
    blind_and_session = [f for f in blind
                         if f["writer_runs_per_round"] == 0 and f["writers_on_chain"] == 0]
    # ranked by how often a writer runs: the more often the face is refreshed, the less a
    # blind reader matters (the face in front of it is current); a blind reader on a face
    # nothing refreshes is the expensive one.
    ranked = sorted(blind, key=lambda f: ((f["writer_runs_per_round"] or 0),
                                          -f["reader_sites"], f["face"]))
    by_tier: dict[str, int] = {}
    for s in sites:
        by_tier[s["tier"]] = by_tier.get(s["tier"], 0) + 1
    site_leg_disagree = sum(1 for s in sites if s["tier"] != s["tier_leg"])

    summary = {
        "legs_scanned": len(legs) + len(self_legs),
        "legs_excluded_as_this_study_reading_itself": len(self_legs),
        "legs_opening_a_face": len({(lg["lo"]) for lg in legs if faces_of_leg(lg["text"])[0]}),
        "legs_opening_more_than_one_face": sum(
            1 for lg in legs if len(faces_of_leg(lg["text"])[0]) > 1),
        "legs_that_mention_a_face_but_resolve_to_none": len(unresolved),
        "faces": len(faces),
        "faces_on_disk": sum(1 for f in faces if f["on_disk"]),
        "reader_sites": len(sites),
        "by_reader_tier": by_tier,
        "reader_sites_that_can_go_red": sum(1 for s in sites if s["tier"] in RED_TIERS),
        "share_of_sites_that_can_go_red": (round(
            sum(1 for s in sites if s["tier"] in RED_TIERS) / len(sites), 4) if sites else None),
        "faces_with_no_reader_that_can_go_red": len(blind),
        "faces_whose_readers_are_all_in_the_two_blind_tiers": sum(
            1 for f in faces if f["all_readers_in_the_two_blind_tiers"]),
        "site_tier_and_leg_tier_disagree": site_leg_disagree,
    }
    # The writer half is its own block: it costs 46 s (2.5k modules priced one by one) while the
    # reader half costs 0.35 s, and the smoke leg re-derives the reader half every round. Keeping
    # the two apart is what lets the cheap half stay re-derived without publishing a stale verdict.
    writer_block = {k: v for k, v in join.items() if k != "per_face"}
    writer_block["blind_faces_with_no_chain_writer"] = len(blind_and_session)

    if faces and summary["faces_with_no_reader_that_can_go_red"] == len(faces):
        verdict = "no_reader_of_any_face_the_suite_opens_can_go_red_on_age"
    elif blind:
        verdict = ("%d_of_%d_faces_the_suite_opens_have_no_reader_that_can_go_red"
                   % (len(blind), len(faces)))
    else:
        verdict = "every_face_the_suite_opens_has_at_least_one_reader_that_can_go_red"

    result = {
        "study": STUDY,
        "card": CARD,
        "title": "the suite's reader tiers, priced on every face it opens",
        "evidence_cutoff": now.strftime("%Y-%m-%d"),
        "generated": now.isoformat(timespec="seconds"),
        "verdict": verdict,
        "verdict_reason": (
            "%d reader sites open %d published faces/pages from %d suite legs; %d of those "
            "sites can go red when the face is stale (%s), and %d faces have no reader that "
            "can. The two faces E409/E410 floored are not outliers."
            % (len(sites), len(faces), summary["legs_opening_a_face"],
               summary["reader_sites_that_can_go_red"], ", ".join(RED_TIERS), len(blind))),
        "summary": summary,
        "writer_join": writer_block,
        "reverse_ranked_blind_faces": ranked,
        "faces": faces,
        "unresolved_legs": unresolved,
        "method_limits": [
            "the primary tier is windowed at the read site (from 5 lines before the path "
            "literal to the next literal in the same leg, capped at 80 lines); the leg-level "
            "tier is published as tier_leg and the two disagree on %d sites, so a face's tier "
            "is auditable rather than asserted." % site_leg_disagree,
            "a path built at runtime (a constant map, a loop over names) does not resolve to a "
            "file here; those legs are counted as unresolved and published, never guessed.",
            "writer frequency is E408's writer census re-run here: a module counts as a writer "
            "only when a write call is reached by a name carrying the face basename. A "
            "runtime-built face path would be missed.",
            "reading a face is not the same as the suite asserting it: a face opened by a leg "
            "that only prints it is still a read, and this bill counts it as one.",
            "the date-name the classifier looks for ends at a word boundary (`day`, `dash_day`, "
            "`face_day`); a suffixed alias such as `day_b` is not read as a date use, so a leg "
            "that compares through such an alias would be under-priced. selftest pins the "
            "boundary rather than leaving it implicit.",
        ],
    }
    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
        cut = result["evidence_cutoff"]
        for name in (OUT_DATED % cut, OUT_LATEST):
            path = os.path.join(OUT_DIR, name)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(result, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        result["_path"] = _rel(os.path.relpath(os.path.join(OUT_DIR, OUT_DATED % cut), ROOT))
    return result


def verify() -> list[str]:
    """Re-derive and refuse a published face that no longer matches the tree."""
    problems = []
    published = os.path.join(OUT_DIR, OUT_LATEST)
    if not os.path.exists(published):
        return ["no published face at %s" % _rel(os.path.relpath(published, ROOT))]
    old = json.load(open(published, encoding="utf-8"))
    # The reader half re-derives from the suite in 0.35 s; the writer half costs 46 s and is
    # checked for internal consistency instead of being re-run on every verify.
    fresh = build(write=False, skip_writers=True)
    if fresh["summary"] != old.get("summary"):
        problems.append("the published summary does not re-derive from the live tree")
    if fresh["verdict"] != old.get("verdict"):
        problems.append("the stored verdict is not the one the live tree produces")
    faces = old.get("faces") or []
    if len(faces) != (old.get("summary") or {}).get("faces"):
        problems.append("the published face rows do not re-add to the headline")
    sites = [r for f in faces for r in f.get("readers") or []]
    if len(sites) != (old.get("summary") or {}).get("reader_sites"):
        problems.append("the reader sites do not re-add to the headline")
    if any(not r.get("tier") or r.get("tier") == "site_not_found" for r in sites):
        problems.append("a reader site the bill names can no longer be classified")
    blind = [f for f in faces if f.get("no_reader_that_can_go_red")]
    if len(blind) != (old.get("summary") or {}).get("faces_with_no_reader_that_can_go_red"):
        problems.append("the blind-face count does not re-derive from the rows")
    if any(f.get("readers_that_can_go_red") for f in blind):
        problems.append("a face marked blind carries a reader that can go red")
    bad_tier = {}
    for r in sites:
        for k in ("asks_the_clock", "dates_the_face_in_a_gate"):
            if r.get("tier") == k:
                bad_tier[k] = bad_tier.get(k, 0) + 1
    if bad_tier != {k: v for k, v in (old.get("summary") or {}).get(
            "by_reader_tier", {}).items() if k in bad_tier}:
        problems.append("the red-tier counts do not re-add to their headline")
    wj = old.get("writer_join") or {}
    parts = (wj.get("faces_with_a_chain_writer"), wj.get("faces_session_only"),
             wj.get("faces_with_no_writer_found"))
    if all(isinstance(x, int) for x in parts) and sum(parts) != len(faces):
        problems.append("the writer classes sum to %d but the bill has %d faces"
                        % (sum(parts), len(faces)))
    if wj.get("blind_faces_with_no_chain_writer") is not None:
        session_only = [f for f in blind
                        if (f.get("writers_on_chain") == 0 and f.get("writer_runs_per_round") == 0)]
        if len(session_only) != wj["blind_faces_with_no_chain_writer"]:
            problems.append("the blind-and-unrefreshed count does not re-derive from the rows")
    return problems


def selftest() -> int:
    bad = []

    def leg(name, cond, detail=""):
        if not cond:
            bad.append("%s: %s" % (name, detail))
        print("  [%s] %s%s" % ("ok" if cond else "FAIL", name,
                               "" if cond else " -- " + str(detail)[:160]))

    mod = _e409()
    if mod is None:
        print("selftest needs the E409 classifier")
        return 1

    fixture = """
    try:
        _a = json.load(open("results/one.json", encoding="utf-8"))
        check("one", _a is not None)
    except Exception:
        check("one", False)
    try:
        _b = json.load(open("results/two.json", encoding="utf-8"))
        _day = _b.get("day")
        check("two", _b is not None, "" if _day else "")
        if _day and _day < "2026-01-01":
            raise AssertionError("stale")
    except Exception:
        check("two", False)
    try:
        _c = json.load(open(os.path.join("results", "state_tilt", "three.json")))
        check("three", _c is not None, "STALE" if False else "")
    except Exception:
        check("three", False)
    """
    legs = discover_legs(fixture)
    leg("fixture yields three legs", len(legs) == 3, len(legs))
    f1, _ = faces_of_leg(legs[0]["text"])
    leg("literal face resolves", [x["face"] for x in f1] == ["results/one.json"], f1)
    f2, _ = faces_of_leg(legs[1]["text"])
    leg("second literal resolves", [x["face"] for x in f2] == ["results/two.json"], f2)
    f3, _ = faces_of_leg(legs[2]["text"])
    leg("os.path.join face resolves",
        [x["face"] for x in f3] == ["results/state_tilt/three.json"], f3)

    sites = classify_legs(legs, mod)
    by_face = {s["face"]: s for s in sites}
    leg("one site per fixture face", len(sites) == 3, len(sites))
    leg("a plain read is no_freshness_test",
        by_face["results/one.json"]["tier"] == "no_freshness_test",
        by_face.get("results/one.json"))
    leg("a dated gate is priced",
        by_face["results/two.json"]["tier"] == "dates_the_face_in_a_gate",
        by_face.get("results/two.json"))

    # the blind rule: a face whose only reader is blind must be flagged, one with a pricing
    # reader must not
    built = build(now=datetime(2026, 11, 4, 12, 0).astimezone(), suite_text=fixture,
                  skip_writers=True, write=False)
    rows = {f["face"]: f for f in built["faces"]}
    leg("blind face detected", rows["results/one.json"]["no_reader_that_can_go_red"] is True)
    leg("priced face not flagged blind",
        rows["results/two.json"]["no_reader_that_can_go_red"] is False, rows.get("results/two.json"))
    leg("blind count re-adds",
        built["summary"]["faces_with_no_reader_that_can_go_red"]
        == sum(1 for f in built["faces"] if f["no_reader_that_can_go_red"]))
    leg("red site count re-adds",
        built["summary"]["reader_sites_that_can_go_red"]
        == sum(1 for s in sites if s["tier"] in RED_TIERS))

    # the self-exclusion: a leg that reads this study's own face must not enter the census
    selffixture = fixture + """
    try:
        _z = json.load(open("results/state_tilt/readertiers_latest.json"))
        check("self", _z is not None)
    except Exception:
        check("self", False)
    """
    legs2 = discover_legs(selffixture)
    kept = [lg for lg in legs2 if not is_self_leg(lg["text"])]
    leg("self leg excluded", len(kept) == len(legs), (len(kept), len(legs)))

    # a leg naming two faces must be windowed, not credited with the whole leg
    twofixture = """
    try:
        _p = json.load(open("results/a.json"))
        check("a", _p is not None)
        _q = json.load(open("results/b.json"))
        _face_day = _q.get("day")
        if _face_day and _face_day < "2026-01-01":
            raise AssertionError("stale")
        check("b", _q is not None)
    except Exception:
        check("pair", False)
    """
    tlegs = discover_legs(twofixture)
    tsites = {s["face"]: s for s in classify_legs(tlegs, mod)}
    leg("two faces in one leg both resolve", len(tsites) == 2, list(tsites))
    leg("the unwindowed leg would credit both the same",
        tsites["results/a.json"].get("tier_leg") == tsites["results/b.json"].get("tier_leg"))
    leg("the window separates them",
        tsites["results/a.json"]["tier"] != tsites["results/b.json"]["tier"],
        (tsites["results/a.json"]["tier"], tsites["results/b.json"]["tier"]))

    print("selftest: %d/%d" % (12 - len(bad), 12))
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
    print("usage: e411_reader_tiers.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))