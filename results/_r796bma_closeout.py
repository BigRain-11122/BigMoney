# -*- coding: utf-8 -*-
"""r796 bm-a closeout: RR rows (r795 dead-session absorption + r796) + state + heartbeat.
Python fresh read-modify-write per multi-writer file law (r109/r773 family)."""
import json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
print("now:", now_iso, "epoch:", epoch)

# ---------- 1. round report rows ----------
rr_path = "logs/iteration-loop/round_reports-bm-a.md"
with open(rr_path, encoding="utf-8", errors="replace") as f:
    rr = f.read()
if not rr.endswith("\n"):
    rr += "\n"

row_r795 = (
"2026-10-06T22:0x+08:00 | r795 bm-a (S5 恢复行·死会话 r796 代录) | W165 freeze+ignition+finalize ONE-WINDOW 全生命周期落地 (dead-r795 21:46-22:15 窗: freeze 链 4 工具执行+6 处值修正 aebb94d2d 已推 origin 21:59 + engine tick 自燃 12/12 shards r535 律 + finalize one-pass rc0 ledger 766,212→768,412 +2,200==prereg 投影恒等·K 358,720→360,920·skill_line_v2 1.1834→1.1833 K-lift −0.0001 如实微降·se_mu 0.000408·A p95 0.3018·§5 四预键机证全过·canon flip NOT performed·audit.finalize_only=true) + §7/§8 同窗回填 (research/PERPETUAL_N1_W165_PREREG.md L57/L67·机证 results/_r795bma_s78_verify.txt) + S6 38/38 rc0 (_r795bma_s6_chain.py) — 会话 25min wrapper 斩首于 S7 前 (全部产物已 staged 未 commit·state/RR/心跳零更新·由 r796 吸收收口) | verify: n1_w165_results.json merged mu −0.0929/sigma 0.245144 断言过·aebb94d2d 在 origin | [r796 bm-a]\n"
)
row_r796 = (
"2026-10-06T22:3x+08:00 | r796 bm-a (dept:工程+研究) | watermark verdict: 绿(red=false lane=healthy; probe py 0.2-0.3% 低位=golden-week 合法 idle 白名单面 py_low_board_clear: 板全闭环 0 open 票+bandit 0+零 active burns+engine verdict idle W165 已烧完) | 当前活: dead-r795 W165 全生命周期产物吸收收口 (takeover closeout per r787/r794 先例) | 最近实物: results/perpetual_faces/n1_w165_results.json + research/PERPETUAL_N1_W165_PREREG.md §7/§8 @22:0x | 下个里程碑: W166 带位+冻结+点火 (never-dry ≤4h·post-W165 注册宇宙重 derive 强制+own-A 预留 leg2) + D-20261005-07/08 回执窗 10-07 12:00 | did: S0 fetch behind=0 ahead=0 (r795 主件 aebb94d2d 在 origin)·S0.5 双水位 SHA-256 程序化消费 (dec a44c39e0→512dc730 = 12:00 批 D-20261006-04/05 r790 已回执确认零新本司派工·ord 415bbcea→e5f28675 = 10-06 12:00-20:3x 增量行全已回执 [O-1207→r773·O-1215/1218→r774·O-1845→r790·O-1900 全面开工本司腿 80bf87d4 origin 实证·C 机游戏窗/CEO 用机口令律=非本司面]·双水位键同步修正·r793 已消费 e13b9bd 值与 takeover-r794 写回 a44c39e0 旧值冲突如实注记=以现行 origin blob 为准) + S1 smoke 48/48 + S3 主产=W165 产物链验证 (merged K=360,920·mu −0.0929·w165_only K=2,200 mu −0.092588·prereg §7/§8 落位核对) + S6 38/38 rc0 104s 本窗首跑实证 (_r795bma_s6_chain.py=r783 血统·golden-week no-op 族·token L2 3 legs today) + n1 selftest PASS (W165 mat face 155th engine wave 含) + pf selftest 9/9 + S7 attrition guard CLEAN 4 账本 (healed 注记照录) + loop pin=8 在位 + watchdog 在位 + 双钩恒等 (pre-commit/pre-push CR 归一) + 宝藏捕获问/方法论问=本批零新增 (例行波·§8 已答·TREASURE_REGISTRY/METHODOLOGY_ASSETS 零 append) + state 794→796 (止 r795 吸收) + 心跳 epoch int 自证 + HANDOVER 5x=r795 死会话跳过如实注记 (r791-r796 覆盖欠账·下次 5x=r800) | verify: ledger_head()=768,412 file=n1_w165_results.json 断言过·orders 尾行全回执·本地未达 origin commit 数=0 (commit 后 push+fetch+rev-list 复核补录) | next: (1) r797=W166 带位+冻结+点火 (A first-clean 379_804..381_803·B 380_004..380_203 §8 投影·post-W165 注册宇宙重 derive 强制+own-A 预留 leg2·阶梯 A-hops-prior-B 第 25 例待 W166 注册宇宙复核) (2) D-20261005-07/08 bigmoney 回执窗 10-07 12:00 (pool_worker origin 同步断言+data_deps 接线·wrapper Step1 grep 清点 rc=0 时消费 stderr 面) (3) 10-07 12:00 D-06 收口窗 (4) T-173 48h 题材报告 due 10-08 午 | [r796 bm-a]\n"
)
with open(rr_path, "a", encoding="utf-8") as f:
    f.write(row_r795)
    f.write(row_r796)
print("RR rows appended: 2")

# ---------- 2. state file ----------
st_path = "state-bm-a.json"
with open(st_path, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 796
st["round"] = 796
st["loop_round"] = 796
st["last_round"] = 796
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["last_seen"] = now_iso
st["updated"] = now_iso
st["ts"] = now_iso
st["clock_read"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = epoch
st["last_run"] = now_iso
st["current_task"] = "r797: W166 seat+derive (post-W165 universe mandatory re-derive + own-A reservation leg2) -> freeze -> ignition -> finalize; plus D-20261005-07/08 receipts due 10-07 12:00"
st["did"] = ("r796 takeover closeout of dead-r795 (killed 22:15 pre-S7): W165 full-lifecycle products absorbed "
             "(burn 12/12 self-ignited + finalize one-pass rc0 ledger 766,212->768,412 +2,200, K 358,720->360,920, "
             "skill 1.1834->1.1833 -0.0001 honest, A p95 0.3018) + prereg s7/s8 backfill verified + S6 38/38 rc0 104s fresh + "
             "smoke 48/48 + n1/pf selftests + dual watermarks consumed (dec 512dc730 / ord e5f28675, zero new dispatch)")
st["last_action"] = ("r796: dead-r795 absorption closeout -- committed r795 staged estate (W165 finalize + shards 5-11 + s7/s8 backfill + S6 faces) "
                     "with fresh verification pass; state 794->796 (r795 absorbed), HANDOVER 5x missed by dead r795 disclosed (next 5x=r800)")
st["next"] = ("W166 seat+derive+freeze+ignition (never-dry <=4h): post-W165 registered-universe MANDATORY re-derive + reserve own-wave A window when deriving B "
              "(W141 leg2 law, 25th staircase instance pending W166 universe recheck); then D-20261005-07/08 receipts 10-07 12:00")
st["verify"] = ("ledger_head()=768,412 (n1_w165_results.json fresh); smoke 48/48; S6 38/38 rc0; n1 selftest PASS; pf 9/9; "
                "attrition guard CLEAN x4; loop pin/watchdog/hooks in place; dual watermarks 512dc730/e5f28675 consumed zero-action")
st["latest_artifact"] = "results/perpetual_faces/n1_w165_results.json + research/PERPETUAL_N1_W165_PREREG.md s7/s8 @2026-10-06T22:0x"
st["notes"] = ("r796 watermarks: dec 512dc730 = 12:00 batch D-20261006-04/05 (r790-receipted, zero BigMoney dispatch confirmed fresh); "
               "ord e5f28675 = 10-06 rows all receipted (O-1900 full-mobilization BigMoney leg 80bf87d4 on origin verified); "
               "state value a44c39e0 from takeover-r794 was stale vs r793 e13b9bd consumption -- resolved to current origin blob hash")
st["last_decisions_sha"] = "512dc730110315c51e8f22e8c39a6d2d8621fe19ab2e27544f63ebdfd239c8f2"
st["last_orders_sha"] = "e5f28675f8718c78aa1efffd32d94550177a7bb1d6ee50cca6afb42bfa3b65fa"
st["last_decisions_at"] = now_iso
st["last_decisions_ts"] = now_iso
st["last_orders_at"] = now_iso
st["last_decisions_src"] = "group-tree origin blob (C:/Users/sjs20/Desktop/FluxGroup git show origin/main:docs/decisions.md, r786 law)"
with open(st_path, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
d2 = json.load(open(st_path, encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
assert d2["round_no"] == 796
print("state updated: round_no=796, epoch int OK, dec/ord watermarks set")

# ---------- 3. heartbeat ----------
hb_path = "fleet/machines/bm-a.json"
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
hb["clock_read"] = now_iso
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = epoch
hb["round_no"] = 796
hb["round"] = 797
hb["loop_round"] = 604
hb["last_round"] = "r796"
hb["last_action"] = "r796: dead-r795 absorption closeout (W165 finalize 768,412 + s7/s8 + S6 38/38) + dual watermarks consumed"
hb["now_active"] = "W165 full lifecycle closed (ledger 768,412; chain W1..W165 fully closed, zero in-flight seats)"
hb["current_task"] = "r797: W166 seat+derive (post-W165 universe re-derive mandatory + own-A reservation leg2) -> freeze -> ignite"
hb["latest_artifact"] = "results/perpetual_faces/n1_w165_results.json + research/PERPETUAL_N1_W165_PREREG.md s7/s8 @2026-10-06T22:0x"
hb["next_milestone"] = "W166 seat+freeze+ignite (never-dry <=4h) + D-20261005-07/08 receipts 10-07 12:00 + D-06 closeout 10-07 12:00"
hb["task"] = "r796 closeout done; next = W166 seat+derive per r797"
hb["verdict"] = "healthy: W165 finalized (768,412), S6 38/38, smoke 48/48, engine idle, golden-week steady"
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1e9, 1)
    hb["ram_free_gb"] = hb["free_ram_gb"]
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["idle_ram_mb"] = round(vm.available / 1e6, 1)
    hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
    hb["cpu_util_pct"] = hb["cpu_pct"]
    hb["cpu_load_pct"] = hb["cpu_pct"]
except Exception as e:
    print("psutil unavailable, keeping last resource values:", e)
with open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
d3 = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(d3["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d3["clock_read"] and " " not in d3["clock_read"]
print("heartbeat updated: epoch int OK, clock T-separated OK")
