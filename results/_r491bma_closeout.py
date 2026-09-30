# r491 bm-a closeout: state round_no 491 + heartbeat (epoch int / ISO clock_read)
# + round report line + T-129 progress note + CODELY memory entry (S4).
# L1 deterministic, zero network. Evidence discipline per S3.
import json, time, datetime, psutil, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now = datetime.datetime.now()
ts_min = now.strftime("%Y-%m-%dT%H:%M") + "+08:00"
clock_read = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

# --- 1) state-bm-a.json: round_no 490 -> 491 ---
with io.open("state-bm-a.json", "r", encoding="utf-8") as f:
    state = json.load(f)
assert state["round_no"] == 490, f"unexpected round_no {state['round_no']}"
state["round_no"] = 491
state["last_round"] = ("2026-09-30 r491: banned-gate LANDED (r471 dead-GM-session adoption: registry+template-s05 verified, "
                       "missing gate script built, selftest 8/8 + realfire 3) + 09-30 bar landed 20:42 (r485 window closed, "
                       "36 rows + live.paper hook accrual rc0) + PROSPECT anchor drift 22/22 ROOT-CAUSED and FIXED "
                       "(RW-1 aftermath: exit-T+1-open not param-gated, r475 legacy pin cannot reproduce pre-RW-1 "
                       "evidence; refreeze same-cutoff per r472 precedent, 22 members, 6 sign-flips disclosed, "
                       "t24paper 22/22 PASS + 09-30 accrual, promotion 0/22 honest) + S6 37 legs rc0 + CODELY union "
                       "5970B + stranded-window closeout")
with io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
    f.write("\n")

# --- 2) heartbeat fleet/machines/bm-a.json ---
vm = psutil.virtual_memory()
cpu_pct = psutil.cpu_percent(interval=1.0)
try:
    import subprocess
    gout = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
    gpu_free_gb = round(float(gout.stdout.strip().splitlines()[0]) / 1024.0, 2)
except Exception:
    gpu_free_gb = None
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = clock_read
hb["current_task"] = ("post-realign normal flow resumed (stranded window closed r491); 10-01 month-first trio "
                      "(science_audit/monthly_briefing/self_review) + REGIME_GUARD v3 auto-activate + fullburn window open")
hb["cpu_cores"] = 32
hb["cpu_pct"] = round(cpu_pct, 1)
hb["free_ram_gb"] = round(vm.available / (1024**3), 1)
if gpu_free_gb is not None:
    hb["gpu_free_vram_gb"] = gpu_free_gb
hb["round_no"] = 491
hb["verdict"] = ("healthy: r491 done -- banned-gate LANDED (Tools/banned_direction_gate.py + BANNED_DIRECTIONS registry + "
                 "PREREG_TEMPLATE s0.5, D-41 sec.1.2 face live, selftest 8/8, realfire CJK fire confirmed; r471 adoption of "
                 "dead GM-session half-product) + 09-30 bar landed 20:42 (36 rows, live.paper hook rc0 shadow, full S6 37 legs "
                 "rc0 incl gated family) + PROSPECT 22-member anchor refreeze same-cutoff (RW-1 exit-at-open aftermath: "
                 "first-new-bar drift 22/22 root-caused, r472 precedent applied, t24paper 22/22 PASS + 09-30 accrual + "
                 "promotion 0/22 honest, diff results/RW1_PROSPECT_REFREEZE_2026-09-30.md, 6 sign-flips disclosed) + CODELY "
                 "3-way union zero-loss 5970B + hot-cold pass (8 entries to archive r491 window-batch) + stranded-window "
                 "closeout (surgical push + mixed reset); smoke 47/47, orders 129/129, decisions zero-new")
hb["heartbeat_epoch_utc"] = epoch  # python int -> JSON int (R170/R178 law)
hb["clock_read"] = clock_read
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb["clock_read"] and "+08:00" in hb["clock_read"], "clock_read must be ISO T + offset"
with io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch roundtrip must be int"
print(f"[closeout] state 490->491 OK; heartbeat epoch={epoch} (int) clock={clock_read} cpu={cpu_pct:.1f}%")

# --- 3) round_reports-bm-a.md r491 line ---
report_line = (
    ts_min + " | r491 | dept:研究+工程 | WM=py_low_board_clear 绿（板 open=0·bandit 0·red=False·O-1901 闸4 合法 idle 白名单）| "
    "**滞留窗收口轮+禁开闸落地轮**："
    "(1)S0.5 双扫=orders 129/129 零未回执（ghost 2=远端已投未同步件·reset 后自现）+decisions 尾 D-41 零新行（D-41=本窗执行面本身） "
    "(2)S1 smoke 47/47 "
    "(3)**禁开方向硬闸落地（T-129 D-41 §1.2·r471 同机死会话收养）**：GM 会话 1.6h 零仓内写+进程树核=死会话判定→半成品逐件验后全数收养"
    "（research/BANNED_DIRECTIONS.json 9 方向登记表·usage 行 ps1→py 接口对齐+staged PREREG_TEMPLATE §0.5）→缺件补齐="
    "**Tools/banned_direction_gate.py 当窗建成**（fail-closed 准入闸：BAN 模式扫正文除 §0.5 自引段+例外三字段验=BAN-xx 引用/"
    "new_data|new_mechanism/不可能看见陈述·UTF-8 stdout 契约〔Windows pipe GBK 坑修复〕）；selftest 8/8 全过（清洁放行/无例外拒/完整例外放行/"
    "占位符拒/缺登记表 fail-closed/缺 prereg fail-closed/错号引用拒/§0.5 自引免疫）+实弹 3 份真 prereg（FUSION_GRID/CN_CORE_DDCTL/AGGR "
    "全部 REJECT=BAN-04/08 CJK 模式真弹触发；BAN-04 裸'网格'对 CSCV 方法论提及的敏感面如实披露=登记表正主未来裁量面·本窗零改动冻结面）"
    "→证据 results/_r491bma_banned_gate_selftest.json+_r491bma_gate_realfire.json "
    "(4)**09-30 bar 20:42 落地（r485 源滞后窗收口）**：update_daily 36 行+live.paper hook 同步过锚 rc0（v3 日期门 10-01 未开=诚实降级 shadow）"
    "+S6 37 腿 rc0（主链 5min 静默工具超时杀于 [repo]→resume 链全绿〔r282 bm-c 同族坑：工具取消不保杀子进程·options 分离刷新幸存自愈〕"
    "+bar-gate 探针误读 sh510300〔bm-b 车道件〕=**r286 bm-c 归档坑同窗自踩实证**→gated 链探针修为裸码 510300 面全跑：livepaper 幂等复核/"
    "t35v PASS 零挂单/aggr/alloc/grid/sysv1/t35export 09-30 累计全过；t24paper rc=2 锚漂移 22/22（猝死会话报告行误书'全过'·收养会话实弹复跑抓获）→(4b)）"
    "(4b)**PROSPECT 锚漂移根因+当窗修复（RW-1 余波·r472 先例收口）**：r472 出场改 T+1 开盘成交=无条件引擎语义（审计 P0-1 前视修复），"
    "6 注册员同窗已同 cutoff 重冻结、22 PROSPECT 未跟进=r475'pinned legacy'假设在真弹面不成立（出场时点不受参数钉扎管辖；无新 bar 窗口 selftest 证不了复现）"
    "→首个新 bar 窗（09-30 bar 20:42）22/22 全漂【三型实证：ANTS 187→181 笔/full_sharpe 0.2599→-0.0086；TMU-CE 笔数不变 sharpe 翻号】"
    "→修法=按 r472 注册员先例同冻结 cutoff 2026-09-22 现引擎重算重冻结 22 员（recorded_*+backtest 镜像+anchor_status 溯源；g1_pass/paper 史/params 零触碰）"
    "+diff 披露表 results/RW1_PROSPECT_REFREEZE_2026-09-30.md（6 员 full_sharpe 正→非正翻号与前视高估方向一致；g1 复评=science face 裁量本窗不越权）"
    "→复验 t24paper 22/22 锚全过+09-30 追踪累计 rc0+promotion 0/22 诚实+smoke 47/47"
    "(5)**CODELY 三方 union+热冷整编**：merge-base 三方合并（ours=GM 指针替换 5 条/theirs=bm-b/c r476/477/282/284/285/286 七新条）"
    "零丢失审计过（D-41 r483 条=GM mem-q-001 指针替换保留·内容=指针目标+TRACK 正典）→union 11,470B 超 ≤10KB 硬线→当窗热冷整编="
    "8 条 verbatim 迁 research/memory-archive/202609.md『r491 bm-a 窗批』节（远端基+追加·本地陈旧面零 clobber）→热层 5,970B 达标 "
    "(6)**滞留窗收口序执行**（r484-490 六窗 watch 终结）：pathspec 提交+外科推（overlay=本轮触面∪my-4 非交集车道件∪union 件·"
    "32 交集面未再生者远端新版保留）+mixed reset origin/main→树清下轮 S0 ff 复通（本行时点④⑤在 S7 执行段） "
    "(7)S7=自愈三件套+attrition 扫描+心跳 epoch int 双验 "
    "| 下轮指针：10-01 月首轮三件套（science_audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门自动激活（禁手改）+"
    "fullburn 窗开启（10-01..re-open-10-09·nice NORMAL 已接线）+RW-5 外审复核 10-03+T-129#1 prereg 起草恢复（禁开闸已在本轮落地可用）"
)
with io.open("round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(report_line + "\n")
print("[closeout] round report r491 line appended, %d chars" % len(report_line))

# --- 4) T-129 progress note ---
p129 = "fleet/tasks/T-2026-09-30-129.json"
t = json.load(io.open(p129, encoding="utf-8"))
t["progress_r491"] = ("r491 bm-a: BANNED-GATE LANDED -- dead GM-session half-product adopted per r471 (liveness probe 1.6h "
                       "silent): research/BANNED_DIRECTIONS.json (9 directions, usage line aligned to py interface) + staged "
                       "PREREG_TEMPLATE s0.5 verified, missing Tools/banned_direction_gate.py BUILT this window (fail-closed "
                       "admission gate, selftest 8/8, realfire 3 real preregs REJECT on BAN-04/08 CJK fire, UTF-8 stdout "
                       "contract); evidence results/_r491bma_banned_gate_selftest.json + _r491bma_gate_realfire.json; "
                       "observation for science owner: BAN-04 bare-'wangge' pattern fires on CSCV-methodology mentions "
                       "(CN_CORE_DDCTL L58) -- registry tuning is GM/science face, zero silent edits this window")
io.open(p129, "w", encoding="utf-8", newline="\n").write(json.dumps(t, ensure_ascii=False, indent=1) + "\n")
print("[closeout] T-129 progress_r491 note written")

# --- 4b) T-127 progress note (RW umbrella: PROSPECT refreeze under D-05) ---
p127 = "fleet/tasks/T-2026-09-30-127.json"
if os.path.exists(p127):
    t127 = json.load(io.open(p127, encoding="utf-8"))
    t127["progress_r491"] = ("r491 bm-a: PROSPECT 22-member anchor refreeze same-cutoff 2026-09-22 (RW-1 "
                             "aftermath): first new-bar window after r472 exit-T+1-open fix surfaced 22/22 "
                             "drift (r475 legacy pinning cannot reproduce pre-RW-1 evidence -- exit timing "
                             "is not param-gated); fixed per r472 registered-member precedent, diff table "
                             "results/RW1_PROSPECT_REFREEZE_2026-09-30.md, 6 full_sharpe sign-flips "
                             "disclosed; t24paper 22/22 PASS + 09-30 accrual, promotion 0/22 honest; "
                             "g1 re-evaluation under refrozen evidence = science-face decision, not taken")
    io.open(p127, "w", encoding="utf-8", newline="\n").write(
        json.dumps(t127, ensure_ascii=False, indent=1) + "\n")
    print("[closeout] T-127 progress_r491 note written")
else:
    print("[closeout] T-127 ticket file absent, note skipped")

# --- 5) CODELY.md S4 memory entry (one entry, four-gate passed) ---
entry = (
    "- [2026-09-30 21:1x r491 bm-a] 滞留窗收口序（r484-490 六窗 watch 后 r491 全收口实证·r471/r486/外科净路 组合律）："
    "并发 GM 会话 staged 态+远端推进=本地 ahead>0/behind N 且 rebase 拒时，全收口序=①r471 探活（~1.5h 零仓内写+进程树核）"
    "→死会话半成品逐件验后收养②缺件补齐（本例：登记表+staged 模板 §0.5 在、引用的 gate 脚本缺→当窗建成+selftest）"
    "③pathspec 提交本窗产出④fresh fetch 后外科推（temp-index read-tree origin/main+overlay=本轮触面∪my-4 非交集车道件∪"
    "union 件；交集面本轮未再生者不 overlay=远端新版保留）⑤mixed reset origin/main+陈旧 derive 面 checkout 远端版→树清、"
    "下轮 S0 ff 复通。CODELY 交集=merge-file 三方（base=merge-base）；union 后 >10KB=当窗热冷整编（本窗 11,470→5,970B）。"
    "How to apply：滞留窗勿只守望，探活过线即按此序一次收口；新 bar 触发判读面必读裸码 <码>.csv（r286 律·本窗 gated 链自踩实证）。\n"
    "- [2026-09-30 21:4x r491 bm-a] 引擎语义变更×参数钉扎≠证据复现律（PROSPECT 锚漂 22/22 实弹·RW-1 余波）："
    "引擎级无条件语义变更（RW-1 出场同收盘成交→T+1 开盘）不受 trade_pnl_mode/strict_open_fills 参数钉扎管辖——"
    "r475 给 22 PROSPECT 钉 legacy 后仅跑离线 selftest（fixture）即宣称复现=未验真弹；首个新 bar 窗必爆 22/22 锚漂"
    "（无新 bar 的窗口 selftest 绿≠复现绿）。修法=r472 注册员先例：同冻结 cutoff 现引擎重算重冻结（recorded_*+镜像面+"
    "anchor_status 溯源），g1 复评归 science face 禁顺手翻。How to apply：今后任何引擎语义变更落地时，受影响登记证据面"
    "必须当窗逐员重算验证（无新数据窗=用真弹 replay 探针替代 selftest 断言复现），不能复现即按先例重冻结+diff 披露，"
    "禁以参数钉扎替代重冻结。\n"
)
with io.open("CODELY.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(entry)
size = os.path.getsize("CODELY.md")
print("[closeout] CODELY S4 entry appended, size=%dB (10KB line: %s)" % (size, size <= 10240))
assert size <= 10240, "CODELY hot layer over 10KB"
print("[closeout] ALL DONE rc=0")
