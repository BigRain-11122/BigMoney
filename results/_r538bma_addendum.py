# -*- coding: utf-8 -*-
# r538 bm-a addendum: CEO orders O-20261001-2103/2106 receipt (S0.5 second-scan catch) + state refresh
import json, time, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')

# --- heartbeat orders_ack (append two new orders, keep list intact) ---
hp = r'fleet\machines\bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
ack = h.setdefault('orders_ack', [])
for oid in ['O-20261001-2103-bm-a.md', 'O-20261001-2106-bm-a.md']:
    if oid not in ack:
        ack.append(oid)
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = iso
h['last_seen'] = iso
h['current_task'] = 'r538 closed: W24 finalize chain-linear 417,348 + town org_chart v2 alignment; CEO 2103/2106 acked (R1 research-wave tickets pending GM dispatch, claim-on-open next round)'
h['verdict'] = ('healthy: r538 W24 finalize one-pass closed loop (ledger 415,148+2,200=417,348 chain-linear, K=50,720, S5 4/4, S7/S8 backfilled, selftest+attrition green) '
                '+ town.html org_chart v2 alignment closure + rerun-doublecount pit caught/fixed (finalize rerun counts own uncommitted output into prev); '
                'CEO O-2103/O-2106 T1 research orders received-acked, execution starts on GM-dispatched tickets (claim same round); W26 frozen by bm-c (W27=bm-a seat waits); S6 28 legs rc0')
assert isinstance(h['heartbeat_epoch_utc'], int)
out = json.dumps(h, ensure_ascii=False, indent=1)
open(hp, 'w', encoding='utf-8', newline='').write(out)
print('heartbeat ack updated:', ack[-2:])

# --- state refresh (did/next reflect W24 closure + CEO orders) ---
sp = r'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
st['did'] = ('r538: W24 finalize one-pass same-round closed loop (12/12 tick-burned, K=50,720 exact, S5 4/4 PASS, ledger 415,148+2,200=417,348 chain-linear prev=W23 r335 live head, '
             'S7/S8 backfill + post-backfill selftest green + attrition CLEAN; rerun-doublecount pit: finalize rerun counted own uncommitted output into prev, caught+fixed delete-rerun) '
             '+ town.html org_chart v2 alignment closure (alloc bldg re-anchored, gate 10/10 + Edge render) + S6 28 legs rc0 + 18-UU rebase storm resolved per skill (bm-c r334) '
             '+ CEO O-2103/O-2106 receipts (T1 research program acked)')
st['verify'] = ('W24: finalize rc0 + null_pool_cumulative pre 48,520 + w24 2,200 = merged 50,720 + skill_line 1.1505->1.1515 @n_eff 415,148 + audit.machine=bm-a + '
                'selftest PASS post-backfill + attrition CLEAN; town: align gate 10/10 + node --check rc0 + Edge dump-dom new-name x5/old-name x0; smoke 47/47; dualrun streak 14')
st['next'] = ('CEO O-2103 (theme methodology five-phase) + O-2106 (battle-tactic field test report, first 3-5 in 48-72h) = research dept top queue: claim GM-dispatched R-tickets same round on open; '
              'W25 finalize=bm-b seat in flight; W27 freeze=bm-a seat waits W26 (frozen by bm-c r335, band-skip both tails); T-140/T-142/W14-GENERATE stay GM-ruled')
st['current_task'] = h['current_task']
st['updated'] = iso
st['last_round_at'] = iso
out = json.dumps(st, ensure_ascii=False, indent=1)
open(sp, 'w', encoding='utf-8', newline='').write(out)
print('state updated')

# --- round report addendum line ---
line = ('%s | r538 补记（push addendum+CEO 令回执）| dept:研究+工程 | 实物2=W24 finalize 同窗闭环：12/12 tick 烧录·K=50,720 预期精确·S5 4/4 PASS（mu-drift +0.00042/sigma +0.045%%/A p95 0.3329/K-lift +0.0010）'
        '·账本 415,148+2,200=417,348 链线性（prev=W23 r335 bm-c 活头 derive）·§7/§8 回填+post-backfill selftest 绿+attrition CLEAN；坑律实弹=finalize 重跑把未 commit 自产件计入 prev（ledger prev derive 扫文件集非幂等）'
        '→删件重跑复原正头·事故件留档 _r538bma_w24_finalize_RERUN_DOUBLECOUNT.log | CEO O-2026103/2106 两令收讫（题材战法方法论 T1 大立项+实测律）：研究部顶队列·GM 开票即同轮认领（R1 外源扫描/R3 普查批先动）·48-72h 首批 3-5 战法实测汇报 | '
        '下轮：R 票认领开动；W27 冻结候 bm-c W26 已落表；W25 finalize=bm-b 在途\n') % iso
with open(r'round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('round report addendum appended')
