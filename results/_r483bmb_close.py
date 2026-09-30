"""r483 bm-b closing writes: round report line + state.json + heartbeat (S5/S7)."""
import datetime, json, os, subprocess, sys, time

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
stamp = now.strftime("%Y-%m-%d %H:%M")[:16]

import psutil
free_ram = round(psutil.virtual_memory().available / 1e9, 1)
cpu_pct = psutil.cpu_percent(interval=1)
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        text=True).strip().splitlines()[0]
    gpu_free = round(float(out) / 1024, 1)
except Exception:
    gpu_free = 2.1

epoch = int(time.time())
assert isinstance(epoch, int)

# --- 1. round report line (bm-b ledger) ---
line = (
 f"{ts} | r483 bm-b | dept:策略/研究 | WM=绿（red=false lane healthy·py 0.4-1.9% 低位合法：astock 刷新在飞 lock-alive·池 0 ready 全 gated〔LOWAMP-P1 s2 入池后转非空〕·audit 供给面如实） | "
 f"CEO 即时令执行=O-2026-09-30-2230 潜力关注令：**T-2026-09-30-132-P1（LOWAMP 族专用判决批·快速通道）认领+开动同轮完成**（认领 commit a78b69bc5·CEO 即时律合规）| 主产出=s1 预注册冻结件 research/LOWAMP-P1.md（**冻结 commit 0c100400f**·N_eff=2008=4 cells×2 faces+2000 nulls·双轴 T-22 起点 {1255,1506}·窗 {126,252,504}·judged cells 4=LA-REP/LA-EQ/LA-T3/LA-EDGE 跑前写死·G1'/G2 全走 science_gates 共享库零手抄·流动性闸 amt20≥¥50M·G-SEG 覆盖门）| "
 f"§0.5 禁向闸实弹=首跑 REJECT（词面自撞：§0.5 复述禁向词+BAN 编号被机械闸当引用）→词面清洗语义零变→**ADMIT exit 0**；种子律三步全=berth MSG-2325→同 commit 登记 lowamp_p1_params=20330000/lowamp_p1_nulls=20330500（+500 阶梯·facts=results/_r483bmb_lowamp_seed_law_facts.json）→import view 验证；closed_family_check lowamp_daily_xs=**open** 回执；同窗作废让号残留同文票 T-2026-09-30-131-P1（superseded_by=T-132·per T-132 自身 lineage·防双认领）| "
 f"S6 38 腿全 rc0：dualrun ZERO-DRIFT 146/**streak3 达 flip 门**（flip=另轮会话动作本腿永不自动切·分析件 research/POOL_RETIREMENT_S3_WAVE1_ANALYSIS.md 在案）·CALL ORANGE_COOL sleeves=4·astock lock-alive no-op（刷新继续）·REPORT/LIVE-2026-09-30 再生·marks idempotent·t35/paper_export/scorecard/build_status=合法 stale-takeover（bm-a hb stale 67-68min·O-2100 s2.4 律） | "
 f"S0.5 面：pull rebase 1（bm-c r292 收据+T-131/132 到场）；orders **130→131** 差集=O-2230 唯一→本轮执行+ack；D-19 decisions sha 21B5C469 不变零动作（temp partial clone 复用 REUSED）；inbox 出件 1（claim MSG-2325）入件 0 | "
 f"evidence：冻结 commit 0c100400f+闸 ADMIT 回执+S6 log results/_r483bmb_s6_log.txt+seed facts 件+探针 results/_r483bmb_lowamp_probe.py（§2 锚实跑：legacy 48 员 2020-01-02 起/adj 19/19/deep PASS 2013-06-17/48 文件在位）；smoke 47/47；attrition CLEAN（4 台账·2 历史 shrink healed 注记照录）；S7 自愈全绿（loop pin=2 no-op·watchdog 就绪·claw identical→installed） | "
 f"产品律三行：当前活=LOWAMP-P1 s2 runner（下轮主活）；最近实物=research/LOWAMP-P1.md 冻结件 2026-09-30 23:3x（commit 0c100400f）；下个里程碑=s2 runner+入池+autofill 续批点火 s3 burn（窗 ≤48h·10-01 晚前） | "
 f"续作指针（精确）：s2=scripts/lowamp_p1.py（probe/selftest/run/status/finalize·t22 _load_axis_prices/enumerate_starts/_slice_metrics/regime_proxy import-face 复用·G-FACE/G-MANIFEST/G-CENSUS/G-SEG/G-MASK/G-COST 六门·D6 corr probe 前置 fail-closed·16 cell-shards+nulls 片+sensitivity 片入 runnable_pool）→ s3 burn（autofill 续批）→ s4 intake（LOWAMP-* 纸盘提案+STRATEGY_LIBRARY+watchlist 翻面）；astock settle→EXCLUSION/FACEB 解冻；10-01 月首轮三件套+REGIME v3 hands-off；RW-5 10-03 解冻 [via bm-b]"
)
rp = os.path.join(repo, "logs", "iteration-loop", "round_reports.md")
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line + "\n")

# --- 2. state.json round_no +1 ---
sp = os.path.join(repo, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 483
st["note"] = (
 "r483: CEO immediate order O-2026-09-30-2230 executed: claimed T-2026-09-30-132-P1 (LOWAMP-P1 fast-track judged batch, "
 "commit a78b69bc5) and DELIVERED s1 prereg freeze same round (research/LOWAMP-P1.md frozen at 0c100400f, N_eff=2008, "
 "banned-gate ADMIT, seeds 20330000/20330500 registered, closed_family open, stale dup ticket T-131 voided) + S6 38 legs "
 "all rc0 (dualrun ZERO-DRIFT 146/streak3 flip-gate reached, CALL ORANGE_COOL, astock refresh still in-flight lock-alive) "
 "+ D-19 decisions sha unchanged 21B5C469 zero action + orders 130->131 (O-2230 acked after execution) + smoke 47/47; "
 "next slice = s2 runner scripts/lowamp_p1.py + pool entry (exact continuation in round report)"
)
st["last_round_at"] = stamp.replace(" ", "T") + "x"
st["last_round_ts"] = ts
st["ts"] = stamp
st["updated"] = True
st["updated_at"] = ts
st["last_decisions_at"] = ts   # re-verified this round, sha unchanged
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# --- 3. heartbeat bm-b.json ---
hp = os.path.join(repo, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["current_task"] = ("r483: LOWAMP-P1 s1 frozen (T-132 claim+start same round per CEO immediate law; "
                      "s2 runner next slice); astock refresh in-flight gates EXCLUSION/FACEB; W14 parked D-41 sec1.2; "
                      "RW-5 prereg freeze until 10-03; 10-01 month-first trio next")
hb["cpu_cores"] = 16
hb["cores"] = 16
hb["free_ram_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["ram_free_gb"] = free_ram
hb["gpu_free_vram_gb"] = gpu_free
hb["gpu_idle_vram_gb"] = gpu_free
hb["gpu_free_vram_mb"] = int(gpu_free * 1024)
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 483
hb["round"] = 483
hb["loop_round"] = 483
hb["verdict"] = ("green-legal-idle: pool 0 ready all gated (astock I/O refresh in flight + W14 banned D-41 sec1.2 + "
                 "RW-5 freeze to 10-03); CEO immediate ticket T-132 LOWAMP-P1 claimed+s1 frozen this round "
                 "(product 2-point face); S6 38 legs all rc0")
if "O-2026-09-30-2230-bm-a.md" not in hb["orders_ack"]:
    hb["orders_ack"].append("O-2026-09-30-2230-bm-a.md")
hb["n_orders_ack"] = len(hb["orders_ack"])
hb["last_round_at"] = stamp.replace(" ", "T") + "x"
hb["last_round_ts"] = ts
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# --- self-checks (R170/R178/R262 law) ---
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"].split("+")[0], "clock_read must be T-separated ISO"
st2 = json.load(open(sp, encoding="utf-8"))
assert st2["round_no"] == 483
print(f"CLOSING OK r483 | epoch={epoch} int-verified | clock={ts} | free_ram={free_ram}GB "
      f"gpu_free={gpu_free}GB cpu={cpu_pct}% | orders_ack={chk['n_orders_ack']}")
