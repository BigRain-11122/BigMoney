"""ETF book -- who produces the swap section, and which bar is it supposed to be on?

The sheet's swap section reads ten faces. Three of them were frozen on 2026-11-06 while the
sheet said "today the spread is +8.67pp": the entry, the gap history and the trigger had no
producer in the chain at all -- they carried `check` legs, and a check can only prove a face
is self-consistent with the world it was built in. Every round the chain re-derived them
against the advanced panel, found them wrong, printed NONZERO and moved on (r1345 wrote that
trap down for three other legs; a gate that is permanently red on inherited state is the r1135
trap). Four sessions of a page quoting a stale spread is what that looks like at the bottom.

This face is the missing word: it names each leg's producer and the bar the official calendar
says that leg must be on, so `check` can say STALE (a refresh buys it) instead of
INCONSISTENT (a refresh would hide a bug), and `run` pays every producer in dependency order.

  * the bar-to-be is the official calendar's last accepted session (15:30 convention, the
    same one update_daily uses) -- never this chain's own panels, which is the r1286 trap;
  * a face that is ahead of the calendar is inconsistent, not stale: it was priced on a bar
    that does not exist yet, and re-running its producer would not make that true;
  * only faces that are behind get a producer paid, in the order the faces import each
    other, so one pass through the chain is enough.

Usage:
    python scripts/etf_book_swap_freshness.py run
    python scripts/etf_book_swap_freshness.py check
    python scripts/etf_book_swap_freshness.py selftest
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# r1532: `run` echoes each producer's last line, and a producer that writes UTF-8 puts a
# replacement char on a GBK console -- printing it raised UnicodeEncodeError inside the
# refresh and the caller saw "no face" instead of "healed". The project already reconfigures
# stdout for exactly this (r1371).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import exchange_calendar_audit as CA   # noqa: E402  (the official calendar owner)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_freshness.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_freshness.md")
PUBLISH = (OUT_JSON, OUT_MD)

# ---- the section, in dependency order (each face reads the ones above it) ----------------
# The bar field differs by authoring round: session (r1464/r1465/r1466), asof (r1467), bar
# (r1522+). The field is named here rather than guessed, so a face that renames it turns
# inconsistent instead of reading as fresh.
LEGS = [
    ("sibling_entry", "scripts/etf_book_sibling_entry.py",
     "results/etf_book_sibling_entry.json", "session"),
    ("sibling_gap", "scripts/etf_book_sibling_gap.py",
     "results/etf_book_sibling_gap.json", "session"),
    ("swap_trigger", "scripts/etf_book_swap_trigger.py",
     "results/etf_book_swap_trigger.json", "session"),
    ("swap_stack", "scripts/etf_book_swap_stack.py",
     "results/etf_book_swap_stack.json", "asof"),
    ("swap_toll", "scripts/etf_book_swap_toll.py",
     "results/etf_book_swap_toll.json", "bar"),
    ("toll_scope", "scripts/etf_book_toll_scope.py",
     "results/etf_book_toll_scope.json", "bar"),
    ("swap_convergence", "scripts/etf_book_swap_convergence.py",
     "results/etf_book_swap_convergence.json", "bar"),
    ("swap_effect", "scripts/etf_book_swap_effect.py",
     "results/etf_book_swap_effect.json", "bar"),
    ("swap_units", "scripts/etf_book_swap_units.py",
     "results/etf_book_swap_units.json", "bar"),
    ("swap_track", "scripts/etf_book_swap_track.py",
     "results/etf_book_swap_track.json", "bar"),
]

FRESH = "FRESH"
STALE = "STALE"
INCONSISTENT = "INCONSISTENT"

# r1287: three of these legs are not a machine's lane at all -- they are children of one
# snapshot directory (`data/etf_premium/snap/<session>.csv`), and that directory is fed by a
# lane another machine owns. "1 session behind" with no name on it is a red flag nobody can
# act on (r1159/r1266: an "I cannot certify this" verdict has to carry who was supposed to),
# so a stale row now says which file it waits for, when that file was last written, and which
# machine is allowed to write the next one.
SNAPSHOT_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
SNAPSHOT_LEGS = ("sibling_entry", "sibling_gap", "swap_trigger")
PREMIUM_COLLECTOR = os.path.join(ROOT, "scripts", "update_fund_premium.py")


def lane_owner_of(snapshot_dir=SNAPSHOT_DIR, collector=PREMIUM_COLLECTOR):
    """The machine allowed to write the next snapshot.

    Read out of the collector's own source instead of a second copy of the constant: an
    import here would pull a network collector into a bookkeeping leg. Returns "" when the
    constant cannot be read -- an unattributable lane stays unattributed, never guessed.
    """
    try:
        import ast
        with open(collector, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tgt = node.targets[0]
                if isinstance(tgt, ast.Name) and tgt.id == "LANE_OWNER":
                    val = getattr(node.value, "value", None)
                    return val if isinstance(val, str) else ""
    except (OSError, SyntaxError, ValueError):
        return ""
    return ""


def snapshot_waiting(exp, snapshot_dir=SNAPSHOT_DIR, collector=PREMIUM_COLLECTOR):
    """Name what the snapshot legs are waiting on: the missing file, the copy's newest, owner.

    `exp` is the session the official calendar says must be printed. Returns "" when the
    snapshot directory cannot be read -- absence of evidence is not a verdict.
    """
    try:
        names = sorted(n for n in os.listdir(snapshot_dir) if n.endswith(".csv"))
    except OSError:
        return ""
    newest = names[-1][:-4] if names else ""
    if not newest or (exp and newest >= exp):
        return ""
    path = os.path.join(snapshot_dir, names[-1])
    try:
        written = dt.datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="seconds")
    except OSError:
        written = "unknown mtime"
    owner = lane_owner_of(snapshot_dir, collector)
    if owner:
        who = "lane owner %s writes it; this copy cannot" % owner
    else:
        who = "lane owner unreadable"
    return ("waiting on %s (newest copy here: %s, written %s; %s)"
            % (os.path.join(os.path.relpath(snapshot_dir, ROOT).replace(os.sep, "/"),
                            "%s.csv" % exp).replace(os.sep, "/"),
               newest, written, who))


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def official_days(cal_path=None):
    """The official session list. Falling back to a panel would judge the calendar by itself."""
    return CA.load_calendar(cal_path or CA.CAL_PATH)


def expected_bar(days, now):
    """Last session whose bar must exist by `now` (15:30 convention, shared with update_daily)."""
    exp, _past = CA.expected_last_day(days, now)
    return exp


def lag_sessions(days, bar, expected):
    """How many official sessions sit between `bar` and `expected` (0 = on the bar)."""
    if not bar or not expected:
        return None
    if bar >= expected:
        return 0
    behind = [d for d in days if bar < d <= expected]
    return len(behind)


def assess(now=None, faces=None, days=None):
    """Judge every leg against the bar the calendar says it must be on.

    `faces` maps leg -> payload (a fixture seam); `days` overrides the calendar list.
    """
    now = now or dt.datetime.now()
    days = days if days is not None else official_days()
    exp = expected_bar(days, now)
    rows = []
    for leg, producer, face_path, field in LEGS:
        if faces is not None:
            payload = faces.get(leg, "MISSING")
        else:
            payload = _read_json(os.path.join(ROOT, face_path))
        if payload == "MISSING" or payload is None:
            rows.append({"leg": leg, "producer": producer, "face": face_path,
                         "field": field, "bar": None, "lag_sessions": None,
                         "status": STALE, "reason": "no face published"})
            continue
        bar = payload.get(field)
        if not bar:
            rows.append({"leg": leg, "producer": producer, "face": face_path,
                         "field": field, "bar": None, "lag_sessions": None,
                         "status": INCONSISTENT,
                         "reason": "face carries no %r field" % field})
            continue
        lag = lag_sessions(days, bar, exp)
        if bar > (exp or ""):
            status, reason = INCONSISTENT, "priced on %s, ahead of the calendar's %s" % (bar, exp)
        elif lag:
            status, reason = STALE, "%s session(s) behind the %s close" % (lag, exp)
        else:
            status, reason = FRESH, "on the %s close" % exp
        rows.append({"leg": leg, "producer": producer, "face": face_path, "field": field,
                     "bar": bar, "lag_sessions": lag, "status": status, "reason": reason})
        if status == STALE and leg in SNAPSHOT_LEGS and faces is None:
            waits = snapshot_waiting(exp)
            if waits:
                rows[-1]["waiting_on"] = waits
    stale = [r["leg"] for r in rows if r["status"] == STALE]
    inconsistent = [r["leg"] for r in rows if r["status"] == INCONSISTENT]
    payload = {
        "artifact": "etf_book_swap_freshness",
        "generated": now.isoformat(timespec="seconds"),
        "evidence_cutoff": exp,
        "calendar_source": os.path.relpath(CA.CAL_PATH, ROOT).replace(os.sep, "/"),
        "close_accept_time": CA.CLOSE_ACCEPT_TIME.strftime("%H:%M"),
        "legs": rows,
        "n_legs": len(rows),
        "stale_legs": stale,
        "inconsistent_legs": inconsistent,
        "verdict": (INCONSISTENT if inconsistent else (STALE if stale else FRESH)),
        "sentence": sentence(rows, exp, stale, inconsistent),
        "caveats": [
            "The bar-to-be comes from the official exchange calendar, never from this "
            "chain's own panels: a panel cannot say which session should already be printed "
            "(r1286).",
            "A face AHEAD of the calendar is not stale -- its producer would not make it "
            "true, so the chain must keep it red instead of paying a refresh (r1345).",
            "Freshness is not correctness: a face on the right bar can still be wrong, and "
            "each producer's own check is what refuses that.",
        ],
    }
    return payload


def sentence(rows, exp, stale, inconsistent):
    if inconsistent:
        return ("%s: %s priced on a bar the calendar does not have yet -- re-running the "
                "producer would not make it true." % (INCONSISTENT, ", ".join(inconsistent)))
    if stale:
        worst = max((r for r in rows if r["status"] == STALE),
                    key=lambda r: (r["lag_sessions"] or 0))
        text = ("STALE: %d of %d faces are older than the %s close -- worst %s on %s (%s)."
                % (len(stale), len(rows), exp, worst["leg"],
                   worst["bar"] or "no face", worst["reason"]))
        # r1287: a reader cannot act on "1 session behind"; name who can move it.
        waits = [r["waiting_on"] for r in rows if r.get("waiting_on")]
        if waits:
            text += " " + waits[0]
        return text
    return "Every one of the %d faces in the swap section is on the %s close." % (len(rows), exp)


def ticket_lines(face):
    """The sheet's own view of the ten faces it quotes (r1532).

    r1530 built this face to answer "is the swap section on today's bar?" and then nothing
    read it: the sheet's freshness section still only named the bar the *ticket* was priced
    on, so a reader took the section below it as same-day too. On 2026-11-11 the entry face
    was two sessions behind and the sheet still said `current`. The sheet now prints this,
    and the ten legs are listed only when they disagree with the calendar -- a block of ten
    green rows would just bury the one that is not.
    """
    head = "## 换票那一节的 10 个面各自在哪一天（r1532）"
    if not isinstance(face, dict) or not face.get("legs"):
        return [head, "",
                "- 新鲜度面不可读（`results/etf_book_swap_freshness.json`）——本单**无法证明**"
                "换票节的 10 个面与票面同一天，但也不因此判它们陈旧（缺输入禁读成没发生）。",
                ""]
    verdict = face.get("verdict")
    exp = face.get("evidence_cutoff") or "未知"
    out = [head,
           "- 该到位的 bar：**%s**（官方交易日历，收盘受理时点 %s）"
           % (exp, face.get("close_accept_time") or "-"),
           "- 判定：**%s**" % verdict]
    if verdict == FRESH:
        out += ["- %d 个面都停在 %s：这一节的数字与票面同一天。" % (face.get("n_legs") or 0, exp)]
    else:
        bad = [r for r in face.get("legs") or [] if r.get("status") != FRESH]
        worst = max(bad, key=lambda r: (r.get("lag_sessions") or 0))
        if verdict == STALE:
            where = "落后 %s 个交易日，刷新能救它" % (
                "?" if worst.get("lag_sessions") is None else worst.get("lag_sessions"))
        elif verdict == INCONSISTENT:
            # "0 sessions behind" would read as fine here: a face ahead of the calendar is
            # not behind, it is early, and no producer run can make that true (r1345).
            where = "在日历还没有的那一天，刷新救不了它"
        else:
            where = "面自己的判词是 %s" % verdict
        out += ["- **这 %d 个节印的不是 %s 的数**：最旧的是 %s（bar %s，%s）"
                % (len(bad), exp, worst.get("leg"), worst.get("bar") or "无面", where),
                "",
                "| 面 | bar | 落后（交易日） | 状态 | 原因 |",
                "|---|---|---|---|---|"]
        for r in bad:
            lag_cell = ("—" if r.get("status") == INCONSISTENT
                        else "—" if r.get("lag_sessions") is None else r.get("lag_sessions"))
            out.append("| %s | %s | %s | %s | %s |"
                       % (r.get("leg"), r.get("bar") or "—", lag_cell,
                          r.get("status"), r.get("reason")))
        out.append("")
        waits = [r for r in face.get("legs") or [] if r.get("waiting_on")]
        if waits:
            out.append("- 还在等谁：%s" % waits[0]["waiting_on"])
        out.append("- 修法：`python scripts/etf_book_swap_freshness.py run`（按依赖顺序付"
                   " 10 个生产者，然后重生成本单）；在这些面回到 %s 之前，上面这些节里的"
                   "数字不能当今天的读。" % exp)
    out += ["- 新鲜≠正确：同一个 bar 上的面也可能算错，那是各面自己的 `check` 管的事。", ""]
    return out


def render_md(face):
    L = ["# 换票这一节，每个面该停在哪根 bar（r1530）", "",
         face["sentence"], "",
         "- 该到位的 bar：**%s**（官方交易日历，收盘受理时点 %s）"
         % (face["evidence_cutoff"], face["close_accept_time"]),
         "- 判词：**%s**（陈旧 %d / 不一致 %d）"
         % (face["verdict"], len(face["stale_legs"]), len(face["inconsistent_legs"])), "",
         "| 面 | bar | 落后（交易日） | 状态 | 原因 | 生产者 |", "|---|---|---|---|---|---|"]
    for r in face["legs"]:
        L.append("| %s | %s | %s | %s | %s | `%s` |"
                 % (r["leg"], r["bar"] or "—", "—" if r["lag_sessions"] is None
                    else r["lag_sessions"], r["status"], r["reason"], r["producer"]))
    waits = [r for r in face["legs"] if r.get("waiting_on")]
    if waits:
        L += ["", "**这三条还在等谁**：" + waits[0]["waiting_on"]]
    L += ["", "## 为什么这张面存在", "",
          "票面写「今日价差」而入场/价差/触发三面停在四个交易日之前——它们在链里只有 "
          "`check` 没有 `run`，而 `check` 只能证明一个面与它被造出来的那个世界自洽。每轮"
          "链都能发现它们不对，打印 NONZERO 就往下走（r1345 为另外三条腿写过同一句话）。", "",
          "## 自证", ""]
    L += ["- " + c for c in face["caveats"]]
    return "\n".join(L) + "\n"


def _shim_in_paid(face):
    """A producer that is a `python -c ...` shim is a test fixture, never a real run (r1533)."""
    for row in face.get("paid") or []:
        cmd = row.get("cmd") or []
        if "-c" in cmd:
            return row.get("leg") or "?"
    return None


def write_out(face, out=None):
    """Publish to `out` = (json, md). `out` None means 'do not publish'.

    r1533: this used to have no path argument, so the selftest's injected producers wrote
    their fixtures straight over the published face -- the committed payload said
    'sibling_entry: its producer returned 7' with `-c import sys;sys.exit(7)` in `paid`,
    and every reader of the ticket's swap section would have believed it.
    """
    if out is None:
        print("[swap_freshness] not published (no destination given)")
        return False
    out_json, out_md = out
    if os.path.abspath(out_json) == os.path.abspath(OUT_JSON):
        shim = _shim_in_paid(face)
        if shim:
            raise RuntimeError("refusing to publish a test shim as the %s producer" % shim)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))
    return True


def _print_rows(face):
    for r in face["legs"]:
        print("  %-17s %-11s lag=%-4s %-12s %s"
              % (r["leg"], r["bar"] or "—",
                 "—" if r["lag_sessions"] is None else r["lag_sessions"],
                 r["status"], r["reason"]))


def check(now=None, faces=None, days=None):
    """The probe the chain pays a refresh from. STALE is repairable; INCONSISTENT is not."""
    face = assess(now=now, faces=faces, days=days)
    if not face["evidence_cutoff"]:
        print("[swap_freshness] cannot judge: the official calendar carries no completed "
              "session for %s" % face["generated"][:19])
        return 3
    _print_rows(face)
    if face["verdict"] == INCONSISTENT:
        print("[swap_freshness] INCONSISTENT: %s" % face["sentence"])
        return 1
    if face["verdict"] == STALE:
        print("[swap_freshness] %s" % face["sentence"])
        print("[swap_freshness] every leg above is stale, not wrong: pay its producer in "
              "dependency order (python scripts/etf_book_swap_freshness.py run)")
        return 2
    print("[swap_freshness] %s" % face["sentence"])
    return 0


def run(now=None, faces=None, days=None, producer_cmd=None, out=None):
    """Pay the producer of every stale leg, in dependency order, then judge again.

    `out` is where the result is published; None means 'publish to the two files under
    results/'. An injected `producer_cmd` (i.e. a test) publishes nothing unless it also
    passes `out` explicitly -- a fixture must never be able to land on the reader's face.
    """
    publish = PUBLISH if (out is None and producer_cmd is None) else out
    before = assess(now=now, faces=faces, days=days)
    if before["verdict"] == INCONSISTENT:
        write_out(before, publish)
        print("[swap_freshness] refusing to refresh: %s" % before["sentence"])
        return 1
    paid = []
    for r in before["legs"]:
        if r["status"] != STALE:
            continue
        cmd = producer_cmd(r) if producer_cmd else [sys.executable, r["producer"], "run"]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", cwd=ROOT, timeout=900)
            rc = p.returncode
            tail = (p.stdout or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            rc, tail = 124, ["TIMEOUT"]
        paid.append({"leg": r["leg"], "cmd": cmd[1:] if len(cmd) > 1 else cmd,
                     "rc": rc, "tail": tail[0][:200]})
        print("  %-17s producer rc=%s %s" % (r["leg"], rc, tail[0][:90]))
        if rc != 0:
            face = assess(now=now, faces=faces, days=days)
            face["paid"] = paid
            face["verdict"] = "PRODUCER_FAILED"
            face["sentence"] = ("%s: its producer returned %s and the face is still not on "
                                "the bar." % (r["leg"], rc))
            write_out(face, publish)
            print("[swap_freshness] %s" % face["sentence"])
            return 3
    after = assess(now=now, faces=faces, days=days)
    after["paid"] = paid
    write_out(after, publish)
    _print_rows(after)
    print("[swap_freshness] %s" % after["sentence"])
    if after["verdict"] == FRESH:
        print("[swap_freshness] refreshed %d leg(s); %d already on the bar"
              % (len(paid), len(after["legs"]) - len(paid)))
        return 0
    print("[swap_freshness] %s" % after["sentence"])
    return 3 if after["verdict"] == STALE else 1


SCEN = ["2026-11-05", "2026-11-06", "2026-11-09", "2026-11-10"]


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    days = SCEN
    # --- the bar-to-be is the calendar's job, and the 15:30 boundary is the one update_daily uses
    before = dt.datetime(2026, 11, 10, 9, 30)
    after = dt.datetime(2026, 11, 10, 16, 0)
    leg("L1 before 15:30 the session in progress is not expected yet",
        expected_bar(days, before) == "2026-11-09")
    leg("L2 after 15:30 today's close is expected", expected_bar(days, after) == "2026-11-10")
    leg("L3 a bar on the expected session has zero lag",
        lag_sessions(days, "2026-11-10", "2026-11-10") == 0)
    leg("L4 lag counts official sessions, not calendar days",
        lag_sessions(days, "2026-11-06", "2026-11-10") == 2
        and lag_sessions(days, "2026-11-05", "2026-11-10") == 3)
    leg("L5 a bar without a session gives None, not 0",
        lag_sessions(days, None, "2026-11-10") is None)

    # --- fresh / stale / inconsistent are three different words
    fresh = {l[0]: {l[3]: "2026-11-10"} for l in LEGS}
    face = assess(now=after, faces=fresh, days=days)
    leg("L6 all ten faces on the close is FRESH", face["verdict"] == FRESH
        and face["n_legs"] == len(LEGS) and not face["stale_legs"])
    prev = dict(fresh, sibling_entry={"session": "2026-11-06"})
    face = assess(now=after, faces=prev, days=days)
    leg("L7 one face four days back is STALE and named", face["verdict"] == STALE
        and face["stale_legs"] == ["sibling_entry"])
    leg("L8 a stale face carries its lag in sessions",
        face["legs"][0]["lag_sessions"] == 2)
    ahead = dict(fresh, swap_units={"bar": "2026-11-11"})
    face = assess(now=after, faces=ahead, days=days)
    leg("L9 a face ahead of the calendar is INCONSISTENT, not stale",
        face["verdict"] == INCONSISTENT and face["stale_legs"] == []
        and face["inconsistent_legs"] == ["swap_units"])
    missing = {k: v for k, v in fresh.items() if k != "swap_track"}
    face = assess(now=after, faces=missing, days=days)
    leg("L10 an unpublished face is stale (a producer can publish it)",
        face["verdict"] == STALE and "no face published" in face["legs"][-1]["reason"])
    wrongfield = dict(fresh, swap_stack={"bar": "2026-11-10"})
    face = assess(now=after, faces=wrongfield, days=days)
    leg("L11 a face without its declared bar field is inconsistent",
        face["verdict"] == INCONSISTENT)

    # --- the chain's contract: only the word "stale" buys a refresh (r1345)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc_stale = check(now=after, faces=prev, days=days)
    text_stale = buf.getvalue()
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc_inc = check(now=after, faces=ahead, days=days)
    text_inc = buf.getvalue()
    leg("L12 a stale probe exits 2 and says 'stale' (the refresh trigger)", rc_stale == 2
        and "stale" in text_stale.lower())
    leg("L13 an inconsistent probe exits 1 and never says 'stale' (no refresh paid)",
        rc_inc == 1 and "stale" not in text_inc.lower())
    leg("L14 a fresh probe exits 0", check(now=after, faces=fresh, days=days) == 0)

    # --- the refresh loop actually pays, in dependency order, and re-judges
    import tempfile
    calls = []
    state = {"faces": dict(prev)}

    def fake_producer(r):
        calls.append(r["leg"])
        state["faces"][r["leg"]] = {r["field"]: "2026-11-10"}
        return [sys.executable, "-c", "pass"]

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = run(now=after, faces=state["faces"], days=days, producer_cmd=fake_producer)
    leg("L15 a paid refresh leaves the section fresh", rc == 0 and calls == ["sibling_entry"])
    leg("L16 the refresh only pays the stale leg", len(calls) == 1)

    order = [l[0] for l in LEGS]
    leg("L17 the producer order is the dependency order, not the alphabet",
        order.index("sibling_entry") < order.index("sibling_gap") < order.index("swap_trigger")
        < order.index("swap_stack") < order.index("swap_toll") < order.index("swap_units"))

    def bad_producer(r):
        return [sys.executable, "-c", "import sys;sys.exit(7)"]

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc_bad = run(now=after, faces=dict(prev), days=days, producer_cmd=bad_producer)
    leg("L18 a failing producer is reported, not swallowed", rc_bad == 3)

    # --- r1533: a fixture walked over the published face, so a test run must publish nothing
    def _published():
        try:
            with open(OUT_JSON, "rb") as fh:
                return fh.read()
        except OSError:
            return None

    before_bytes = _published()
    buf = io.StringIO()
    with redirect_stdout(buf):
        run(now=after, faces=dict(prev), days=days, producer_cmd=fake_producer)
        run(now=after, faces=dict(prev), days=days, producer_cmd=bad_producer)
    leg("L24 a test-injected run publishes nothing -- the face under results/ is untouched",
        _published() == before_bytes)

    with tempfile.TemporaryDirectory() as td:
        tmp = (os.path.join(td, "face.json"), os.path.join(td, "face.md"))
        live = dict(prev)

        def gen(r):
            live[r["leg"]] = {r["field"]: "2026-11-10"}
            return [sys.executable, "-c", "pass"]

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc_tmp = run(now=after, faces=live, days=days, producer_cmd=gen, out=tmp)
        written = os.path.exists(tmp[0]) and os.path.exists(tmp[1])
        loaded = json.load(open(tmp[0], encoding="utf-8")) if written else {}
        leg("L25 an explicit destination is written and holds the same judgment",
            rc_tmp == 0 and written and loaded.get("verdict") == FRESH
            and _published() == before_bytes)

        shim_face = dict(assess(now=after, faces=fresh, days=days))
        shim_face["paid"] = [{"leg": "sibling_entry", "cmd": ["-c", "import sys;sys.exit(7)"],
                              "rc": 7, "tail": ""}]
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                write_out(shim_face, PUBLISH)
            refused = False
        except RuntimeError:
            refused = True
        leg("L26 a `-c` producer is a fixture and is refused at the published face",
            refused and _published() == before_bytes)

    # --- the calendar is the official one, never this chain's own panel
    leg("L19 the expected bar comes from the official exchange calendar",
        os.path.basename(CA.CAL_PATH) == "exchange_calendar.csv")

    # --- the sheet's view (r1532): ten green rows would bury the one that is not green
    fresh_face = assess(now=after, faces=fresh, days=days)
    stale_face = assess(now=after, faces=prev, days=days)
    txt = "\n".join(ticket_lines(fresh_face))
    leg("L20 a same-bar section prints one line and no leg table",
        "都停在 2026-11-10" in txt and "| 面 |" not in txt and FRESH in txt)
    txt = "\n".join(ticket_lines(stale_face))
    leg("L21 a stale section names the face, its bar and its lag -- and never says same-day",
        "sibling_entry" in txt and "2026-11-06" in txt and "落后 2 个交易日" in txt
        and "都停在" not in txt and "同一天" not in txt)
    txt = "\n".join(ticket_lines(None))
    leg("L22 an unreadable section says so and claims nothing",
        "无法证明" in txt and "都停在" not in txt and "| 面 |" not in txt)
    txt = "\n".join(ticket_lines(assess(now=after, faces=ahead, days=days)))
    leg("L23 a face ahead of the calendar is never called 'behind 0 sessions'",
        "落后 0 个交易日" not in txt and "刷新救不了它" in txt and INCONSISTENT in txt)

    # r1287: "1 session behind" has to name who can move it, and name nothing when it cannot
    with tempfile.TemporaryDirectory() as td:
        snapdir = os.path.join(td, "snap")
        os.makedirs(snapdir)
        p = os.path.join(snapdir, "2026-11-09.csv")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("code,price\n")
        coll = os.path.join(td, "collector.py")
        with open(coll, "w", encoding="utf-8") as fh:
            fh.write('LANE_OWNER = "bm-x"\n')
        waits = snapshot_waiting("2026-11-10", snapshot_dir=snapdir, collector=coll)
        leg("L27 a stale snapshot leg names the missing file, the newest copy and its writer",
            "2026-11-10.csv" in waits and "2026-11-09" in waits and "bm-x" in waits)
        leg("L28 the lane owner is read out of the collector's source, not a second copy",
            lane_owner_of(snapdir, coll) == "bm-x"
            and lane_owner_of(snapdir, os.path.join(td, "absent.py")) == "")
        leg("L29 an unreadable snapshot directory produces no sentence (never an invented one)",
            snapshot_waiting("2026-11-10", snapshot_dir=os.path.join(td, "nope")) == "")
        # a leg that is NOT a snapshot child gets no waiting sentence even when it is stale
        stale_rows = assess(now=after, faces=prev, days=days)["legs"]
        others = [r for r in stale_rows if r["leg"] == "swap_stack"]
        leg("L30 a stale leg with its own producer is not told to wait for a file",
            all("waiting_on" not in r for r in others))

    # r1533: this read `sum(1 for _, ok in legs)`, which counts every leg whatever its
    # verdict -- the suite printed its own [FAIL] lines and still said "N/N PASS" and rc 0.
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name)
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest" or args.selftest:
        return selftest()
    if args.cmd == "check" or args.check:
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
