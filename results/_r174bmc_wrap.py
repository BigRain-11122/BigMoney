# -*- coding: utf-8 -*-
"""r174 bm-c wrap: heartbeat + state + orders_ack (5 new orders)."""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
NOW_EPOCH = int(time.time())
NOW = time.strftime("%Y-%m-%d %H:%M:%S")
NEW_ORDERS = ["O-20260928-1614-bm-a.md", "O-20260928-1625-bm-a.md",
              "O-20260928-1630-bm-a.md", "O-20260928-1640-bm-a.md",
              "O-20260928-1655-bm-a.md"]


def ps_num(cmd):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                             capture_output=True, text=True, timeout=30)
        return float(out.stdout.strip())
    except Exception:
        return None


def main():
    missing = [o for o in NEW_ORDERS
               if not os.path.exists(os.path.join(ROOT, "fleet", "orders", o))]
    if missing:
        print(f"REFUSE: orders missing locally (pull first): {missing}",
              file=sys.stderr)
        return 2
    free_ram = ps_num("[math]::Round((Get-CimInstance Win32_OperatingSystem)"
                      ".FreePhysicalMemory/1MB,2)")
    cpu_pct = ps_num("(Get-CimInstance Win32_Processor | Measure-Object "
                     "-Property LoadPercentage -Average).Average")
    gpu_free = None
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.used",
             "--format=csv,noheader,nounits"], capture_output=True, text=True,
            timeout=15)
        tot, used = [float(x.strip()) for x in out.stdout.strip().split(",")[:2]]
        gpu_free = round(tot - used)
    except Exception:
        pass

    # ---- heartbeat (own file only) ----
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hp, encoding="utf-8") as f:
        hb = json.load(f)
    ack = hb.setdefault("orders_ack", [])
    for o in NEW_ORDERS:
        if o not in ack:
            ack.append(o)
    hb["last_seen"] = NOW_ISO
    hb["heartbeat_epoch_utc"] = NOW_EPOCH          # MUST be JSON int (F7)
    hb["clock_read"] = NOW_ISO                       # T-separated (F7/F5)
    hb["round_no"] = 174
    hb["cpu_util_pct"] = cpu_pct
    hb["cpu_pct"] = cpu_pct
    hb["free_ram_gb"] = free_ram
    hb["idle_ram_gb"] = free_ram
    hb["gpu_free_vram_mb"] = gpu_free
    hb["gpu_idle_vram_mb"] = gpu_free
    hb["current_task"] = ("r174 closed: T-107 slice-1 landed (audit v2.4 "
                         "supply-family + utilization face + disabled-heal) "
                         "+ T-108 claim D2-design + 5 CEO orders acked; "
                         "next = T-108 D2 resident dispatcher code + T-107 "
                         "slice-2 fill ladder + bar-landing paper chain")
    hb["verdict"] = ("green: 5 CEO orders same-window acked (O-1614/1625/"
                     "1630/1640/1655); T-107 slice-1 same-round (audit v2.4 "
                     "selftest 25/25 + live supply_gap flag fired = "
                     "O-1625 miss-face closed + utilization report face "
                     "first product + loop-task disabled-heal); T-108 "
                     "claim-and-start (D2 design in-ticket); W1-JUDGE flip "
                     "lawful yield to bm-a r398-cont live ignite; T-103 "
                     "yield to bm-b 16:06 prior claim; T-109 not claimed "
                     "(two P0 in hand anti-pile-up, bm-a/bm-b fit-present, "
                     "T-106 input faces ready zero-block); S6 full chain "
                     "rc=0 (no new bar honest: mid-autumn 09-25 closed + "
                     "today bar not yet at source 16:42)")
    hb["updated_at"] = NOW_ISO
    with open(hp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    assert isinstance(json.loads(open(hp, encoding="utf-8").read())
                      ["heartbeat_epoch_utc"], int), "epoch must be int"

    # ---- state (own file only) ----
    sp = os.path.join(ROOT, "state-bm-c.json")
    with open(sp, encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = 174
    st["updated"] = NOW_ISO
    st["note"] = ("r174: five-CEO-order saturation window. (1) O-1614/1625 "
                  "receipts: W1-JUDGE 4-shard flip executed then LAWFULLY "
                  "YIELDED to bm-a r398-cont live claim+ignite (rebase "
                  "conflict resolved checkout --ours = in-flight state "
                  "kept); V2-P1 ignition confirmed claimed bm-b 16:18:31. "
                  "(2) T-107 claim + slice-1 SAME round: compute_audit v2.4 "
                  "(supply_gap 8th flag never-CLEAN + 15min window + "
                  "supply_floor + ignition_sla legs + streak escalation; "
                  "selftest 25/25; live fire correct: supply_gap span "
                  "891.7min = the O-1625 miss-face now surfaced) + "
                  "daily_report sec.5 utilization face (selftest PASS, "
                  "same-day first product) + COMPUTE_AUDIT sec.8.4 + "
                  "register_loop_task disabled-state heal (MSG-1622 root "
                  "cause; idempotent run = phase ok no-op). (3) T-108 "
                  "claim-and-start: D2 resident-dispatcher design decisions "
                  "landed in-ticket (30s precheck, quiescence guards, "
                  "reuse autofill engine, pythonw zero-window). (4) T-109 "
                  "NOT claimed: anti-pile-up (two P0s in hand) + bm-a/"
                  "bm-b fit-present + T-106 input faces ready. (5) S6 "
                  "chain rc=0: no new bar honest (mid-autumn 09-25 closed, "
                  "today bar absent at source 16:42 -> next-round retry), "
                  "LHB +40 rows cutoff->09-28, fund_premium no-op (NAV "
                  "09-24 covered), lane guards honest no-ops.")
    st["did"] = ("S0-1 anchor -> S0 pull+rebase x2 -> S0.5 five CEO orders "
                 "(O-1614/1625/1630/1640/1655) -> S1 smoke 25/25 -> S2 T-107 "
                 "+ T-108 claims -> S3 slice-1 (audit v2.4 + report face + "
                 "charter + heal) -> S6 chain rc=0 -> S7 heartbeat/state")
    st["verify"] = ("push 61404360 (T-107 slice-1 + T-108 claim) + 7008155e "
                    "(flip yield + T-107 claim); compute_audit selftest "
                    "25/25; daily_report selftest PASS + same-day run; "
                    "register_loop_task phase-ok no-op; smoke 25/25; "
                    "heartbeat epoch int-verified")
    st["next"] = ("r175 = T-108 D2 resident dispatcher CODE build + "
                  "registration on bm-c (30s ignition per O-1630); T-107 "
                  "slice-2 fill-ladder generator + audit SLA 60s tighten "
                  "with D2; T-109 watch (bm-a/bm-b claim expected); "
                  "bar-landing legs (daily 09-28 bar retry + paper chain) "
                  "next round")
    st["last_round_ts"] = NOW_ISO
    st["current_task"] = hb["current_task"]
    with open(sp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)

    print(json.dumps({"heartbeat": "ok", "epoch_int": NOW_EPOCH,
                      "clock_read": NOW_ISO, "orders_acked_new": len(
                          NEW_ORDERS), "ram_gb": free_ram,
                      "gpu_free_mb": gpu_free}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
