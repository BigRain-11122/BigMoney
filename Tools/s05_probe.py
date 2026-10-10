#!/usr/bin/env python
# s05_probe.py -- standing S0.5 probe composer (r844 bm-c tech chore, queued
# by r843 adjudication). The per-round ad-hoc s05 probe lineage
# (results/_rNNNbmc_s05*.py) read the orders_ack set from state-<id>.json --
# a face that does not carry the key (canonical ack store = heartbeat
# fleet/machines/<id>.json), so the diff degenerated to an empty set ->
# false "all orders unacked" longlist (r843: zero enforcement impact, queued
# as next-window tech chore). This tool is the structural gate: it composes
# the two standing mechanisms with the CORRECT read positions and retires
# the hand-rolled faces:
#   Face A (D-19 watermark): scripts/d19_watermark.py probe -- orders/
#     decisions blob sha vs this machine's state watermark (group-tree
#     origin/main, fresh-fetch fallback handled inside that tool).
#   Face B (ack diff): Tools/orders_ack_scan.scan() -- fleet/orders/O-*.md
#     vs HEARTBEAT orders_ack. THE FIX: acks are never read from state.
# The session-side rule: run this tool instead of cloning an ad-hoc probe;
# on watermark delta TRUE the session still does its own full group-tree
# origin blob read for consumption (fresh-read law -- this tool emits
# verdicts, not row content).
#
# Output: results/_s05_probe.<machine>.json + one-line stdout verdict.
# Exit codes (priority order):
#   0 = both faces green: no new orders/decisions to consume, zero unacked
#   3 = face B unacked orders (P0 dispatch debt, FLEET-OPS sec.3)
#   4 = face A watermark delta TRUE (session must consume new rows this
#       round; JSON also carries face B verdict)
#   2 = mechanism fault (either face unreadable)
#
# Law map: FLEET-OPS sec.3 (receipt closure), iteration prompt S0.5 (full
# scan, NO timestamp filtering, set-diff only), R13 O-1820 skip-row lesson.
#
# ENCODING: pure ASCII body (repo law: PS/py hosts on zh-CN decode BOM-less
# files as GBK; keep every non-ASCII string out of this file).
import json
import os
import subprocess
import sys
import tempfile

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(TOOLS_DIR)
WM_TOOL = os.path.join(PROJECT, "scripts", "d19_watermark.py")
WM_TIMEOUT_S = 240


def now_iso():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def run_hard(cmd, timeout_s):
    """Run with hard timeout; tree-kill via taskkill on expiry (r843 lineage
    discipline: plain subprocess timeouts can leave git children alive)."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(timeout=timeout_s)
        return p.returncode, out.decode("utf-8", "replace"), \
            err.decode("utf-8", "replace"), False
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)],
                       capture_output=True)
        try:
            out, err = p.communicate(timeout=10)
        except Exception:
            out, err = b"", b""
        return -9, out.decode("utf-8", "replace"), \
            err.decode("utf-8", "replace"), True


def probe_watermark():
    """Face A: delegate to scripts/d19_watermark.py probe, parse its JSON.
    Returns dict (may carry 'error')."""
    face = {"tool": "d19_watermark.py probe", "rc": None, "timed_out": False}
    if not os.path.isfile(WM_TOOL):
        face["error"] = "scripts/d19_watermark.py missing"
        return face
    rc, out, err, timed_out = run_hard(
        [sys.executable, WM_TOOL, "probe"], WM_TIMEOUT_S)
    face["rc"] = rc
    face["timed_out"] = timed_out
    parsed = None
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            cand = json.loads(line)
        except ValueError:
            continue
        if isinstance(cand, dict) and "orders_changed" in cand:
            parsed = cand
    if parsed is None:
        face["error"] = "no verdict JSON on stdout (rc=%s timeout=%s)" \
            % (rc, timed_out)
        if err:
            face["stderr_tail"] = err[-300:]
        return face
    face.update({k: parsed[k] for k in parsed
                 if k in ("orders_changed", "decisions_changed",
                          "orders_sha", "wm_orders", "decisions_sha",
                          "wm_decisions", "orders_method", "decisions_method")})
    return face


def probe_ack():
    """Face B: delegate to Tools/orders_ack_scan.scan() (heartbeat face).
    Returns (verdict_dict, exit_code)."""
    sys.path.insert(0, TOOLS_DIR)
    import orders_ack_scan
    return orders_ack_scan.scan(PROJECT)


def decide(wm_face, ack_face, ack_rc):
    """Combined exit code. Priority: fault > unacked > watermark delta."""
    wm_fault = "error" in wm_face
    ack_fault = ack_rc == 2 or "error" in ack_face
    if wm_fault or ack_fault:
        return 2
    if ack_face.get("unacked"):
        return 3
    if wm_face.get("orders_changed") or wm_face.get("decisions_changed"):
        return 4
    return 0


def run():
    ts = now_iso()
    wm_face = probe_watermark()
    ack_face, ack_rc = probe_ack()
    rc = decide(wm_face, ack_face, ack_rc)
    verdict = {
        "tool": "s05_probe",
        "ts": ts,
        "machine_id": ack_face.get("machine_id", "unknown"),
        "watermark_face": wm_face,
        "ack_face": {k: ack_face[k] for k in
                     ("machine_id", "orders_count", "ack_count",
                      "unacked", "stale_acks", "error") if k in ack_face},
        "orders_delta": bool(wm_face.get("orders_changed")),
        "decisions_delta": bool(wm_face.get("decisions_changed")),
        "unacked": ack_face.get("unacked", []),
        "exit": rc,
    }
    out = os.path.join(PROJECT, "results",
                       "_s05_probe.%s.json" % verdict["machine_id"])
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)
    print(json.dumps({k: verdict[k] for k in
                      ("machine_id", "orders_delta", "decisions_delta",
                       "unacked", "exit")}, ensure_ascii=False))
    if rc == 3:
        print("UNACKED ORDERS (P0 dispatch debt, FLEET-OPS sec.3):")
        for f in verdict["unacked"]:
            print("  " + f)
    elif rc == 4:
        print("WATERMARK DELTA TRUE: consume new orders/decisions rows "
              "(full group-tree origin blob read) this round.")
    elif rc == 2:
        print("MECHANISM FAULT: see watermark_face/ack_face in JSON.")
    return rc


def selftest():
    """Offline legs: no live fetch, no writes outside temp dirs."""
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, ok))
        print("%-64s %s %s" % (name, "PASS" if ok else "FAIL", extra))

    tmp = tempfile.mkdtemp(prefix="s05p_st_")
    try:
        import orders_ack_scan

        # L1: THE BUG SCENARIO -- state-<id>.json exists WITHOUT orders_ack,
        # heartbeat HAS the acks. scan() must see the heartbeat acks
        # (r843 bug: ad-hoc probe read state -> empty set -> false longlist).
        f1 = os.path.join(tmp, "L1")
        os.makedirs(os.path.join(f1, "fleet", "machines"), exist_ok=True)
        os.makedirs(os.path.join(f1, "fleet", "orders"), exist_ok=True)
        with open(os.path.join(f1, "fleet", "machine.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"machine_id": "bm-x"}, fh)
        with open(os.path.join(f1, "state-bm-x.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"round_no": 1}, fh)  # deliberately NO orders_ack key
        with open(os.path.join(f1, "fleet", "machines", "bm-x.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"orders_ack": ["O-1.md", "O-2.md"]}, fh)
        for name in ("O-1.md", "O-2.md"):
            with open(os.path.join(f1, "fleet", "orders", name), "w",
                      encoding="utf-8") as fh:
                fh.write("x\n")
        v, rc = orders_ack_scan.scan(f1)
        leg("L1 heartbeat face wins when state lacks acks",
            rc == 0 and v["ack_count"] == 2 and not v["unacked"],
            "ack_count=%s unacked=%s" % (v["ack_count"], v["unacked"]))

        # L2: unacked detection intact (heartbeat source).
        with open(os.path.join(f1, "fleet", "orders", "O-3.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("x\n")
        v, rc = orders_ack_scan.scan(f1)
        leg("L2 unacked -> exit 3 from heartbeat diff",
            rc == 3 and v["unacked"] == ["O-3.md"],
            "unacked=%s" % v["unacked"])

        # L3: face A stdout parser -- picks the verdict JSON line, ignores
        # noise, tolerates trailing garbage lines.
        stub_out = ('fetch noise line\n'
                    '{"orders_changed": true, "decisions_changed": false,'
                    ' "orders_sha": "abc123", "wm_orders": "000",'
                    ' "decisions_sha": "def", "wm_decisions": "def"}\n'
                    'garbage {not json}\n')
        parsed = None
        for line in stub_out.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                cand = json.loads(line)
            except ValueError:
                continue
            if isinstance(cand, dict) and "orders_changed" in cand:
                parsed = cand
        leg("L3 face A parser picks verdict JSON",
            parsed is not None and parsed["orders_changed"] is True
            and parsed["orders_sha"] == "abc123")

        # L4: face A parser on pure noise -> None (fault face).
        parsed2 = None
        for line in ("noise", "{}", ""):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                cand = json.loads(line)
            except ValueError:
                continue
            if isinstance(cand, dict) and "orders_changed" in cand:
                parsed2 = cand
        leg("L4 face A parser rejects noise", parsed2 is None)

        # L5: decide() priority -- fault > unacked > delta > green.
        wm_ok = {"orders_changed": False, "decisions_changed": False}
        wm_delta = {"orders_changed": True, "decisions_changed": False}
        wm_fault = {"error": "x"}
        ack_ok = {"unacked": []}
        ack_debt = {"unacked": ["O-9.md"]}
        leg("L5 decide green", decide(wm_ok, ack_ok, 0) == 0)
        leg("L6 decide delta -> 4", decide(wm_delta, ack_ok, 0) == 4)
        leg("L7 decide unacked -> 3", decide(wm_ok, ack_debt, 3) == 3)
        leg("L8 decide unacked beats delta", decide(wm_delta, ack_debt, 3) == 3)
        leg("L9 decide fault -> 2 (wm)", decide(wm_fault, ack_ok, 0) == 2)
        leg("L10 decide fault -> 2 (ack rc)", decide(wm_ok, {"error": "e"}, 2) == 2)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    fails = [n for n, ok in legs if not ok]
    print("selftest: %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 1 if fails else 0


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
