# -*- coding: utf-8 -*-
"""r438 bm-c wrap: state round_no++ + round report append + heartbeat refresh.
Template: r437 closeout pattern (python JSON channel, PS-domain-pit-free).
Usage: python results/_r438bmc_wrap.py
"""
import datetime
import json
import os

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now = datetime.datetime.now().astimezone()
TS = now.isoformat(timespec='seconds')            # 2026-10-04T01:5X:XX+08:00
EPOCH = int(now.timestamp())                       # int, smoke F7 law
STATE = os.path.join(REPO, 'state-bm-c.json')
REPORT = os.path.join(REPO, 'round_reports-bm-c.md')
HEART = os.path.join(REPO, 'fleet', 'machines', 'bm-c.json')

DID = ("r438 bm-c (等待态轮·W2 判决批在飞=合法等待面): WM 绿（red=false lane healthy·py_watermark "
       "verdict=py_low_with_work_cands n=2·§四白名单成立=唯一在飞 W2 finalize 单线真烧〔pid 31336·CPU 累积 "
       "7975s≈spawn 23:34 后 2h13m 单核满载·psutil+Get-Process 双证非挂死〕+N1 本地队列烧空〔waves 2-115 全 "
       "12/12·queue_next 空〕+板空〔fleet tasks 164 票 0 open·job_list 空·bandit 0〕+黄金周周日零新 bar——W2 "
       "落地即恢复下一波供给）。(1) S0 零手术：fetch 后 0/0 干净基座（轮首脏面=本机 daemon 4 再生成快照+W2 烧日志 "
       "untracked·与 origin 在途改动集交集空）；S0.5 orders 152/152 程序化差集零差（轮首+S7 双扫零新令）；D-19 "
       "EB14B510 MATCH+GORDERS 68947C17 MATCH 双水位零消费。(2) S1 smoke 47/47 首跑全绿零修复；satengine rc0 活"
       "（alive_flag·age 13s·queue_next 空=烧空如实）。(3) S6 全链 37/37 rc0 NON-ZERO=none（_r438bmc_s6_log.txt·"
       "adapt→run→restore r429 三段律〔canon driver _r428bmc_s6.py HEAD blob 复原 status clean〕·dualrun "
       "ZERO-DRIFT streak 40·五 lane_io 面 stale-takeover derive 合法〔bm-a 心跳 64min 陈旧·O-2100 s2.4 STALE_MIN "
       "law〕·周末+国庆采集腿诚实 no-op 族·update_lhb 30min 节流 no-op·主产出=docs/daily_report/REPORT-2026-10-04."
       "md/.json+docs/live_usage/LIVE-2026-10-04.md/.json（state=ORANGE 仓位帽 50%）+results/strategy_scorecard.json "
       "52s 重算+CALL-2026-09-30 ORANGE_COOL sleeves=4 activated=0）。(4) W2 poll：pid 31336 活·CPU 7975s 实证真烧"
       "·w2_judge.json 未落·deadline <=10-06 维持（4.5h 静默死灭门线未触）·烧日志 _r426bmc_w2_judge_finalize_log."
       "txt 本轮纳入 commit（r437 遗漏补收）。(5) post_review 复核：REPORT-20261004.md 现态 ✓44/✗0/🟡5——MSG-0030 "
       "载荷 7 ✗ 历史 backfill 批=r437 已修毕·本轮零新 P0；MSG-0030 本体=bm-b→bm-a 总控件留置非本司。(6) S7：四件套在位"
       "（loop pin=5 零漂移 no-op first-fire 01:55·watchdog 重注册 first-fire 01:54·双 claw 重装 LF 归一）+attrition "
       "CLEAN rc0（4 台账文件·2 healed 注记照录）。五收口步捕获问：无判决 finalize/族炉收口/考面冻结/名单进出/方法论"
       "新方法→TREASURE_REGISTRY 零新行+METHODOLOGY_ASSETS 零行照实；登记簿零命中断言=本轮删除/清扫/归档类动作 0 起"
       "（treasure_guard prescan 未触发=零删除面）。本地未达 origin commit 数=0（push_verify 实证）。")

VERIFY = ("S6 37/37 rc0 NON-ZERO=none (_r438bmc_s6_log.txt; dualrun streak 40; canon driver restored clean); "
          "smoke 47/47; orders 152/152 double-scan zero-diff (programmatic); D-19 EB14B510 MATCH + GORDERS "
          "68947C17 MATCH; satengine alive rc0 (queue exhausted honest); W2 pid 31336 alive CPU 7975s burning "
          "evidence; post_review 0 red rows (44 YES/0 NO/5 WAIT); attrition CLEAN rc0; S7 4/4 (loop pin=5 "
          "no-drift; watchdog+claws reinstalled); epoch int + clock T-sep in-wrap")

NEXT = ("(a) W2 poll: python Tools/_r426bmc_w2_judge_finalize.py status -> w2_judge.json 落地即收养 (adapt "
        "_r426bmc_close.py 模板, count->replace->assert 三段律 + 幂等 no-op check + 烧日志原子 commit, deadline "
        "<=10-06); pid 31336 静默死判定=4.5h 窗 (04:04 后零 log 进展+CPU 停增) -> 确定性灭门升级呈报 (防再烧三连浪"
        "费); W2 落地=N1 供给线重开 + 首个判决-finalize 捕获点样例 (10-08 验收包); (b) O-2030 验收证据包 10-08 (weld "
        "face complete r434 + demo receipts r432/433/434 + W2 landing 样例); (c) D-06 全线收口 10-07 (pit-git "
        "107KB sub-split + pit-data CRLF 裁定 + 流水下沉终扫); (d) T-143 月考装配窗 10-09 后 (交付 10-29); (e) W2 "
        "落地后 N1 供给重开观察——落地后仍 py_low 零点火=引擎供给链 P0 呈报 GM。")

REPORT_LINE = "\t| ".join([
    TS,
    "r438 bm-c",
    DID,
    VERIFY,
    "下轮指针: " + NEXT,
]) + "\n"

ARTIFACT = ("results/_r438bmc_s6_log.txt (37/37 rc0, dualrun ZERO-DRIFT streak 40) + docs/daily_report/"
            "REPORT-2026-10-04.md/.json + docs/live_usage/LIVE-2026-10-04.md/.json + results/"
            "strategy_scorecard.json (52s re-derive) @ " + TS)


def main():
    # 1) state-bm-c.json
    with open(STATE, 'r', encoding='utf-8') as f:
        st = json.load(f)
    assert st['machine_id'] == 'bm-c' and st['round_no'] == 437, \
        'identity/round anchor mismatch: %s/%r' % (st.get('machine_id'), st.get('round_no'))
    st['round_no'] = 438
    st['clock_read'] = TS
    st['cpu_pct'] = 5.4
    st['current_task'] = ("r438 closeout done (S6 37/37 + W2 poll alive-burning + orders/D19/GORDERS all MATCH "
                          "zero-new); next: W2 landing adoption / O-2030 evidence pack 10-08 / D-06 closure 10-07")
    st['did'] = DID
    st['gpu_free_vram_mib'] = 14358
    st['heartbeat_epoch_utc'] = EPOCH
    st['idle_ram_gb'] = 9.6
    st['last_decisions_read_at'] = TS
    st['last_round'] = ("r438 bm-c: waiting-state round (S6 37/37 rc0 chain, CEO faces daily report + live usage + "
                        "scorecard refreshed; W2 judge burn alive CPU 7975s verified; orders/D19/GORDERS all "
                        "MATCH zero-new; smoke 47/47; post_review 0 red rows; attrition CLEAN)")
    st['last_round_at'] = TS
    st['last_round_ts'] = TS
    st['last_seen'] = TS
    st['last_ts'] = TS
    st['updated'] = TS
    st['updated_at'] = TS
    st['next'] = NEXT
    st['verify'] = VERIFY
    with open(STATE, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
        f.write('\n')

    # 2) round report append (file ends with newline per r437 entry)
    with open(REPORT, 'r', encoding='utf-8') as f:
        rep = f.read()
    if not rep.endswith('\n'):
        rep += '\n'
    rep += REPORT_LINE
    with open(REPORT, 'w', encoding='utf-8', newline='') as f:
        f.write(rep)

    # 3) heartbeat fleet/machines/bm-c.json
    with open(HEART, 'r', encoding='utf-8') as f:
        hb = json.load(f)
    assert hb['machine_id'] == 'bm-c' and hb['round_no'] == 437, 'heartbeat anchor mismatch'
    hb['round_no'] = 438
    hb['activity_now'] = ("r438: waiting-state round delivered (S6 37/37 rc0 full chain; CEO faces: daily report + "
                          "live usage + scorecard refreshed; W2 judge burn verified alive and CPU-accumulating)")
    hb['clock_read'] = TS
    hb['cpu_pct'] = 5.4
    hb['cpu_util_pct'] = 5.4
    hb['cpu_idle_pct'] = 94.6
    hb['free_ram_gb'] = 9.6
    hb['ram_free_gb'] = 9.6
    hb['idle_ram_gb'] = 9.6
    for k in ('gpu_free_vram_mb', 'gpu_free_vram_mib', 'gpu_idle_vram_mb', 'gpu_idle_vram_mib', 'gpu_vram_free_mb', 'gpu_free_mb'):
        hb[k] = 14358
    hb['heartbeat_epoch_utc'] = EPOCH
    hb['health'] = 'ok'
    hb['verdict'] = 'healthy'
    hb['last_seen'] = TS
    hb['last_seen_at'] = TS
    hb['updated_at'] = TS
    hb['current_task'] = ("r438 closeout done; W2 judge-finalize burn in flight (pid 31336, alive, CPU 7975s "
                           "accumulated, artifact absent, deadline <=10-06); next: W2 adopt-at-landing + O-2030 "
                           "evidence pack + D-06 closure")
    hb['latest_artifact'] = ARTIFACT
    hb['next_milestone'] = ("W2 w2_judge.json landing -> adoption same round (deadline <=10-06, first "
                            "judge-finalize capture-point example); O-2030 acceptance evidence pack 10-08; D-06 "
                            "full closure 10-07 (pit-git sub-split + pit-data CRLF + flow down-migration); T-143 "
                            "monthly-exam assembly post-10-09 (deliver 10-29)")
    hb['prod_lanes'] = ("O-2030 weld face complete (r432-434, on origin); MASS_TRIAL_W2-JUDGE finalize burn in "
                        "flight (pid 31336 alive CPU-accumulating, artifact absent, deadline <=10-06, log "
                        "committed r438); push_verify single-source IN SERVICE; N1 local queue exhausted (waves "
                        "<=115 done) -- next-wave supply gated on W2 landing")
    with open(HEART, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
        f.write('\n')

    # self-verify: reload all three, assert int epoch + T-sep clock + round_no
    st2 = json.load(open(STATE, encoding='utf-8'))
    hb2 = json.load(open(HEART, encoding='utf-8'))
    assert isinstance(st2['heartbeat_epoch_utc'], int) and isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
    assert 'T' in st2['clock_read'] and 'T' in hb2['clock_read'], 'clock must be T-separated'
    assert st2['round_no'] == 438 and hb2['round_no'] == 438, 'round_no must be 438'
    assert len(open(REPORT, encoding='utf-8').read().splitlines()) > 100, 'report append sanity'
    print('WRAP OK: state/round_no=438, report line appended, heartbeat refreshed, epoch=%d int, clock=%s T-sep'
          % (EPOCH, TS))


if __name__ == '__main__':
    main()
