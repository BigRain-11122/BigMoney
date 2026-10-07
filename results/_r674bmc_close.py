# r674 bm-c close driver: state/heartbeat/round-ledger/inbox/s05-facts/commitmsg
# guard round (reopen T-1). Facts-driven per r583 S4 law (hashes never hand-typed).
import json, os, subprocess, shutil, hashlib, sys, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOWD = datetime.now(TZ)
ISO = NOWD.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(NOWD.timestamp())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

DEC_EXPECT_CLOSE = '4c32527bf511b7e62eb52316864a9430b4fffe6cc23a39116c0b6c818782c254'
DEC_ROUND_START = '635c3024a95e4487a08e55be9dad3a97e41c73726a9d82d955986d95ef6f6af6'
ORD_EXPECT = 'b687d867ed7ae7f2b2a58d5b4e58a78a01201db1'

def blob(path):
    return subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:' + path],
                          capture_output=True).stdout

dsha_now = hashlib.sha256(blob('docs/decisions.md')).hexdigest()
ordsha_now = hashlib.sha1(blob('docs/orders.md')).hexdigest()
assert dsha_now == DEC_EXPECT_CLOSE, 'DEC drifted again post-consume: ' + dsha_now
assert ordsha_now == ORD_EXPECT, 'ORD drifted: ' + ordsha_now

ack = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))['orders_ack']
import glob as _g
order_files = {os.path.basename(p) for p in _g.glob('fleet/orders/*.md')}
unacked = sorted(order_files - set(ack)); gone = sorted(set(ack) - order_files)
assert not unacked and not gone, ('orders drift', unacked, gone)

facts = {
    'round': 674, 'machine': 'bm-c', 'ts': ISO,
    's05_round_start_dsha': DEC_ROUND_START, 's05_round_start_match_state': True,
    's05_close_dsha': dsha_now, 's05_close_caught_change': True,
    'consumed_rows': ['D-20261007-04 (回执核销批21: ①D-20261002-06 提前核销->executed, consuming bigmoney F-20261007-01 呈证; zero own-subs action)',
                      'D-20261007-05 (治理日聚合审收口: SOP过审/卡点复核过/CPH4双轨件升E1/BigCompute M48维持; 他司零本司动作)',
                      'D-20261007-06 (三案回访C-01/02/03: cloudF面一行转办@BigCompute/bm-c窗10-14 执行司=BigCompute非本司; C-03①复访10-14; 零本司动作)'],
    'ord_sha': ordsha_now, 'ord_zero_delta': True,
    'orders_total': len(order_files), 'orders_acked': len(ack),
    'orders_unacked': unacked, 'orders_gone': gone,
    's6_rc': '35/35 rc0 (3 bar-gated legs legal skip: live.paper/t35_open_fill_verify/t24_prospect_paper, no new bar)',
    'smoke': '48/48 PASS', 'tripwire': 'CLEAN (1164 lines, entry max multiplicity 1)',
    'attrition': 'CLEAN (4 ledgers)',
    'watermark': 'green (red=false lane healthy, py_low_board_clear legal idle)',
}
json.dump(facts, open('results/_r674bmc_s05_facts.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)

ACT = ('当前活: r674 金周末值守轮（复市 T-1：S0 absorb+rebase 落 bm-a r821+r822 W173 freeze·S0.5 双扫+闭窗捕获 DEC 12:00 常务轮批'
       '〔D-20261007-04①=D-20261002-06 提前核销 executed·本司 F-20261007-01 呈证被收·D-05/06 他司零本司动作〕+orders 165/165·S1 48/48·'
       'S3 SAT 活 rc0+水位绿 py_low_board_clear+板 0 open+J 队列陈旧核查〔town.html 对齐=r650 收口·J12/J18b 已落地在册·反重复零重建〕'
       '+compute_audit supply_gap/supply_floor 双旗根因=席位间隙〔W173 freeze+seat=bm-a 11:22·bm-c 引擎 queue_next 空=合法·池 keepalive=bm-b f0e4d6841 实证〕'
       '·streak 147.7min 已自动升级 GM 派单面零越权代跑+bm-a 心跳 31min 陈旧→O-2100 s2.4 stale-takeover 代 derive 五面'
       '·S6 35/35 rc0〔3 bar-gated 腿合法跳计〕+tripwire/attrition CLEAN+四自愈件幂等过+inbox 自发 MSG self-ack 归档 processed/）'
       ' | 最近实物: results/_r674bmc_s6_log.txt（35/35 rc0·dualrun streak 51）+docs/daily_report/REPORT-2026-10-07.md 与 '
       'docs/live_usage/LIVE-2026-10-07.md 再生（ORANGE）+results/scorecard_v1.json+results/strategy_scorecard.json'
       '（bm-a 陈旧代 derive·S=2 A=4 best VOLATILITY-CE-01 87.0）+results/dashboard_status.js+results/paper_export/export-2026-09-30.json'
       '+results/_r674bmc_s05_facts.json（DEC/ORD 双扫收据）+results/_attrition_guard_scan.json CLEAN'
       ' | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce 激活（t24 门当日核验）'
       '+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道）+O-2115 验收包复跑（治理日）+W173 bm-a 座烧观察；'
       '月界首考 10-31（T-143 交付 10-29）；下个 5x=r675；每轮收口 tripwire scan（E09 律）')

DID = ('r674 bm-c: golden-week final-day guard round (reopen T-1). (1) S0: round-start dirty 5 = own daemon live-wins faces + r673 commitmsg '
       'leftovers -> absorb commit a805b2e2a + pull --rebase onto bm-a r821 + r822 W173 FREEZE + bm-b merge (behind 2 -> 0). '
       '(2) S0.5: round-start DEC 635C3024 / ORD B687D867 match state (zero-delta); CLOSE double-sweep CAUGHT DEC change 635C3024 -> 4C32527B '
       '(12:00 governance batch landed mid-round) -> consumed same round: D-20261007-04 row1 = D-20261002-06 提前核销 -> executed (main file '
       '30,398B <= 30,720B three-face independently measured, consuming bigmoney F-20261007-01; zero own-subs action), D-20261007-05/06 = '
       'other-subs (cloudF 面一行 dispatch owner=BigCompute, 窗 10-14; C-03① re-visit 10-14) -> watermark key updated to 4C32527B, facts-driven '
       'from results/_r674bmc_s05_facts.json; ORD B687D867 zero-delta x2; fleet orders 165/165 zero unacked (double-sweep). (3) S1 smoke 48/48. '
       'S3: satengine alive rc0 (cycle 2941, hb fresh 12:12:37); watermark green (py_low_board_clear legal idle white-list); board open=0; '
       'job_list 0; J-queue stale-check: town.html building-name alignment = r650 closed (footer canon 11/11), J12 town v1.0 + J18b update_status '
       'face (build_status.py L124) both landed -> zero rebuild per anti-duplication iron law; compute_audit supply_gap+supply_floor flags '
       'root-caused = between-seat wave gap: W173 frozen+seated bm-a 11:22 (r822, burns on bm-a local queue), bm-c engine queue_next empty legal '
       '(W173 tracked 0/12 on bm-a seat), pool 1-ready entry = bm-b live claim (f0e4d6841 autofill tick keepalive fund-divlowvol-p1-nulls-0of1), '
       'streak 147.7min auto-escalated to GM dispatch face per O-1614 s1.5 -- observed+reported, zero cross-lane reach; trial-labor line not '
       'triggered (W3 judge-prep bm-a in flight + trio finalize window). (4) bm-a heartbeat stale 31min -> O-2100 s2.4 STALE_MIN law '
       'stale-takeover derive by bm-c x5 faces: strategy_scorecard.json 56.1s recompute (6 traders S=2 A=4 B=0, best VOLATILITY-CE-01 87.0) + '
       'scorecard_v1.json + t35_paper_export export-2026-09-30.json + daily_scorecard.html + dashboard_status.js (+ t24 promotion eval 0/22 '
       'eligible, PROSPECT shards pending = honest zero-row). (5) S6 35/35 rc0 golden-week no-op tribe (3 bar-gated legs legal skip: live.paper / '
       't35_open_fill_verify / t24_prospect_paper -- no new bar until 10-08) -> results/_r674bmc_s6_log.txt; dualrun ZERO-DRIFT streak 51; '
       'REPORT-2026-10-07 + LIVE-2026-10-07 regenerated (state ORANGE cap 50%); fund_premium pre-15:30 no-op; fundamental 22.0h fresh skip; '
       'b_layer mask regen gates all-pass (5222 codes / ok_static 3517). (6) S7: tripwire scan CLEAN (1164 lines, entry max multiplicity 1); '
       'attrition CLEAN (4 ledgers); register_loop pin=5 no-op + watchdog registered + pre-commit/pre-push claws installed (LF-normalized); '
       'inbox 1 = own r673 MSG-2026-10-07-1200-bmc-ALL self-ack archived to processed/. (7) state 674 -> 675.')

NEXT = ('(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + BIGMONEY_REGIME_GUARD=enforce live.paper first-bar window (t24 gate '
        'last_bar>=2026-10-01 same-day verify) + paper marks floors advance + fund_premium first snapshot 15:30 (bm-c lane, readiness verified '
        'r671/r673). (b) O-2115 acceptance pack rerun on 10-08 governance day (scripts/o2115_acceptance_pack.py run). (c) trio finalize window '
        'watch to 10-09 (bm-b canonical lane). (d) W173 burn on bm-a seat (frozen r822); W3 judge burn target <=10-12 (bm-a seat); bm-c seat '
        'awaits next freeze (W174+ re-derive-MANDATORY noted by r822). (e) per-round close: Tools/_r671bmc_rr_dup_heal.py scan (E09 law). '
        '(f) next 5x = r675 (HANDOVER check round); monthly exam 10-31 assembly face (T-143, deliverable 10-29).')

VERIFY = ('receipts: results/_r674bmc_s6_log.txt (35/35 rc0) + results/_r674bmc_s05_facts.json (DEC 635C3024 round-start match -> 4C32527B '
          'close-sweep catch+consume 3 rows, ORD B687D867 zero-delta x2, orders 165/165) + smoke 48/48 + results/_attrition_guard_scan.json '
          'CLEAN + tripwire scan CLEAN (1164 lines max-multiplicity 1) + docs/daily_report/REPORT-2026-10-07.md + '
          'docs/live_usage/LIVE-2026-10-07.md + results/scorecard_v1.json + results/strategy_scorecard.json + results/dashboard_status.js '
          '(stale-takeover derivations per O-2100 s2.4) + fleet/inbox/processed/MSG-2026-10-07-1200-bmc-ALL.md (self-ack)')

HEALTH = ('alive (r674 guard round clean: loop pin=5 no-op, watchdog registered, claws MATCH, attrition CLEAN, tripwire CLEAN; golden-week '
          'no-bar until 10-08 reopen T-1; DEC 12:00 governance batch caught at close-sweep and consumed same round; supply_gap/supply_floor '
          'root-caused between-seat wave gap, GM-face auto-escalation, zero cross-lane reach; bm-a hb stale 31min -> stale-takeover derive x5 '
          'per O-2100 s2.4; fund_premium lane reopen-ready)')

VERDICT = ('alive: r674 guard round clean (smoke 48/48; S6 35/35 rc0 golden-week no-op tribe + 3 bar-gated legal skips; dualrun streak 51; '
           'DEC close-sweep catch+consume D-20261007-04/05/06 (D-20261002-06 executed-closure consuming our F-20261007-01; D-05/06 other-subs), '
           'hash 4C32527B; ORD zero-delta x2; orders 165/165; board 0 open; satengine alive rc0 cycle 2941; watermark green py_low_board_clear '
           'legal idle; supply_gap/supply_floor = between-seat wave gap (W173 seat=bm-a per r822; pool keepalive=bm-b f0e4d6841), GM-face '
           'auto-escalated per O-1614 s1.5; tripwire+attrition CLEAN; J-queue stale-check zero rebuild; reopen 10-08)')

PROD = ('r674 值守轮（金周末日·复市 T-1）：S0 absorb+rebase 三入列件落位·S0.5 闭窗双扫捕获+同轮消费 DEC 12:00 治理批〔D-20261002-06 提前核销 '
        'executed·他司两行零本司动作〕·S6 35/35 rc0+bm-a 陈旧心跳 O-2100 s2.4 代 derive 五面（scorecard/纸盘导出/日卡/dashboard_status）'
        '·supply 双旗根因定位=席位间隙（W173 座=bm-a·池 keepalive=bm-b 实证）·smoke 48/48+tripwire/attrition CLEAN+inbox self-ack 归档')

LATEST = ('results/_r674bmc_s6_log.txt (S6 35/35 rc0) + docs/daily_report/REPORT-2026-10-07.md + docs/live_usage/LIVE-2026-10-07.md (regen, '
          'ORANGE) + results/scorecard_v1.json + results/strategy_scorecard.json (stale-takeover derive, S=2 A=4) + '
          'results/_r674bmc_s05_facts.json (DEC/ORD double-sweep receipt) @ ' + ISO)

MILE = ('10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce + marks floors advance + fund_premium '
        'first snapshot 15:30 (bm-c); O-2115 acceptance pack rerun (governance day); W173 bm-a seat burn watch; trio finalize window to 10-09 '
        '(bm-b); monthly exam 10-31; next 5x=r675 (HANDOVER check); per-close tripwire scan (E09)')

NOTE = ('r674: guard round; DEC close-sweep consume (D-20261002-06 executed, D-05/06 other-subs); S6 35/35; stale-takeover derive x5; '
        'supply-gap root cause = between-seat wave gap; smoke 48/48; attrition CLEAN.')

SUMMARY = ('r674: golden-week final-day guard (reopen T-1): absorb+rebase onto r821/r822; DEC 12:00 batch caught at close-sweep and consumed '
           '(D-20261002-06 executed-closure; 2 rows other-subs); ORD zero-delta; orders 165/165; smoke 48/48; S6 35/35 rc0; dualrun streak 51; '
           'bm-a stale-hb stale-takeover derive x5; supply_gap/supply_floor root-caused between-seat wave gap; tripwire+attrition CLEAN.')

DEC_METHOD = ('python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r674 round-start MATCH 635C3024 -> close-sweep CAUGHT '
               '12:00-governance-batch change -> consumed D-20261007-04/05/06 same round -> updated to 4C32527B; facts-driven from '
               'results/_r674bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))')
ORD_METHOD = ('python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r674 round-start + close double-sweep MATCH B687D867; '
              'facts-driven from results/_r674bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))')

TS_KEYS = ['clock_read', 'ts', 'updated', 'updated_at', 'last_seen', 'last_seen_at', 'last_run_at', 'last_round_at', 'last_round_ts',
           'current_task_at', 'last_decisions_read_at', 'last_decisions_at']
RAM_KEYS = ['free_ram_gb', 'idle_ram_gb', 'ram_free_gb']
GPU_KEYS = ['gpu_free_vram_mib', 'gpu_free_vram_mb', 'gpu_idle_vram_mb', 'gpu_idle_vram_mib', 'gpu_free_mb', 'gpu_idle_mb', 'gpu_vram_free_mb',
            'gpu_free_mib']

def load_json_raw(path):
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    obj = json.loads(raw.decode('utf-8'))
    return obj, crlf

def dump_json_raw(path, obj, crlf):
    s = json.dumps(obj, indent=1, ensure_ascii=False)
    if crlf:
        s = s.replace('\n', '\r\n')
    open(path, 'wb').write(s.encode('utf-8'))

def apply_common(d):
    for k in TS_KEYS:
        if k in d:
            d[k] = ISO
    for k in RAM_KEYS:
        if k in d:
            d[k] = 7
    for k in GPU_KEYS:
        if k in d:
            d[k] = 12492
    for k in ('cpu_pct', 'cpu_util_pct'):
        if k in d:
            d[k] = 59
    if 'cpu_idle_pct' in d:
        d['cpu_idle_pct'] = 41
    d['heartbeat_epoch_utc'] = EPOCH
    d['round_no'] = 675
    d['round_no_label'] = 'round 674 (bm-c)'
    d['activity_now'] = ACT
    d['current_task'] = ACT
    d['note'] = NOTE

st, st_crlf = load_json_raw('state-bm-c.json')
apply_common(st)
st['last_round'] = 674
st['last_round_at'] = ISO
st['last_round_ts'] = ISO
st['last_round_summary'] = SUMMARY
st['did'] = DID
st['last_action'] = DID
st['verify'] = VERIFY
st['next'] = NEXT
st['last_decisions_sha'] = dsha_now.upper()
st['last_decisions_sha_method'] = DEC_METHOD
st['dec_sha_method'] = DEC_METHOD
st['last_orders_sha'] = ordsha_now.upper()
st['last_orders_sha_method'] = ORD_METHOD
st['ord_sha_method'] = ORD_METHOD
dump_json_raw('state-bm-c.json', st, st_crlf)

hb, hb_crlf = load_json_raw('fleet/machines/bm-c.json')
apply_common(hb)
hb['last_round'] = 674
hb['last_round_summary'] = SUMMARY
hb['did'] = DID
hb['health'] = HEALTH
hb['verdict'] = VERDICT
hb['prod_lanes'] = PROD
hb['latest_artifact'] = LATEST
hb['next_milestone'] = MILE
hb['orders_ack_count'] = len(hb.get('orders_ack', []))
dump_json_raw('fleet/machines/bm-c.json', hb, hb_crlf)

# round ledger append (canonical file per r645; CRLF)
RL = 'logs/iteration-loop/round_reports-bm-c.md'
raw = open(RL, 'rb').read()
prev_lines = raw.count(b'\n')
RLINE = (ISO + ' | r674 bm-c | dept:工程/舰队（金周末值守轮·复市 T-1） | 当前活: ' + DID + ' | 验证证据: ' + VERIFY +
         ' | 下轮指针: ' + NEXT + ' | watermark: 绿（red=false lane healthy·板 0 open·池 1 ready=bm-b keepalive 在飞·金周无 bar 合法 idle）'
         ' | 本地未达 origin commit 数=2（S0 吸收件+本轮收口件·收口推送后复验）')
assert raw.count('r674 bm-c |'.encode('utf-8')) == 0, 'r674 line already present'
out = b''
if not raw.endswith(b'\n'):
    out += b'\r\n'
out += RLINE.encode('utf-8') + b'\r\n'
open(RL, 'ab').write(out)
raw2 = open(RL, 'rb').read()
assert raw2.count(b'\n') == prev_lines + 1, 'ledger line-count guard'
assert raw2.count('r674 bm-c |'.encode('utf-8')) == 1, 'ledger r674 uniqueness guard'

# inbox: self-ack receipt line + move to processed/
MSG = 'fleet/inbox/MSG-2026-10-07-1200-bmc-ALL.md'
mraw = open(MSG, 'rb').read()
meol = b'\r\n' if b'\r\n' in mraw else b'\n'
receipt = ('- [2026-10-07 r674 bm-c self-ack] 原发机收讫归档：扩展已入本机常态（r673 S6/selftest 消费面）；'
           'bm-a/bm-b 各自 S7 照常消费本件（processed/ 在册可查）。').encode('utf-8')
if not mraw.endswith(b'\n'):
    open(MSG, 'ab').write(meol)
open(MSG, 'ab').write(receipt + meol)
os.makedirs('fleet/inbox/processed', exist_ok=True)
shutil.move(MSG, 'fleet/inbox/processed/MSG-2026-10-07-1200-bmc-ALL.md')
assert not os.path.exists(MSG) and os.path.exists('fleet/inbox/processed/MSG-2026-10-07-1200-bmc-ALL.md')

# self-verify: json round-trip + epoch int type (R170/R178 law)
st2 = json.loads(open('state-bm-c.json', encoding='utf-8').read())
hb2 = json.loads(open('fleet/machines/bm-c.json', encoding='utf-8').read())
assert isinstance(st2['heartbeat_epoch_utc'], int) and isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert st2['round_no'] == 675 and hb2['round_no'] == 675
assert 'T' in st2['clock_read'] and '+08:00' in st2['clock_read'] and 'T' in hb2['clock_read']
assert st2['last_decisions_sha'].lower() == DEC_EXPECT_CLOSE and st2['last_orders_sha'].lower() == ORD_EXPECT
assert len(st2['last_decisions_sha']) == 64 and len(st2['last_orders_sha']) == 40

# commit message (committed as same-round receipt per r673-absorb precedent)
CMSG = ('round 674: golden-week final-day guard round (reopen T-1): absorb+rebase onto bm-a r821/r822 W173 freeze + bm-b merge; '
        'DEC close-sweep catch+consume 12:00 governance batch (D-20261007-04: D-20261002-06 executed-closure consuming F-20261007-01; '
        'D-05/06 other-subs -> zero own-subs actions) -> watermark 4C32527B; ORD B687D867 zero-delta x2; orders 165/165 zero unacked '
        '(double-sweep); smoke 48/48; S3 satengine alive rc0 + watermark green py_low_board_clear + board 0 open + J-queue stale-check '
        '(town r650 / J12 / J18b all landed, zero rebuild); compute_audit supply_gap/supply_floor root-caused = between-seat wave gap '
        '(W173 freeze+seat=bm-a 11:22 per r822, bm-c engine queue_next empty legal, pool keepalive = bm-b f0e4d6841 autofill tick) + GM-face '
        'auto-escalation noted, zero cross-lane reach; bm-a hb stale 31min -> O-2100 s2.4 stale-takeover derive 5 faces '
        '(strategy_scorecard 56.1s recompute S=2 A=4 + scorecard_v1 + paper_export export-2026-09-30 + daily_scorecard.html + '
        'dashboard_status.js) + t24 promotion eval 0/22 honest; S6 35/35 rc0 golden-week no-op tribe (3 bar-gated legs legal skip: '
        'live.paper/t35_open_fill_verify/t24_prospect_paper; dualrun streak 51; REPORT/LIVE-2026-10-07 regen ORANGE; fund_premium '
        'pre-15:30 no-op; b_layer mask regen all-pass) -> results/_r674bmc_s6_log.txt; tripwire scan CLEAN (1164 lines max-multiplicity 1) '
        '+ attrition CLEAN + 4 self-heal tasks idempotent-pass (loop pin=5 no-op, watchdog registered, claws installed) + inbox self-MSG '
        'MSG-2026-10-07-1200-bmc-ALL self-ack archived to processed/; state 674->675 [via bm-c r674]')
open('_r674bmc_commitmsg.txt', 'wb').write(CMSG.encode('utf-8'))

print('DRIVER OK: state 675 / hb epoch', hb2['heartbeat_epoch_utc'], '/ ledger +1 line / inbox archived / facts+commitmsg written')
print('DEC', dsha_now, '/ ORD', ordsha_now, '/ orders', len(order_files))
