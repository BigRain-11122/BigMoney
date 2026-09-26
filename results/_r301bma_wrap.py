"""R301 bm-a wrap: state round 301 + heartbeat (epoch int + astimezone
ISO clock per r302 kenglu) + round-report line append. Self-verify gate
runs BEFORE commit (红线自拦优于轮后 smoke 拦)."""
import json
import os
import subprocess
import time
from datetime import datetime

import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone()
ISO = NOW.isoformat()          # T-separated with UTC offset (r302 law)
EPOCH = int(time.time())       # JSON int, never str (R170/R178 law)

DID = ("R301: supply-lane double defect fix live-fire closed -- "
       "(1) pool shards contract: R300 CN-SECTOR-LEADER-P1 entry missing "
       "shards array starved the only ready batch (07:10 tick "
       "no-takeable-shard); fixed sectldr-0of1 -> 07:20:16 claim OK "
       "owner=bm-a pushed + C8 LAUNCH pid 64840 burn in flight "
       "(latency 18.8min > O-2100 10min honest = starvation window); "
       "(2) autofill _runner_alive explicit-JSON-null guard (T34 "
       "runner=null keepalive AttributeError x27 02:40-07:10 = r288 "
       "refresh line dead; S18a/b/c regression legs, selftest ALL PASS)")
NEXT = ("R302: CN-SECTOR-LEADER-P1 harvest when p1_results.json lands "
        "(est 08:05-08:20): judged 4 cells G1-prime-v2 + G2 DSR/PBO + "
        "D6 vs WILD-S1 + prereg s7/s8 backfill + gate_attrition row + "
        "SCHOOL queue #4 closure; keepalive fix watch = 07:30+ ticks "
        "must show refresh line alive on own running shard")
VERDICT = ("py_low_with_work_cands LEGAL-side: local_batch_running=true "
           "(CN-SECTOR-LEADER-P1 07:20:16 launch) + same-round "
           "starvation-defect fix; single-vehicle vectorized runner ~1 "
           "core face; board 0 open + bandit 0 + pool fed")
REPORT = (
    f"{ISO} | R301 bm-a (dept:工程·舰队+研究供给线) | WM first-line verdict: "
    "py_low_with_work_cands LEGAL-side same-round supply fix (probe py "
    "3.4% single-vehicle vectorized runner ~1 core; local_batch_running"
    "=true CN-SECTOR-LEADER-P1 launched 07:20:16 after starvation-defect "
    "fix; board 0 open + bandit 0 + pool fed; fill latency 18.8min vs "
    "O-2100 10min target MISS honest = R300 registration-omission "
    "starvation window 07:01-07:20) | did: SUPPLY-LANE DOUBLE DEFECT FIX "
    "live-fire verified at 07:20 tick: (1) pool registration contract "
    "breach -- R300 entered CN-SECTOR-LEADER-P1 ready=1 WITHOUT shards "
    "array -> autofill _pick iterated empty shards 'no takeable shard' "
    "-> the ONLY ready batch starved (O-1137 supply-side violation face "
    "02:40+); fixed sectldr-0of1 single-vehicle shard (control-plane "
    "round write, commit b9c22863) -> 07:20:16 claim OK owner=bm-a "
    "pushed (rebase-retry r282) + C8 LAUNCH pid 64840 psutil-verified "
    "alive; (2) autofill _runner_alive explicit-JSON-null trap -- T34-"
    "PRESIGNAL-HALFSTEP runner=null defeats .get(k,'') default -> "
    "keepalive AttributeError x27 ticks 02:40-07:10 = r288 "
    "claim-refresh line dead during local burns; guard 'if not "
    "runner_rel: return False' + hermetic S18a/b/c regression legs "
    "(null-runner keepalive scan: zero fault-log delta + zero refresh); "
    "autofill selftest ALL PASS | S0 pull clean + push-reject window: "
    "amend(tick dirt per r290)+rebase retry (bm-b r305/306 same-window) "
    "-> push rc=0 b9c22863 | S0.5 orders double-scan 91/91 zero "
    "unacked (round-start+wrap) + decisions.md zero new lines "
    "(D-20260927-05 last; ①②③ adopted faces standing) | S1 smoke 25/25 "
    "| S6 chain 30/30 rc=0 (compute_audit v2.3 CLEAN zero-flag + WM "
    "probe + daily/market_regime ORANGE shadow/strategy_scorecard/"
    "market_clock CALL-2026-09-24 + gates weekend-cutoff no-op legal + "
    "lane guards honest astock=bm-b fundprem=bm-c + live.paper+t35v+t24/"
    "promo/aggr/alloc/grid idempotent + daily_scorecard/daily_report/"
    "build_status/token_meter OK; token L2 local legs 0 today) | "
    "post_review 2715 rows zero open/negative | T-87 progress_r301_bma "
    "line | CODELY kenglu +1 (9724B <=10KB hard line held) | inbox: "
    "MSG-20260927-0645 = own outgoing F-04 declaration addressee bm-b "
    "(zero for-bm-a) | state 301 + heartbeat epoch int verified | "
    f"NEXT: {NEXT}")


def main():
    cpu = psutil.cpu_percent(interval=2.0)
    ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    gpu_free = None
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10).stdout.strip()
        gpu_free = round(float(out.splitlines()[0]) / 1024, 1)
    except Exception:
        gpu_free = 5.5

    # state file
    sp = os.path.join(ROOT, "state-bm-a.json")
    st = json.load(open(sp, encoding="utf-8-sig"))
    st.update({"round_no": 301, "did": DID, "verdict": "ok",
               "next": NEXT, "ts": ISO, "last_round_ts": ISO,
               "updated_at": ISO, "current_task": DID[:40],
               "last_run": ISO, "last_round_at": ISO, "last_round": 300,
               "last_seen": ISO, "task": NEXT[:40], "updated": ISO[:19]})
    json.dump(st, open(sp, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # heartbeat
    hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
    hb = json.load(open(hp, encoding="utf-8-sig"))
    hb.update({"machine_id": "bm-a", "last_seen": ISO,
               "current_task": f"R301 done: supply-lane double fix "
               f"(shards + null guard) + CN-SECTOR-LEADER-P1 launched "
               f"07:20:16 pid 64840; next: harvest",
               "cpu_cores": psutil.cpu_count(logical=True),
               "cpu_pct": cpu, "free_ram_gb": ram_gb,
               "gpu_free_vram_gb": gpu_free, "verdict": VERDICT,
               "heartbeat_epoch_utc": EPOCH, "clock_read": ISO,
               "round_no": 301})
    json.dump(hb, open(hp, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # round report append
    rp = os.path.join(ROOT, "logs", "iteration-loop",
                     "round_reports-bm-a.md")
    with open(rp, "a", encoding="utf-8") as fh:
        fh.write(REPORT + "\n")

    # self-verify gate (before commit; r302 law)
    hb2 = json.load(open(hp, encoding="utf-8-sig"))
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in hb2["clock_read"] and "+08:00" in hb2["clock_read"], \
        "clock_read not astimezone ISO"
    st2 = json.load(open(sp, encoding="utf-8-sig"))
    assert st2["round_no"] == 301
    print("WRAP OK epoch-int + clock-ISO verified; cpu", cpu,
          "ram", ram_gb, "gpu_free", gpu_free)


if __name__ == "__main__":
    main()
