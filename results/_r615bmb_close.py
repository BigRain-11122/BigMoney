import json, time, datetime, psutil

now = datetime.datetime.now(datetime.timezone.utc).astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

vm = psutil.virtual_memory()
free_gb = round(vm.available / 1024**3, 2)
cpu_pct = psutil.cpu_percent(interval=1)

try:
    import subprocess
    q = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, creationflags=0x08000000)
    gpu_free_gb = round(int(q.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    gpu_free_gb = None

hb_path = 'fleet/machines/bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8-sig'))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['round_no'] = 615
hb['round_no_label'] = 'round 615 (bm-b)'
hb['current_task'] = ('dual NULLS burns alive (VALUE 157/2000 pid34396 since 04:38, QUALITY 72/2000 pid57116 since 07:26) '
                      '+ kill-advice MSG-2026-10-03-1132 to bm-a re VALUE-NULLS double-burn (r489 invisible-claim: our claim 10:24 was '
                      'merge-blocked from origin; bm-a launch-claimed 10:44); DIVLOWVOL NULLS/SENS claims fuse-blocked after 4/4 detached '
                      'launch deaths under 3.85GB free RAM (inline run healthy; re-attempt at >=8GB headroom)')
hb['verdict'] = ('round 615 done: WM=insufficient_history (holiday window, red=false green lane); smoke 47/47; S6 34/34 rc0 '
                 '(dualrun streak 4 green >= flip gate, flip left to separate session per law); attrition CLEAN; orders 150/150 zero-new; '
                 'D-19 unchanged 4167b784 (python-bytes case-normalized); merge concluded 5cddd6817 unblocked fleet view; '
                 'DELIVERABLES: kill-advice MSG-2026-10-03-1132 + merge closure + double-burn diagnosis + DIVLOWVOL launch-death root-cause hypothesis')
hb['cpu_util_pct'] = cpu_pct
hb['free_ram_gb'] = free_gb
hb['idle_ram_gb'] = free_gb
hb['ram_avail_gb'] = free_gb
hb['ram_free_gb'] = free_gb
hb['gpu_idle_vram_gb'] = gpu_free_gb
hb['ts'] = iso
hb['updated'] = iso
hb['updated_at'] = iso
with open(hb_path, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

chk = json.load(open(hb_path, encoding='utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written, epoch int OK:', chk['heartbeat_epoch_utc'], '| cpu:', cpu_pct, '| free RAM:', free_gb, '| gpu free:', gpu_free_gb)

# round report line
line = ('2026-10-03T11:38:00+08:00 | r615 bm-b | dept:工程/舰队 | [watermark verdict: insufficient_history（国庆假期窗重置·red=false 绿牌面·引擎 idle 池 gated 合法）] | '
        '当前活: 双 NULLS 烧录在飞（VALUE 157/2000 pid34396·QUALITY 72/2000 pid57116）+ r489 双烧治理；'
        '最近实物: fleet/inbox/MSG-2026-10-03-1132-bmb-bma.md（11:32 kill-advice 落盘）+ merge commit 5cddd6817（10:5x r614 遗留 MERGE_HEAD 收口·池面 newer-wins）；'
        '下个里程碑: VALUE-NULLS 双烧裁定回执（bm-a 侧 kill+release 或反向让路·窗 ≤24h）→ NULLS 两批烧完 settle 翻面（VALUE ETA ~30h+·QUALITY 随后） | '
        '本轮做了: S0 r614 遗留未收口 merge 定谳（MERGE_HEAD 存在+origin 领先 1 commit=bm-a autofill 10:44:48 claim fund-value-p1-nulls·staged 面与 origin/wt 三方内容恒等 362 entries 已核）→git commit 收口 5cddd6817；'
        'S0.5 orders 150/150 零新令+D-19 python 字节哈希 4167B784≡state 键（case-normalized 零消费·r617 律）+inbox 零未读；S1 smoke 47/47；S2 板零 open（106 done/45 claimed/1 in_progress）；S3 饱和引擎 status rc0 活（idle·queue 0）；'
        'r489 隐形认领双烧定谳：本机 VALUE-NULLS claim 10:24:10 因 merge 在飞未达 origin→bm-a 10:44:48 launch-claim=合法接管但双烧（本机烧录 6.4h 在飞 mtime 新鲜）→kill-advice MSG-1132 已发（后到让路律·bm-a QUALITY 侧 off-caliber fuse 已contained 无需动作）；'
        'DIVLOWVOL 4/4 分离态发射即死定谳（x1/x2/nulls/sens 全 47B 日志止于 todo 行·inline 复跑健康存活 5min+·__main__ 守卫在位·r613 probe 曾全过）→假设=RAM 压迫面（free 3.85GB<4GB 共享机纪律禁重活）非代码 bug·NULLS/SENS 两 claim 暂 fuse-blocked 待 RAM≥8GB 头寸再试；'
        'S6 34/34 rc0（dualrun streak=4 连绿≥flip 门·flip 留另轮会话动作·reconcile 先于 audit 顺序合规）+attrition CLEAN（2 旧 shrink healed）；'
        'S4 记忆零 append（四问门：r489 族新实例非新律·DIVLOWVOL 根因未确认不入册）| 验证证据: smoke 47/47 输出+S6 日志 results/_r615bmb_s6_runner.log+guard results/_attrition_guard_scan.json+nulls.jsonl mtime 11:00/10:59 | '
        '下轮指针: ①VALUE-NULLS bm-a 回执消费②RAM≥8GB 时 DIVLOWVOL NULLS/SENS 重试发射（fuse crash-count 面·若仍拒按 fuse 律上报）③merge_lane_views sync_face 幂等补 settle 一次（S0 环律·池面 replay 后补）| 本地未达 origin commit 数=见收口后自证行')
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write('\n' + line + '\n')
print('round report appended')
