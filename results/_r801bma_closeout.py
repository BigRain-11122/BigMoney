# -*- coding: utf-8 -*-
"""r801 bm-a closeout: state + heartbeat + round ledger (single-file fresh
read-modify-write per r610 law; heartbeat epoch int self-check per R170/R178)."""
import json
import time
import datetime
import psutil

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state-bm-a.json -----------------------------------------------------------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["current_task"] = ("r802: W167 freeze half-window (r799 W166 lineage verbatim): "
                      "face probe _r801bma_w167_face_probe.py (dump 4 W166 faces) "
                      "-> prereg build (xform PERPETUAL_N1_W166_PREREG.md -> W167; "
                      "gate receipt _r801bma_w167_band_gate.json A 382_204..384_203 / "
                      "B 384_204..384_403; W166 finalize r799 one-pass K=363,120 ledger "
                      "770,612; registered W166 row citation bm-a r799 freeze c2d6c5e14) "
                      "-> freeze edits 5-face (pf comment+row 167 / n1 entry / mat "
                      "block / PASS claim; vmap r773/r776/r777 laws; TOK from face-probe "
                      "receipt) -> dual selftest (pf 9/9 + n1) -> commit push -> 2-tick "
                      "ignite verify (n1_w167/ shard growth, r535 bm-a tick law); seat "
                      "MSG-2026-10-07-0056-bma-w167-seat.md self-ack inbox->processed")
st["did"] = ("r801 W167 pre-seat half-window complete: probe _r801bma_w167_probe.py "
            "rc0 ADMIT (A 382_204..384_203 staircase 26th instance hops=1 past "
            "registered W166 B band 382_004..382_203; B 384_204..384_403 own-A mutual "
            "exclusion hops=1; naive-B-inside-naive-A W141 leg2) + seat MSG on origin "
            "982424c5f (r565 pre-seat push) + band gate _r801bma_w167_band_gate.py rc0 "
            "ADMIT 4 legs (leg0b own seat dual-dir zero others; leg1 parity held; leg2 "
            "zero conflicts origin vacancy; leg3 W168+ projection) + S6 38/38 rc0 100s "
            "holiday no-op family + smoke 48/48 + attrition CLEAN + decisions watermark "
            "consumed (10-07 00:00 patrol block, zero new BigMoney dispatch)")
st["last_action"] = "r801: W167 pre-seat (probe+seat+gate) complete"
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
st["last_round"] = 800
st["last_round_at"] = now
st["last_round_ts"] = now
st["loop_round"] = 801
st["round"] = 801
st["round_no"] = 801
st["updated"] = now
st["ts"] = now
st["clock_read"] = now
st["last_run"] = now
st["last_seen"] = now
st["last_decisions_sha"] = "acc322169eaa759a6ea34c65be35aa7eed7ea9b96dc0895dc7f4f682becdf2fd"
st["last_decisions_at"] = now
st["last_decisions_seen"] = "2026-10-07"
st["last_decisions_ts"] = "2026-10-07T00:52:00+08:00"
st["last_decisions_src"] = "group-tree origin blob (C:/Users/sjs20/Desktop/FluxGroup git show origin/main:docs/decisions.md, r786 law; python sha256 raw bytes)"
st["last_orders_at"] = now
st["latest_artifact"] = ("results/_r801bma_w167_band_gate.json + fleet/inbox/MSG-2026-10-07-0056-bma-w167-seat.md "
                         "@2026-10-07T00:56:30+08:00")
st["verify"] = ("W167 probe rc0 ADMIT + gate rc0 ADMIT 4-leg (parity held band-for-band) + "
                "S6 38/38 rc0 + smoke 48/48 + attrition CLEAN + pre-seat push 982424c5f + "
                "gate push bec051bf0 + heartbeat epoch int + T-separated clock self-checked")
st["notes"] = ("r801 = second half-session of the 00:47-01:0x window; r800 main session "
               "(a6c5ee909 00:39) cleared r799 deferrals (S6/D-06/O-2358 receipt); W167 "
               "freeze half-window deliberately deferred to r802 per W166 two-session "
               "precedent (r797 pre-seat / r799 freeze) — 25min wrapper budget law")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int (R170/R178 law)"
assert "T" in chk["clock_read"][:11], "clock_read not T-separated (R262 law)"
print("state-bm-a.json: round_no=801 written, epoch int + T-clock self-checked")

# --- fleet/machines/bm-a.json (heartbeat) ---------------------------------------
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
h["ts"] = now
h["last_seen"] = now
h["clock_read"] = now
h["heartbeat_epoch_utc"] = epoch
h["round_no"] = 801
h["current_task"] = "W167 pre-seat complete (probe+seat MSG+band gate rc0); freeze half-window next r802"
h["verdict"] = "healthy; W167 A 382_204..384_203 / B 384_204..384_403 seated=reserved; engine idle queue0 post-W166"
h["ram_free_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 1)
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "heartbeat epoch not int (R170/R178 law)"
assert "T" in chk2["clock_read"][:11], "heartbeat clock_read not T-separated"
print("heartbeat bm-a: epoch int verified, ts/clock/verdict refreshed")

# --- round ledger ---------------------------------------------------------------
line = (now + " | r801 bm-a W167 席位半窗（probe+席位+带闸全绿 ADMIT） (dept:研究/工程/舰队) | "
        "[watermark verdict: 绿 red=false; satengine alive rc0 queue0 idle（W166 12/12 已收口·W167 已坐席待冻结）] | "
        "当前活: W167 pre-seat 链完成——probe _r801bma_w167_probe.py rc0 ADMIT（A 382_204..384_203 阶梯 A-hops-prior-B 第二十六例 hops=1 越注册 W166 B 带 382_004..382_203；B 384_204..384_403 own-A 互斥保留走位 hops=1·naive B 382_204..382_403 落 own-A 窗内 W141 leg2）+ 席位 MSG-2026-10-07-0056-bma-w167-seat 已上 origin（982424c5f r565 pre-seat push·禁 no-verify）+ 带闸 _r801bma_w167_band_gate.py rc0 ADMIT 四腿（leg0 164 行表尾 W166 序 157/bm-a 83；leg0b own seat 双向扫零他座；leg1 与 pre-seat probe 带对带平价恒等；leg2 零冲突+origin 空位；leg3 W168+ 投影门尾） | "
        "最近实物: results/_r801bma_w167_band_gate.json + fleet/inbox/MSG-2026-10-07-0056-bma-w167-seat.md @00:56 | "
        "下个里程碑: W167 冻结半窗（r799 W166 血统 verbatim：face probe→prereg→freeze edits 五面→双 selftest→点火验证 n1_w167/ 分片增长）r802 窗 ≤48h | "
        "did: S0 吸收 daemon churn 后 pull --rebase 干净 + S0.5 令扫描零未回执 O 令 + 决策水位消费（10-07 00:00 巡逻窗 D-01c 已由 r800 执行/02/03 非本司·hash acc322169 已记·零新派工）+ smoke 48/48 + S6 38/38 rc0 100s（节假日全 no-op 族·REPORT-2026-10-07/LIVE-2026-10-07 面已由 r800 主窗落·本窗幂等）+ attrition CLEAN（历史 healed 行照录）+ S7 双任务活（IterationLoop 针位 :08/LoopWatchdog）+ pre-commit/pre-push 双爪在位 | "
        "verify: probe rc0 + gate rc0 四腿 + 席位 push 982424c5f + gate push bec051bf0 送达（fetch+push 输出复核） | "
        "计分: 2（能跑/能看实物=W167 席位三件套：probe receipt+origin 席位 MSG+gate receipt·引擎波供给线在册件） | "
        "承接判定: 本轮零新方法（r797 W166 pre-seat 血统 verbatim 复用零漂移）；零清扫/归档/恢复类动作（treasure_guard 未触发） | "
        "下轮指针: r802=W167 冻结半窗（face probe→prereg xform→freeze edits 五面 vmap→pf/n1 双 selftest→commit push→2-tick 点火验证；席位 MSG self-ack inbox→processed；注册行引用=bm-a r799 freeze c2d6c5e14） | "
        "本地未达 origin commit 数: 0（收尾 commit 后 push+fetch 复核） [r801 bm-a]")
with open("round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(line + "\r\n")
print("round ledger: r801 line appended")
