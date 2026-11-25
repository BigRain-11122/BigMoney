# -*- coding: utf-8 -*-
"""r2115 (bm-c) round bookkeeping: report row + state keys.

Written as a script rather than a hand edit so the state file is re-serialised
with the settings it already uses (indent=1, sort_keys=True, trailing newline)
and the round report row is appended from a single literal.
"""
import io
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORTS = os.path.join(ROOT, "round_reports-bm-c.md")

NOW = time.localtime()
STAMP = time.strftime("%Y-%m-%d %H:%M", NOW)

ROW = (
    "| {stamp} | 2115 | **PRODUCT（产品优先律·watermark=green（red=false·lane=healthy）·孤儿面=0·"
    "竞争窗 rc=0 CLEAN）**：把上一轮没关掉的那条红关掉——全量冒烟里 "
    "`product: the book a person holds is priced in money (r1900)` 判红「the page does not print -30,503」"
    "**不是账算错，是账本多走了一根 bar 而读它的那一页没重生成**：`results/etf_book_forward/LEDGER.json` "
    "已有 **24 根 bar**（末根 2026-11-25·nav 0.9694971·provisional），换成一笔钱 = **-30,503 元**；"
    "而 `docs/live_usage/LIVE-latest.md` 停在 **23 根 bar**（至 11-24·0.981079·-18,921 元）。"
    "根因=读面只在链里被重生成，而链已经连着多轮没跑完整代（竞争窗），账本却每交易日长一根——"
    "**这是一场比赛，不是内容不符**。修法=在链上重生成读面：`--only=ceo_live_usage` rc0 1.3s → "
    "页面已印 **-30,503 元**，并按账本字节重算该 token 复验命中（True）；同日 `LIVE-2026-11-26` 孪生落盘。"
    "**第二件**：把躺在 `Tools/s6_chain_bmc.py` 里未提交的 **5 条孤儿面链腿**（idx_fut_carry_always_on_price /"
    " roll_step_reversal / capacity_lots / decision_face / etf_book_defense_spells）实跑验证——"
    "`--only` 五腿 **5/5 rc0 CHECK_OK**（2.6s，判词 PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND /"
    " MIXED_BY_PRODUCT / MARKET_IS_NOT_THE_GATE / NO_ORDER_ON_BOTH_LEGS / 17 spells·defensive 54.5%）→ "
    "接线可发布（r1282 孤儿类：面在、读它的腿不在）。"
    "｜**未验证（如实）**：①**全量套件本轮仍未跑完**——套件自己的 harness 腿写明「cannot close inside a round "
    "window」（慢腿 240.5s/2 腿），本轮实跑至 **262 腿**被 5 分钟无输出上限杀掉，"
    "**不宣称套件总数**；观察到的唯一 FAIL 就是上面这条且已修；②轮首 **1,963 件脏件**"
    "（1,946 M + 17 ??）= 已死对端跑出的整代链产物（data/daily 刷新到 11-25、docs/research 派生面），"
    "按轮首脏纪律**只定向 add 本轮产出**，不动它们；③`update_astock_daily.py refresh`（pid 98764·11-25 19:16 起·"
    "7h）仍在跑，属 bm-b 车道数据拉取，本轮只读观察未触碰。｜S0：machine.json=**bm-c**｜"
    "`orphan_face_probe` py_faces=4 **orphans=0**／resident_servers=2｜"
    "`repo_write_contention --lookback-min 45` **rc=0 CLEAN**（单宿主 pid 22284，无对端在写）｜"
    "fetch 后 ahead=0 behind=0｜S0.5：`Tools/orders_ack_scan.py` **CLEAN**（117 令 / 331 ack / unacked=[] / "
    "124 条他机 lane 广播 stale 注记）；集团 `origin/main:docs/decisions.md` 原生字节 **250,586B** sha256 "
    "**79e3083b…** 与自持水位**逐位相等** → 零新决策行零动作；fleet/inbox 空、fleet/tasks 无 open｜"
    "S3：水位 **red=false / lane=healthy**；饱和引擎 `Tools/saturation_engine.py status` **rc0 alive**"
    "（last_verdict=idle·struct_wait 0）；attrition **CLEAN**（4 账本·3 条历史缩行 healed）｜"
    "S6：`--only=ceo_live_usage` rc0 + `--only` 五条新腿 5/5 rc0；**全链未跑**（单轮预算 + 1,963 件在途世代）｜"
    "S7：`register_loop_task` 幂等 no-op（pin=0·PT5H·下次 02:35）；`register_watchdog_task` 重注册 OK 但 "
    "**S4U XML 翻转仍被拒（拒绝访问·需提权）→ LogonType 回归面挂着，不当自愈**；pre-commit / pre-push 两爪"
    "重装（LF 归一）。｜**CEO 过程可见面**：当前活＝关掉「页面比账本少一根 bar」那条红，并把 5 条孤儿面接上链｜"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\docs\\live_usage\\LIVE-2026-11-26.md`"
    "（02:30，已印 -30,503 元）｜下个里程碑＝**用分离日志跑一次完整套件并落总数**（≤48h）+ "
    "整代链产物落地（等 1,963 件在途世代跑齐）｜记账：本行 1 处 + state 1 处 + 心跳 1 处 = 3 处。|"
).format(stamp=STAMP)


def append_row():
    with io.open(REPORTS, "a", encoding="utf-8", newline="") as fh:
        fh.write("\n" + ROW + "\n")
    return ROW


def update_state():
    raw = io.open(STATE, encoding="utf-8").read()
    d = json.loads(raw)
    prev = d.get("round_no")
    d["round_no_prev"] = prev
    d["round_no"] = 2115
    d["round_no_note"] = (
        "r2115: prev=%s read from this file; the report rows above agree on r2114, "
        "so prev+1 is the free number this window" % prev
    )
    d["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", NOW)
    d["clock_read_source"] = "local system clock (Win32, Asia/Shanghai)"
    d["heartbeat_epoch_utc"] = int(time.time())
    d["heartbeat_epoch_utc_type"] = "int"
    d["yield_note"] = {
        "round": 2115,
        "did": "closed the r1900 smoke red (reader face re-derived after the ledger gained its 24th bar) "
               "and proved the five orphan chain legs sitting uncommitted in Tools/s6_chain_bmc.py",
        "why": "the chain has not closed a generation for many rounds under contention while the ledger "
               "grows one bar per session, so every reader face drifts one bar and the leg reads a clock "
               "race as a content mismatch",
        "next": "detached full-suite run with a total, then a full chain generation once the in-flight "
                "1,963-file generation is ready to publish",
    }
    d["s0_r2115"] = (
        "machine.json=bm-c | orphan_face_probe py_faces=4 orphans=0 resident_servers=2 | "
        "repo_write_contention rc=0 CLEAN (single host pid 22284) | ahead=0 behind=0 | "
        "1963 dirty at open (1946 M + 17 ??, a dead peer's full chain generation) -> directional add only"
    )
    d["s05_r2115"] = (
        "orders_ack_scan CLEAN (117 orders / 331 acks / unacked=[] / 124 stale other-lane notes); "
        "origin/main:docs/decisions.md native 250,586 B sha256 79e3083b… == watermark -> zero new rows; "
        "fleet/inbox empty; fleet/tasks no open"
    )
    d["s1_r2115"] = (
        "full suite NOT closed: the suite's own harness leg says it cannot close inside a round window "
        "(240.5 s over the slow legs); this round's run reached 262 legs before the 5-minute no-output cap "
        "killed it. The one FAIL observed was 'product: the book a person holds is priced in money (r1900)' "
        "-> fixed (page re-derived, -30,503 printed, token re-derived from LEDGER bytes = True). No suite "
        "total is claimed."
    )
    d["s7_r2115"] = (
        "register_loop_task no-op (pin=0 PT5H, next 02:35) | watchdog re-registered but S4U XML flip "
        "REFUSED (access denied, needs elevation -> LogonType regression face stands, not called healed) | "
        "pre-commit + pre-push claws reinstalled (LF normalised) | attrition CLEAN (4 ledgers, 3 historic "
        "shrinks healed) | saturation_engine status rc0 alive (last_verdict idle)"
    )
    d["product_r2115"] = {
        "red_closed": "smoke r1900: docs/live_usage re-derived in-chain (--only=ceo_live_usage rc0 1.3s); "
                      "page printed -18,921 CNY / 0.981079 over 23 bars while LEDGER had 24 bars "
                      "(2026-11-25, nav 0.9694971, provisional) = -30,503 CNY; page now prints -30,503",
        "wiring_proved": "5 orphan faces now ride check-first chain legs: idx_fut_carry_always_on_price, "
                         "idx_fut_carry_roll_step_reversal, idx_fut_carry_capacity_lots, "
                         "idx_fut_carry_decision_face, etf_book_defense_spells -> --only 5/5 rc0 CHECK_OK "
                         "(2.6 s) on the uncommitted Tools/s6_chain_bmc.py additions",
        "artifacts": [
            "docs/live_usage/LIVE-2026-11-26.md (+LIVE-latest)",
            "Tools/s6_chain_bmc.py (five legs, verified this round)",
            "results/_r2115bmc_s6_chain.only-ceo_live_usage.json",
        ],
        "unverified": [
            "full smoke total (suite cannot close in a round window; 262 legs then killed)",
            "full S6 chain generation (1,963-file generation in flight, not published)",
        ],
    }
    d["next_r2115"] = (
        "run the full suite from a detached log and publish the total; publish one full chain generation "
        "when the in-flight work settles; keep reader faces re-derived in-chain so a ledger bar never "
        "outruns the page that quotes it"
    )
    out = json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    io.open(STATE, "w", encoding="utf-8", newline="").write(out)
    return prev, len(d)


if __name__ == "__main__":
    prev, nk = update_state()
    row = append_row()
    print("state round_no %s -> 2115 (%d keys)" % (prev, nk))
    print("report row appended (%d chars) at %s" % (len(row), STAMP))
