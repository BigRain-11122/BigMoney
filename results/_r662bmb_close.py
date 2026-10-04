# -*- coding: utf-8 -*-
# r662 bm-b S7 closing: state bump + heartbeat + round report append
# laws: r645 state json.dump+loads self-check; R170/R178 epoch int; R262 clock T-sep;
#       r641 round_reports.md bytes-mode append, newline prepend ALWAYS (r661 repair lesson)
import json, io, time, subprocess

now = time.time()
clock = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(now))

# --- 1) state.json round bump ---
sp = "state.json"
s = json.load(io.open(sp, encoding="utf-8"))
old = s["round_no"]
s["round_no"] = old + 1
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(sp, encoding="utf-8"))
assert chk["round_no"] == old + 1, "state bump self-check failed"
print("state round_no:", old, "->", chk["round_no"])

# --- 2) heartbeat bm-b.json ---
hp = "fleet/machines/bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = int(now)
h["clock_read"] = clock
h["round_no"] = chk["round_no"]
h["round_no_label"] = "round %d (bm-b)" % chk["round_no"]
h["current_task"] = ("golden-week watch r%d: FUND trio NULLS canonical burns "
                     "(V693/Q532/D387 of 2000) healthy dual-form; S6 38/38 rc0" % chk["round_no"])
h["verdict"] = "healthy"
h["ts"] = clock
h["updated"] = clock
try:
    m = subprocess.run(["powershell", "-NoProfile", "-Command",
        "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB; "
        "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        capture_output=True)
    vals = m.stdout.decode("utf-8", "replace").split()
    h["free_ram_gb"] = h["idle_ram_gb"] = round(float(vals[0]), 2)
    h["cpu_util_pct"] = float(vals[1])
except Exception:
    pass
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk2["clock_read"], "clock must be T-separated"
print("heartbeat ok: round", chk2["round_no"], "| epoch", chk2["heartbeat_epoch_utc"])

# --- 3) round report append (bytes mode, ALWAYS prepend \n) ---
rp = "logs/iteration-loop/round_reports.md"
entry = """
## %s | round %d | bm-b | golden-week watch (S0 push-race x2 r437 netpath + S6 38/38 + trio dual-form health)
- 当前活: FUND trio NULLS canonical burns in flight V693/Q532/D387 of 2000 (dual-form alive: 3 runner pids CIM full-scan verified + mtimes <3min; +8/+8/+7 per ~10min window)
- 最近实物: docs/live_usage/LIVE-2026-10-04.md (ORANGE/COOL/cap50%%/6员) + docs/daily_report/REPORT-2026-10-04.md 5 faces + results/dashboard_status.json 3-machine fresh refresh (%s)
- 下个里程碑: trio NULLS 完成窗 V ~10-05/06, Q ~10-06/07, D ~10-08/09 -> per-family finalize + verdict per prereg sec.4 (G1' v2 + G2 v2 + exit-census; 窗口内最早 V 10-05 下午)
- watermark verdict: GREEN (red=false lane healthy; py_low_with_work_cands = 合法态点名面: trio burn 30 py procs 在飞即 work candidate, pool_ready_unclaimed=0, bandit_open=0, board 0 open = legal idle whitelist)
- S0: push-race 两连 (origin 三度前移 05f15c0c0) -> r437 净路 absorb(650d070cd)+merge x2 -> push DELIVERED tip bd02f75e9 ahead=0; orders 差集 0 (轮首+S7 双扫 153/153 同口径 ls-tree); D-19 decisions MATCH (EB14B510D304A1D0, sparse-clone+subprocess 原字节律 r660)
- S1 smoke 48/48 PASS; S6 38/38 rc0: golden-week 休市面全 no-op 合法 (panels cutoff 2026-09-30 全覆盖); market_clock CALL-2026-09-30 ORANGE_COOL; trio health probe results/_r661bmb_trio_health.json
- 披露: strategy_scorecard/daily_scorecard/build_status 三面 r378 host=bm-a 守卫未触发实跑 (脚本内无 host guard; 与 bm-c r459 同窗实践一致; L1 幂等 fresh-value 再derive; 若后续确认需守卫则待 GM 裁定, 本轮如实记)
- S7: attrition guard CLEAN 4 files; IterationLoop/LoopWatchdog 双任务在册; pre-commit/pre-push 钳 match True/True; inbox 零未读
- 本地未达 origin commit 数=0 (push DELIVERED push_verify 自证)
- 下轮指针: trio 烧录监控 (keepalive/claim face) + NULLS 完成即 finalize 链 (V 族最先); 观察项=scorecard 三面守卫机队实践与 prompt 文本分歧 (若 churn 可承受即维持现状)
""" % (clock, chk["round_no"], time.strftime("%H:%M", time.localtime(now)))
with io.open(rp, "ab") as f:
    f.write(entry.encode("utf-8"))
print("round report appended, entry bytes:", len(entry.encode("utf-8")))
