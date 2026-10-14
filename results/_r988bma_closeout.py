# -*- coding: utf-8 -*-
# r988 bm-a closeout: state round_no 987 -> 988 + heartbeat + round report line
import json, datetime, time, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_dt = datetime.datetime.now().astimezone()
now = now_dt.isoformat(timespec="seconds")
epoch = int(time.time())

# 1) state round_no 987 -> 988
sp = os.path.join(ROOT, "state-bm-a.json")
d = json.load(open(sp, encoding="utf-8"))
prev_round = d.get("round_no", 987)
d["round_no"] = 988
json.dump(d, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 2) heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
h = json.load(open(hp, encoding="utf-8"))
h["active"] = True
h["last_seen"] = now
h["current"] = ("r988: S6 deferred data-gate legs resumed post-throttle (41-leg chain 0 bad exits, CEO faces "
                "RE-2026-10-14 + LIVE-2026-10-14 + scorecard regenerated, dualrun ZERO-DRIFT streak 22; moneyflow "
                "+AH detached refreshes in-flight) + W239 12/12 shards landed burn-complete verify, finalize NOT "
                "yet on origin -> W240 freeze watch armed (M12 chain-order) + W-line supply assessment: axis arc "
                "entry/exit/sizing/timing all burned-or-closed, 5th axis domain = BAN-05-adjacent, next legal "
                "supply = A13-style predictor extension (bm-b funnel) per supply-pivot digest")
h["current_task"] = h["current"]
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now
h["ts"] = now
h["verdict"] = ("green (red=false lane=healthy; satengine ALIVE idle queue0; W239 burn 12/12 on origin, finalize "
                "pending bm-c -> W240 freeze next window <=48h; pool 456 done 0 ready; boards both empty)")
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# epoch int self-check
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "F7: epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "F7: clock_read T-separator"

# 3) round report line
rp = os.path.join(ROOT, "round_reports-bm-a.md")
line = (
    now + " | r988 | bm-a | dept:工程/数据（S6 延迟数据腿恢复=W239 finalize 盯守窗主使命）| "
    "WM-VERDICT: green (red=false lane=healthy; satengine ALIVE rc0 idle queue0; py_low_board_clear=合法闲白名单+本轮 "
    "S6 全链恢复=实质工作) | 孤儿面=0 (round-zero probe 30 py faces 0 orphans) | "
    "S0: autostash pull --rebase ff 94136b9dd..42b6f6111 (bm-b r934/935 W19 judge-finalize lawful-zero 112 判 0 过 + "
    "bm-c r996 W239 five-face freeze splice landed + burn self-ignited 13:47; 轮首脏 8 面=本机 daemon live faces) | "
    "S0.5: orders 全差集扫描 0 未回执 (程序化 diff 88 文件 vs ack 集·README 非令件排除) + D-19 决策水位 "
    "sha256 MATCH (d9d8aa72 python-raw via C: 实径 group tree fetch+show·K 盘缺席回退本机实径 D-20261004-02③) 零动作 | "
    "S1: smoke 49/49 PASS | "
    "S3: 优先序全扫=水位红牌 false+bandit 指针空+引擎活 rc0+池 456 全 done 0 ready+任务板 0 open 票+tech/explore 双板 "
    "fully consumed (r987 CLEAR 承面) | **W239 烧录验证 12/12 分片全落 origin（n1_w239/shard-0..11）+ finalize 产品 "
    "absent=W240 freeze 链序保持 waits-upstream，watch armed（W239 finalize 落地窗=W240 五面拼接窗 ≤48h）** | "
    "W 线供给评估（TRIAL_LABOR §1 常供律触发面如实记录）: W19 timing-axis judged lawful-zero 13:49 落地=轴系四轴 "
    "(入场 W1-16/出场 W17/仓位 W18/时机 W19) 全烧毕；第五轴 域=BAN-05 毗邻面（市场级情绪择时族级闭合 LHB_THERMO "
    "0/12+THERMO_OVERLAY 0/6 双判负档+A9/A10 政体门用法关闭）+ zt_pool 前向史 2026-10-08 起<12 个月冻结律=域轴 "
    "本窗无合法新数据源重开通道；下一合法供给=A13 式预测器扩展批（f_c2v4/f_mp1 掩码均值 vs fwd20 IC·supply-pivot "
    "digest §二裁定·bm-b 漏斗在飞）——本窗零起草零抢跑（协同反重复铁律）| "
    "S6: r987 延迟数据腿全恢复=41 腿链 detached PID 45388 完整落盘 (14:05-14:09, 非 0/1 出口=0): dualrun "
    "ZERO-DRIFT streak 22 (456 entries) + compute_audit zero-flags + py_watermark rc0 + update_daily "
    "intraday no-op + lhb/zt_pool/futures/repo no-op cutoff 10-13 覆盖 + heat 15:30 前窗 no-op + **moneyflow "
    "spawned detached refresh (panel first-pull 面在飞=r977 已知 EM 阻断面自愈循环)** + sina_mf no-op (cutoff "
    "10-09-24 滚动窗内) + ths_panel 窗保守阻断 (intraday) + **ah_panel spawned detached refresh** + fundamental "
    "fresh + fund_stmt no-op + 纸盘族 cutoff 10-13 幂等 no-op (bars 15:30 后落) + CEO 面四件再生 "
    "(daily_scorecard 6 traders / REPORT-2026-10-14 faces=5 / LIVE-2026-10-14 ORANGE / build_status) + token "
    "L2 delta flat | "
    "S7: schtasks 四件套=loop pin 14:08 next-fire + watchdog present + 双爪在位 (r987 承面) + post_review "
    "10995 行尾 6 全 YES 零 ✗ + idle_trigger --worked (idle_rounds 2->0) | "
    "最近实物: results/_r988bma_s6_chain.log (41 legs 0 bad, 14:09) + docs/daily_report/REPORT-2026-10-14.md + "
    "docs/live_usage/LIVE-2026-10-14.md (14:06-14:09 再生) | "
    "下个里程碑: W239 finalize (bm-c 下 1-2 轮) -> W240 five-face freeze (r984 血统 derive_editor 滚代, 窗≤48h); "
    "moneyflow/AH 分离刷新回执下轮吸收; 15:30 bars 后 marks 链 (REGIME_GUARD enforce+live.paper+t35/t24 族) 由 "
    "后续轮承接 | "
    "本轮产品积分: 2 (S6 全链 41 腿=能跑/能看 CEO 面实物 + W239 烧录验证=供给链推进) | 记账预算: 4 (state+心跳+"
    "轮报告+S6 链件) | 本地未达 origin commit 数=0 (push+fetch+rev-list 自证随收尾) | token: L1 零 API (token_meter "
    "delta flat)"
)
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + line + "\n")

print("closeout done: round 988, epoch", epoch, "prev", prev_round)
