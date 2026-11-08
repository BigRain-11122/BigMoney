# -*- coding: utf-8 -*-
"""E575 -- for the rounds whose chain script declares a `--only` switch, did the run pass it?

E573 (r1601 bm-b) published a partition of 22 sentences that print fewer legs than their
round's own legs table: no row of those rounds declares a subset, and 11 of the rounds' chain
scripts carry a real scope switch (`--only`).  Its own note says the witness -- did the
invocation pass the flag -- is recorded nowhere in the report, so the prose cannot be blamed
for being silent until something else is asked.

This study asks that something else, on the 11 rounds, with three arms and no runner:

  row_arm    the round's own row and its sibling rows in the same report file, scanned for a
             printed invocation carrying the switch.  E573's phrase arm returned 0 here; it is
             re-derived rather than inherited so the control stays visible.
  disk_arm   any chain log or receipt on disk named for that round
             (`results/*r<round>bm<X>*s6*.log` / `*s6_chain*.json`), scanned for the flag.
  call_arm   the executed commands in this host's own session transcripts
             (`.codely-cli/auto-saves/*.json`, untracked by design).  Only a tool call's own
             `args.command` counts -- a mention inside model prose or inside a tool *result* is
             not an invocation, and the first draft of this study proved how much noise the
             prose arm carries (English "only", report text, the system prompt).

Attribution rule (published, and the reason this arm can speak at all): a command belongs to
the first round row of the same machine that was printed at or after the command's own
timestamp, within ATTRIB_TOL.  Round report rows are written at the end of a round, after its
commands, so "the next row after the command" is the round that ran it.  A command with no
following row inside the tolerance is published as unattributable, never assigned by guess.

Classes (first match wins, witness with every row):

  the_round_s_chain_was_invoked_with_the_switch
  the_round_s_chain_was_invoked_without_the_switch
  no_invocation_of_the_chain_is_recorded_on_this_host   (this machine's round, corpus searched)
  not_recoverable_on_this_host                          (another machine's round: its commands
                                                         ran on a host whose transcripts are
                                                         not here, so absence is not a finding)

Usage: python scripts/e575_only_flag.py [build|check|check-fast|verify|selftest]
"""
import glob
import importlib.util
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
E573_FACE = os.path.join(OUTDIR, "silentchain_latest.json")
CUTOFF = "2026-11-08"
TRANSCRIPT_DIR = os.path.join(ROOT, ".codely-cli", "auto-saves")
REPORTS = ("logs/iteration-loop/round_reports.md",
           "logs/iteration-loop/round_reports-bm-a.md",
           "logs/iteration-loop/round_reports-bm-c.md")

C_FLAG = "the_round_s_chain_was_invoked_with_the_switch"
C_NOFLAG = "the_round_s_chain_was_invoked_without_the_switch"
C_NONE = "no_invocation_of_the_chain_is_recorded_on_this_host"
C_OFF = "not_recoverable_on_this_host"
CLASSES = (C_FLAG, C_NOFLAG, C_NONE, C_OFF)

ROW_TS = re.compile(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2})(?::(\d{2}))?")
SNAP_TS = re.compile(r"chat-auto-save-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})")
ONLY = re.compile(r"--only(?:\s+|=)([A-Za-z0-9_.\-]+)?")
CHAIN_SCRIPT = re.compile(r"s6_chain_bm([abc])", re.I)
# A *mention* is not an invocation: `git add -- Tools/s6_chain_bmb.py` and
# `Select-String -Path Tools/s6_chain_bmb.py ...` both name the script.  An execution is a line
# that *starts* an interpreter on the script, and only those may decide this study.  The
# separator anchor and the required whitespace after the token are load-bearing: a bare `\bpy\b`
# also matches the `.py` extension of every file name on a `git add` line, which is exactly how
# the first build counted four `git add` commands as runs of the chain.
EXEC_LINE = re.compile(
    r"(?:^|[;&|]\s*|\bthen\s+)\s*(?:python[0-9.]*(?:\.exe)?|py|powershell(?:\.exe)?|pwsh)"
    r"\s+[^\n\r]*s6_chain_bm[abc]", re.I)
ATTRIB_TOL = timedelta(hours=6)
SNIPPET = 200


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _e573():
    """Reuse E573's row parsing so a round means the same thing in both studies."""
    path = os.path.join(HERE, "e573_silent_chain.py")
    spec = importlib.util.spec_from_file_location("e573_silent_chain", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row_ts(sentence):
    """The round row's own timestamp, when the row prints one (a few print a %s placeholder)."""
    m = ROW_TS.search((sentence or "")[:40])
    if not m:
        return None
    try:
        return datetime.strptime("%sT%s:%s" % (m.group(1), m.group(2), m.group(3) or "00"),
                                 "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None


def script_name(path):
    return os.path.basename(path or "")


def _snip(text, at, width=SNIPPET):
    if at is None or at < 0:
        return ""
    text = re.sub(r"\s+", " ", text or "")
    return text[max(0, at - width // 3): at + width]


def row_arm(row, e573):
    """A printed invocation of this round's chain script, with or without the switch."""
    lines = [(row.get("line"), row.get("sentence") or "")]
    report = row.get("report")
    for i, line in enumerate(e573.lines_of(report) if report else []):
        if e573.round_of_row(line) == row.get("round"):
            lines.append((i + 1, line))
    name = script_name((row.get("script") or {}).get("path"))
    hits = [{"line": n, "flag_token": m.group(0).strip(), "snippet": _snip(t, m.start())}
            for n, t in lines if name and name in (t or "")
            for m in ONLY.finditer(t or "")]
    invocations = [{"line": n, "snippet": _snip(t, (t or "").find(name))}
                   for n, t in lines if name and name in (t or "")]
    return {"declared_flag_lines": hits, "script_mentions": invocations}


def disk_arm(row):
    """Chain logs and receipts named for that round, if any survive on this host."""
    rnd, machine = row.get("round"), row.get("machine")
    seen, files = set(), []
    for pat in ("results/*r%sbm%s*s6*.log" % (rnd, machine),
                "results/*r%sbm%s*s6*.json" % (rnd, machine),
                "results/*r%sbm%s*_chain*.json" % (rnd, machine),
                "logs/iteration-loop/*r%s*" % rnd):
        for path in glob.glob(os.path.join(ROOT, pat)):
            base = os.path.basename(path)
            if base not in seen:
                seen.add(base)
                files.append(path)
    name = script_name((row.get("script") or {}).get("path"))
    hits, scanned = [], []
    for path in files:
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        scanned.append({"path": os.path.relpath(path, ROOT).replace("\\", "/"),
                        "bytes": len(text)})
        if name and name not in text:
            continue
        for m in ONLY.finditer(text):
            hits.append({"path": os.path.relpath(path, ROOT).replace("\\", "/"),
                         "flag_token": m.group(0).strip(), "snippet": _snip(text, m.start())})
    return {"files": scanned, "declared_flag_hits": hits}


def _snapshots():
    """(file timestamp, path) for every session-transcript snapshot on this host."""
    out = []
    for path in sorted(glob.glob(os.path.join(TRANSCRIPT_DIR, "chat-auto-save-*.json"))):
        m = SNAP_TS.search(os.path.basename(path))
        if not m:
            continue
        try:
            out.append((datetime(*[int(x) for x in m.groups()]), path))
        except ValueError:
            continue
    return out


def _parse_call_ts(raw, fallback):
    """A tool call's own timestamp, converted to this host's local naive clock.

    The transcripts stamp calls in UTC (`...Z`) while every round row prints `+08:00`.  Read as
    if it were local, a 16:31Z command lands eight hours early and is attributed to a round that
    finished before it ran -- the first build of this study did exactly that and moved a whole
    window's calls one round back, which is why the conversion is explicit and self-tested.
    """
    if not isinstance(raw, str):
        return fallback
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            got = datetime.strptime(raw.replace("Z", "+0000"), fmt)
            return got.astimezone().replace(tzinfo=None) if got.tzinfo else got
        except ValueError:
            continue
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            got = datetime.strptime(raw, fmt)
            return got + (datetime.now() - datetime.utcnow())
        except ValueError:
            continue
    return fallback


def executes_the_chain(cmd):
    """True only when a line of the command launches the chain through an interpreter."""
    return any(EXEC_LINE.search(line) for line in (cmd or "").splitlines())


def execution_lines(cmd):
    """The individual lines of a command that launch the chain, each with its own flag state.

    The unit has to be the execution *line*: a single tool call can `git add` the chain script
    and then run it twice, once with `--only` and once without, and a command-level answer would
    have to pick one of those two runs to describe.
    """
    out = []
    for line in (cmd or "").splitlines():
        m = EXEC_LINE.search(line)
        if not m:
            continue
        out.append({"line": re.sub(r"\s+", " ", line).strip()[:240],
                    "carries_the_switch": bool(ONLY.search(line)),
                    "flag_token": (ONLY.search(line).group(0).strip()
                                   if ONLY.search(line) else None)})
    return out


def command_corpus():
    """Executed chain invocations on this host's transcripts, deduped by tool call and line.

    Snapshots are cumulative (each file re-states the session so far), so the same call shows up
    in many files; the tool-call id plus the line index identifies one execution.
    """
    seen, calls, mentions, files = {}, [], 0, 0
    for snap_ts, path in _snapshots():
        files += 1
        try:
            face = _read_json(path)
        except Exception:
            continue
        for msg in ((face.get("conversationRecord") or {}).get("messages") or []):
            for call in (msg.get("toolCalls") or []):
                cmd = (call.get("args") or {}).get("command")
                if not isinstance(cmd, str) or not CHAIN_SCRIPT.search(cmd):
                    continue
                key = call.get("id") or (str(snap_ts) + cmd[:120])
                ts = _parse_call_ts(call.get("timestamp"), snap_ts)
                lines = execution_lines(cmd)
                if not lines:
                    mentions += 0 if key in seen else 1
                    seen[key] = True
                    continue
                for i, line in enumerate(lines):
                    sub = "%s#%d" % (key, i)
                    if sub in seen:
                        continue
                    seen[sub] = True
                    calls.append(dict(line, id=sub, ts=ts, snapshot=os.path.basename(path),
                                      command=cmd[:300],
                                      machine=CHAIN_SCRIPT.search(cmd).group(1).lower()))
    calls.sort(key=lambda c: c["ts"])
    return calls, mentions, files


def round_index(e573):
    """Every round row on this host's three report files, with the ts it printed."""
    rows = []
    for report in REPORTS:
        for i, line in enumerate(e573.lines_of(report)):
            rnd = e573.round_of_row(line)
            if rnd is None:
                continue
            ts = row_ts(line)
            rows.append({"report": report, "line": i + 1, "round": rnd, "ts": ts,
                         "machine": _machine_of(report)})
    rows.sort(key=lambda r: (r["ts"] or datetime.min))
    return rows


def _machine_of(report):
    if "bm-a" in report:
        return "a"
    if "bm-c" in report:
        return "c"
    return "b"


def attribute(calls, rows):
    """Assign each chain invocation to the first same-machine row printed at or after it."""
    unassigned = []
    for call in calls:
        machine = call.get("machine") or CHAIN_SCRIPT.search(call["command"]).group(1).lower()
        cands = [r for r in rows if r["machine"] == machine and r["ts"] and r["ts"] >= call["ts"]
                 and (r["ts"] - call["ts"]) <= ATTRIB_TOL]
        if not cands:
            unassigned.append({"line": call.get("line") or call["command"][:200],
                               "ts": call["ts"].strftime("%Y-%m-%dT%H:%M:%S"),
                               "carries_the_switch": bool(call.get("carries_the_switch")),
                               "reason": "no following row of that machine inside the tolerance"})
            continue
        target = min(cands, key=lambda r: r["ts"])
        call["round"] = target["round"]
        call["round_ts"] = target["ts"].strftime("%Y-%m-%dT%H:%M:%S")
        call["report"] = target["report"]
    return calls, unassigned


def _verdict(summary):
    s = summary
    n = s.get("rows", 0)
    if not n:
        return "no_round_to_price"
    c = s.get("by_class") or {}
    if c.get(C_FLAG) or c.get(C_NOFLAG):
        return ("%d_of_%d_rounds_leave_a_recorded_chain_invocation_and_%d_of_those_pass_the_switch"
                % (c.get(C_FLAG, 0) + c.get(C_NOFLAG, 0), n, c.get(C_FLAG, 0)))
    return "no_round_of_the_%d_leaves_a_recorded_chain_invocation_on_this_host" % n


def _verdict_line(s):
    c = s.get("by_class") or {}
    return ("rows=%d passed=%d without_it=%d none=%d off_host=%d "
            "| row_arm_flag_lines=%d disk_files=%d "
            "| corpus_executions=%d of_which_with_flag=%d unattributable=%d "
            "| snapshots_parsed=%d"
            % (s.get("rows", 0), c.get(C_FLAG, 0), c.get(C_NOFLAG, 0), c.get(C_NONE, 0),
               c.get(C_OFF, 0), s.get("row_arm_flag_lines", 0), s.get("disk_files", 0),
               s.get("corpus_executions", 0), s.get("corpus_executions_with_flag", 0),
               s.get("unattributable_executions", 0), s.get("snapshots_parsed", 0)))


def build(write=True):
    e573 = _e573()
    face = _read_json(E573_FACE)
    population = [r for r in face.get("rows") or []
                  if (r.get("script") or {}).get("scope_switch_tokens")]
    calls, mentions, snapshots = command_corpus()
    rows_index = round_index(e573)
    calls, unassigned = attribute(calls, rows_index)
    by_round = {}
    for call in calls:
        by_round.setdefault((call.get("report"), call.get("round")), []).append(call)
    rows = []
    for src in population:
        row = {"report": src.get("report"), "line": src.get("line"),
               "machine": src.get("machine"), "round": src.get("round"),
               "script_path": (src.get("script") or {}).get("path"),
               "script_commit": (src.get("script") or {}).get("commit"),
               "printed": src.get("printed"), "table_from_E568": src.get("table_from_E568"),
               "row_ts": None, "row_ts_source": None}
        ts = row_ts(src.get("sentence"))
        row["row_ts"] = ts.strftime("%Y-%m-%dT%H:%M:%S") if ts else None
        row["row_ts_source"] = ("the row's own printed timestamp" if ts
                                else "the row prints a placeholder instead of a timestamp")
        inner = {"round": row["round"], "machine": row["machine"], "report": row["report"],
                 "line": row["line"], "script": {"path": row["script_path"]},
                 "sentence": src.get("sentence")}
        row["row_arm"] = row_arm(inner, e573)
        row["disk_arm"] = disk_arm(inner)
        mine = [{"line": c["line"],
                 "command": c["command"],
                 "ts": c["ts"].strftime("%Y-%m-%dT%H:%M:%S"),
                 "snapshot": c["snapshot"],
                 "carries_the_switch": c["carries_the_switch"],
                 "flag_token": c["flag_token"]}
                for c in by_round.get((row["report"], row["round"]), [])]
        executed = mine
        row["call_arm"] = {"executions": executed,
                           "mentions_that_do_not_execute": 0,
                           "with_switch": sum(1 for c in executed if c["carries_the_switch"]),
                           "without_switch": sum(1 for c in executed
                                                 if not c["carries_the_switch"])}
        row["class"], row["decided_by"] = classify(row)
        rows.append(row)
    by_class = {k: sum(1 for r in rows if r["class"] == k) for k in CLASSES}
    summary = {
        "rows": len(rows),
        "by_class": by_class,
        "switchable_scripts": len(rows),
        "row_arm_flag_lines": sum(len(r["row_arm"]["declared_flag_lines"]) for r in rows),
        "disk_files": sum(len(r["disk_arm"]["files"]) for r in rows),
        "corpus_executions": len(calls),
        "corpus_mentions_that_do_not_execute": mentions,
        "corpus_executions_with_flag": sum(1 for c in calls if c["carries_the_switch"]),
        "attributed_executions": sum(len(r["call_arm"]["executions"]) for r in rows),
        "attributed_executions_other_rounds": len(
            [c for c in calls if c.get("round") is not None
             and (c.get("report"), c.get("round")) not in
             {(r["report"], r["round"]) for r in rows}]),
        "executions_with_flag_other_rounds": len(
            [c for c in calls if c.get("round") is not None and c["carries_the_switch"]
             and (c.get("report"), c.get("round")) not in
             {(r["report"], r["round"]) for r in rows}]),
        "unattributable_executions": len(unassigned),
        "unattributable_executions_with_flag": sum(
            1 for c in unassigned if c.get("carries_the_switch")),
        "unattributable_calls": len(unassigned),
        "snapshots_parsed": snapshots,
        "rows_whose_row_prints_no_timestamp": sum(1 for r in rows if not r["row_ts"]),
        "off_host_rows": sum(1 for r in rows if r["machine"] != "b"),
        "attribution_rule": ("a command belongs to the first row of the same machine printed at "
                             "or after it, within %s" % ATTRIB_TOL),
        "unnamed_witnesses": ["whether_an_unrecorded_run_passed_the_flag"],
    }
    out = {
        "study": "E575_only_flag",
        "card": "E575",
        "dept": "research+engineering",
        "machine": "bm-b",
        "evidence_cutoff": CUTOFF,
        "population": ("every E573 row whose round's own chain script carries a scope switch "
                       "(`--only`), machine-read from silentchain_latest.json"),
        "rule": ("a printed invocation in the row or a surviving chain file -> decided; else the "
                 "executed commands in this host's transcripts, attributed by first-following-row; "
                 "this machine with no such command -> none; another machine -> off host"),
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "unattributable_sample": unassigned[:12],
        "rows": rows,
    }
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        for path in (os.path.join(OUTDIR, "ONLYFLAG-%s.json" % CUTOFF),
                     os.path.join(OUTDIR, "onlyflag_latest.json")):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return out


def classify(row):
    if row["row_arm"]["declared_flag_lines"] or row["disk_arm"]["declared_flag_hits"]:
        return C_FLAG, "the round's own row or a surviving chain file prints the switch"
    call = row["call_arm"]
    if call["with_switch"]:
        return C_FLAG, ("%d executed command(s) of this round's chain carry the switch; first "
                        "witness: %r" % (call["with_switch"], next(
                            c.get("line") or c.get("command") for c in call["executions"]
                            if c["carries_the_switch"])))
    if call["without_switch"]:
        return C_NOFLAG, ("%d executed command(s) of this round's chain carry no switch; first "
                          "witness: %r" % (call["without_switch"], next(
                              c.get("line") or c.get("command") for c in call["executions"]
                              if not c["carries_the_switch"])))
    if row.get("machine") != "b":
        return C_OFF, ("another machine's round: its commands ran on a host whose transcripts "
                       "are not here, and no chain file for it survives on this one")
    return C_NONE, ("this machine's round: no executed command naming the chain script was "
                    "attributed to it and no chain file survives")


def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if face.get("verdict") != _verdict(s):
        problems.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(s):
        problems.append("the verdict line does not re-derive from the summary")
    if s.get("rows") != len(rows):
        problems.append("summary.rows does not equal the rows")
    counts = {k: sum(1 for r in rows if r.get("class") == k) for k in CLASSES}
    for k, v in counts.items():
        if (s.get("by_class") or {}).get(k) != v:
            problems.append("by_class.%s does not re-derive from the rows" % k)
    if s.get("row_arm_flag_lines") != sum(
            len((r.get("row_arm") or {}).get("declared_flag_lines") or []) for r in rows):
        problems.append("row_arm_flag_lines does not re-derive from the rows")
    if s.get("disk_files") != sum(len((r.get("disk_arm") or {}).get("files") or [])
                                 for r in rows):
        problems.append("disk_files does not re-derive from the rows")
    executions = sum(len((r.get("call_arm") or {}).get("executions") or []) for r in rows)
    mentions = sum((r.get("call_arm") or {}).get("mentions_that_do_not_execute") or 0
                   for r in rows)
    flags = sum((r.get("call_arm") or {}).get("with_switch") or 0 for r in rows)
    if s.get("attributed_executions") != executions:
        problems.append("attributed_executions does not re-derive from the rows")
    if s.get("unattributable_executions") < len(face.get("unattributable_sample") or []):
        problems.append("the unattributable sample is larger than the count it is a sample of")
    if s.get("corpus_executions") != (s.get("attributed_executions") or 0) + \
            (s.get("attributed_executions_other_rounds") or 0) + \
            (s.get("unattributable_executions") or 0):
        problems.append("corpus_executions does not equal population + other rounds + "
                        "unattributable")
    if s.get("corpus_executions_with_flag") != flags + \
            (s.get("executions_with_flag_other_rounds") or 0) + \
            (s.get("unattributable_executions_with_flag") or 0):
        problems.append("corpus_executions_with_flag does not re-derive")
    if (s.get("corpus_mentions_that_do_not_execute") or 0) < mentions:
        problems.append("corpus mentions are fewer than the mentions published in the rows")
    for r in rows:
        if r.get("class") not in CLASSES:
            problems.append("r%s: class %r is not one this study declares"
                            % (r.get("round"), r.get("class")))
            break
        if not r.get("decided_by"):
            problems.append("r%s: no witness is named" % r.get("round"))
            break
        arm = r.get("call_arm") or {}
        if r.get("class") == C_FLAG and not (
                (r.get("row_arm") or {}).get("declared_flag_lines")
                or (r.get("disk_arm") or {}).get("declared_flag_hits")
                or arm.get("with_switch")):
            problems.append("r%s: passed class with no printed invocation" % r.get("round"))
            break
        if r.get("class") == C_NOFLAG and not arm.get("without_switch"):
            problems.append("r%s: without-it class with no invocation to point at"
                            % r.get("round"))
            break
        if r.get("class") == C_OFF and r.get("machine") == "b":
            problems.append("r%s: off-host class on this machine's own round" % r.get("round"))
            break
        if arm.get("calls") and not (arm.get("with_switch") or arm.get("without_switch")):
            problems.append("r%s: calls published but neither arm counts them" % r.get("round"))
            break
    return problems


def selftest():
    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "%r != %r" % (got, want) if got != want else ""))

    eq("a_row_timestamp_is_read", row_ts("| 2026-11-02T00:45:00+08:00 | r1373 | x"),
       datetime(2026, 11, 2, 0, 45))
    eq("a_placeholder_row_has_no_timestamp", row_ts("%s | r1544 | E516 local carrier"), None)
    eq("a_date_only_row_still_yields_a_stamp",
       row_ts("2026-10-26 16:22 | r1285 (bm-c)"), datetime(2026, 10, 26, 16, 22))
    eq("the_switch_token_is_captured", ONLY.search("ran --only silent_chain x").group(1),
       "silent_chain")
    eq("the_equals_form_is_captured", ONLY.search("--only=leg_x").group(1), "leg_x")
    eq("the_chain_script_names_its_machine",
       CHAIN_SCRIPT.search(r"python Tools\s6_chain_bmC.py").group(1), "C")
    eq("a_snapshot_name_parses",
       SNAP_TS.search("chat-auto-save-2026-11-08-23-29-11-801.json").groups(),
       ("2026", "11", "08", "23", "29", "11"))
    _z = _parse_call_ts("2026-11-05T07:15:30.460Z", None)
    eq("a_zulu_call_is_moved_onto_the_local_clock",
       _z - datetime(2026, 11, 5, 7, 15, 30, 460000),
       datetime(2026, 11, 5, 7, 15, 30, tzinfo=timezone.utc).astimezone().utcoffset())
    eq("a_call_without_a_timestamp_falls_back_to_the_snapshot",
       _parse_call_ts(None, datetime(2026, 11, 5, 7, 0)), datetime(2026, 11, 5, 7, 0))

    def mkrows():
        return [{"report": "logs/iteration-loop/round_reports.md", "line": 1, "round": 10,
                 "ts": datetime(2026, 11, 1, 10, 0), "machine": "b"},
                {"report": "logs/iteration-loop/round_reports.md", "line": 2, "round": 11,
                 "ts": datetime(2026, 11, 1, 10, 30), "machine": "b"}]

    calls = [{"command": r"python Tools\s6_chain_bmb.py --only leg_x", "ts": datetime(2026, 11, 1, 9, 55),
              "id": "1", "snapshot": "s1", "executes_the_chain": True},
             {"command": r"python Tools\s6_chain_bmb.py", "ts": datetime(2026, 11, 1, 10, 5),
              "id": "2", "snapshot": "s1", "executes_the_chain": True},
             {"command": r"python Tools\s6_chain_bmb.py", "ts": datetime(2026, 11, 1, 20, 0),
              "id": "3", "snapshot": "s2", "executes_the_chain": True},
             {"command": r"python Tools\s6_chain_bmc.py", "ts": datetime(2026, 11, 1, 10, 1),
              "id": "4", "snapshot": "s1"}]
    got, unassigned = attribute([dict(c) for c in calls], mkrows())
    eq("a_command_belongs_to_the_first_following_row", got[0].get("round"), 10)
    eq("the_next_command_belongs_to_the_next_row", got[1].get("round"), 11)
    eq("a_command_without_a_following_row_is_unattributed", got[2].get("round"), None)
    eq("a_command_of_another_machine_is_unattributed_here", got[3].get("round"), None)
    eq("the_unattributable_list_keeps_both", len(unassigned), 2)
    eq("a_mention_that_executes_nothing_is_never_attributed",
       execution_lines(r"git add -- Tools/s6_chain_bmb.py"), [])
    eq("a_git_add_of_other_py_files_is_not_an_execution_either",
       execution_lines(r"git add -- Tools/card_ledger_guard.py Tools/s6_chain_bmb.py"), [])
    eq("a_select_string_over_the_script_is_not_an_execution",
       execution_lines(r"Select-String -Path Tools\s6_chain_bmb.py -Pattern x"), [])
    eq("an_interpreter_after_a_separator_is_an_execution",
       len(execution_lines("cd repo; python Tools\\s6_chain_bmb.py")), 1)
    eq("one_command_that_runs_the_chain_twice_yields_two_executions",
       len(execution_lines("python Tools\\s6_chain_bmb.py\n"
                           "python Tools\\s6_chain_bmb.py --only x")), 2)
    eq("each_of_those_two_lines_keeps_its_own_flag_state",
       [x["carries_the_switch"] for x in execution_lines(
           "python Tools\\s6_chain_bmb.py\npython Tools\\s6_chain_bmb.py --only x")],
       [False, True])

    def row(cls, **kw):
        r = {"round": 100, "machine": "b", "row_ts": "2026-11-01T10:00:00",
             "row_arm": {"declared_flag_lines": [], "script_mentions": []},
             "disk_arm": {"files": [], "declared_flag_hits": []},
             "call_arm": {"calls": [], "executions": [], "mentions_that_do_not_execute": 0,
                          "with_switch": 0, "without_switch": 0}}
        for k, v in kw.items():
            if k in ("row_arm", "disk_arm", "call_arm"):
                r[k] = dict(r[k], **v)
            else:
                r[k] = v
        return classify(r)[0]

    eq("a_printed_switch_in_the_row_passes",
       row(C_FLAG, row_arm={"declared_flag_lines": [{"line": 1}]}), C_FLAG)
    eq("a_surviving_chain_file_passes",
       row(C_FLAG, disk_arm={"declared_flag_hits": [{"path": "x.log"}]}), C_FLAG)
    eq("a_command_with_the_switch_passes",
       row(C_FLAG, call_arm={"calls": [{"command": "--only x", "carries_the_switch": True}],
                             "executions": [{"command": "--only x", "carries_the_switch": True}],
                             "with_switch": 1}), C_FLAG)
    eq("a_command_without_the_switch_is_recorded",
       row(C_NOFLAG, call_arm={"calls": [{"command": "python x", "carries_the_switch": False}],
                               "executions": [{"command": "python x",
                                               "carries_the_switch": False}],
                               "without_switch": 1}), C_NOFLAG)
    eq("a_mention_that_executes_nothing_does_not_decide",
       row(C_NONE, call_arm={"calls": [{"command": "git add -- x", "carries_the_switch": False,
                                        "executes_the_chain": False}],
                             "mentions_that_do_not_execute": 1}), C_NONE)
    eq("a_git_add_is_not_an_execution",
       executes_the_chain(r"git add -- Tools/s6_chain_bmb.py"), False)
    eq("a_select_string_is_not_an_execution",
       executes_the_chain(r"Select-String -Path Tools\s6_chain_bmb.py -Pattern x"), False)
    eq("a_python_run_is_an_execution",
       executes_the_chain(r"python Tools\s6_chain_bmb.py --only x"), True)
    eq("an_execution_on_a_later_line_still_counts",
       executes_the_chain("cd repo;\npython Tools/s6_chain_bmc.py"), True)
    eq("this_machine_with_nothing_is_none", row(C_NONE), C_NONE)
    eq("another_machine_with_nothing_is_off_host", row(C_OFF, machine="c"), C_OFF)

    fx = {"summary": {"rows": 1, "by_class": {C_FLAG: 1, C_NOFLAG: 0, C_NONE: 0, C_OFF: 0},
                      "row_arm_flag_lines": 0, "disk_files": 0, "corpus_executions": 1,
                      "corpus_mentions_that_do_not_execute": 0,
                      "corpus_executions_with_flag": 1, "attributed_executions": 1,
                      "attributed_executions_other_rounds": 0,
                      "executions_with_flag_other_rounds": 0,
                      "unattributable_executions": 0,
                      "unattributable_executions_with_flag": 0, "snapshots_parsed": 1},
          "unattributable_sample": [],
          "rows": [{"round": 100, "machine": "b", "class": C_FLAG, "decided_by": "fixture",
                    "row_arm": {"declared_flag_lines": [], "script_mentions": []},
                    "disk_arm": {"declared_flag_hits": [], "files": []},
                    "call_arm": {"calls": [{"command": "--only x", "carries_the_switch": True}],
                                 "executions": [{"command": "--only x",
                                                 "carries_the_switch": True}],
                                 "mentions_that_do_not_execute": 0,
                                 "with_switch": 1, "without_switch": 0}}]}
    fx["verdict"] = _verdict(fx["summary"])
    fx["verdict_line"] = _verdict_line(fx["summary"])
    eq("a_consistent_fixture_face_has_no_problems", face_problems(fx), [])
    bad = json.loads(json.dumps(fx))
    bad["verdict"] = "some_verdict_this_study_never_publishes"
    eq("a_hand_written_verdict_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["rows"][0]["call_arm"] = {"calls": [], "with_switch": 0, "without_switch": 0}
    bad["summary"]["calls_with_flag"] = 0
    bad["summary"]["chain_calls"] = 0
    bad["summary"]["by_class"][C_FLAG] = 0
    bad["verdict"] = _verdict(bad["summary"])
    bad["verdict_line"] = _verdict_line(bad["summary"])
    eq("a_passed_class_without_its_witness_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["rows"][0]["class"] = "probably_passed"
    eq("an_invented_class_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["rows"][0]["class"] = C_OFF
    eq("off_host_on_this_machine_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fx))
    bad["summary"]["corpus_executions"] = 7
    eq("a_call_count_that_does_not_re_derive_is_refused", bool(face_problems(bad)), True)
    failed = [n for n, good, _ in ok if not good]
    for n, good, detail in ok:
        print("  %s %s%s" % ("PASS" if good else "FAIL", n, "" if good else "  <- " + detail))
    print("selftest %d/%d" % (len(ok) - len(failed), len(ok)))
    return 0 if not failed else 1


def _check(face, label):
    problems = face_problems(face)
    if problems:
        for p in problems:
            print("%s FAIL %s" % (label, p))
        return 1
    print("%s PASS %s" % (label, face.get("verdict_line")))
    return 0


def check():
    return _check(_read_json(os.path.join(OUTDIR, "onlyflag_latest.json")), "CHECK")


def check_fast():
    """The cheap arm: the published face must still re-derive its own counts."""
    return check()


def verify():
    fresh = build(write=False)
    published = _read_json(os.path.join(OUTDIR, "onlyflag_latest.json"))
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "summary"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    if [(r.get("class"), r.get("round"), r.get("machine")) for r in fresh.get("rows") or []] != \
            [(r.get("class"), r.get("round"), r.get("machine"))
             for r in published.get("rows") or []]:
        problems.append("a row's class changed between the published face and a live rebuild")
    for p in problems:
        print("VERIFY FAIL %s" % p)
    if not problems:
        print("VERIFY PASS %d rows re-derived" % len(published.get("rows") or []))
    return 0 if not problems else 1


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "build"
    if cmd == "selftest":
        return selftest()
    if cmd == "build":
        face = build(write=True)
        print("BUILT %s | %s" % (face["verdict"], face["verdict_line"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "check-fast":
        return check_fast()
    if cmd == "verify":
        return verify()
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())