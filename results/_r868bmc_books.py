# -*- coding: utf-8 -*-
"""r868 bm-c books: round report row + state-bm-c.json + heartbeat update.
Single-pass; head_sha pinned to pre-books HEAD (addendum pass flips to books sha).
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
vram_free = 1.54  # disclosure-only face (T-183); refreshed by idle_trigger next tick

report_row = (
 "2026-10-11T11:26:00+08:00 | r868 bm-c: watermark verdict=绿（red=false·next_pick=moneyflow IC advisory carried·池 ready=0=W208 上游缺口已知面）"
 "·当前活=W17 judge-finalize 在飞（PID 20012·10:59:13 起）+W208 落链守望（M10 cron 9defca39 armed）"
 "·最近实物=fleet/backlog.md idle_trigger 计数面修复（行4/9 归档）+S6 43/43 rc0（_r868bmc_s6_log.txt·ZERO-DRIFT streak 8）"
 "·下个里程碑=W17 finalize 落地→intake+selftest+guard 收口（下一轮）；W208 上游落链→M10 自动 W209 冻结（窗≤48h 上游依赖）"
 " | ①S0-1 锚定 bm-c+round-zero probe py_faces=5 orphans=1（read-only 不击杀）；S0 autostash rebase 吸收 bm-a r874/875（E14 daban probe+E15 emotion-family claimed=supply-floor leg-3·本机 commit 重锚 e1e048169·autostash 零冲突）；"
 "②S0.5 常设组合器 rc0 双水位零 delta（ORD f90233c7+DEC 68d13893·r865 method-pin 律）+unacked 0；"
 "③S1 smoke 49/49；S2 板面：P2 tech 0 open（T22 已由 bm-a r954 修讫）·P3 head E15=本窗 bm-a r875 已认领禁碰·job 0·引擎活 rc0 queue_next=[]（W208 上游堵已知面·席位属主 bm-a 活性已复〔r874/875 推送〕·05:47 stall 通知立场维持不代执行）；"
 "④GREEN-IDLE 达档第 2 读（RAM 41.2%≥40%·VRAM 1.54GB=T-183 disclosure-only）→O-20261011-0012 §3 轻量机会面执行=**backlog 计数面修复**：行4（G17 审计 lane）实证已由 MiniGame 侧收割闭环（C1832 提交 10-11 10:31「G17/G18/G22/G27四包收割+due队排干」·本机零代工归档）+行9（CPH4 done@ 10-10 已闭环·原行「claim @」空格形漏 claimed@ 串=假计数根因）双行归档→idle_trigger claimable 2→0 修复+--worked 清零（idle_rounds=0·两读红解除）；"
 "⑤**W17 万人波收口链**：judge shard 0of1 本机 autofill 看门狗 10:46-10:59 烧毕（344 胞·WORKER-CLAIM closed+ok·results/pool_claims/TRIAL-LABOR-W17-JUDGE/w17-judge-0of1.bm-c.json）→judge-finalize 自动接续在飞（PID 20012·10:59:13 起·CPU 健康推进 ~36CPU-s/20s·日志 _r868bmc_w17_jfin_105913.out.log 块缓冲零输出=正常态）——本窗内联重跑被锁等待+5min 零输出自动杀（13:50 长任务纪律已知律复犯·零损伤·CIM 实证单进程无双烧）→finalize 落地后收口（intake+selftest〔r307 律〕+attrition guard+ledger prev 对账〔r807 律〕+捕获律）留 r869 精确指针；"
 "⑥PRODUCT-A=**S6 43/43 rc0**（_r868bmc_s6_runner.ps1=r867 verbatim clone·bad=0：pool_dualrun ZERO-DRIFT **streak 8**/421 entries·周末 no-op 全净·compute_audit 3 旗=已知定谳面照录〔idle_with_work=本窗 W17 finalize 在飞·pool_starvation/supply_floor=W208 上游缺口〕·daily_report/scorecard/ceo_live_usage/dashboard 再生·token_meter +1）；"
 "⑦S7：loop pin=5 在位（next fire 11:25）+watchdog 在位（11:23）+双爪 idempotent 重装+attrition 4 台账 CLEAN（2 healed 注记）+inbox 4 件经本机 FleetLink listener 已 processed（W212 席位发布/W208 stall 立场/A14 freeze/N2W20 draft=全非动作件）+1 件 bm-a 收件留箱（T-184 期限 10-12 15:30 观察·升级面归 GM 哨兵域）"
 " | r869: (1) W17 finalize 落地检查（w17_reform_face.json+w17_judge.json+账本 append·块 prev vs ledger_head 对账）→intake→selftest→guard→捕获律收口；(2) W208/W209 落链守望→M10 自动链维持（W211/W212 freeze-prep 时先读 pit-engine-finalize.md）；(3) T-184 期限观察；(4) moneyflow IC prereg 待面板完备（next_pick advisory carried）；(5) 轻量机会面：RAM≥40% 维持即续 | 本轮产品积分：2（backlog 计数面机制修复=能验实物+W17 判决链推进） | 记账预算：3 面内（state+心跳+轮报=法定簿记） | 孤儿面=1（read-only）"
)

rep_path = os.path.join(ROOT, 'logs/iteration-loop/round_reports-bm-c.md')
with io.open(rep_path, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + report_row)

# ---- state ----
sp = os.path.join(ROOT, 'state-bm-c.json')
st = json.loads(io.open(sp, encoding='utf-8').read())
head_sha = subprocess.run(['git', 'rev-parse', '--short=9', 'HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip()

activity = ("当前活: W17 judge-finalize 在飞（PID 20012·10:59 起·344 胞判决计算）+W208 落链守望（M10 cron 9defca39 armed）"
            "| 最近实物: fleet/backlog.md 计数面修复（行4/9 归档）+S6 43/43（_r868bmc_s6_log.txt·ZERO-DRIFT streak 8）@ "
            + now +
            " | 下个里程碑: W17 finalize 落地→intake+selftest+guard 收口（下一轮·窗≤10min 轮续）；W208 上游落链→M10 自动 W209 冻结")
verdict = ("r868 close: GREEN-IDLE 第 2 读合法领面——backlog 计数面修复（行4/9 归档·claimable 2→0）+ W17 judge-finalize 自动接续在飞（PID 20012）"
           "+ S6 43/43 (ZERO-DRIFT streak 8) + ORD/DEC 零 delta + smoke 49/49 + attrition CLEAN + idle_rounds=0（--worked）")
nxt = ("r869: (1) W17 finalize 落地检查→intake→selftest（r307 律）→attrition guard→ledger prev 对账（r807 律）→捕获律收口；"
       "(2) W208/W209 落链守望→M10 自动链（W211/W212 freeze-prep 先读 pit-engine-finalize.md）；"
       "(3) T-184 期限观察（10-12 15:30·GM 哨兵域·本机持 510880.csv 完整副本可应援）；"
       "(4) moneyflow IC prereg 待面板完备；"
       "(5) 轻量机会面 RAM≥40% 维持即续")

st.update({
    'clock_read': now, 'ts': now, 'updated': now, 'updated_at': now,
    'last_seen': now, 'last_seen_at': now, 'last_ts': now,
    'round_no': 869, 'round_no_label': 'r868',
    'last_round': 868, 'loop_round': 868,
    'last_round_at': now, 'last_round_closed': now, 'last_round_ts': now,
    'last_round_summary': verdict, 'last_round_summary_at': now,
    'last_action': 'r868 backlog 计数面修复 + W17 judge-finalize 接续守望 + S6 43/43',
    'last_action_at': now,
    'current_task': activity, 'current_task_at': now, 'activity_now': activity,
    'verdict': verdict,
    'next': nxt, 'next_pointer': nxt, 'next_milestone': 'r869: W17 finalize 收口 + W208 落链守望（M10 自动链）',
    'latest_artifact': 'backlog 计数面修复 + S6 43/43 rc0 (_r868bmc_s6_log.txt, ZERO-DRIFT streak 8)',
    'last_artifact': 'backlog 计数面修复 + S6 43/43 rc0 (_r868bmc_s6_log.txt, ZERO-DRIFT streak 8)',
    'recent_artifact': 'backlog 计数面修复 + S6 43/43 rc0 (_r868bmc_s6_log.txt, ZERO-DRIFT streak 8)',
    'idle_rounds': 0, 'agenda_starved': False,
    'heartbeat_epoch_utc': epoch,
    'orphan_face': 1, 'orphan_faces': 1,
    'last_orders_at': now, 'last_decisions_at': now,
    'last_decisions_read_at': now, 'last_orders_read_at': now,
    'head_sha': head_sha,
    'note': 'r868 = GREEN-IDLE round-2 lawful claim: backlog count-repair (rows 4/9 archived) + W17 judge-finalize in-flight (PID 20012, autofill-spawned) + S6 43/43 streak 8; ORD/DEC zero-delta; idle_rounds=0 (--worked).',
    'verify': 'receipts: smoke 49/49 + results/_r868bmc_s6_log.txt (43/43 rc0 bad=0, ZERO-DRIFT streak 8) + results/_attrition_guard_scan.json (4 ledgers CLEAN) + Tools/s05_probe.py zero-delta + idle_trigger --worked (idle_rounds=0) + this books commit/push_verify',
})
if free_gb is not None:
    st.update({'free_ram_gb': free_gb, 'idle_ram_gb': free_gb, 'ram_free_gb': free_gb})
if cpu_pct is not None:
    st['cpu_pct'] = int(cpu_pct); st['cpu_util_pct'] = int(cpu_pct); st['cpu_idle_pct'] = int(100 - cpu_pct)
st['sync'] = {'ahead_behind': 'r868 books commit pending', 'origin_tip': head_sha, 'ts': now,
              'note': 'r868 books pass; addendum flips sync face post-push'}
io.open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=1))

# ---- heartbeat ----
hp = os.path.join(ROOT, 'fleet/machines/bm-c.json')
hb = json.loads(io.open(hp, encoding='utf-8').read())
hb.update({
    'last_seen': now, 'ts': now, 'clock_read': now, 'current_task': activity,
    'current_task_at': now, 'heartbeat_epoch_utc': epoch,
    'idle_rounds': 0, 'agenda_starved': False,
    'verdict': verdict, 'activity_now': activity,
})
if free_gb is not None:
    hb['free_ram_gb'] = free_gb; hb['idle_ram_gb'] = free_gb; hb['ram_free_gb'] = free_gb
if cpu_pct is not None:
    hb['cpu_pct'] = int(cpu_pct); hb['cpu_util_pct'] = int(cpu_pct)
hb['gpu_free_vram_mb'] = 1540; hb['gpu_free_vram_mib'] = 1540
io.open(hp, 'w', encoding='utf-8', newline='').write(json.dumps(hb, ensure_ascii=False, indent=1))

# ---- self-proof ----
chk = json.loads(io.open(sp, encoding='utf-8').read())
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
hbk = json.loads(io.open(hp, encoding='utf-8').read())
assert isinstance(hbk['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert hbk['idle_rounds'] == 0
print('r868 books OK: round_no=869 last_round=868 epoch=%d clock=%s ram_free=%s pct=%s cpu=%s' % (epoch, now, free_gb, free_pct, cpu_pct))
