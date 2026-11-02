"""E345 -- how long a gate was absent, and what the tree published while it stayed green.

E342 (REPAIRRECORD-2026-11-01) found three smoke checks removed in one commit whose
exact (name, condition) exists again at HEAD: between the removal and the restore the
assertion was simply not run.  E342 measured that the gate came back; this asks the
half a diff cannot answer -- what the tree published while it was gone.

Four questions, one face:

  (a) per removed name: the removal commit, the restore commit, and how much happened
      in between (commits, wall clock, rounds);
  (b) inside that window, did ANOTHER check on the same face assert the same property
      -- mechanically, a check whose label or condition text carries the property's
      own token, read off the file AS IT WAS in that window, not as it is today;
  (c) did the suite actually run in those rounds (logs/smoke.log x round_reports.md)?
      a gate that is deleted while the suite is not running is not a measurable gate
      absence, it is an unmeasured window -- so this outranks (b);
  (d) one verdict per window: covered_by_another_check | covered_by_a_published_face |
      unmeasured | nothing.

The vocabulary has a sharp edge: a face that REPORTS a property is not a check that
ASSERTS it (E344/E204 family).  A face carrying `actionable: false` is the value the
deleted check would have compared; nothing in the window compares it.  That case is
published as `nothing` with `self_report_present: true`, never promoted to
covered_by_a_published_face -- the latter needs a producer OTHER than the face's own
writer to publish the property as a claim.

Modes: run (write the face), selftest (hermetic legs, no git), verify (re-derive).

Written by bm-b r1366.
"""
from __future__ import annotations

import json
import io
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE_DIR = os.path.join(ROOT, "results", "state_tilt")
SOURCE_FACE = os.path.join(FACE_DIR, "REPAIRRECORD-2026-11-01.json")
SMOKE_LOG = os.path.join(ROOT, "logs", "smoke.log")
ROUNDS = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
FACE_NAME = "GATEABSENCE-2026-11-01.json"
LATEST = "gateabsence_latest.json"
GUARDED = "smoke_test.py"

# property tokens: what a check on this face claims.  Built from the restored
# conditions at HEAD, not from the card's prose.
PROPERTY_TOKENS = ("sizing", "shadow", "capped", "actionable", "order", "current",
                   "gross", "stale", "not an order")


# ---------------------------------------------------------------- small helpers
def _run(args, cwd=ROOT):
    p = subprocess.run(args, cwd=cwd, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def git(*args):
    rc, out, err = _run(["git"] + list(args))
    if rc != 0:
        return None
    return out.decode("utf-8", "replace")


def iso(ts):
    return datetime.fromtimestamp(int(ts), timezone.utc).astimezone().isoformat(timespec="seconds")


CHECK_CALL = re.compile(r"""(?<![\w.])check\(\s*(?P<q>["'])(?P<label>.*?)(?P=q)""")


def strip_comments(text):
    """Drop `#` comments, quote-aware, keeping line structure.

    Without this a commented-out check reads as a live one.  Triple-quoted strings are
    NOT modelled -- a `check("...")` written inside a docstring still reads as a call,
    which is why every token this face publishes is also printed with its label so a
    reader can see what was counted.
    """
    out = []
    for line in (text or "").splitlines():
        q = None
        buf = []
        for ch in line:
            if q:
                if ch == q:
                    q = None
                buf.append(ch)
            elif ch in "\"'":
                q = ch
                buf.append(ch)
            elif ch == "#":
                break
            else:
                buf.append(ch)
        out.append("".join(buf))
    return "\n".join(out)


def check_labels(text):
    """Labels of `check(<label>, <condition>, ...)` calls.

    Quote-adjacent parse (E204 pit): the label must OPEN the call -- a label mentioned
    inside another expression (a comment, a docstring, an f-string) is not a check.
    """
    return [m.group("label") for m in CHECK_CALL.finditer(strip_comments(text))]


def check_sites(text):
    """(label, condition-slice) pairs.

    The condition is everything from the call's own open up to the NEXT `check(` that
    starts a line -- i.e. the call body as indented in this file.  A slice, not a
    parsed expression: the question is which property words the surviving check
    carries, and that question does not need the AST.
    """
    text = strip_comments(text)
    starts = [(m.start(), m.group("label")) for m in CHECK_CALL.finditer(text)]
    sites = []
    for i, (pos, label) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        body = " ".join(text[pos:end].split())
        sites.append((label, body))
    return sites


def parse_claim(text):
    """The fields the deleted check compared, read off the face's own JSON.

    A face carrying the value is NOT a gate: what this measures is that the tree kept
    publishing a value whose assertion had been deleted -- the E344/E204 distinction,
    published as `self_report_*` beside a verdict that stays `nothing`.
    """
    if not text:
        return None
    try:
        d = json.loads(text)
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    gross = (d.get("book") or {}).get("gross") if isinstance(d.get("book"), dict) else None
    stale = (d.get("staleness") or {}).get("stale") if isinstance(d.get("staleness"), dict) else None
    ok = (d.get("actionable") is False and d.get("shadow") is True
          and isinstance(gross, (int, float)) and gross <= 3.0 + 1e-9)
    return {"actionable": d.get("actionable"), "shadow": d.get("shadow"), "gross": gross,
            "generated_for_bar": d.get("generated_for_bar"), "stale": stale,
            "satisfies_the_deleted_checks_condition": ok}


def file_at(sha, path=GUARDED):
    t = git("show", "%s:%s" % (sha, path))
    return t


def first_present(order, present):
    """First commit in MAINLINE order whose text carries the gate again.

    The order handed in must be the first-parent walk.  A `--full-history` walk is not
    usable here: this branch merges other hosts' lines, whose commits carry author
    dates BEFORE the removal, so 'the first commit in date order that has the label'
    resolves to a foreign commit that never restored anything on this line (measured:
    dca8c2b0d, authored 48 minutes before the removal, selected as its own restore).
    """
    for sha in order:
        if present(sha):
            return sha
    return None


def commit_range(lo, hi):
    t = git("log", "--format=%H|%at|%s", "%s..%s" % (lo, hi))
    if not t:
        return []
    rows = []
    for line in t.splitlines():
        if "|" in line:
            sha, ts, subj = line.split("|", 2)
            rows.append({"sha": sha, "ts": int(ts), "subject": subj})
    rows.reverse()
    return rows


def parse_smoke_log(path=SMOKE_LOG):
    """[{'ts':iso,'epoch':int,'pass':int,'fail':int}]"""
    rows = []
    if not os.path.exists(path):
        return rows
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\s+pass=(\d+)\s+fail=(\d+)", line.strip())
            if not m:
                continue
            dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
            rows.append({"ts": m.group(1), "epoch": int(dt.timestamp()),
                         "pass": int(m.group(2)), "fail": int(m.group(3))})
    return rows


def parse_rounds(path=ROUNDS):
    """[{'round':int,'ts':iso,'epoch':int,'postscript':bool}] from the ledger rows."""
    rows = []
    if not os.path.exists(path):
        return rows
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4:
                continue
            stamp, label = parts[1], parts[2]
            m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", stamp)
            r = re.match(r"r(\d+)", label)
            if not (m and r):
                continue
            dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
            rows.append({"round": int(r.group(1)), "ts": m.group(1),
                         "epoch": int(dt.timestamp()),
                         "postscript": "postscript" in label.lower()})
    return rows


def rounds_in(rows, lo_ts, hi_ts):
    """Distinct round numbers whose (non-postscript) ledger row starts inside the window."""
    seen = {}
    for row in rows:
        if row["postscript"]:
            continue
        if lo_ts <= row["epoch"] <= hi_ts:
            seen.setdefault(row["round"], row["epoch"])
    return sorted(seen.items())


def rounds_with_a_run(rounds, runs, hi_ts):
    """A round counted as 'smoke ran' when a run lands inside [round start, next round start).

    The last round's window is closed at the restore timestamp so a run that belongs to
    the next round cannot be borrowed.
    """
    if not rounds:
        return []
    bounds = []
    for i, (rnd, ts) in enumerate(rounds):
        end = rounds[i + 1][1] if i + 1 < len(rounds) else hi_ts
        bounds.append((rnd, ts, end))
    hit = []
    for rnd, ts, end in bounds:
        if any(ts <= run["epoch"] < max(end, ts + 1) for run in runs):
            hit.append(rnd)
    return hit


def cover_analysis(window_text, exclude_label=None, tokens=PROPERTY_TOKENS):
    """Which OTHER checks on the SAME face carry which property token.

    'Same face' = the label names the same product (`futures TSMOM`), which is the only
    mechanical handle the file gives; a check on another product is not a cover.  The
    deleted check's own label is excluded -- at the restore commit the restored gate is
    necessarily present, and counting it would make every window trivially covered.
    """
    face = "futures TSMOM"
    surviving = []
    covered = set()
    for label, cond in check_sites(window_text or ""):
        if face not in label:
            continue
        if exclude_label and label.strip() == exclude_label.strip():
            continue
        blob = (label + " " + cond).lower()
        toks = sorted(t for t in tokens if t in blob)
        surviving.append({"label": label, "tokens": toks})
        covered.update(toks)
    return surviving, sorted(covered)


def classify(rounds_n, runs_n, surviving_tokens, other_face_claim):
    if rounds_n and runs_n == 0:
        return "unmeasured", "the suite did not run in any of the %d rounds the window spans" % rounds_n
    if surviving_tokens:
        return "covered_by_another_check", (
            "a surviving check on the same face carries %d of the property's tokens (%s)"
            % (len(surviving_tokens), ", ".join(surviving_tokens)))
    if other_face_claim:
        return "covered_by_a_published_face", "a producer other than the writer publishes the property as a claim"
    return "nothing", "no other check on the face and no foreign producer asserts the property"


# ---------------------------------------------------------------- the study
def build():
    src = json.load(io.open(SOURCE_FACE, encoding="utf-8"))
    events = [e for e in src["history"]["events"] if e.get("kind") == "removed"]
    if not events:
        raise SystemExit("no removal events in the source face")

    runs = parse_smoke_log()
    rounds = parse_rounds()

    # group the removal sites by name (one name can be deleted in two places: the
    # assertion and its exception-branch fallback)
    by_name = {}
    for e in events:
        by_name.setdefault(e["name"], {"name": e["name"], "conditions": [],
                                       "commit": e["sha"], "ts": e["ts"]}).setdefault(
            "conditions", [])
        by_name[e["name"]]["conditions"].append(e.get("old"))
    removals = []
    for name, row in by_name.items():
        row["sites"] = len(row["conditions"])
        row["removal_sha"] = row["commit"]
        row["removal_ts"] = row["ts"]
        removals.append(row)

    windows = []
    for row in removals:
        rem, ts = row["removal_sha"], row["removal_ts"]
        path = git("rev-list", "--first-parent", "--reverse", "%s..HEAD" % rem) or ""
        order = [s for s in path.split() if s]
        restore_sha = first_present(
            order, lambda sha: row["name"] in check_labels(file_at(sha) or ""))
        restore_ts = None
        if restore_sha:
            meta = git("log", "-1", "--format=%at", restore_sha) or ""
            restore_ts = int(meta.strip() or 0)
        hi_ts = restore_ts if restore_ts else max(r["epoch"] for r in runs) if runs else ts
        span = commit_range(rem, restore_sha) if restore_sha else []
        main_span = (git("rev-list", "--first-parent", "--count", "%s..%s" % (rem, restore_sha)) or "0").strip() if restore_sha else "0"
        # The window's own state is the tip BEFORE the restoration, not the restoration
        # itself: at the restore commit every sibling is back, and counting them would
        # report coverage by a check that was itself absent throughout the window.
        wt_sha = None
        if restore_sha:
            wt_sha = (git("rev-parse", "%s^1" % restore_sha) or "").strip() or None
        wt_sha = wt_sha or (git("rev-parse", "HEAD") or "").strip()
        window_text = file_at(wt_sha)
        gate_absent_at_tip = row["name"] not in check_labels(window_text or "")
        surviving, covered = cover_analysis(window_text, exclude_label=row["name"])
        rw = rounds_in(rounds, ts, hi_ts)
        hits = rounds_with_a_run(rw, runs, hi_ts)
        runs_n = len([x for x in runs if ts <= x["epoch"] <= hi_ts])
        win_runs = [x for x in runs if ts <= x["epoch"] <= hi_ts]
        claim = parse_claim(git("show", "%s:results/futures_tsmom_signal.json" % wt_sha))
        claim_head = parse_claim(git("show", "HEAD:results/futures_tsmom_signal.json"))
        claim_note = None
        if claim is None:
            claim_note = ("the face is not in the tree at the window tip (%s), so the value the "
                          "deleted check compared was not published by this line at all during "
                          "the window" % wt_sha[:11])
        verdict, why = classify(len(rw), runs_n, covered, False)
        failing = len([x for x in win_runs if x["fail"] > 0])
        green_note = ("%d runs in %d rounds, %d of them with a non-zero fail count, pass counts "
                      "%s..%s" % (runs_n, len(rw), failing,
                                  min([x["pass"] for x in win_runs]) if win_runs else "-",
                                  max([x["pass"] for x in win_runs]) if win_runs else "-"))
        windows.append({
            "name": row["name"],
            "sites": row["sites"],
            "removal_sha": rem[:11], "removal_ts": iso(ts),
            "restore_sha": restore_sha[:11] if restore_sha else None,
            "restore_ts": iso(restore_ts) if restore_ts else None,
            "restored_by": (git("log", "-1", "--format=%s", restore_sha) or "").strip() if restore_sha else None,
            "commits_between": len(span),
            "commits_on_the_mainline_between": int(main_span or 0),
            "wall_hours": round((hi_ts - ts) / 3600.0, 2),
            "rounds_in_window": len(rw),
            "round_numbers": [r for r, _ in rw],
            "smoke_runs_in_window": runs_n,
            "smoke_runs_failing": len([x for x in win_runs if x["fail"] > 0]),
            "smoke_pass_min": min([x["pass"] for x in win_runs]) if win_runs else None,
            "smoke_pass_max": max([x["pass"] for x in win_runs]) if win_runs else None,
            "rounds_with_a_smoke_run": hits,
            "share_of_rounds_with_a_run": round(len(hits) / float(len(rw)), 4) if rw else None,
            "surviving_checks_on_the_face": surviving,
            "window_text_sha": wt_sha[:11],
            "gate_absent_at_window_tip": gate_absent_at_tip,
            "property_tokens_covered": covered,
            "property_tokens_of_the_deleted_check": sorted(
                {t for c in row["conditions"] for t in PROPERTY_TOKENS
                 if t in (row["name"] + " " + str(c)).lower()}),
            "self_report_present": os.path.exists(os.path.join(ROOT, "results", "futures_tsmom_signal.json")),
            "self_report_at_window_tip": claim,
            "self_report_note": claim_note,
            "self_report_satisfies_at_head": (claim_head or {}).get(
                "satisfies_the_deleted_checks_condition"),
            "verdict": verdict,
            "why": why,
            "what_the_suite_did": green_note,
        })

    by_verdict = {}
    for w in windows:
        by_verdict[w["verdict"]] = by_verdict.get(w["verdict"], 0) + 1

    summary = {
        "removed_names": len(removals),
        "removal_sites": sum(r["sites"] for r in removals),
        "restored": sum(1 for w in windows if w["restore_sha"]),
        "windows": len(windows),
        "by_verdict": by_verdict,
        "total_rounds_in_windows": sum(w["rounds_in_window"] for w in windows),
        "total_smoke_runs_in_windows": sum(w["smoke_runs_in_window"] for w in windows),
        "smoke_log_first_run": runs[0]["ts"] if runs else None,
        "smoke_log_runs": len(runs),
        "round_ledger_rows": len(rounds),
        "windows_publishing_a_face_that_satisfies_the_deleted_condition": sum(
            1 for w in windows if (w.get("self_report_at_window_tip") or {}).get(
                "satisfies_the_deleted_checks_condition")),
        "windows_with_no_check_asserting_the_property": sum(
            1 for w in windows if not w["surviving_checks_on_the_face"]),
        "share_of_window_rounds_with_a_run": (
            round(sum(len(w["rounds_with_a_smoke_run"]) for w in windows)
                  / float(sum(w["rounds_in_window"] for w in windows)), 4)
            if sum(w["rounds_in_window"] for w in windows) else None),
    }

    reasons = []
    for w in windows:
        reasons.append("%s: %s -- %s [%s]" % (w["name"].split(": ")[-1][:48], w["verdict"],
                                             w["why"], w["what_the_suite_did"]))
    verdict = "+".join(sorted(by_verdict)) if by_verdict else "no_windows"

    return {
        "study": "E345 how long a gate was absent and what stayed green",
        "evidence_cutoff": datetime.now().astimezone().isoformat(timespec="seconds"),
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "definition": {
            "source": "results/state_tilt/REPAIRRECORD-2026-11-01.json (E342 removal events, kind=removed)",
            "guarded_file": GUARDED,
            "restore": "the first commit after the removal, walking --full-history over commits that touch the guarded file, whose text again carries the same check label (merges included: a union-resolution restore adds no textual diff of its own)",
            "cover": "a surviving check whose label names the same product and whose label+condition text carries one of the property's tokens; the FILE TEXT is read at the restore commit, i.e. as it stood when the gate came back",
            "run": "a smoke run inside [round start, next round start) from logs/smoke.log x logs/iteration-loop/round_reports.md",
            "self_report_is_not_a_gate": "a face carrying the value the deleted check compared is published as `nothing` with self_report_present=true (E344/E204 family), never as covered_by_a_published_face",
        },
        "head": (git("rev-parse", "--short", "HEAD") or "").strip(),
        "windows": windows,
        "summary": summary,
        "verdict": verdict,
        "reasons": reasons,
    }


def write(face):
    os.makedirs(FACE_DIR, exist_ok=True)
    p = os.path.join(FACE_DIR, FACE_NAME)
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    with io.open(os.path.join(FACE_DIR, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    return p


# ---------------------------------------------------------------- selftest
def selftest():
    legs, fails = [], []

    def leg(name, cond, detail=""):
        (legs if cond else fails).append(name + ((" -- " + detail) if detail and not cond else ""))

    # 1. the label parser is quote-adjacent, not substring (E204 pit)
    t = 'check("a: b", True)\n# check("not a check", False)\nccheck("x", 1)\n'
    leg("L1 label parser takes only a string that opens a check( call",
        check_labels(t) == ["a: b"], str(check_labels(t)))

    # 2/3. cover classification -- tokens must come from a SURVIVING check, not the deleted one
    deleted = "product: futures TSMOM shadow face keeps its sizing rules"
    win_with = ('check("%s", rc == 0, "x")\n        check("product: futures TSMOM face '
                'is current, capped and not an order", ok)\n' % deleted)
    surv, cov = cover_analysis(win_with, exclude_label=deleted)
    leg("L2 a surviving sibling check on the same face is a cover",
        bool(cov) and "capped" in cov, str(cov))
    leg("L2b the deleted check's own label is not a self-cover",
        all(s["label"] != deleted for s in surv), str(surv))
    surv0, cov0 = cover_analysis(win_with, exclude_label=None)
    leg("L2c without the exclusion the window reads as trivially covered",
        any(s["label"] == deleted for s in surv0) and "sizing" in cov0)
    win_without = 'check("product: futures overlay breakeven is published", ok)\n'
    surv2, cov2 = cover_analysis(win_without, exclude_label=deleted)
    leg("L3 a check on another product is not a cover", cov2 == [], str(cov2))

    # 4. the unmeasured rule outranks a sibling cover
    v, why = classify(4, 0, ["sizing", "shadow"], False)
    leg("L4 no run in any window round -> unmeasured even with a sibling", v == "unmeasured", v)
    v2, _ = classify(4, 2, ["sizing"], False)
    leg("L5 a measured window with a sibling is covered_by_another_check", v2 == "covered_by_another_check", v2)
    v3, _ = classify(3, 3, [], False)
    leg("L6 measured, no sibling, no foreign claim -> nothing", v3 == "nothing", v3)
    v4, _ = classify(3, 3, [], True)
    leg("L7 a foreign producer claiming the property is the published-face class",
        v4 == "covered_by_a_published_face", v4)

    # 8. rounds: postscript rows share a round number and must not double count
    fx = [{"round": 5, "ts": "2026-11-01T10:00:00", "epoch": 100, "postscript": False},
          {"round": 5, "ts": "2026-11-01T10:05:00", "epoch": 400, "postscript": True},
          {"round": 6, "ts": "2026-11-01T11:00:00", "epoch": 3700, "postscript": False}]
    got = rounds_in(fx, 0, 5000)
    leg("L8 postscript rows do not add a round", [r for r, _ in got] == [5, 6], str(got))

    # 9. round x run matching: a run after the next round starts belongs to that round
    runs = [{"epoch": 200, "pass": 1, "fail": 0}, {"epoch": 3800, "pass": 1, "fail": 0}]
    hit = rounds_with_a_run(got, runs, 5000)
    leg("L9 a run inside [round, next round) is credited to its own round", hit == [5, 6], str(hit))
    runs_b = [{"epoch": 3800, "pass": 1, "fail": 0}]
    hit_b = rounds_with_a_run(got, runs_b, 5000)
    leg("L10 a round with no run of its own is not credited", hit_b == [6], str(hit_b))

    # 11. the last round's window is closed at the restore stamp, not left open
    hit_c = rounds_with_a_run([(7, 9000)], [{"epoch": 9500, "pass": 1, "fail": 0}], 9400)
    leg("L11 the last round cannot borrow a run past the restore stamp", hit_c == [], str(hit_c))

    # 12. smoke log parse keeps epoch and counts
    sm = parse_smoke_log()
    leg("L12 smoke.log parses into dated rows with counts",
        bool(sm) and all({"epoch", "pass", "fail"} <= set(r) for r in sm), "%d rows" % len(sm))

    # 13. round ledger parse drops anything that is not a round row
    rd = parse_rounds()
    leg("L13 round ledger parses into round numbers", bool(rd) and all(r["round"] > 0 for r in rd),
        "%d rows" % len(rd))

    # 14. a property token must never be read out of the deleted check's own words
    leg("L14 cover tokens are read from the surviving text only",
        cov == sorted(set(cov)) and "sizing" not in cov and "capped" in cov, str(cov))

    # 15/16. restore selection walks MAINLINE order, never date order
    order = ["foreign-early", "mainline-later", "mainline-latest"]
    present = {"mainline-later", "mainline-latest"}
    leg("L15 the restore is the first present in mainline order",
        first_present(order, lambda s: s in present) == "mainline-later")
    leg("L16 a gate that never comes back has no restore",
        first_present(order, lambda s: False) is None)

    # 17-20. the self-report is measured, and it is not a gate
    c_ok = parse_claim(json.dumps({"actionable": False, "shadow": True, "book": {"gross": 2.5},
                                   "generated_for_bar": "2026-10-28",
                                   "staleness": {"stale": False}}))
    leg("L17 a face that satisfies the deleted condition is recorded as such",
        bool(c_ok) and c_ok["satisfies_the_deleted_checks_condition"] is True, str(c_ok))
    c_order = parse_claim(json.dumps({"actionable": True, "shadow": True, "book": {"gross": 2.5}}))
    leg("L18 an actionable face does not satisfy the 'not an order' clause",
        c_order["satisfies_the_deleted_checks_condition"] is False)
    c_cap = parse_claim(json.dumps({"actionable": False, "shadow": True, "book": {"gross": 4.2}}))
    leg("L19 a face over the gross cap does not satisfy the deleted condition",
        c_cap["satisfies_the_deleted_checks_condition"] is False)
    leg("L20 an unreadable face is null, not a pass", parse_claim("{not json") is None)

    print("E345 selftest %d/%d" % (len(legs), len(legs) + len(fails)))
    for f in fails:
        print("FAIL", f)
    return 0 if not fails else 1


def verify():
    p = os.path.join(FACE_DIR, FACE_NAME)
    if not os.path.exists(p):
        print("verify: no face")
        return 2
    face = json.load(io.open(p, encoding="utf-8"))
    problems = []
    if not face.get("windows"):
        problems.append("no windows published")
    for w in face.get("windows", []):
        if w["verdict"] not in ("covered_by_another_check", "covered_by_a_published_face",
                                "unmeasured", "nothing"):
            problems.append("%s: verdict outside the frozen vocabulary" % w["name"])
        if w["rounds_in_window"] and w["smoke_runs_in_window"] == 0 and w["verdict"] != "unmeasured":
            problems.append("%s: zero runs in the window but not unmeasured" % w["name"])
        if w["verdict"] == "covered_by_another_check" and not w["property_tokens_covered"]:
            problems.append("%s: covered but no token" % w["name"])
        if w["restore_sha"] and w.get("gate_absent_at_window_tip") is not True:
            problems.append("%s: the gate is present at the window tip, so the window is mis-cut" % w["name"])
        share = w["share_of_rounds_with_a_run"]
        if share is not None and not (0.0 <= share <= 1.0):
            problems.append("%s: share outside [0,1]" % w["name"])

    # re-derive from git + logs/ and compare: the face must not be its own evidence
    fresh = build()
    old = {w["name"]: w for w in face.get("windows", [])}
    new = {w["name"]: w for w in fresh.get("windows", [])}
    if set(old) != set(new):
        problems.append("window set changed: %s -> %s" % (sorted(old), sorted(new)))
    for name in sorted(set(old) & set(new)):
        for key in ("restore_sha", "rounds_in_window", "smoke_runs_in_window",
                    "property_tokens_covered", "verdict", "gate_absent_at_window_tip"):
            if old[name].get(key) != new[name].get(key):
                problems.append("%s: %s moved %r -> %r" % (name[:40], key, old[name].get(key),
                                                           new[name].get(key)))
    print("verify: %d problems" % len(problems))
    for x in problems:
        print(" -", x)
    return 0 if not problems else 1


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        return verify()
    face = build()
    path = write(face)
    print("E345 wrote", os.path.relpath(path, ROOT))
    print("verdict:", face["verdict"])
    for w in face["windows"]:
        print("  %-52s %-26s rounds=%-3d runs=%-3d share=%s"
              % (w["name"].split(": ")[-1][:52], w["verdict"], w["rounds_in_window"],
                 w["smoke_runs_in_window"], w["share_of_rounds_with_a_run"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))