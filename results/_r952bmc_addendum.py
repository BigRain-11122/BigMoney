# r952 addendum: orders watermark advance (mid-round @bm-c append order consumed) + addon rider note
import json, time, datetime

ST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
d = json.load(open(ST, encoding="utf-8"))
ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
d["last_orders_sha"] = "4aebbfc3f5a1b5b48c497c1f2f7c938ddf05d58f340442c2ec0b6b0423bcb84d"
d["last_orders_sha_method"] = "sha256 origin blob fresh-read r952 addendum (Seedance harvest + @bm-c append 4-shot row consumed + EXECUTED same-window)"
d["last_orders_read_at"] = ts
d["last_orders_seen"] = ts
d["orders_ack_receipt"] = ("r952: ORD delta TRUE consumed x2 this window (ce3cfa1d Seedance-rescue informational row + 4aebbfc3 @bm-c append order row); "
                           "append order EXECUTED same-window: bmc_addon_r952.py PID 50376 launched 03:33 (4 face-close-up clips D02_she_reads/D03_two_worlds/B01_weary/E03_gaze_meet, "
                           "local INT8 768P, prompts=mv_full_shots.py three-field canon, full-name tags per collection-naming law, D02 SUBMITTED 03:33:39, ETA all-4 ~06:05 < 07:45 deadline); unacked=0; dec fb5825cb FALSE hold")
d["last_round_summary"] = ("r952: harvest QC R01 8.0 PASS locked / C02_v4 7.3 FAIL disclosed / C09 3.5 FAIL frame-level -> track-2 regen merge + "
                          "MID-ROUND @bm-c append order consumed+executed (4 face-shot INT8 re-burns vs Seedance moderation wall, rider PID 50376, 07:45 deadline)")
d["last_round_summary_at"] = ts
d["current_task"] = "r952 closeout + add-on rider PID 50376 burning 4 face re-burns (D02 submitted 03:33:39) + factory R02 burning + r951b rider C04_v2 burning"
d["current_task_at"] = ts
d["now_active"] = "2026-10-13 03:3x | r952 | bm-c: harvest QC done + @bm-c append order executed (4 face re-burns rider PID 50376) + factory R02/rider C04_v2 burning; counter 952->953"
d["activity_now"] = d["now_active"]
d["prod_lanes"] = ("GPU=CEO deathline i2v: 16/21 landed+QC'd + R02 burning + R03-R06 queued + r951b rider (C04_v2 burning, C06_v2/C07_v2 queued) + "
                   "ADDON-R952 rider PID 50376 (4 Seedance-moderation-rejected face shots D02/D03/B01/E03 local INT8, 07:45 deadline, D02 submitted 03:33:39, ETA ~06:05) + "
                   "C02 best-of v4 7.3 disclosed; C03+C09 track-2 frame-regen armed post-drain (~06:00+, deathline-disclose if late); 06:30 closeout 08:30 CEO screen; "
                   "CPU=N1 W226 complete, W227 seat RAM-arbitration-deferred per O-20261012-2330-2 (freeRAM <4G gate)")
d["r952_addon_note"] = ("r952 addendum: S7 收尾双扫 caught mid-round ORD row 10-13 03:4x (@bm-c 追加 4 镜改本地·Seedance content_moderation 拒人脸近景 4/15=D02/E03/B01/D03·"
                         "引擎矩阵新行=云端人脸镜死路·本地 INT8 唯一活路) -> consumed + executed same-window: bmc_addon_r952.py (reuses bmc_night_factory verbatim, "
                         "sequential self-interleave, full-name tags per 收片命名律, seeds 9213-9216, life-pulse positive phrasing on face shots); "
                         "assembly clock acknowledged: 06:43 first assembly + 4 镜落位即重装配 -> 08:30 deathline; watermark orders sha ce3cfa1d->4aebbfc3 consumed this window")
with open(ST, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print("state addendum written, epoch still int:", isinstance(d["heartbeat_epoch_utc"], int))

RP = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
with open(RP, encoding="utf-8") as f:
    lines = f.read().splitlines()
assert lines and "r952" in lines[-1], "tail anchor: expected r952 line, got: " + (lines[-1][:60] if lines else "EMPTY")
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
row = (now + " | r952-addendum | bm-c: S7 收尾双扫 caught mid-round @bm-c append order (10-13 03:4x orders row 4aebbfc3) -> consumed + EXECUTED same-window: "
        "bmc_addon_r952.py PID 50376 launched 03:33 (4 Seedance-moderation-rejected face close-ups D02_she_reads/D03_two_worlds/B01_weary/E03_gaze_meet -> local INT8 768P, "
        "prompts=mv_full_shots.py three-field canon + life-pulse positive phrasing, full-name tags per 收片命名律, seeds 9213-9216, D02 SUBMITTED 03:33:39, ETA all-4 ~06:05 < 07:45 deadline) | "
        "engine-matrix new row consumed: cloud face shots = dead lane (content_moderation), local INT8 = only lane | assembly clock ack: 06:43 first assembly + 4 镜落位即重装配 -> 08:30 deathline | "
        "orders watermark ce3cfa1d->4aebbfc3 consumed | [r952 bm-c addendum]")
with open(RP, "a", encoding="utf-8", newline="\n") as f:
    f.write(row + "\n")
print("RP addendum appended")
