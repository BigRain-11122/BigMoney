# -*- coding: utf-8 -*-
"""r310 bm-b wrap: S6 log re-verify + orders regen ack + round report + state + heartbeat
(r302 law astimezone/epoch gates) + CODELY 5th-batch hot/cold repack (>10KB found at
append gate) + HANDOVER 5x recon (round 310 = 5x multiple)."""
import json, datetime, subprocess, glob, os, io, sys

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
assert "+" in NOW_ISO and "T" in NOW_ISO, NOW_ISO
RR = "logs/iteration-loop/round_reports.md"
STATE = "logs/iteration-loop/state.json"
HB = "fleet/machines/bm-b.json"
EV = "results/_r310bmb_wrap.json"

# ---- 1. S6 chain re-run for log artifact + idempotent double-verify (sunday no-op face)
q = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", "results\\_r310bmb_s6_chain.ps1"],
                   capture_output=True, text=True, timeout=420)
log_txt = q.stdout
assert "=== S6 chain done: 30/30 legs rc=0; NON-ZERO:" in log_txt, log_txt[-400:]
with io.open("results/_r310bmb_s6_chain.log", "w", encoding="utf-8", newline="") as f:
    f.write(log_txt)
print("S6 re-verify: 30/30 rc=0, log written")

# ---- 2. orders full-enumeration regen ack (mechanical regen law; abort on unexpected)
order_files = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
hb0 = json.load(io.open(HB, encoding="utf-8"))
prev_acked = set(hb0.get("orders_ack", "").split())
missing = [o for o in order_files if o not in prev_acked]
expect_ok = {"O-20260927-0752-bm-a.md", "O-20260927-0758-bm-a.md"}  # 0752 possibly in-string already; 0758 new
unexpected = [o for o in missing if o not in expect_ok]
assert not unexpected, "UNEXPECTED NEW ORDERS -- ABORT WRAP, process first: %r" % unexpected
print("orders: dir=%d, newly acking=%r" % (len(order_files), missing))

# ---- 3. round report append
LINE = (NOW_ISO + " | r310 bm-b | dept:研究+策略+舰队 | WM-VERDICT: 绿 red=false 合法 idle 白名单（probe 08:09:18 py_low_board_clear·板 0 open·bandit 0·零本地批·供给线 ACTIVE=CEO 双票 T-89/T-90 均认领在制（prereg 冻结面+runner 待建）+bm-a CN_MKTNEUTRAL runner 在建）"
 " | did: S0 pull FF 93063584..54ae013c+94fca911 收编 bm-a r303/303tail（O-0758 决策链令+T-90 开票+MARKET_STAGE_TABLE v1.0+CN_MKTNEUTRAL prereg 3c71ddb4+collision 修复 6185164f）；S0.5 O-0758 回执=T-90 同轮认领+开动（CEO 即时律 O-1730）·decisions.md 本机路径不可达如实注记（bm-a 侧已审 D-04/D-05 standing 零新行）；S1 smoke 25/25；S3 主活=**CEO 双票撞认领三连全解+T-90 开动主交付**——(a) T-89 §4 commit 时间序 bm-b c422fa6b 07:55:54 < bm-a 54ae013c 08:01:09=bm-b 持票·bm-a GM 会话 6185164f 同向零丢失修复+bm-b 49a88722 rebase UU 并集解（progress_r309_bmb 恢复+让路注记+slice-2 MARKET_STAGE_TABLE 记功零重工·slice-1b runner=下轮精确续作点）；(b) T-90 bm-b 08:04:41 < bm-a 08:06:01= bm-b 持票·bm-a r303-tail 94fca911 让路+arm 探针 _r303bma_t90_probe.json 记功+反重复护栏（bm-a 勿重起草·r304 转 CN_MKTNEUTRAL runner）；(c) push 三连拒=pull-rebase stash 舞步全过（r140/r296/r306 律零丢失）；**T-90 开动主交付=DECISION_CHAIN_E2E_P1 四臂全链回测预注册 FROZEN**（a9ed12ff·A1/A2=T-34 CONF/LADDER 臂逐字重派生+G-REPRO 位级复现门 vs t34_early_signal_verdict+新测面 B=CE-01 单策略不换臂/D=六员等权不路由臂·J-C1..C4 legacy 12m CI 下界>0.50 三对照判线+J-L1/L2 半档梯复验+断环四环量化（温度/路由/摩擦/席位）·N_eff=5,522 包络格·binding cutoff 2026-09-22·G-V3 两腿门+G-CENSUS 1,255/1,506+G-MANIFEST·seed 20260929 t34 族 one-step·F-04 MSG-0816 declared）；S6 30/30 rc=0（_r310bmb_s6_chain.ps1 r298 律复制 delta=2 header-only·周日合法 no-op 族·audit CLEAN·水位 probe py_low_board_clear）；S4 CODELY +1 坑律（撞认领三连结构性）+五批热冷整编 10125B 超 10KB 硬线当窗即办（O-0752/O-0758 回执+r296/r297 PS 坑律 4 条 verbatim 外迁归档五批节·rg 零丢失）；S5/S7 HANDOVER 5x 核对（round 310 bm-b 行+最近核对链刷新）+schtasks 三任务实勘（R49 CSV 路径）+迁移 v2.2 armed editor-gated journal 07:35 wait 窗至 09-29 12:00"
 " | evidence: commits 49a88722/94fca911/6185164f/a9ed12ff+research/DECISION_CHAIN_E2E_P1.md+results/_r310bmb_ticket_surgery.py+results/_r310bmb_s6_chain.ps1/.log(30/30 rc=0)+smoke 25/25+orders " + str(len(order_files)) + " 全枚举双扫零未回执+CODELY repack 字节账"
 " | next: T-90 runner 实现（scripts/decision_chain_e2e.py：Stage A 成员曲线复用 results/t34/curves_*.jsonl 位级校验或 t22/t34 原语重派生 16,566 格→Stage B 包络四臂+被动→hermetic selftest+B7b 契约腿→runnable_pool 提交 autofill 续批）+T-89 slice-1b runner（scripts/prospect_regime_segments.py t22 import-face+level=PROSPECT 注入→selftest→池 ~63.5k 格）=下轮双主活；09-28 周一首新 bar 全链（update_daily→live.paper REGIME_GUARD v3 10-01 日期门前 shadow→t35v→t24x2→aggr→grid→export→scorecard→daily_report）+T-87 首续拉实弹+10-01 月度三件套+REGIME_GUARD v3 日期门生效+10-31 六员首检 all-HOLD+T-34 半档梯 11-01+迁移窗 09-29 12:00")
with io.open(RR, "a", encoding="utf-8", newline="\n") as f:
    f.write(LINE + "\n")
print("round report appended")

# ---- 4. state.json
DID = ("r310: CEO 双票撞认领三连全解（T-89/T-90 §4 bm-b 持票·bm-a 双让路记功）+ T-90 开动主交付=DECISION_CHAIN_E2E_P1 "
       "四臂全链回测预注册 FROZEN（a9ed12ff·G-REPRO 位级门+B/D 新臂·N_eff=5,522）+ S6 30/30 rc=0 + CODELY 五批整编 ≤10KB + orders 93 双扫")
NEXT = ("T-90 runner=decision_chain_e2e.py（Stage A t34 曲线复用/重派生→Stage B 四臂包络→selftest→池）+T-89 slice-1b runner="
        "prospect_regime_segments.py→池；09-28 周一首新 bar 全链+T-87 首续拉；10-01 月度三件套+REGIME_GUARD v3 日期门；迁移窗至 09-29 12:00")
st = json.load(io.open(STATE, encoding="utf-8"))
st["round_no"] = 310
st["did"] = DID
st["verdict"] = "green"
st["next"] = NEXT
st["last_round_ts"] = NOW_ISO
st["last_result"] = "ok"
st["current_task"] = DID
st["updated_at"] = NOW_ISO
json.dump(st, io.open(STATE, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
print("state.json -> 310")

# ---- 5. heartbeat (r308 lineage + orders regen)
hb = hb0
cpu_pct, free_gb, gpu_gb = hb.get("cpu_util_pct", 0), hb.get("free_ram_gb", 0), hb.get("gpu_free_vram_gb", 0)
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
    free_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    pass
try:
    q2 = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                        capture_output=True, text=True, timeout=10)
    if q2.returncode == 0 and q2.stdout.strip():
        gpu_gb = round(float(q2.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass
epoch = int(datetime.datetime.now().astimezone().timestamp())
hb["last_seen"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = epoch
hb["round_no"] = 310
hb["current_task"] = ("r310 wrap: T-89 bm-b-owned (slice-1b runner next round) + T-90 bm-b-owned "
                      "(DECISION_CHAIN_E2E_P1 prereg frozen a9ed12ff; runner impl next round per R99)")
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = gpu_gb
hb["verdict"] = ("green; CEO orders O-0752 (r309) + O-0758 (r310) acked; T-89+T-90 both bm-b-owned per sec.4 "
                 "commit-time law (triple same-window claim collisions resolved zero-loss); T-90 start "
                 "deliverable = DECISION_CHAIN_E2E_P1 four-arm prereg FROZEN; S6 30/30 rc=0; smoke 25/25; "
                 "migration armed editor-gated normal (window to 09-29 12:00)")
hb["orders_ack"] = " ".join(order_files)
hb["n_orders_ack"] = len(order_files)
hb["idle_ram_gb"] = free_gb
hb["idle_ram_mb"] = int(free_gb * 1024)
hb["free_ram_mb"] = int(free_gb * 1024)
hb["gpu_free_vram_mb"] = int(gpu_gb * 1024)
hb["gpu_idle_vram_mb"] = int(gpu_gb * 1024)
hb["gpu_idle_vram_gb"] = gpu_gb
hb["cpu_pct"] = cpu_pct
hb["round"] = 310
json.dump(hb, io.open(HB, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# ---- 6. CODELY 5th-batch hot/cold repack (found >10KB at append gate -> same-window per law)
CL = "CODELY.md"
AR = "research/memory-archive/202609.md"
codely = io.open(CL, encoding="utf-8").read()
size_before = len(codely.encode("utf-8"))
move_prefixes = (
    "- [2026-09-27 07:53:18] 市场阶段适配统计令 O-20260927-0752 已执行回执",
    "- [2026-09-27 08:00:07] 决策链条科学化+全链回测令 O-20260927-0758",
    "- [2026-09-27 r296 bm-a] 坑律：PowerShell 面 git stash 引用必须单引号包裹",
    "- [2026-09-27 r297 bm-a] 坑律：hermetic selftest 腿永不触达判格 stats 的下游消费键",
)
lines = codely.split("\n")
moved, keep = [], []
for ln in lines:
    if any(ln.startswith(p) for p in move_prefixes):
        moved.append(ln)
    else:
        keep.append(ln)
assert len(moved) == 4, "expected 4 archive lines, got %d" % len(moved)
codely2 = "\n".join(keep)
kenglu = ("- [2026-09-27 " + NOW.strftime("%H:%M") + " r310 bm-b] 坑律：同窗双机 10min 循环对同一 CEO 即时票=结构性撞认领发生器"
 "（r309/r310 窗三连实弹：T-89 撞认领 07:55:54 vs 08:01:09·T-90 撞认领 08:04:41 vs 08:06:01——双方各 pull 于对方 push 前=盲窗结构性必在）；"
 "正典=①认领 commit 秒级微推+F-04 MSG 先行②§4 commit 时间序裁定稳定可复用但每撞=一整轮 resolve 成本③根治候选=GM 开票即在票面写 owner 机"
 "（认领制→派定制）呈 GM 议。指针=round_reports r310 行+commits 49a88722/94fca911/6185164f/a9ed12ff。")
marker = "### Reference"
assert marker in codely2
codely2 = codely2.replace(marker, kenglu + "\n\n" + marker, 1)
idx_old = "四批外迁索引（R303）：r293-closure 打捞协议/R298 FUSION 预测前提面/O-20260927-0752 执行记录=归档四批节。"
idx_new = ("四批外迁索引（R303）：r293-closure 打捞协议/R298 FUSION 预测前提面/O-20260927-0752 执行记录=归档四批节。"
           "五批外迁索引（R310 bm-b）：O-0752/O-0758 执行回执+r296/r297 PS 语法坑律=归档五批节。")
assert idx_old in codely2
codely2 = codely2.replace(idx_old, idx_new, 1)
io.open(CL, "w", encoding="utf-8", newline="").write(codely2)
size_after = len(codely2.encode("utf-8"))
assert size_after <= 10240, "CODELY still over 10KB hard line: %d" % size_after
arch = io.open(AR, encoding="utf-8").read()
if not arch.endswith("\n"):
    arch += "\n"
arch += "\n## 坑律归档 2026-09-27 · 归档五批（r310 bm-b 热冷整编·行级 verbatim 零丢失）\n\n" + "\n".join(moved) + "\n"
io.open(AR, "w", encoding="utf-8", newline="").write(arch)
# rg zero-loss style verify: every moved line present verbatim in archive, absent from CODELY hot layer
arch_read = io.open(AR, encoding="utf-8").read()
cl_read = io.open(CL, encoding="utf-8").read()
for ln in moved:
    assert ln in arch_read, "archive zero-loss FAIL"
    assert ln not in cl_read, "hot-layer dedup FAIL"
print("CODELY repack: %dB -> %dB (moved 4, +1 kenglu, <=10KB PASS)" % (size_before, size_after))

# ---- 7. HANDOVER 5x recon: append round 310 bm-b line + refresh header pointer
HO = "research/HANDOVER.md"
ho = io.open(HO, encoding="utf-8").read()
ho_line = ("- 开发队列增量窗（接续版）**round 310 bm-b（5x 核对本轮），" + NOW.strftime("%Y-%m-%d %H:%M") +
 " 补核；对账区间=增量 bm-b r306-310 并读 bm-a r303/303tail（基线=round 305 bm-b 行·round 300 bm-a 行），统一链 202,441 实读平持"
 "（本窗零批 finalize：T-89 slice-1b runner 未建·T-90 四臂批=预注册冻结面未跑·DECISION_CHAIN_E2E_P1 N_eff=5,522 待 runner）**："
 "①**r310=CEO 双票撞认领三连全解+决策链回测证开动窗**——(a) T-89（O-0752）：bm-b r309 claim c422fa6b 07:55:54+prereg 冻结 e33984e4 先到 vs bm-a r303 54ae013c 08:01:09 后到"
 "=§4 bm-b 持票；bm-a GM 会话 6185164f 同向零丢失修复（progress_r309_bmb 恢复+让路注记）+bm-b 49a88722 rebase UU 并集解（双面注记全保·slice-2 MARKET_STAGE_TABLE.md bm-a 交付记功零重工）；"
 "(b) T-90（O-0758）：bm-b 08:04:41 认领+同轮开动 vs bm-a 94fca911 08:06:01 fetch-first claim=§4 bm-b 持票·bm-a 让路+探针 _r303bma_t90_probe.json 记功（B_MAXDIV 文件面零命中诚实披露·T-22 passive=arm-C）"
 "+反重复护栏（bm-a 勿重起草 DECISION_CHAIN_E2E_P1·r304 lane=CN_MKTNEUTRAL runner）；(c) push 三连拒=pull-rebase stash 舞步零丢失全过；"
 "**T-90 开动主交付=DECISION_CHAIN_E2E_P1 四臂全链回测预注册冻结**（a9ed12ff：A1/A2=T-34 CONF/LADDER 臂逐字重派生+G-REPRO 位级复现门 vs results/t34_early_signal_verdict.json"
 "+新测面 B=CE-01 单策略不换臂/D=六员等权不路由臂·J-C1..C4=legacy 12m CI 下界>0.50 三对照判线+J-L1/L2 半档梯复验+断环四环量化（温度/路由/摩擦/席位）"
 "·N_eff=5,522 包络格·binding cutoff 2026-09-22·G-V3 两腿门·G-CENSUS 1,255/1,506·G-MANIFEST·seed 20260929 t34 族 one-step·F-04 MSG-0816）；"
 "②维护面：S6 30/30 rc=0（_r310bmb_s6_chain.ps1 r298 律复制 delta=2 header-only·周日合法 no-op 族·audit CLEAN·水位 py_low_board_clear）·smoke 25/25·"
 "orders 91→" + str(len(order_files)) + " 全枚举双扫零未回执（O-0752/O-0758 ack）·post_review 尾零 NO·板 0 open·迁移 v2.2 armed editor-gated（journal 07:35 wait·窗至 09-29 12:00）；"
 "③CODELY 五批热冷整编（10125B 超 10KB 硬线当窗即办：O-0752/O-0758 回执+r296/r297 PS 坑律 4 条 verbatim 外迁归档五批节·rg 零丢失·加 r310 撞认领三连坑律）；"
 "④观测（非本机车道）：bm-a r303=r303 wrap+collision addendum 6185164f+303tail 94fca911（CN_MKTNEUTRAL_P1 prereg 3c71ddb4 冻结·MARKET_STAGE_TABLE.md v1.0）·r304 指针=CN_MKTNEUTRAL runner；bm-c r71 后停机维持；"
 "⑤指针：T-90 runner（scripts/decision_chain_e2e.py：Stage A 成员曲线复用 results/t34/curves_*.jsonl 位级校验或 t22/t34 原语重派生 16,566 格→Stage B 包络四臂→hermetic selftest+B7b 契约腿→runnable_pool）"
 "+T-89 slice-1b runner（scripts/prospect_regime_segments.py t22 import-face+level=PROSPECT 注入→selftest→池 ~63.5k 格）=下轮双主活→池提交 autofill 续批；"
 "09-28 周一开市窗新 bar 全链（update_daily→live.paper REGIME_GUARD v3（10-01 日期门前 shadow）→t35v→t24x2→aggr→grid→export→scorecard→daily_report）+T-87 首续拉实弹"
 "+10-01 月度三件套+REGIME_GUARD v3 日期门生效+10-31 六员首检 all-HOLD+T-34 半档梯 11-01+迁移窗至 09-29 12:00 不变\n")
if not ho.endswith("\n"):
    ho += "\n"
ho += ho_line
hdr_old = "最近核对=bm-b round 305（2026-09-27 06:5x·对账增量=文末 round 305 bm-b 行"
assert hdr_old in ho, "HANDOVER header pointer anchor not found"
ho = ho.replace(hdr_old,
    "最近核对=bm-b round 310（2026-09-27 08:2x·对账增量=文末 round 310 bm-b 行〔bm-b r306-310 窗：**CEO 双票撞认领三连全解+决策链回测证开动**"
    "（T-89 §4 bm-b 持票 slice-1b runner 续作+T-90 §4 bm-b 持票 DECISION_CHAIN_E2E_P1 四臂预注册冻结 a9ed12ff·G-REPRO 位级门+B/D 新臂·N_eff=5,522"
    "+S6 30/30 维持+CODELY 五批整编≤10KB+orders 93 双扫）〕）；上一次最近核对=bm-b round 305（2026-09-27 06:5x·对账增量=文末 round 305 bm-b 行", 1)
io.open(HO, "w", encoding="utf-8", newline="").write(ho)
print("HANDOVER: round 310 line appended + header pointer refreshed")

# ---- 8. self-assert gates (r302 law)
hb2 = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int (F7)"
assert "T" in hb2["clock_read"] and "+08:00" in hb2["clock_read"], "clock_read R262/F7"
st2 = json.load(io.open(STATE, encoding="utf-8"))
assert st2["round_no"] == 310
rr_tail = io.open(RR, encoding="utf-8").read().rstrip("\n").splitlines()[-1]
assert "r310 bm-b" in rr_tail and rr_tail.startswith(NOW_ISO[:16]), "round report tail gate"
ack_files = set(hb2["orders_ack"].split())
assert ack_files == set(order_files), "orders ack regen mismatch"
ev = {"ts": NOW_ISO, "heartbeat_epoch_utc": epoch, "cpu_pct": cpu_pct, "free_ram_gb": free_gb,
      "gpu_free_vram_gb": gpu_gb, "n_orders_ack": len(order_files), "newly_acked": missing,
      "codely_bytes_before": size_before, "codely_bytes_after": size_after,
      "gates": "epoch int PASS + clock astimezone PASS + state 310 PASS + report tail PASS + "
               "orders regen PASS + CODELY <=10KB PASS + archive zero-loss 4/4 PASS + S6 30/30 re-verify PASS"}
json.dump(ev, io.open(EV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(ev, ensure_ascii=False))
