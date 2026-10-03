"""r448 bm-c closeout: round report + state + heartbeat (no HANDOVER: 448 not 5x).

All writes json.dump/programmatic + post-write self-verify (state trailing-comma
law + heartbeat epoch int-type law). Hard asserts throughout. r446 template.
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_COMPACT = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
CREATE = 0x08000000

# ---------------------------------------------------------------- 1) round report append
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr_path, "rb").read()
assert raw.endswith(b"\n"), "round report must end with newline"
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
RR_LINE = (
    "watermark: 绿 (red=false ts 06:33 lane healthy; satengine bm-c rc0 alive queue 0; golden-week 合法 idle; N1 W116+ 供给裁定维持关闭〔O-2115 §二·fund-trio NULLS bm-b 在烧 keepalive 06:0x 实证〕) | "
    + NOW + " | r448 | dept:工程 | 当前活: r447 猝死遗产收养+合并收口（未推 commit 882d27793 经 merge 2e9eef1b7 DELIVERED 同步 origin·state/轮报断点治愈）+ O-2115 验收包 LIVE 刷新 ALL_MET 4/4 | "
    "S0: 单 codely 进程三证探测（r643 律·无并发会话）→ r447 遗产定谳=commit 已落 push 未落·state/心跳/轮报停在 r446 → absorb e60f27ba1（3 lane daemon 面）+ merge origin/main 16-behind-1-ahead（单 UU pit-encoding.md append-append union 保双条目：r447 cp936 治愈律+bm-a r662 PS5.1 解码律·EOL 探测 CRLF 实证〔r657 律·断言层首拦后治愈零伤害〕·114 staged 零 marker·18 面 JSON 复验）→ push_verify DELIVERED tip=2e9eef1b7 ahead==0 | "
    "S0.5: orders 152/152 双扫零未回执（ls-tree -r 口径修正自愈·ghost-ack 告警哨抓回）+ D-19 双面 MATCH EB14B510/68947C17（raw-blob 零树触碰）+ inbox 零未读 | "
    "S1: smoke 47/47 | S2/S3: 板 45 claimed 0 open 零可认领; satengine rc0 活 queue 0; T-143 bm-c prep 面 r405-r408 已全交付（余面=他机 lane 装配窗 10-09 后）; town.html 对齐=bm-b r650 已完成（防重复让路）; finalize readiness watcher=bm-b r651 已建（禁重建）; N1 W116+ 维持关闭（O-2115 §二·fund-trio 在烧） | "
    "主产出: O-2115 验收包 live 刷新 ALL_MET 4/4（pack_latest.json + O2115-ACCEPTANCE-LIVE.md 原地再生·new_share 71.6% 持平=金周零新点火实证·10-08 呈报日终跑前可复跑性复证） | "
    "S4: 增量入件 pit-git-parse 1 条（ls-tree 目录 pathspec 缺 -r=只回子树条目→假 unacked=0 全绿危险向·ghost 双向打印告警哨律·r646 同口径律递归深度维）; CODELY 零新条（EOL 复犯=r657 在册律·断言层当场拦截·四问门不复述在册律） | "
    "S6: 37/37 rc0（dualrun ZERO-DRIFT streak 49; compute_audit pool-supply-gap 观察相 ready=3/unclaimed=1; update_daily 金周 cutoff 2026-09-30 零新行; LHB refetch 5432 行零 beyond-cutoff; b_layer 全门过; 11 面 lane-guard/stale-view veto 让路诚实（bm-a 心跳 13-14min fresh）; REPORT/LIVE-2026-10-04 再生; token delta=0 全 L1） | "
    "S7: 自愈 4x 绿（pin5 no-op 06:45/watchdog 在位 06:37/双爪字节恒等零重装）+attrition CLEAN（2 healed 历史注记照录）+orders 双扫复核零漂 | "
    "验证证据: merge 2e9eef1b7 push_verify DELIVERED (tip==remote·ahead==0) + S6 37/37 rc0 + smoke 47/47 + pack selftest 0 fails + live ALL_MET 4/4 | "
    "记分: 1（验收包 LIVE 刷新+pit 入件+合并收口=文件实改·金周观察相合法; r447 主产出分归 r447 commit 本轮仅收养送达） | 记账预算: 3/5（state+心跳+轮报） | 本地未达 origin commit 数: 1（closeout commit 即推·push_verify 自证） | "
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（prescan 未触发; pit-git-parse +1 行=增量入件合法 append 非删除面） | "
    "ceo-visibility: [当前活] r447 治愈收口完成（D-06 全线收口+CODELY mojibake 治愈已同步 origin）·验收包 LIVE 面已刷新 | [最近实物] results/o2115_acceptance/pack_latest.json + docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md @ " + NOW + " | "
    "[下个里程碑] FUND 三族 finalize 窗 10-05..10-09（bm-b r662 rehearsal ALL-GREEN x3·G-SEG/VALUE 两前置裁决待面）+ O-2115 呈报 10-08 + T-143 装配 10-09 后 | "
    "下轮指针: (a) fund-trio finalize 就绪观察（NULLS 烧完+G-SEG GM/VALUE bm-b 两前置） (b) O-2115 pack 10-08 呈报前终跑 (c) O-2030 宝藏保护验收 10-08 (d) T-143 装配 10-09 后"
)
with open(rr_path, "ab") as fh:
    fh.write(RR_LINE.encode("utf-8") + eol)
chk = open(rr_path, "rb").read().decode("utf-8", errors="strict").splitlines()
assert chk[-1].startswith("watermark: 绿") and "r448" in chk[-1], "rr tail"
print("RR-APPEND-OK lines=%d eol=%r" % (len(chk), eol))

# ---------------------------------------------------------------- 2) state update
st_path = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 448
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["last_ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["updated"] = NOW_COMPACT
st["updated_at"] = NOW
st["last_round"] = ("r448 bm-c: r447 dead-session adoption (unpushed commit 882d27793 delivered via merge 2e9eef1b7, D-06 closeout + CODELY heal synced to origin; state/heartbeat/report breakpoint healed) + pit-encoding append-append union + O-2115 pack live refresh ALL_MET 4/4; orders/D19 MATCH; smoke 47/47")
st["current_task"] = ("r448 done (r447 adoption: absorb e60f27ba1 + merge origin/main 16-behind single-UU union + push DELIVERED; O-2115 acceptance pack live rerun ALL_MET 4/4 new_share 71.6%; pit-git-parse +1 entry); next: fund-trio finalize watchers 10-05..10-09, O-2115 pack final run 10-08, T-143 assembly post 10-09")
st["did"] = (
    "r448 bm-c golden-week adoption + maintenance round: "
    "(1) ADOPTION (r643/r637 pattern): r447 session died post-commit pre-S7 -- single-codely three-proof probe clean, absorb 3 lane daemon faces (e60f27ba1), merge origin/main (16 behind/1 ahead), single UU research/pit-encoding.md resolved as line-level union keeping both entries verbatim (r447 cp936 reverse-map heal law + bm-a r662 PS5.1 Get-Content law; CRLF EOL probe per r657 after assert-layer first-intercept), 114 staged files zero-marker sweep + 18 shared-face JSON reparse, merge 2e9eef1b7 push_verify DELIVERED -- r447 D-06 closeout + CODELY mojibake heal now on origin; state/heartbeat/round-report breakpoint healed this round (state counter skips to 448 per next-round-number law). "
    "(2) O-2115 acceptance pack live refresh: selftest 0 fails + run ALL_MET 4/4 (new_share 71.6% flat = golden-week zero new ignitions; pack_latest.json + O2115-ACCEPTANCE-LIVE.md regenerated in place; re-runnability re-proven ahead of 10-08 final run). "
    "(3) S0.5 orders 152/152 double-scan zero un-acked (ls-tree -r caliber fix same-window, ghost-ack telltale caught it) + D-19 dual-face MATCH EB14B510/68947C17 + inbox empty. "
    "(4) S1 smoke 47/47; S2 board 45 claimed 0 open; S3 satengine rc0 alive queue 0; T-143 bm-c prep faces all delivered (r405-r408); town.html align + finalize watcher = already built by bm-b (no-rebuild yield); N1 W116+ stays closed per O-2115 sec-2 (fund-trio fire in-flight). "
    "(5) S4 incremental pit entry x1 -> research/pit-git-parse.md (ls-tree dir pathspec without -r = subtree-entry-only, false unacked=0 danger direction, ghost dual-print sentinel law). "
    "(6) S6 chain 37/37 rc0 (dualrun ZERO-DRIFT streak 49, compute_audit pool-supply-gap observation phase, 11 lane-guard/stale-view honest vetoes to bm-a fresh host, REPORT/LIVE-2026-10-04 regenerated, token delta=0). "
    "(7) S7 self-heal 4x green (loop pin5 no-op, watchdog present, dual claws byte-identical) + attrition CLEAN (2 healed notes)."
)
st["next"] = (
    "(a) FUND trio finalize window 10-05..10-09 watchers (bm-b r662 rehearsal ALL-GREEN x3; two pre-rulings pending: G-SEG GM + VALUE passive bm-b fix; NULLS burn completion -> finalize readiness face). "
    "(b) O-2115 acceptance pack final run at 10-08 governance day (re-runs in place). "
    "(c) O-2030 treasure-protection acceptance 10-08. (d) T-143 assembly post 10-09 (deliver 10-29). (e) W116+ N1 supply reassess after fund-trio finalize."
)
st["verify"] = (
    "merge 2e9eef1b7 push_verify DELIVERED (tip==remote, ahead==0); pit-encoding union sha16=717d5312c3ee85b7 zero-marker 114 files + JSON reparse 18 faces; O-2115 pack selftest 0 fails + live ALL_MET 4/4; S6 37/37 rc0; smoke 47/47; orders 152/152 zero-unacked double-scan; D-19 EB14B510/68947C17 raw-bytes MATCH; attrition CLEAN"
)
with open(st_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_st = json.load(open(st_path, encoding="utf-8"))
assert re_st["round_no"] == 448 and isinstance(re_st["heartbeat_epoch_utc"], int)
print("STATE-OK round=448 epoch=%d" % re_st["heartbeat_epoch_utc"])

# ---------------------------------------------------------------- 3) heartbeat update
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hb_path, encoding="utf-8"))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = st.get("cpu_pct", 0.0), st.get("idle_ram_gb", 0.0)
gpu_free = None
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                        capture_output=True, creationflags=CREATE, timeout=20)
    if p.returncode == 0:
        gpu_free = int(str(p.stdout.decode("ascii", "replace").strip().splitlines()[0]).strip())
except Exception:
    gpu_free = None
hb["activity_now"] = "r447 adoption delivered (merge 2e9eef1b7 DELIVERED: D-06 closeout + CODELY heal on origin); O-2115 pack live refresh ALL_MET 4/4; FUND trio NULLS bm-b in-flight; N1 W116+ closed per O-2115 sec-2"
hb["clock_read"] = NOW
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
hb["current_task"] = st["current_task"]
hb["free_ram_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["latest_artifact"] = "results/o2115_acceptance/pack_latest.json + docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md (O-2115 four statutory items ALL_MET re-proven re-runnable @ 10-08 final-run readiness) @ " + NOW
hb["next_milestone"] = "FUND trio finalize window 10-05..10-09 (G-SEG GM + VALUE passive pre-rulings; bm-b rehearsal ALL-GREEN x3); O-2115 acceptance presentation 10-08; T-143 assembly post 10-09 (deliver 10-29)"
hb["prod_lanes"] = "O-2115 acceptance pack live (4/4 MET, refresh proven); N1 closed per O-2115 sec-2 supply priority (fund-trio has fire); FUND trio NULLS bm-b in-flight; W2 MASS_TRIAL judged+consumed (negative, E27 card)"
hb["round_no"] = 448
hb["updated_at"] = NOW
hb["verdict"] = "green (adoption delivered + golden-week maintenance all-green; board/pool/orders lawful; lane divisions respected)"
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb"):
        hb[k] = gpu_free
with open(hb_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_hb = json.load(open(hb_path, encoding="utf-8"))
assert re_hb["round_no"] == 448 and isinstance(re_hb["heartbeat_epoch_utc"], int) and len(re_hb["orders_ack"]) == 153
print("HEARTBEAT-OK cpu=%.1f ram_free=%.1f gpu_free=%s epoch=%d acks=%d" % (cpu, ram_free, gpu_free, re_hb["heartbeat_epoch_utc"], len(re_hb["orders_ack"])))
print("CLOSE-ALL-GREEN", NOW)
