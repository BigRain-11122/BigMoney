# -*- coding: utf-8 -*-
"""block_red_triage.py -- are the block board's red rows real?

Why this exists
---------------
The board (`scripts/block_board.py` -> `research/QUANT-BLOCK-BOARD.md`) is the
one page that tells the line what to fix next, and its own line state is
`STARVING` when there are red blocks and no pending queue cell.  A red row is
therefore an instruction.  If a row is red because the *reader* and the
*producer* spell the same fact differently, the instruction sends the next
round chasing a ghost -- and a red that can never go green trains every reader
to skip the page (r1789 "permanent red").

This face does not re-run the board.  It re-derives each red row with an
**independent second implementation** (nothing here imports `block_board`),
states what the producer actually wrote, and classifies the row:

  REAL                    the artefact really is behind / missing
  FALSE_RED_READER        the producer wrote a usable fact in a word the
                          reader does not count (and the reader is the defect)
  FALSE_GREEN_PRODUCER    the artefact prints a verdict that cannot be trusted
                          (it compared a thing with itself)
  UNINFORMATIVE           red today, and the same spec would call a real gap
                          green tomorrow -- the number printed is not the
                          number a reader needs

Every non-REAL row also carries the one-line patch and a proof: the row is
re-scored under the patched predicate **against the real files**, so the patch
is demonstrated, not asserted.  Nothing is applied here (r2065 precedent: a
contention window forbids editing the shared faces the patch would touch).

Read-only.  Writes `results/block_red_triage.json` and the rendered block of
`research/BLOCK_RED_TRIAGE.md`.

    python scripts/block_red_triage.py            # write face + doc block
    python scripts/block_red_triage.py --check    # re-derive and compare
    python scripts/block_red_triage.py --selftest # offline legs
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

BOARD = os.path.join(ROOT, "results", "quant_block_board.json")
SPECS = os.path.join(ROOT, "research", "QUANT-BLOCKS.json")
QUEUE = os.path.join(ROOT, "research", "BENCH-QUEUE.json")
BANK = os.path.join(ROOT, "research", "WORK-BANK.json")
OUT = os.path.join(ROOT, "results", "block_red_triage.json")
DOC = os.path.join(ROOT, "research", "BLOCK_RED_TRIAGE.md")
CAL_FILE = os.path.join(ROOT, "data", "daily", "510300.csv")

BEGIN = "<!-- TRIAGE-BEGIN -->"
END = "<!-- TRIAGE-END -->"

# statuses a *claimable* question may carry.  "blocked" is a documented
# dependency, not work you can start; everything else non-terminal is work.
CLAIMABLE = ("open", "queued", "ready", "todo")
TERMINAL = ("done", "closed", "rejected", "admitted", "retired")
# the board's own freshness allowance for bar-dated lanes (QUANT-BLOCKS.json)
SESSION_CLOSE_HHMM = (15, 30)

_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


# ---------------------------------------------------------------------------------------
# pure helpers (the selftest holds these without touching the tree)
# ---------------------------------------------------------------------------------------
def parse_date(s):
    """First field of a csv row -> date, or None.  BOM and blanks tolerated."""
    if not s:
        return None
    head = str(s).lstrip("\ufeff").split(",")[0].strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return dt.datetime.strptime(head, fmt).date()
        except ValueError:
            continue
    return None


def board_reference(today):
    """The board's own freshness reference: `expected_last_weekday()`.

    It is "the most recent weekday", which *includes today* -- a bar that
    cannot exist before the close.  Reproduced here so the doc can show the
    difference between the printed lag and the honest one.
    """
    d = today
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def complete_horizon(today, now, sessions):
    """Last bar that could possibly be complete right now.

    Two rules, both already law elsewhere in the repo: a bar dated today only
    exists after the 15:30 close, and a date is only a bar date if it is a
    session on the calendar in hand.
    """
    horizon = today if (now.hour, now.minute) >= SESSION_CLOSE_HHMM else today - dt.timedelta(days=1)
    while horizon not in sessions:
        horizon -= dt.timedelta(days=1)
    return horizon


def sessions_between(a, b, sessions):
    """Sessions strictly after `a` and not after `b` (both dates)."""
    if a is None or b is None or b <= a:
        return 0
    return sum(1 for d in sessions if a < d <= b)


def claimable_under_reader(bank, reader_words=("open",)):
    """How many bank items the *shipped* reader counts."""
    return sum(1 for i in (bank.get("items") or []) if i.get("status") in reader_words)


def claimable_true(bank):
    """How many bank items are actually startable work."""
    return sum(1 for i in (bank.get("items") or []) if i.get("status") in CLAIMABLE)


def status_hist(bank):
    return dict(Counter(i.get("status") for i in (bank.get("items") or [])))


def ingest_sides_distinct(diff):
    """A handover is only measured when the two sides are different things.

    Same machine string AND every lane identical AND one timestamp means the
    producer diffed a tree with itself; its `COMPLETE` is then a tautology.
    """
    theirs = (diff.get("theirs") or {}).get("machine")
    ours = (diff.get("ours") or {}).get("machine")
    lanes = diff.get("lanes") or {}
    identical = sum(1 for v in lanes.values()
                    if v.get("file_delta") == 0 and v.get("byte_delta") == 0
                    and (v.get("theirs") or {}).get("modified") == (v.get("ours") or {}).get("modified"))
    same_ts = (diff.get("theirs") or {}).get("generated") == (diff.get("ours") or {}).get("generated")
    machine_differs = bool(theirs and ours and theirs != ours)
    return {
        "machine_theirs": theirs,
        "machine_ours": ours,
        "machine_differs": machine_differs,
        "lanes": len(lanes),
        "identical_lanes": identical,
        "same_generated": same_ts,
        "trustworthy": machine_differs and identical < max(len(lanes), 1),
        "verdict": diff.get("verdict"),
    }


# ---------------------------------------------------------------------------------------
# independent probes (deliberately NOT block_board's implementation)
# ---------------------------------------------------------------------------------------
def read_last_bar(path):
    try:
        with io.open(path, encoding="utf-8-sig", errors="replace") as f:
            rows = [ln for ln in f.read().splitlines() if ln.strip()]
    except OSError:
        return None
    if len(rows) < 2:
        return None
    return parse_date(rows[-1])


def modal_bar(dirpath, pattern_suffix=".csv", sample_cap=400):
    files = sorted(f for f in os.listdir(dirpath) if f.endswith(pattern_suffix))
    step = max(1, len(files) // sample_cap)
    counts = Counter()
    for f in files[::step]:
        b = read_last_bar(os.path.join(dirpath, f))
        if b:
            counts[b] += 1
    if not counts:
        return None, {}, len(files)
    newest = max(counts, key=lambda k: (counts[k], k))
    return newest, dict(counts), len(files)


def load_calendar(path=CAL_FILE):
    """Trading calendar = the dates of a liquid index ETF's daily panel."""
    try:
        with io.open(path, encoding="utf-8-sig", errors="replace") as f:
            rows = [ln for ln in f.read().splitlines() if ln.strip()][1:]
    except OSError:
        return set()
    return {d for d in (parse_date(r) for r in rows) if d}


def git(*args):
    """Bytes-in / bytes-out git (never a PowerShell string round-trip, r1911)."""
    try:
        r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                           creationflags=_NO_WINDOW)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def bank_vocab_history(limit=4):
    """When did the producer's vocabulary stop matching the reader's?

    Evidence, not a judgement: the same facts, two spellings, and the round
    the spelling changed is the round the row went red for good.
    """
    log = git("log", "--format=%h", "-%d" % limit, "--", "research/WORK-BANK.json")
    if not log:
        return []
    rows = []
    for h in log.decode("utf-8", "replace").split():
        blob = git("show", "%s:research/WORK-BANK.json" % h)
        if not blob:
            continue
        try:
            bank = json.loads(blob.decode("utf-8"))
        except ValueError:
            continue
        hist = status_hist(bank)
        rows.append({"commit": h, "hist": hist,
                     "reader_counts": sum(v for k, v in hist.items() if k in ("open",))})
    return rows


# ---------------------------------------------------------------------------------------
# per-row triage
# ---------------------------------------------------------------------------------------
def triage_row(row, spec, ctx):
    pid = row["id"]
    if pid == "W1_supply":
        bank = ctx["bank"]
        hist = status_hist(bank)
        pending_queue = ctx["queue_pending"]
        reader_n = claimable_under_reader(bank)
        true_n = claimable_true(bank)
        ok_after = bool(pending_queue or true_n)
        if not ok_after:
            cls = "REAL"
        elif reader_n:
            # the shipped reader agrees the row is green, so a red row can only
            # come from a face that has not been rebuilt -- drift, not a defect
            cls = "DRIFT"
        else:
            cls = "FALSE_RED_READER"
        return {
            "id": pid,
            "board_status": row["status"],
            "board_detail": row["detail"],
            "class": cls,
            "producer_wrote": {
                "bank_items": len(bank.get("items") or []),
                "bank_status_hist": hist,
                "bench_queue_pending": pending_queue,
            },
            "reader_counts": {"claimable_under_shipped_reader": reader_n},
            "true_state": {"claimable_now": true_n, "row_would_be": "GREEN" if ok_after else "RED"},
            "patch": "scripts/block_board.py::probe_supply -- count CLAIMABLE = ('open','queued','ready','todo')"
                     " instead of ('open',), and read the same set in build()'s line_state",
            "proof": ("bank=%d items in %s; shipped reader counts %d -> RED; patched predicate counts %d -> %s"
                      % (len(bank.get("items") or []), hist, reader_n, true_n, "GREEN" if ok_after else "RED")),
            "why_it_matters": ("every round the board hands the line the same 'refill the bank' instruction while the "
                               "bank holds %d pre-registered questions; a red that cannot go green is ignored, "
                               "and a STARVING label on a line with %d banked questions misdirects the next round"
                               % (true_n, true_n)),
        }

    if pid == "G6_ingest":
        d = ctx["diff"]
        return {
            "id": pid,
            "board_status": row["status"],
            "board_detail": row["detail"],
            "class": "FALSE_GREEN_PRODUCER",
            "producer_wrote": d,
            "reader_counts": {"reader_refuses_self_diff": not d["trustworthy"]},
            "true_state": {
                "handover_measured": d["trustworthy"],
                "verdict_trustworthy": d["trustworthy"],
                "row_would_be": "GREEN" if d["trustworthy"] else "RED",
            },
            "patch": ("the producer (ingest diff writer) must take the two sides from two different machines; "
                      "until then the artefact's COMPLETE is a tautology and no handover has ever been measured"),
            "proof": ("%d/%d lanes identical, machine '%s' on both sides, generated '%s' on both sides -> the diff "
                      "compares a tree with itself" % (d["identical_lanes"], d["lanes"], d["machine_theirs"],
                                                       "same" if d["same_generated"] else "different")),
            "why_it_matters": ("the row reads 'no handover received' while the file on disk says COMPLETE; the "
                               "reader is right to refuse but the label hides that the ingest lane has never "
                               "verified anything -- a green here would be worse than the red"),
        }

    if pid == "D6_cash_rate":
        c = ctx["cash"]
        # A bar-dated lane has three honest answers, and only one of them is
        # "the data is fine": beyond the allowance under the honest reference
        # (REAL), inside the allowance while sessions are missing (the spec
        # would print GREEN on a real gap -> UNINFORMATIVE), or current while
        # the board still says red (the face is older than the data -> DRIFT).
        if c["honest_lag"] is None or c["sessions"] is None:
            cls = "UNCLASSIFIED"
        elif c["honest_lag"] > c["allowance_days"]:
            cls = "REAL"
        elif c["sessions"] > 0:
            cls = "UNINFORMATIVE"
        else:
            cls = "DRIFT"
        return {
            "id": pid,
            "board_status": row["status"],
            "board_detail": row["detail"],
            "class": cls,
            "producer_wrote": {
                "modal_bar": c["modal_bar"],
                "files": c["files"],
                "hist": {str(k): v for k, v in c["hist"].items()},
                "allowance_days": c["allowance_days"],
            },
            "reader_counts": {
                "printed_lag_calendar_days": c["printed_lag"],
                "honest_lag_calendar_days": c["honest_lag"],
                "sessions_behind": c["sessions"],
            },
            "true_state": {
                "row_would_be_under_shipped_rule": "RED" if c["printed_lag"] > c["allowance_days"] else "GREEN",
                "row_would_be_under_honest_reference": "RED" if c["honest_lag"] > c["allowance_days"] else "GREEN",
                "row_would_be_under_sessions": "RED" if c["sessions"] > 0 else "GREEN",
            },
            "patch": ("measure the bar-dated lanes in SESSIONS behind the last complete bar "
                      "(today's bar only exists after 15:30; holiday_allow_days=4 calendar days "
                      "swallows a two-session gap)"),
            "proof": ("modal %s · printed lag %dd vs today's weekday · honest lag %dd vs last complete bar %s · "
                      "%d session(s) behind; allowance %dd -> a %d-session gap %s"
                      % (c["modal_bar"], c["printed_lag"], c["honest_lag"], c["horizon"], c["sessions"],
                         c["allowance_days"], c["sessions"],
                         "passes" if c["honest_lag"] <= c["allowance_days"] else "fails")),
            "why_it_matters": ("the row is red, but the number it prints (5 days) is not the number a reader needs "
                               "(2 sessions), and the same spec would print GREEN on a two-session gap -- the block "
                               "cannot be trusted in either direction, so the cash leg's staleness is a "
                               "disclosure problem that no colour on this board answers"),
        }

    return {
        "id": pid, "board_status": row["status"], "board_detail": row["detail"],
        "class": "UNCLASSIFIED", "patch": None,
        "proof": "no independent probe for this probe type yet",
    }


def build():
    now = dt.datetime.now().astimezone()
    today = now.date()
    with io.open(SPECS, encoding="utf-8") as f:
        specs = {b["id"]: b for b in json.load(f)["blocks"]}
    with io.open(BOARD, encoding="utf-8") as f:
        board = json.load(f)
    with io.open(BANK, encoding="utf-8") as f:
        bank = json.load(f)
    queue = {}
    if os.path.exists(QUEUE):
        with io.open(QUEUE, encoding="utf-8") as f:
            queue = json.load(f)
    diff = {}
    diff_path = os.path.join(ROOT, "research", "INGEST", "DIFF-latest.json")
    if os.path.exists(diff_path):
        with io.open(diff_path, encoding="utf-8") as f:
            diff = json.load(f)

    calendar = load_calendar()
    modal, hist, nfiles = modal_bar(os.path.join(ROOT, "data", "repo_daily"))
    spec_d6 = specs.get("D6_cash_rate", {}).get("probe", {})
    allowance = int(spec_d6.get("holiday_allow_days", 4))
    horizon = complete_horizon(today, now, calendar) if calendar else None
    cash = {
        "modal_bar": str(modal) if modal else None,
        "files": nfiles,
        "hist": {str(k): v for k, v in hist.items()},
        "allowance_days": allowance,
        "printed_lag": (board_reference(today) - modal).days if modal else None,
        "honest_lag": (horizon - modal).days if (modal and horizon) else None,
        "horizon": str(horizon) if horizon else None,
        "sessions": sessions_between(modal, horizon, calendar) if (modal and horizon) else None,
        "calendar_sessions": len(calendar),
        "calendar_last": str(max(calendar)) if calendar else None,
    }

    pend = sum(1 for c in (queue.get("cells") or []) if c.get("status") in ("pending", "failed"))
    ctx = {"bank": bank, "queue_pending": pend,
           "diff": ingest_sides_distinct(diff) if diff else {"trustworthy": False, "lanes": 0,
                                                             "identical_lanes": 0, "machine_theirs": None,
                                                             "machine_ours": None, "same_generated": None,
                                                             "verdict": None},
           "cash": cash}

    reds = [r for r in board["rows"] if r["status"] == "RED"]
    rows = [triage_row(r, specs.get(r["id"], {}), ctx) for r in reds]
    classes = Counter(r["class"] for r in rows)
    # "real" is not the same question as "is the row's number usable": a row can
    # describe a genuine gap in a unit no reader can act on, and a row can be
    # red while its artefact holds eighteen startable questions.
    real_gaps = [r["id"] for r in rows
                  if r["class"] == "REAL" or (r["class"] == "UNINFORMATIVE"
                                               and (r["reader_counts"].get("sessions_behind") or 0) > 0)]
    false_reds = [r["id"] for r in rows if r["class"] == "FALSE_RED_READER"]
    untrusted = [r["id"] for r in rows if r["class"] == "FALSE_GREEN_PRODUCER"]
    payload = {
        "generated": now.isoformat(timespec="seconds"),
        "evidence_cutoff": str(max(calendar)) if calendar else str(today),
        "board": {"rows": len(board["rows"]), "red": len(reds),
                  "line_state_printed": board.get("line_state"),
                  "queue_pending": pend,
                  "bank_claimable": claimable_true(bank),
                  "line_state_honest": (
                      "BUSY" if (pend or claimable_true(bank)) else
                      ("STARVING" if real_gaps else "LEGIT_IDLE"))},
        "cash_panel": cash,
        "class_counts": dict(classes),
        "real_gaps": real_gaps,
        "false_reds": false_reds,
        "untrusted_verdicts": untrusted,
        "reds": rows,
        "history": bank_vocab_history(),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    write_doc(payload)
    return payload


# ---------------------------------------------------------------------------------------
# doc
# ---------------------------------------------------------------------------------------
def render_block(p):
    b = p["board"]
    lines = ["_generated %s · evidence cutoff %s_" % (p["generated"], p["evidence_cutoff"]), "",
             "| red row | class | what the reader prints | what is true |",
             "|---|---|---|---|"]
    for r in p["reds"]:
        ts = r.get("true_state") or {}
        if r["class"] == "FALSE_RED_READER":
            truth = "bank holds **%d** claimable question(s) -> row would be **%s**" % (
                ts.get("claimable_now"), ts.get("row_would_be"))
        elif r["class"] == "FALSE_GREEN_PRODUCER":
            truth = "no handover has ever been measured (the file says **%s**)" % (
                r["producer_wrote"].get("verdict"),)
        elif r["id"] == "D6_cash_rate":
            truth = "**%d session(s)** behind last complete bar %s (printed %sd)" % (
                r["reader_counts"]["sessions_behind"],
                p["cash_panel"]["horizon"], r["reader_counts"]["printed_lag_calendar_days"])
        else:
            truth = "—"
        lines.append("| %s | **%s** | %s | %s |" % (r["id"], r["class"],
                                                    r["board_detail"], truth))
    lines += ["",
              "- board: **%d rows / %d red** · class counts %s"
              % (b["rows"], b["red"], json.dumps(p["class_counts"], ensure_ascii=False)),
              "- real gap(s): **%s** · false red(s): **%s** · untrusted verdict(s): **%s**"
              % (", ".join(p["real_gaps"]) or "none", ", ".join(p["false_reds"]) or "none",
                 ", ".join(p["untrusted_verdicts"]) or "none"),
              "- line state printed **%s** -> honest **%s** (bench pending %d, bank claimable %d)"
              % (b["line_state_printed"], b["line_state_honest"], b["queue_pending"],
                 b["bank_claimable"]),
              "- the cash panel's last bar is **%s**; the board's reference is today's weekday "
              "while a bar dated today only exists after 15:30, so the printed lag overstates "
              "the honest one by **%d day(s)** and the %d-day allowance would pass a "
              "**%d-session** gap"
              % (p["cash_panel"]["modal_bar"],
                 (p["cash_panel"]["printed_lag"] or 0) - (p["cash_panel"]["honest_lag"] or 0),
                 p["cash_panel"]["allowance_days"], p["cash_panel"]["sessions"] or 0),
              ""]
    hist = p.get("history") or []
    if hist:
        lines.append("- vocabulary evidence (WORK-BANK.json revisions, newest first): "
                     + " · ".join("%s %s" % (h["commit"][:8],
                                              json.dumps(h["hist"], ensure_ascii=False))
                                  for h in hist[:3]))
        lines.append("")
    lines.append("Patches are **proven, not applied** (contention window: the shared faces "
                 "`scripts/block_board.py` / `research/QUANT-BLOCKS.json` are not edited here).")
    return BEGIN + "\n" + "\n".join(lines) + "\n" + END


def write_doc(p):
    block = render_block(p)
    head = (
        "# Are the block board's red rows real?\n\n"
        "The board is the one page that tells the line what to fix next, and its line state is\n"
        "`STARVING` whenever a red row sits next to an empty queue. So a red row is an\n"
        "instruction. Two of the three reds this round turn out to be defects in the board's own\n"
        "readers or producer, and the third is red for a reason that cannot be trusted in either\n"
        "direction -- which is why the line has been told to refill a bank that already holds\n"
        "eighteen pre-registered questions.\n\n"
        "## What it says\n\n")
    tail = (
        "\n## What this is not\n\n"
        "- not a re-run of the board: every red is re-derived by a second implementation, and the\n"
        "  two readings are printed side by side so a disagreement is visible\n"
        "- not a fix: the patches are proven against the real files but the shared faces are left\n"
        "  untouched until the contention window closes\n"
        "- not a claim that the cash panel is fine: it is two sessions behind, and the honest\n"
        "  number is the one this face prints, not the board's\n\n"
        "Reproduce: `python scripts/block_red_triage.py` (writes this block), `--check`\n"
        "(re-derive and compare), `--selftest` (offline legs).\n")
    text = head + block + tail
    old = None
    if os.path.exists(DOC):
        with io.open(DOC, encoding="utf-8") as f:
            old = f.read()
    if old and BEGIN in old and END in old:
        text = old.split(BEGIN, 1)[0] + block + old.split(END, 1)[1]
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def check_only():
    if not os.path.exists(OUT) or not os.path.exists(DOC):
        print("CHECK FAILED face or doc missing")
        return 3
    with io.open(OUT, encoding="utf-8") as f:
        p = json.load(f)
    with io.open(DOC, encoding="utf-8") as f:
        text = f.read()
    if BEGIN not in text or END not in text:
        print("CHECK FAILED doc has no rendered block")
        return 3
    block = text.split(BEGIN, 1)[1].split(END, 1)[0]

    # drift = the inputs moved under the published face (r1934 vocabulary)
    now = dt.datetime.now().astimezone()
    calendar = load_calendar()
    modal, _, nfiles = modal_bar(os.path.join(ROOT, "data", "repo_daily"))
    horizon = complete_horizon(now.date(), now, calendar) if calendar else None
    with io.open(BANK, encoding="utf-8") as f:
        bank = json.load(f)
    drift = []
    if str(modal) != str(p["cash_panel"]["modal_bar"]):
        drift.append("cash panel bar %s != face %s" % (modal, p["cash_panel"]["modal_bar"]))
    if horizon and str(horizon) != str(p["cash_panel"]["horizon"]):
        drift.append("complete horizon %s != face %s" % (horizon, p["cash_panel"]["horizon"]))
    if claimable_true(bank) != p["board"]["bank_claimable"]:
        drift.append("bank claimable %d != face %d" % (claimable_true(bank), p["board"]["bank_claimable"]))
    if nfiles != p["cash_panel"]["files"]:
        drift.append("cash panel files %d != face %d" % (nfiles, p["cash_panel"]["files"]))
    if drift:
        print("STALE STALE_FACE_INPUTS_MOVED " + "; ".join(drift) + " -- re-run block_red_triage.py")
        return 3

    if str(p["board"]["red"]) not in block:
        print("CHECK FAILED doc block does not print the red count %s" % p["board"]["red"])
        return 3
    if p["board"]["line_state_honest"] not in block:
        print("CHECK FAILED doc block does not print the honest line state")
        return 3
    print("CHECK OK %d red rows re-derived · %s · honest line state %s"
          % (p["board"]["red"], json.dumps(p["class_counts"], ensure_ascii=False),
             p["board"]["line_state_honest"]))
    return 0


# ---------------------------------------------------------------------------------------
# offline selftest
# ---------------------------------------------------------------------------------------
def selftest():
    cases = []

    def leg(name, fn):
        try:
            fn()
            cases.append((name, True, ""))
        except AssertionError as e:
            cases.append((name, False, str(e)))

    # --- calendar / lag arithmetic -----------------------------------------------------
    def t_parse_iso():
        assert parse_date("2026-11-24,1.2,1.3") == dt.date(2026, 11, 24)

    def t_parse_bom_slash():
        assert parse_date("\ufeff2026/11/24,1,2") == dt.date(2026, 11, 24)

    def t_parse_blank():
        assert parse_date("") is None and parse_date("date,open") is None

    def t_board_reference_weekday():
        # Wednesday -> itself: the board counts today, which has no bar yet
        assert board_reference(dt.date(2026, 11, 25)) == dt.date(2026, 11, 25)

    def t_board_reference_weekend():
        assert board_reference(dt.date(2026, 11, 22)) == dt.date(2026, 11, 20)

    SESS = {dt.date(2026, 11, d) for d in (18, 19, 20, 23, 24, 25)}

    def t_horizon_before_close():
        # 03:20 on 11-25: today's bar does not exist yet
        assert complete_horizon(dt.date(2026, 11, 25), dt.datetime(2026, 11, 25, 3, 20), SESS) \
            == dt.date(2026, 11, 24)

    def t_horizon_after_close():
        assert complete_horizon(dt.date(2026, 11, 25), dt.datetime(2026, 11, 25, 16, 0), SESS) \
            == dt.date(2026, 11, 25)

    def t_horizon_skips_holiday():
        # 11-26 is not a session: the horizon must walk back to 11-25
        assert complete_horizon(dt.date(2026, 11, 26), dt.datetime(2026, 11, 26, 9, 0), SESS) \
            == dt.date(2026, 11, 25)

    def t_sessions_two():
        assert sessions_between(dt.date(2026, 11, 20), dt.date(2026, 11, 24), SESS) == 2

    def t_sessions_zero_when_future():
        assert sessions_between(dt.date(2026, 11, 24), dt.date(2026, 11, 20), SESS) == 0

    # --- supply vocabulary -------------------------------------------------------------
    def t_reader_misses_queued():
        bank = {"items": [{"status": "queued"}] * 18 + [{"status": "blocked"}] * 2}
        assert claimable_under_reader(bank) == 0
        assert claimable_true(bank) == 18

    def t_reader_sees_open():
        bank = {"items": [{"status": "open"}, {"status": "done"}]}
        assert claimable_under_reader(bank) == 1 == claimable_true(bank)

    def t_blocked_is_not_work():
        assert claimable_true({"items": [{"status": "blocked"}]}) == 0

    def t_vocab_flip_changes_colour():
        # the same four facts, two spellings, two colours
        before = {"items": [{"status": "open"}] * 4}
        after = {"items": [{"status": "queued"}] * 4}
        assert claimable_under_reader(before) == 4 and claimable_under_reader(after) == 0
        assert claimable_true(before) == claimable_true(after) == 4

    # --- ingest provenance -------------------------------------------------------------
    def _lanes(n, same=True):
        out = {}
        for i in range(n):
            out["l%d" % i] = {"file_delta": 0, "byte_delta": 0,
                              "theirs": {"modified": "T"}, "ours": {"modified": "T" if same else "U"}}
        return out

    def t_self_diff_untrusted():
        d = {"theirs": {"machine": "HOST", "generated": "G"}, "ours": {"machine": "HOST", "generated": "G"},
             "lanes": _lanes(3), "verdict": "COMPLETE"}
        r = ingest_sides_distinct(d)
        assert r["trustworthy"] is False and r["identical_lanes"] == 3 and r["same_generated"] is True

    def t_two_machines_trusted():
        d = {"theirs": {"machine": "bm-a", "generated": "G1"}, "ours": {"machine": "bm-c", "generated": "G2"},
             "lanes": _lanes(3, same=False), "verdict": "COMPLETE"}
        assert ingest_sides_distinct(d)["trustworthy"] is True

    def t_two_machines_one_lane_differs():
        lanes = _lanes(3)                      # two lanes identical, one moved
        lanes["l0"] = {"file_delta": 2, "byte_delta": 10,
                       "theirs": {"modified": "T"}, "ours": {"modified": "U"}}
        d = {"theirs": {"machine": "bm-a", "generated": "G1"}, "ours": {"machine": "bm-c", "generated": "G2"},
             "lanes": lanes, "verdict": "GAPS"}
        r = ingest_sides_distinct(d)
        assert r["trustworthy"] is True and r["identical_lanes"] == 2, r

    def t_empty_diff_untrusted():
        assert ingest_sides_distinct({})["trustworthy"] is False

    # --- classification contract (the three rows this round) ----------------------------
    def t_class_false_red_reader():
        bank = {"items": [{"status": "queued"}] * 3}
        ctx = {"bank": bank, "queue_pending": 0, "diff": {}, "cash": {}}
        row = {"id": "W1_supply", "status": "RED", "detail": "no open question left"}
        r = triage_row(row, {}, ctx)
        assert r["class"] == "FALSE_RED_READER", r["class"]
        assert r["true_state"]["row_would_be"] == "GREEN"

    def t_class_real_when_bank_empty():
        ctx = {"bank": {"items": [{"status": "blocked"}]}, "queue_pending": 0, "diff": {}, "cash": {}}
        row = {"id": "W1_supply", "status": "RED", "detail": "no open question left"}
        assert triage_row(row, {}, ctx)["class"] == "REAL"

    def t_class_ingest():
        d = {"theirs": {"machine": "HOST", "generated": "G"}, "ours": {"machine": "HOST", "generated": "G"},
             "lanes": _lanes(2), "verdict": "COMPLETE"}
        r = triage_row({"id": "G6_ingest", "status": "RED", "detail": "self-diff"},
                       {}, {"bank": {}, "queue_pending": 0, "diff": ingest_sides_distinct(d), "cash": {}})
        assert r["class"] == "FALSE_GREEN_PRODUCER" and r["true_state"]["handover_measured"] is False

    def t_class_cash_uninformative():
        cash = {"modal_bar": "2026-11-20", "files": 11, "hist": {}, "allowance_days": 4,
                "printed_lag": 5, "honest_lag": 4, "horizon": "2026-11-24", "sessions": 2}
        r = triage_row({"id": "D6_cash_rate", "status": "RED", "detail": "5d behind"},
                       {}, {"bank": {}, "queue_pending": 0, "diff": {}, "cash": cash})
        assert r["class"] == "UNINFORMATIVE", r["class"]
        # the killer: the honest reference passes the 4-day allowance while 2 sessions are missing
        assert r["true_state"]["row_would_be_under_honest_reference"] == "GREEN"
        assert r["true_state"]["row_would_be_under_sessions"] == "RED"

    def t_class_cash_real():
        # six sessions of a nine-day gap: beyond the allowance even on the honest reference
        cash = {"modal_bar": "2026-11-13", "files": 11, "hist": {}, "allowance_days": 4,
                "printed_lag": 12, "honest_lag": 11, "horizon": "2026-11-24", "sessions": 7}
        r = triage_row({"id": "D6_cash_rate", "status": "RED", "detail": "12d behind"},
                       {}, {"bank": {}, "queue_pending": 0, "diff": {}, "cash": cash})
        assert r["class"] == "REAL", r["class"]

    def t_class_cash_drift():
        # panel current, board still red -> the face is older than the data
        cash = {"modal_bar": "2026-11-24", "files": 11, "hist": {}, "allowance_days": 4,
                "printed_lag": 1, "honest_lag": 0, "horizon": "2026-11-24", "sessions": 0}
        r = triage_row({"id": "D6_cash_rate", "status": "RED", "detail": "5d behind"},
                       {}, {"bank": {}, "queue_pending": 0, "diff": {}, "cash": cash})
        assert r["class"] == "DRIFT", r["class"]

    def t_line_state_honest_busy():
        # recompute the honest label the way build() does, from the same three facts
        def honest(pend, claimable, real):
            return "BUSY" if (pend or claimable) else ("STARVING" if real else "LEGIT_IDLE")
        assert honest(0, 18, ["D6_cash_rate"]) == "BUSY"
        assert honest(0, 0, ["D6_cash_rate"]) == "STARVING"
        assert honest(0, 0, []) == "LEGIT_IDLE"

    legs = [
        ("csv first field parses as an ISO date", t_parse_iso),
        ("BOM and slash dates parse", t_parse_bom_slash),
        ("blank and header rows have no date", t_parse_blank),
        ("board reference on a weekday is today", t_board_reference_weekday),
        ("board reference on a weekend is Friday", t_board_reference_weekend),
        ("before 15:30 today's bar does not exist", t_horizon_before_close),
        ("after 15:30 it does", t_horizon_after_close),
        ("the horizon skips a non-session", t_horizon_skips_holiday),
        ("two sessions between Friday and Tuesday", t_sessions_two),
        ("a backwards range has no sessions", t_sessions_zero_when_future),
        ("shipped reader counts zero on a queued bank", t_reader_misses_queued),
        ("shipped reader counts open", t_reader_sees_open),
        ("blocked is not claimable work", t_blocked_is_not_work),
        ("same facts, two spellings, two colours", t_vocab_flip_changes_colour),
        ("a self-diff is untrusted", t_self_diff_untrusted),
        ("two machines with different lanes are trusted", t_two_machines_trusted),
        ("two machines with one differing lane stay trusted", t_two_machines_one_lane_differs),
        ("an empty diff is untrusted", t_empty_diff_untrusted),
        ("a queued bank classifies as a reader false red", t_class_false_red_reader),
        ("an all-blocked bank stays a real red", t_class_real_when_bank_empty),
        ("a self-diff classifies as a producer false green", t_class_ingest),
        ("the cash row classifies as uninformative", t_class_cash_uninformative),
        ("a nine-day cash gap is a real red", t_class_cash_real),
        ("a current cash panel under a red row is drift", t_class_cash_drift),
        ("the honest line state counts the bank", t_line_state_honest_busy),
    ]
    for n, f in legs:
        leg(n, f)
    bad = [c for c in cases if not c[1]]
    for n, ok, why in cases:
        print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", n, "" if ok else " | " + why))
    print("%d/%d legs pass" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


def main():
    p = build()
    b = p["board"]
    print("BLOCK-RED-TRIAGE %s · board %d rows / %d red · classes %s"
          % (p["generated"], b["rows"], b["red"], json.dumps(p["class_counts"], ensure_ascii=False)))
    for r in p["reds"]:
        print("  %-14s %-22s %s" % (r["id"], r["class"], r["proof"]))
    print("  real gap(s): %s · false red(s): %s · untrusted verdict(s): %s · line state %s -> %s"
          % (", ".join(p["real_gaps"]) or "none", ", ".join(p["false_reds"]) or "none",
             ", ".join(p["untrusted_verdicts"]) or "none",
             b["line_state_printed"], b["line_state_honest"]))
    print("  face -> results/block_red_triage.json ; doc -> research/BLOCK_RED_TRIAGE.md")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(selftest())
    if arg == "--check":
        sys.exit(check_only())
    sys.exit(main())
