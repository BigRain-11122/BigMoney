"""A face can be priced on the same bar as its input and still have read the old one.

Two rounds on 2026-11-12 paid for this twice. r1589: the chain ran
`etf_book_next_decision` after a rebase had swapped the code under its writer, so it
answered from `etf_book_rebalance_permission.json` written by the *previous* code and
the leg went red as `AGREE != DISAGREE`. r1590: `etf_book_cut_order_gap` had priced
itself at 19:56, the permission face was rewritten at 20:11, and the gap face kept
carrying a `decision_date` from the world before the rewrite.

Every existing freshness gate is blind to this. They key on the *business* bar
(`evidence_cutoff`, `as_of`, `bar`) -- and both faces honestly say `2026-11-12`. What
differs is the order in which they were produced. So the check has to compare the
producers' own wall clock, which in turn means surviving four spellings that this
repo actually emits today:

    2026-11-12T20:11:52+0800     (etf_book_rebalance_permission.json)
    2026-11-12T20:28:21          (etf_book_swap_freshness.json)
    2026-11-12 19:54:18          (live_book_section_bars.json)
    <absent>                     (etf_book_exec_delta.json)

A face that cannot be read is NOT fresh. Missing field, missing file and unparseable
stamp are all reported as UNREADABLE, because "I could not check" and "I checked and
it is fine" are the two answers that must never be printed by the same word (r98,
E318 family).

Usage:
    python Tools/face_input_staleness.py run        # write results/face_input_staleness.json
    python Tools/face_input_staleness.py selftest

Exit codes: 0 clean, 1 at least one STALE_INPUT_MOVED, 2 mechanism failure.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys
import tempfile

OUT = "results/face_input_staleness.json"
LOCAL_TZ = _dt.timezone(_dt.timedelta(hours=8))

# Each pair is justified by a producer that reads the input by path. The field names
# differ per face, so they are declared rather than guessed: a wrong field would read
# as UNREADABLE, not as a false FRESH.
REGISTRY = [
    {
        "derived": "results/etf_book_cut_order_gap.json",
        "derived_field": "generated",
        "inputs": [
            {"path": "results/etf_book_rebalance_permission.json", "field": "generated"},
        ],
        "why": "r1590: priced at 19:56, permission rewritten at 20:11, gap kept the old decision date",
    },
    {
        # r1597: r1596's third smoke red was not a count mismatch -- the leg ran while the
        # ticket was still the previous generation, so it compared today's ledger against
        # yesterday's sheet and called the difference a defect. A sheet must be written after
        # the ledger run it quotes; that is a wall-clock fact, and now it is one this face can
        # state. The ledger keeps one entry per advance, so the last run's `ts` is the stamp.
        "derived": "results/etf_book_order/latest.json",
        "derived_field": "generated",
        "inputs": [
            {"path": "results/etf_book_forward/LEDGER.json", "field": "runs.-1.ts"},
        ],
        "why": "r1596: the sheet quotes the ledger's bar and k; written before the ledger's last run it prices the previous world",
    },
    {
        # r1889: the ticket prices the executed account off results/etf_book_positions.json
        # (scripts/etf_book_order.py, POSITIONS_FACE) and embeds that snapshot. The positions
        # face carries no wall clock of its own, so the honest "when did this book move" is the
        # ledger row it upserts -- a content stamp that survives a rebase, where a file mtime
        # would reset on every checkout and manufacture a permanent STALE.
        #
        # Why this pair earns a line: when the ledger row is written after the ticket, the two
        # faces simply hold different numbers, and every content leg that compares them (base
        # gap vs executable delta, printed rows vs the book) reports a disagreement. Nothing in
        # those legs can tell "the writer was not run again" from "the writer got it wrong", so
        # the reader is handed the expensive reading. This face answers it with a clock.
        "derived": "results/etf_book_order/latest.json",
        "derived_field": "generated",
        "inputs": [
            {"path": "results/etf_book_positions/LEDGER.json", "field": "rows.-1.written_ts"},
        ],
        "why": "r1889: the ticket embeds the positions face; a ledger row written after the ticket is a missed run, not a content defect",
    },
]

# r1889: a wall-clock inversion has two readings and they cost very different amounts of
# time. "The producer was not run again" is a rerun; "the producer printed the wrong number"
# is a defect hunt. The verdict alone (STALE_INPUT_MOVED) never said which one, so the
# sentence below is what keeps the cheap reading from being lost.
MISSING_RUN = "MISSING_RUN"


def missing_run_sentence(derived, derived_stamp, input_path, input_stamp, lag_sec):
    """The plain-words reason a pair is stale: one face is a generation behind its input."""
    return ("少跑一趟：%s 写于 %s，而 %s 在它之后 %.0f 秒才写（%s）——两边数字对不上不是"
            "内容不一致，是拿面没有在输入之后重跑一趟"
            % (derived, derived_stamp, input_path, float(lag_sec),
               input_stamp))


def reader_line(derived, root=".", face_path=None):
    """What a published page may print about one derived face's inputs (r1890).

    Five states, and they are not interchangeable (r98): a page that could not read the
    clock may not print "fine", and a page whose pair was never registered may not print
    "fine" either -- that is the whole difference between "checked" and "not checked".
    The caller always prints the face's own `generated`, so a stale copy of this face
    cannot be read as a statement about right now (r1781).
    """
    path = os.path.join(root, face_path or OUT)
    base = {"derived": derived, "sentence": "", "generated": None, "lag_sec": None}
    if not os.path.exists(path):
        return dict(base, state="FACE_MISSING")
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception:
        return dict(base, state="FACE_UNREADABLE")
    gen = doc.get("generated")
    matches = [p for p in (doc.get("pairs") or []) if p.get("derived") == derived]
    if not matches:
        return dict(base, state="NOT_COMPARED", generated=gen)
    # r1890: one sheet can be priced off more than one face (the ticket reads both the
    # forward ledger and the positions ledger), so answering from the first matching pair
    # would let a fresh sibling hide a missed run -- the reader is told about ALL of them.
    stale = [p for p in matches if p.get("verdict") == "STALE_INPUT_MOVED"]
    if stale:
        lag = None
        for pair in stale:
            for row in pair.get("inputs") or []:
                if row.get("reading") == MISSING_RUN and row.get("lag_sec") is not None:
                    lag = row["lag_sec"] if lag is None else max(lag, row["lag_sec"])
        said = " ".join(p.get("sentence") for p in stale if p.get("sentence"))
        return dict(base, state=MISSING_RUN, generated=gen, lag_sec=lag, sentence=said,
                    pairs_compared=len(matches), pairs_stale=len(stale))
    unread = [p for p in matches if p.get("verdict") == "UNREADABLE"]
    if unread:
        return dict(base, state="UNREADABLE", generated=gen,
                    pairs_compared=len(matches))
    return dict(base, state="FRESH", generated=gen, pairs_compared=len(matches))


def parse_ts(text):
    """Return an aware datetime or None. Naive stamps are read as this machine's zone."""
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    # 2026-11-12T20:11:52+0800 -> +08:00 ; datetime can parse +HH:MM but not +HHMM
    if len(s) >= 5 and s[-5] in "+-" and s[-4:].isdigit():
        s = s[:-5] + s[-5:-2] + ":" + s[-2:]
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
        try:
            v = _dt.datetime.strptime(s, fmt)
        except ValueError:
            continue
        return v if v.tzinfo else v.replace(tzinfo=LOCAL_TZ)
    # %z also accepts 'Z'-style offsets once normalised; try the general ISO path last
    try:
        v = _dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return v if v.tzinfo else v.replace(tzinfo=LOCAL_TZ)


_MISS = object()


def dig(doc, field):
    """Walk a dotted path ('runs.-1.ts'), returning _MISS when any step is absent.

    Not every published stamp sits at the top of its file: a ledger records one `runs`
    entry per advance, and the only honest "when did this book last move" is the last
    entry's `ts`. Reading the newest entry is the whole point, so a list index is allowed
    to be negative; anything else that is not a mapping key is simply absent.
    """
    cur = doc
    for step in str(field).split("."):
        if isinstance(cur, list):
            try:
                idx = int(step)
                if idx < 0:
                    idx += len(cur)
                if idx < 0 or idx >= len(cur):
                    return _MISS
                cur = cur[idx]
            except (TypeError, ValueError):
                return _MISS
        elif isinstance(cur, dict):
            if step not in cur:
                return _MISS
            cur = cur[step]
        else:
            return _MISS
    return cur


def read_stamp(path, field, root="."):
    """(datetime|None, reason). reason is '' only when a stamp was actually read."""
    full = os.path.join(root, path)
    if not os.path.exists(full):
        return None, "file_missing"
    try:
        with open(full, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception:
        return None, "unreadable_json"
    if not isinstance(doc, dict):
        return None, "not_an_object"
    raw = dig(doc, field)
    if raw is _MISS:
        return None, "field_absent:%s" % field
    v = parse_ts(raw)
    if v is None:
        return None, "unparseable_stamp"
    return v, ""


def judge_pair(pair, root="."):
    derived = pair["derived"]
    d_ts, d_reason = read_stamp(derived, pair["derived_field"], root)
    rows = []
    worst = "FRESH"
    sentences = []
    for inp in pair["inputs"]:
        i_ts, i_reason = read_stamp(inp["path"], inp["field"], root)
        row = {
            "input": inp["path"],
            "input_field": inp["field"],
            "input_stamp": i_ts.isoformat() if i_ts else None,
            "input_reason": i_reason,
        }
        if d_ts is None or i_ts is None:
            row["verdict"] = "UNREADABLE"
            if worst == "FRESH":
                worst = "UNREADABLE"
        elif i_ts > d_ts:
            row["verdict"] = "STALE_INPUT_MOVED"
            row["lag_sec"] = round((i_ts - d_ts).total_seconds(), 1)
            worst = "STALE_INPUT_MOVED"
            # r1889: name the cheap reading next to the expensive one.
            row["reading"] = MISSING_RUN
            row["reading_sentence"] = missing_run_sentence(
                derived, d_ts.isoformat(), inp["path"], i_ts.isoformat(), row["lag_sec"])
            sentences.append(row["reading_sentence"])
        else:
            row["verdict"] = "FRESH"
            row["lag_sec"] = round((i_ts - d_ts).total_seconds(), 1)
        rows.append(row)
    verdict = "UNREADABLE" if (d_ts is None and worst != "STALE_INPUT_MOVED") else worst
    return {
        "derived": derived,
        "derived_field": pair["derived_field"],
        "derived_stamp": d_ts.isoformat() if d_ts else None,
        "derived_reason": d_reason,
        "why": pair.get("why", ""),
        "verdict": verdict,
        # A reading is only printed when it was earned: FRESH has nothing to explain, and
        # UNREADABLE means the clock itself could not be read -- calling that a missed run
        # would be the r98 family (an unreadable face dressed as a known one).
        "reading": MISSING_RUN if verdict == "STALE_INPUT_MOVED" else None,
        "sentence": " ".join(sentences),
        "inputs": rows,
    }


def run(root=".", out=OUT):
    pairs = [judge_pair(p, root) for p in REGISTRY]
    stale = [p["derived"] for p in pairs if p["verdict"] == "STALE_INPUT_MOVED"]
    unread = [p["derived"] for p in pairs if p["verdict"] == "UNREADABLE"]
    # r1889: one line per stale pair, written so a reader does not have to decide whether
    # today's red means "rerun the writer" or "find the bug".
    missing = [{"derived": p["derived"],
                "input": r["input"],
                "lag_sec": r.get("lag_sec"),
                "sentence": r.get("reading_sentence") or ""}
               for p in pairs if p["verdict"] == "STALE_INPUT_MOVED"
               for r in p["inputs"] if r.get("reading") == MISSING_RUN]
    doc = {
        "face": "face_input_staleness",
        "generated": _dt.datetime.now(LOCAL_TZ).isoformat(timespec="seconds"),
        "compared": len(pairs),
        "stale": stale,
        "unreadable": unread,
        "missing_runs": missing,
        "pairs": pairs,
        "verdict": "STALE" if stale else ("UNREADABLE" if unread else "FRESH"),
        "law": "a face may quote the same bar as its input and still have been priced before that input was written",
    }
    if out:
        full = os.path.join(root, out)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
    return doc


# ---------------------------------------------------------------- selftest

def _fixture(tmp, name, payload):
    p = os.path.join(tmp, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    return name


def selftest():
    global REGISTRY
    checks = []

    def ck(label, got, want):
        checks.append((label, got == want, got, want))

    # stamp spellings this repo actually emits
    ck("parse +0800 offset", parse_ts("2026-11-12T20:11:52+0800").utcoffset().total_seconds(), 28800)
    ck("parse bare T", parse_ts("2026-11-12T20:28:21").hour, 20)
    ck("parse space separator", parse_ts("2026-11-12 19:54:18").minute, 54)
    ck("bare and offset compare equal", parse_ts("2026-11-12T20:00:00") == parse_ts("2026-11-12T20:00:00+0800"), True)
    ck("offset spelled +08:00 compares equal", parse_ts("2026-11-12T20:00:00+08:00") == parse_ts("2026-11-12T20:00:00+0800"), True)
    ck("garbage is not a stamp", parse_ts("yesterday"), None)
    ck("empty is not a stamp", parse_ts(""), None)
    ck("absent is not a stamp", parse_ts(None), None)

    # r1597: a stamp can live inside the last entry of a list (the ledger's runs), and the
    # negative index is the only way to name "the newest advance" without reading a length.
    ck("dotted path reaches into the last list entry",
       dig({"runs": [{"ts": "a"}, {"ts": "b"}]}, "runs.-1.ts"), "b")
    ck("positive index works too", dig({"runs": [{"ts": "a"}, {"ts": "b"}]}, "runs.0.ts"), "a")
    ck("index past the end is absent", dig({"runs": [{"ts": "a"}]}, "runs.4.ts") is _MISS, True)
    ck("negative index past the start is absent", dig({"runs": [{"ts": "a"}]}, "runs.-4.ts") is _MISS, True)
    ck("walking into a scalar is absent", dig({"runs": "nope"}, "runs.-1.ts") is _MISS, True)
    ck("missing top-level key is absent", dig({}, "runs.-1.ts") is _MISS, True)

    # r1889: the round's own registration is asserted against REGISTRY, not trusted. Delete
    # the entry and this goes red, so the guard cannot shrink silently (r1282 family: a
    # mechanism with no leg on its own presence).
    _pairs = {(p["derived"], i["path"]) for p in REGISTRY for i in p["inputs"]}
    ck("the ticket's positions edge is registered",
       ("results/etf_book_order/latest.json",
        "results/etf_book_positions/LEDGER.json") in _pairs,
       True)

    with tempfile.TemporaryDirectory() as tmp:
        p = {
            "derived": _fixture(tmp, "d.json", {"generated": "2026-11-12T19:56:00+0800"}),
            "derived_field": "generated",
            "inputs": [{"path": _fixture(tmp, "i.json", {"generated": "2026-11-12T20:11:52+0800"}), "field": "generated"}],
        }
        r = judge_pair(p, tmp)
        ck("input written after derived is STALE", r["verdict"], "STALE_INPUT_MOVED")
        ck("staleness is reported in seconds", r["inputs"][0]["lag_sec"], 952.0)

        p2 = dict(p)
        p2["inputs"] = [{"path": _fixture(tmp, "i2.json", {"generated": "2026-11-12 19:00:00"}), "field": "generated"}]
        ck("derived after input is FRESH", judge_pair(p2, tmp)["verdict"], "FRESH")

        p3 = dict(p)
        p3["inputs"] = [{"path": _fixture(tmp, "i3.json", {"generated": "2026-11-12T19:56:00+0800"}), "field": "generated"}]
        ck("equal stamps are FRESH (not stale by construction)", judge_pair(p3, tmp)["verdict"], "FRESH")

        p4 = dict(p)
        p4["inputs"] = [{"path": _fixture(tmp, "i4.json", {"bar": "2026-11-12"}), "field": "generated"}]
        r4 = judge_pair(p4, tmp)
        ck("missing field is UNREADABLE, never FRESH", r4["verdict"], "UNREADABLE")
        ck("missing field names the field", r4["inputs"][0]["input_reason"], "field_absent:generated")

        # r1597: the live shape -- a sheet priced before the ledger's last advance. The last
        # run is the only run that matters, so the leg must read the tail, not the head.
        p_led = {
            "derived": _fixture(tmp, "sheet.json", {"generated": "2026-11-12T19:56:00+0800"}),
            "derived_field": "generated",
            "inputs": [{"path": _fixture(tmp, "led.json", {"runs": [
                {"ts": "2026-11-12T15:58:15+0800"}, {"ts": "2026-11-12T20:11:52+0800"}]}),
                "field": "runs.-1.ts"}],
        }
        ck("a sheet older than the ledger's last advance is STALE",
           judge_pair(p_led, tmp)["verdict"], "STALE_INPUT_MOVED")
        ck("the leg reads the tail, not the head",
           judge_pair(p_led, tmp)["inputs"][0]["lag_sec"], 952.0)
        p_led2 = dict(p_led)
        p_led2["derived"] = _fixture(tmp, "sheet2.json", {"generated": "2026-11-12T23:41:05+0800"})
        ck("a sheet written after the last advance is FRESH", judge_pair(p_led2, tmp)["verdict"], "FRESH")

        p5 = dict(p)
        p5["inputs"] = [{"path": "nope/absent.json", "field": "generated"}]
        ck("missing file is UNREADABLE", judge_pair(p5, tmp)["verdict"], "UNREADABLE")

        p6 = dict(p)
        p6["inputs"] = [{"path": _fixture(tmp, "i6.json", {"generated": "not a time"}), "field": "generated"}]
        ck("unparseable stamp is UNREADABLE", judge_pair(p6, tmp)["verdict"], "UNREADABLE")

        # a derived face with no stamp at all can never certify its inputs
        p7 = {"derived": _fixture(tmp, "d7.json", {"bar": "2026-11-12"}), "derived_field": "generated",
              "inputs": [{"path": _fixture(tmp, "i7.json", {"generated": "2026-11-12T20:11:52+0800"}), "field": "generated"}]}
        r7 = judge_pair(p7, tmp)
        ck("stampless derived face is UNREADABLE", r7["verdict"], "UNREADABLE")
        ck("stampless derived face says why", r7["derived_reason"], "field_absent:generated")

        # a stale input outranks an unreadable sibling: the actionable half must survive
        p8 = dict(p)
        p8["inputs"] = [
            {"path": "nope/absent.json", "field": "generated"},
            {"path": _fixture(tmp, "i8.json", {"generated": "2026-11-12T21:00:00+0800"}), "field": "generated"},
        ]
        ck("one stale input outranks one unreadable", judge_pair(p8, tmp)["verdict"], "STALE_INPUT_MOVED")

        # run() must write the face and keep the two failure kinds apart
        saved = REGISTRY
        try:
            REGISTRY = [p, p5]
            doc = run(tmp, out="out/staleness.json")
            ck("run separates stale from unreadable", (doc["verdict"], len(doc["stale"]), len(doc["unreadable"])),
               ("STALE", 1, 1))
            ck("run writes its face", os.path.exists(os.path.join(tmp, "out", "staleness.json")), True)
            # r1889: the stale pair also lands in the rerun list, one line per inversion
            ck("run lists the missed run with its sentence",
               (len(doc["missing_runs"]), "少跑一趟" in (doc["missing_runs"][0]["sentence"] or "")),
               (1, True))
        finally:
            REGISTRY = saved

        # r1889: a ticket priced before the positions row is one writer that was not run
        # again -- not two faces that disagree. The verdict never said which; the reading
        # and its sentence are what keep the cheap reading from being lost.
        _tk = {"derived": _fixture(tmp, "tk.json", {"generated": "2026-11-20T22:39:30+08:00"}),
               "derived_field": "generated",
               "inputs": [{"path": _fixture(tmp, "pos_led.json", {"rows": [
                   {"written_ts": "2026-11-20T20:33:57+08:00"},
                   {"written_ts": "2026-11-20T23:10:00+08:00"}]}),
                   "field": "rows.-1.written_ts"}]}
        _rtk = judge_pair(_tk, tmp)
        ck("a ticket priced before the positions row is a missed run",
           _rtk["reading"], MISSING_RUN)
        ck("the missed run is said in words, not as a content defect",
           "少跑一趟" in (_rtk["sentence"] or ""), True)
        ck("the sentence names both faces",
           ("tk.json" in (_rtk["sentence"] or "")) and ("pos_led.json" in (_rtk["sentence"] or "")),
           True)
        _tk2 = dict(_tk)
        _tk2["derived"] = _fixture(tmp, "tk2.json", {"generated": "2026-11-21T01:00:00+08:00"})
        _r2 = judge_pair(_tk2, tmp)
        ck("a ticket written after the row earns no reading",
           (_r2["reading"], _r2["sentence"]), (None, ""))

        # r1890: a reader's page may only print what this face actually checked. Five
        # states, and the two "I could not look" ones must never read as FRESH (r98).
        _face = _fixture(tmp, "face/staleness.json", {
            "face": "face_input_staleness", "generated": "2026-11-21T00:30:00+08:00",
            "pairs": [
                {"derived": "results/etf_book_order/latest.json",
                 "verdict": "STALE_INPUT_MOVED", "sentence": "少跑一趟：票早于账面",
                 "inputs": [{"input": "results/etf_book_positions/LEDGER.json",
                             "reading": MISSING_RUN, "lag_sec": 7533.0}]},
                {"derived": "results/etf_book_cut_order_gap.json",
                 "verdict": "FRESH", "sentence": "", "inputs": []},
            ]})
        _rl = reader_line("results/etf_book_order/latest.json", tmp, _face)
        ck("reader line repeats the missed run for the ticket", _rl["state"], MISSING_RUN)
        ck("reader line carries the face's own clock", _rl["generated"],
           "2026-11-21T00:30:00+08:00")
        ck("reader line keeps the words", "少跑一趟" in _rl["sentence"], True)
        ck("reader line names the lag", _rl["lag_sec"], 7533.0)
        _rf = reader_line("results/etf_book_cut_order_gap.json", tmp, _face)
        ck("a fresh pair earns no reading but is still named",
           (_rf["state"], _rf["sentence"]), ("FRESH", ""))
        _rn = reader_line("results/not_registered.json", tmp, _face)
        ck("an unregistered pair is NOT_COMPARED, never fresh", _rn["state"], "NOT_COMPARED")
        _rm = reader_line("results/etf_book_order/latest.json", tmp, "face/absent.json")
        ck("a missing face is FACE_MISSING, never fresh", _rm["state"], "FACE_MISSING")

        # must-fail shape: the ticket is registered against TWO inputs, and answering
        # from the first matching pair would print FRESH here while the second pair's
        # ledger row is what actually moved (r1890).
        _face2 = _fixture(tmp, "face/two_pairs.json", {
            "face": "face_input_staleness", "generated": "2026-11-21T00:40:00+08:00",
            "pairs": [
                {"derived": "results/etf_book_order/latest.json", "verdict": "FRESH",
                 "sentence": "", "inputs": [
                     {"input": "results/etf_book_forward/LEDGER.json",
                      "reading": None, "lag_sec": -60.0}]},
                {"derived": "results/etf_book_order/latest.json",
                 "verdict": "STALE_INPUT_MOVED", "sentence": "少跑一趟：票早于持仓账",
                 "inputs": [{"input": "results/etf_book_positions/LEDGER.json",
                             "reading": MISSING_RUN, "lag_sec": 7533.0}]},
            ]})
        _r2p = reader_line("results/etf_book_order/latest.json", tmp, _face2)
        ck("a fresh first pair does not hide the second pair's missed run",
           (_r2p["state"], _r2p.get("pairs_stale"), _r2p.get("pairs_compared")),
           (MISSING_RUN, 1, 2))
        ck("the lag printed is the stale pair's, not the fresh sibling's",
           _r2p["lag_sec"], 7533.0)

    passed = sum(1 for c in checks if c[1])
    for label, ok, got, want in checks:
        if not ok:
            print("FAIL %-52s got=%r want=%r" % (label, got, want))
    print("selftest %d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        try:
            doc = run()
        except Exception as exc:  # mechanism failure must not look like a clean face
            print("MECHANISM_FAILURE %s: %s" % (type(exc).__name__, exc))
            return 2
        print("verdict=%s compared=%d stale=%d unreadable=%d -> %s"
              % (doc["verdict"], doc["compared"], len(doc["stale"]), len(doc["unreadable"]), OUT))
        for row in doc["pairs"]:
            if row["verdict"] != "FRESH":
                print("  %-14s %s" % (row["verdict"], row["derived"]))
        for row in doc["missing_runs"]:
            print("  %-14s %s <- %s (%.0fs behind)"
                  % (MISSING_RUN, row["derived"], row["input"], float(row["lag_sec"] or 0)))
        return 1 if doc["stale"] else 0
    print("usage: face_input_staleness.py [run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
