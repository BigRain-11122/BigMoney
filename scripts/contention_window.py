"""How long is the write-contention window still open, and is the peer still writing?

Background
----------
`Tools/repo_write_contention.py` answers one question each round: is another host
writing this repo right now (rc3 CONTENTION).  It deliberately does *not* say how long
that lasts, so a line running against a peer that went quiet hours ago keeps declaring
"contention" round after round and can only land new files.  This face answers the
missing half:

  * who the peer is (pid, kind, age) and whether that process is still alive
  * when the peer last wrote a shared face, and therefore
  * the moment the lookback window closes on its own (`closes_at`)
  * how quiet the peer has been since its last write

It is **descriptive only**.  It never edits a shared face, never kills a process, and
never relaxes the law: a round that reads WINDOW_OPEN must still restrict itself to new
files.  What it changes is that the restriction now has an end time you can plan around.

Usage
-----
    python scripts/contention_window.py run       # derive + write page block
    python scripts/contention_window.py --check   # re-derive and compare (rc3 on drift)
    python scripts/contention_window.py --selftest

Verdicts
--------
    NO_PEER         no other host alive -> shared faces are free
    PEER_EXITED     the peer process is gone; the window is a leftover, not a live risk
    WINDOW_OPEN     peer alive and wrote inside the lookback -> new files only
    WINDOW_CLOSED   lookback elapsed since the peer's last write -> the window is over

A peer that is alive but has not written for longer than the lookback still yields
WINDOW_CLOSED: the window measures writes, not process lifetime.  When that happens the
line is told it may resume shared-face work *and* that the peer shell is still up, so a
sudden new write would reopen the window.
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
import time

PROBE = os.path.join("results", "_repo_write_contention.{mid}.json")
OUT = os.path.join("results", "contention_window.json")
PAGE = os.path.join("research", "CONTENTION_WINDOW.md")
BEGIN = "<!-- BEGIN contention_window -->"
END = "<!-- END contention_window -->"

SCHEMA = "contention-window/v1"


def _machine_id() -> str:
    try:
        with open(os.path.join("fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id") or "unknown"
    except Exception:
        return "unknown"


def _pid_alive(pid) -> bool:
    """Windows-safe liveness probe; never raises."""
    try:
        pid = int(pid)
    except Exception:
        return False
    if pid <= 0:
        return False
    try:
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        if not h:
            return False
        k32.CloseHandle(h)
        return True
    except Exception:
        # non-Windows fallback
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def _parse_ts(ts) -> float | None:
    if not ts:
        return None
    try:
        return time.mktime(time.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S"))
    except Exception:
        return None


def classify(probe: dict, now_epoch: float, pid_alive=_pid_alive) -> dict:
    """Pure function: probe payload -> window reading.  No disk, no clock of its own."""
    my_pid = probe.get("my_host_pid")
    lookback = float(probe.get("lookback_min") or 45.0)
    hosts = probe.get("hosts") or []
    peers = [h for h in hosts if h.get("pid") != my_pid]
    writes = probe.get("recent_writes") or []

    peer_last = None
    peer_last_path = None
    for w in writes:
        e = w.get("mtime_epoch")
        if e is None:
            e = _parse_ts(w.get("mtime"))
        if e is None:
            continue
        if peer_last is None or e > peer_last:
            peer_last = float(e)
            peer_last_path = w.get("path")

    alive_peers = [p for p in peers if pid_alive(p.get("pid"))]
    lookback_s = lookback * 60.0

    reading = {
        "schema": SCHEMA,
        "probed_at": probe.get("probed_at"),
        "lookback_min": lookback,
        "my_host_pid": my_pid,
        "peer_count": len(peers),
        "peer_alive_count": len(alive_peers),
        "peer_pids": [p.get("pid") for p in peers],
        "peer_alive_pids": [p.get("pid") for p in alive_peers],
        "peer_last_write": None,
        "peer_last_write_path": peer_last_path,
        "peer_quiet_min": None,
        "closes_at": None,
        "minutes_to_close": None,
        "source_probe": probe.get("probed_at"),
    }

    if not peers:
        reading["verdict"] = "NO_PEER"
        reading["why"] = "no other host is alive in this repo; shared faces are free"
        return reading

    if peer_last is None:
        # peers exist but none of the recent writes are attributable to them
        if alive_peers:
            reading["verdict"] = "WINDOW_OPEN"
            reading["why"] = ("%d peer host(s) alive and no attributable write inside the "
                              "lookback -- assume it may write at any moment" % len(alive_peers))
        else:
            reading["verdict"] = "PEER_EXITED"
            reading["why"] = "peer process(es) gone and no attributable write inside the lookback"
        return reading

    closes = peer_last + lookback_s
    quiet_min = (now_epoch - peer_last) / 60.0
    reading["peer_last_write"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(peer_last))
    reading["peer_quiet_min"] = round(quiet_min, 1)
    reading["closes_at"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(closes))
    reading["minutes_to_close"] = round((closes - now_epoch) / 60.0, 1)

    if now_epoch >= closes:
        reading["verdict"] = "WINDOW_CLOSED"
        reading["why"] = ("peer last wrote %.1f min ago, beyond the %.0f min lookback -- "
                          "the window has closed on its own" % (quiet_min, lookback))
        if alive_peers:
            reading["why"] += ("; the peer shell is still up, so a new write would reopen it")
    elif not alive_peers:
        reading["verdict"] = "PEER_EXITED"
        reading["why"] = ("peer last wrote %.1f min ago and its process is now gone -- the "
                          "remaining window is a leftover, not a live risk" % quiet_min)
    else:
        reading["verdict"] = "WINDOW_OPEN"
        reading["why"] = ("peer wrote %.1f min ago and is still alive -- new files only "
                          "until %s" % (quiet_min, reading["closes_at"]))
    return reading


def render(reading: dict, inputs_digest: str) -> str:
    v = reading["verdict"]
    lines = [
        BEGIN,
        "generated %s | verdict **%s** | machine %s | inputs %s" % (
            reading.get("generated") or time.strftime("%Y-%m-%dT%H:%M:%S"),
            v, reading.get("machine_id", "?"),
            inputs_digest[:12]),
        "",
        "| 项 | 读数 |",
        "|---|---|",
        "| 对端进程 | %s |" % (", ".join(str(p) for p in reading.get("peer_pids") or []) or "无"),
        "| 对端仍存活 | %s |" % (
            ", ".join(str(p) for p in reading.get("peer_alive_pids") or []) or "否"),
        "| 对端最后写入 | %s |" % (reading.get("peer_last_write") or "窗口内无可归因写入"),
        "| 那张面 | %s |" % (reading.get("peer_last_write_path") or "—"),
        "| 静默时长 | %s |" % (
            "—" if reading.get("peer_quiet_min") is None else "%.1f 分钟" % reading["peer_quiet_min"]),
        "| 回看窗 | %.0f 分钟 |" % reading.get("lookback_min", 45),
        "| 窗口自然关闭于 | %s |" % (reading.get("closes_at") or "—"),
        "| 距关闭 | %s |" % (
            "—" if reading.get("minutes_to_close") is None
            else "%.1f 分钟" % reading["minutes_to_close"]),
        "",
        "**判词**：%s" % v,
        "",
        "> %s" % reading.get("why", ""),
        "",
        "**本轮可做什么**：%s" % _advice(v),
        END,
    ]
    return "\n".join(lines)


def _advice(verdict: str) -> str:
    return {
        "NO_PEER": "共享面可改；照常跑 S6 链与全量冒烟。",
        "PEER_EXITED": "对端已退出且窗口内无写入——按 r1907 仍只写新增文件面一轮，下一轮重跑探针确认再放开。",
        "WINDOW_OPEN": "只写新增文件面；禁改共享面、禁重跑 S6 链（r1907/r1927）。到期后重跑探针再判。",
        "WINDOW_CLOSED": "窗口已自然关闭，可恢复共享面工作；若对端壳仍活着，下一轮开工前重跑探针一次。",
    }.get(verdict, "—")


def _digest_probe(probe: dict) -> str:
    import hashlib
    payload = json.dumps({
        "probed_at": probe.get("probed_at"),
        "lookback_min": probe.get("lookback_min"),
        "hosts": sorted((h.get("pid"), h.get("started")) for h in (probe.get("hosts") or [])),
        "writes": sorted((w.get("path"), w.get("mtime_epoch"), w.get("mtime"))
                         for w in (probe.get("recent_writes") or [])),
        "my_host_pid": probe.get("my_host_pid"),
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_probe(mid: str) -> dict:
    path = PROBE.format(mid=mid)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def derive(mid: str, now_epoch: float | None = None) -> dict:
    probe = load_probe(mid)
    now = now_epoch if now_epoch is not None else time.time()
    reading = classify(probe, now)
    reading["machine_id"] = mid
    reading["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now))
    reading["inputs_digest"] = _digest_probe(probe)
    return reading


def write_page(block: str) -> None:
    if os.path.exists(PAGE):
        with open(PAGE, encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = ("# 竞争窗还有多久\n\n"
                "一张面，回答每轮都要问的那句话：另一个宿主还在写吗，窗口还有几分钟自然关闭。\n"
                "由 `scripts/contention_window.py` 渲染；只描述不修板、不杀进程、不放宽律法。\n\n"
                "<!-- BEGIN contention_window -->\n<!-- END contention_window -->\n\n"
                "## 它不声称什么\n\n"
                "- 不替代 `Tools/repo_write_contention.py`：那个回答「现在有没有冲突」，这个回答「冲突还有多久」\n"
                "- 不杀进程、不改共享面、不改 r1907/r1927 的执法口径\n"
                "- 窗口关闭不等于对端安全：对端壳仍活着时，下一次写入会重开窗口，所以开工前要重跑探针\n")
    if BEGIN in text and END in text:
        head = text.split(BEGIN)[0]
        tail = text.split(END, 1)[1]
        text = head + block + tail
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    with open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def cmd_run(mid: str) -> int:
    reading = derive(mid)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(reading, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    write_page(render(reading, reading["inputs_digest"]))
    print("CONTENTION-WINDOW %s machine=%s closes_at=%s minutes_to_close=%s" % (
        reading["verdict"], mid, reading["closes_at"], reading["minutes_to_close"]))
    return 0


def cmd_check(mid: str) -> int:
    """Re-derive and compare.  Drift in the inputs -> STALE; same inputs, different
    numbers -> a disagreement (no STALE word, so the S6 chain does not pay a rebuild).
    """
    fresh = derive(mid)
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    with open(OUT, encoding="utf-8") as fh:
        old = json.load(fh)
    if old.get("inputs_digest") != fresh["inputs_digest"]:
        print("STALE inputs moved: probe %s -> %s" % (
            str(old.get("inputs_digest"))[:12], fresh["inputs_digest"][:12]))
        return 3
    diffs = []
    for key in ("verdict", "peer_last_write", "closes_at", "peer_alive_pids", "peer_count"):
        if old.get(key) != fresh.get(key):
            diffs.append("%s: face=%r rederive=%r" % (key, old.get(key), fresh.get(key)))
    if diffs:
        print("CHECK FAILED (same inputs, different numbers -- a disagreement, not drift): %s"
              % "; ".join(diffs)[:300])
        return 3
    if not os.path.exists(PAGE):
        print("STALE page missing: %s" % PAGE)
        return 3
    with open(PAGE, encoding="utf-8") as fh:
        text = fh.read()
    if BEGIN not in text or END not in text:
        print("STALE page has no marker block")
        return 3
    block = text.split(BEGIN, 1)[1].split(END, 1)[0]
    # the page is compared against the *face's own* generation stamp, so a wall-clock
    # minute passing between run and check is not a mismatch
    want = render(old, fresh["inputs_digest"]).split(BEGIN, 1)[1].split(END, 1)[0]
    if block.strip() != want.strip():
        print("CHECK FAILED page block does not match re-derivation")
        return 3
    print("CONTENTION-WINDOW CHECK OK verdict=%s closes_at=%s" % (
        fresh["verdict"], fresh["closes_at"]))
    return 0


def selftest() -> int:
    import tempfile
    ok = 0
    bad = []

    def chk(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s %s" % (name, detail))

    T0 = 1795551102.0  # a fixed epoch, so the legs never read the wall clock
    base = {
        "probed_at": "2026-11-25T04:16:31",
        "lookback_min": 45.0,
        "my_host_pid": 111,
        "hosts": [{"pid": 111, "kind": "other", "started": "2026-11-25T04:15:03"},
                  {"pid": 222, "kind": "interactive", "started": "2026-11-24T22:39:04"}],
        "recent_writes": [{"path": "research/X.md", "mtime_epoch": T0 - 300}],
    }

    # 1. lone host -> NO_PEER
    solo = dict(base)
    solo["hosts"] = [h for h in base["hosts"] if h["pid"] == 111]
    r = classify(solo, T0, lambda p: True)
    chk("lone host reads NO_PEER", r["verdict"] == "NO_PEER", r["verdict"])

    # 2. peer wrote 5 min ago, alive -> WINDOW_OPEN with 40 min left
    r = classify(base, T0, lambda p: True)
    chk("peer wrote 5min ago reads WINDOW_OPEN", r["verdict"] == "WINDOW_OPEN", r["verdict"])
    chk("window has 40 min left", abs(r["minutes_to_close"] - 40.0) < 0.01, r["minutes_to_close"])
    chk("closes_at is printed", bool(r["closes_at"]))

    # 3. peer wrote 50 min ago, alive -> WINDOW_CLOSED but warns the shell is up
    late = dict(base)
    late["recent_writes"] = [{"path": "research/X.md", "mtime_epoch": T0 - 3000}]
    r = classify(late, T0, lambda p: True)
    chk("peer quiet 50min reads WINDOW_CLOSED", r["verdict"] == "WINDOW_CLOSED", r["verdict"])
    chk("closed-with-shell-up says a new write reopens it", "reopen" in r["why"], r["why"][:60])

    # 4. peer died 20 min after its last write -> PEER_EXITED (window is a leftover)
    r = classify(base, T0, lambda p: p != 222)
    chk("dead peer reads PEER_EXITED", r["verdict"] == "PEER_EXITED", r["verdict"])

    # 5. exact boundary: quiet == lookback -> closed, not open
    edge = dict(base)
    edge["recent_writes"] = [{"path": "research/X.md", "mtime_epoch": T0 - 2700}]
    r = classify(edge, T0, lambda p: True)
    chk("quiet == lookback reads CLOSED", r["verdict"] == "WINDOW_CLOSED", r["verdict"])

    # 6. peers alive, no attributable write -> assume it may write
    r = classify({**base, "recent_writes": []}, T0, lambda p: True)
    chk("alive peer with no write reads WINDOW_OPEN", r["verdict"] == "WINDOW_OPEN", r["verdict"])

    # 7. mtime string only (no epoch) still parses
    r = classify({**base, "recent_writes": [{"path": "research/X.md",
                                             "mtime": time.strftime("%Y-%m-%dT%H:%M:%S",
                                                                    time.localtime(T0 - 600))}]},
                 T0, lambda p: True)
    chk("string mtime is honoured", r["verdict"] == "WINDOW_OPEN", r["verdict"])

    # 8. digest ignores poll order but catches a changed write
    d1 = _digest_probe(base)
    d2 = _digest_probe({**base, "recent_writes": list(reversed(base["recent_writes"]))})
    chk("digest is order-insensitive", d1 == d2)
    d3 = _digest_probe({**base, "recent_writes": [{"path": "research/X.md", "mtime_epoch": T0}]})
    chk("digest catches a changed write", d1 != d3)

    # 9. the page block carries the verdict and the close time
    blk = render({**classify(base, T0, lambda p: True), "machine_id": "bm-c"}, d1)
    chk("block prints the verdict", "WINDOW_OPEN" in blk)
    chk("block prints the close time", "窗口自然关闭于" in blk)

    # 10. advice differs by verdict (a constant would be a lie)
    chk("advice is not one constant",
        _advice("WINDOW_OPEN") != _advice("WINDOW_CLOSED") != _advice("NO_PEER"))

    # 11. a dead pid really reads dead through the production probe
    chk("pid 0 is not alive", _pid_alive(0) is False)

    if bad:
        print("SELFTEST FAILED %d/%d" % (ok, ok + len(bad)))
        for b in bad:
            print("  -", b)
        return 1
    print("SELFTEST OK %d/%d" % (ok, ok))
    return 0


def main(argv) -> int:
    mid = _machine_id()
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest":
        return selftest()
    if cmd == "--check":
        return cmd_check(mid)
    return cmd_run(mid)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
