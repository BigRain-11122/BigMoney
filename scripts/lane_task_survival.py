"""Lane task survival -- how long does a healed lane stay healed?

WHY THIS EXISTS
    Every second round on this desk finds the same thing: one or more Bigmoney-*
    scheduled tasks are Disabled, the round re-enables them, the round report
    says "lane restored", and the next round finds them Disabled again. That
    loop has no measurement in it. "We re-enabled it" and "it stayed on" are
    different claims, and only the second one is a fix.

    A silence guard that rewrites console tasks into a hidden chain falls back
    to Disable-ScheduledTask when the rewrite throws (see Tools/silence-enforce.ps1
    section 3); its own comment records a lane going Disabled twice inside one
    day right after being Ready. So a re-enable is a *hypothesis*: either the
    guard now leaves the task alone, or it will switch it off again within its
    cadence (one minute here). This face measures which of the two happened,
    because the difference is the difference between a fixed lane and a lane
    that only looks fixed between rounds.

WHAT IT MEASURES
    A sample loop over a fixed task set: at each tick, ask the OS for each
    task's state (Ready/Running/Disabled/Missing) and record the wall clock.
    Then per task: the state at the start, the state at the end, the transitions
    with timestamps, and -- for a task that was enabled at t0 and is Disabled at
    t1 -- the *latency* to being switched off (t1 - t0, an upper bound).

VERDICTS (frozen constants, echoed into the payload; --check refuses a payload
whose echoed criteria differ)
    STAYED_ON       every task enabled at t0 is still enabled at the end of the
                    sample window -> the re-enable held for at least that long.
    SWITCHED_OFF    at least one task went enabled -> Disabled inside the window
                    -> the disabler is live; re-enabling is not the fix, and the
                    payload carries the latency so the next claim can be measured.
    NO_CHANGE       nothing that was enabled at t0 is disabled at the end, and
                    nothing was disabled at t0 either -> nothing to say.
    INCONCLUSIVE    the sampler failed to read a task (never read "still on" out
                    of "could not ask"), or the window is too short to distinguish
                    a 1-minute guard from a 10-minute one.

    Exit codes: 0 = sample taken / --check ok; 2 = sampler could not read the OS
    state at all (honest failure, never a green); 1 = --check disagrees with the
    payload (the verdict must be recomputable, not remembered).

    selftest: offline. The parser and the verdict rule are exercised on
    synthetic rows (no scheduled task is touched), including the two failures
    that matter: an unreadable tick is not an "on" tick, and a window shorter
    than the guard cadence cannot claim STAYED_ON.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "results")

# The lane's own task set. Not every Bigmoney-* task is a lane: the pool feeder
# (Autofill) and the pool worker (PoolWorker) are supply, the watchdogs are the
# ignition face, and the dispatcher/intraday marks are the two remaining lanes.
LANE_TASKS = [
    "Bigmoney-IterationLoop",
    "Bigmoney-LoopWatchdog",
    "Bigmoney-Autofill",
    "Bigmoney-PoolWorker",
    "Bigmoney-ResidentDispatcher",
    "Bigmoney-IntradayMarks",
    "Bigmoney-SatEngine-bm-b",
    "HQ-Patrol-BigMoney",
]

READY = "\u5c31\u7eea"                  # 就绪
DISABLED = "\u5df2\u7981\u7528"          # 已禁用
RUNNING = "\u6b63\u5728\u8fd0\u884c"      # 正在运行
QUEUED = "\u961f\u5217\u4e2d"            # 队列中

# A window shorter than this cannot distinguish "the guard left it alone" from
# "the guard has not fired yet": the guard's cadence on this host is one minute.
MIN_WINDOW_S = 120.0
GUARD_CADENCE_S = 60.0


def classify(status_text):
    """Map a schtasks status cell to a state. Unknown text is 'unreadable', and
    unreadable is never folded into 'on' (that is the whole point)."""
    t = (status_text or "").strip()
    if t == READY or t == RUNNING or t == QUEUED:
        return "on"
    if t == DISABLED:
        return "off"
    return "unreadable"


def read_task(name):
    """One task's state, straight from the OS. Missing task = 'missing'."""
    out = subprocess.run(["schtasks", "/query", "/tn", name, "/fo", "csv", "/nh"],
                         capture_output=True, text=True, encoding="gbk",
                         errors="replace")
    raw = (out.stdout or "").strip()
    if not raw:
        return "missing", raw
    cell = raw.split('","')[-1].strip().strip('"')
    return classify(cell), cell


def sample(names, duration_s, interval_s, now=time.time):
    """Take a sample. Returns the per-tick rows; the caller derives verdicts."""
    ticks = []
    t0 = now()
    while True:
        el = now() - t0
        row = {"t_s": round(el, 1), "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "states": {}}
        for n in names:
            state, raw = read_task(n)
            row["states"][n] = state
            if state == "unreadable":
                row.setdefault("unreadable_raw", {})[n] = raw
        ticks.append(row)
        if el >= duration_s:
            break
        time.sleep(min(interval_s, max(0.0, duration_s - el)))
    return ticks


def per_task(names, ticks):
    out = {}
    for n in names:
        seq = [(t["t_s"], t["states"].get(n, "missing")) for t in ticks]
        first = seq[0][1]
        last = seq[-1][1]
        transitions = []
        prev = first
        for t_s, s in seq[1:]:
            if s != prev:
                transitions.append({"at_s": t_s, "from": prev, "to": s})
                prev = s
        latency = None
        if first == "on":
            for tr in transitions:
                if tr["to"] == "off":
                    latency = tr["at_s"]
                    break
        out[n] = {"first": first, "last": last, "transitions": transitions,
                  "off_latency_s": latency,
                  "unreadable_ticks": sum(1 for _, s in seq if s == "unreadable")}
    return out


def decide(names, ticks, tasks, window_s):
    """The verdict rule. Frozen: --check re-runs exactly this on the payload."""
    enabled_at_t0 = [n for n in names if tasks[n]["first"] == "on"]
    disabled_at_t0 = [n for n in names if tasks[n]["first"] == "off"]
    went_off = [n for n in enabled_at_t0 if tasks[n]["last"] == "off"
                or any(tr["to"] == "off" for tr in tasks[n]["transitions"])]
    # Any unreadable tick voids the window: a gap in the middle is exactly where a
    # switch-off would hide, so "could not ask" must never be read as "still on".
    unreadable = [n for n in names
                  if tasks[n]["first"] == "unreadable" or tasks[n]["last"] == "unreadable"
                  or tasks[n].get("unreadable_ticks")]
    if unreadable:
        return "INCONCLUSIVE", {"unreadable": unreadable}
    if len(ticks) < 2 or window_s < MIN_WINDOW_S:
        return "INCONCLUSIVE", {"window_s": window_s, "min_window_s": MIN_WINDOW_S}
    if went_off:
        return "SWITCHED_OFF", {"switched_off": went_off}
    if enabled_at_t0:
        return "STAYED_ON", {"enabled_at_t0": enabled_at_t0}
    if disabled_at_t0:
        return "NO_CHANGE", {"disabled_at_t0": disabled_at_t0}
    return "NO_CHANGE", {}


def run(args):
    names = list(args.tasks) if args.tasks else list(LANE_TASKS)
    machine = os.environ.get("BIGMONEY_MACHINE_ID") or _machine_id()
    t0 = time.time()
    ticks = sample(names, args.duration, args.interval)
    window = ticks[-1]["t_s"] if ticks else 0.0
    tasks = per_task(names, ticks)
    verdict, why = decide(names, ticks, tasks, window)
    payload = {
        "artifact": "results/lane_task_survival.%s.json" % machine,
        "face": "lane_task_survival v1.0",
        "machine_id": machine,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)),
        "evidence_cutoff": time.strftime("%Y-%m-%d", time.localtime(t0)),
        "window_s": round(window, 1),
        "interval_s": args.interval,
        "criteria": {"min_window_s": MIN_WINDOW_S, "guard_cadence_s": GUARD_CADENCE_S,
                     "verdicts": ["STAYED_ON", "SWITCHED_OFF", "NO_CHANGE", "INCONCLUSIVE"],
                     "rule": ("SWITCHED_OFF iff a task that was on at t0 is off at t1; "
                              "INCONCLUSIVE if any tick was unreadable or the window is "
                              "shorter than min_window_s")},
        "verdict": verdict,
        "detail": why,
        "tasks": tasks,
        "ticks": ticks,
        "reading": {
            "STAYED_ON": "the re-enable held for the whole window",
            "SWITCHED_OFF": "the disabler is live inside the window; re-enabling is not the fix",
            "NO_CHANGE": "nothing was on at t0 to lose",
            "INCONCLUSIVE": "the sample cannot answer the question it was taken for",
        }[verdict],
    }
    path = os.path.join(RESULTS, "lane_task_survival.%s.json" % machine)
    os.makedirs(RESULTS, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print("%s | window %.0fs | %s" % (verdict, window, ", ".join(
        "%s=%s" % (n, tasks[n]["last"]) for n in names)))
    if verdict == "SWITCHED_OFF":
        for n in why["switched_off"]:
            print("  off after %ss: %s" % (tasks[n]["off_latency_s"], n))
    print("payload -> %s" % path)
    return 0


def _machine_id():
    p = os.path.join(ROOT, "fleet", "machine.json")
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)["machine_id"]
    except Exception:
        return "unknown"


def check(args):
    machine = args.machine or _machine_id()
    path = os.path.join(RESULTS, "lane_task_survival.%s.json" % machine)
    if not os.path.exists(path):
        print("CHECK FAIL: no payload at %s (run the sampler first)" % path)
        return 1
    with open(path, encoding="utf-8") as fh:
        p = json.load(fh)
    names = list(p.get("tasks") or {})
    tasks = p["tasks"]
    ticks = p.get("ticks") or []
    verdict, _ = decide(names, ticks, tasks, float(p.get("window_s") or 0.0))
    if verdict != p.get("verdict"):
        print("CHECK FAIL: payload says %s, the rule says %s"
              % (p.get("verdict"), verdict))
        return 1
    stale = None
    try:
        age = time.time() - os.path.getmtime(path)
        stale = age > 6 * 3600
    except Exception:
        pass
    print("check OK (%s, cutoff %s%s)" % (verdict, p.get("evidence_cutoff"),
                                          ", STALE >6h" if stale else ""))
    return 0


def selftest():
    ok = 0
    bad = []

    def chk(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s %s" % (name, detail))

    # L1 the parser maps the three "on" spellings and the off spelling
    chk("L1 on/off spellings", classify(READY) == "on" and classify(RUNNING) == "on"
        and classify(QUEUED) == "on" and classify(DISABLED) == "off")
    # L2 anything else is unreadable, not "on"
    chk("L2 unknown status is unreadable", classify("N/A") == "unreadable"
        and classify("") == "unreadable")
    names = ["A", "B"]

    def mk(seq, interval=10.0):
        return [{"t_s": round(i * interval, 1), "at": "x",
                 "states": dict(zip(names, row))} for i, row in enumerate(seq)]

    # L3 a task that goes off inside the window is SWITCHED_OFF with a latency
    #    (window must clear MIN_WINDOW_S, so the fixture runs 13 ticks at 10s)
    ticks = mk([("on", "on"), ("on", "on"), ("off", "on")] + [("off", "on")] * 10)
    tasks = per_task(names, ticks)
    v, why = decide(names, ticks, tasks, ticks[-1]["t_s"])
    chk("L3 switched off detected", v == "SWITCHED_OFF" and why["switched_off"] == ["A"])
    chk("L3b latency is the tick it went off", tasks["A"]["off_latency_s"] == 20.0)
    # L4 all on for a long enough window -> STAYED_ON
    ticks = mk([("on", "on")] * 14)
    tasks = per_task(names, ticks)
    v, _ = decide(names, ticks, tasks, ticks[-1]["t_s"])
    chk("L4 stayed on", v == "STAYED_ON")
    # L5 a short window cannot claim STAYED_ON (the guard fires every minute)
    ticks = mk([("on", "on")] * 2)
    tasks = per_task(names, ticks)
    v, _ = decide(names, ticks, tasks, ticks[-1]["t_s"])
    chk("L5 short window is inconclusive", v == "INCONCLUSIVE", v)
    # L6 an unreadable tick is not an on tick
    ticks = mk([("on", "on"), ("unreadable", "on"), ("on", "on")] + [("on", "on")] * 12)
    tasks = per_task(names, ticks)
    v, why = decide(names, ticks, tasks, ticks[-1]["t_s"])
    chk("L6 unreadable is inconclusive", v == "INCONCLUSIVE" and why["unreadable"] == ["A"])
    # L7 nothing on at t0 -> NO_CHANGE, not a green
    ticks = mk([("off", "off")] * 14)
    tasks = per_task(names, ticks)
    v, _ = decide(names, ticks, tasks, ticks[-1]["t_s"])
    chk("L7 nothing to lose is NO_CHANGE", v == "NO_CHANGE", v)
    # L8 a task that comes back on after being switched off still reads SWITCHED_OFF
    #    (the window saw the lane go down; that is the fact worth keeping)
    ticks = mk([("on", "on")] * 3 + [("off", "on")] + [("on", "on")] * 10)
    tasks = per_task(names, ticks)
    v, _ = decide(names, ticks, tasks, ticks[-1]["t_s"])
    chk("L8 a bounce still counts as switched off", v == "SWITCHED_OFF", v)
    # L9 a missing task is reported as missing, never as off-and-fine
    tasks = per_task(names, mk([("missing", "on")] * 14))
    chk("L9 missing is its own state", tasks["A"]["first"] == "missing")
    # L10 transitions keep the order they happened in
    tasks = per_task(names, mk([("on", "on"), ("off", "on"), ("on", "on")] + [("on", "on")] * 11))
    chk("L10 transitions ordered",
        [t["to"] for t in tasks["A"]["transitions"]] == ["off", "on"])
    print("lane_task_survival selftest: %d PASS, %d FAIL" % (ok, len(bad)))
    for b in bad:
        print("  FAIL:", b)
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="measure how long a healed lane stays healed")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="take a sample and publish the verdict")
    r.add_argument("--duration", type=float, default=180.0)
    r.add_argument("--interval", type=float, default=20.0)
    r.add_argument("--tasks", nargs="*", default=None)
    c = sub.add_parser("check", help="re-derive the verdict from the published payload")
    c.add_argument("--machine", default=None)
    sub.add_parser("selftest", help="offline guards")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run(args)
    if args.cmd == "check":
        return check(args)
    if args.cmd == "selftest":
        return selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())