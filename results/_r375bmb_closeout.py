# -*- coding: utf-8 -*-
"""r375 bm-b closeout: round-report line + CODELY pit-law append + conditional
hot-cold fold (<=10KB hard line, D-20260924-01 paradigm) + state round_no 375
+ heartbeat (epoch int law R170/R178, re-read self-verify r128)."""
import io, json, time, datetime

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S') + ('+%02d:%02d' % (now.utcoffset().seconds // 3600, (now.utcoffset().seconds // 60) % 60) if now.utcoffset() else '')
epoch = int(time.time())

# ---------- 1) round report line (CRLF, byte append) ----------
rr_line = (
    ts + " | round 375 bm-b | dept:工程/舰队 (push-storm reconcile 收口轮) | "
    "WM-VERDICT: 绿 (red=false; probe 10:18 py_low_with_work_cands=合法§四回执: census W2B 4-worker 在飞 i=3399/5620 结构性占车道 + 板 0 open/0 bandit + pool 2 ready 候 RAM 门 2.17GB<4GB r354 未过=census 完释放后续批 autofill C8 接管, 非怠工) | "
    "did: (1) S0 身份锚定 bm-b (machine.json) + pull --rebase 撞 r374 逃逸分支回汇重放窗 (a0ee1d53 onto origin 5da13a8e) -> 12-UU 分类器全 auto 0 UNKNOWN -> results/_r375bmb_resolve.py (r374 范式): 8 snapshot take stage-2 (origin bm-c r154 面 10:00-10:01 ts 探针全新于本机 09:5x) + REPORT-0928 双件 twin-locked 同侧 stage-2 (r373 双子同侧律) + compute_audit history union 83+83->84 零丢失 + dashboard_status.js whole-bytes stage-2 (R209) -> 12 面 parse-verified marker-free -> rebase --continue 三连拒发 (GIT_EDITOR=true / core.editor=true 均败 = r358 族拒发面再证) -> r355-addendum 直连收口: commit -F .git/rebase-merge/message (64390067) -> rebase --quit -> update-ref -> cherry-pick 余件: bd3363e6 撞活写面 (autofill live tick 10:10:02 vs pick 10:00:02, launches 字节恒等=活面严格超集) -> r369 活面新者胜: 活面直落 13a730c5 替代 addendum + 陈 pick 跳过零丢失; aa6c4f34 干净落 2629c141 (仅 3 件本机单写残差) -> push LANDED 5da13a8e..2629c141 = r374 escape branch machine/bm-b-r374 reconcile 使命闭环 (全程零 force-push) "
    "(2) S0.5 orders 99/99 双扫 (轮首+S7) 零未回执 + 集团 decisions.md 本机缺位零动作 + firm/DECISIONS.md 09-26 后零新行 "
    "(3) S1 smoke 25/25 "
    "(4) S2 job_list 0 + 票板 0 open/37 claimed 全有主 "
    "(5) S3 witness: census W2B pid28820 4-worker 活性实证 (checkpoint mtime 10:12:33 新鲜) + 实测速率 ~9行/min -> ETA 修正≈14:1x (r374 估 10:40 过乐观) + RAM 2.17GB 三采样门未过 = judge flips W1/MASS x4/W2/W3 继续合法 RAM-gated 诚实缓 "
    "(6) S6 30 腿全 rc=0 + 3 新bar门合法 skip (pre-market Monday 无新 bar): audit CLEAN / scorecard+daily_scorecard+t35_export+build_status=lane_io 守卫诚实 skip (bm-a 心跳 19min fresh, r378 守卫在位实证) / market_clock CALL-2026-09-24 cell=ORANGE_COOL / 本机车道 astock_daily 面板新鲜零网络 no-op + rev_osc SIG/BARS 幂等 no-op / 客宿主族 (heat/repo/options/moneyflow/sina_mf/ths/ah) 全诚实 no-op / bm-c 车道 fund_premium no-op / daily_report REPORT-2026-09-28 再生 faces=4 token=1 / token_meter L1 0 today (crash-fuse 拒发 4 计 3 签在册) "
    "(7) S7 自愈: schtasks 双任务在位 (R49 律) + loop pin=2 no-op + watchdog 幂等重建 first-fire 10:40 + precommit claw in-sync "
    "| verified: 12 面 resolve 逐件 parse-verify + compute_audit 84 行=并集零丢失 + push fast-forward 落地 + 双扫零 + smoke 25/25 + S6 30 腿 rc=0 "
    "| next: census W2B finalize (ETA≈14:1x) -> RAM 释放后三采样窗 -> W1/MASS x4/W2/W3 judge flips (bm-b=flip executor) -> burns -> finalize x5 -> W2/W3 intake -> V2-P1 un-defer; 15:30 新 bar 窗 = astock_daily/rev_osc 车道 + live.paper/t35/t24_prospect 三腿随新 bar"
)
with io.open('logs/iteration-loop/round_reports.md', 'ab') as f:
    f.write(rr_line.encode('utf-8') + b'\r\n')
print('1) round report line appended', len(rr_line.encode('utf-8')), 'B')

# ---------- 2) CODELY.md pit-law append (LF, byte append) ----------
codely_new = (
    "- [" + ts[:16].replace('T', ' ')[:15].replace('-', '-') + " r375 bm-b] 坑律：**逃逸分支 reconcile 重放自家陈 addendum 撞活写面＝r369 活面新者胜律的 cherry-pick 面**——活面 launches 恒等+last_tick 较新=严格超集→活面直落为替代 addendum（r372 先例）+陈 pick 跳过零丢失；continue 拒发窗 r355-addendum 直连实测闭环（commit -F message→rebase --quit→update-ref→cherry-pick 余件）。指针=results/_r375bmb_resolve.py+13a730c5/2629c141。\n"
)
d = io.open('CODELY.md', 'rb').read()
with io.open('CODELY.md', 'ab') as f:
    f.write(codely_new.encode('utf-8'))
size_after = len(d) + len(codely_new.encode('utf-8'))
print('2) CODELY append', len(codely_new.encode('utf-8')), 'B -> total', size_after, 'B')

# ---------- 3) conditional hot-cold fold (hard line 10,000B conservative) ----------
folded = False
if size_after > 10000:
    lines = io.open('CODELY.md', 'r', encoding='utf-8').read().split('\n')
    # find the oldest dated hot entry (r154 bm-c line)
    target_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith('- [2026-09-28 10:0x r154 bm-c]'):
            target_idx = i
            break
    assert target_idx is not None, 'r154 entry not found for fold'
    moved = lines[target_idx]
    pointer = ("冷层指针：坑律正典 2026-09-28 四十五批（r375 bm-b 窗·水位律当窗整编：CODELY.md append 后超 ≤10KB 硬线）："
               "r154 共享 md 台账 replace 锚律 一条全文 verbatim=archive 202609.md『坑律归档 2026-09-28 四十五批』节（行级零丢失校验）。")
    lines[target_idx] = pointer
    out = '\n'.join(lines)
    io.open('CODELY.md', 'w', encoding='utf-8', newline='\n').write(out)
    # archive append (CRLF)
    arch = io.open('research/memory-archive/202609.md', 'r', encoding='utf-8').read()
    if not arch.endswith('\r\n'):
        arch += '\r\n'
    section = ("\r\n## 坑律归档 2026-09-28 四十五批（r375 bm-b 窗·水位律当窗整编：CODELY.md append 后超 ≤10KB 硬线）\r\n\r\n"
               + moved + "\r\n")
    io.open('research/memory-archive/202609.md', 'w', encoding='utf-8', newline='').write(arch + section)
    # zero-loss verify: moved line byte-identical in archive, absent in CODELY hot
    arch_now = io.open('research/memory-archive/202609.md', 'r', encoding='utf-8').read()
    hot_now = io.open('CODELY.md', 'r', encoding='utf-8').read()
    assert moved in arch_now, 'archive zero-loss FAIL'
    assert moved not in hot_now, 'hot residue FAIL'
    print('3) hot-cold fold DONE batch-45: moved', len(moved.encode('utf-8')), 'B -> hot now', len(hot_now.encode('utf-8')), 'B')
    folded = True
else:
    print('3) fold not needed (<=10,000B)')

# ---------- 4) state.json round_no 375 ----------
s = json.load(io.open('state.json', 'r', encoding='utf-8'))
s['round_no'] = 375
s['note'] = ("r375 bm-b push-storm reconcile closeout: escape branch machine/bm-b-r374 fully landed main "
             "(12-UU _r375bmb_resolve + r355 direct-connection + r369 live-face supersede); "
             "census W2B in-flight ETA~14:1x; judge flips RAM-gated not-yet")
io.open('state.json', 'w', encoding='utf-8', newline='\n').write(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
chk = json.load(io.open('state.json', 'r', encoding='utf-8'))  # r128 re-read self-verify
assert chk['round_no'] == 375
print('4) state.json round_no=375 re-read verified')

# ---------- 5) heartbeat (epoch int law + re-read assert) ----------
hb = json.load(io.open('fleet/machines/bm-b.json', 'r', encoding='utf-8'))
hb['last_seen'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['current_task'] = ("r375 done: push-storm reconcile landed (12-UU _r375bmb_resolve + r355 direct-connection + "
                      "live-face supersede 13a730c5); witness: census W2B i=3399/5620 alive pid28864 ETA~14:1x; "
                      "judge flips RAM-gated (2.17GB<4GB 3-sample not-yet); next: census finalize -> RAM 3-sample -> "
                      "W1/MASS x4/W2/W3 flips -> finalize x5 -> W2/W3 intake; 15:30 new-bar window astock_daily/rev_osc + live.paper trio")
hb['round_no'] = 375
import subprocess
free_ram = round(float(subprocess.run(['powershell','-NoProfile','-Command',
    '(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB'],
    capture_output=True, text=True).stdout.strip()), 1)
cpu = int(float(subprocess.run(['powershell','-NoProfile','-Command',
    '(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average'],
    capture_output=True, text=True).stdout.strip()))
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['idle_ram_mb'] = int(free_ram * 1024)
hb['free_ram_mb'] = int(free_ram * 1024)
hb['cpu_util_pct'] = float(cpu)
hb['cpu_pct'] = float(cpu)
hb['loop_round'] = 375
hb['round'] = 375
hb['verdict'] = ("healthy: smoke 25/25, S6 30 legs rc=0; RECONCILE DONE: r374 escape branch landed main 5da13a8e..2629c141 "
                 "(12-UU canon-resolved: 8 snapshot take-new stage-2 + REPORT twins same-side + audit union 83+83->84 + js whole-bytes; "
                 "_r375bmb_resolve.py; rebase-continue 3x refused r358 family -> r355-addendum direct-connection; "
                 "bd3363e6 superseded by live autofill face per r369 law); census W2B in-flight ETA~14:1x; "
                 "judge flips RAM-gated r354 not-yet; orders 99/99; board 0 open")
io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='\n').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
chk2 = json.load(io.open('fleet/machines/bm-b.json', 'r', encoding='utf-8'))  # R170/R178 re-read assert
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in chk2['clock_read'] and '+' in chk2['clock_read'], 'clock_read not T-separated'
print('5) heartbeat epoch int verified:', chk2['heartbeat_epoch_utc'], chk2['clock_read'], 'ram', free_ram, 'GB cpu', cpu)
print('CLOSEOUT ALL DONE, folded=', folded)
