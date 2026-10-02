# -*- coding: utf-8 -*-
# r400 bm-c bookkeeping (r610 idempotent order: products first, state
# bump LAST; R262 strftime all-% template; R170/R178 epoch int law).
import json
import os
import time
from datetime import datetime

ROOT = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)

now = datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')          # 2026-10-03THH:MM:SS+08:00
hms = now.strftime('%Y-%m-%d %H:%M:%S')           # r262: every field %-led
epoch = int(time.time())

REPORT_LINE = (
    hms + ' | r400 | dept:工程 | r399 猝死收口恢复轮首动作（r381 律）：WIP 58 件定向收编 commit 3e60e65ea→rebase 13 冲突'
    '（12 共享 derive 聚合面 origin 侧让路+S6 本轮再 derive 零损·CODELY.md union 保 r610 bm-a 行+本机域指针注记）'
    '→push 被拒一轮→pull --rebase 二连→164737489 直达+fetch/ls-tree 送达自证 PASS；T-152 交付三件上 origin'
    '（quality_faces.parquet 306,414 行 sha256=ef35c733..+sender manifest+MSG-0610 回执·PASS 7/7·bm-b 到货链解锁）'
    '｜S3 主产：MSG-0612 提案②落地=pre-push 爪池 claim 单调门（Tools/git_claw.py pool_claim_regressions+'
    '_pool_owner_since_map+check_push 接线·单源 hook/daemon 双通道免重装·selftest 15→23 腿 ALL PASS·'
    '实弹 fast-pass rc0·连带坑修=git show 缺失 path 双形态 stderr 判据·入 pit-git.md 域件 post-split direct-write）'
    '+T-144 票 done 行（JSON 手术引号吞噬当场自愈）｜S1 smoke 47/47；S6 37/37 ALL-RC0（分离链 _r400bmc_s6_chain.py·'
    'r324 律·dualrun ZERO-DRIFT streak 7/3·scorecard/build_status=origin-fresh veto 合法〔bm-a 心跳 14min〕·'
    'ORANGE_COOL cap50% 面新鲜）；attrition 4 账本 CLEAN；D-19 4167B784 不变零动作；orders 151/151 双扫零未回执；'
    'MSG-0612 处理完移 processed（提案②本轮落地=回执本体）；sat-engine rc0 活（常驻 run 形态·tick 任务面缺位披露：'
    '双实例坑〔pit-engine r585 域〕风险下按 r576 no-proactive-re-registration 先例不注册·watchdog 兜底）；'
    'watermark 绿（黄金周无新 bar·moneyflow IC advisory=claimed·前置面板 source-blocked 30min 自愈观察）'
    '｜S2 job_list 空｜双爪 CR 归一 MATCH·pre-commit/pre-push 在位｜下轮指针：(a) T-144(c) engine/pool/data/protocol '
    '增量回扫+流水下沉 due 10-07；(b) T-152 bm-b 到货链跟踪（10-09 开市窗 probe→prereg→池）；'
    '(c) moneyflow IC advisory 面板完备观察｜本地未达 origin commit 数=收口 push 后自证回填'
)

VERIFY = (
    'smoke 47/47 rc0; S6 37/37 ALL-RC0 (reconcile ZERO-DRIFT streak 7/3; golden-week data legs legal no-ops; '
    'ORANGE_COOL cap 50% face fresh); claw selftest 23/23; attrition 4 ledgers CLEAN; D-19 4167B784 unchanged zero action; '
    'orders 151/151 double-scan zero unacked; sat-engine rc0 alive (resident-run form, tick-task absent disclosed, '
    'watchdog coverage); watermark GREEN (golden week no-new-bar, moneyflow IC advisory claimed/pending panel)'
)

DID = (
    'r400: (1) recovery closeout of r399 (died pre-commit): 58-file WIP adopted byte-identical as commit 3e60e65ea, '
    'rebased over origin +3 with 13 conflicts resolved (12 shared derive aggregates -> origin side per yield law, '
    'CODELY.md manual union keeping r610 bm-a line + r399 pointer note), second push rejected then pull --rebase '
    'rerun -> 164737489 delivered + self-verified; T-152 three deliverables now ON ORIGIN (quality_faces.parquet '
    '306,414 rows + manifest + MSG-0610 receipt, PASS 7/7). (2) MSG-0612 proposal-2 LANDED: pre-push claw pool '
    'claim monotonicity gate (Tools/git_claw.py: pool_claim_regressions + _pool_owner_since_map + check_push wiring, '
    'hook+daemon inherit via single source, selftest 15->23 ALL PASS, live-fire fast-pass rc0, +1 new git-domain pit '
    'direct-write: git-show missing-path dual-form stderr). (3) T-144 ticket done-line appended. (4) S6 r400 chain '
    '37/37 ALL-RC0, dualrun streak 7/3.'
)

NEXT = (
    '(a) T-144(c) remaining domain increment sweeps: engine/pool/data/protocol batches + flow-sinking, D-06 full '
    'closure 10-07; (b) T-152 bm-b intake-chain tracking (probe -> prereg -> pool registration, 10-09 pre-market '
    'window); (c) moneyflow IC reference batch advisory (panel source-blocked, 30-min self-heal observation)'
)

# --- products first ---
# heartbeat (fleet/machines/bm-c.json)
hb_path = os.path.join('fleet', 'machines', 'bm-c.json')
with open(hb_path, encoding='utf-8') as fh:
    hb = json.load(fh)
hb.update({
    'round_no': 400,
    'last_seen': hms,
    'last_seen_at': hms,
    'updated_at': iso,
    'clock_read': iso,
    'heartbeat_epoch_utc': epoch,
    'cpu_pct': 8.6,
    'cpu_util_pct': 8.6,
    'cpu_idle_pct': 91.4,
    'cpu_cores': 32,
    'idle_ram_gb': 3.5,
    'ram_free_gb': 3.5,
    'free_ram_gb': 3.5,
    'gpu_idle_vram_mb': 886,
    'gpu_idle_vram_mib': 886,
    'gpu_free_vram_mb': 886,
    'gpu_free_vram_mib': 886,
    'current_task': 'r400 closeout: MSG-0612 pool-claim claw gate delivered + r399 recovery closeout pushed',
    'activity_now': 'r400 closeout: bookkeeping + commit push',
    'prod_lanes': 'r400: r399 WIP recovery-closeout pushed (T-152 deliverables ON ORIGIN); MSG-0612 proposal-2 '
                  'pool-claim monotonicity claw gate (selftest 23/23, live-fire rc0); S6 37/37 rc0; smoke 47/47',
    'latest_artifact': 'Tools/git_claw.py pool-claim gate (23/23 selftest, live-fire rc0) + T-152 quality_faces.parquet '
                       'ON ORIGIN (306,414 rows, sha256 ef35c733..) + results/_r400bmc_s6_log.txt (37/37 ALL-RC0) @ ' + hms,
    'next_milestone': 'T-144(c) D-06 full closure 10-07 (engine/pool/data/protocol increment sweeps + flow-sinking); '
                      'T-152 bm-b intake chain to pool ignition 10-09 pre-market',
    'verdict': 'r400: recovery round -- r399 closeout relanded byte-identical (T-152 deliverables + git-domain sweep '
               'now on origin); MSG-0612 proposal-2 claw gate landed same-round (fleet proposal -> mechanical gate '
               'in one round); watermark GREEN golden-week',
})
with open(hb_path, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# round report line (idempotent guard: skip if r400 line already present)
rep_path = 'round_reports-bm-c.md'
with open(rep_path, encoding='utf-8') as fh:
    rep = fh.read()
if '| r400 |' not in rep:
    with open(rep_path, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(REPORT_LINE + '\n')

# --- state bump LAST (r610 law) ---
st_path = 'state-bm-c.json'
with open(st_path, encoding='utf-8') as fh:
    st = json.load(fh)
st.update({
    'round_no': 400,
    'last_round_at': 'r400',
    'last_round_ts': hms,
    'updated': iso,
    'verify': VERIFY,
    'did': DID,
    'current_task': 'r400 closeout: bookkeeping four + targeted commit + push + delivery self-verify',
    'next': NEXT,
    'heartbeat_epoch_utc': epoch,
    'clock_read': iso,
    'last_ts': hms,
    'last_round': '2026-10-03 r400 bm-c: r399 recovery closeout pushed (T-152 ON ORIGIN) + MSG-0612 pool-claim claw '
                  'gate (23/23) + S6 37/37 rc0',
    'last_seen': hms,
    'updated_at': iso,
})
with open(st_path, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(st, fh, fh if False else None, ensure_ascii=False, indent=1) if False else json.dump(
        st, fh, ensure_ascii=False, indent=1)

# --- post-write assertions (R170/R178/R262 laws) ---
for p in (hb_path, st_path):
    with open(p, encoding='utf-8') as fh:
        d = json.load(fh)
    assert isinstance(d['heartbeat_epoch_utc'], int), p + ' epoch not int'
    datetime.fromisoformat(d['clock_read'])     # raises if not real ISO-8601
print('bookkeeping OK: hb+report+state, epoch=%d clock=%s' % (epoch, iso))
