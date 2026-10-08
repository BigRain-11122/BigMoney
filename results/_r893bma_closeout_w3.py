# -*- coding: utf-8 -*-
"""r893 composite closeout writer (window#3 per r844/r888 adoption law):
state-bm-a.json + round_reports-bm-a.md append + fleet/machines/bm-a.json heartbeat."""
import io, json, time, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
DEC = "a6fe4864142a9491c928c953b793237f8a07d7db7caa52e6460576cfc49c7aa7"
ORD = "b998322344c7256bd6054b0a65f2ff56efc3abe1d54b82739ba0fc53b4f49538"

# ---------- state ----------
st = json.loads(io.open(ROOT + r"\state-bm-a.json", encoding="utf-8").read())
st.update({
    "round_no": 893, "round": 893, "loop_round": 893, "last_round": 893,
    "last_round_at": now, "last_round_closed": now, "last_round_ts": now,
    "last_run": now, "last_seen": now, "ts": now, "updated": now,
    "clock_read": now,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
    "last_decisions_sha": DEC, "last_orders_sha": ORD,
    "last_decisions_at": now, "last_decisions_ts": now, "last_orders_at": now,
    "last_decisions_seen": ("r893: DEC ee70cef0->a6fe4864 (D-20261008-09 governance-domain revisit, "
        "non-quant zero-action; consumed by r893 window#2 84badf07d; rolled here at closeout per that "
        "commit's own note; this window re-verified live origin blob sha == a6fe4864 exactly, zero new rows)"),
    "last_orders_seen": ("r893: ORD caef5b78->b9983223 (row 317 MV order-12 takeover = MV-domain "
        "already-deployed non-quant zero-action + EOL relayout format face; consumed by window#2 84badf07d; "
        "rolled here at closeout; this window re-verified live origin blob sha == b9983223 exactly, zero new rows)"),
    "last_decisions_src": "group origin/main via C: real-path fetch + git show (python subprocess raw-bytes canonical)",
    "current_task": ("W191 five-face insertion (S90 freeze-edits tool construction from committed forensics; "
        "prereg frozen ea42ee94a; seat 2130; tick ignite after) + GM bm-b reroute decision watch"),
    "task": ("W191 five-face insertion (S90 tool build from pairs_dump/s89_full_dump/BACK211; then tick ignite) "
        "+ GM bm-b reroute decision watch"),
    "next": ("W191 five-face insertion NEXT WINDOW FIRST: S90 freeze-edits tool = roll r892-emitted tool pairs "
        "one generation per extraction-from-emission law (OLD side = r892 tool's NEW column, now-live W190 faces; "
        "NEW side = W191 values from frozen prereg research/PERPETUAL_N1_W191_PREREG.md + BACK211 map in "
        "results/_r893bma_w191_buildgen.py); materials committed b411f1bfd: _r893bma_w191_pairs_dump.txt (all "
        "PF/EN/MAT/CL pairs extracted) + _r893bma_s89_full_dump.txt + 4 stage-1 probe dumps + inspect1.py; "
        "four insertions = pf N1_BANDS[191] row+prose (45-line pattern = 0cce3c47e diff verbatim template) + "
        "n1 WAVE_CONFIGS[191] + W191 materializer block + PASS claim; battery = py_compile + --dry + pf 9/9 + "
        "n1 selftest BEFORE commit; then tick ignite (r535 tick-architecture law: freeze edits on live stack, "
        "next tick self-ignites; verification = product growth within 2 ticks r325 law) + S6 chain rerun "
        "(skipped this window: midnight closed-market no-op territory, last full green = bm-c r784 40/40 + "
        "bm-a r892 39-leg) + S0 ff-sync: absorb branch machine/bm-a-r893 + local main 4-behind catch-up "
        "(rebase was blocked this window by foreign post_review 00:15 new-day half-product)"),
    "did": ("r893 composite closeout (3rd window per r844/r888): window#1 (22:38 dead 22:59) prereg chain "
        "3 commits incl ea42ee94a freeze; window#2 (23:28 dead 23:50:41) S0.5 = O-20261008-2315 receipt "
        "84badf07d + DEC/ORD consumption + W190 sec7/8 backfill 6cc28b65b + S90 forensics to disk; window#3 "
        "(this): concurrent-session adjudication by cmdline (23:55/23:57/00:00 = evolution-reflection / "
        "minigame-tick / group-decision foreign domains, non-bigmoney; 23:03/23:05 = interactive idle zero "
        "repo writes) + r893 dead-tail confirmed (last artifact 23:50:46, no state/report write) + S0 absorb "
        "b411f1bfd (daemon live faces + 12 S90 forensic files preserved on origin lineage) + rebase blocked "
        "by foreign post_review half-product (00:15 day-rollover write, not mine to commit) -> branch-route "
        "per protocol + S1 smoke 49/49 + DEC/ORD live re-verified == window#2 receipt values"),
    "last_action": "r893 composite closeout: state/report/heartbeat writes + branch push machine/bm-a-r893",
    "last_artifact": ("W191 prereg frozen+pushed ea42ee94a (research/PERPETUAL_N1_W191_PREREG.md, banned_direction_gate "
        "ADMIT) + S90 construction materials committed b411f1bfd + O-20261008-2315 receipt 84badf07d + W190 "
        "sec7/8 backfill 6cc28b65b"),
    "latest_artifact": "W191 prereg frozen on origin (ea42ee94a) + S90 forensic materials preserved (b411f1bfd)",
    "now_active": "r893 closed: W191 prereg frozen+pushed, five-face insertion = next window first task; engine idle queue 0",
    "verify": ("smoke 49/49 + DEC/ORD origin blob re-verified == receipt values (a6fe4864/b9983223, zero new rows) "
        "+ orphan face=0 (22 py faces, read-only probe) + engine ALIVE idle (rc0 ticks) + branch push receipt "
        "+ local-vs-origin: branch route (see next pointer, clear next window S0)"),
    "idle_rounds": 0, "agenda_starved": False,
})
io.open(ROOT + r"\state-bm-a.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))

# ---------- heartbeat ----------
hp = ROOT + r"\fleet\machines\bm-a.json"
hb = json.loads(io.open(hp, encoding="utf-8").read())
hb.update({
    "last_seen": now, "ts": now, "clock_read": now,
    "heartbeat_epoch_utc": epoch,
    "current": "r893 closed: W191 prereg frozen, five-face insertion next window first; engine idle rc0",
    "verdict": "green (red=false; engine alive; W191 freeze chain in flight, prereg done, insertion next)",
    "idle_rounds": 0, "agenda_starved": False,
})
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"

# ---------- round report append (UTF-8 face, CRLF tail probe per r843 law) ----------
line = (
    "2026-10-09T00:21+08:00 | r893 | dead-tail composite closeout (3rd window per r844/r888 law; "
    "dead#1 22:38 window W191 prereg chain 3 commits incl freeze ea42ee94a; dead#2 23:28 window S0.5 "
    "O-20261008-2315 receipt 84badf07d + DEC/ORD consumption + W190 sec7/8 backfill 6cc28b65b + S90 "
    "forensics; this window#3 adjudication+absorb+closeout) | WM-VERDICT: green (red=false lane healthy; "
    "engine ALIVE rc0 idle queue 0; next_pick moneyflow IC claimed=advisory panel-source-blocked) | "
    "当前活: r893 收口 (孤儿面=0; 并发窗判定=3 外域窗 evolution/minigame-tick/group-decision + 2 交互窗零仓内写; "
    "r893 死尾实锚=末件 23:50:46 无 state/报告写) | 本轮: S0 吸收 b411f1bfd (daemon live faces + 12 件 S90 "
    "构造材全保: pairs_dump/s89_full_dump/4 stage-1 dumps/inspect1) + rebase 被外写者 post_review 00:15 新日 "
    "半成品阻塞→分支投递通道留痕 + S1 smoke 49/49 + DEC/ORD 活 blob 复核==window#2 回执值 (a6fe4864/b9983223) "
    "零新行 | 实物: ①W191 prereg 冻结已上 origin (research/PERPETUAL_N1_W191_PREREG.md @ ea42ee94a·A "
    "435_004..437_003 staircase FIFTY-FIRST / B 437_004..437_203 own-A W141 leg2·N=2,200·banned_direction_gate "
    "ADMIT) ②O-20261008-2315 维持全力回执已推 (84badf07d·orders_ack 189) ③W190 sec7/8 回填 (6cc28b65b·账本 "
    "825,328/K 415,920 EXACT) ④S90 构造材 12 件入库 (b411f1bfd) | 下轮指针: ①W191 五面插入=下轮第一活 (S90 "
    "freeze-edits 工具=滚 r892 工具 pairs 一代 extraction-from-emission 律; 四插入=pf N1_BANDS[191]+散文 "
    "(0cce3c47e diff 逐字模板)+n1 WAVE_CONFIGS[191]+W191 物化器块+PASS claim; 电池=py_compile+--dry+pf 9/9+n1 "
    "selftest; 后 tick 点火 r535/r325 律) ②S0 ff-sync: 吸收 branch machine/bm-a-r893 + local main 4-behind "
    "追赶 ③S6 全链补跑 (本窗跳过·午夜闭市 no-op 域·last full green=bm-c r784 40/40+bm-a r892 39 腿) ④GM bm-b "
    "reroute A/B decision watch ⑤DEC a6fe4864/ORD b9983223 水位已收口 | 验证: smoke 49/49 + DEC/ORD 复核恒等 + "
    "attrition guard 未跑 (S6 面下轮补) + orphan face=0 (22 py faces) + engine ALIVE idle + 自愈四件套=loop "
    "pin 8/watchdog rc0/双爪 PRESENT (未逐一复验·下轮 S7 补) + orders unacked=0 (window#2 已收) + 本地未达 "
    "origin commit 数=2 (branch machine/bm-a-r893 投递·下轮 S0 ff-sync 清偿·rebase 被外写者半成品阻塞留痕) + "
    "token: L1 零 API [via bm-a r893]\r\n")
with io.open(ROOT + r"\round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("CLOSEOUT WRITES OK", now, "epoch", epoch)
