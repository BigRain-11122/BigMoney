# -*- coding: utf-8 -*-
# r608 bm-a bookkeeping: state, round report append, CODELY pit append, heartbeat
import json, time, datetime, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def now_cst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))

t = now_cst()
ts = t.strftime("%Y-%m-%d %H:%M")
ts_iso = t.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---------- 1) state-bm-a.json ----------
p = "state-bm-a.json"
raw = open(p, "rb").read()
st = json.loads(raw.decode("utf-8"))
st["round_no"] = 608
st["did"] = ("r608 bm-a: S0 surgical-reland aftermath repair (43 files: 20 D-artifacts + 23 stale "
             "other-machine/shared faces restored origin-verbatim per r595/r607 laws; pool_core_samples union +1 dict row CRLF r570/r600) "
             "+ caught&healed duplicate-burn contamination (autofill claimed done VALUEPB-X2 off stale post-reland pool view 04:54, "
             "overwrote 59 rows of bm-b delivered cells_VALUE-PB_x2.jsonl with different-snapshot values; origin canon intact, verbatim restore zero-loss; pit logged) "
             "+ SENS 500/500 products delivered to origin (r598 pool-done-but-products-stranded heal) "
             "+ N4-B2 wave 6/6 burned (04:28-04:51) -> finalize face n4_b2_results.json delivered same round (cumulative pooled K_eff=400, "
             "sec.4 five faces, distinct-seed 400/member gate, bootstrap seed 69_000 B1-identical re-derivation) + prereg sec.6 backfill (B1 precedent mirror) "
             "+ S6 34 legs rc0")
st["verify"] = ("smoke 47/47; S6 34 legs rc0; attrition CLEAN (4 healed); dualrun 1 DRIFT observation (entry346 owner) "
                "recorded then ZERO-DRIFT streak 1/3; orders 150/150 zero unacked (README not an order); "
                "D-19 S4U honest skip (K: absent, watermark 937A373D untouched)")
st["next"] = ("FUND-VALUE-P1 batch finalize judged verdict face once bm-b NULLS lands (SENS+4 cells done; window <=48h to 10-05); "
              "N4-B3+ wave per code sec.4 tail-law band-expansion timing check; T-152 quality-faces export stays bm-c lane "
              "(bm-c-local data, not executable on bm-a)")
st["current_task"] = "r608: N4-B2 finalize face + SENS products delivered to origin; awaiting bm-b NULLS for batch finalize"
st["updated"] = t.strftime("%Y-%m-%d %H:%M")
st["last_round_at"] = t.strftime("%Y-%m-%d %H:%M")
st["last_round_ts"] = ts_iso
st["last_round"] = 608
indent = 2 if b'\n  "' in raw[:200] or b'\n\t"' in raw[:200] else None
open(p, "wb").write(json.dumps(st, ensure_ascii=False, indent=indent).encode("utf-8"))
print("state r608 written (indent=%s)" % indent)

# ---------- 2) round_reports-bm-a.md append ----------
rp = "round_reports-bm-a.md"
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") or raw.count(b"\r\n") > raw.count(b"\n") // 2 else b"\n"
line = (
 "2026-10-03 05:1x | dept:工程+研究 | watermark verdict=绿（red=false·probe py 0.4% 板清=假期合法 idle·引擎队列 0=N4-B2 波已尽）| "
 "当前活: FUND-VALUE-P1 仅余 bm-b NULLS 在飞（本机 autofill 认领尝试被 crash fuse 正确拒 46 次=双烧保护生效）+ moneyflow rank pass/ah_panel 后台刷新合法 spawn | "
 "最近实物: results/perpetual_faces/n4_b2_results.json（05:1x·池化 K_eff=400 五面·2400 宇宙行）+ results/fund_value_p1/sens.jsonl（500/500 draws·04:50 烧毕·72.5KB）| "
 "下个里程碑: FUND-VALUE-P1 6/6 finalize judged 判决面（bm-b NULLS 落地即收口·窗 ≤48h→10-05）| "
 "did: (1) S0 外科重落善后=r607 reset --mixed（04:52:53）未 checkout 空窗确诊（reflog 取证）：20 D 伪影+23 他机/陈旧 M 面 origin-verbatim 恢复（r595/r607 律）+pool_core_samples union +1 dict 行（CRLF r570/r600 律）；"
 "(2) 双烧污染当场治愈：autofill 04:54:08 按陈旧盘面池视图（pre-r602·VALUEPB-X2 尚 ready）认领 bm-b r602 已交付 done 条目→04:55-05:0x 重复烧录以不同数据快照覆写 cells_VALUE-PB_x2.jsonl 59 行（n_base 3263 vs 3260·p_ret 全变）——幸未 commit 未推·origin 正典完好·verbatim 恢复零损失·坑律入 CODELY.md（daemon 认领读工作树面=r598『claim 可见性=origin refs』daemon 侧复发面）；"
 "(3) SENS 500/500 产物送达 origin（r598 池 done 产物缺位愈合·sens.jsonl+claim 件）；"
 "(4) N4-B2 波 6/6（ledger 04:28:05→04:51:04 六分片各 59-60s）finalize 面 n4_b2_results.json 同轮交付（--wave B2 pin·cumulative pooled K_eff=400·distinct-seed 400/员完备门全过·§4 五面齐·bootstrap seed 69_000 与 B1 确定性同值复证=CE-01 +0.153/VOLATILITY +0.414 两员下界>0 与 B1 同员同值·其余四员跨零·DSR 0.0015-0.0024 深度紧缩如实）+prereg §6 回填（B1 先例镜像·冻结文本只增不改）；"
 "(5) S0.5 双扫 orders 150/150 差集 0（README.md 非令）·D-19=S4U 无 K: 盘 Test-Path False 验证 skip（r597 律·水位 937A373D 不动）；"
 "(6) S1 smoke 47/47；(7) S2 双板：job_list 空·任务板 T-152 open（bm-c→fleet 传输票·数据 bm-c 机本地=非本机可执·留 bm-c 车道）·T-153 bm-b claimed 禁碰；"
 "(8) S6 34 腿全 rc0（新 bar 条件三腿实读跳过·最新 bar 2026-09-30 黄金周；dualrun 首跑 1 DRIFT 观察相记录 streak 重置→复跑 ZERO-DRIFT streak 1/3·reconcile 先行序守法；ORANGE_COOL call·cap 50%·市场态 ORANGE shadow；合法 spawn=moneyflow rank+ah_panel 刷新；车道护栏诚实 no-op 全对）；"
 "(9) S7 自愈 4/4（loop pin :8 no-op 首烧 05:18+watchdog 重注册首烧 05:13+双爪字节级装）+attrition CLEAN（4 healed 注记照录）+state r608 "
 "| 验证证据: smoke 47/47+S6 34 rc0+attrition CLEAN+心跳 epoch int json.loads 自证+orders 150/150 "
 "| 本地未达 origin commit 数: 0（commit 后 push+fetch 自证）"
 " | 下轮指针: bm-b NULLS 落地→FUND-VALUE-P1 6/6 finalize judged 判决面（D6+judged 判线·窗 ≤48h→10-05）；N4-B3+ 按法典 §4 尾律展行时机验再立项；T-152 留 bm-c 车道 [via bm-a r608]"
)
with open(rp, "ab") as f:
    if not raw.endswith(b"\n") and not raw.endswith(b"\r\n"):
        f.write(eol)
    f.write(line.encode("utf-8").replace(b"\n", b"") + eol)
print("round report appended (eol=%s)" % ("CRLF" if eol == b"\r\n" else "LF"))

# ---------- 3) CODELY.md pit append ----------
cm = "CODELY.md"
raw = open(cm, "rb").read()
eol2 = b"\r\n" if raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n")) else b"\n"
pit = (
 "[2026-10-03 05:1x r608 bm-a] 外科重落 checkout 空窗×daemon 认领竞态=done 条目双烧坑（VALUEPB-X2 实弹·r489 新面·origin 零污染当场治愈）："
 "r607 外科重落 reset --mixed（04:52:53）后未做分面 checkout 的空窗内，autofill tick（04:54:08）按陈旧盘面 runnable_pool（pre-r602 视图·VALUEPB-X2 尚 ready）"
 "认领并点火 bm-b r602 已烧完交付条目→04:55-05:0x 重复烧录以不同数据快照覆写 cells_VALUE-PB_x2.jsonl 59 行（n_base 3263 vs 3260·p_ret 全变）；"
 "幸未 commit 未推·分面恢复即愈零损失。根因=活 daemon 认领决策读工作树面（r598『claim 可见性=origin refs』daemon 侧复发面）。"
 "How to apply：外科/FF 重落序列的分面 checkout 必须赶在 daemon 下一 tick 前完成（或 daemon 认领面改读 origin ref）；"
 "轮首见『池已 done 条目有本机新鲜 claim/采样行』先查该窗是否经历过 reset 未 checkout 序列。"
)
with open(cm, "ab") as f:
    if not raw.endswith(b"\n") and not raw.endswith(b"\r\n"):
        f.write(eol2)
    f.write(pit.encode("utf-8") + eol2)
print("CODELY pit appended (eol=%s)" % ("CRLF" if eol2 == b"\r\n" else "LF"))

# ---------- 4) heartbeat ----------
hp = "fleet/machines/bm-a.json"
raw = open(hp, "rb").read()
h = json.loads(raw.decode("utf-8"))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=0.5)
    ram = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    cpu, ram = h.get("cpu_pct", 0.0), h.get("free_ram_gb", 50.0)
h["last_seen"] = ts_iso
h["current_task"] = "r608 closeout: N4-B2 finalize face (K_eff=400) + SENS products delivered to origin; S6 34 legs rc0; awaiting bm-b NULLS for FUND-VALUE-P1 batch finalize"
h["cpu_pct"] = cpu
h["free_ram_gb"] = ram
h["verdict"] = "loaded_ok"
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = ts_iso
h["round_no"] = 608
h["round"] = 608
h["loop_round"] = 608
indent2 = 2 if b'\n  "' in raw[:400] else None
open(hp, "wb").write(json.dumps(h, ensure_ascii=False, indent=indent2).encode("utf-8"))
chk = json.loads(open(hp, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written: epoch=%d (int ok) clock=%s cpu=%.1f ram=%.1f" % (chk["heartbeat_epoch_utc"], chk["clock_read"], cpu, ram))
