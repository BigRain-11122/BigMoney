# r273 bm-a closeout: state round_no 273, heartbeat refresh (epoch int / T-sep clock), round report line.
# Byte-face laws probed this round: state/heartbeat = no-BOM/CRLF/indent=1/no-trail-NL;
# round_reports = BOM/CRLF/no-trail-NL. orders_ack preserved verbatim (84/84, no new orders).

import json, time, datetime, os

now = datetime.datetime.now()
ts_str = now.strftime("%Y-%m-%d %H:%M")
iso = now.astimezone().isoformat()
epoch = int(time.time())

# ---- 1) state-bm-a.json ----
p = "state-bm-a.json"
d = json.load(open(p, encoding="utf-8-sig"))
d["round_no"] = 273
d["ts"] = ts_str
d["last_round"] = 273
d["last_round_at"] = ts_str
d["did"] = (
    "R273 unattended maintenance+supervision round: S0 push-convergence of parked r272 "
    "(rebase onto bm-b r275+addendum, push clean 9e66d7b8->main); S0.5 orders 84/84 double-verified "
    "(first probe mis-read ack string char-wise per r123 pit law, recovered via ''.join+split, "
    "canonical Tools/orders_diff.py diff empty 84/84 = healthy, NO fake-repair executed); decisions tail "
    "unchanged D-11 (zero new BigMoney rows); smoke 25/25; S6 25 legs rc=0 weekend no-op family "
    "(mid-autumn holiday 09-25, cutoff 09-24 legal; moneyflow rank-pass spawn + AH panel refresh spawn "
    "both throttled-detached per 30-min self-heal); migration v2.1 precheck heartbeat cadence adjudicated "
    "= design-internal 15-min still-waiting loop (journal quiet 10min not stall), executor PID 35344 alive, "
    "sole holder CEO Code.exe/28276 fail-closed; compute_audit pool_starvation flag = weekend legal-idle "
    "whitelist (py_low_board_clear: open 0/bandit 0/pool 0)"
)
d["verdict"] = (
    "R273: watermark GREEN (red=false py_low_board_clear legal-idle weekend whitelist R272 continuity), "
    "smoke 25/25, S6 25x rc=0, post_review latest run 22:20 all YES, orders 84/84 canonical tool verified"
)
d["next"] = (
    "09-28 next trading-bar chain (Monday first post-holiday bar: paper/prospect/t35 legs fire), "
    "migration executor supervised (precheck auto-triggers on CEO editor close, window to 09-29 12:00), "
    "10-01 month-first round chain (science_audit+monthly_briefing+self_review+date gate)"
)
d["updated"] = ts_str
d["updated_at"] = ts_str
out = json.dumps(d, ensure_ascii=False, indent=1)
open(p, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))

# ---- 2) heartbeat fleet/machines/bm-a.json ----
p = "fleet/machines/bm-a.json"
h = json.load(open(p, encoding="utf-8-sig"))
ack_before = h["orders_ack"]
h["last_seen"] = ts_str
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["round_no"] = 273
h["current_task"] = "R273 closed (maintenance+supervision round; S0 push-convergence + S6 weekend no-ops + migration v2.1 precheck supervision)"
h["verdict"] = (
    "R273 maintenance+supervision: watermark GREEN py_low_board_clear (weekend legal-idle), smoke 25/25, "
    "S6 25 legs rc0, orders 84/84 canonical diff empty, post_review all YES, migration executor alive "
    "precheck-waiting (design-internal 15-min heartbeat), pool 0 ready legal-idle whitelist"
)
out = json.dumps(h, ensure_ascii=False, indent=1)
open(p, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
back = json.load(open(p, encoding="utf-8-sig"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert back["orders_ack"] == ack_before, "orders_ack must be preserved verbatim"
assert "T" in back["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat: epoch int", back["heartbeat_epoch_utc"], "| ack tokens", len(ack_before.split()))

# ---- 3) round report line (BOM/CRLF/no-trail-NL) ----
p = "logs/iteration-loop/round_reports-bm-a.md"
b = open(p, "rb").read()
assert b.endswith(b"\r\n") is False  # current tail has no trailing newline
line = (
    f"{ts_str} | R273 | bm-a dept:工程·舰队（无人值守维护+监督轮）| 水位=绿（py_low_board_clear 合法 idle 周末白名单 R272 延续：open 0/bandit 0/池 0）"
    f"| did: S0 r272 停靠分支自然收敛（pull --rebase 落 bm-b r275+addendum 上、push 干净 9e66d7b8 上 main）；"
    f"S0.5 双扫 84/84 差集空——首探针把 ack 字符串按字符迭代（r123 坑律现场重犯自捕，''.join+split 自纠），正典 Tools/orders_diff.py 复跑 diff empty 84/84=心跳健康、零假修复；"
    f"decisions 尾停 D-11 零新增行；S1 smoke 25/25；S2 板 84 票全 done/claimed 零 open+job_list 0；"
    f"S3 复审最新 run 22:20 全 YES+迁移执行器监督裁定=journal 静默 10min 非卡死（v2 precheck 心跳降频律：签名稳定后 15min/条，22:35 下一条），执行器 PID 35344 活、唯一占柄=CEO Code.exe/28276 fail-closed；"
    f"S6 25 腿全 rc=0 周末 no-op 族（中秋 09-25 休市 cutoff 09-24 合法；moneyflow rank-pass spawn+AH 面板 refresh spawn=30-min 自愈节流分离车道）；"
    f"S7 双任务健康（Loop Running/Watchdog Ready）"
    f"| 证据: smoke 25/25+S6 25x rc0+orders_diff.py diff empty 84/84+git push 9e66d7b8 main+journal 尾读 22:20:04"
    f"| 下轮: 09-28 周一节后首 bar 链+迁移 precheck 自动触发监督+10-01 月首轮三件套 [via bm-a]"
)
if not b.endswith(b"\n"):
    b += b"\r\n"
b += line.encode("utf-8")
open(p, "wb").write(b)
print("round report: R273 line appended, file now", len(open(p, "rb").read()), "bytes")
