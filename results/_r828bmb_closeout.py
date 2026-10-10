# r828 bm-b closeout: state.json + heartbeat + round report (load-modify-save law)
import datetime as dt
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

NOW = dt.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")  # 2026-10-10T10:3x:xx+08:00 (T-separated)
EPOCH = int(time.time())

VERDICT = ("r828: product round - E8 futures calendar-spread monitor face delivered "
           "(9/9 pairs, selftest 14/14, panel cross-validated, 791 spread rows); "
           "smoke 49/49; S6 41 legs rc0 ZERO-DRIFT streak 13; watermark green "
           "(insufficient_history legal, pool ready 0); orders 60/60 zero unacked "
           "double sweep; DEC/ORD MATCH; attrition CLEAN; orphans=0; push-race "
           "rebase dual-batch canonical resolve LANDED (bm-a r950 same-window)")

DID = ("r828: E8 DELIVERED: scripts/futures_calendar_spread.py (calendar-spread "
       "monitor face, selftest 14/14 hermetic; 48 sina per-contract requests 0 "
       "failures, 2.5s rate limit; near/far = alive<=20d + OI 15% floor + far_thin "
       "fallback) + evidence results/futures_calendar_spread/{face.json,spreads.csv} "
       "(791 rows, panel cutoff 2026-10-09 aligned) + digest "
       "research/digests/DIGEST-20261010-e8-futures-calendar-spread.md; per-variety: "
       "IF/IC/IM/IH 2610/2612 backwardation -38.6..-127 (ratio 0.982-0.986), T/TF "
       "2612/2703 [far_thin] CTD carry -7..-9bp, RB 2701/2703 z=-2.14, AU 2612/2702 "
       "+2.4 contango, SC 2611/2612 deep backwardation -23.3 (ratio 0.968); "
       "basis(near-panel)=0.0 x6 + OI byte-identical (RB 1,673,458 / SC 23,669 / T "
       "377,917) = main-continuous panel three-way cross-validation; upstream latent "
       "key-slot bug (update_futures raw fallback reads OI from key 'o'=open, true "
       "key 'p') registered as tech T20, bm-a lane, not fixed here | claim lock "
       "3b5b3686b (T-18 probe CLEAR; bm-a r950 same-window probe = COLLISION_RISK on "
       "my in-flight E8 and YIELDED - probe first dual-end fleet live proof) | "
       "explore.md r827 record line-split + 3 path-missing-r birth defect healed "
       "(4 lines->1, artifact-existence verified, byte account 3LF out + 3r in) | "
       "push-race: delivery push hit bm-a r950 same-window (pre-push claw, non-FF) "
       "-> absorb + rebase dual-batch canonical resolve (batch1: tech.md T19 "
       "adjacent-row union HEAD-done + mine-T20; probe json take-HEAD bm-a "
       "COLLISION_RISK operative face; batch2: satengine 3 faces r609 stale-replay "
       "family - writer-pause window per bm-a r950-pre2 precedent, schtasks pause "
       "both daemons -> checkout --ours clean blobs -> json/jsonl validated (116 "
       "lines) -> continue -> re-enable) -> push LANDED d625b2157..29ae11bd6, "
       "origin==HEAD fetch-verified | S6 41 legs rc0 (Saturday legal no-op family, "
       "dualrun ZERO-DRIFT streak 13, zt_pool_crosscheck soft-warn strong_x_dtgc "
       "known-benign) | S7 quartet green (loop pin=2 no-op, watchdog re-registered, "
       "claws IN-SYNC) | inbox MSG-20261010-0935 addressed to bm-c (W17 SLA), not "
       "bm-b - zero action, left in place | explore.md P3 5->4 (E9 head = AH premium "
       "deepening)")

NEXT = ("r829: E9 explore head (HK-connect AH premium mean-reversion deepening, "
        "T-18 probe before claiming) + W18 drafting window once W17-JUDGE drains "
        "(bm-c lane) + Monday 2026-10-12 09:15 minute_feed first gated run "
        "backfills 10-08/10-09")

ARTIFACT = ("r828: scripts/futures_calendar_spread.py (selftest 14/14) + "
            "results/futures_calendar_spread/{face.json,spreads.csv} + "
            "research/digests/DIGEST-20261010-e8-futures-calendar-spread.md, "
            "2026-10-10 10:3x")

NOW_ACTIVE = ("r828: E8 futures calendar-spread monitor face delivered (9/9 pairs, "
              "791 rows) + push-race rebase dual-batch canonical resolve")

MILESTONE = ("r829+: E9 explore head (AH premium mean-reversion, T-18 probe first) "
             "+ W18 drafting window once W17-JUDGE drains; Monday 2026-10-12 09:15 "
             "minute_feed first gated run backfills 10-08/10-09")

# ---- machine metrics --------------------------------------------------------
try:
    import psutil
    ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    ram = None
try:
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True).stdout.strip().splitlines()
    vmb = int(sum(float(x) for x in o))
except Exception:
    vmb = None
vram = round(vmb / 1024.0, 2) if vmb is not None else None
print("metrics: ram=%s vram_gb=%s" % (ram, vram))

# ---- 1. state.json -----------------------------------------------------------
p = "state.json"
s = json.load(open(p, encoding="utf-8"))
s["machine_id"] = "bm-b"
s["round_no"] = 828
s["round"] = 828
s["note"] = VERDICT
s["verdict"] = VERDICT
s["last_round_at"] = TS
s["ts"] = TS
s["updated"] = TS
s["updated_at"] = TS
s["last_seen"] = TS
s["clock_read"] = TS
s["last_round_ts"] = TS
s["round_no_label"] = "r828"
s["did"] = DID
s["current_task"] = NEXT
s["task"] = NEXT
s["next"] = NEXT
s["now_active"] = NOW_ACTIVE
s["latest_artifact"] = ARTIFACT
s["next_milestone"] = MILESTONE
s["last_action"] = ("r828: E8 calendar-spread face delivered (9/9 pairs 791 rows) + "
                    "S6 41 legs rc0 + push-race dual-batch resolve LANDED")
json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=True, indent=1)
print("state.json updated, round_no=828")

# ---- 2. heartbeat fleet/machines/bm-b.json ------------------------------------
p = "fleet/machines/bm-b.json"
h = json.load(open(p, encoding="utf-8"))
h["machine_id"] = "bm-b"
h["round_no"] = 828
h["round"] = 828
h["last_seen"] = TS
h["ts"] = TS
h["updated"] = TS
h["updated_at"] = TS
h["last_round_at"] = TS
h["clock_read"] = TS
h["heartbeat_epoch_utc"] = EPOCH  # JSON int (F7 law)
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["cpu_cores"] = 16
if ram is not None:
    h["free_ram_gb"] = ram
if vram is not None:
    h["gpu_free_vram_gb"] = vram
    h["gpu_free_vram_mb"] = vmb
h["current_task"] = NEXT
h["task"] = NEXT
h["next"] = NEXT
h["now_active"] = NOW_ACTIVE
h["latest_artifact"] = ARTIFACT
h["next_milestone"] = MILESTONE
h["last_action"] = s["last_action"]
h["verdict"] = VERDICT
h["orphan_faces"] = 0
h["orphan_face_note"] = "probe 14 py faces 0 orphans (round-zero probe rc0)"
json.dump(h, open(p, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

# F7 self-assert: epoch int + clock_read T-separated
h2 = json.load(open(p, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and not isinstance(
    h2["heartbeat_epoch_utc"], bool)
assert "T" in h2["clock_read"] and " " not in h2["clock_read"]
print("heartbeat updated: epoch int=%d clock=%s" % (
    h2["heartbeat_epoch_utc"], h2["clock_read"]))

# ---- 3. round report -----------------------------------------------------------
WM = ("WM-VERDICT: 绿（red=false；probe verdict=insufficient_history=合法〔15min 窗"
      "史不足·池 ready 0·板全闭环〕）")
CEO3 = ("CEO three-line: 当前活=r828 E8 商品期货跨期价差监控面交付（9/9 品种成对 791 "
        "行·面板三方交叉验证）+push 竞速 rebase 双批冲突正典解 LANDED；最近实物="
        "scripts/futures_calendar_spread.py（selftest 14/14）+results/"
        "futures_calendar_spread/{face.json,spreads.csv}+research/digests/"
        "DIGEST-20261010-e8-futures-calendar-spread.md, 2026-10-10 10:3x；下个里程碑="
        "E9 探索头（AH 折溢价深化·领前必跑 T-18 探针）+W17-JUDGE 排空后 W18 起草窗"
        "+周一 10-12 09:15 minute_feed 门控首轮回补（≤48h）")
DID_RR = ("做了什么：①E8 认领锁 commit 3b5b3686b（T-18 探针 CLEAR；bm-a r950 同窗"
          "探针=COLLISION_RISK 见我 in-flight 让路=探针机队双端首证）→预检 "
          "results/_r828bmb_e8_shape_probe.py 四族 5/5（键位 d/o/h/l/c/v/p/s·p=OI "
          "真键·CFFEX s=0.000 诚实 None）→交付监控面 scripts/futures_calendar_spread.py"
          "（selftest 14/14 hermetic·48 请求 0 失败 2.5s 限速·near/far=活 20d+OI 15% "
          "floor+far_thin 回退披露）+证据 face.json/spreads.csv（791 行·panel cutoff "
          "2026-10-09 全对齐）+digest 调研件；判读=股指 2610/2612 贴水 -38.6~-127〔"
          "分红贴现正向结构〕·国债 2612/2703[far_thin] CTD 微贴水 -7~-9bp·RB 2701/2703 "
          "z=-2.14 近期翻面·AU 2612/2702 +2.4 升水·SC 2611/2612 深贴水 -23.3〔ratio "
          "0.968=近月现货紧面最厚信号面〕；basis=0.0×6+OI 逐位恒等（RB 1,673,458/SC "
          "23,669/T 377,917）=主力连续面板三方交叉验证；②上游 latent 键位坑登记 tech "
          "T20（update_futures raw fallback OI 读键 o=open·真键 p·akshare 主径未中招"
          "本地面板 OI 健康·归 bm-a lane 不越道修）；③explore.md r827 消耗记录行界分"
          "裂+3 路径缺 r 出生缺陷治愈（4 行并 1·工件存在性先验·字节账 3LF 剔除+3r "
          "还原）；④push 竞速=交付批 push 撞 bm-a r950 同窗（pre-push 爪拒 non-FF）"
          "→吸收+rebase 双批 canonical 解：批1=tech.md T19 邻行 union〔HEAD done+我 "
          "T20 open〕+probe json take-HEAD〔bm-a COLLISION_RISK 让路实证面·r140 tie→"
          "HEAD〕；批2=satengine 3 面 r609 陈旧重放族〔分类器 append-log 误判实测=116 "
          "行滚动窗快照·daemon writer-pause 窗 bm-a r950-pre2 先例：schtasks 暂停 "
          "SatEngine+Autofill→checkout --ours 净版→json/jsonl 全验→GIT_EDITOR=true "
          "continue→复活〕→push LANDED d625b2157..29ae11bd6 fetch 自证 origin==HEAD；"
          "⑤S6 41 腿全 rc0（dualrun ZERO-DRIFT streak 13·周六合法 no-op 族·lane 守卫"
          "诚实跳过·update_lhb 11/11 披露抓取正常）；⑥S7 四查绿（loop pin=2 no-op·"
          "watchdog 重注册·双爪 IN-SYNC）")
VERIFY = ("验证：smoke 49/49 PASS；selftest 14/14；orders 双扫 CLEAN 零 unacked（"
          "orders_ack_scan 60/184·124 stale 软档非债）；DEC/ORD 双水位 MATCH（"
          "a3ea37bd/e286f842 canonical probe _r686bmb_d19_check.py）；attrition CLEAN "
          "4 台账；S6 41 腿全 rc0；合并树三件快验（T19 done+T20 open+E8 done+face "
          "9 pairs+selftest 复跑 14/14）")
PTR = ("下轮指针：r829=E9 队头（AH 折溢价均值回归深化·T-18 探针先行）+W18 起草窗"
       "（W17-JUDGE 排空后）+周一 10-12 09:15 minute_feed 门控首轮回补 10-08/09 | "
       "孤儿面=0；本地未达 origin commit 数=0（closeout push 后 fetch 自证）")

line = "%s | r828 bm-b | dept:数据（P3-E8 商品期货跨期价差监控面·update_futures 面板消费）+dept:工程（push 竞速 rebase 双批冲突解） | %s | %s | %s | %s | %s" % (
    TS, WM, CEO3, DID_RR, VERIFY, PTR)
p = "logs/iteration-loop/round_reports.md"
with open(p, "ab") as f:
    f.write(line.encode("utf-8") + b"\n")
print("round report appended, line bytes:", len(line.encode("utf-8")))
print("CLOSEOUT FACES DONE")
