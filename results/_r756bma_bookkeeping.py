# -*- coding: utf-8 -*-
"""r756 bm-a S7 bookkeeping: state + heartbeat + round report (json-safe writes)."""
import json
import time
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8)))
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
hhmm = now.strftime("%H:%M")

# ---- state-bm-a.json -------------------------------------------------------
p = r"state-bm-a.json"
st = json.load(open(p, encoding="utf-8"))
st["round_no"] = 756
st["last_round"] = 756
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["last_run"] = "r756"
st["last_seen"] = now.strftime("%Y-%m-%d %H:%M")
st["updated"] = now.strftime("%Y-%m-%d %H:%M")
st["loop_round"] = 599
st["round"] = "r756"
st["current_task"] = ("r756 closed; next r757: W147 freeze window (band gate + extract + registry "
                      "inserts x2 + cite fix + prereg xform + dual selftest + freeze commit + push + "
                      "ignition; seat MSG-2026-10-06-045x-bma-w147-seat already on origin a5eadcdd7, "
                      "bands A 338_204..340_203 / B 340_204..340_403 hops 1/1 per probe receipt "
                      "_r756bma_w147_probe_receipt.json; W148+ projection A 340_204..342_203 / B "
                      "340_404..340_603 disclosed)")
st["did"] = ("r756: W146 finalize one-pass (merged K=319,120 / ledger 715,011+2,200=717,211, both "
             "projections hit; S5 four prediction keys machine-verified PASS; dual selftest PASS) + "
             "W145 S7/S8 dead-tail debt backfilled (late window disclosed; W146 S5 claim-reality gap "
             "corrected) + W147 pre-seat probe ADMIT + seat published=reserved pushed a5eadcdd7 + "
             "push-race behind-3 merge 24-UU canonical resolve (merge_lane_views 6 faces + resolver "
             "9 faces; mixed-separator ts probe poison found+healed in-session) + S6 29 legs rc0 "
             "FAILS:0")
st["last_action"] = "W146 finalize one-pass closed+delivered; W147 seat reserved on origin"
st["next"] = ("r757 W147 freeze window (xform bloodline = results/_r755bma_w146_prereg_xform.py "
              "adapt W147 facts; residue-allowlist per r547 owner-context law)")
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
st["verify"] = ("smoke 48/48; W146 finalize rc0 K=319,120/ledger 717,211 (S5 keys 4/4 PASS); dual "
                "selftest PASS (n1 full chain W146 + pf 9/9); D-19 decisions MATCH (7674E37BF062 "
                "python-bytes); orders 0 unacked; S6 29 legs rc0 FAILS:0 83s; dualrun ZERO-DRIFT "
                "streak 51; watermark red=false; attrition CLEAN (4 files); W147 seat delivery "
                "0/0 @a5eadcdd7; CODELY.md 28,098B water noted")
st["notes"] = ("r756 golden-week steady-state; merge-conflict resolver probe poison new pit entry "
               "appended CODELY.md; D-06 collection window 10-07")
json.dump(st, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written round_no=756")

# ---- heartbeat fleet/machines/bm-a.json ------------------------------------
p = r"fleet\machines\bm-a.json"
hb = json.load(open(p, encoding="utf-8"))
hb["clock_read"] = iso
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M")
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = hb.get("heartbeat_epoch_utc", epoch)
hb["last_round"] = 756
hb["round_no"] = 756
hb["round"] = "r756"
hb["loop_round"] = 599
hb["last_action"] = ("r756: W146 finalize one-pass delivered (K=319,120/ledger 717,211) + W145 "
                     "S7/S8 debt backfill + W147 seat reserved a5eadcdd7 + merge 24-UU resolve + S6 "
                     "29 legs rc0")
hb["current"] = "W146 finalized+delivered; W147 seat reserved"
hb["current_task"] = "r757: W147 freeze window (prereg xform + freeze commit + ignition)"
hb["task"] = "r756 done: W146 finalize + W147 seat -> r757: W147 freeze window"
hb["next_milestone"] = "r757 W147 freeze (bands A 338_204..340_203 / B 340_204..340_403 frozen prereg + ignition), window <=48h"
hb["latest_artifact"] = "results/perpetual_faces/n1_w146_results.json @2026-10-06 04:2x (K=319,120, ledger 717,211)"
hb["verdict"] = ("healthy: W146 finalize one-pass delivered (projections hit, S5 4/4, dual selftest "
                 "PASS); smoke 48/48; S6 29 legs green; W147 seat reserved")
hb["now_active"] = "r756 S7 close"
ack = hb.setdefault("orders_ack", [])
seat = "MSG-2026-10-06-045x-bma-w147-seat.md"
if seat not in ack:
    ack.append(seat)
json.dump(hb, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify (R170/R178/R262 laws)
hb2 = json.load(open(p, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"].split("+")[0], "clock_read must be T-separated"
print("heartbeat written epoch=", hb2["heartbeat_epoch_utc"], "clock=", hb2["clock_read"])

# ---- round report -----------------------------------------------------------
line = (
    f"{iso} | r756 (bm-a) | dept:研究+工程 | watermark verdict=red=false lane=healthy py 4.0/0.3 "
    f"golden-week idle | 当前活: W146 finalize one-pass 收口交付+W147 席位已推 origin | 最近实物: "
    f"results/perpetual_faces/n1_w146_results.json（K=319,120 合并池·ledger 717,211·04:2x）+ "
    f"W147 席位 MSG-2026-10-06-045x-bma-w147-seat（A 338_204..340_203/B 340_204..340_403·origin "
    f"a5eadcdd7·04:5x） | 下个里程碑: r757 W147 冻结窗（prereg xform+冻结 commit+点火·窗 ≤48h 实际下一轮）"
    f" | did: S0.5 orders 0 unacked + D-19 decisions MATCH（sha256 7674E37BF062 python 字节法·PS "
    f"重定向 UTF-16 假阳性被 r631 律当场拦截）-> S1 smoke 48/48 -> **W146 finalize one-pass**（r708 "
    f"预飞行三腿过：分片 12/12 唯一+活进程零+席位声明零冲突 -> finalize rc0：pre K=316,920 mu "
    f"-0.092857/sigma 0.244957 -> W146-only K=2,200 mu -0.088835/sigma 0.243602 -> merged "
    f"K=319,120 mu -0.0928/sigma 0.2449·账本 715,011+2,200=717,211 投影双中·skill_line 1.179->"
    f"1.179 K-lift +0.0000·se_mu 0.000435->0.000434·S5 四预测键机证全过 ①mu 差 0.0040<0.02 "
    f"②sigma 相对 -0.0039%<±10% ③A p95 +0.0026<0.05 ④K-lift +0.0000）-> dual selftest PASS（n1 "
    f"全链 W146 materializer+pf 9/9·r522 缺省波律）-> **W145 S7/S8 死尾欠账补回**（r755 会话死于 "
    f"W146 席位窗未及回填·W146 S5 注记宣称「同 commit 在场」与实况不符=宣称-实况断差已修正·迟到窗如实披露）"
    f"-> commit ba6355cab -> push 撞拒 behind-3（bm-c r593 D-06 预验收窗）-> merge 24-UU 正典解"
    f"（merge_lane_views resolve 6 ALL_FACES+reconcile 全零漂移+resolver 9 件：分类器 15 归类+1 "
    f"UNKNOWN 手工定性 _attrition_guard_scan 快照面；**混合分隔符 ts 探针毒坑当场发现+当场治愈**——"
    f"origin T03:56:20+08:00 数据键词典序压 local 空格04:03:03 generated 键→REPORT 孪生侧判反转，"
    f"strptime 归一化重解+全 9 件侧判复核防同坑·坑律已入 CODELY.md）-> delivery 5de34bd42 -> "
    f"**W147 pre-seat probe rc0 ADMIT**（A 338_204..340_203 hops=1 越过 W146 B 带=阶梯第六例 E36 卡"
    f"·B 340_204..340_403 hops=1 own-A 预留 leg2 律·r755 W146 gate-tail 双强制注记全兑现·144 行注册面"
    f"137th wave/bm-a 63rd owned·冲突 0·origin 空缺核证）-> 席位 MSG published=reserved 推 origin "
    f"a5eadcdd7（r565 冻结前公示律）-> S6 29 legs rc0 FAILS:0 83s（dualrun ZERO-DRIFT streak 51·"
    f"compute_audit rc0 py 0.3%·golden-week 无新 bar 腿合法 no-op·lane-guard 他机道诚实 no-op）-> "
    f"S7: loop pin=8 no-op + watchdog 注册（首火 04:28）+ 双爪重装 + attrition scan CLEAN（4 账本件·"
    f"healed 注记照录）| evidence: research/PERPETUAL_N1_W146_PREREG.md S7/S8 回填+W145 同窗补回+"
    f"results/perpetual_faces/n1_w146_results.json+results/_r756bma_w147_probe_receipt.json+"
    f"results/_r756bma_merge_resolve.py+results/_r756bma_s6_chain.py | 本地未达 origin commit 数=0 "
    f"| commit 链: ba6355cab finalize 产物 -> 5de34bd42 merge -> a5eadcdd7 W147 席位\n"
)
with open(r"round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report appended", len(line.encode("utf-8")), "bytes")
