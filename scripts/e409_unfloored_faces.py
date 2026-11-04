"""E409 -- two faces are written only from a session script, and the suite reads them.

E408 (r1426) showed the two surfaces never share a signal: 12 of 14 real writers run on
the standing round chain, 2 run only when a session happens to call them --
`scripts/e321_*.py` writes results/state_tilt/quantityname_latest.json and
`scripts/t35_open_fill_verify.py` writes results/t35_open_fill_verify.json. Both faces are
read by legs of smoke_test.py. So on a round where no session ran them, the leg compares
against a face nobody refreshed.

This asks the question per face, measured rather than assumed:

  1. how old is the face now (git commit time, file mtime, the face's own dated field);
  2. how many rounds have passed since it last changed;
  3. what does each reader do when the face is stale -- fail, or silently pass;
  4. which fix is cheaper: put the writer on the round chain, or make the reader price the
     age it is already able to read (a face that carries its own date can be priced by the
     reader; a face that carries no date can only be fixed at the producer).

The bill is the two-face staleness ledger. Nothing in this script writes either face: the
whole point is that a leg which rewrites its own input to make the read pass destroys the
evidence that it was stale.

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
PANEL = os.path.join(ROOT, "data", "daily", "sh510300.csv")

# The two faces E408 named, with the reader sites measured from smoke_test.py (line
# numbers are advisory: the classifier reads a window around them, and a moved reader
# is reported as "site not found" rather than silently classified).
FACES = [
    {
        "face": "results/t35_open_fill_verify.json",
        "label": "T-35 open-fill verification",
        "writer": "scripts/t35_open_fill_verify.py",
        "writer_surface": "session",
        "date_fields": ["day", "ts"],
        "expected_refresh": "every trading day after the open bar is captured",
        # The suite already ruled that this pair must NOT be hard-gated: requiring equality
        # made a healthy bm-b run red against a bm-a-written dashboard (E185 family).
        "gate_blocked_by": "smoke_test.py:593-597 -- a hard day gate was already litigated "
                           "and removed (E185: an assertion that assumes a deployment layout)",
        "readers": [
            {"file": "smoke_test.py", "line": 589,
             "anchor": '_fv2 = json.load(open("results/t35_open_fill_verify.json"',
             "what": "dashboard/verify counter agreement"},
            {"file": "smoke_test.py", "line": 619,
             "anchor": '_ofv = json.load(open("results/t35_open_fill_verify.json"',
             "what": "evidence tier and per-trader detail shape"},
        ],
    },
    {
        "face": "results/state_tilt/quantityname_latest.json",
        "label": "E321 quantity-name census",
        "writer": "scripts/e321_quantity_named_by_producer.py",
        "writer_surface": "session",
        "date_fields": ["evidence_cutoff"],
        "expected_refresh": "only when the E321 study is re-derived",
        "readers": [
            {"file": "smoke_test.py", "line": 9164,
             "anchor": '_p306 = os.path.join("results", "state_tilt", "quantityname_latest.json")',
             "what": "E306 producer-name leg"},
            {"file": "smoke_test.py", "line": 9257,
             "anchor": '_p301 = os.path.join("results", "state_tilt", "quantityname_latest.json")',
             "what": "E307 refused-population leg"},
            {"file": "smoke_test.py", "line": 9329,
             "anchor": '_p309 = os.path.join("results", "state_tilt", "quantityname_latest.json")',
             "what": "E309 rejected-name leg"},
        ],
    },
]

WINDOW = 40  # lines of reader context; wide enough to hold a whole leg body

# A freshness probe actually asks the filesystem or the clock how old the face is.
PROBE_RE = re.compile(
    r"getmtime|getctime|st_ctime|st_mtime|\.stat\(\)|git\s+log|now\s*\(\s*\)|utcnow|"
    r"timedelta\s*\(", re.I)
# A gate is any expression that can turn the reader red.
GATE_RE = re.compile(r"check\s*\(|_bad\w*\s*\.append|_ok\w*\s*=\s*False|raise\s+\w*Error")
# Printed-but-not-gated staleness: the reader says the word and moves on.
STALE_WORD_RE = re.compile(r"STALE|staleness|stale", re.I)
# A date claim is the face field the reader would have to compare against. The lookbehind
# admits the snake_case carriers (`dash_day`, `face_day`) without also matching `today`.
DATE_USE_RE = re.compile(r"(?<![A-Za-z])day\b|evidence_cutoff|(?<![A-Za-z])ts\b|_at\b|(?<![A-Za-z])date\b")
CMP_RE = re.compile(r"[<>]=?|==|!=")


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def _git_last_commit(path: str) -> dict:
    for args in (["log", "-1", "--format=%H|%cI|%ct", "--", path],):
        try:
            out = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                                 text=True, timeout=60)
        except Exception as exc:  # noqa: BLE001 - reported, never guessed
            return {"sha": None, "ts": None, "epoch": None, "error": repr(exc)[:120]}
        text = (out.stdout or "").strip()
        if out.returncode != 0 or not text:
            return {"sha": None, "ts": None, "epoch": None,
                    "error": (out.stderr or "no output").strip()[:120]}
        sha, iso, epoch = text.split("|")
        return {"sha": sha, "ts": iso, "epoch": int(epoch)}
    return {"sha": None, "ts": None, "epoch": None, "error": "unreachable"}


def _panel_cutoff() -> str:
    """Last complete bar day on the local daily panel: the clock the faces are judged by."""
    try:
        with open(PANEL, encoding="utf-8") as fh:
            rows = [ln.strip() for ln in fh if ln.strip()]
        last = rows[-1].split(",")[0]
        return last[:10] if re.match(r"\d{4}-\d{2}-\d{2}", last) else ""
    except Exception:  # noqa: BLE001
        return ""


def _round_rows() -> list[dict]:
    """Round report rows: | ts | rN | ... -- the only in-repo record of how often a round ran."""
    try:
        with open(REPORT, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except Exception:  # noqa: BLE001
        return []
    rows = []
    for ln in lines:
        m = re.match(r"\|\s*(\d{4}-\d{2}-\d{2}T[0-9:+\-]+)\s*\|\s*(r\d+[a-z]?)\s*\|", ln)
        if m:
            rows.append({"ts": m.group(1), "round": m.group(2)})
    return rows


def _face_dates(face: dict) -> dict:
    p = os.path.join(ROOT, face["face"])
    out = {"dated_fields": {}, "mtime": None, "bytes": None, "exists": os.path.exists(p)}
    if not out["exists"]:
        return out
    try:
        st = os.stat(p)
        out["mtime"] = _iso(st.st_mtime)
        out["mtime_epoch"] = int(st.st_mtime)
        out["bytes"] = st.st_size
    except Exception as exc:  # noqa: BLE001
        out["error"] = repr(exc)[:120]
    try:
        data = json.load(open(p, encoding="utf-8"))
        for k in face["date_fields"]:
            if k in data:
                out["dated_fields"][k] = data[k]
    except Exception as exc:  # noqa: BLE001
        out["error"] = repr(exc)[:120]
    return out


def _locate(site: dict) -> tuple:
    """Resolve a reader site to a line number from its anchor text.

    r1429: the sites were hard-coded line numbers, so inserting 19 lines at the top of
    smoke_test.py moved every one of them -- and the E306 leg was then classified as
    `dates_the_face_in_a_gate` from whatever happened to sit at its old line (E305's check
    call). An anchor is a claim about the code; a line number is a claim about the file's
    layout. When the anchor does not resolve to exactly one line the published `line` is kept
    as a hint and `how` says so, so verify() can refuse rather than mislead.
    """
    anchor = site.get("anchor")
    if not anchor:
        return site.get("line"), "line_hint"
    try:
        lines = open(os.path.join(ROOT, site["file"]), encoding="utf-8",
                     errors="replace").read().splitlines()
    except Exception:  # noqa: BLE001
        return site.get("line"), "file_unreadable"
    hits = [i + 1 for i, ln in enumerate(lines) if anchor in ln]
    if not hits:
        return site.get("line"), "anchor_not_found"
    if len(hits) > 1:
        return site.get("line"), "anchor_ambiguous"
    return hits[0], "anchor"


def _reader_block(path: str, line: int) -> dict:
    """The site's own leg, not a fixed window.

    A fixed +-N line window bled one leg's evidence into its neighbour's (r1428: the
    dashboard leg's own `STALE` print was attributed to the tier leg that starts 30 lines
    later), so the block is anchored on the enclosing `try:`/`except` pair -- the unit the
    suite actually reports as one leg.
    """
    p = os.path.join(ROOT, path)
    try:
        lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    except Exception as exc:  # noqa: BLE001
        return {"found": False, "error": repr(exc)[:120]}
    if not lines or line - 1 >= len(lines):
        return {"found": False, "error": "line out of range"}
    anchor = line - 1
    lo = None
    for i in range(anchor, max(-1, anchor - 400), -1):
        if re.match(r"^\s*try:\s*$", lines[i]):
            lo = i
            break
    hi = None
    if lo is not None:
        for i in range(anchor, min(len(lines), anchor + 400)):
            if re.match(r"^\s*except\b", lines[i]):
                hi = i
                break
    if lo is None or hi is None:
        lo = max(0, anchor - WINDOW // 4)
        hi = min(len(lines) - 1, anchor + WINDOW // 4)
    block = lines[lo:hi + 1]
    return {"found": True, "lo": lo + 1, "hi": hi + 1, "lines": block,
            "anchored_on_leg": lo is not None and hi is not None}


def _classify(block: dict) -> dict:
    """Three tiers, each backed by the line numbers that produced the call."""
    if not block.get("found"):
        return {"tier": "site_not_found", "evidence": block.get("error")}
    probe, gate, stale_word, date_use = [], [], [], []
    for i, ln in enumerate(block["lines"]):
        n = block["lo"] + i
        if PROBE_RE.search(ln):
            probe.append({"line": n, "text": ln.strip()[:120]})
        if STALE_WORD_RE.search(ln):
            stale_word.append({"line": n, "text": ln.strip()[:120]})
        if DATE_USE_RE.search(ln) and CMP_RE.search(ln):
            date_use.append({"line": n, "text": ln.strip()[:120]})
        if GATE_RE.search(ln):
            gate.append({"line": n, "text": ln.strip()[:120]})
    # A gate only counts as a freshness gate if it sits within three lines of a date
    # comparison -- otherwise it is the leg's ordinary shape check.
    fresh_gate = []
    date_lines = [d["line"] for d in date_use]
    for g in gate:
        if any(abs(g["line"] - d) <= 3 for d in date_lines):
            fresh_gate.append(g)
    if probe:
        tier = "asks_the_clock"
    elif fresh_gate:
        tier = "dates_the_face_in_a_gate"
    elif stale_word and date_use:
        tier = "prints_staleness_without_gating"
    elif date_use:
        tier = "compares_the_face_to_itself"
    else:
        tier = "no_freshness_test"
    return {"tier": tier, "probe_lines": probe, "fresh_gate_lines": fresh_gate,
            "date_comparison_lines": date_use[:6], "stale_word_lines": stale_word[:4],
            "gate_lines": len(gate),
            "block": [block["lo"], block.get("hi", block["lo"] + len(block["lines"]) - 1)]}


BEHAVIOUR = {
    "asks_the_clock": "fails or warns on age without help from the producer",
    "dates_the_face_in_a_gate": "fails when the face's own date falls behind",
    "prints_staleness_without_gating": "prints STALE and passes -- the reader knows and does not act",
    "compares_the_face_to_itself": "passes on a stale face as long as it is internally consistent",
    "no_freshness_test": "passes on any age at all",
    "site_not_found": "unmeasured",
}


def _age_days(epoch: int | None, now: datetime) -> float | None:
    if not epoch:
        return None
    return round((now.timestamp() - epoch) / 86400.0, 3)


def _suite_practice() -> dict:
    """How often does the suite price the age of a face it opens?

    The two faces here are not being held to a standard invented by this card: the same
    suite already prices staleness for other faces. Counting the practice tree-wide turns
    'add a freshness check' from a suggestion into a comparison with what the file does
    elsewhere.
    """
    p = os.path.join(ROOT, "smoke_test.py")
    try:
        lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    except Exception as exc:  # noqa: BLE001
        return {"error": repr(exc)[:120]}
    legs, cur = [], []
    for ln in lines:
        if re.match(r"^\s*try:\s*$", ln) and cur:
            legs.append(cur)
            cur = [ln]
            continue
        cur.append(ln)
    if cur:
        legs.append(cur)
    opens_face, prices_age, examples = 0, 0, []
    narrow_open = 0  # a literal 'results/' string misses os.path.join("results", ...)
    self_excluded = 0
    for leg in legs:
        text = "\n".join(leg)
        # The study's own smoke leg reads results/state_tilt/unfloored_latest.json, so a census
        # of the suite would count itself (E180/E207/E319 family).  It is excluded by name and
        # the count is published rather than dropped silently.
        if "unfloored" in text.lower():
            self_excluded += 1
            continue
        if "results/" in text or "docs/" in text:
            narrow_open += 1
        if not any(k in text for k in ("results", "docs/")):
            continue
        opens_face += 1
        probe = PROBE_RE.search(text) is not None
        fresh_gate = False
        for i, ln in enumerate(leg):
            if DATE_USE_RE.search(ln) and CMP_RE.search(ln):
                window = "\n".join(leg[i:i + 4])
                if GATE_RE.search(window):
                    fresh_gate = True
                    break
        if probe or fresh_gate:
            prices_age += 1
            head = next((x.strip()[:70] for x in leg
                         if x.strip().startswith("check(")), "")
            if len(examples) < 4:
                examples.append(head or leg[0].strip()[:70])
    return {"legs_opening_a_face_or_page": opens_face,
            "legs_opening_a_face_by_the_narrow_rule": narrow_open,
            "legs_excluded_as_this_study_reading_itself": self_excluded,
            "legs_pricing_the_age": prices_age,
            "share": round(prices_age / opens_face, 4) if opens_face else None,
            "examples": examples}


def build(now: datetime | None = None, faces: list[dict] | None = None,
          root: str | None = None, write: bool = True) -> dict:
    """Derive the ledger. `root`/`faces` exist so selftest can run it on a fixture."""
    now = now or datetime.now().astimezone()
    faces = faces or FACES
    global ROOT, OUT_DIR, REPORT, PANEL  # noqa: PLW0603 - fixture redirection
    if root:
        ROOT = root
        OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
        REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
        PANEL = os.path.join(ROOT, "data", "daily", "sh510300.csv")

    panel = _panel_cutoff()
    rounds = _round_rows()
    ledger = []
    for face in faces:
        git = _git_last_commit(face["face"])
        dates = _face_dates(face)
        changed_epoch = git.get("epoch") or dates.get("mtime_epoch")
        # rounds since the face last changed: report rows newer than the commit
        since = [r for r in rounds
                 if changed_epoch and r["ts"][:19] > git["ts"][:19]] if git.get("ts") else []
        readers = []
        for rd in face["readers"]:
            line, how = _locate(rd)
            blk = _reader_block(rd["file"], line or rd.get("line"))
            cls = _classify(blk)
            readers.append({"site": f'{rd["file"]}:{line}', "what": rd["what"],
                            "resolved_by": how,
                            "tier": cls["tier"],
                            "behaviour_under_staleness": BEHAVIOUR.get(cls["tier"], "unmeasured"),
                            "evidence": {k: v for k, v in cls.items() if k != "tier"}})
        # staleness against the panel clock, from the face's own dated field when it has one
        claimed = {k: dates["dated_fields"].get(k) for k in face["date_fields"]}
        stale = None
        stale_by = None
        for k, v in claimed.items():
            if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v) and panel:
                if v[:10] < panel:
                    stale = True
                    stale_by = {"field": k, "face": v[:10], "panel": panel}
                    break
        if stale is None:
            stale = False
        priced_by_reader = [r for r in readers
                            if r["tier"] in ("asks_the_clock", "dates_the_face_in_a_gate")]
        # Which fix is cheaper: the reader can only price an age it can read, so a face
        # with its own dated field is fixable in one comparison; a face without one is a
        # producer problem.
        carries_date = bool(claimed)
        blocked = face.get("gate_blocked_by")
        if carries_date and blocked:
            cheaper = ("no reader-side gate is available for this face (%s); the fix is a "
                       "chain leg or a bounded-lag allowance" % blocked)
        elif carries_date:
            cheaper = ("reader prices the age it already reads (one comparison; the face is "
                       "self-dated)")
        else:
            cheaper = "put the writer on the chain (the face carries no date to price)"
        ledger.append({
            "face": face["face"], "label": face["label"], "writer": face["writer"],
            "writer_surface": face["writer_surface"],
            "expectation": face["expected_refresh"],
            "last_commit": git, "on_disk": dates,
            "age_days_since_commit": _age_days(changed_epoch, now),
            "age_days_since_mtime": _age_days(dates.get("mtime_epoch"), now),
            "rounds_since_change": len(since),
            "round_rows_total": len(rounds),
            "claimed_dates": claimed, "stale_vs_panel": stale,
            "stale_detail": stale_by,
            "readers": readers,
            "readers_that_price_the_age": len(priced_by_reader),
            "carries_its_own_date": carries_date,
            "gate_blocked_by": blocked,
            "cheaper_fix": cheaper,
        })

    stale_faces = [f for f in ledger if f["stale_vs_panel"]]
    blind = [f for f in stale_faces if f["readers_that_price_the_age"] == 0]
    summary = {
        "faces": len(ledger),
        "stale_vs_panel": len(stale_faces),
        "stale_and_no_reader_prices_it": len(blind),
        "reader_sites": sum(len(f["readers"]) for f in ledger),
        "reader_sites_that_price_the_age": sum(f["readers_that_price_the_age"] for f in ledger),
        "faces_carrying_their_own_date": sum(1 for f in ledger if f["carries_its_own_date"]),
        "by_reader_tier": {},
        "panel_cutoff": panel,
        "round_rows_parsed": len(rounds),
        "suite_practice": _suite_practice(),
    }
    for f in ledger:
        for r in f["readers"]:
            summary["by_reader_tier"][r["tier"]] = summary["by_reader_tier"].get(r["tier"], 0) + 1

    if summary["faces"] and summary["stale_and_no_reader_prices_it"] == summary["faces"]:
        verdict = ("every_face_in_this_set_is_behind_the_panel_and_no_reader_asks_how_old_it_is")
    elif blind:
        verdict = "a_stale_face_passes_every_reader_that_never_asks_how_old_it_is"
    elif summary["reader_sites"] and summary["reader_sites_that_price_the_age"] == summary["reader_sites"]:
        verdict = "the_readers_price_the_age_no_producer_change_is_needed"
    else:
        verdict = "the_staleness_is_visible_to_at_least_one_reader"

    result = {
        "study": "E409_session_only_writers_leave_their_readers_unfloored",
        "title": "two faces read by suite legs have no standing refresh",
        "evidence_cutoff": panel or now.strftime("%Y-%m-%d"),
        "generated": now.isoformat(timespec="seconds"),
        "verdict": verdict,
        "verdict_reason": (
            "%d of %d faces are behind the panel cutoff (%s) and %d of those have no reader "
            "that asks how old the face is; the suite therefore re-asserts a stale reading "
            "as if it were current." % (
                len(stale_faces), summary["faces"], panel or "unknown", len(blind))),
        "summary": summary,
        "ledger": ledger,
        "method_limits": [
            "rounds_since_change counts round-report rows, not suite executions: the suite is "
            "not run every round (r1425/r1426 ran two legs standalone; r1427's detached run "
            "did not finish in-window), so 'rounds' is an upper bound on suite runs.",
            "reader tiers are a lexical classifier over a %d-line window; it names the lines "
            "that produced each call so a wrong call is auditable rather than invisible." % WINDOW,
            "staleness is judged against the local daily panel's last bar day, which is the "
            "clock the rest of the chain uses; a face may be legitimately newer than that day "
            "when it is written after the close.",
        ],
    }
    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
        cut = result["evidence_cutoff"]
        path = os.path.join(OUT_DIR, "UNFLOORED-%s.json" % cut)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        latest = os.path.join(OUT_DIR, "unfloored_latest.json")
        with open(latest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        result["_path"] = os.path.relpath(path, ROOT)
    return result


def verify() -> list[str]:
    """Re-derive and refuse a published face that no longer matches the tree."""
    problems = []
    published = os.path.join(OUT_DIR, "unfloored_latest.json")
    if not os.path.exists(published):
        return ["no published face at %s" % os.path.relpath(published, ROOT)]
    old = json.load(open(published, encoding="utf-8"))
    new = build(write=False)
    if old.get("evidence_cutoff") != new["evidence_cutoff"]:
        problems.append("cutoff moved: %r vs %r" % (old.get("evidence_cutoff"),
                                                     new["evidence_cutoff"]))
    if old.get("verdict") != new["verdict"]:
        problems.append("verdict moved: %r vs %r" % (old.get("verdict"), new["verdict"]))
    for key in sorted(set(new["summary"]) | set(old.get("summary") or {})):
        a = (old.get("summary") or {}).get(key)
        b = new["summary"].get(key)
        if a != b:
            problems.append("summary.%s moved: %r vs %r" % (key, a, b))
    if problems:
        return problems
    # the ledger must still price every reader site it names
    for face in new["ledger"]:
        for r in face["readers"]:
            if r["tier"] == "site_not_found":
                problems.append("reader site not found: %s" % r["site"])
            if r.get("resolved_by") not in (None, "anchor"):
                problems.append("reader site %s did not resolve from its anchor (%s)"
                                % (r["site"], r.get("resolved_by")))
            if not r["behaviour_under_staleness"] or r["behaviour_under_staleness"] == "unmeasured":
                problems.append("reader %s has no measured behaviour" % r["site"])
    # an unfloored face that has no dated field must be flagged as a producer problem
    for face in new["ledger"]:
        if not face["carries_its_own_date"] and "chain" not in face["cheaper_fix"]:
            problems.append("face %s carries no date but the fix is not the chain" % face["face"])
    return problems


def selftest() -> int:
    import tempfile
    fails = []

    def ok(name, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + name + ("" if cond else " :: " + str(detail)))
        if not cond:
            fails.append(name)

    ok("classifier: a clock probe beats every other signal",
       _classify({"found": True, "lo": 1, "lines": [
           "d = json.load(open(p))",
           "age = time.time() - os.path.getmtime(p)",
           "if age > 86400: _bad.append('stale')"]})["tier"] == "asks_the_clock")
    ok("classifier: a dated comparison inside a gate counts",
       _classify({"found": True, "lo": 1, "lines": [
           "day = d.get('day') or ''",
           "if day < panel_day:",
           "    _bad.append('face is behind the panel')"]})["tier"] == "dates_the_face_in_a_gate")
    ok("classifier: printing STALE without gating is its own tier",
       _classify({"found": True, "lo": 1, "lines": [
           "if dash_day and dash_day < face_day:",
           "    msg += ' STALE(another host writes the dashboard)'"]})["tier"]
       == "prints_staleness_without_gating")
    ok("classifier: shape checks with no date are invisible staleness",
       _classify({"found": True, "lo": 1, "lines": [
           "tier = d.get('evidence_tier')",
           "if tier not in ('marks',):",
           "    _bad.append('unknown tier')"]})["tier"] == "no_freshness_test")
    ok("classifier: a date compared to itself is not freshness",
       _classify({"found": True, "lo": 1, "lines": [
           "if d.get('day') == expected:",
           "    _ok = True"]})["tier"] == "compares_the_face_to_itself")
    ok("classifier: a missing site is not silently classified",
       _classify({"found": False, "error": "gone"})["tier"] == "site_not_found")

    # end-to-end on a fixture tree: one stale self-dated face, one blind reader
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        os.makedirs(os.path.join(tmp, "data", "daily"))
        os.makedirs(os.path.join(tmp, "logs", "iteration-loop"))
        with open(os.path.join(tmp, "data", "daily", "sh510300.csv"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("2026-11-01,1,2,3,4,5\n2026-11-03,1,2,3,4,5\n")
        with open(os.path.join(tmp, "logs", "iteration-loop", "round_reports.md"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("| 2026-11-04T09:00:00+08:00 | r1 | x |\n"
                     "| 2026-11-03T09:00:00+08:00 | r0 | x |\n")
        face_rel = "results/state_tilt/fixture_latest.json"
        with open(os.path.join(tmp, face_rel), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"evidence_cutoff": "2026-10-31", "rows": []}, fh)
        with open(os.path.join(tmp, "reader.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join([
                "def leg():",
                "    d = json.load(open(p))",
                "    if not d.get('rows'):",
                "        _bad.append('empty')",
            ]) + "\n")
        fixture = [{
            "face": face_rel, "label": "fixture", "writer": "scripts/w.py",
            "writer_surface": "session", "date_fields": ["evidence_cutoff"],
            "expected_refresh": "never", "readers": [{"file": "reader.py", "line": 2,
                                                      "what": "shape only"}],
        }]
        res = build(now=datetime(2026, 11, 4, 9, 0).astimezone(), faces=fixture, root=tmp,
                    write=False)
        ok("fixture: the stale face is detected against the panel",
           res["summary"]["stale_vs_panel"] == 1, res["summary"])
        ok("fixture: the blind reader is counted as not pricing the age",
           res["summary"]["reader_sites_that_price_the_age"] == 0, res["summary"])
        ok("fixture: verdict names the blind read",
           res["verdict"] == "every_face_in_this_set_is_behind_the_panel_and_no_reader_asks_how_old_it_is",
           res["verdict"])
        ok("fixture: a self-dated face makes the reader the cheaper fix",
           "reader prices" in res["ledger"][0]["cheaper_fix"], res["ledger"][0]["cheaper_fix"])
        ok("fixture: rounds_since_change counts report rows after the commit",
           isinstance(res["ledger"][0]["rounds_since_change"], int))
        ok("fixture: the face is not rewritten by the build",
           json.load(open(os.path.join(tmp, face_rel)))["evidence_cutoff"] == "2026-10-31")

    total = 12
    print("\nselftest %d/%d" % (total - len(fails), total))
    return 0 if not fails else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        res = build()
        print(json.dumps({k: res[k] for k in ("evidence_cutoff", "verdict", "summary")},
                         ensure_ascii=False, indent=1))
        print("written:", res.get("_path"))
        for face in res["ledger"]:
            print("  %-46s age=%sd stale=%-5s priced_by=%d/%d  %s" % (
                face["face"], face["age_days_since_commit"], face["stale_vs_panel"],
                face["readers_that_price_the_age"], len(face["readers"]),
                face["cheaper_fix"][:60]))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e409_unfloored_faces.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))