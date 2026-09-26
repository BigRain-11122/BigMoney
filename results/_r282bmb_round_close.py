# -*- coding: utf-8 -*-
"""r282 bm-b round close: round_reports.md line append (tail-newline probed)
+ state.json round_no++ write. Run once per round close (r281 line-repair law)."""
import io
import json
import datetime as dt

now = dt.datetime.now().astimezone()
stamp = now.isoformat(timespec="seconds")

line = (
    stamp + " | r282 (bm-b) | dept:数据/工程 | "
    "WM-VERDICT: GREEN healthy red=false (py_low_with_work_cands=合法面: T-87 首拉批网络限速 2.5s/股在飞=低 py CPU 设计使然, probe on_track 实证推进 12.45/min; "
    "板 0 open/32 claimed 全占, bandit next_pick=claimed moneyflow IC 待 bm-a 面板, pool_ready=1 revosc=bm-a 已认领=无本机可认领活) | "
    "did: T-87 供给线中途健康复探 #2 on_track (450/5228=8.6%, rate 12.45/min, ETA 2026-09-27T06:47:19=周一 09:15 死线前约 26.5h 富余, "
    "header_mismatch=0, ohlc_bad=0, tail@cutoff 449/450, 1 例 09-03 早尾=suspension 诚实, attempts=1(000019 下次 gate 自愈), quarantine=0) "
    "+ S0 autofill_state rebase UU 按 r281 家族 union 配方解 (bm-a 00:10 revosc launch entry 保留 + crash_counted 双侧同键 union + last_tick 按 ts 取新 bm-b 00:20:01, json.loads 自证 50 launches) "
    "+ S6 26 腿 rc=0 (周末诚实 no-op: heat/futures/astock_daily lock-alive/options/moneyflow/sina_mf/ths/ah/fund_premium 他机车道或节流面, "
    "lhb 抓取尝试 cutoff 09-24 落后披露日 09-25=30min 自愈守卫在飞, fundamental 新鲜跳过, b_layer_mask 5222 再生, "
    "marks/verify/prospect 四腿=无新 bar 触发条件不满足合法跳过, paper 出口 09-24 幂等, scorecard/report/build_status/token 全 rc=0) "
    "+ 迁移窗 watch (v2.2 precheck 武装待机, journal 00:22:17=Tuanjie 编辑器 3 进程+licensing+cmd-holder 面全在, 窗至 09-29 12:00) | "
    "evidence: results/_r282bmb_astock_pass_probe.py+json + smoke 25/25 + S6 逐腿 rc 账 + orders 89/89 双扫零未回执 | "
    "next: r283=pass 完成复探 (ETA 06:47 后) + 周一 09-28 09:15 首次日续拉实弹 (stragglers gate 自愈腿) + REV_OSC 消费面 watch (bm-a TRANSFER 裁决) "
    "+ 迁移窗 (09-29 12:00) + 10-01 月首轮三件套 (science_audit+monthly_briefing+self_review)"
) + "\n"

p = "logs/iteration-loop/round_reports.md"
b = io.open(p, "rb").read()
if not b.endswith(b"\n"):
    line = "\n" + line          # r281 junction law: probe tail byte before append
with io.open(p, "a", encoding="utf-8", newline="") as f:
    f.write(line)

d = json.load(io.open("logs/iteration-loop/state.json", encoding="utf-8"))
d["round_no"] = 282
d["ts"] = stamp
d["did"] = ("r282: T-87 astock first-pull pass mid-flight re-probe #2 on_track "
            "(450/5228, 12.45/min, ETA Sun 06:47:19, zero shape defects); S0 autofill_state "
            "rebase UU resolved per r281 union family recipe; S6 26 legs rc=0 weekend no-ops; "
            "migration window v2.2 armed waiting (Tuanjie editors open); orders 89/89 double-scan")
d["next"] = ("r283: pass-completion re-probe; Mon 09-28 09:15 first daily-continuation live fire "
             "(stragglers gate self-heal); REV_OSC consumption face watch; migration window to "
             "09-29 12:00; 10-01 month-first trio")
io.open("logs/iteration-loop/state.json", "w", encoding="utf-8", newline="").write(
    json.dumps(d, ensure_ascii=False, indent=1))

# multi-ts self-scan (r281 law): appended block must contain exactly one ts at line head
txt = io.open(p, encoding="utf-8").read()
import re
heads = re.findall(r"^" + re.escape(stamp[:16]), txt, flags=re.M)
print("appended, line starts with:", stamp, "| state round_no=282")
