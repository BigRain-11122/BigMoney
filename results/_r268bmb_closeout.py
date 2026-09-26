"""r268 bm-b closeout: round report line + state.json + heartbeat (one shot,
byte-face preserving; heartbeat epoch must be JSON int + clock_read T-sep per
R170/R178/R262 law, self-verified after write)."""
import datetime
import io
import json
import os
import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")           # T separator guaranteed
EPOCH = int(NOW.timestamp())                       # JSON int per smoke F7

REPORT_LINE = (
    "%s | r268 (bm-b) | dept:工程/总经理治理审计 | T-83 s2 conflict/duplication/dead-face "
    "DETECTION delivered (detection-only zero canon edits per O-1355 discipline 1): detector "
    "scripts/governance_audit_s2.py selftest 9/9 + rerun byte-identical, snapshot "
    "results/governance_s2_20260926.json (D1 161 carriers/1 prereg zero-face; D2 971 canon refs "
    "-> 5 template+17 inbox-moved+19 relocated+24 true-missing incl SYSTEM_LOGIC 8 stale "
    "artifacts + POST_REVIEW/LOCAL_FIRST jsonl false-positive self-bug caught+fixed pre-report; "
    "D5 zero cross-doc status contradictions; D9 1 explicit supersession edge O-1136->O-1738 "
    "clause + 6 mechanism-amendment candidates; D10 zero stale round-report citations, 1 canon "
    "cite of partially-superseded O-1738) + report research/AUDIT-20260926-S2.md + post_review "
    "row T-83-S2-DETECTION registered (reviewer YES=24 NO=0) + ticket progress_r268 | evidence: "
    "detector selftest 9/9, sha-rerun identical, post_review run exit 0, smoke 25/25 PASS, S6 "
    "21 legs all exit 0 (py_low_board_clear legal idle; regime ORANGE shadow; no new bar Sat, "
    "paper trio gated; LHB refresh fetch new_beyond_cutoff=0 no-op; token delta +6) | next: r269 "
    "s2 spillover if GM s3 asks mechanical wiring; T-76 face(a)/T-78 GRID marks on next new bar; "
    "s3 GM seven deliverables + s4 quarterly wiring untouched per lane note"
) % ISO


def main():
    # 1. round report line (append, LF file face)
    p = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    with io.open(p, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(REPORT_LINE + "\n")

    # 2. state.json round bump (mirror face: LF, indent=1, no sort)
    sp = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
    with io.open(sp, encoding="utf-8") as fh:
        s = json.load(fh)
    s["round_no"] = 268
    s["did"] = ("r268: T-83 s2 detection delivered (detector+selftest 9/9+snapshot+report+"
                "post_review row+ticket progress_r268); S6 21 legs exit 0; smoke 25/25")
    s["verdict"] = "green"
    s["next"] = ("r269: pool/board watch; T-76 face(a)+T-78 GRID marks on next new bar; "
                 "T-83 s3 GM faces reserved")
    s["last_round_ts"] = ISO
    s["current_task"] = "r268 done: T-83 s2 detection faces; next: board/pool watch + marks on new bar"
    s["last_seen"] = ISO[:19]
    with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1)

    # 3. heartbeat (epoch int + T-sep clock per R170/R178/R262)
    hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    with io.open(hp, encoding="utf-8") as fh:
        h = json.load(fh)
    vm = psutil.virtual_memory()
    h["last_seen"] = ISO[:19]
    h["heartbeat_epoch_utc"] = EPOCH
    h["clock_read"] = ISO
    h["current_task"] = s["current_task"]
    h["round_no"] = 268
    h["verdict"] = "healthy"
    h["cpu_cores"] = psutil.cpu_count(logical=True)
    h["cpu_util_pct"] = psutil.cpu_percent(interval=1)
    h["idle_ram_gb"] = round(vm.available / 1e9, 1)
    h["free_ram_gb"] = round(vm.available / 1e9, 1)
    h["idle_ram_mb"] = int(vm.available / 1e6)
    h["cpu_pct"] = h["cpu_util_pct"]
    with io.open(hp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(h, fh, ensure_ascii=False, indent=1)

    # self-verify epoch int + T-sep (smoke F7 gate)
    h2 = json.load(io.open(hp, encoding="utf-8"))
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "clock_read T-sep ISO"
    assert h2["n_orders_ack"] == 83
    print("closeout written: report line + state r268 + heartbeat epoch=%d" % EPOCH)


if __name__ == "__main__":
    main()
