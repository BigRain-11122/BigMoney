"""r468 bm-c round-report main-line append (bytes-safe, EOL-adaptive).
Detects the file's tail EOL convention and appends the r468 line with the
same separator (mixed-EOL history protection, r641 family)."""
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
REPORT = os.path.join(REPO, "round_reports-bm-c.md")

LINE = ("2026-10-04T12:21｜r468｜dept:工程（golden-week 值守轮·D-19 消费窗=集团回执批"
        "+D-02-03① 移植同窗收口）｜watermark verdict=绿（轮首 red=false·轮中红牌一次："
        "T-168 开票未即认领→py_low_with_work_cands=CEO 即时律水印系统按设计点名→同窗认领"
        "+移植完成→re-probe py_low_board_clear 红牌自愈·satengine rc0 活〔Tools 注册面"
        "·scripts 面 selftest 11 legs+Tools 46/46〕·N1 关面 per O-2115 sec-2）｜当前活=金周值守"
        "+D-19 消费批+D-02-03 fix① scripts 面移植同窗收口｜最近实物=HQ-FEEDBACK.md "
        "F-20261004-01（D-20261002-02/03/05/06 四行回执补呈·补呈窗 10-05 00:00 内）"
        "+scripts/saturation_engine.py（fix① 移植+selftest 第 9 腿+存量陈旧 N4 腿治愈 12→18）"
        "+results/_r468bmc_s6_log.txt（S6 38/38 rc0）｜下个里程碑=fund-trio finalize 窗 10-05 "
        "10:30 开（QUALITY 长杆 567/2000·bm-b 正主）+D-20261004-02①②③ 回执窗 10-06 00:00"
        "+开市 10-09（≤48h）｜S0: 无 rebase 残留·轮首 2 脏面=本机 satengine daemon 车道面"
        "·HEAD==origin/main 零差｜S0.5: 令差集=0（153/153 同口径零差 _r468bmc_s05_probe.py）"
        "·inbox 0·D-19 CHANGED（EB14B510→4E5BE321 raw-blob）→消费 D-20261004-03/04/05/06"
        "——05 行=本司回执补呈派工·水位键已更新 4E5BE321｜S1 smoke 48/48（裸跑复核：首跑被我"
        "自己的 Select-Object 截断管道杀半·r460 在册律自纠）｜S2 板空（job_list 0·fleet 0 "
        "open）｜S3: satengine rc0 活·FUND trio 全 bm-b 属主 healthy（watch-only·V734/Q567/"
        "D418 delta 0·claim age 11.0min·证据 _r468bmc_fundnulls_watch.json）｜核心产出①回执批: "
        "F-20261004-01——③a D-02-02 principal 单源回执 closed（r576 S4U-first 退役+本机三任务 "
        "XML InteractiveToken 实读+CEO 改判面在册）；③b D-02-03 回执=② CAS 双面+① mtime 重读"
        "双面收口+双面 selftest 绿；② D-02-06 对账行呈证=13 域分件 314,851B 逐件字节+md5"
        "（_r468bmc_d0206_recon.txt）+主件 62,651B 回弹如实+线级 16,719B·收口窗 10-07 维持；"
        "① D-02-05 selftest 呈证提前=perpetual_faces 9/9（第 9 腿 skip-semantics-pin 正反断言"
        "·_r468bmc_pf_selftest.txt）｜核心产出②T-168 移植（WM 红牌→同窗认领开动）: scripts 面 "
        "_MOD_WATCH+_mtime_stale+_refresh_family_modules（tick 首行·reload+rebind FAMILIES"
        "·mid-surgery 保视图）+selftest 第 9 腿 9 断言→scripts 面 selftest 11 legs PASS+Tools "
        "面 46/46 回归零破坏+AST rc0；连带治愈=scripts 面 selftest 存量陈旧断言（N4 队列 12"
        "〔B1+B2〕→18〔B1+B2+B3〕·B3 已注册而引擎自检腿未随更新=登记方漏更）；新坑律 1 条入 "
        "pit-engine.md（importlib.reload 按模块名经 sys.path 重找 spec·hermetic 夹具三件正法）；"
        "py_watermark re-probe=py_low_board_clear（红牌自愈实证）｜S6 38/38 rc0 NON-ZERO=none"
        "（dualrun streak 51〔367 entries〕·update_daily 金周 cutoff 2026-09-30 零新行"
        "·market_regime ORANGE shadow days=2·REPORT/LIVE 幂等再生·金周无新 bar 腿诚实 no-op）"
        "｜S7: loop pin5 在位·watchdog 在位·双爪 parity TRUE x2 零重装·attrition CLEAN（4 "
        "ledgers·2 bm-a healed 注记照录）·orders S7 二扫零差｜S4: 1 新坑律（pit-engine.md 域件面"
        "·主件零行=D-02-06 主件 ≤30KB 节律配合）｜记分: 2（F-20261004-01 回执件+T-168 移植"
        "〔claim→port→selftest 同窗〕+selftest/对账证据件+S6 管线产出=能跑能看能用实物·非空转）"
        "｜记账预算: 3/5（state+心跳+轮报·CODELY 主件零行）｜本地未达 origin commit 数: 收口 "
        "push 后 push_verify 自证（见下）｜登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作"
        "（treasure_guard 零调用面照实·五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS "
        "零新行照实）｜下轮指针=r469 值守（finalize 窗 10-05 10:30 开后进度核）+D-20261004-02"
        "①②③ 回执窗 10-06 00:00+开市 10-09 数据道恢复（新 bar 门控腿自动复挂）+下一 5x=r470")


def main():
    with open(REPORT, "rb") as f:
        raw = f.read()
    tail = raw[-400:]
    eol = b"\r\n" if b"\r\n" in tail else b"\n"
    sep = eol if raw.endswith(eol) else eol
    add = LINE.encode("utf-8")
    assert b"\x00" not in add
    with open(REPORT, "ab") as f:
        f.write(sep + add)
    with open(REPORT, "rb") as f:
        chk = f.read()
    assert chk.endswith(add), "append verify failed"
    print("REPORT_APPEND_OK eol", "CRLF" if eol == b"\r\n" else "LF",
          "bytes", len(add))


if __name__ == "__main__":
    main()
