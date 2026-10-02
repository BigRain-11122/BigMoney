# -*- coding: utf-8 -*-
# r375 bm-c round wrap: state + heartbeat + round report + HANDOVER 5x +
# CODELY union (origin blob + my pit line) + pool_core_samples union check
# + targeted add + commit -F + push. Bytes in/out (r373 law), int epoch
# (R170/R178), ISO-T clock (R262).
import json
import os
import subprocess
import time
import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000


def git(args, check=True, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(['git'] + args, capture_output=True, cwd=REPO,
                       creationflags=CREAT, env=e)
    if check and r.returncode != 0:
        raise SystemExit('GIT FAIL %s -> %s' % (args[:4],
                        r.stderr.decode('utf-8', 'replace')[:300]))
    return r


git(['fetch', 'origin'])
origin_tip = git(['rev-parse', 'origin/main']).stdout.decode().strip()
print('origin tip:', origin_tip[:12])

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('%z')[:3] + ':' + now.strftime('%z')[3:]
epoch = int(time.time())

# ---- 1) CODELY union: origin blob (LF) + my pit line before ### Reference ----
PIT = ('- [2026-10-02 16:5x r375 bm-c] PS 超长命令串解析层静默吞=整段零执行坑（W102 冻结 push 窗实弹）：'
       '~2.9KB 单行命令（add+status+长内联 commit -m+push 四连）返回**空输出 rc=1 且无条件字符串字面量未打印'
       '=整段从未执行的诊断签名**（非 git 失败——git 面零输出零状态变化·冻结件仍 unstaged 幸 status 复核抓回）；'
       '误判风险=按「add/commit 已发生」继续推进。修法=长 commit 消息一律落文件走 commit -F 通道'
       '（..\\.codely-cli\\scratch\\<msg>.txt·免引号/长度/转义三面）+多步 git 拆步或经包装器单步。'
       'How to apply：含长内联消息的 commit 从会话壳发起必走 -F 文件；遇「空输出+rc!=0+无条件 literal 缺席」'
       '先判整段零执行勿疑 git。')
src = os.path.join(REPO, 'CODELY.md')
origin_lf = git(['show', 'origin/main:CODELY.md']).stdout
assert origin_lf.count(b'\r') == 0
o_lines = origin_lf.decode('utf-8').split('\n')
assert o_lines.count('### Reference') == 1
assert PIT not in o_lines, 'pit line already present'
ref_i = o_lines.index('### Reference')
union = o_lines[:ref_i] + [PIT] + o_lines[ref_i:]
union_lf = '\n'.join(union).encode('utf-8')
assert len(union_lf) == len(origin_lf) + len(PIT.encode('utf-8')) + 1
open(src, 'wb').write(union_lf.replace(b'\n', b'\r\n'))
print('CODELY union: origin %dB + r375 pit line' % len(origin_lf))

# ---- 2) pool_core_samples.jsonl union check (r570/r580 law) ------------------
PCS = os.path.join(REPO, 'results', 'pool_core_samples.jsonl')
if os.path.exists(PCS):
    o_raw = git(['show', 'origin/main:results/pool_core_samples.jsonl']).stdout
    o_lines_set = set(o_raw.decode('utf-8').splitlines())
    local = open(PCS, 'rb').read().decode('utf-8')
    l_lines = [ln for ln in local.splitlines() if ln.strip()]
    extras = []
    for ln in l_lines:
        if ln not in o_lines_set:
            try:
                import json as _j
                if isinstance(_j.loads(ln), dict):
                    extras.append(ln)
            except Exception:
                print('local non-dict/non-json line skipped (r570 gate):', ln[:80])
    if extras:
        merged = o_raw.decode('utf-8').rstrip('\n').split('\n') + extras
        open(PCS, 'wb').write(('\n'.join(merged) + '\n').encode('utf-8').replace(b'\n', b'\r\n'))
        print('pool_core_samples union: origin %d + local extras %d' % (len(o_lines_set), len(extras)))
    else:
        git(['checkout', 'origin/main', '--', 'results/pool_core_samples.jsonl'])
        print('pool_core_samples: no local extras -> synced to origin version')

# ---- 3) state-bm-c.json (round 375) -------------------------------------------
sp = os.path.join(REPO, 'state-bm-c.json')
st = json.load(open(sp, encoding='utf-8-sig'))
st['round_no'] = 375
st['last_round_at'] = 'r375'
st['last_round_ts'] = now.strftime('%m/%d/%Y %H:%M:%S')
st['updated'] = iso
st['verify'] = ('r375: W102 FREEZE delivered end-to-end (seat MSG-20261002-1642-bmc pre-pushed a369ae045 per r565; '
                'band gate ADMIT rc0 A 247_004..249_003 + B 59_201..59_400 both arithmetic CLEAN hops 0/0; '
                'banned gate ADMIT 0; five faces + PERPETUAL_N1_W102_PREREG frozen, anchor=W97 finalize head 577,948 K=211,320; '
                'freeze commit ac078162d; direct push claw-blocked on bm-b cd2610688 diverged base -> surgical re-parent '
                'b4b4b335af 13-file payload incl. 6 ignition shards, delivery ls-tree verified; 92nd engine wave, bm-c 30th '
                'owned per gate machine face -- seat prose ordinal hand-calc drift disclosed per r359) + W102 engine '
                'self-ignition 12/12 burned (mtime-reload v0.4, product growth proof r325; appender pushes shards) + '
                'S6 37/37 rc0 (dualrun streak 51/3 zero-drift, WM py_low_board_clear holiday-legal, audit flags '
                'pool_starvation/supply_floor = never-dry trigger answered by W102 freeze, ORANGE_COOL clock, daily report '
                '+ CEO live page written, stale-takeover scorecard/dashboard faces legal L3) + smoke 47/47 + orders 143/143 '
                'double-scan + D-19 937A373D MATCH + attrition CLEAN + self-heal 4/4 (loop pin=5 no-op, watchdog, claws MATCH)')
st['did'] = ('r375: W102 seat+gate+prereg+five-face freeze+surgical re-parent push + W99 12/12 burn completed (finalize '
             'gated on W98 bm-a pending) + W102 ignition 12/12 + S6 all-green + PS long-command zero-exec pit line')
st['current_task'] = ('W102 burn complete 12/12 on local engine (finalize gated: upstream W98 bm-a + W99 own finalize '
                      'pending, FAIL-CLOSED r307; W100 bm-b + W101 bm-a burning on their engines); T-144(c) engine/data/'
                      'protocol domains + flow-sinking due 10-07; T-143 month-exam prep 10-29; month-boundary first exam 10-31')
st['next'] = ('(r376)(a) W99 finalize when W98 lands on origin (fetch check -> one-pass finalize --wave 99, prev=origin '
              'chain head derive r518, no blind rerun r538); (b) T-144(c) engine-domain split (r369/r373 paradigm); '
              '(c) W103 never-dry if engine queue empty (projection A 249_004..251_003 / B 59_401..59_600, re-derive '
              'never transcribe); (d) T-143 month-exam prep; (e) month-boundary first exam 10-31')
st['heartbeat_epoch_utc'] = epoch
st['clock_read'] = iso
st['last_ts'] = iso
st['last_round'] = ('2026-10-02 r375 bm-c: W102 FREEZE delivered (five faces + surgical re-parent b4b4b335af) + '
                    'ignition 12/12 + S6 all-green + smoke 47/47 + orders 143/143')
st['last_seen'] = iso
st.pop('note', None)
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178)'
assert 'T' in chk['clock_read'], 'clock_read must be ISO-T (R262)'
print('state-bm-c.json: round 375, epoch int verified')

# ---- 4) heartbeat fleet/machines/bm-c.json ------------------------------------
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-c.json')
hb = json.load(open(hp, encoding='utf-8-sig'))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['current_task'] = 'W102 burn 12/12 complete; W99 finalize waits upstream W98 bm-a'
hb['verdict'] = 'healthy: W102 freeze delivered + ignition 12/12; S6 green; smoke 47/47'
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'heartbeat epoch must be int'
print('heartbeat bm-c.json: epoch int verified')

# ---- 5) round report line -------------------------------------------------------
rp = os.path.join(REPO, 'round_reports-bm-c.md')
line = ('{ts} | r375 | W102 冻结交付全程（席位 MSG-20261002-1642-bmc 先推 a369ae045 r565 律→带闸 ADMIT rc0 '
        'A 247_004..249_003/B 59_201..59_400 双侧算术 CLEAN hops 0/0→banned ADMIT 0→prereg 冻结锚=W97 finalize '
        '〔head 577,948·K=211,320〕→五面冻结 FIX-A/B/C+AST 纯插入 +30/+178/+2→commit ac078162d→直推被爪正确双拦 '
        '〔bm-b cd2610688 分叉基座·r366 族〕→外科 re-parent b4b4b335af 13 件 payload〔7 冻结件+6 点火分片〕三断言+送达 '
        'ls-tree 自证→第 92 枚引擎波·bm-c 第 30 席〔gate 机面；席位 prose 序数手算偏差披露 r359〕〕+W99 12/12 烧毕'
        '（finalize 候 W98 bm-a FAIL-CLOSED）+W102 引擎自燃 12/12（mtime-reload·产物增长=唯一证据 r325）+S6 37/37 rc0 '
        '〔dualrun 51/3·WM 绿假日合法·审计旗 pool_starvation/supply_floor=never-dry 已由 W102 应答·ORANGE_COOL·'
        'scorecard/dashboard stale-takeover 合法 L3〕 | 证据: ac078162d+b4b4b335af+gate/banned 回执+selftest 9/9+缺省波 '
        'PASS+ls-tree 送达 6 分片+S6 rc0 全录+smoke 47/47+orders 143/143 双扫+D-19 MATCH 937A373D+attrition CLEAN+自愈 4/4 '
        '〔loop pin=5·watchdog·双爪 MATCH〕 | 下轮: W98 落 origin 即 W99 finalize one-pass〔r538〕；T-144(c) 引擎域拆件；'
        'W103 never-dry 复核投影〔A 249_004..251_003/B 59_401..59_600 机闸重 derive 禁转抄〕\n').format(ts=iso)
with open(rp, 'a', encoding='utf-8') as fh:
    fh.write(line)
print('round report appended')

# ---- 6) HANDOVER 5x line (round 375) -------------------------------------------
HPATH = os.path.join(REPO, 'research', 'HANDOVER.md')
h5 = ('> bm-c round 375 五倍数核对（2026-10-02 16:5x·增量窗 r371-375 五轮）：增量窗 r371-375=bm-c 面'
      '（**T-144(c) 域拆件续+W99/W102 引擎供给线双连营**——r371 T-131 采集器网关 pid 复用假阳性+双龄停滞自愈腿'
      '〔psutil cmdline 归属验证+lock 双龄机判〕+lane_io origin-ref 心跳读腿落地〔r366 修复候选收口·18/18〕；'
      'r372 autocrlf 双空间对账坑〔blob 空间算字节/md5·落盘按工作树 EOL〕；r373 **T-144(c) 池域拆件交付**'
      '〔16 条 verbatim→research/pit-pool.md·字节对账零丢失·due 10-07 全线余=engine/data/protocol+流水下沉〕；'
      'r374 **W99 FREEZE**〔席位 MSG-20261002-1625-bmc 先推 fed0b4054 r565 律+带闸 ADMIT A 241_004..243_003/B '
      '58_551..58_750 D-20261002-05 钉死跳位 hops 2+五面 f2191688c+引擎自燃 12/12〕+seat-MSG 归档窗坑律'
      '〔leg0c 扫描面=inbox+processed 双目录合集〕；r375=本核对轮 **W102 FREEZE 交付全程**〔席位 '
      'MSG-20261002-1642-bmc 先推 a369ae045+带闸 ADMIT 双侧算术 CLEAN hops 0/0+banned ADMIT 0+prereg 锚=W97 '
      'finalize+五面 ac078162d+直推被爪正确双拦〔bm-b cd2610688 分叉基座 r366 族〕→**外科 re-parent b4b4b335af**'
      '〔13 件 payload=7 冻结件+6 点火分片·三断言+送达自证·PS 超长命令零执行坑=commit -F 通道修法〕+W102 自燃 '
      '12/12+第 92 枚引擎波/bm-c 第 30 席〔gate 机面·席位 prose 序数手算偏差披露 r359〕+W99 12/12 烧毕 finalize '
      '候 W98〕）产物清单漂移=research/pit-pool.md〔r373〕+Tools/lane_io origin-ref 心跳读腿〔r371〕+'
      'research/PERPETUAL_N1_W99_PREREG.md+scripts/perpetual_faces.py〔N1_BANDS[99]〕+perpetual_faces_n1.py'
      '〔WAVE_CONFIGS[99]+W99 腿〕+results/p2cal_ext/n1_w99/*〔12/12〕〔r374〕+research/PERPETUAL_N1_W102_PREREG.md+'
      'pf/n1/canon W102 五面+results/p2cal_ext/n1_w102/*〔12/12〕+results/_r375bmc_w102_{band_gate,freeze_edits,'
      'surgery_push}.py〔r375〕；统一链 **577,948 实读**（live head=n1_w97_results.json·W98/W99/W100/W101/W102 '
      'finalize 依次落地前移·W99 候 W98 bm-a FAIL-CLOSED）；orders 143/143 双扫零未回执；smoke 47/47；指针：'
      '**W98 bm-a finalize 落地→W99 one-pass finalize→W100/W101/W102 链推进〔窗≤48h〕+T-144(c) 引擎/数据/协议域'
      '拆件〔due 10-07〕+月界首考 10-31 清单**；下一 5x=bm-c r380。\n')
raw = open(HPATH, 'rb').read().decode('utf-8')
first_gt = raw.index('\n> ') + 1
out = raw[:first_gt] + h5 + raw[first_gt:]
open(HPATH, 'wb').write(out.encode('utf-8'))
print('HANDOVER 5x line r371-375 prepended')

# ---- 7) tmp index cleanup + targeted add ----------------------------------------
tmp_idx = os.path.join(REPO, 'results', '_r375bmc_tmp_index')
if os.path.exists(tmp_idx):
    os.remove(tmp_idx)

ADD = [
    'state-bm-c.json', 'fleet/machines/bm-c.json', 'round_reports-bm-c.md',
    'research/HANDOVER.md', 'CODELY.md',
    'results/_r375bmc_w102_surgery_push.py',
    'results/pool_core_samples.jsonl',
    'docs/daily_report/REPORT-2026-10-02.md', 'docs/daily_report/REPORT-2026-10-02.json',
    'docs/live_usage/LIVE-2026-10-02.md', 'docs/live_usage/LIVE-2026-10-02.json',
    'docs/live_usage/LIVE-latest.md', 'docs/live_usage/LIVE-latest.json',
    'results/strategy_scorecard.json', 'results/daily_scorecard.json',
    'results/scorecard_v1.json', 'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-30.json', 'results/paper_export/latest.json',
    'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
    'results/regime_state.json', 'results/regime_state.bm-c.json',
    'results/t35_open_fill_verify.json', 'results/update_status.json',
    'results/update_status.bm-c.json', 'results/fund_premium_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/futures_update_status.bm-c.json', 'results/lhb_update_status.json',
    'results/lhb_update_status.bm-c.json', 'results/compute_audit.json',
    'results/compute_audit.bm-c.json', 'results/pool_dualrun.bm-c.jsonl',
    'results/token_usage.json', 'results/token_usage.bm-c.json',
    'results/x2_watch_log.jsonl', 'results/p1d_gates.json',
    'results/autofill_state.bm-c.json', 'results/dispatcher_state.bm-c.json',
    'results/saturation_engine_state.bm-c.json',
    'results/saturation_engine/face_bm-c.json',
    'fleet/inbox/processed/MSG-20261002-1642-bmc-w102-seat.md',
]
for extra_dir in ('results/p2cal_ext/n1_w102', 'results/saturation_engine'):
    pass
git(['add', '--'] + [p for p in ADD if os.path.exists(os.path.join(REPO, p))])
# W102 shards not yet on origin ride too (appender may lag)
r = git(['ls-tree', '--name-only', 'origin/main', '--', 'results/p2cal_ext/n1_w102/'])
on_origin = set(r.stdout.decode().strip().splitlines())
local_shards = set('results/p2cal_ext/n1_w102/' + f
                   for f in os.listdir(os.path.join(REPO, 'results', 'p2cal_ext', 'n1_w102'))
                   if f.endswith('.json'))
pending = sorted(local_shards - on_origin)
if pending:
    git(['add', '--'] + pending)
print('added %d wrap files + %d pending W102 shards' % (len(ADD), len(pending)))

# ---- 8) commit -F + push ----------------------------------------------------------
msg_file = os.path.abspath(os.path.join(REPO, '..', '.codely-cli', 'scratch',
                                        '_r375bmc_wrap_msg.txt'))
open(msg_file, 'w', encoding='utf-8').write(
    'round 375 bm-c wrap: W102 FREEZE delivered end-to-end (seat a369ae045 pre-pushed r565 + band gate ADMIT '
    'A 247_004..249_003 / B 59_201..59_400 hops 0/0 + banned ADMIT 0 + five faces + prereg anchor=W97 finalize '
    'head 577,948 K=211,320; freeze commit ac078162d; direct push claw-blocked on bm-b cd2610688 diverged base '
    'r366 family -> surgical re-parent b4b4b335af 13-file payload incl. 6 ignition shards, ls-tree delivery '
    'verified; 92nd engine wave, bm-c 30th owned per gate machine face, seat prose ordinal drift disclosed r359) '
    '+ W102 engine self-ignition 12/12 (mtime-reload v0.4, product growth proof r325) + W99 12/12 burned finalize '
    'gated on W98 bm-a (FAIL-CLOSED r307) + S6 37 legs rc0 (dualrun streak 51/3, WM green holiday-legal, audit '
    'pool_starvation/supply_floor answered by W102 never-dry, ORANGE_COOL, daily report + CEO live page, '
    'stale-takeover derive faces legal L3) + smoke 47/47 + orders 143/143 double-scan + D-19 937A373D MATCH + '
    'attrition CLEAN + self-heal 4/4 (loop pin=5 no-op, watchdog, claws MATCH) + PS long-command zero-exec pit '
    '(commit -F channel) + HANDOVER r371-375 5x line + CODELY union + surgery tool receipt rides [via bm-c r375]\n')
git(['commit', '-F', msg_file])
git(['push', 'origin', 'main'])
print('WRAP PUSH OK')
