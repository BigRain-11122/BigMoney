"""_r235bmc_close.py -- bm-c r235 close: round report append + state flip
235->236 + heartbeat update. Ledger append three-checks (tail-newline,
pipe-count, diff-range) per account-file discipline.
"""
import datetime as dt
import json
import time

REPORT = "logs/iteration-loop/round_reports-bm-c.md"
STATE = "state-bm-c.json"
HB = "fleet/machines/bm-c.json"

LINE = (
    "2026-09-29T19:5x+08:00 | r235 bm-c (dept:数据+舰队·源分层定谳+5x 补账轮) | "
    "WM-VERDICT: 绿 (red=false@watermark_red.json 19:10 lane=healthy; probe 19:40 py_low_board_clear 合法=板 0 open/bandit claimed-parked/池 ready 1=W10-GENERATE bm-b pid3808 在飞=漏斗纪律合法等待) | "
    "CEO 可见面: 当前活=core48 日线源分层定谳（update_daily 零行 no-op 之谜三源探针收口）; "
    "最近实物=research/digests/DIGEST-20260929-daily-source-stratification.md（19:5x·三源探针+500 行 parity=klc2 慢性 ~21:00 夜发滞后·hisdata/generic 缺 amount 禁写源 R34 二例）+results/_r235bmc_sinalag_{probe,parity}.{py,json}; "
    "下个里程碑=W10-GENERATE 收割→SCREEN/JUDGE 链（bm-b lane·窗 ≤48h）+09-29 bar klc2 ~21:00 自然发布→纸盘链当晚自动落 | "
    "did: S0-1 锚 bm-c→漂移吸收 commit（autofill/dispatcher）→pull×2（吸收 bm-b r438 收口=W10-GENERATE 发射死锁根修+人工点火 pid3808 dedup 1500/5000@close+CODELY 再整编 7,120B）→"
    "S0.5 令差集 122/122 集合差 0+decisions 三新行核（D-29-01 executed/D-29-02②回执 F-20260929-01 在树复验=已闭·D-29-03 BigDomain 域零动作）→S1 smoke 26/26→S2 双板 0 open+job_list 空→"
    "S6 37 腿全 rc=0 零非绿（dualrun streak 43/3·09-29 bar klc2 未发诚实 cutoff 09-28·REPORT/LIVE-0929 重生）→"
    "r235 5x HANDOVER 补账（r225/r230 两窗漏核对披露=坑-79 族再犯+增量窗 r221-235 条目落盘·统一链 344,056 实读线性归位 W9 344,031→A158-FV +9→A10 +16）→"
    "源分层探针批（三源尾 bar 探针+klc2 vs hisdata 500 行重叠窗逐列 parity=唯一差异列 amount·OHLCV 逐位同+通用端点字段核无 amount→三源终谳：klc2 唯一 amount 全源=唯一合法写源·~21:00 慢性夜发=结构性诚实等源·两早源禁建回退写腿）→digest+CODELY 条目落地→S7 三查绿（pin=5 no-op/看门狗 Ready/爪 OK）| "
    "verify: smoke 26/26; S6 37 腿 rc=0 证据=results/_r235bmc_s6_chain.json（non_green=NONE）; 探针证据=results/_r235bmc_sinalag_probe.json+_r235bmc_sinalag_parity.json（3 符号交叉验证）; HANDOVER r235 条目在树+统一链 344,056=t101_v4_a10_regimecombo.json 直读; CODELY 8.3KB≤10KB 线内 | "
    "next: (a) W10-GENERATE 收割观察（bm-b pid3808）→SCREEN/JUDGE 链 (b) 09-29 bar ~21:00 klc2 自然发布→当晚 S6 链自动落 bar+纸盘记账 (c) W11 候选起草窗（gated W10 落地·48 PASS 门池族选+D6 邻接双披露） (d) 10-01 月首轮三件套+REGIME_GUARD v3 日期门 hands-off (e) r240 下次 5x [via bm-c]\n"
)


def main():
    # 1) round report append (three-checks)
    with open(REPORT, "rb") as f:
        raw = f.read()
    tail_ok = raw.endswith(b"\n")
    with open(REPORT, "a", encoding="utf-8", newline="") as f:
        if not tail_ok:
            f.write("\n")
        f.write(LINE)
    with open(REPORT, "rb") as f:
        raw2 = f.read()
    added = raw2 == raw + (b"" if tail_ok else b"\n") + LINE.encode("utf-8")
    print("report_append:", "OK" if added else "DIFF-RANGE-FAIL",
          "| tail_newline_was:", tail_ok,
          "| pipes:", LINE.count("|"))

    # 2) state flip 235->236
    st = json.load(open(STATE, encoding="utf-8"))
    assert st.get("round_no") == 235, f"unexpected round_no {st.get('round_no')}"
    now = dt.datetime.now().astimezone().isoformat(timespec="minutes")
    st.update({
        "round_no": 236,
        "updated": now,
        "note": "r235: source-stratification verdict landed (klc2 chronic ~21:00 nightly publication = sole amount-capable source = structural honest-wait; hisdata/generic lack amount = R34-family no-write-source) + 5x HANDOVER debt backfill (r225/r230 missed) + S6 37 legs green + state 235->236",
        "last_round_ts": now,
        "did": "r235 closed: source stratification probe batch (3-feed tail probe + klc2-vs-hisdata 500-row parity = amount-only diff, OHLCV byte-equal; generic endpoint amount-absent -> klc2 sole legal write source, ~21:00 chronic lag = honest wait, no fallback write leg lawful) + DIGEST-20260929-daily-source-stratification.md + CODELY entry + 5x HANDOVER backfill entry (r221-235 window, unified ledger 344,056 linear W9 344,031 -> A158-FV +9 -> A10 +16) + S6 37 legs all rc=0 (dualrun streak 43/3; 09-29 bar klc2 unpublished honest cutoff 09-28) + drift-absorb commit + bm-b r438 close absorbed (W10-GENERATE manual ignition pid3808 in-flight)",
        "verify": "smoke 26/26; S6 37 legs rc=0 evidence _r235bmc_s6_chain.json; probe/parity JSONs 3-symbol cross-validated; HANDOVER r235 entry in-tree; CODELY 8.3KB under 10KB line; orders 122/122 diff 0",
        "next": "(a) W10-GENERATE harvest watch (bm-b pid3808) -> SCREEN/JUDGE chain (b) 09-29 bar ~21:00 klc2 natural publication -> same-night S6 auto-land + paper marks (c) W11 candidate drafting window (gated on W10 landing, 48 PASS gate pool family selection, D6 adjacency dual-disclosure) (d) 10-01 month-first trio + REGIME_GUARD v3 date-gate hands-off (e) r240 next 5x",
        "last_round_at": "r235",
        "current_task": "r235 closed: source stratification verdict + 5x HANDOVER backfill; next: W10 harvest watch -> W11 drafting window",
        "updated_at": now,
        "gpu_free_vram_mib": 9715,
        "cpu_pct": 7.0,
        "idle_ram_gb": 10.3,
    })
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    print("state: 235->236")

    # 3) heartbeat (epoch int + clock_read T-separated)
    hb = json.load(open(HB, encoding="utf-8"))
    epoch = int(time.time())
    hb.update({
        "last_seen": now,
        "current_task": "r235 closed: daily-source stratification verdict (klc2 ~21:00 chronic lag, amount-gate on alternates) + 5x HANDOVER backfill; next: W10 harvest watch -> W11 drafting window",
        "cpu_cores": 32,
        "idle_ram_gb": 10.3,
        "gpu_free_vram_mib": 9715,
        "verdict": "healthy",
        "heartbeat_epoch_utc": epoch,
        "clock_read": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    })
    with open(HB, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    # post-write self-verify (R170/R178: value AND type)
    hb2 = json.load(open(HB, encoding="utf-8"))
    ep = hb2.get("heartbeat_epoch_utc")
    print("heartbeat epoch:", ep, "| isinstance(int):", isinstance(ep, int),
          "| clock_read:", hb2.get("clock_read"))


if __name__ == "__main__":
    main()
