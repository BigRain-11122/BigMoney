"""r947 bm-a closeout: state increment, heartbeat, round-report append."""
import datetime as dt
import io
import json
import time

now = dt.datetime.now()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- state file: round_no 946 -> 947
p = "state-bm-a.json"
s = json.load(io.open(p, encoding="utf-8"))
assert s["round_no"] == 946, s["round_no"]
s["round_no"] = 947
s["last_round_ts"] = ts
io.open(p, "w", encoding="utf-8", newline="").write(
    json.dumps(s, ensure_ascii=False, indent=1))

# --- heartbeat
hp = "fleet/machines/bm-a.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = ts
h["current_task"] = "E3 北向源扫描判负关闭收口完成；W205 守窗（待 bm-c W204 首烧）；THS/AH/moneyflow 分离刷新在途"
h["cpu_cores"] = 32
h["idle_ram_gb"] = round(59.8, 1)
h["gpu_idle_vram_mb"] = 8796
h["verdict"] = "GREEN-IDLE worked-clear (E3 实物产出轮)"
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = ts
h["ts"] = ts
io.open(hp, "w", encoding="utf-8", newline="").write(
    json.dumps(h, ensure_ascii=False, indent=1))
# post-write self-check: epoch must be JSON int
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(chk["heartbeat_epoch_utc"])
assert "T" in chk["clock_read"], chk["clock_read"]

# --- round report
line = (
    "2026-10-10T09:0x+08:00 | r947 | bm-a | dept:研究/数据 "
    "(E3 北向资金源可达性扫描判负关闭 + r947 死会话遗产收口 + S6 全链) | "
    "WM-VERDICT: red=false lane healthy; DEC/ORD 正典探针双 MATCH 零消费（S0.5 双扫 0 未回执） | "
    "S1 smoke 49/49 | S2 idle two_read_red 入轮 → 本轮实物产出工 --worked 清零（idle_rounds 2→0） | "
    "S3: ①r947 死会话遗产吸收=pre commit 9fccb2984（E5 slice-2 判决回填 §7/§8 0/12 全链+results/lhb_thermo_ic_p1 三件+CODELY 记忆整编+runtime faces take-worktree-live）"
    "+S0 rebase 6 UU 全 ALL_FACES 族 merge_lane_views resolve（compute_audit/futures/lhb/regime_state/runnable_pool/update_status）+reconcile 全零漂+push d2244da4b 送达自证 0/0 "
    "②E3 P3 队头出列=scripts/hsgt_source_probe.py（selftest 7/7·6 接口 8 请求·3s 节流直连）+results/shortline/hsgt_source_probe.json+results/_e3_hsgt_introspect.json"
    "+判词件 research/digests/DIGEST-20261010-e3-hsgt-source-probe.md——主候选（北向日度流量情绪因子）判负关闭：post-2024-08-16 政策死亡实证三面"
    "（hist 501 行流量列 alive 0/501 全 NaN+min 面 241 行 0.0 零填僵尸+summary 同端点南向对照：北向 0 vs 南向 -23.31/+26.22 亿真值=零填系政策面非源损坏）；"
    "季度持股快照 8 点存活（2024-09-30..2026-06-30 季度末 2.41→3.10 万亿）+南向旁系日度真值=登记不开发；hold_stock/individual_detail/stock_statistics wrapper 全破=数据债登记；"
    "R58 承接修正（可达≠可用量纲判读）；零判据零账本零引擎 "
    "③S6 39 腿全 rc0：pool_dualrun 零漂移 streak5→compute_audit FLAG supply_gap+ignition_sla（W204 门 bm-c 席+W17 SHARD-5/6/7/JUDGE 未烧=bm-c lane 依赖如实）"
    "+py_watermark py_low_board_clear 合法白名单（板闭环+池 lane-pinned）+采集批全合法 no-op（周六·面板尾 2026-10-09）+options RETIRED 面+moneyflow/THS/AH 三分离刷新 spawn 在途"
    "+paper/报告/面板/token 全落地（system_v1 cutoff 10-09 marks5 entries10·LIVE-2026-10-10 ORANGE cap50%·REPORT-2026-10-10） "
    "④S7: attrition guard 4 台账 CLEAN（1 healed 历史缩行注记照录）+双爪字节等+loop pin=8 no-op+watchdog -Force 重注册+inbox 1 件处理（MSG-0830 r947 在制声明→批已终态回执移 processed） "
    "| 当前活: E3 判负关闭收口完成·W205 守窗 | "
    "最近实物: scripts/hsgt_source_probe.py+results/shortline/hsgt_source_probe.json+research/digests/DIGEST-20261010-e3-hsgt-source-probe.md（09:0x·commit 本轮）+r947 遗产 push d2244da4b | "
    "下个里程碑: bm-c W204 首烧→bm-a W205 席位（守窗纪律·不越权）；THS/AH/moneyflow 分离刷新落地面回查（下轮）；10-31 月界首考（T-143 装配 10-29） "
    "| verification: smoke 49/49+S6 39 腿 rc0+attrition CLEAN+push 自证 0/0+heartbeat epoch int 自证+T 分隔钟 "
    "| scoring: 2（能跑探针+可看判决 JSON/CSV/判词件+队列消耗闭环） "
    "| bookkeeping: 5/5（state 946→947+轮报行+心跳+idle_trigger --worked+inbox 回执） "
    "| treasure-capture: 零 append 如实（探针=R58 血统复用·判负结论入正典 digest 承载） "
    "| orphan_face=1（ComfyUI 8188 PID71284 三面孤儿·MV 车道豁免只读未杀） "
    "| unacked_orders=0（S0.5+S7 双扫） | 本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） "
    "| token: L1 零 API（今日 0 本地 LLM 腿/14 total 面） | [r947 bm-a]"
)
rp = "round_reports-bm-a.md"
txt = io.open(rp, encoding="utf-8", newline="").read()
if not txt.endswith("\n"):
    txt += "\n"
txt += line + "\n"
io.open(rp, "w", encoding="utf-8", newline="").write(txt)
print("state 947 written; heartbeat updated (epoch int OK); round report appended", len(line), "chars")
