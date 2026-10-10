# r823 bm-b S7 closeout: state.json 822->823 + heartbeat + round ledger row
# (r801bmb_closeout.py mechanical pattern; r818 big-list law: load-modify-save only, orders_ack untouched)
import io, json, time, datetime, subprocess

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# best-effort machine sampling (fallback: keep previous value)
def sample_ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / 2**30, 1)
    except Exception:
        return None

def sample_gpu_mb():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                              "--format=csv,noheader,nounits"],
                             capture_output=True, timeout=20)
        return round(float(out.stdout.decode().strip().splitlines()[0]))
    except Exception:
        return None

# --- state.json ---
s = json.load(io.open("state.json", encoding="utf-8"))
s["round_no"] = 823
s["note"] = ("r823: P3-E3 northbound funds data-source reachability scan adjudicated NEGATIVE-closure "
             "(disclosure cliff empirically confirmed: core flow columns 100% NaN since 2024-08-16 across 3 hist faces, "
             "candidate anchor 2024-08-19 split-window only, measured last_nonnull is canon; minute face 241 rows all-0.0 "
             "placeholder trap; per-stock face frozen 2024-08-16; sparse exception days 2026-04-08/2024-09-27 on record; "
             "residual live fields single-source EM + frozen-holdings attribution unverifiable -> no viable production lane "
             "under current disclosure regime, T-67 s2 forward 12-month window unreachable = E2-options isostructure): "
             "probe scripts/northbound_probe.py (selftest 9/9; 45s jacket + 2.5s rate-limit + getattr guards + ASCII-source "
             "u-escape law) + evidence results/northbound_probe.json + survey research/shortline/NORTHBOUND_DATA_REACHABILITY.md; "
             "value-liveness lesson direct-written pit-data.md (+1105B, main CODELY.md over-cap 31,001B = bm-a append debt, "
             "direct-write exception r666); explore queue E3 done 10->9 (E4 head); r946 paste-artifact stray E2 row healed; "
             "tech queue 0 remaining (bm-a r946 evidence-verified closure T15/T16, r822 'T15 awaiting GM flag' note now stale); "
             "S6 37 legs rc0 (ZERO-DRIFT streak 8; Saturday no-new-bar quad legitimately skipped)")
s["last_round_at"] = ts; s["ts"] = ts; s["updated"] = ts; s["last_seen"] = ts
s["round_no_label"] = "r823"; s["clock_read"] = ts
s["last_round_ts"] = ts
s["next"] = ("P3 explore E4 head (central-bank OMO liquidity indicator face: OMO net injection -> REPO rate linkage, "
             "REPO_PANEL consumer; check same-day new CEO orders before claiming); waiting: W17-JUDGE drain (bm-c lane, "
             "jman training ETA ~22:45) / Monday 10-12 09:15 minute_feed first gated run backfills 10-08/10-09 / "
             "CODELY.md main-file hot-cold mini-split debt (31,001B>30,720B, next append window)")
s["did"] = s["note"]
s["verdict"] = ("r823: E3 northbound negative closure (probe+evidence+survey piece; 6/12 reachable, flow columns dead "
                "since 2024-08-16, minute face all-0 placeholder trap, per-stock frozen 2024-08-16; revival gated on "
                "disclosure-restoration / 2-source-channel / new-CEO-order, all + GM ticket + T-67 s2); compute_audit flags "
                "supply_gap+ignition_sla on W17 family = bm-c lane-pinned (machine-local checkpoints r429 + lane_owner bm-c + "
                "owner_since 07:02:07 today + bm-c mid CEO-order jman training burn) -> bm-b zero-touch honest attribution; "
                "smoke 49/49; S6 37 legs rc0 (ZERO-DRIFT streak 8; Saturday quad skipped); watermark red=false healthy; "
                "orders both sweeps zero unacked (60/184); ORD/DEC hash MATCH both keys; attrition CLEAN; orphans=0")
s["current_task"] = ("P3 explore E4 head after E3 done; waiting: W17-JUDGE drain (bm-c lane) / Monday 10-12 09:15 "
                     "minute_feed gated backfill / CODELY.md over-cap mini-split debt next append window")
s["task"] = s["current_task"]
s["now_active"] = "r823: P3-E3 northbound negative closure (scripts/northbound_probe.py + evidence + survey piece)"
s["latest_artifact"] = ("r823: scripts/northbound_probe.py (selftest 9/9) + results/northbound_probe.json + "
                       "research/shortline/NORTHBOUND_DATA_REACHABILITY.md, 2026-10-10 08:1x")
s["next_milestone"] = ("r824+: P3 explore E4 head (central-bank OMO liquidity indicator face, survey-first, <=48h) / "
                       "Monday 2026-10-12 09:15 minute_feed first gated run backfills 10-08/10-09 / W18 wave drafting "
                       "once W17-JUDGE drains")
with io.open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
json.loads(io.open("state.json", encoding="utf-8").read())  # self-verify

# --- heartbeat fleet/machines/bm-b.json ---
h = json.load(io.open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = ts; h["heartbeat_epoch_utc"] = epoch; h["clock_read"] = ts
h["ts"] = ts; h["updated"] = ts; h["last_round_at"] = ts
h["round_no"] = 823; h["round"] = 823
h["idle_rounds"] = 0; h["agenda_starved"] = False
h["orphan_faces"] = 0
h["orphan_face_note"] = "probe 11 py faces 0 orphans (r823)"
ram = sample_ram_gb(); gpu = sample_gpu_mb()
if ram: h["free_ram_gb"] = ram
if gpu:
    h["gpu_free_vram_mb"] = gpu; h["gpu_free_vram_gb"] = round(gpu / 1024.0, 1)
try:
    import psutil
    h["cpu_cores"] = psutil.cpu_count(logical=True)
except Exception:
    pass
h["last_action"] = ("r823: P3-E3 northbound data-source reachability scan NEGATIVE closure (probe selftest 9/9 + evidence "
                    "JSON + survey piece; disclosure cliff 2024-08-16 empirically nailed; minute face all-0 placeholder trap "
                    "on record; value-liveness lesson -> pit-data.md) + explore queue E3 done 10->9 + S6 37 legs rc0 + "
                    "S7 quartet green + attrition CLEAN")
h["now_active"] = s["now_active"]; h["latest_artifact"] = s["latest_artifact"]
h["next_milestone"] = s["next_milestone"]; h["verdict"] = s["verdict"]
h["current_task"] = s["current_task"]; h["task"] = s["current_task"]
with io.open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
d = json.loads(io.open("fleet/machines/bm-b.json", encoding="utf-8").read())
assert isinstance(d["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert len(d.get("orders_ack", [])) == 184, "orders_ack big-list must be preserved untouched (r818 law)"

# --- round ledger row ---
row = (ts + " | r823 bm-b | dept:研究（P3-E3 北向资金数据源可达性扫描·判负收口·调研先行合法落地） | "
 "WM-VERDICT: 绿：red=false·lane healthy；py_watermark probe verdict=py_low_board_clear=合法闲白面（板全闭环+bandit 0+可跑批 0 全空）；"
 "compute_audit flags=supply_gap+ignition_sla（W17 分片 5-7+JUDGE=lane bm-c 结构性钉死〔lane_owner=bm-c+机本 checkpoint r429+screen-finalize 读本机 CKPT_DIR〕"
 "+owner_since 今日 07:02:07 活跃+bm-c 在烧 CEO 令 jman 训练〔PID 53412·ETA ~22:45〕→本机零触碰如实披露非本机违例） | "
 "孤儿面=0（probe 11 py faces 0 orphans） | "
 "①S0-1 锚定 bm-b（machine.json 首读）；轮首脏=own daemon 活面 8 件→定向快照 commit（own lane·take-worktree-live）→pull --rebase 1/1 干净零 UU"
 "（incoming=bm-a r946/947 pre 吸收面·文件集零重叠实测）"
 "②S0.5 双扫=orders 60 件/184 acks unacked=[] CLEAN（正典 orders_ack_scan.py 轮首+S7 双跑）+D-19 正典探针 DEC a3ea37bd/ORD e286f842 双 MATCH=零新决策零新待办"
 "③S1 smoke 49/49"
 "④S2 job_list 0+fleet 票 open=0+tech 队列=0（bm-a r946 证据核验收口 T15/T16·r822 state 注记「T15 待 GM 旗」已陈旧如实更正）"
 "⑤P0 产品=**P3-E3 北向资金数据源可达性扫描→判负收口**：探针 scripts/northbound_probe.py（45s 超时夹克+2.5s 限速+getattr 守卫+ASCII 源码 \\u 转义律+selftest 9/9·"
 "selftest L9 v[:4]==\"20\" 字面量坑当场自纠零出户）+证据 results/northbound_probe.json+判读件 research/shortline/NORTHBOUND_DATA_REACHABILITY.md；"
 "实测=akshare 1.18.96 十二面**可达 6/12**，核心资金流字段（当日成交净买额/买入/卖出/历史累计净买额）自 **2024-08-16** 起三面一致 100% NaN"
 "〔disclosure 断崖实证·候选锚 2024-08-19 仅切窗·实测 last_nonnull 为准〕·分钟面 241 行**全 0.0 占位陷阱**〔端点活≠数据活〕"
 "·summary 面北向行 0.0 占位与南向行真值同包混排〔逐行方向归属〕·个股持股面（600519）冻结 2024-08-16〔跨日即冻结律〕"
 "·稀疏例外日（北向/深 2026-04-08·沪 2024-09-27）在册禁作恢复信号·残余活面（领涨股/指数收盘/宽度字段）单源集中 EM+「北向持股」归因不可核〔持股集冻结 2+ 年〕"
 "→**判负：现行披露制度下北向情绪因子生产车道不可立·T-67 §2 前向 12 个月窗永不可达〔E2 期权同构判负〕**；零 prereg 零回测零引擎零面板写；"
 "复活门=披露恢复/两源新渠道/CEO 新令三选一+GM 署名票+T-67 §2 前向窗；explore.md E3→done+消耗记录行（P3 队列 10→9·E4 队头）+顺手治愈 r946 粘贴残留 E2 幽灵行；"
 "**值活性腿坑律直写 pit-data.md**（+1105B·md5 db915a015edc97a5bf06802a7a7d3c15·增量行机械对账；主件 CODELY.md 当窗 31,001B>30,720B 越帽=bm-a r946/947 增量推越"
 "非本轮 append 所致→直写例外 r666 范式·主件热冷整编债=下一 append 窗承做）"
 "⑥S6 37 腿全 rc0（dualrun ZERO-DRIFT streak 8·排 compute_audit 前〔T-116 s3 顺序律〕；周六无新 bar 四连 quad"
 "〔live.paper/t35_open_fill_verify/t24_prospect_paper/t24_prospect_promotion〕合法跳过；scorecard/paper_export/daily_scorecard/dashboard_status 守卫跳过"
 "=bm-a origin commit 14min 新鲜〔r701 third-signal veto〕健康让路面；thermo 全史重建+DUALARM-2026-09-30 再生〔指数臂 BEAR@09-30/情绪臂@09-22 asof 如实披露〕"
 "+REPORT/LIVE-2026-10-10 ORANGE cap50 COOL 再生落 CEO 面；token delta=0）"
 "⑦S7 四件套绿（loop no-op pin=2 首发即 08:12+watchdog present+双爪 OK）+attrition 4 台账 CLEAN（历史 shrink 588d4c160 [healed] 注记照录）"
 "+idle_trigger --worked（idle_rounds 0·agenda_starved false） | "
 "等待态一行声明：W17-JUDGE drain=bm-c 道在跑（jman 训练 ETA ~22:45）→W18 起草窗；周一 10-12 09:15 minute_feed 首 gated 轮回补 10-08/10-09；"
 "CODELY.md 主件越帽整编债=下一 append 窗 | "
 "验证证据: smoke 49/49+northbound_probe selftest 9/9+live probe 证据件 results/northbound_probe.json+S6 37 legs rc0 逐腿 exit 码核账"
 "+dualrun ZERO-DRIFT streak 8+attrition CLEAN+双扫零未回执+心跳 epoch int 自证（" + str(epoch) + "） | "
 "记分: 2（E3=能跑〔探针+selftest〕能看〔证据 JSON+判读件〕能用〔explore 队列消费+判负类处置正典先例〕实物） | "
 "记账预算: 5/5（state+心跳+轮报+explore 消耗行+pit-data 坑律条·无超标） | "
 "宝藏捕获: 坑律 1 条入 pit-data.md（数据源探针值活性腿·全 0 占位面静默吞流坑）；方法论资产卡零新方法（探针范式=cb_data_probe r821 既有先例复用非新法） | "
 "unacked_orders=0 | 本地未达 origin commit 数：0（commit 后 push+fetch+rev-list 自证） | "
 "下轮指针: r824: ①P3 explore E4 队头（央行 OMO 流动性指标面：OMO 净投放→REPO 利率联动·领队头前先查当日新 O 令面）"
 "②W17-JUDGE drain 观察→W18 起草窗 ③周一 10-12 09:15 minute_feed 首 gated 轮回补 10-08/10-09")
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(row + "\n")
print("closeout written: state=823 epoch=%d ram=%s gpu_mb=%s ledger_row=%dB" %
      (epoch, ram, gpu, len(row.encode("utf-8"))))
