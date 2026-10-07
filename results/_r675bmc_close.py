# r675 bm-c close driver: state/heartbeat/round-ledger/s05-facts/HANDOVER-5x/commitmsg
# guard + 5x HANDOVER check round (reopen T-1). Facts-driven per r583 S4 law
# (hashes never hand-typed). Mid-round fleet order O-20261007-1157-bm-c
# (full-power broadcast, GM-session commit b8bb0b8c9 in shared tree) caught
# by close double-sweep -> consumed same round (orders_ack + receipt + report).
# Pattern credit: results/_r674bmc_close.py.
import json, os, subprocess, hashlib, sys, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOWD = datetime.now(TZ)
ISO = NOWD.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(NOWD.timestamp())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

DEC_EXPECT_CLOSE = '4c32527bf511b7e62eb52316864a9430b4fffe6cc23a39116c0b6c818782c254'
ORD_EXPECT = 'b687d867ed7ae7f2b2a58d5b4e58a78a01201db1'
MIDROUND_ORDER = 'O-20261007-1157-bm-c.md'

# fresh machine readings (heartbeat law: real values, epoch must be int)
CPU_PCT, RAM_FREE, GPU_FREE = 59, 7, 12492
try:
    import psutil
    CPU_PCT = int(psutil.cpu_percent(interval=1))
    RAM_FREE = round(psutil.virtual_memory().available / (1024 ** 3))
except Exception:
    pass
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, timeout=20)
    GPU_FREE = int(float(r.stdout.decode('utf-8', 'replace').strip().splitlines()[0]))
except Exception:
    pass

def blob(path):
    return subprocess.run(['git', '-C', 'K:/Fluxgroup/FluxGroup', 'show', 'origin/main:' + path],
                          capture_output=True).stdout

dsha_now = hashlib.sha256(blob('docs/decisions.md')).hexdigest()
ordsha_now = hashlib.sha1(blob('docs/orders.md')).hexdigest()
assert dsha_now == DEC_EXPECT_CLOSE, 'DEC drifted post-sweep: ' + dsha_now
assert ordsha_now == ORD_EXPECT, 'ORD drifted: ' + ordsha_now

ack = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))['orders_ack']
import glob as _g
order_files = {os.path.basename(p) for p in _g.glob('fleet/orders/*.md')}
unacked = sorted(order_files - set(ack)); gone = sorted(set(ack) - order_files)
assert unacked == [MIDROUND_ORDER] and not gone, ('orders drift', unacked, gone)
# mid-round catch (S0.5 double-sweep law): broadcast resume order -> ack same round
if MIDROUND_ORDER not in ack:
    ack.append(MIDROUND_ORDER)
assert sorted(set(order_files) - set(ack)) == [] and sorted(set(ack) - order_files) == []
ORDERS_ACKED = len(ack)

facts_rd = json.load(open('results/_r675bmc_s05_facts.json', encoding='utf-8'))
assert facts_rd['inbox_unread'] == [], 'inbox unread appeared mid-round'
assert facts_rd['dec_delta'] is False and facts_rd['ord_delta'] is False, 'mid-round delta'

facts = {
    'round': 675, 'machine': 'bm-c', 'ts': ISO,
    's05_round_start_dsha': DEC_EXPECT_CLOSE, 's05_round_start_match_state': True,
    's05_close_dsha': dsha_now, 's05_close_caught_change': False,
    'midround_order_caught': MIDROUND_ORDER + ' (全面开工广播令 §全员 resume 节; landed via GM-session commit b8bb0b8c9 in the 12:32-12:36 window, after both round-start sweeps = double-sweep law working; issuer-machine self-exec complete per §2, loop-verified six production tasks Enabled 6/6 live [Autofill/LoopWatchdog/PoolWorker/ResidentDispatcher=Ready, IterationLoop/SaturationEngine=Running]; loop action = orders_ack append + 回执节 receipt line + round-report receipt, zero extra physical action; O-20261007-0935 in-flight reminder noted unchanged)',
    'consumed_rows': ['O-20261007-1157-bm-c.md (broadcast resume order: acked + 回执节 line, zero own physical action beyond verification)'],
    'ord_sha': ordsha_now, 'ord_zero_delta': True,
    'orders_total': len(order_files), 'orders_acked': ORDERS_ACKED,
    'orders_unacked': [], 'orders_gone': gone,
    's6_rc': '38/38 rc0 (all legs executed, no bar-gated skips; dualrun streak 51 @403; update_lhb quarter refetch 11/11)',
    'smoke': '48/48 PASS',
    'qa': 'qa/smoke-r675.md 5/5 + qa/equity-curve-r675.png 66,322B (93 trades, determinism=True, face-identical)',
    'tripwire': 'CLEAN (1165 lines, entry max multiplicity 1, active_dup false)',
    'attrition': 'CLEAN (4 ledgers; 5 healed historical shrink rows annotated)',
    'watermark': 'green (red=false lane healthy, py_low_board_clear legal idle)',
    'compute_audit': 'CLEAN flags=[] (first clean window since supply_gap family; W173 burned 12/12 on bm-a seat 12:13)',
}
json.dump(facts, open('results/_r675bmc_s05_facts.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)

ACT = ('当前活: r675 金周值守 5x 核对轮（复市 T-1：S0 absorb d4b44a7ab+up-to-date·S0.5 双扫零 delta〔DEC 4C32527B/ORD B687D867〕'
       '·S7 闭窗双扫捕获轮中广播令 O-20261007-1157〔全面开工 §全员 resume 节·GM 会话 b8bb0b8c9 落树·本机自执毕 §2 已载'
       '·六任务 Enabled 6/6 实证·同窗 ack 166/166+回执节留痕〕·S1 48/48·S3 SAT 活 rc0+水位绿 py_low_board_clear+板 0 open'
       '+job_list 0+S6 38/38 rc0〔dualrun streak 51·bm-a 心跳陈 50min→stale-takeover derive 六面〕+QA r675 5/5 面恒等'
       '+tripwire CLEAN〔1165 lines〕+attrition CLEAN+四自愈件幂等过+CA flags=[] 首清洁窗〔supply 双旗随 W173 烧毕 12:13 自然清〕'
       '+5x HANDOVER 核对本轮兑现）'
       ' | 最近实物: results/_r675bmc_s6_log.txt（38/38 rc0）+qa/smoke-r675.md+qa/equity-curve-r675.png（5/5·93 trades·determinism=True）'
       '+docs/daily_report/REPORT-2026-10-07.md 与 docs/live_usage/LIVE-2026-10-07.md 再生（ORANGE）'
       '+results/strategy_scorecard.json+results/dashboard_status.js（stale-takeover derive）'
       '+results/_r675bmc_s05_facts.json（双扫+轮中令收据）+research/HANDOVER.md（r675 5x 行）'
       ' | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce 激活+纸盘 marks 地板推进'
       '+fund_premium 15:30 首采（bm-c 车道）+O-2115 验收包复跑（治理日）+W173 finalize 观察（bm-a）；'
       '月界首考 10-31（T-143 交付 10-29）；下个 5x=r680；每轮收口 tripwire scan（E09 律）')

DID = ('r675 bm-c: golden-week guard round + 5x HANDOVER check (reopen T-1). (1) S0: round-start dirty 3 = own daemon live-faces -> '
       'absorb commit d4b44a7ab (r620 law); pull --rebase up-to-date (0 behind). (2) S0.5 double-sweep: round-start DEC 4C32527B / '
       'ORD B687D867 zero-delta match state; close re-sweep zero-delta x2; inbox 0 unread. (2b) S7 close-sweep CAUGHT mid-round '
       'fleet order O-20261007-1157-bm-c (全面开工广播令 §全员 resume 节; GM-session commit b8bb0b8c9 landed it in the shared tree '
       'inside the 12:32-12:36 window, after both round-start sweeps = double-sweep law working as designed) -> consumed same round: '
       'bm-c issuer-machine self-execution already complete per §2 (interactive session ~11:5x), loop-verified six production tasks '
       'Enabled 6/6 live (Autofill/LoopWatchdog/PoolWorker/ResidentDispatcher=Ready, IterationLoop/SaturationEngine=Running), zero '
       'extra physical action; orders_ack 165->166 + 回执节 bm-c receipt line + round-report receipt; O-20261007-0935 in-flight '
       'reminder noted unchanged (due <=10-09 12:00). (3) S1 smoke 48/48. (4) S3: satengine alive rc0; watermark green (red=false '
       'lane healthy, py_low_board_clear legal idle white-list: board 0 open + golden-week no-bar); board 0 open; job_list 0; '
       'J-queue zero rebuild (town r650 / J12 / J18b all landed, anti-dup iron law); trial-labor line not triggered (W3 judge-prep '
       'bm-a in flight + trio finalize window to 10-09 + golden-week no-bar). (5) S6 chain 38/38 rc0 -> '
       'results/_r675bmc_s6_log.txt: dualrun ZERO-DRIFT streak 51 @403; compute_audit CLEAN flags=[] (first clean window since the '
       'supply_gap family opened -- W173 burned 12/12 on bm-a seat 12:03-12:13, between-seat gap resolved); update_lhb quarter '
       'refetch 11/11 rc0; REPORT-2026-10-07 + LIVE-2026-10-07 regenerated (ORANGE); bm-a hb stale 50min -> O-2100 s2.4 '
       'stale-takeover derive x6 faces (t35_open_fill_verify, t35_paper_export, daily_scorecard, build_status, '
       'strategy_scorecard, scorecard_v1); fund_premium pre-15:30 no-op (bm-c lane reopen-ready for 10-08 15:30 first snapshot); '
       'b_layer mask regen all-pass. (6) QA pack r675: qa/smoke-r675.md 5/5 + equity-curve-r675.png 66,322B (93 trades, sharpe '
       '0.1586, maxdd -4.33%, win 46.24%, determinism=True, face-identical to frozen panel). (7) 5x HANDOVER duty: '
       'research/HANDOVER.md r671-675 window line added (E09 rr-dup tripwire legislation r671 / D-06 redline increment r672 / '
       'reopen-eve readiness r673 / final-day guard r674 / this check round). (8) S7: tripwire scan CLEAN (1165 lines, entry max '
       'multiplicity 1); attrition CLEAN (4 ledgers); register_loop pin=5 no-op + watchdog registered + pre-commit/pre-push claws '
       'installed (LF-normalized, idempotent); state 675 -> 676.')

NEXT = ('(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + BIGMONEY_REGIME_GUARD=enforce live.paper first-bar window + '
        'paper marks floors advance + fund_premium first snapshot 15:30 (bm-c lane, readiness verified r671/r673). (b) O-2115 '
        'acceptance pack rerun on 10-08 governance day (scripts/o2115_acceptance_pack.py run). (c) W173 finalize watch (bm-a lane, '
        'burned 12/12 12:13); W174+ re-derive-MANDATORY for bm-c seat per r822 note. (d) trio finalize window watch to 10-09 (bm-b '
        'canonical lane). (e) O-20261007-0935 本地算力主供执法令能力盘点回执 due <=10-09 12:00 (in-flight, unchanged). (f) '
        'per-round close: Tools/_r671bmc_rr_dup_heal.py scan (E09 law). (g) next 5x = r680; monthly exam 10-31 assembly face '
        '(T-143, deliverable 10-29).')

VERIFY = ('receipts: results/_r675bmc_s6_log.txt (38/38 rc0) + results/_r675bmc_s05_facts.json (DEC/ORD double-sweep zero-delta '
          'x2 + mid-round order catch O-20261007-1157-bm-c acked, orders 166/166) + qa/smoke-r675.md (5/5) + '
          'qa/equity-curve-r675.png (66,322B, determinism=True) + smoke 48/48 + results/_attrition_guard_scan.json CLEAN + '
          'tripwire scan CLEAN (1165 lines max-multiplicity 1) + docs/daily_report/REPORT-2026-10-07.md + '
          'docs/live_usage/LIVE-2026-10-07.md (regen ORANGE) + results/strategy_scorecard.json + results/scorecard_v1.json + '
          'results/dashboard_status.js (stale-takeover derivations per O-2100 s2.4) + fleet/orders/O-20261007-1157-bm-c.md '
          '回执节 bm-c line (six-task Enabled 6/6 verified) + research/HANDOVER.md r675 5x line')

HEALTH = ('alive (r675 guard+5x check round clean: loop pin=5 no-op, watchdog registered, claws installed, attrition CLEAN, '
          'tripwire CLEAN; golden-week no-bar until 10-08 reopen; DEC/ORD zero-delta double-sweep; mid-round broadcast order '
          'O-20261007-1157 caught at close-sweep and consumed same round (resume confirmed, six tasks Enabled 6/6 verified); '
          'compute_audit flags=[] first clean window after W173 burn completed on bm-a seat; fund_premium lane reopen-ready for '
          '10-08 15:30 first snapshot)')

VERDICT = ('alive: r675 guard+5x check round clean (smoke 48/48; S6 38/38 rc0 all legs executed, dualrun streak 51; QA r675 5/5 '
           'face-identical determinism=True; DEC 4C32527B / ORD B687D867 zero-delta x2; orders 166/166 incl. mid-round broadcast '
           'order O-20261007-1157 caught at close-sweep + acked + six-task Enabled 6/6 verified (4 Ready + 2 Running); board 0 '
           'open; satengine alive rc0; watermark green py_low_board_clear legal idle; compute_audit CLEAN flags=[] (W173 '
           'between-seat gap resolved post-burn); bm-a hb stale 50min -> stale-takeover derive x6 per O-2100 s2.4; '
           'tripwire+attrition CLEAN; HANDOVER r671-675 5x line landed; reopen 10-08)')

PROD = ('r675 值守+5x 核对轮（金周·复市 T-1）：S0 absorb+up-to-date·S0.5 双扫零 delta+S7 闭窗捕获轮中广播令 O-20261007-1157'
        '〔全面开工 §全员 resume 节·同窗 ack 166/166+回执节留痕·六任务 Enabled 6/6 实证〕·S6 38/38 rc0（dualrun streak 51'
        '·update_lhb quarter refetch 11/11·REPORT/LIVE-2026-10-07 再生 ORANGE·bm-a 陈旧心跳 stale-takeover derive 六面）'
        '·QA r675 5/5 面恒等（93 trades·png 66,322B）·CA flags=[] 首清洁窗（supply 双旗随 W173 烧毕自然清）'
        '·tripwire/attrition CLEAN·四自愈件幂等过·HANDOVER r671-675 5x 行落地')

LATEST = ('results/_r675bmc_s6_log.txt (S6 38/38 rc0) + qa/smoke-r675.md + qa/equity-curve-r675.png (QA 5/5, 93 trades, '
          'determinism=True) + docs/daily_report/REPORT-2026-10-07.md + docs/live_usage/LIVE-2026-10-07.md (regen, ORANGE) + '
          'results/strategy_scorecard.json + results/_r675bmc_s05_facts.json (double-sweep + mid-round order receipt) + '
          'fleet/orders/O-20261007-1157-bm-c.md (bm-c 回执节) + research/HANDOVER.md (r675 5x line) @ ' + ISO)

MILE = ('10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce + marks floors advance + '
        'fund_premium first snapshot 15:30 (bm-c) + O-2115 acceptance pack rerun (governance day); W173 finalize watch (bm-a); '
        'trio finalize window to 10-09 (bm-b); monthly exam 10-31; next 5x=r680; per-close tripwire scan (E09)')

NOTE = ('r675: guard+5x check round; mid-round broadcast order caught+acked (resume confirmed, six tasks verified); S6 38/38 rc0; '
        'QA 5/5 face-identical; CA flags=[] first clean window; DEC/ORD zero-delta; tripwire+attrition CLEAN; HANDOVER r671-675 '
        'line landed.')

SUMMARY = ('r675: golden-week guard + 5x HANDOVER check (reopen T-1): absorb d4b44a7ab + up-to-date; DEC/ORD zero-delta '
           'double-sweep; mid-round broadcast order O-20261007-1157 (全面开工 resume) caught at close-sweep, acked 166/166 with '
           'six-task Enabled 6/6 verified; smoke 48/48; S6 38/38 rc0 (dualrun streak 51; update_lhb refetch 11/11; '
           'REPORT/LIVE-2026-10-07 regen ORANGE); QA r675 5/5 determinism=True; compute_audit CLEAN flags=[] (W173 gap resolved); '
           'bm-a stale-hb derive x6; tripwire+attrition CLEAN; HANDOVER r671-675 landed.')

DEC_METHOD = ('python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r675 round-start + close double-sweep '
              'MATCH 4C32527B zero-delta; facts-driven from results/_r675bmc_s05_facts.json, 64hex shape-asserted, never hand-typed '
              '(r583 S4 law))')
ORD_METHOD = ('python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r675 round-start + close double-sweep MATCH '
              'B687D867; facts-driven from results/_r675bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))')

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
            d[k] = RAM_FREE
    for k in GPU_KEYS:
        if k in d:
            d[k] = GPU_FREE
    for k in ('cpu_pct', 'cpu_util_pct'):
        if k in d:
            d[k] = CPU_PCT
    if 'cpu_idle_pct' in d:
        d['cpu_idle_pct'] = 100 - CPU_PCT
    d['heartbeat_epoch_utc'] = EPOCH
    d['round_no'] = 676
    d['round_no_label'] = 'round 675 (bm-c)'
    d['activity_now'] = ACT
    d['current_task'] = ACT
    d['note'] = NOTE

st, st_crlf = load_json_raw('state-bm-c.json')
apply_common(st)
st['last_round'] = 675
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
if MIDROUND_ORDER not in hb.get('orders_ack', []):
    hb['orders_ack'].append(MIDROUND_ORDER)
apply_common(hb)
hb['last_round'] = 675
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
RLINE = (ISO + ' | r675 bm-c | dept:工程/舰队（金周值守轮·复市 T-1·5x HANDOVER 核对+轮中广播令捕获） | 当前活: ' + DID +
         ' | 验证证据: ' + VERIFY + ' | 下轮指针: ' + NEXT + ' | watermark: 绿（red=false lane healthy·板 0 open·池 ready 1 全 bm-b keepalive 属主·'
         '金周无 bar 合法 idle·py_low_board_clear） | 本地未达 origin commit 数=3（S0 吸收件+GM 会话广播令件 b8bb0b8c9+本轮收口件·收口推送后复验）')
assert raw.count('r675 bm-c |'.encode('utf-8')) == 0, 'r675 line already present'
out = b''
if not raw.endswith(b'\n'):
    out += b'\r\n'
out += RLINE.encode('utf-8') + b'\r\n'
open(RL, 'ab').write(out)
raw2 = open(RL, 'rb').read()
assert raw2.count(b'\n') == prev_lines + 1, 'ledger line-count guard'
assert raw2.count('r675 bm-c |'.encode('utf-8')) == 1, 'ledger r675 uniqueness guard'

# HANDOVER 5x line insert-at-top (this round's 5x duty; anchor = r670 5x line)
HO = 'research/HANDOVER.md'
horaw = open(HO, 'rb').read()
hocr = b'\r\n' if b'\r\n' in horaw else b'\n'
marker = '> bm-c round 670 五倍数核对（2026-10-07 10:5x'
assert horaw.count(marker.encode('utf-8')) == 1, 'HANDOVER r670 anchor not unique'
HO_LINE = ('> bm-c round 675 五倍数核对（2026-10-07 12:3x·增量窗 r671-675 五轮）：增量窗 r671-675=bm-c 面'
           '（金周值守主线+复市 T-1 收口窗+E09 轮账本 tripwire 立法与 D-06 红线两连批+轮中广播令捕获——r671 值守+立法轮'
           '〔E09 律=Tools/_r671bmc_rr_dup_heal.py 三态 scan/heal/selftest（whole-file 2^N 串接 tripwire·r666/668/669 三窗 8x '
           '串接 17.87MB 治愈后防复发·零写扫描/隔离区 heal）+QA r671 5/5+fund_premium 复市车道 readiness 首验〕；'
           'r672 值守+红线处置轮〔D-20261002-06 达标呈证（主件 ≤30,720B 三面独立实测·本司 F-20261007-01 呈证后由 r674 '
           'DEC 消费窗收编）+主件余量红线触发增量批 1 条（水位 hash 管道快照假 delta 坑=r814 写面坑的读面姊妹→'
           'pit-protocol-d19.md·收据 _r672bmc_codely_increment.json）+push-race addendum（pre-push 爪 behind-signal 幻影删除面'
           '+池 owner_since 回退面=MSG-0612 环重放族）〕；r673 值守轮〔复市前夜就绪探针+S0 absorb+rebase 落 bm-a r821+'
           '双扫零 delta orders 164/164+QA r673 5/5+fund_premium readiness 复验〕；r674 金周末值守轮〔复市 T-1：absorb+rebase '
           '落 bm-a r821/r822 W173 freeze+S0.5 闭窗双扫捕获+同轮消费 DEC 12:00 治理批（D-20261002-06 提前核销 executed·'
           'D-05/06 他司零本司动作）+bm-a 心跳陈 31min→O-2100 s2.4 代 derive 五面+S6 35/35 rc0+supply 双旗根因=席位间隙'
           '+tripwire/attrition CLEAN〕；r675=本核对轮〔5x HANDOVER 义务（本行）+S0 absorb d4b44a7ab+up-to-date·S0.5 双扫零 '
           'delta（DEC 4C32527B/ORD B687D867）·S7 闭窗双扫捕获轮中广播令 O-20261007-1157〔全面开工 §全员 resume 节·GM 会话 '
           'b8bb0b8c9 落树·本机自执毕 §2 已载·六生产任务 Enabled 6/6 实证〔4 Ready+2 Running〕·同窗 ack 166/166+回执节留痕〕'
           '·smoke 48/48·S6 38/38 rc0（dualrun streak 51·update_lhb quarter refetch 11/11 rc0·bm-a 心跳陈 50min→stale-takeover '
           'derive 六面·REPORT/LIVE-2026-10-07 再生 ORANGE·fund_premium pre-15:30 no-op）+QA r675 5/5（93 trades·determinism=True'
           '·面恒等·png 66,322B）+CA flags=[] 首清洁窗（supply 双旗随 W173 12/12 烧毕 12:13 自然清）+tripwire CLEAN（1165 '
           'lines）+attrition CLEAN+四自愈件幂等过〕）'
           '产物清单漂移=qa/smoke-r67{1,3,5}.md+qa/equity-curve-r67{1,3,5}.png〔QA 证据包〕+results/_r67{1..5}bmc_* 工件族'
           '〔s05 facts+s6 log+close 收据〕+Tools/_r67{1..5}bmc_{s05,s6}.py 驱动族+Tools/_r671bmc_rr_dup_heal.py〔E09〕'
           '+research/pit-protocol-d19.md〔r672 +1 条〕+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md'
           '+fleet/orders/O-20261007-1157-bm-c.md 回执节〔r675〕；'
           '板 open=0·job_list 0·satengine rc0 活·试用劳力线不触发（W3 judge-prep bm-a 在飞+trio finalize 窗至 10-09+金周无 bar）；'
           '下个 5x=r680；指针：10-08 复市首交易日（数据链 re-arm+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采 bm-c '
           '车道+O-2115 验收包复跑治理日）+月界首考 10-31（T-143 交付 10-29）。')
newraw = horaw.replace(marker.encode('utf-8'), HO_LINE.encode('utf-8') + hocr + marker.encode('utf-8'), 1)
assert newraw.count('bm-c round 675 五倍数核对'.encode('utf-8')) == 1, 'HANDOVER r675 uniqueness'
assert newraw.count(marker.encode('utf-8')) == 1, 'HANDOVER marker preserved'
open(HO, 'wb').write(newraw)

# self-verify: json round-trip + epoch int type (R170/R178 law)
st2 = json.loads(open('state-bm-c.json', encoding='utf-8').read())
hb2 = json.loads(open('fleet/machines/bm-c.json', encoding='utf-8').read())
assert isinstance(st2['heartbeat_epoch_utc'], int) and isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert st2['round_no'] == 676 and hb2['round_no'] == 676
assert 'T' in st2['clock_read'] and '+08:00' in st2['clock_read'] and 'T' in hb2['clock_read']
assert st2['last_decisions_sha'].lower() == DEC_EXPECT_CLOSE and st2['last_orders_sha'].lower() == ORD_EXPECT
assert len(st2['last_decisions_sha']) == 64 and len(st2['last_orders_sha']) == 40
assert MIDROUND_ORDER in hb2['orders_ack'] and hb2['orders_ack_count'] == 166

# commit message (round commit; absorb msg file already committed as receipt)
CMSG = ('round 675: golden-week guard + 5x HANDOVER check (reopen T-1): S0 absorb d4b44a7ab (own daemon live-faces, r620 law) + '
        'pull --rebase up-to-date; S0.5 double-sweep DEC 4C32527B / ORD B687D867 zero-delta x2 (facts-driven '
        '_r675bmc_s05_facts.json); S7 close-sweep CAUGHT mid-round fleet order O-20261007-1157-bm-c (全面开工广播令 §全员 resume '
        '节, GM-session commit b8bb0b8c9) -> consumed same round: bm-c self-exec already complete per §2, loop-verified six '
        'production tasks Enabled 6/6 (Autofill/LoopWatchdog/PoolWorker/ResidentDispatcher=Ready + '
        'IterationLoop/SaturationEngine=Running), orders_ack 165->166 + 回执节 bm-c receipt line; O-20261007-0935 in-flight '
        'reminder unchanged; smoke 48/48; S3 satengine alive rc0 + watermark green py_low_board_clear legal idle + board 0 open + '
        'job_list 0 + trial-labor line not triggered (W3 judge-prep bm-a in flight + trio finalize window); S6 38/38 rc0 all legs '
        'executed -> results/_r675bmc_s6_log.txt (dualrun streak 51 @403; compute_audit CLEAN flags=[] first clean window after '
        'W173 12/12 burn completed on bm-a seat 12:13; update_lhb quarter refetch 11/11 rc0; REPORT-2026-10-07 + '
        'LIVE-2026-10-07 regen ORANGE; bm-a hb stale 50min -> O-2100 s2.4 stale-takeover derive x6 faces '
        '[t35_open_fill/t35_paper_export/daily_scorecard/build_status/strategy_scorecard/scorecard_v1]; fund_premium pre-15:30 '
        'no-op bm-c lane reopen-ready; b_layer mask regen all-pass); QA r675 5/5 qa/smoke-r675.md + equity-curve-r675.png '
        '66,322B (93 trades, sharpe 0.1586, determinism=True, face-identical); 5x HANDOVER duty: research/HANDOVER.md r671-675 '
        'window line (E09 rr-dup tripwire legislation r671 / D-06 redline increment r672 / reopen-eve readiness r673 / '
        'final-day guard r674 / this check round); tripwire scan CLEAN (1165 lines max-multiplicity 1) + attrition CLEAN + 4 '
        'self-heal tasks idempotent-pass (loop pin=5 no-op, watchdog registered, claws installed); state 675->676 [via bm-c '
        'r675]')
open('_r675bmc_commitmsg2.txt', 'wb').write(CMSG.encode('utf-8'))

print('DRIVER OK: state 676 / hb epoch', hb2['heartbeat_epoch_utc'], '/ ledger +1 line / HANDOVER 5x line / facts+commitmsg written')
print('DEC', dsha_now, '/ ORD', ordsha_now, '/ orders', len(order_files), 'acked', hb2['orders_ack_count'],
      '/ cpu', CPU_PCT, 'ram', RAM_FREE, 'gpu', GPU_FREE)
