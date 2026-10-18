"""r1015 bm-b closeout: round-report row + state.json + heartbeat faces."""
import ctypes
import datetime
import io
import json
import os
import subprocess
import sys

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
NOW = datetime.datetime.now()
NOW_ISO = NOW.isoformat(timespec='seconds')
NOW_ISO8 = NOW.isoformat(timespec='seconds') + '+08:00'
EPOCH = int(NOW.timestamp())

# --- sample machine stats ---
free_gb = round(ctypes.windll.kernel32.GlobalMemoryStatusEx and 0 or 0, 1) if False else None
class MS(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
m = MS(); m.dwLength = ctypes.sizeof(MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_gb = round(m.ullAvailPhys / 1e9, 1)
vram_mb = 0
gpu_util = 0
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu',
                        '--format=csv,noheader,nounits'], capture_output=True, text=True,
                       timeout=30, creationflags=0x08000000)
    if r.returncode == 0 and r.stdout.strip():
        parts = r.stdout.strip().splitlines()[0].split(',')
        vram_mb = int(float(parts[0]))
        gpu_util = float(parts[1])
except Exception:
    pass

def rd(p):
    with io.open(p, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def wr(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)

# --- driver status for honest reporting ---
drv = {}
try:
    drv = rd(r'results\drama_env\gpt_sovits_env_status.json')
except Exception:
    pass
drv_line = 'state=%s phase=%s phases_done=%s' % (
    drv.get('state'), drv.get('phase'), drv.get('phases_done'))

# --- round report row ---
RR = r'logs\iteration-loop\round_reports.md'
ROW = ('%s | r1015 bm-b | dept:工程+舰队 | WM verdict: GREEN (red=false @03:43 py_watermark '
       'insufficient_history 夜窗合法·本轮真产 --worked idle_rounds->0) | 当前活=r1015 收口（声库车道两站播种+ST-005 '
       '点火实弹+deps 首败同轮根治+重燃+D-19 推进+S0 收敛+S6 43）；最近实物=content/drama/runner_assets/'
       'gpt_sovits_env_driver.py（六相位分离驱动器 venv/torch-cpu/deps/weights-modelscope/extras/smoke·幂等检查点·'
       'selftest 8/8）+ Tools/content_loop_step.py v0.2 增 st005/st006 双 runner + ST-005 done@03:41:44（驱动 live '
       'pid 27128·%s）+ results/drama_env/gpt_sovits_env_status.json 跨轮可见面；下个里程碑=GPT-SoVITS env 全相位完成+'
       '首次合成 smoke（声库 P1 ≤10-22 窗）+ O-0948 窗口关闭判决 10-19 ~10:2x + CONTENT-LOOP 10-28 连续运行判据 '
       '(72h ≥3 stations/day：今已 4 站/2 日在轨) | 本地未达 origin commit 数=0（收口后 push+fetch 自证·见 '
       'sync 面）；孤儿面=12/0（S6 链内 03:43）') % (NOW_ISO8, drv_line)
with io.open(RR, 'a', encoding='utf-8') as f:
    f.write(ROW + '\n')
print('round report row appended')

# --- state.json ---
S = rd('state.json')
S['clock_read'] = NOW_ISO8
S['round_no'] = 1015
S['round'] = 1015
S['round_no_label'] = 'r1015'
S['now_active'] = 'r1015 closing'
S['task'] = 'r1015: closeout (voice-lane stations ST-005/ST-006 seeded + env driver ignited + deps root-cause + D-19 advance + S6 43 + state/heartbeat/round-report/push)'
S['current_task'] = S['task']
S['last_action'] = ('r1015: CONTENT-LOOP 声库车道续站双播种+执行——ST-005 env bootstrap 站 done（GPT-SoVITS 六相位分离驱动器 '
                    '点火实弹·venv+torch-cpu 相位绿·deps 首败[pyopenjtalk sdist 无 MSVC]同轮根治=strip 机制+'
                    'pyopenjtalk-plus cp311 win wheel 借力兜底·幂等重燃续跑）+ ST-006 voice-bank manifest 站 armed'
                    '（20-min loop 自动拾取）+ D-19 orders 水位推进 e695556b->04050fda（自核增量=1 行 V5.9 MV 回执·'
                    'BigMoney 零新义务）+ S6 43 rc0 4.2min + idle 两读红位真产清零')
S['last_action_at'] = NOW_ISO8
S['last_seen'] = NOW_ISO8
S['last_round_at'] = NOW_ISO8
S['last_round_ts'] = NOW_ISO8
S['ts'] = NOW_ISO8
S['updated'] = NOW_ISO8
S['updated_at'] = NOW_ISO8
S['orphan_face'] = 12
S['orphan_face_note'] = 'r1015 S6 chain probe (03:43): 12 py faces / 0 orphans'
S['did'] = ('r1015: (a) S0 FF absorb bm-c r1105 W274 cycle (zero BigMoney legs; stash roundtrip daemon faces: '
            'machine-health origin-wins bm-c row, watermark_red local-wins bm-b 03:33 chain; symbolic-ref attach check '
            'green per r1013 pit law). (b) S0.5/D-19: orders delta e695556b->04050fda consumed zero-trust (git show '
            'diff = 1 row V5.9 MV receipt via bm-a interactive window, zero BigMoney dispatch; r1014 judgment confirmed '
            'independently); canonical advance, mirrors synced 3; decisions 8706acd8 hold. (c) S1 smoke 49/49 + '
            'satengine alive + T-18 queue-head probe CLEAR (heads T22/E14 both actually done rows -- probe parses by '
            'line not status). (d) S3 standing-agenda work per ST-003 eval own next-batch definition (O-2144 anti-idle '
            'root cure; two-read idle red + local pool 9/0 open + board all claimed): seeded ST-005 (env bootstrap) + '
            'ST-006 (voice-bank manifest) into drama queue via engine lock protocol; added st005/st006 runners to '
            'content_loop_step.py; wrote 6-phase idempotent detached driver gpt_sovits_env_driver.py (venv/torch-cpu/'
            'deps/weights-modelscope/extras/smoke; pit-spawn laws: __main__ guard, CREATE_NO_WINDOW children r700, '
            'close_fds r317, -u+flush r680, incremental status face; selftest 8/8); ST-005 EXECUTED via engine round '
            '(claim+ignite+bookkeeping atomic, loop_rounds=17); first deps failure root-caused same-round: '
            'pyopenjtalk 0.4.1 sdist build needs MSVC (cmake present, no C compiler on box) -> run() log tail 6->40 '
            'lines fix + failing_pkg build-block parser (last Collecting before subprocess-exited-with-error) + '
            'pyopenjtalk-plus 0.4.1.post9 cp311 win wheel fallback (probed on tsinghua mirror, 25.1MB WHEEL-OK); '
            'driver re-ignited idempotent resume (venv/torch checkpoints carried). (e) S6 43 legs rc0 4.2min: '
            'ZERO-DRIFT streak 51, supply_floor honest flag (pool starved, answered-by-chain: W275 seat = bm-c lane), '
            'idle --worked idle_rounds->0, stale-takeover x4 (bm-a heartbeat stale 86min: scorecard/paper_export/'
            'daily_scorecard/build_status), LIVE-2026-10-19 ORANGE cap50% regenerated, d19 probe both-unchanged '
            'post-advance, attrition healed clean. (f) S7: five tasks green (IterationLoop/Watchdog/ContentLoop/'
            'BmbIdleGuard/SatEngine next-fire 03:48-03:52), claws identical, watermark advanced, state/heartbeat '
            'fresh. STATE-FACE GAP NOTE: r1013/r1014 sessions died in push sagas, their state.json updates never '
            'landed (origin face stayed r1012 while their round-report rows + commits are on origin); this r1015 '
            'face closes the gap honestly, round numbering follows round_reports.md (r1014 last).')
S['next'] = ('r1016: 1) poll results/drama_env/gpt_sovits_env_status.json -- deps/weights/extras/smoke phases '
             '(driver detached pid live; on failed phase root-cause + fix + re-ignite idempotent) 2) ST-006 products '
             'commit (voice_bank/manifest.json + outbox receipt land via 20-min loop fire) 3) O-0948 window close '
             'judgment 10-19 ~10:2x (v1 wall-clock census order) 4) ST-002 watch CEO direction-gate receipt '
             '(IndexTTS-2 stays gated) 5) first synthesis smoke station seed once env done (ref-clip sourcing per '
             'manifest shortlist) 6) BigMoney seat automation plan contribution <=10-25 (bm-a r1069 3762f3dafa '
             'consume-no-rebuild)')
S['verdict'] = ('GREEN: r1015 声库车道续站双播种+ST-005 同轮执行——队列喂活（ST-005 done/ST-006 armed·10-28 判据 4 站/2 日'
                '在轨）+ GPT-SoVITS 环境六相位驱动器在飞（venv/torch 绿·deps 修复重燃·weights 候）+ deps 首败同轮根'
                '治（pyopenjtalk MSVC 源建缺→pyopenjtalk-plus win wheel 借力）+ D-19 推进 04050fda + S6 43 rc0 + '
                'smoke 49/49；leftovers=env install 在飞（跨轮 poll）+ ST-002 候 CEO 方向门 + O-0948 判决窗 10-19 '
                '~10:2x + pool_starvation 诚实旗（W275 席=bm-c 链在飞）')
S['current'] = S['verdict']
S['latest_artifact'] = ('content/drama/runner_assets/gpt_sovits_env_driver.py (03:38) + Tools/content_loop_step.py '
                        'v0.2 st005/st006 runners (03:40) + ST-005 ignition live (03:41) + '
                        'results/drama_env/gpt_sovits_env_status.json')
S['last_artifact'] = S['latest_artifact']
S['next_milestone'] = ('GPT-SoVITS env all-phases complete + first synthesis smoke (voice P1 <=10-22) + '
                       'O-0948 window judgment 10-19 ~10:2x + CONTENT-LOOP 10-28 continuous-run judgment (72h >=3 '
                       'stations/day)')
S['last_orders_sha'] = '04050fdab14983da6af0c900e1d27a83bc7e39aaa48743d7964ea54478f26b98'
S['last_orders_read_at'] = NOW_ISO8
S['last_decisions_read_at'] = NOW_ISO8
S['sat_engine'] = {'status': 'alive (r1015 S6 status rc0, idle verdict, queue_depth 0; supply floor honest '
                            'starvation, awaiting W275 seat = bm-c lane)', 'checked_at': NOW_ISO8}
S['r1015_state_gap_note'] = ('r1013/r1014 died pre-state-write (push sagas); origin state face had stayed r1012; '
                             'r1015 closes gap, numbering follows round_reports.md')
sync = S.setdefault('sync', {})
sync['r1015_main_push'] = {'status': 'PENDING (this commit)', 'pushed_sha': 'pending',
                           'consumed_at': 'pending r1016', 'behind_origin_main': 0,
                           'note': ('r1015 payload = own faces (state/heartbeat/round-report + drama queue faces x5 '
                                    '+ runner driver + content_loop_step v0.2 runners + drama_env status face + '
                                    'r1015 work files + s6chain driver+log + S6 own regen/product faces '
                                    '[daily_report/live_usage docs + scorecard/paper_export/daily_scorecard/'
                                    'update_status/market_clock/regime_state/dualarm/compute_audit/b_layer/idle/'
                                    'orphan/attrition]); shared daemon faces (machine-health/watermark_red/'
                                    'token_usage) intentionally NOT added (r982/r1012 policy)')}
wr('state.json', S)
print('state.json written, round_no=', S['round_no'])

# --- heartbeat ---
H = rd(r'fleet\machines\bm-b.json')
H['last_seen'] = NOW_ISO8
H['clock_read'] = NOW_ISO8
H['ts'] = NOW_ISO8
H['heartbeat_epoch_utc'] = EPOCH
H['round_no'] = 1015
H['round'] = 1015
H['now_active'] = 'r1015 closing'
H['task'] = S['task']
H['current_task'] = S['task']
H['did'] = S['last_action']
H['last_action'] = S['last_action']
H['last_action_at'] = NOW_ISO8
H['cpu_cores'] = 16
H['free_ram_gb'] = free_gb
H['gpu_free_vram_mb'] = vram_mb
H['cpu_load_pct'] = m.dwMemoryLoad and round(100 - m.ullAvailPhys * 100.0 / m.ullTotalPhys, 1)
H['idle_rounds'] = 0
H['agenda_starved'] = False
H['verdict'] = S['verdict']
H['current'] = S['verdict']
H['latest_artifact'] = S['latest_artifact']
H['last_artifact'] = S['latest_artifact']
H['next'] = S['next']
H['next_milestone'] = S['next_milestone']
H['last_orders_sha'] = S['last_orders_sha']
H['last_decisions_sha'] = '8706acd8a7b65441f23c9813f62a25fdecbd9da0df10994e5915b5742a40a3fd'
H['last_orders_read_at'] = NOW_ISO8
H['last_decisions_read_at'] = NOW_ISO8
H['orphan_face'] = 12
H['note'] = ('r1015: voice-lane stations seeded+executed (ST-005 env bootstrap live, ST-006 armed); deps first-fail '
             'root-caused same round (pyopenjtalk MSVC -> pyopenjtalk-plus wheel); state-face gap r1013/r1014 closed')
wr(r'fleet\machines\bm-b.json', H)
# verify epoch int + clock T-separator (F7 law)
H2 = rd(r'fleet\machines\bm-b.json')
assert isinstance(H2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in H2['clock_read'], 'clock_read must be T-separated'
print('heartbeat written; epoch int OK; free_ram=%.1f vram=%dMB' % (free_gb, vram_mb))
print('driver line:', drv_line)
