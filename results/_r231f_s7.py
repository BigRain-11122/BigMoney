# r231 S7 writer: state file, round report line, heartbeat (python UTF-8 direct
# write per r230 GBK law; EOL/indent preserved per R230 indent-drift law).
import io
import json
import subprocess
import time
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone(timedelta(hours=8)))
STAMP = NOW.strftime("%Y-%m-%d %H:%M:%S")
STAMP_COMPACT = NOW.strftime("%Y-%m-%d %H:%M")

# ---- live samples for heartbeat (same faces compute_audit uses) ----
def _ps(cmd):
    return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=30).stdout.strip()

free_ram_gb = round(float(_ps(
    "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)")), 1)
cpu_pct = float(_ps(
    "(Get-CimInstance Win32_Processor | Measure-Object -Property "
    "LoadPercentage -Average).Average"))
vram_free_mb = 0
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=15).stdout.strip()
    vram_free_mb = int(float(out.splitlines()[0]))
except Exception:
    vram_free_mb = 0

epoch = int(time.time())

# ---- state file (bm-b: logs/iteration-loop/state.json) ----
STATE = "logs/iteration-loop/state.json"
state = {
    "round_no": 231,
    "did": (
        "r231: P1E_SYNTH harvest finalize exit 0 = honest FAIL verdict "
        "(V1: primary IS IC 0.0700 < thr 0.0762=max(0.02,nullA_p95,nullB_p95 "
        "0.0019), rank 5/21, V2 0.552/V3 116.6%/A3 8011 all pass = V1 "
        "single-point death, shelf effect, prereg sec.5 pred-7 hit; top pair "
        "terrified+coin_team 0.0822 closed-line observation no adoption) + "
        "chain-fork fix adopted from dead r231 session debris + extended "
        "(ledger_head canonical prev_total: p1e_synth/a158/p1e_ic_batch, "
        "narrow 183292 vs real 184754 fork empirically verified pre-adoption, "
        "t24_g2_pack already canonical) + ledger 184754->184826 (+72) + "
        "gate_attrition auto-booked + prereg sec.7 backfill (7/8 pred hit + 1 "
        "honest not-run) + STRATEGY_LIBRARY Zoo row FAIL disposition + pool "
        "flip P1E-SYNTH done (r224 window: landed 07:47 -> flipped 07:59) + "
        "S0 rebase UU + stash-pop 11-UU resolved per skill classifier "
        "(zero-loss verified) + S6 17 legs green weekend face + smoke 25/25 "
        "+ orders 74/74 double-scan"
    ),
    "verdict": "green",
    "next": (
        "r232: 09-28 Monday new-bar full-chain relay (update_daily -> "
        "live.paper REGIME_GUARD v3 enforce window -> t35verify -> t24 x2 -> "
        "aggr/alloc paper -> export/scorecard); pool now EMPTY (P1E lane "
        "closed) -> board/bandit watch for next prereg candidate (O-1819 "
        "advisory); a158/p1e_ic_batch ledger_head fix rides next finalize "
        "organically; bm-a T-72 sina first-pull acceptance ~08:27-09:05 "
        "their lane"
    ),
    "last_round_ts": STAMP,
    "last_result": "exit 0 all legs (17 run, paper family new-bar-gated "
                   "weekend skip: cutoff 09-24, next bar 09-28)",
    "current_task": "r231 done: P1E_SYNTH harvested (FAIL, single-factor "
                    "usage retained, +72 ledger); next: r232 board watch",
    "last_tick": NOW.strftime("%H:%M"),
    "updated_at": NOW.isoformat(timespec="seconds"),
    "last_seen": NOW.strftime("%Y-%m-%d %H:%M"),
    "ts": NOW.isoformat(timespec="seconds"),
    "last_ts": NOW.strftime("%Y-%m-%d %H:%M"),
    "last_run": NOW.isoformat(timespec="seconds"),
    "last_round_at": NOW.isoformat(timespec="seconds"),
}
body = json.dumps(state, ensure_ascii=False, indent=2)
with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(body + "\n")
json.loads(io.open(STATE, encoding="utf-8").read())
print("state written: round_no", state["round_no"])

# ---- heartbeat (fleet/machines/bm-b.json; single-writer own file) ----
HB = "fleet/machines/bm-b.json"
hb_raw = io.open(HB, "rb").read()
hb_crlf = b"\r\n" in hb_raw[-500:]
hb = json.loads(hb_raw.decode("utf-8"))
hb["last_seen"] = NOW.isoformat(timespec="seconds")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = NOW.isoformat(timespec="seconds")
hb["current_task"] = ("r231 done: P1E_SYNTH harvested honest FAIL (V1 "
                      "0.0700<0.0762 rank 5/21, +72 ledger 184754->184826, "
                      "single-factor usage retained); chain-fork fix "
                      "landed 3 callers; pool empty; next r232 board watch")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = round(vram_free_mb / 1024.0, 1)
hb["gpu_free_vram_mb"] = vram_free_mb
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 231
hb["verdict"] = "healthy"
hb["idle_ram_gb"] = free_ram_gb
hb["idle_ram_mb"] = int(free_ram_gb * 1024)
hb["gpu_idle_vram_mb"] = vram_free_mb
hb_body = json.dumps(hb, ensure_ascii=False, indent=1)
with io.open(HB, "w", encoding="utf-8",
             newline="\r\n" if hb_crlf else "\n") as fh:
    fh.write(hb_body + "\n")
# post-write self-assert (R170/R178 law)
chk = json.loads(io.open(HB, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat written: epoch", chk["heartbeat_epoch_utc"],
      "int-verified; ram_free", free_ram_gb, "GB; cpu", cpu_pct, "%")

# ---- round report (bm-b: logs/iteration-loop/round_reports.md) ----
REP = "logs/iteration-loop/round_reports.md"
rep_raw = io.open(REP, "rb").read()
rep_crlf = b"\r\n" in rep_raw[-2000:]
rep_ends_nl = rep_raw.endswith(b"\n")
entry = (
    f"[{STAMP_COMPACT} | r231 | bm-b OS loop] 水位判定：绿——red=false、"
    "py CPU 尾窗 1.1/0.9/7.3% 低位合法（板全 claimed+池已清空=P1E 车道收线后"
    "合法 idle；probe insufficient_history 单样本窗如实、水位线未越）。"
    "S0：pull --rebase 收 bm-a R230补/R231/R232 三轮（behind 5）→ 23468fd8 "
    "重放 UU autofill_state 按技能解（union 50+50→50 cap50·last_tick 07:50:01 "
    "取新·pid17616 发射记录保全）→ stash-pop 11-UU 批量按分类器零 UNKNOWN 解"
    "（compute_audit history union 201+201→205→newest-200 零丢失·regime_state "
    "union·autofill last_tick 07:50:02 claim_lost_yield theirs·7 快照+dash.js "
    "孪生律 take-ours 整字节·CRLF 镜像）。S0.5：orders 74/74 双扫零差集；"
    "decisions.md 本机不存在（bm-a 面）零动作。S1：smoke 25/25。"
    "S3 主闭环=P1E_SYNTH 收割：死轮 r231 会话残骸收养（r225 三件套判死："
    "07:31 mtime 停摆+零进程+零 commit）=finalize prev 读点链分叉修复"
    "（窄面 _chain_head_total 183292 漏 results/wild_route/ 嵌套目录 vs 真头 "
    "184754·收养前实测复证分叉真实）+同族扫净补齐 a158_truegap_ic 与 "
    "p1e_ic_batch 两 caller（t24_g2_pack 已 canonical 免修）→ selftest 19/19"
    "（含 2 新 inspect 源断言）+两兄弟 selftest PASS+py_compile 三件；"
    "finalize exit 0=诚实 FAIL 判定（V1：primary stv+coin_team IS IC 0.0700 < "
    "0.0762=max(0.02, nullA_p95, nullB_p95 0.0019)·rank 5/21·V2 IR 0.552≥0.30"
    "·V3 留存 116.6%·A3 n=8011 全过=V1 单点死亡·货架效应·§5 预判⑦精确命中；"
    "批池顶部对 terrified+coin_team 0.0822≠primary=封闭线观察禁直接采信）→ "
    "账本 184754→184826（+72·V1 fail +0 条件列·引擎账本零动）·gate_attrition "
    "finalize 自动记账（measurement·delta 72·eliminated 1）·prereg §7 回填"
    "（预测对账 7 对+1 如实记：①锚全过②IC 0.07∈[0.055,0.08]③nullA 0.0762∈"
    "[0.058,0.095]④nullB 0.0019∈[0.0008,0.003]⑤V2 0.552∈[0.5,0.8]绑定=V1"
    "⑥留存 116.6%⑦FAIL 死于 V1 全中⑧分年段未跑如实）+§8 FAIL 分支照执"
    "（联合增益主张收缩·两员维持单因子用法·+2 合成货架不授·xstock 线另开）"
    "·STRATEGY_LIBRARY Zoo 行 FAIL 处置更新·runnable_pool 翻面 P1E-SYNTH "
    "entry+shard→done（r224 窗：07:47 落地→07:59 翻面，下一 tick 前完成零"
    "空转；EOL 字节级保真 CRLF 修复自捕）。S4：CODELY.md +1 坑律行"
    "（链分叉族·33.6KB<50KB 免整编）。S6：17 腿绿周末面（audit CLEAN flags=0"
    "·pool_ready 0=车道收线后清空·daily 0 新行 cutoff 09-24·regime ORANGE d2 "
    "shadow·lhb 30min 节流 no-op·heat/futures 周末 no-op·options/mf/ths/ah "
    "bm-a 车道+fp bm-c 车道 stdout 诚实 no-op·fundamental 10.8h 新鲜跳过·blf "
    "五门全过·scorecard 6 员·build_status 432combos·token delta=+4）；paper "
    "族新 bar 门控周末跳（次 bar 09-28 周一）。S7：inbox 0 pending（3 件 bm-b "
    "F-04 声明 0610/0644/0655 已 processed 07:03:28·三声明全闭环：0610→邻检 "
    "r228 done·0644→prereg r229 冻结·0655→池化 r230）·schtasks 双任务在"
    "（IterationLoop+LoopWatchdog）·orders 尾扫 74/74·state 231·心跳 epoch "
    "python int 自证。下轮指针：09-28 周一新 bar 全链中继（update_daily→"
    "live.paper REGIME_GUARD v3 enforce 窗→t35verify→t24×2→aggr/alloc→"
    "export/scorecard）；池已清空→板/bandit 观察下一 prereg 候选（O-1819 "
    "advisory 队列永不清空）；a158/p1e_ic_batch ledger_head 修复随各自下次 "
    "finalize 自然生效；bm-a T-72 sina 首拉验收窗 ~08:27-09:05（其车道）。"
)
sep = "\r\n" if rep_crlf else "\n"
with io.open(REP, "a", encoding="utf-8", newline="") as fh:
    if not rep_ends_nl:
        fh.write(sep)
    fh.write(entry + sep)
print("round report appended; crlf=", rep_crlf)
