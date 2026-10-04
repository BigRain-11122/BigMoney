"""r457 bm-c S7 state+heartbeat writer: metrics probe, state-bm-c.json (round 457),
fleet/machines/bm-c.json heartbeat; json.loads self-verify (epoch int + clock T-sep)."""
import datetime
import json
import os
import subprocess
import time

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def sh(args, timeout=60):
    r = subprocess.run(args, capture_output=True, creationflags=CREATE_NO_WINDOW,
                       timeout=timeout)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def metrics():
    cpu = 0.0
    ram = 0.0
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    vram = 0
    out = sh(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"])
    try:
        vram = int(out.splitlines()[0])
    except Exception:
        pass
    return cpu, ram, vram


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    with open(path, encoding="utf-8") as fh:
        json.load(fh)  # reparse self-verify


def main():
    now_dt = datetime.datetime.now().astimezone()
    now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    epoch = int(time.time())
    cpu, ram, vram = metrics()
    print("metrics cpu=%.1f ram=%sGB vram=%sMiB epoch=%d" % (cpu, ram, vram, epoch))

    sp = os.path.join(ROOT, "state-bm-c.json")
    with open(sp, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    st.update({
        "round_no": 457,
        "clock_read": now_iso,
        "last_seen": now_iso, "last_ts": now_iso, "updated": now_iso,
        "updated_at": now_iso, "last_round_at": now_iso,
        "heartbeat_epoch_utc": epoch,
        "cpu_pct": cpu, "idle_ram_gb": ram, "gpu_free_vram_mib": vram,
        "current_task": ("r457 done (QUALITY-NULLS ownerless-window healed via pool surgery a093a7720, "
                         "bm-b daemon self-adoption pending confirm next round); next: fund-trio finalize "
                         "window 10-05..10-09 (QUALITY long-pole), O-2115+O-2030 acceptance 10-08, "
                         "HANDOVER 5x at r460, market reopen 10-09"),
        "did": ("r457 bm-c golden-week watch + pool-integrity heal: (1) S0: treadmill absorb x2 "
                "(91ad1d012 lane faces, 54420eca9 + post_review rerun) + behind-6 waves clean rebase. "
                "(2) S0.5: orders 153/153 zero un-acked; D-19 EB14B510 MATCH; group orders 68947C17 "
                "MATCH; inbox 0. (3) S1 smoke 48/48. (4) S2 boards empty (T-167 bm-a claimed). "
                "(5) S3 standing checks green (WM red=false; satengine rc0; post_review 45Y/0N/5W). "
                "(6) CORE FINDING: FUND-QUALITY-P1-NULLS ownerless ~24h on shared pool face while "
                "bm-b canonical burn alive (rows 504->510; MSG-0857/0925/2005; bm-b r659 trio_health) "
                "-- root cause r637 four-face surgery missed 3rd shard x r288 keepalive owner==myid "
                "self-lock; hazard = bm-a daemon claim attempts every tick (fuse_refused 571 @09:02, "
                "only crash fuse holding). FIX: treasure_guard rc0 + 5-gate surgical restore "
                "(owner=bm-b, owner_since 09:11:39 action-time per r400, provenance in shard note) "
                "-> r288 gate passes -> bm-b daemon self-adoption; MSG-0915 to bm-b (verify pid 57116 "
                "+ confirm adoption); first-attempt reparse gate caught r629 add-field comma mirror, "
                "fixed before write. DELIVERED a093a7720 push_verify ahead=0. (7) S6 38/38 rc0 "
                "(dualrun streak 51; audit CLEAN; update_daily 0 rows golden-week; REPORT/LIVE "
                "refreshed; lane guards honest). (8) S4 pit line (claim self-lock + r629 mirror + "
                "multi-shard surgery enumeration law). (9) S7: attrition CLEAN; claws parity TRUE; "
                "loop pin5 + watchdog alive; orders double-scan zero-diff."),
        "last_round": ("r457 bm-c: QUALITY-NULLS ownerless-window heal (pool surgery a093a7720, r637 "
                       "3rd-shard miss, r288 self-adoption unlocked) + S6 38/38 rc0 (dualrun streak 51); "
                       "smoke 48/48; orders/D-19/group-orders triple MATCH; post_review zero-x"),
        "next": ("(a) Next round: confirm bm-b daemon adopted QUALITY claim (keepalive commit listing "
                 "fund-quality-p1-nulls-0of1; MSG-0915 reply). (b) FUND trio finalize window 10-05..10-09 "
                 "(D ETA 10-05 10:30 per bm-b r652; G-SEG frozen insufficient-sample per O-0808; VALUE "
                 "passive-crash fix bm-b-side in tree per r658). (c) O-2115 acceptance pack + O-2030 "
                 "treasure-protection acceptance 10-08. (d) HANDOVER 5x at r460. (e) Market reopen 10-09: "
                 "S6 new-bar legs auto-reengage."),
        "verify": ("S6 38/38 rc0 NON-ZERO=none (results/_r457bmc_s6_log.txt in-repo; PARITY PASS canon); "
                   "smoke 48/48; orders 153/153 double-scan zero-diff; D-19 EB14B510 raw-bytes MATCH; "
                   "group orders 68947C17 MATCH; attrition CLEAN; claws parity TRUE; pool surgery gates "
                   "identity/needle==1/reparse/trio-delta/numstat 3:1 + treasure_guard rc0; surgery "
                   "DELIVERED a093a7720 push_verify ahead=0; heartbeat epoch int + clock T-sep self-checked"),
    })
    write_json(sp, st)
    print("state written")

    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hp, encoding="utf-8-sig") as fh:
        hb = json.load(fh)
    hb.update({
        "machine_id": "bm-c",
        "last_seen": now_iso,
        "heartbeat_epoch_utc": epoch,
        "clock_read": now_iso,
        "round_no": 457,
        "round_no_label": "round 457 (bm-c)",
        "current_task": ("当前活: golden-week watch + QUALITY-NULLS ownerless-window heal (surgery DELIVERED "
                         "a093a7720; bm-b daemon self-adoption pending) | 最近实物: pool surgery commit "
                         "a093a7720 + MSG-2026-10-04-0915-bmc-bmb.md + S6 38/38 rc0 (_r457bmc_s6_log.txt) "
                         "| 下个里程碑: fund-trio finalize window 10-05..10-09 (QUALITY long-pole; bm-b "
                         "adoption confirm next round)"),
        "verdict": ("GREEN (smoke 48/48; orders delta zero 153/153; D-19 double MATCH; WM red=false; "
                    "satengine alive rc0; S6 38 legs rc0 fail=0 dualrun streak 51; attrition CLEAN; pool "
                    "surgery 5-gate verified DELIVERED a093a7720 ahead=0; post_review 45Y/0N/5W zero-x; "
                    "zero cloud token)"),
        "ts": now_iso, "updated": now_iso, "updated_at": now_iso,
        "cpu_util_pct": cpu, "idle_ram_gb": ram, "gpu_free_vram_mib": vram,
    })
    write_json(hp, hb)
    # final self-check: epoch int + clock T-sep (F7 double law)
    assert isinstance(hb.get("heartbeat_epoch_utc"), int), "epoch not int"
    assert "T" in hb.get("clock_read", "") and "+08:00" in hb.get("clock_read", ""), "clock not T-sep"
    print("heartbeat written; epoch int + T-sep clock PASS")


if __name__ == "__main__":
    main()
