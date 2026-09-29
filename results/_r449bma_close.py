# -*- coding: utf-8 -*-
"""r449 bm-a S5 round-report append + S7 state/heartbeat close."""
import json, time, io, sys

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

REPORT = "logs/iteration-loop/round_reports-bm-a.md"
STATE = "state-bm-a.json"
HEART = "fleet/machines/bm-a.json"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

LINE = (
    "2026-09-29 23:5x | r449 | dept:工程·舰队+研究 (风暴窗收口+死窗遗产落地) | WM verdict: 绿 "
    "(red=false lane=healthy 23:10; py tail 1.4/0.6/0.5 低位·白名单面: job_list 0+fleet tasks 零 open+"
    "pool ready=1=W11-GENERATE（bm-b T-123 道点燃面·autofill C8 归属·轮内禁代跑 per O-2100 批纪律）+"
    "bandit next_pick=claimed（moneyflow IC 等面板物理依赖）) | 当前活: S0 31-UU 风暴双轮正典解收口+"
    "r448 死窗遗产全队接线落地·最近实物: scripts/attrition_ledger_guard.py origin 落地（全队 S7 tripwire 修复·"
    "selftest 6/6+scan CLEAN·23:4x 推 7063099ef）+results/_r449bma_resolve.py（31 UU 零丢失解）·"
    "下个里程碑: W11 verdict（bm-b 在飞=T-123 泊位窗死线）→W12 冻结窗开+10-01 月界三件套（48h 内） | did: "
    "S0-1 锚 bm-a; S0 pull --rebase 撞 31 UU（r448 遗产 push 撞车批 vs bm-b r442 五连推·分类器 27+4 定性）"
    "→6 ALL_FACES merge_lane_views resolve（compute_audit 207 行 ts-union+regime/x2 union+4 snapshot take-new）"
    "+25 件 _r449bma_resolve.py（R350 硬化探针+twin 同侧耦合+js 整字节+jsonl 1787+1781→1793 行 union+"
    "CODELY memory-union 条目级双向核验 15 条零丢失）→continue 前 fetch=origin 又推进（r444 fork-point 风暴窗复现）"
    "→abort+--onto origin/main 显式重放→二轮脚本化 resolve→fork-point 恒定→continue+push 4d6b93538+"
    "reconcile 6 面 ZERO-DRIFT; S0.5 orders 122/122 零未回执+decisions=D-07 已在 prompt 生效零新动作; "
    "S1 smoke 26/26; S2 双板零 open; S3 主产出=r448 死窗遗产落地（P0 接线缺口: iteration_prompt S7 已在 origin "
    "引用 guard 而脚本本体未推=全队断腿险·r446 分离律舰队级实例）→selftest 6/6+scan CLEAN×4 账本+定向 9 件 "
    "commit 推 origin; MSG-2225 泊位窗读检（本机 r447 声明·留 inbox 供收件侧）; S4 坑律=风暴 union 复活已归档"
    "条目坑+CODELY 热冷整编（archive 去重前置=5 条复活条目删除+User 元律误删即时修复+r442/r446/r440b/r242 "
    "让位迁移=13,828→9,438B 零丢失·指针行全在位）; S6 链 37 腿=36 rc0+update_lhb rc=3 源改史旗标（EM 重述史"
    "第二次观测·本地史不动·契约原样上报） | verify: smoke 26/26; rebase 双轮解 31 UU 零丢失（19 JSON 面 parse+"
    "冲突标记零残留）; guard selftest 6/6+scan exit 0 CLEAN; CODELY 9,438B<10,240B; 心跳 epoch int 自证 | "
    "next: (1) W11 verdict watch（bm-b T-123）(2) W12 收编冻结窗开于 W11 全链落地后（seeds 20320500/20321000/"
    "20321500 三步律复验）(3) 10-01 月界三件套+REGIME_GUARD v3 hands-off (4) r450=5x HANDOVER 核查轮 "
    "(5) update_lhb 源改史慢性面 watch（披露窗守卫已挡·本地史完整）"
)

def main() -> int:
    with open(REPORT, "a", encoding="utf-8", newline="") as f:
        f.write(LINE + "\n")
    print("round report appended")

    st = json.load(open(STATE, encoding="utf-8"))
    st["round_no"] = 450
    st["did"] = ("r449: S0 31-UU storm dual-pass canonical resolve (fork-point replay per r444 law) + "
                 "r448 dead-window heritage landed origin (attrition_ledger_guard.py fleet-wide S7 wiring fix) + "
                 "CODELY storm-resurrection dedupe archival 13,828->9,438B; S6 37 legs 36 rc0 + lhb rc3 source-restated honest")
    st["verify"] = ("smoke 26/26; guard selftest 6/6 + scan CLEAN x4 ledgers; rebase zero-loss (15 CODELY entries "
                    "bidirectional verify + 19 JSON parse + jsonl 1793 union); CODELY 9,438B<10,240B; orders 122/122; epoch int")
    st["next"] = ("r450+: (a) W11 verdict watch (bm-b T-123 = W12 berth deadline); (b) W12 adoption freeze post-W11-full-chain "
                  "(seeds three-step re-verify); (c) 10-01 month trio + REGIME_GUARD v3 hands-off; (d) r450 = 5x HANDOVER check; "
                  "(e) update_lhb source-restated chronic-face watch")
    st["current_task"] = ("r449 closed: storm 31-UU dual-pass resolve + heritage landing + CODELY dedupe archival; "
                          "next = W11 verdict watch + W12 freeze window + 10-01 trio")
    st["last_round_at"] = NOW
    st["updated"] = NOW
    json.dump(st, open(STATE, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
    print("state round_no -> 450")

    h = json.load(open(HEART, encoding="utf-8"))
    h["last_seen"] = NOW
    h["clock_read"] = NOW
    ep = int(time.time())
    assert isinstance(ep, int)
    h["heartbeat_epoch_utc"] = ep
    h["current_task"] = st["current_task"]
    h["round_no"] = 449
    json.dump(h, open(HEART, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
    chk = json.load(open(HEART, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
    print("heartbeat epoch", chk["heartbeat_epoch_utc"], "int-verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
