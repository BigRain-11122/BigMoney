"""R299 bm-a wrap: state + heartbeat + round report + CODELY kenglu line.

Laws applied: r302/F7 heartbeat face (astimezone ISO with T separator,
epoch_utc as JSON int, write-then-self-verify), R291 live-read asserts on
shared state, memory four-question gate (single kenglu line with pointer).
"""
import json
import os
import time
from datetime import datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

# ---------- state-bm-a.json (round_no 298 -> 299)
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8"))
assert st["round_no"] == 298, f"unexpected round_no {st['round_no']}"
now_local = datetime.now().astimezone()
now_iso = now_local.isoformat(timespec="seconds")
now_flat = now_iso.replace("T", " ")
st["round_no"] = 299
st["did"] = ("R299: CN_SECTOR_LEADER_P1 prereg FROZEN (T-87 s2 queue #4 sector-leader "
             "non-limit-up face, commit b3d72924 pushed) -- sector taxonomy source hunt: "
             "legulegu cons anti-bot dead / EM dead r280 / THS cons API absent -> SW OFFICIAL "
             "2021 classification workbook landed (sha256 1111bceb, L2=131 point-in-time "
             "131 sectors, 100% bars coverage, TLS verify=False disclosed); universe 3106 "
             "KLINE-identical; trigger census 17823 events / 7026 days / <=3 per day / "
             "limit-face excluded 2562 (EF W20/K3/MIN5/TOL0.002 frozen); 4 judged cells "
             "FIX10/FIX20/SECT10/STOP10 N_eff 2004 + Sobol 500 sec2.2 descriptive + K=2000 "
             "own nulls seed cn_sector_leader_p1=20277200 registered same-commit (R250 "
             "one-step); cache-vs-bars crosscheck 0 mismatch; wild_route stale gate-stamp "
             "disclosed; S6 30/30 rc=0; smoke 25/25; orders 91/91 zero unacked")
st["verdict"] = "ok"
st["next"] = ("R300: runner scripts/cn_sector_leader_p1.py build per R99 order "
              "(prereg frozen b3d72924 -> runner before any run -> pool submit ready; "
              "B7b contract leg mandatory per r297 kenglu)")
st["ts"] = now_flat
st["last_round_ts"] = "2026-09-27 06:03:00"
st["updated_at"] = now_flat
st["current_task"] = st["did"][:100]
st["last_run"] = now_flat
st["last_seen"] = now_flat
st["task"] = st["next"]
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- heartbeat fleet/machines/bm-a.json
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
assert h.get("round_no") in (298, 299)
epoch = int(time.time())
h["last_seen"] = now_flat
h["round_no"] = 299
h["current_task"] = ("R299 done: CN_SECTOR_LEADER_P1 prereg frozen b3d72924 (queue #4 "
                     "sector-leader); runner build next round per R99")
h["task"] = h["current_task"]
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["verdict"] = ("healthy: supply line delivered (#4 prereg frozen+pushed same round per R99 "
                "freeze-first); pool 0 ready / board 0 open / bandit 0 = py_low_board_clear "
                "legal with supply acted; wild_route_lab stale cache gate-stamp disclosed "
                "(judged-closed runner, zero live impact)")
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# self-verify (R170/R178/R262 law)
chk = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and ("+08:00" in chk["clock_read"] or "Z" in chk["clock_read"]), \
    "clock_read must be ISO8601 with offset"
print("heartbeat verified: epoch int", chk["heartbeat_epoch_utc"], "clock", chk["clock_read"])

# ---------- round report line
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
line = (
    f"{now_flat} | R299 bm-a (dept:研究·策略·舰队) | "
    "WM first-line verdict: py_low_board_clear LEGAL (pool 0 ready / board 0 open / bandit 0; "
    "supply line ACTED same round: queue #4 prereg frozen+pushed b3d72924 -- O-2320 quench "
    "supply law; next_pick advisory=claimed moneyflow-IC-when-panel-completes, not this lane) | "
    "S0 pull clean (bm-b r304 fast-forward) + S0.5 orders double-scan 91/91 zero unacked + "
    "group decisions new lines D-20260927-04 (BigMoney 复审钩子法条化: 本司自纠已收口=R256/bm-b r264, "
    "集团周轮立法归 HQ, 本司零新执行面) / D-20260927-05 (②全文件令扫=本司既有实践 ③冲突标记钩子=R294 已采纳) "
    "-- 本仓例回执, 集团台账收取面禁写 | S1 smoke 25/25 | S3 MAIN: CN_SECTOR_LEADER_P1 prereg FREEZE "
    "(T-87 s2 queue #4 板块龙头非涨停面, R99 freeze-first): (1) 板块谱系源三源死活实证 legulegu cons "
    "anti-bot dead (conn-fuse ValueError 'No tables found' 手工单发成功/连发失败=服务端节流, 退避拉长仍死) / "
    "EM dead (r280 判例复证) / THS cons API 本版 akshare 无 -> SW OFFICIAL 2021 分类簿直下 "
    "sw_stock_classify_2021.xls (swsresearch.com TLS 服务端链不全 verify=False 披露=公开静态研究件, "
    "sha256 1111bceb... meta 留痕 _r299bma_sw_clf_meta.json): 12925 行/5930 股/553 行业码/bars 覆盖 100%, "
    "粒度 L2=industry_code[:4] 131 板块 (中位 25 员, 124 板块>=5 员), point-in-time 生效日史 (3914 股改类, "
    "2021 标准回溯适配三面诚实披露), 层级事实件 _r299bma_sw_hierarchy.json; (2) 宇宙 KLINE 同式机械再derive=3106 "
    "(skip 1705/163/5/243 零漂移); (3) 触发 census 17823 事件/7026 日/峰 3 每日 (K_TOP 构造帽)/1994-2026 逐年 "
    "380-630 均匀/distinct leaders 1545/涨停面剔除 2562 如实计 (cn_sector_leader_probe.json 26.0s, EF 参数 "
    "W20/K_TOP3/MIN_SECT5/LIMIT_EXCL_TOL0.002+板型阈 WILD-S1 冻结面); (4) cache-vs-bars 交叉验证 PASS "
    "(_r299bma_cache_crosscheck.json: 4 样本股有限掩码 0 失配, 值偏差 <=1.1e-4=float32 精度面, 末端 2026-09-22) "
    "-- 附带发现: wild_route_lab.py L117 cache 门断言 '2026-09-24 03:42:50' vs 实际 meta '2026-09-23 18:12:59' "
    "=judged-closed runner 潜伏门错值 (WILD-S1 若重载会炸, 判负族不重开零现役影响, 留档不改); (5) prereg "
    "CN_SECTOR_LEADER_PREREG.md 起草冻结: 4 judged cells LDR-FIX10/FIX20/SECT10/STOP10 (N_eff 2004) + x1 披露列 "
    "+ K=2000 own nulls (RANDOM_LARGE_SAMPLE_LAW §3, 双法 block bootstrap+sign-flip) + §2.1 全史虚拟起点 census "
    "+ §2.3 随机分窗 >=100+WF5 + §2.2 Sobol 500 描述腿 (seed-sequence [20277200,2000]); seed cn_sector_leader_p1="
    "20277200 band 20277200..20279200 (kline 带顶 20277100 之上构造性零碰撞, rg 全档扫描零命中 06:3x) "
    "scripts/science_gates.py 同 commit 登记 (R250 一步律) | F-04 MSG-20260927-0645-bm-a 先行 | "
    "git: freeze commit b3d72924 -> push rc=0 clean (marker gate CLEAN, 73 files) | "
    "S6 30/30 rc=0 (compute_audit v2.3 CLEAN zero-flag, WM probe, update_daily/market_regime/"
    "strategy_scorecard/market_clock CALL-2026-09-24, gates all no-op legal (weekend/cutoff), live.paper OK, "
    "t35v PASS zero-pending, t24 22/22 drift 0, promo 0/22, aggr idempotent, daily_report faces=4 token=1, "
    "build_status, token_meter) | post_review scan zero verdict-X | schtasks IterationLoop Running + "
    "Watchdog Ready (R49 CSV caliber) | inbox zero unread-to-me | state 299, heartbeat epoch int verified"
    " | 下轮指针: R300 runner build + pool submit per R99\n"
)
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line)
print("round report appended", len(line), "chars")

# ---------- CODELY.md kenglu (four-question gate: one lesson, pointer, <1.5KB)
cp = os.path.join(ROOT, "CODELY.md")
cur = open(cp, encoding="utf-8").read()
kenglu = (
    "- [2026-09-27 06:5x r299 bm-a] 坑律：**冻结血统 runner 的 cache 门戳必须与资产 meta 实值对账**——"
    "wild_route_lab.py L117 断言 generated=='2026-09-24 03:42:50' 而实际 meta='2026-09-23 18:12:59'（judged-closed "
    "runner 潜伏炸；WILD-S1 烧批年代门戳或与备份恢复史相关未定谳）；新批消费共享对齐面板时=自带交叉验证门"
    "（样本股有限掩码 0 失配+值偏差=float32 精度面+末端=cutoff）而非继承旧门字符串。指针="
    "results/_r299bma_cache_crosscheck.json+research/CN_SECTOR_LEADER_PREREG.md §2。\n"
)
assert os.path.getsize(cp) + len(kenglu.encode("utf-8")) < 10240, "CODELY 10KB hard line"
anchor = "### Project\n"
assert anchor in cur
open(cp, "w", encoding="utf-8").write(
    cur.replace(anchor, anchor + kenglu, 1))
print("CODELY.md kenglu appended, new size:",
      os.path.getsize(cp), "bytes (<=10KB line held)")
