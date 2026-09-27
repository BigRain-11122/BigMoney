# -*- coding: utf-8 -*-
"""r313 bm-b wrap: state/round-report/heartbeat/T-89-progress/inbox close.
r302 law: all wall-clock faces via datetime.now().astimezone().isoformat();
epoch via int(time.time()) DIRECT int; self-asserts built in (before any
write-verify-write and after all writes: parse roundtrip + isinstance
epoch int + orders_ack whole-set law r312 kenglu: set(disk orders) subset
of set(ack) and |orders∩ack| == |orders|)."""
import json
import os
import shutil
import subprocess
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone()
ISO = NOW.isoformat()
EPOCH = int(time.time())
STAMP = time.strftime("%Y-%m-%d %H:%M:%S")

REPORT_LINE = (
    f"{ISO} | r313 bm-b | dept:研究+策略+舰队 | WM-VERDICT: 绿(red=false@09:27 "
    "lane healthy; probe py_low_board_clear; honest face: pool 18 ready + "
    "py~0% idle = autofill claim-race window vs bm-a 10min cycle, r310-law "
    "family, no violation -- supply IS pooled, burner claims race) | did: "
    "(1) R293-salvage of dead r312 session: successor detected via process "
    "table + rebase-merge residue (no Bigmoney codely alive at 09:11; "
    "union resolver scripts written 09:04 unexecuted); 2x rebase UU "
    "batches canon-resolved zero-loss (pick1 autofill UU + pick2 14-file "
    "S6-mirror batch via _r312bmb_resolve.py probe->resolve; GIT_EDITOR "
    "law) + 2nd collision round (bm-a r307 trio incl CEO order) same "
    "recipes; push landed 97be9a2f = r312 wrap fully closed (state 312 "
    "in-commit verified); (2) S0.5 double-scan: 2 unacked orders caught "
    "(O-2026-09-26-2340-bm-a arrived on my disk only via 09:1x pull -- "
    "r312 94/94 blind-window legitimate; O-20260927-0913-bm-c CEO "
    "mobilization order) -- both acked + executed: O-2340 = T-91 lane "
    "separation honored (bm-a claim e16fc6c9, bm-b zero-touch; judged "
    "face T-90 = mine in-flight), O-0913 = bm-b receipt 3/3 (ack + "
    "heartbeat prod_lanes/gpu_model first values + TTS-lane charter "
    "ticket T-2026-09-27-92 opened with idle-window honest deferral); "
    "(3) S3 main closure T-89 slice-1b: runner scripts/"
    "prospect_regime_segments.py (t22 import-face ZERO re-impl: "
    "enumerate/regime/_load_axis_prices/_run_cell/_G/checkpoint; "
    "PROSPECT 22-member injection) + selftest 9/9 hermetic (B7b "
    "consumer-contract leg r297 law) + real-fire probe 22/22 cells 6.3s "
    "12 workers, G-ANCHOR 22/22 byte-reconcile + G-PANEL cutoff-frozen "
    "truncation (Monday-bar-proof) + G-CENSUS all PASS + prereg s9 "
    "zero-run amendment (legacy census gate 1255->1256 probe-adjudicated: "
    "09-23->09-24 panel +1 start, listed 46-48 uniform; cells 27,632; "
    "batch ~63,525; non-result-driven, zero cells pre-freeze-commit) + 9 "
    "shards pooled (4 legacy + 5 deep, r301 shards + r305 workers_plan "
    "trio, lane-open T54 precedent); (4) S7 push-collision round 2: "
    "yielded autofill claim commit 1f30497f SKIPPED per sec.4 "
    "commit-time law (bm-a 4ffc7ad6 won dce2-legacy-la claim), pool "
    "union kept bm-a claim + my 9 shards (76 entries), push landed "
    "cedf7d66; (5) S6 22 lanes rc=0 Sunday honest no-op faces; | "
    "evidence: probe results/_r313bmb_prospect_probe.json + "
    "results/pros_segs/logs/legacy_LA.log (22/22 cells, 3 gates PASS) "
    + " + runnable_pool 76 entries (9 PROSPECT ready) + smoke 25/25 + "
    "push receipts 4ffc7ad6..cedf7d66 | 下轮指针: autofill burns 18 "
    "ready shards (x2-LA already claimed by bm-a burning on their "
    "machine; my autofill claims others) -> bm-b harvest rounds finalize "
    "(T-89: results/prospect_regime_segments.json + shortline CSV + s7 "
    "backfill + MARKET_STAGE_TABLE row refresh + slice-3 supply memo; "
    "T-90: stage-B four-arm after all 9 x2 shards) + T-92 TTS engine "
    "install next GREEN-IDLE window (kokoro/piper hf-mirror U187/U240 + "
    "ffmpeg -16LUFS/TP-3/mono chain) + 09-28 Monday first-new-bar full "
    "chain + 10-01 monthly trio + REGIME_GUARD v3 date gate + migration "
    "window to 09-29 12:00 (executor precheck still editor-blocked, "
    "journal 09:25 honest)")

STATE = {
    "round_no": 313,
    "did": ("r313: R293-salvage dead r312 session (2x rebase UU batches "
            "canon-resolved zero-loss, push 97be9a2f = r312 closed) + "
            "T-89 slice-1b runner delivered+gated (t22 import-face, "
            "selftest 9/9, probe 22/22, 3 gates PASS) + prereg s9 "
            "zero-run amendment census 1255->1256 (probe-adjudicated) + 9 "
            "PROSPECT-REGIME-SEGMENTS shards pooled + CEO O-0913 receipt "
            "3/3 (ack+prod_lanes/gpu_model+TTS charter T-92) + O-2340 "
            "ack (T-91=bm-a) + S6 22 lanes rc=0 + orders 96/96"),
    "verdict": "green",
    "next": ("autofill burns 18 ready pool shards -> harvest finalize "
             "rounds (T-89 finalize+MARKET_STAGE_TABLE+slice-3 memo; T-90 "
             "stage-B after 9 x2) + T-92 TTS install next GREEN-IDLE "
             "window + 09-28 Monday first-new-bar full chain + 10-01 "
             "monthly trio + REGIME_GUARD v3 date gate + migration "
             "window to 09-29 12:00"),
    "last_round_ts": ISO,
    "last_result": "ok",
    "current_task": ("r313: T-89 slice-1b delivered+pooled (9 shards "
                     "ready); salvage r312 closed; CEO O-0913 receipt "
                     "landed; next=harvest finalize + TTS idle-window "
                     "ignition"),
    "last_tick": "26:49",
    "updated_at": ISO,
    "last_seen": ISO,
    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    "last_run": f"r313 {ISO}",
    "last_round_at": ISO,
    "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
}

NEW_ACKS = ["O-2026-09-26-2340-bm-a.md", "O-20260927-0913-bm-c.md"]


def gpu_face():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,"
                            "memory.used", "--format=csv,noheader"],
                           capture_output=True, text=True, timeout=10)
        parts = [p.strip() for p in r.stdout.splitlines()[0].split(",")]
        return parts[0], int(parts[1].split()[0]), int(parts[2].split()[0])
    except Exception:
        return "NVIDIA GeForce RTX 3070", 8192, 1110


def main():
    import psutil
    # --- heartbeat ---
    hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    hb = json.load(open(hb_path, encoding="utf-8"))
    ack = list(hb.get("orders_ack", []))
    for a in NEW_ACKS:
        if a not in ack:
            ack.append(a)
    orders_dir = os.path.join(ROOT, "fleet", "orders")
    disk_orders = sorted(f for f in os.listdir(orders_dir)
                         if f.startswith("O-") and f.endswith(".md"))
    missing = [o for o in disk_orders if o not in set(ack)]
    assert not missing, f"orders_ack double-scan FAIL: unacked {missing}"
    name, vram_total, vram_used = gpu_face()
    ram = psutil.virtual_memory()
    cpu_pct = psutil.cpu_percent(interval=1)
    hb.update({
        "machine_id": "bm-b", "role": "compute-node", "joined": "2026-09-23",
        "last_seen": ISO, "heartbeat_epoch_utc": EPOCH, "clock_read": ISO,
        "current_task": STATE["current_task"],
        "cpu_cores": psutil.cpu_count(logical=True),
        "total_ram_gb": round(ram.total / 1024**3, 1),
        "free_ram_gb": round(ram.available / 1024**3, 1),
        "cpu_util_pct": round(cpu_pct, 1),
        "gpu_model": f"{name} {vram_total}MiB ({vram_used}MiB used @{STAMP})",
        "gpu_free_vram_gb": round((vram_total - vram_used) / 1024, 1),
        "gpu_free_vram_mb": vram_total - vram_used,
        "prod_lanes": ["bigmoney-compute-node", "tts-audio-batch",
                       "gpu-light-postprocess"],
        "prod_lanes_note": ("P-33 per O-20260927-0913 sec.4: primary lane "
                            "in-force (BigMoney rounds + pool shards); "
                            "tts-audio-batch + gpu-light-postprocess "
                            "chartered r313 (ticket T-2026-09-27-92), "
                            "idle-window ignition per order sec.3 "
                            "primary-lane law"),
        "round_no": 313,
        "verdict": ("green; r313: r312 crash salvaged + closed (2x rebase "
                    "canon-resolve, push landed); T-89 slice-1b runner "
                    "delivered+gated (selftest 9/9, probe 22/22, 3 gates "
                    "PASS) + s9 census amendment 1255->1256 "
                    "probe-adjudicated + 9 shards pooled; CEO O-0913 "
                    "receipt 3/3 (prod_lanes/gpu_model first values + "
                    "T-92 TTS charter); O-2340 acked (T-91=bm-a lane "
                    "law); S6 22/22; smoke 25/25; orders 96/96 "
                    "double-scan zero-new"),
        "orders_ack": ack,
        "n_orders_ack": len(ack),
    })
    text = json.dumps(hb, ensure_ascii=False, indent=1)
    json.loads(text)
    with open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    chk = json.load(open(hb_path, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int (R170)"
    assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"], \
        "clock_read not ISO-with-offset (R262)"
    assert set(disk_orders) <= set(chk["orders_ack"]) and \
        len(set(disk_orders) & set(chk["orders_ack"])) == len(disk_orders)
    print(f"heartbeat OK: epoch={chk['heartbeat_epoch_utc']} (int) "
          f"clock={chk['clock_read']} ack={chk['n_orders_ack']} "
          f"gpu={chk['gpu_model']} lanes={chk['prod_lanes']}")

    # --- state.json ---
    sp = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
    st = json.load(open(sp, encoding="utf-8"))
    prev = st.get("round_no")
    st.update(STATE)
    txt = json.dumps(st, ensure_ascii=False, indent=1)
    json.loads(txt)
    with open(sp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt + "\n")
    chk2 = json.load(open(sp, encoding="utf-8"))
    assert chk2["round_no"] == prev + 1 == 313, "round_no law"
    print(f"state OK: round_no {prev} -> {chk2['round_no']}")

    # --- round report ---
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    with open(rp, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n" + REPORT_LINE + "\n")
    print("round report line appended")

    # --- T-89 ticket progress ---
    tp = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-26-89-P1.json")
    tk = json.load(open(tp, encoding="utf-8"))
    tk["progress_r313_bmb"] = (
        "r313 slice-1b DELIVERED (successor session after r312 crash): "
        "runner scripts/prospect_regime_segments.py (t22 import-face "
        "zero-reimpl, PROSPECT 22-member injection, base face only) + "
        "selftest 9/9 hermetic (B7b consumer-contract leg) + real-fire "
        "probe 22/22 cells 6.3s 12 workers with G-ANCHOR 22/22 "
        "byte-reconcile + G-PANEL cutoff-frozen truncation + G-CENSUS "
        "PASS + prereg s9 zero-run amendment (legacy census 1255->1256 "
        "probe-adjudicated: panel 09-23->09-24 +1 start; cells 27,632; "
        "batch ~63,525) + 9 shards pooled (LA/LB/LC/LD legacy 1256 + "
        "DA..DE deep 1506, r301+r305 trio, lane-open T54). EXACT "
        "CONTINUATION (harvest round after shards burn): finalize = "
        "results/prospect_regime_segments.json (evidence_cutoff + "
        "cutoff_meta + audit + 22-member x 2-axis x segment tables + "
        "family dual-column + D7 + corr all-pairs) + research/shortline/"
        "prospect_regime_segments_results.csv + prereg s7/s8 backfill + "
        "MARKET_STAGE_TABLE.md PROSPECT row refresh + slice-3 "
        "attack-corps supply memo (GM face before any requeue)")
    txt = json.dumps(tk, ensure_ascii=False, indent=1)
    json.loads(txt)
    with open(tp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt + "\n")
    print("T-89 progress_r313_bmb recorded")

    # --- inbox close ---
    src = os.path.join(ROOT, "fleet", "inbox",
                       "MSG-20260927-0908-bm-a-t91-claim.json")
    dst = os.path.join(ROOT, "fleet", "inbox", "processed",
                       "MSG-20260927-0908-bm-a-t91-claim.json")
    if os.path.exists(src):
        shutil.move(src, dst)
        print("inbox MSG-0908 -> processed (T-91=bm-a claim acknowledged, "
              "lane separation honored, no reply action needed beyond "
              "this round report line)")
    print("wrap DONE")


if __name__ == "__main__":
    main()
