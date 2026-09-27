# r339 bm-b closeout: state.json + heartbeat bm-b.json + round report append, with self-verification
import json, time, datetime, psutil

NOW = datetime.datetime.now().astimezone()
iso = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")
iso = iso[:-2] + ":" + iso[-2:]          # 2026-09-27T18:xx:xx+08:00
spc = NOW.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

cpu_pct = psutil.cpu_percent(interval=0.5)
vm = psutil.virtual_memory()
free_mb = int(vm.available / 1024 / 1024)

# ---- state.json ----
st = {
    "round_no": 339,
    "did": ("S0 collision-resolve mission landed: tick-artifact self-commit -> pull --rebase 1-UU autofill_state -> "
            "3-blob freeze (r335 tick-strike prevention) -> classify mixed-dict+ledger -> theirs launches subset-of-base zero-new + "
            "ours=base+1 (dce2-legacy-lb 09:40:01 bm-b) + last_tick same-second 18:30:01 tie->HEAD=ours (r140 law) -> "
            "union==ours byte-identical -> take-ours whole-byte writeback zero fake churn (r339 law) -> rebase continue -> "
            "push landed 5b32474e..c28b63c7 pre-18:40-tick; S0.5 orders 96/96 zero-diff + group decisions ledger 3-probe absent "
            "(../../docs / MiniGame docs / cph4 subtree) honest no-op r104/r107 precedent + v7 council-seat read-face same-absent "
            "(first opinion F-20260927-02 issued, window to 09-29); smoke 25/25; S2 dual board 0 open (63 done + 30 claimed other-machines); "
            "S3 town.html 10-building org_chart v2/v5/v6/v7 alignment verify PASS (mandate zero drift, no edit needed); "
            "S6 30/30 rc=0 Sunday idempotent family (regime ORANGE shadow asof 09-24 / clock ORANGE_COOL / bm-a 6-lane guards honest no-op / "
            "astock+rev_osc bm-b dual-lane idempotent cutoff 09-24 / t24_promotion 0/22 honest / export+scorecard+report refreshed); "
            "live.paper/t35v/t24_paper three new-bar-gated legs legal skip (weekend, next bar Mon 09-28 15:30); "
            "S4 zero append (no new pitlaw, CODELY line preserved); S7 schtasks both tasks alive + pre-commit claw identical + "
            "r291->r339 misnumber rename trail"),
    "verdict": "green",
    "next": ("W2-A burn harvest watch (finalize -> r312 done-flip pool face + T-86 bm-a receipt), ETA window to 21:40; "
             "Mon 09-28: 09:15 T-91 s3 auto-fire (SIG/BARS replay) + 15:30 T-87 astock first increment + new-bar full chain "
             "(preflight 8/8 green); R340 5x HANDOVER bm-b side; 10-01 monthly trio + REGIME_GUARD v3 date gate"),
    "last_round_ts": iso,
    "last_result": "ok",
    "current_task": "r339 closed: S0 collision resolve landed + Sunday maintenance 30/30 green",
    "updated_at": iso,
    "last_seen": iso,
    "ts": spc,
}
with open("logs/iteration-loop/state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---- heartbeat ----
with open("fleet/machines/bm-b.json", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = 16
hb["cores"] = 16
hb["cpu_util_pct"] = cpu_pct
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = round(free_mb / 1024, 1)
hb["free_ram_mb"] = free_mb
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["idle_ram_mb"] = free_mb
hb["gpu_free_vram_gb"] = 6.9
hb["gpu_free_vram_mb"] = 6904
hb["gpu_idle_vram_mb"] = 6904
hb["gpu_model"] = "NVIDIA GeForce RTX 3070 (1115MiB used @" + iso + ")"
hb["round_no"] = 339
hb["round"] = 339
hb["loop_round"] = 339
hb["verdict"] = "healthy"
hb["n_orders_ack"] = len(hb.get("orders_ack", []))
with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---- round report append (one line, fixed fields) ----
REPORT = "logs/iteration-loop/round_reports.md"
row = (
    iso + " | round 339 bm-b | dept:工程+舰队 | "
    "WM=绿 red=false@18:30:21 lane healthy；probe 18:45 py_low_with_work_cands(py 28.8%)=W2-A census burn 自家 claim 合法占用"
    "(parent 13148 alive·4 workers ~94% 满速·ETA 至 21:40 窗)；RAM 0.6-2.2GB 波动零新重活 | "
    "did: (1) **S0 撞车解主闭环**：tick 尾迹定向收编(autofill_state+p1d_gates 自提交 7fe070c6)->pull --rebase 1-UU autofill_state->"
    "**三面 blob 先冻结**(r335 tick 盲 add 防)->技能分类器 mixed-dict+ledger->定谳=theirs launches ⊆ base 零新 + ours=base+1"
    "(dce2-legacy-lb 09:40:01)+ last_tick 同秒 18:30:01 tie->HEAD=ours(r140 律)->union 结果=ours 字节恒等->**take-ours 整字节写回**"
    "(json.loads 验证后 add·r339 blob 尾态律防伪 churn)->rebase --continue->push 落定 5b32474e..c28b63c7(赶 18:40 tick 前零竞态)；"
    "(2) S0.5 orders 96/96 python 双向差集零未回执 + 集团台账三径探测缺席(../../docs·MiniGame docs·cph4 子树)诚实 no-op"
    "(r104/r107 典)+v7 委员会席位读面同缺席(首件意见 F-20260927-02 已出·窗至 09-29)；(3) S1 smoke 25/25；"
    "(4) S2 双板 0 open(93 票=63 done+30 claimed 他机在飞)+inbox 0；(5) S3 开发队列小活=town.html 十楼对齐 org_chart "
    "v2/v5/v6/v7 部门表**核验 PASS**(mandate 零漂移免改·研究部 v6 KPI 行/总经办 v7 席位行均已上盘·r277 勘注复核)；"
    "(6) S6 30/30 rc=0 周日幂等族：audit CLEAN flags=[]/update_daily 0 新行 cutoff 09-24/regime ORANGE shadow(hs300<MA200)/"
    "clock ORANGE_COOL sleeves=4 幂等/lhb 30min 节流 no-op/heat 周末 no-op/futures 覆盖 no-op/bm-a 六道护栏诚实 no-op(repo·options·"
    "moneyflow·sina_mf·ths·ah)+fund_premium bm-c 道诚实 no-op/astock+rev_osc bm-b 双道幂等 cutoff 09-24/t24_promotion 0/22 如实/"
    "aggr-alloc-grid 纸盘 no-op/system_v1 bm-a 道 no-op/t35_export 再生(6 员·18 持仓·权益 ¥5,996,645)/scorecard 6+28+7 卡/"
    "daily_report faces=4 幂等/b_layer gates all_pass/fundamental 快照新鲜跳过；live.paper+t35_open_fill+t24_prospect_paper "
    "三件 new-bar 条件不满足合法跳计(周末·下一 bar=周一 09-28 15:30)；(7) S4 零 append(无新坑例·CODELY 9956B 线保·四问门 "
    "①③不过)；(8) S7：schtasks 实探双任务在岗(Loop Running 18:50/Watchdog Ready 19:00)+pre-commit 钳 CR 归一 hash 恒等+"
    "轮号误名勘误(_r291bmb_*→_r339bmb_* git mv 留痕·冻结/勘验/解三件+orders_scan) | "
    "验证证据=results/_r339bmb_resolve.py 断言面(union48==|AuB|+字节恒等+last_tick dict)+_r339bmb_s6.log 30x rc=0+smoke 25/25+"
    "_r339bmb_orders_scan.py 双向差集空+push 5b32474e..c28b63c7 reflog 定谳 | "
    "下轮: W2-A finalize 收割窗(->r312 done-flip 池面+T-86 bm-a 票面回执·ETA 至 21:40·count2 OOM 深探)；周一 09-28: 09:15 "
    "T-91 s3 自动点火(SIG/BARS-2026-09-28 重放)+15:30 T-87 astock 首增量 new-bar 全链接力(preflight 8/8 已绿)；"
    "R340 5x HANDOVER bm-b 侧；10-01 月首轮三件套+REGIME_GUARD v3 日期门"
)
with open(REPORT, "a", encoding="utf-8", newline="\n") as f:
    f.write(row + "\n")

# ---- self-verification ----
with open("fleet/machines/bm-b.json", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be T-separated ISO (R262 law)"
with open("logs/iteration-loop/state.json", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 339
assert hb2["round_no"] == 339 and hb2["n_orders_ack"] == 96
with open(REPORT, encoding="utf-8") as f:
    lines = f.readlines()
assert lines[-1].startswith(iso[:16]) or iso[:13] in lines[-1], "report tail must be this round"
print("CLOSEOUT OK | epoch", hb2["heartbeat_epoch_utc"], "| clock", hb2["clock_read"],
      "| cpu%", hb2["cpu_util_pct"], "| freeMB", free_mb, "| report lines", len(lines))
