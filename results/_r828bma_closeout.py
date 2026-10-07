# -*- coding: utf-8 -*-
"""r828 bm-a round closeout writer (r819/r821/r827 bloodline): state 827->828,
heartbeat epoch int + T-sep clock, seat MSG self-ack -> processed, round report
line append. Fresh-read-modify-write single-writer (multi-writer file law)."""
import json, os, time, datetime, subprocess, shutil, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

dec_sha = "ee4837e9287da2702b3d4a410a141bfe07b343756be0857aa4e7bddb37abb1dd"

# --- state file ---
sp = os.path.join(ROOT, "state-bm-a.json")
s = json.load(open(sp, encoding="utf-8"))
assert s["round_no"] == 827, f"round_no drift: {s['round_no']}"
s.update({
    "round_no": 828, "round": 828, "loop_round": "r828",
    "last_round": "r828", "last_round_at": iso, "last_run": iso,
    "last_seen": iso, "ts": iso, "clock_read": iso, "updated": iso,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": s.get("heartbeat_epoch_utc", epoch),
    "current_task": "W175 seat chain DELIVERED (probe rc0 ADMIT + seat MSG-1434 push 25c414e95); next W175 prereg build",
    "last_action": "W175 pre-seat probe + seat published=reserved (r827-declared anchor fulfilled); S6 37/37 rc0 re-run; token_usage drift healed via chain token_meter re-derive",
    "now_active": "W175 prereg build next window per two-window law (r797/r799)",
    "latest_artifact": "fleet/inbox/MSG-2026-10-07-1434-bma-w175-seat.md + results/_r828bma_w175_probe_receipt.json @2026-10-07T14:3x (A 399_804..401_803 staircase 35th instance + B 401_804..402_003 own-A mutual exclusion)",
    "next": "(1) W175 prereg build (xform W174->W175, facts=probe receipt + seat 25c414e95, banned gate) (2) W175 freeze chain 5-face edits + double selftest + freeze commit + 2-tick ignition (two-window law) (3) W176 pre-seat probe+seat (4) 10-08 re-arm data chain first trading day after golden week",
    "last_decisions_sha": dec_sha,
    "last_decisions_at": iso, "last_decisions_ts": iso,
    "last_decisions_seen": "D-20261007-06 (newest; D-20261007-04① D-02-06 early-core verified + 05/06 governance-day rows consumed r828, zero BigMoney dispatch)",
    "last_orders_sha": "e6a1dee6270e08f5fbc457b3fa275c62804d0e9d158765d84e03d358ff4b5703",
    "last_orders_at": iso,
    "did": "r828 W175 seat chain (r823 bloodline): pre-S0 daemon keepalive self-commit (r642 net-tree root cure) + rebase+push; S0.5 orders diff 0 unacked + decisions consumed ee4837e9; S1 smoke 48/48; S3 W175 probe rc0 ADMIT + seat MSG published push 25c414e95 (r565 early-visibility law); S6 37/37 rc0 via _r828bma_s6_chain (r819/r823 bloodline verbatim; golden-week no-op legs honest; token_usage drift healed); S7 four-piece suite green (loop pin=8 next 14:48 + watchdog 14:42 + precommit/prepush claws reinstalled LF-normalized)",
    "verify": "W175 probe leg0-4 asserts ALL PASS (registry 172 rows tail=W174, ledger head 788,212 machine-read; staircase A 399_604..401_603 refused by W174 B -> A 399_804..401_803 hops=1 35th instance; naive B inside own-A -> B 401_804..402_003 hops=1; leg2 conflicts=0; leg3 origin vacancy held); seat delivery 25c414e95 push+fetch behind0/ahead0; smoke 48/48; S6 37/37 rc0 (CHAIN_EXIT=0 re-verified; first-run Exit-1 = shell pipeline artifact, disclosed)",
    "notes": s.get("notes", ""),
})
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written: round_no 827->828, decisions sha -> ee4837e9...")

# --- heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
h.update({
    "machine_id": "bm-a", "last_seen": iso, "ts": iso, "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "last_heartbeat_epoch_utc": h.get("heartbeat_epoch_utc", epoch),
    "round_no": 828, "round": 828, "loop_round": "r828", "last_round": "r828",
    "current_task": "W175 seat chain delivered; next W175 prereg build (two-window law)",
    "current": "W175 seat chain delivered; next W175 prereg build",
    "task": "W175 seat chain delivered",
    "now_active": "W175 prereg build next window per two-window law",
    "last_action": "W175 pre-seat probe + seat MSG published=reserved + S6 37/37 rc0 + token heal",
    "latest_artifact": "fleet/inbox/MSG-2026-10-07-1434-bma-w175-seat.md + results/_r828bma_w175_probe_receipt.json @2026-10-07T14:3x",
    "next_milestone": "W175 prereg+freeze+finalize (proj ledger 790,412/K 382,920; window <=48h never-dry) + 10-08 re-arm data chain (first trading day)",
    "verdict": "healthy",
    "cpu_load_pct": h.get("cpu_load_pct"),
})
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
d2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(d2.get("heartbeat_epoch_utc"), int), "epoch must be JSON int"
assert "T" in d2.get("clock_read", ""), "clock_read must be T-separated"
print("heartbeat written + epoch-int self-check PASS")

# --- seat MSG self-ack -> processed ---
src = os.path.join(ROOT, "fleet", "inbox", "MSG-2026-10-07-1434-bma-w175-seat.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-2026-10-07-1434-bma-w175-seat.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("seat MSG self-ack filed -> processed/")

# --- round report line ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
line = (
    f"\n2026-10-07T14:4x+08:00 | r828 bm-a (dept:研究+工程) | "
    f"watermark verdict: 绿(red=false lane=healthy; probe py_low_board_clear=假期合法 idle 白名单面: 板全闭环 0 open 票+W174 已 finalize 已送达+W175 seat 已发布 never-dry 线保持·satengine alive rc0 queue0) | "
    f"当前活: W175 pre-seat 席位链本窗落地(r827 预宣告锚兑现) | "
    f"最近实物: fleet/inbox/MSG-2026-10-07-1434-bma-w175-seat.md + results/_r828bma_w175_probe_receipt.json @2026-10-07T14:3x (A 399_804..401_803 阶梯第三十五例 E36/B 401_804..402_003 own-A leg2·post-W174 宇宙重 derive 强制兑现) | "
    f"下个里程碑: W175 prereg build+freeze+finalize (proj ledger 790,412/K 382,920; 窗≤48h never-dry) + 10-08 复市首交易日数据链 re-arm | "
    f"did: S0 pre-S0 daemon keepalive self-commit(r642 净树根治)+rebase+push; S0.5 orders 差集 166/166 零未回执+ord 水位 e6a1dee6 MATCH+dec 水位 4c32527b->ee4837e9 消费(D-20261007-04① D-02-06 提前核销注记/05/06 治理日行=HQ 域零 BigMoney 派单); S1 smoke 48/48; S3 主产=W175 席位链(pre-seat probe rc0 ADMIT post-W174 宇宙重 derive 强制兑现+seat MSG-1434 published=reserved push 25c414e95 r565 律); S6 37/37 rc0(_r828bma_s6_chain=r819/r823 血统 verbatim·金周 no-op 族如实·token_usage 漂移经链内 token_meter 再 derive 自愈); S7 四件套绿(loop pin=8 下次 14:48 在位+watchdog 14:42 在位+precommit/prepush claw 重装 LF 归一)+state 827->828 递进+心跳 epoch int+T 分隔自证+seat MSG self-ack 收档 processed | "
    f"verify: W175 probe leg0-4 断言全过(注册表 172 行 tail=W174·ledger head 788,212 机读·A 399_604..401_603 被 W174 B 拒->A 399_804..401_803 hops=1 第三十五例·naive B 落 own-A->B 401_804..402_003 hops=1·leg2 conflicts=0·leg3 origin 空位持); seat 送达 25c414e95 push+fetch behind0/ahead0; smoke 48/48; S6 37/37 rc0(CHAIN_EXIT=0 复验·首跑外壳 Exit-1=管道伪影已披露) | "
    f"计分: 2(能跑/能看/能用实物=W175 席位链=引擎连续波供给线实物增量+S6 37 门面板再生) | "
    f"宝藏捕获问: 本批零新方法零新宝藏(席位链 r823 血统 verbatim 复用非新方法论·TREASURE/METHODOLOGY 零 append) | "
    f"登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作(treasure_guard 未触发) | "
    f"下轮指针: r829=W175 prereg build(xform W174->W175·facts=probe 回执+seat 25c414e95·banned gate)+freeze 链 5-face 编辑(两窗律 r797/r799: prereg 与 freeze 分窗)+2-tick 点火+finalize | "
    f"本地未达 origin commit 数=0(收尾 push 后 fetch 复核补录) | [r828 bm-a]\n"
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended")
