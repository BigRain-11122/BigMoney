# -*- coding: utf-8 -*-
"""r869 bm-c books: round report row + state-bm-c.json + heartbeat update.
Single-pass; head_sha pinned to pre-books HEAD (addendum pass flips to books sha).
r869 fix: heartbeat round counters synced (round_no/last_round/label/loop_round).
"""
import io, json, os, time, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime())
epoch = int(time.time())

def read(p):
    return io.open(os.path.join(ROOT, p), encoding='utf-8').read()

def write(p, s):
    io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='').write(s)

# ---- fresh probes ----
def probe_mem():
    try:
        import psutil
        vm = psutil.virtual_memory()
        return round(vm.available / 2**30, 1), round(vm.available * 100.0 / vm.total, 1)
    except Exception:
        return None, None

def probe_cpu():
    try:
        import psutil
        return round(psutil.cpu_percent(interval=1), 0)
    except Exception:
        return None

free_gb, free_pct = probe_mem()
cpu_pct = probe_cpu()

report_row = (
 "2026-10-11T11:52:00+08:00 | r869 bm-c: watermark verdict=绿（red=false·next_pick=moneyflow IC advisory carried·池 ready=0=E15 已烧 bm-b 11:12:33）"
 "·当前活=W17 judge-finalize 在飞（PID 20012·10:59:13 起·CPU 2548s 持续推进·344 胞判决聚合）+W208 落链守望（M10 cron 9defca39 armed）"
 "·最近实物=S6 43/43 rc0（_r869bmc_s6_log.txt·ZERO-DRIFT streak 9）"
 "·下个里程碑=W17 finalize 落地→intake+selftest+guard 收口（下一轮）；W208 上游落链→M10 自动 W209 冻结（窗≤48h 上游依赖）"
 " | ①S0-1 锚定 bm-c+round-zero probe py_faces=5 orphans=1（read-only 不击杀）；S0 autostash rebase 吸收 bm-b r877（E16 alphagen census leg-1+E15 queue row flip+T-184 bm-a push pending 披露·HEAD 重锚 014e6da16·autostash 零冲突）；"
 "②S0.5 常设组合器 rc0 双水位零 delta（ORD f90233c7+DEC 68d13893·r865 method-pin 律）+unacked 0；"
 "③S1 smoke 49/49；S2 板面：job 0·queue head 探针 T22/E14 双 CLEAR（E15-E16 链 bm-b 认领面禁碰）·池 non-done=[]（E15-EMOTION-REEVAL-P1-RUN bm-b 11:12:33 已烧毕·supply floor 回 0=bm-b 供给链面目标 ≥3 by 10-13）·引擎活 rc0 cycle 3062 queue_next=[]（W208 上游堵已知面）；"
 "④idle 闸未过（RAM 32.8-36%<40%·VRAM 1.49GB disclosure-only T-183）→无领单义务·--worked 清零（idle_rounds=0）；"
 "⑤W17 finalize 守望：PID 20012 CPU 2439→2548s 持续推进·产物四件（w17_judge/w17_reform_face/w17_paired_deltas/w17_intake）未落地=344 胞聚合长跑正常态（W16 40 胞先例的 8.6× 规模）→收口链留 r870 精确指针；"
 "⑥inbox：MSG-20261011-1108-bmb-e15-freeze（ALL·E15 冻结+入池声明）→池条目实证已由 bm-b 自烧（done@11:12:33·harvest e15-reeval-0of1.bm-b.json）→零撞建合规收讫+移入 processed 零动作回执；MSG-0940（bm-a 收件·T-184）留箱（期限 10-12 15:30·升级面归 GM 哨兵域）；"
 "⑦PRODUCT-A=**S6 43/43 rc0**（_r869bmc_s6_runner.ps1=r868 verbatim clone·bad=0：pool_dualrun ZERO-DRIFT **streak 9**/422 entries·周末 no-op 全净·compute_audit pool_ready=0 照录·alloc_paper rc=0〔本机持 510880.csv 完整副本·bm-b 侧 rc=2=T-184 dep honest 各自披露〕·daily_report/live_usage 再生·token_meter +1）；"
 "⑧S7：loop pin=5 no-op（next fire 11:45）+watchdog 重注册（fire 11:43）+双爪 idempotent 重装+attrition 4 台账 CLEAN（2 healed 注记）+W209 守望 cron 9defca39 armed"
 " | r870: (1) W17 finalize 落地检查（w17_judge.json+w17_reform_face.json+paired_deltas+账本 append·块 prev vs ledger_head 对账〔r807 律〕）→intake〔lawful-zero 实读〕→selftest〔r307 律〕→attrition guard→捕获律收口；(2) W208/W209 落链守望→M10 自动链维持；(3) T-184 期限观察（10-12 15:30·本机持 510880.csv 副本可应援）；(4) moneyflow IC prereg 待面板完备（周末 parked）；(5) 心跳轮计数器三面同步已修（r869 起）| 本轮产品积分：2（S6 43 腿链 streak 9=经营层可验实物+判决链守望推进）| 记账预算：3 面内（state+心跳+轮报=法定簿记）| 孤儿面=1（read-only）"
)

rep_path = os.path.join(ROOT, 'logs/iteration-loop/round_reports-bm-c.md')
with io.open(rep_path, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + report_row)

# ---- state ----
sp = os.path.join(ROOT, 'state-bm-c.json')
st = json.loads(io.open(sp, encoding='utf-8').read())
head_sha = subprocess.run(['git', 'rev-parse', '--short=9', 'HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip()

activity = ("当前活: W17 judge-finalize 在飞（PID 20012·10:59 起·344 胞判决聚合·CPU 持续推进）+W208 落链守望（M10 cron 9defca39 armed）"
            "| 最近实物: S6 43/43 rc0（_r869bmc_s6_log.txt·ZERO-DRIFT streak 9）@ "
            + now +
            " | 下个里程碑: W17 finalize 落地→intake+selftest+guard 收口（下一轮）；W208 上游落链→M10 自动 W209 冻结")
verdict = ("r869 close: 周末守望轮 3——S6 43/43 (ZERO-DRIFT streak 9) + W17 finalize 守望（PID 20012 在飞）"
           "+ ORD/DEC 零 delta + smoke 49/49 + attrition CLEAN + idle_rounds=0（--worked·闸未过无领单义务）+ 心跳计数器三面同步修复")
nxt = ("r870: (1) W17 finalize 落地检查→intake→selftest（r307 律）→attrition guard→ledger prev 对账（r807 律）→捕获律收口；"
       "(2) W208/W209 落链守望→M10 自动链（W211/W212 freeze-prep 先读 pit-engine-finalize.md）；"
       "(3) T-184 期限观察（10-12 15:30·GM 哨兵域·本机持 510880.csv 完整副本可应援）；"
       "(4) moneyflow IC prereg 待面板完备；"
       "(5) 轻量机会面 RAM≥40% 维持即续")

st.update({
    'clock_read': now, 'ts': now, 'updated': now, 'updated_at': now,
    'last_seen': now, 'last_seen_at': now, 'last_ts': now,
    'round_no': 870, 'round_no_label': 'r869',
    'last_round': 869, 'loop_round': 869,
    'last_round_at': now, 'last_round_closed': now, 'last_round_ts': now,
    'last_round_summary': verdict, 'last_round_summary_at': now,
    'last_action': 'r869 S6 43/43 (streak 9) + W17 finalize watch + E15 inbox receipt + heartbeat counter sync',
    'last_action_at': now,
    'current_task': activity, 'current_task_at': now, 'activity_now': activity,
    'verdict': verdict,
    'next': nxt, 'next_pointer': nxt, 'next_milestone': 'r870: W17 finalize 收口 + W208 落链守望（M10 自动链）',
    'latest_artifact': 'S6 43/43 rc0 (_r869bmc_s6_log.txt, ZERO-DRIFT streak 9) + E15 inbox zero-action receipt',
    'last_artifact': 'S6 43/43 rc0 (_r869bmc_s6_log.txt, ZERO-DRIFT streak 9)',
    'recent_artifact': 'S6 43/43 rc0 (_r869bmc_s6_log.txt, ZERO-DRIFT streak 9)',
    'idle_rounds': 0, 'agenda_starved': False,
    'heartbeat_epoch_utc': epoch,
    'orphan_face': 1, 'orphan_faces': 1,
    'last_orders_at': now, 'last_decisions_at': now,
    'last_decisions_read_at': now, 'last_orders_read_at': now,
    'head_sha': head_sha,
    'note': 'r869 = weekend watch round 3: S6 43/43 (streak 9); W17 finalize in-flight watch (PID 20012); E15 inbox receipt (already burned by bm-b); idle gate not green (RAM 32.8-36%); heartbeat counter sync fix (round_no/last_round/label).',
    'verify': 'receipts: smoke 49/49 + results/_r869bmc_s6_log.txt (43/43 rc0 bad=0, ZERO-DRIFT streak 9) + results/_attrition_guard_scan.json (4 ledgers CLEAN) + Tools/s05_probe.py zero-delta + idle_trigger --worked (idle_rounds=0) + this books commit/push_verify',
})
if free_gb is not None:
    st.update({'free_ram_gb': free_gb, 'idle_ram_gb': free_gb, 'ram_free_gb': free_gb})
if cpu_pct is not None:
    st['cpu_pct'] = int(cpu_pct); st['cpu_util_pct'] = int(cpu_pct); st['cpu_idle_pct'] = int(100 - cpu_pct)
st['sync'] = {'ahead_behind': 'r869 books commit pending', 'origin_tip': head_sha, 'ts': now,
              'note': 'r869 books pass; addendum flips sync face post-push'}
io.open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=1))

# ---- heartbeat (r869: full face incl. round counters) ----
hp = os.path.join(ROOT, 'fleet/machines/bm-c.json')
hb = json.loads(io.open(hp, encoding='utf-8').read())
hb.update({
    'last_seen': now, 'ts': now, 'clock_read': now, 'current_task': activity,
    'current_task_at': now, 'activity_now': activity, 'heartbeat_epoch_utc': epoch,
    'idle_rounds': 0, 'agenda_starved': False,
    'round_no': 870, 'round_no_label': 'r869', 'last_round': 869, 'loop_round': 869,
    'last_round_at': now, 'last_round_closed': now, 'last_round_ts': now,
    'last_round_summary': verdict, 'last_round_summary_at': now,
    'verdict': verdict, 'note': st['note'], 'verify': st['verify'],
    'next': nxt, 'next_pointer': nxt, 'next_milestone': st['next_milestone'],
    'latest_artifact': st['latest_artifact'], 'last_artifact': st['last_artifact'],
    'recent_artifact': st['recent_artifact'],
    'last_action': st['last_action'], 'last_action_at': now,
    'last_seen_at': now, 'updated_at': now, 'updated': now, 'last_run_at': now, 'last_ts': now,
    'last_pulled_at': now,
})
if free_gb is not None:
    hb['free_ram_gb'] = free_gb; hb['idle_ram_gb'] = free_gb; hb['ram_free_gb'] = free_gb
if cpu_pct is not None:
    hb['cpu_pct'] = int(cpu_pct); hb['cpu_util_pct'] = int(cpu_pct); hb['cpu_idle_pct'] = int(100 - cpu_pct)
hb['gpu_free_vram_mb'] = 1490; hb['gpu_free_vram_mib'] = 1490
io.open(hp, 'w', encoding='utf-8', newline='').write(json.dumps(hb, ensure_ascii=False, indent=1))

# ---- self-proof ----
chk = json.loads(io.open(sp, encoding='utf-8').read())
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
hbk = json.loads(io.open(hp, encoding='utf-8').read())
assert isinstance(hbk['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert hbk['idle_rounds'] == 0
assert hbk['round_no'] == 870 and hbk['last_round'] == 869, 'hb counters must be synced'
print('r869 books OK: round_no=870 last_round=869 epoch=%d clock=%s ram_free=%s pct=%s cpu=%s' % (epoch, now, free_gb, free_pct, cpu_pct))
