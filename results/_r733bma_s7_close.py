# -*- coding: utf-8 -*-
"""r733 bm-a S7 close: state round bump + heartbeat + round report line.
Bytes-safe UTF-8, JSON int epoch, T-format clock (R170/R178/R262 laws)."""
import json, time, datetime, io

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
flat = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

# ---- 1. state-bm-a.json ----
sp = ROOT + r"\state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 733
st["round"] = "r733"
st["last_round"] = "r733"
st["last_round_at"] = flat
st["last_round_ts"] = iso
st["last_seen"] = flat
st["updated"] = flat
st["last_action"] = ("r733: W127 finalize one-pass (K 277,320, ledger 675,411, 4-asserts PASS, "
                     "sec7/8 backfilled) + W128 freeze chain delivered (118th wave, A 299_004..301_003 "
                     "+ B 68_001..68_200 hops=1 refusal cny_window_p1=68_000, gate ADMIT, engine "
                     "self-ignited) + S0 double-merge (16+18 UU resolved)")
st["current_task"] = ("r734: W128 finalize on 12/12 landing (r708 pre-flight: dup + active-process "
                      "probe + seat check) + W129 freeze window (gate-tail projection A 301_004..303_003 "
                      "CLEAN / B 68_201..68_400 CLEAN hops=0, re-derive r587 law)")
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = epoch
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")

# ---- 2. heartbeat fleet/machines/bm-a.json ----
hp = ROOT + r"\fleet\machines\bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-a"
hb["clock_read"] = iso
hb["last_seen"] = flat
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = epoch
hb["round_no"] = 733
hb["round"] = "r733"
hb["last_round"] = "r733"
hb["loop_round"] = 733
hb["verdict"] = "ok"
hb["task"] = ("r733 close: W128 burn in flight (12 shards, tick-ignited 16:2x); r734 = W128 "
              "finalize on 12/12 (r708 pre-flight) + W129 freeze window")
hb["last_action"] = st["last_action"]
hb["now_active"] = ("W128 engine wave burning (12 shards, tick self-ignited 16:2x, 118th wave, "
                    "bm-a 44th owned); golden-week watch (no new bars until 10-09 reopen)")
hb["latest_artifact"] = ("results/perpetual_faces/n1_w127_results.json (W127 finalize: K=277,320, "
                         "ledger 675,411, mu -0.092805, skill 1.1757) + research/PERPETUAL_N1_W128_PREREG.md "
                         "FROZEN @ 2026-10-05T16:1x+08:00 (freeze commit 26ce3f5d6)")
hb["next_milestone"] = ("W128 finalize on 12/12 landing (r708 pre-flight, same-day ~16:4x) + W129 "
                        "freeze window; 10-09 reopen legs (external + marks + REGIME_GUARD v3 "
                        "first-new-bar) within 72h")
hb["notes"] = "r733: W127 finalize + W128 freeze; S0 double-merge vs bm-b r734/bm-c r554 waves"
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
rb = json.load(open(hp, encoding="utf-8"))
assert isinstance(rb["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in rb["clock_read"], "clock_read must be T-format (R262 law)"
print("state 732->733 + heartbeat epoch int self-verified")

# ---- 3. round report line ----
rp = ROOT + r"\round_reports-bm-a.md"
entry = """
r733 (bm-a) | dept:研究+工程 | watermark verdict=绿（loaded_ok·py 94.4% 假期值守+引擎波烧录·16:01:03 实测）｜当前活=W128 引擎波烧录中（12 分片·tick 自燃 16:2x·第 118 波 bm-a 第 44 枚自有波）+黄金周值守（10-09 复市前无新 bar）｜最近实物=results/perpetual_faces/n1_w127_results.json（W127 finalize：K=277,320·ledger 675,411·mu −0.092805·skill 1.1757·四断言全 PASS）+research/PERPETUAL_N1_W128_PREREG.md 冻结（freeze 26ce3f5d6）｜下个里程碑=W128 finalize 12/12 落地收口（r708 预检·当日窗）+W129 冻结窗；10-09 复市腿（external+marks+REGIME_GUARD v3 首新 bar）窗 ≤72h
DONE-1 S0: 双窗 merge 收口——首窗 16 UU（14 take-ours bm-a 15:48-15:51 机探新于 bm-b 15:42-15:46·REPORT/LIVE+dashboard 孪生+attrition+4 gate 面；compute_audit/regime_state rolling union base=ours r729 律；token per-key union picked_theirs=0 r715/r522 律）+二窗 18 UU vs bm-c r554 波（15 take-theirs 15:50-15:52 较新+scorecard 双面；union 双面 base=theirs）；resolver=_r733bma_merge_resolve.py（r734 bm-b 血统复刻+扩脸 6 面：dashboard 孪生+gate 状态+scorecard）；零 UU 复核 r713 律+readback CR 归一断言全过+md/js 孪生随 json 同侧 r708 律；churn-absorb 前置 r620 律；首推撞拒 2 次=落后信号 r524 律两跳收口法
DONE-2 S0.5: orders 154/154 零未回执（轮首+S7 双扫·ack=.md 后缀形态核对）+D-19 dual MATCH（decisions d14dcc74 SHA-256/orders 3bf0f16e SHA-1 r537 钉·K: 缺席→Desktop 实径 fallback r631 配方·空字节=e3b0 路径缺席信号非空文件 r710-②律当场定性）→零动作
DONE-3 S1: smoke 48/48 全绿
DONE-4 产出之一 **W127 finalize one-pass**（r708 预检三腿：status 12/12 reparse+Win32_Process 全扫零 N1 runner 活进程+dup fail-closed 内建；席位 MSG-1548 published=spawn 唯一合法性；W127_only mu −0.081695 σ 0.249066 → merged −0.092805/0.244843@K=277,320 算术检；skill_line_v2 @n_eff 673,211 1.1754→1.1757 K-lift +0.0003；se_mu 0.000467→0.000465；A p95 0.3248/p99 0.4756；账本 673,211+2,200=675,411 单发；四断言全 PASS 机件复算（dmu 0.011110/sigma +0.0146pc/A-p95 +0.0241/K-lift +0.0003）；§7/§8 机械回填随 freeze 同 commit）
DONE-5 产出之二 **W128 never-dry 全链冻结+点火交付**（pre-seat probe rc0 ADMIT：A 299_004..301_003 CLEAN hops=0+B first-clean 68_001..68_200 hops=1·拒收事实 cny_window_p1=68_000 上缘端点→past-hit restart·D-20261002-05 pin 边缘端点族两读法恒同解；席位 MSG-2026-10-05-1612 先推 0826a8e65 r565 律〔首推撞 behind3=bm-b r735 值守波=r524 律落后信号→merge 零 UU→DELIVERED 99e292c9d 0/0〕；冻结窗 gate 双跑 derive 恒等 ADMIT _r733bma_w128_band_gate.json 四腿（leg0 125 rows 尾=W127/leg0b 席位在 origin 零外机/leg1 B 拒收窗复算恒等/leg2 零冲突 vacancy/leg3 W129+ 投影双 CLEAN）；registry insert=pf 128 行+WAVE_CONFIGS[128]+W128 materializer face（B 拒收窗语义断言改写：算术窗 67_801..68_000 恰含 68_000 机证腿+first-clean 净窗腿）+selftest 汇总面；banned gate ADMIT 0；n1 selftest PASS（W128 face 在列）+pf 9/9 双跑 r727 律；freeze commit 26ce3f5d6 送达 0/0；引擎 tick 自燃 shard-0 active=产物增长面 r325 律点火证据在位；W129+ 投影 A 301_004..303_003/B 68_201..68_400 双 CLEAN hops=0 下家必复核 r587 律）
DONE-6 S6: 假期窗合法复用——r732 链产物 15:49-15:51 本窗新鲜（churn-absorb 收编 57 面+两跳 merge 送达·面板机探 15:48-15:51 新于 bm-b 15:42-15:46 与 bm-c 合并面）·零重烧复跑（意义律 O-20260930-1901：黄金周幂等 no-op 重跑=0 分记账·禁为用而用）·py_watermark 16:01:03 探针绿 red=false·pool_dualrun/compute_audit/market_regime/scorecard 等链腿随 r732 链 rc0 在案
DONE-7 S7: 四件套绿（loop pin=8 no-op+watchdog -Force 幂等重注册+pre-commit/pre-push 双爪 LF 归一幂等重装）+attrition CLEAN（历史 healed 注记照录·零 active loss）+orders 双扫 154/154+state 732→733+心跳 epoch int 自证+席位 MSG-1612 归档 processed
评分 2+2=4（W127 finalize 实物+W128 冻结链实物；S7 例行簿记不计分）｜记账预算 3/5（state+轮账行+心跳）｜本地未达 origin commit 数=0（26ce3f5d6 送达 0/0 ls-tree 自证）｜dept:研究 [via bm-a]
"""
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(entry)
print("round report r733 line appended")
