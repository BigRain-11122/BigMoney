# -*- coding: utf-8 -*-
# r857 closeout writer: heartbeat + state + round report (fresh read-modify-write,
# no replace-tool on multi-writer files). ASCII-only stdout (GBK console safe).
import json, time, datetime, io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())
rid = 'r857'

# ---------------- heartbeat: fleet/machines/bm-a.json
hb_path = os.path.join(ROOT, 'fleet', 'machines', 'bm-a.json')
with open(hb_path, encoding='utf-8') as f:
    hb = json.load(f)
hb.update({
    'last_seen': ts,
    'ts': ts,
    'clock_read': ts,
    'heartbeat_epoch_utc': epoch,
    'current_task': 'r857 closed: S5_01_ZT_PILOT prereg frozen (1fb041a22) + burn rc0 8/8 PASS; next=10-08 15:30 reopen re-arm + pilot panel-face re-verify after first accrual',
    'last_action': 'r857 S5_01_ZT_PILOT adaptation-replay pilot landed and burned PASS (48/48 cells)',
    'idle_rounds': 0,
    'agenda_starved': False,
    'verdict': 'loaded_ok',
    'latest_artifact': 'research/S5_01_ZT_PILOT.md + scripts/zt_pool_pilot_replay.py + results/zt_pool_pilot_replay.json @' + ts,
})
with open(hb_path, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat ok: epoch=%d (int verified)' % chk['heartbeat_epoch_utc'])

# ---------------- state: state-bm-a.json
st_path = os.path.join(ROOT, 'state-bm-a.json')
with open(st_path, encoding='utf-8') as f:
    st = json.load(f)
st.update({
    'round_no': 857,
    'round': 857,
    'loop_round': rid,
    'last_round': rid,
    'last_round_at': ts,
    'last_round_ts': ts,
    'last_run': ts,
    'last_seen': ts,
    'updated': ts,
    'ts': ts,
    'clock_read': ts,
    'heartbeat_epoch_utc': epoch,
    'current_task': 'r857 closed: S5_01_ZT_PILOT pilot burned PASS; next=15:30 reopen re-arm',
    'last_action': 'r857: S5_01_ZT_PILOT prereg frozen + burned PASS (adaptation-replay pilot, data face)',
    'now_active': 'r857 closed (S5_01_ZT_PILOT 8/8 PASS); next = 10-08 15:30 market-reopen data chain re-arm + pilot panel-face re-verify',
    'did': ('r857: S0-1 anchor bm-a + orphan probe (py_faces=13, orphans=1 BigDomain cross-company read-only) '
            '+ orders 51/51 double-scan zero-unacked + DEC/ORD hash identical (ee659451/2bb2ee75, case-normalized) zero-action '
            '+ smoke 49/49 + watermark red=false lane healthy (next_pick moneyflow IC claimed, advisory) + saturation engine alive idle '
            '+ S5_01_ZT_PILOT LANDED AND BURNED: prereg research/S5_01_ZT_PILOT.md frozen 1fb041a22 '
            '(banned-gate ADMIT with BAN-03 new_data exception, dimension-orthogonal; runner scripts/zt_pool_pilot_replay.py '
            'selftest 12/12; evidence_cutoff 2026-09-30 D2 lockbox; F-04 MSG claim in fleet/inbox) + burn rc0 8/8 verdicts PASS '
            '(48/48 cells = 12 trading days x 4 faces, zero exempt zero shape flags zero dup codes; N_zt median 53.5 p99.9 103 '
            'max_board 4..7; zb_rate median 0.232; J2 dual-derive-through-storage identity 100%; J5 determinism; elapsed 131.4s) '
            '+ predictions P3/P4/P5 hit, P1 partial (12 vs ~13 days, calendar-derive caveat), P2 partial-miss (N_zt lower band too '
            'tight: 09-15=32 / 09-28=33 below 40; median/p99.9 main judgments unaffected) '
            '+ ADDITIONAL OBSERVATION: 09-28 N_dt=56 ~ 5.9x window median with NO index-level crisis day = N_dt axis carries '
            'independent microstructure info (REGIME-5 supply positive evidence; predictive face deferred >=12mo per T-67 s2) '
            '+ S6 35 legs rc0 + 4 bar-conditioned legs skip-legal (no new bar, pre-market; dualrun streak 51 zero-drift; '
            'compute_audit supply_floor flag -> standing-line response DISCHARGED this round via prereg+burn) '
            '+ idle_trigger --worked (idle_rounds 0) + attrition CLEAN + self-heal 4 in place (loop pin 8 no-op, watchdog, '
            'precommit/prepush claws)'),
    'next': ('r858: 10-08 15:30 market-reopen data chain re-arm (update_daily drops 10-08 bar -> all gates re-collect incl. '
             'zt_pool FIRST REAL accrual day; REGIME_GUARD v3 enforce; live.paper+t35_open_fill_verify+t24 legs run on new bar) '
             '-> after first zt_pool accrual: pilot panel-face re-verify (J2 identity on real panel rows vs same-day re-fetch, '
             'runner idempotent re-run) -> supply line next piece: cycle_position 3-axis -> REGIME-5 supply prereg draft '
             '(needs ~10td forward zt_pool history, usable ~10-22) + W181 seat watch + N_dt independent-info observation '
             'carried into three-axis gate design'),
    'verify': ('runner selftest 12/12 + burn rc0 8/8 PASS + banned-gate ADMIT rc0 + smoke 49/49 + S6 35 legs rc0 + '
               'dualrun streak 51 + attrition CLEAN + orders 51/51 double-scan + DEC/ORD identical + orphan face=1 '
               '(BigDomain cross-company read-only) + not-at-origin=0 post-push (to verify)'),
    'latest_artifact': 'research/S5_01_ZT_PILOT.md + scripts/zt_pool_pilot_replay.py + results/zt_pool_pilot_replay.json @' + ts,
    'last_artifact': 'research/S5_01_ZT_PILOT.md + scripts/zt_pool_pilot_replay.py + results/zt_pool_pilot_replay.json @' + ts,
})
with open(st_path, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print('state ok: round_no=%d' % json.load(open(st_path, encoding='utf-8'))['round_no'])

# ---------------- round report: round_reports-bm-a.md (repo root, r844 law)
rp_path = os.path.join(ROOT, 'round_reports-bm-a.md')
line = (
    ts + ' | ' + rid + ' | bm-a | dept:数据 | '
    'S0-1 anchor + orphan probe 孤儿面=1 (BigDomain cross-company read-only) | '
    'orders 51/51 双扫零未回执 + DEC/ORD hash identical (ee659451/2bb2ee75) 零动作 | '
    'smoke 49/49 + watermark red=false healthy + saturation engine alive idle | '
    '**S5_01_ZT_PILOT 落地+烧录 PASS**: prereg frozen 1fb041a22 (banned-gate ADMIT·BAN-03 new_data 豁免·维度正交论证·'
    'evidence_cutoff 2026-09-30 D2 锁盒·F-04 MSG 认领) + runner scripts/zt_pool_pilot_replay.py (selftest 12/12·复用采集器同面存储机械) '
    '+ burn rc0 8/8 判据全过 (48/48 格=12 交易日×4 面·零豁免零形状旗零重复代码·N_zt median 53.5/p99.9 103/max_board 4..7·'
    'zb_rate med 0.232·J2 双 derive 恒等 100%·J5 幂等·131.4s) | '
    '预测对账: P3/P4/P5 对·P1 部分对(日数 12 vs ~13·日历 derive 条款内)·P2 部分错(N_zt 带下沿过紧 09-15=32/09-28=33·主判面 median/p99.9 不受影响照过) | '
    '附加观察: 09-28 N_dt=56≈5.9×窗内中位而无指数级危机日=N_dt 轴独立微观结构信息量(REGIME-5 供给正向证据·预测值面待 ≥12mo 史另批) | '
    'S6 35 腿 rc0 + 4 bar 条件腿 skip 合法(无新 bar·pre-market) | dualrun streak 51 零漂移 | '
    'compute_audit supply_floor 旗→常设线响应本轮解除(prereg+烧) | idle_trigger --worked 清零 | attrition CLEAN | 自愈四件在位(loop pin 8 no-op) | '
    'L1 本地腿 0 token | '
    'verify: runner selftest 12/12 + burn rc0 8/8 + smoke 49/49 + banned ADMIT + attrition CLEAN + orders 51/51 | '
    'next: r858 10-08 15:30 重开数据链 re-arm(zt_pool 首采+全 gate 重臂+REGIME_GUARD v3 enforce+live.paper 族随新 bar) '
    '+ zt_pool 首采后 pilot 面板面 J2 复验(runner 幂等重跑) + W181 seat watch + 供给线下一件 cycle_position 三轴起草(usable ~10-22) | '
    '本地未达 origin commit 数=0 (post-push verify)\n'
)
with open(rp_path, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report appended (1 line)')
print('CLOSEOUT_OK')
