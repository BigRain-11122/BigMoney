# -*- coding: utf-8 -*-
# r877 bm-c closeout: heartbeat + state + round-report line (S5/S7)
import io
import json
import time
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
ISO = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())
RAM_FREE = 3.1
VRAM_FREE_MIB = 2914

CT = ('当前活: W17 judge-finalize 在飞守望(PID 20012 CPU 12459s 推进·out 未落)+W209 M10 冻结链守望(cron 9defca39 armed) | '
      '最近实物: P0 切片二双武器主场验证落地(scripts/regime_p0_slice2.py selftest 11/11·P0-SLICE2-DIPREBOUND-THEME-20261011.json·'
      'dip_rebound BEAR 主场失守 12m中位-3.1%/x2 -9.0% vs CHOP +3.67% 达标·theme TJ-FULL BULL 主场成立 +3.69%/集超BH 57.5%)@ '
      + ISO + ' | 下个里程碑: W17 finalize 落地→intake+捕获三问收口(落地轮)+10-16 P0 白话报告底料两切片合并(窗内)')

VERDICT = ('r877 bm-c: S0-1 anchor+probe(5 faces/1 orphan=ComfyUI standing face 只读) + S0 up-to-date + S0.5 双水位零增量(ORD/DEC '
           'delta false·unacked 0) + S1 smoke 49/49 + S2 boards clear(jobs 0/tasks open 0/satengine alive queue_next=[]) + '
           'PRODUCT=P0 切片二(超跌反弹淬炼版日流已定位接线=DECISION_CHAIN_V2_P1 sleeve-daily-series FY_BG_TP8·BEAR 自declared 主场 '
           '证伪 gate_off/CHOP 才是正主场 +3.67% 达标;题材波骑 TJ-FULL BULL 主场成立 +3.69%/集·SOLO 层全负·TJ2 近随机=消费面只认 '
           'FULL 层口径) + S6 43 腿 42 rc0+strategy_scorecard 瞬态(paper JSON mid-write read race·直跑复绿 rc0·bm-a stale 999min '
           'takeover derive 合法 O-2100 s2.4) + W17 watch(PID 20012 CPU 6686->12459s 推进·out 未落·closeout 顺延落地轮) + '
           'S7: attrition 4 CLEAN + loop pin=5 no-op + watchdog 重注册 + 双爪安装')

NEXT = ('r878: (1) W17 finalize 落地检查->intake->selftest->attrition->ledger prev 对账->捕获三问收口(落地轮); '
        '(2) W209 M10 自动冻结链守望+备份 cron 9defca39; (3) P0 剩余面=四资产核心仓重放腿(外部配置·需重放非重切)+'
        '防御族六员/SYSTEM-V1 前向 marks 积累中(12m 窗不可开如实); (4) 10-16 P0 白话报告底料=切片一(fund 三族)+切片二(双武器)合并; '
        '(5) E16 分片 bm-b 域观测·W209 链外零动作')

DID = ('r877 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=5 orphans=1 (ComfyUI 8188 idle standing face, '
       'read-only per precedent); S0 pull up-to-date zero delta; (2) S0.5 dual watermark consumed: ORD/DEC delta FALSE '
       '(probe rc0), unacked 0 (68 orders); (3) S1 smoke 49/49; S2 boards CLEAR (job 0, tasks open 0, queue heads not '
       'probed=board empty), satengine alive rc0 queue_next=[] (W209 upstream face); idle NOT GREEN (RAM 36.2%<40% at '
       'probe, now 87% loaded by W17) no claim obligation, idle_rounds=0; (4) inbox MSG-20261011-0940-bmb addressed to '
       'bm-a -> left for addressee (T-184 non-party); (5) PRODUCT = P0 matrix slice TWO (O-1725 sec.2 zero-burn, declared-'
       'weapon home-ground verification): scripts/regime_p0_slice2.py (selftest 11/11, v1 import reuse law) + results/'
       'regime_style_matrix/P0-SLICE2-DIPREBOUND-THEME-20261011.json + P0_MATRIX_SLICE_V1.md sec.5 + E59 method card. '
       'Headlines: dip_rebound FY_BG_TP8 (located stream = DECISION_CHAIN_V2_P1 sleeve-daily-series, supersedes slice-v1 '
       'sec.4 no-stream claim): CHOP 12m median +3.67% floor-beat PASS vs BEAR (declared home) -3.10% x1/-9.04% x2 '
       'gate_off advice -> scheduling prereg must confront style-matrix BEAR 0.20 weight premise; theme TJ-FULL BULL home '
       'HOLDS (median +3.69%/episode, beat-BH 57.5%, n=292) while TJ-SOLO all-negative and TJ2 near-random -> consumption '
       'face = FULL stratum only; (6) S6 43 legs: 42 rc0 + strategy_scorecard transient rc1 (paper JSON mid-write read '
       'race; full rescan of paper faces 0 bad; direct re-run rc=0 green 83.7s, bm-a stale-takeover derive legal per '
       'O-2100 s2.4 STALE_MIN 999min; disclosed honestly); py_watermark verdict=insufficient_history (15min window, '
       'honest); (7) W17 watch: finalize PID 20012 cmdline-verified alive, CPU 6686s->12459s advancing, output not '
       'landed, closeout chain deferred to landing round; W209 freeze chain armed (M10 + cron 9defca39 alive in session); '
       '(8) S7: attrition 4 ledgers CLEAN (2 healed notes) + loop task pin=5 no-op + watchdog re-registered + pre-commit/'
       'pre-push claws installed + this books commit/push delivery self-proof.')


def update_json(path, updates):
    with io.open(path, 'r', encoding='utf-8') as fh:
        d = json.load(fh)
    d.update(updates)
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    with io.open(tmp, 'r', encoding='utf-8') as fh:
        json.load(fh)  # parse verify
    import os
    os.replace(tmp, path)
    return d


# 1) heartbeat
hb_updates = {
    'last_seen': ISO, 'ts': ISO, 'updated': ISO, 'updated_at': ISO,
    'current_task': CT, 'current_task_at': ISO, 'current_task_ts': ISO,
    'free_ram_gb': RAM_FREE, 'idle_ram_gb': RAM_FREE, 'ram_free_gb': RAM_FREE,
    'gpu_free_vram_mib': VRAM_FREE_MIB, 'gpu_free_vram_mb': VRAM_FREE_MIB,
    'gpu_idle_vram_mib': VRAM_FREE_MIB, 'gpu_idle_vram_mb': VRAM_FREE_MIB,
    'gpu_idle_mib': VRAM_FREE_MIB, 'gpu_idle_mb': VRAM_FREE_MIB,
    'gpu_vram_free_mb': VRAM_FREE_MIB, 'gpu_free_mib': VRAM_FREE_MIB,
    'gpu_free_mb': VRAM_FREE_MIB,
    'idle_rounds': 0, 'agenda_starved': False,
    'heartbeat_epoch_utc': EPOCH,
    'clock_read': ISO,
    'round_no': 877, 'round_no_label': 'r877',
    'verdict': VERDICT, 'did': DID,
}
hb = update_json(r'fleet\machines\bm-c.json', hb_updates)
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in hb['clock_read'], 'clock_read must use T separator'

# 2) state
st_updates = {
    'round_no': 877, 'round_no_label': 'r877',
    'last_round': 877, 'last_round_at': ISO, 'last_round_ts': ISO,
    'last_round_closed': ISO,
    'current_task': CT, 'current_task_at': ISO, 'current_task_ts': ISO,
    'note': ('r877 closed: P0 slice TWO landed (dip_rebound BEAR home FAILS / CHOP passes; theme TJ-FULL BULL home '
             'HOLDS, SOLO/TJ2 weak) + S6 43 legs 42 rc0 + 1 transient re-run green + W17 finalize still in flight '
             '(PID 20012 advancing, closeout deferred) + W209 M10 armed; idle_rounds=0.'),
    'next': NEXT, 'next_pointer': NEXT,
    'next_milestone': 'r878: W17 finalize closeout chain + W209 M10 watch + 10-16 P0 plain-report material merge',
    'did': DID, 'verdict': VERDICT, 'last_round_summary': VERDICT,
    'last_artifact': ('P0-SLICE2-DIPREBOUND-THEME-20261011.json + scripts/regime_p0_slice2.py (selftest 11/11) + '
                      'round_reports-bm-c.md r877 line'),
    'recent_artifact': ('P0-SLICE2-DIPREBOUND-THEME-20261011.json + scripts/regime_p0_slice2.py (selftest 11/11) + '
                        'round_reports-bm-c.md r877 line'),
    'latest_artifact': ('P0-SLICE2-DIPREBOUND-THEME-20261011.json + scripts/regime_p0_slice2.py (selftest 11/11) + '
                        'round_reports-bm-c.md r877 line'),
    'free_ram_gb': RAM_FREE, 'idle_ram_gb': RAM_FREE, 'ram_free_gb': RAM_FREE,
    'orphan_face': 1, 'orphan_faces': 1,
    'idle_rounds': 0, 'agenda_starved': False,
    'last_seen': ISO, 'ts': ISO, 'updated': ISO, 'clock_read': ISO,
}
d19 = None
with io.open(r'state-bm-c.json', 'r', encoding='utf-8') as fh:
    st = json.load(fh)
d19 = st.get('d19_watermark_guard') or {}
d19['round_ref'] = 877
d19['ts'] = ISO
st_updates['d19_watermark_guard'] = d19
st = update_json(r'state-bm-c.json', st_updates)

# 3) round report line
LINE_TPL = ('{ts} | r877 bm-c | dept:研究(P0 矩阵切片二·O-1725 §2 零烧)——超跌反弹淬炼版日流定位接线'
            '(DECISION_CHAIN_V2_P1 sleeve-daily-series FY_BG_TP8·切片一 §4 无流宣判当场推翻→E59 教训卡)+'
            '题材波骑事件窗归因(点火日政体分桶·恐慌优先)——头条: dip_rebound BEAR 自declared 主场证伪'
            '(12m 中位 x1 -3.10%/x2 -9.04%·gate_off·正份额 34%/25%)·CHOP 才是正主场(+3.67% 达标·正份额 76.5%)·'
            'theme TJ-FULL BULL 主场成立(+3.69%/集·超 BH 57.5%·n=292)·TJ-SOLO 全负·TJ2 近随机=消费面只认 FULL 层 | '
            '验证证据=scripts/regime_p0_slice2.py selftest 11/11+P0-SLICE2-DIPREBOUND-THEME-20261011.json(全跨度 stats '
            '对账门过·日历恒等门 3284 复验)+S6 43 腿 42 rc0+strategy_scorecard 瞬态复绿(paper JSON mid-write·直跑 rc0·'
            'bm-a stale 999min takeover 合法 O-2100 s2.4)+smoke 49/49+attrition 4 CLEAN+W17 PID 20012 CPU 6686→12459s '
            '推进 out 未落 | 下轮指针=' + NEXT + ' | 本地未达 origin commit 数=0(收尾自证)')
with io.open(r'logs\iteration-loop\round_reports-bm-c.md', 'a', encoding='utf-8', newline='') as fh:
    fh.write('\n' + LINE_TPL.format(ts=ISO) + '\n')

print('closeout books OK:', ISO, 'epoch', EPOCH)
