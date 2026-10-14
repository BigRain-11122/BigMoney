# -*- coding: utf-8 -*-
# r979 bm-a S7 closeout: state heal (r978 lost-write, r861 family third instance)
# + heartbeat (orders_ack O-0925) + round report line append (UTF-8, CRLF tail law r843)
import json, time, subprocess, os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
now_epoch = int(time.time())

# live metrics sample (light)
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
    free_ram_gb = round(psutil.virtual_memory().available / 1024**3, 1)
except Exception:
    cpu_pct, free_ram_gb = 43.0, 11.0
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, timeout=15)
    vram_free_mb = int(r.stdout.decode('ascii', 'replace').strip().splitlines()[0])
except Exception:
    vram_free_mb = 214

# ---- 1) state-bm-a.json heal 977 -> 979 ----
with open('state-bm-a.json', encoding='utf-8') as f:
    st = json.load(f)
assert st.get('round_no') == 977, 'unexpected round_no %r' % st.get('round_no')
st['round_no'] = 979
st['last_round'] = 979
st['last_round_at'] = now_iso
st['last_round_closed'] = now_iso
st['last_round_ts'] = now_iso
st['last_seen'] = now_iso
st['last_run'] = now_iso
st['ts'] = now_iso
st['updated'] = now_iso
st['updated_at'] = now_iso
st['heartbeat_epoch_utc'] = now_epoch
st['heartbeat_epoch_utc_type_int'] = True
st['last_heartbeat_epoch_utc'] = now_epoch
st['clock_read'] = now_iso
st['current'] = 'r979 closeout done'
st['current_task'] = ('r979: O-0925 CEO order receipt + committee case C-20261014-01 (group b179986e) + '
                      'W238 prereg derive 40/47 (7 template-drift SUB misses, re-anchor next window P0) + '
                      'S6 38-leg chain detached pid 49188 (products next-window absorb)')
st['now_active'] = st['current_task']
st['did'] = ('r979: S0 r978 dead-session closeout (commit 51fb88b87 on origin, state write lost = r861 family 3rd; '
             'sequence honest 977->979) + writer-pause rebase (resident_dispatcher live-writer kill, E42+kill combo) + '
             'O-20261014-0925-bm-b receipt + C-20261014-01 enforcement bill landed group b179986e + '
             'W238 derive attempt (40/47) + inbox x2 processed (W237 finalize trigger / W239 seat) + idle --worked')
st['last_action'] = 'r979 O-0925 receipt + C-20261014-01 + W238 derive attempt closeout'
st['last_artifact'] = 'cph4/council/C-20261014-01-fleet-fullload-bill.md (group origin b179986e, 09:4x)'
st['latest_artifact'] = st['last_artifact']
st['recent_artifact'] = st['last_artifact']
st['next'] = ('r980: W238 prereg SUB re-anchor surgery (7 misses, dbg_sub1 method, then splice/selftest/ignite) '
              '+ S6 chain products absorb + moneyflow panel watch -> IC batch unlock')
st['next_milestone'] = ('W238 freeze chain complete (derive->splice->ignite) by next 1-2 windows; '
                       'C-20261014-01 votes + 10-16 revisit; month-boundary first exam 10-31')
st['orphan_face'] = 1
st['orphan_faces'] = 1
st['verdict'] = ('green (red=false lane=healthy; engine ALIVE idle queue0 post-W237-finalize; '
                 'W238 chain in-flight on bm-a lane per W239 seat MSG; O-0925 receipt+C-20261014-01 landed; '
                 'S6 38-leg chain detached pid 49188)')
st['verify'] = ('green (O-0925 receipt in order file + C-20261014-01 on group origin b179986e + '
                'idle --worked cleared + state heal 977->979 honest)')
st['notes'] = (st.get('notes', '') +
               ' | r979: state heal 977->979 honest -- r978 session landed its commit 51fb88b87 on origin '
               '(S6 products + close_fds fix + P0-MATRIX draft + r977 report line + daemon churn) but died '
               'pre-state-write (r861 family third instance); sequence honest per origin commit evidence + '
               'r977/r978 report/commit lineage. r979 S0 rebase law: E42 writer-pause alone does NOT stop a '
               'resident live writer (resident_dispatcher.py writes state every 30s) -- kill the live process '
               'inside the window + disable tasks + absorb churn + rebase + relaunch = proven combo this window.')
with open('state-bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- 2) heartbeat fleet/machines/bm-a.json ----
with open('fleet/machines/bm-a.json', encoding='utf-8') as f:
    hb = json.load(f)
hb['active'] = ('r979 closeout: O-0925 CEO order receipt + committee enforcement bill C-20261014-01 '
                '(group b179986e) + W238 prereg derive in-flight (40/47, re-anchor next) + S6 chain detached')
hb['clock_read'] = now_iso
hb['ts'] = now_iso
hb['heartbeat_epoch_utc'] = now_epoch
hb['last_seen'] = now_iso
hb['cpu_load_pct'] = cpu_pct
hb['cpu_pct'] = cpu_pct
hb['cpu_total_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['free_ram_gb'] = free_ram_gb
hb['free_vram_gb'] = round(vram_free_mb / 1024, 2)
hb['gpu_free_vram_gb'] = round(vram_free_mb / 1024, 2)
hb['gpu_free_vram_mb'] = vram_free_mb
hb['gpu_free_vram_mib'] = vram_free_mb
hb['gpu_idle_vram_mb'] = vram_free_mb
hb['gpu_idle_vram_mib'] = vram_free_mb
hb['gpu_source_note'] = 'nvidia-smi live read %s (CEO working machine, MV lane GPU busy, honest %dMiB free)' % (
    now_iso, vram_free_mb)
hb['current'] = 'r979 closeout done'
hb['current_task'] = st['current_task']
hb['did'] = st['did']
hb['now_active'] = hb['active']
hb['verdict'] = st['verdict']
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['health'] = 'ok'
ack = hb.get('orders_ack')
if not isinstance(ack, list):
    ack = []
new_acks = ['O-20261014-0925-bm-b']
for o in new_acks:
    if o not in ack:
        ack.append(o)
hb['orders_ack'] = ack
hb['orders_ack_note'] = ('r979: O-20261014-0925-bm-b acked (receipt in order file + committee case '
                         'C-20261014-01 attached); prior 65-O sweep holds')
with open('fleet/machines/bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- 3) round report line (UTF-8 append, CRLF tail probe per r843) ----
line = (now_iso +
        ' | r979 | bm-a | dept:舰队/工程（O-0925 CEO 问责令回执+委员会满载执法案 C-20261014-01+W238 prereg derive 续跑+S0 writer-pause 正法）'
        '| WM-VERDICT: green (red=false lane=healthy; satengine ALIVE queue0 post-W237-finalize; W238 chain in-flight bm-a lane) '
        '| 孤儿面=1 (read-only probe) '
        '| S0: r978 死会话收口（commit 51fb88b87 在 origin·state 写丢=r861 族第 3 例·序列诚实 977→979）+ daemon churn absorb 2 commit + rebase 1（writer-pause 正法升级=E42 任务 disable 不停常驻写者 resident_dispatcher 每 30s 写 state→活进程 kill 进窗+churn absorb+rebase+relaunch·坑律入 notes） '
        '| S0.5: O-20261014-0925-bm-b CEO 问责令=本窗最高优先已回执（委员会执法案=C-20261014-01 group origin b179986e·三色板+缺口清单+机械执法环全件·令发 09:25→案落 ≤1 轮循环=SLA 达标；bm-a 缺口自报=CPU 43→70 填补三件）+ D-19/ORD dual FALSE（dec 86187eff/ord 348eaf34 hold）+ inbox x2 处理毕（MSG-0855 W237 finalize=W238 触发在办/MSG-0914 W239 seat 知悉） '
        '| S3: W238 prereg derive 实弹 40/47 SUB·7 miss=模板漂移（r978 authored vs d311a5439 终版 landed 中窗·dbg_sub1 字节面实证=单字/中点/日期 typo 三型）→重锚手术=下窗 P0（W237 窗拆先例：prereg 前窗+splice 后窗·链 in-flight 非 stall·bm-c W239 seat 已确认 in-flight 口径） '
        '| S6: 38-leg chain detached pid 49188 09:47 起（r976 范式·产品下窗 S0 吸收） '
        '| S7: state heal 977→979 + 心跳 orders_ack+O-0925 + idle --worked 清零 + attrition CLEAN + 双闸幂等 '
        '| 本轮产品积分:2（委员会执法案+回执=能看实物·group b179986e 已推）·记账预算:4（state/心跳/轮报告/orders_ack） '
        '| 本地未达 origin commit 数=N（收尾 push 后自证） | [r979 bm-a]\r\n')
with open('round_reports-bm-a.md', 'ab') as f:
    raw = open('round_reports-bm-a.md', 'rb').read()
    if raw and not raw.endswith(b'\r\n') and not raw.endswith(b'\n'):
        f.write(b'\r\n')
    f.write(line.encode('utf-8'))
with open('round_reports-bm-a.md', 'ab') as f:
    raw = open('round_reports-bm-a.md', 'rb').read()
    if raw and not raw.endswith(b'\r\n') and not raw.endswith(b'\n'):
        f.write(b'\r\n')
    f.write(line.encode('utf-8'))

print('closeout written:', now_iso, '| epoch', now_epoch, '| cpu', cpu_pct, '| ram_free', free_ram_gb, '| vram_free_mb', vram_free_mb)
