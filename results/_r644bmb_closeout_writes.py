# r644 bm-b closeout writer (temp, deleted after run)
import json, time, os, subprocess

NOW_EPOCH = int(time.time())
import datetime
now = datetime.datetime.fromtimestamp(NOW_EPOCH).astimezone()
ISO = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
print('clock:', ISO)

# ---------- 1. round report append (mixed-encoding file: utf-8 append, no CRLF translation) ----------
block = f"""{ISO} | round 644 (bm-b, dept:工程/数据+研究): watermark verdict=GREEN (red=false; audit CLEAN burning-healthy; WM probe py_low_with_work_cands=合法〔local_batch_running=true 三守护烧批内在速率非违令〕; dualrun ZERO-DRIFT streak 36)
当前活: FUND 三族 NULLS 烧录在飞 Q396/V535/D268 of 2000（三守护进程 CIM 实证 pid 34396/57116/30208·append mtime<6min·dup_k=0；ETA V~10-06/Q~10-07/D~10-08，DIVLOWVOL 贴窗尾持续盯）+ finalize 窗 10-05..10-09（G-SEG 裁定待 GM·r638 insufficient-sample fallback 在位）
最近实物: S0 收口 merge 34eb31b08 DELIVERED（31 UU 三分类=r440 两分法完整实弹：29 S6 可再生面 origin-newer-wins+x2_watch union 双块保留+token_usage ours）+ 就绪探针刷新 results/finalize_trio_readiness.json 03:3x（G1=F G2=T G3=T G4=PENDING·双采样速率/ETA）
下个里程碑: 三族 NULLS 烧满 2000 → finalize+E1 判决落窗 10-05..10-09（探针 mechanical_ready 即执行；G-SEG 无裁定走 r638 单读判决）。窗 ≤48h 首查=烧录完成度
做了什么: S0 daemon treadmill 吸收 ccd3cbd46+merge origin 波（bm-a r656/bm-c r441）31 UU r440 配方+push DELIVERED；S0.5 令牌 152/152 首扫+收尾双扫零差+D-19 sparse-clone fallback MATCH EB14B510 零消费；S1 47/47；S2 板 165 票 0 open·job_list 空；S3 门全绿（WM red=false·engine alive rc0·常设线由在飞三族烧批满足·W14-GENERATE RAM 3.72GiB<4GB 闸正确排队）；post_review 两 NO 行核毕=00:00:04 瞬态已被 01:04/01:29 复审翻绿零欠账；S6 ~30 腿 rc0（周日黄金周诚实 no-op 族+车道护栏十腿；strategy_scorecard stale-takeover 合法〔bm-a hb 22min>20min 阈·本地+origin 双视图〕）；S7 四件幂等+attrition CLEAN+针位 2 no-op
验证证据: push_verify DELIVERED ahead=0 behind=0 tip 34eb31b08；smoke 47/47；三守护进程 CIM 实证活；nulls Q396/V535/D268 零 dup_k；dualrun streak 36；attrition scan CLEAN；double_scan orders=152/152 inbox=0
下轮指针: r645 = 烧录进位复跑 readiness 探针；mechanical_ready=true 且窗开即执行三族 finalize+E1（G-SEG 无裁定=r638 fallback）；DIVLOWVOL ETA 若劣化贴 10-09→评估合规提速面（禁池面整文件重放陷阱 r630 律）
本地未达 origin commit 数=0（push_verify DELIVERED·remote tip 恒等 34eb31b08）
"""
p = 'logs/iteration-loop/round_reports.md'
with open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(block)
print('round report appended')

# ---------- 2. heartbeat rewrite (preserve eol style) ----------
hp = 'fleet/machines/bm-b.json'
raw = open(hp, 'rb').read()
eol = b'\r\n' if b'\r\n' in raw else b'\n'
h = json.loads(raw.decode('utf-8'))
import psutil
vm = psutil.virtual_memory()
avail_gb_dec = round(vm.available / 1e9, 2)
total_gb_dec = round(vm.total / 1e9, 2)
gpu_free_mb = 2486  # 8192 - 5706 used per this round's compute_audit sample
h['last_seen'] = ISO
h['heartbeat_epoch_utc'] = NOW_EPOCH
h['clock_read'] = ISO
h['round_no'] = 644
h['round_no_label'] = 'round 644 (bm-b)'
h['current_task'] = ('FUND trio NULLS burn watch (daemons live Q/V/D=396/535/268 of 2000, dup_k=0, ETA V~10-06 Q~10-07 D~10-08; '
                     'finalize window 10-05..10-09 opens on mechanical_ready w/ r638 fallback) + r644 S0 31-UU merge wave DELIVERED 34eb31b08')
h['verdict'] = ('GREEN (smoke 47/47; S0 31-UU merge r440 recipe DELIVERED; readiness probe G2/G3 green G1-pending burns; '
                'dualrun ZERO-DRIFT streak 36; attrition CLEAN; engine alive rc0 idle; orders 152/152 double-scan zero-diff; trio burns healthy dup_k=0)')
h['ts'] = ISO
h['updated'] = ISO
h['updated_at'] = ISO
h['cpu_util_pct'] = psutil.cpu_percent(interval=0.3)
h['free_ram_gb'] = avail_gb_dec
h['idle_ram_gb'] = avail_gb_dec
h['total_ram_gb'] = total_gb_dec
h['ram_free_gb'] = avail_gb_dec
h['ram_avail_gb'] = avail_gb_dec
h['gpu_idle_vram_gb'] = round(gpu_free_mb / 1024, 2)
h['gpu_idle_vram_mb'] = gpu_free_mb
h['gpu_free_vram_gb'] = round(gpu_free_mb / 1024, 2)
h['gpu_free_vram_mb'] = gpu_free_mb
h['gpu_vram_free'] = gpu_free_mb
h['gpu_free_vram_mib'] = gpu_free_mb
h['ram_gb'] = total_gb_dec
txt = json.dumps(h, indent=1, ensure_ascii=False)
open(hp, 'wb').write(txt.replace('\n', eol.decode()).encode('utf-8'))
chk = json.loads(open(hp, encoding='utf-8').read())
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written; epoch int OK:', chk['heartbeat_epoch_utc'])

# ---------- 3. state.json remaining fields (line-level byte surgery, preserve eol) ----------
sp = 'state.json'
raw = open(sp, 'rb').read()
seol = b'\r\n' if b'\r\n' in raw else b'\n'
note_new = ('r644: watch/merge round -- S0 daemon treadmill absorb ccd3cbd46 + merge origin wave (bm-a r656 / bm-c r441) with 31 UU '
            'resolved per r440 two-branch recipe (29 S6 regenerable origin-newer-wins + x2_watch union both-blocks + token_usage ours-newer), '
            'push DELIVERED 34eb31b08 (ahead=0). S0.5 orders 152/152 double-scan zero-diff; D-19 sparse-clone fallback MATCH EB14B510 zero-consume. '
            'S1 47/47. S2 board 165 tickets 0 open. S3 gates green (WM red=false healthy; engine alive rc0; trial-labor standing line satisfied '
            'by in-flight trio NULLS burns; W14-GENERATE RAM 3.72GiB<4GB correctly queued). post_review two transient NO rows verified '
            're-derived YES same window. S6 ~30 legs rc0 (Golden-Week Sunday honest no-op family + lane guards; strategy_scorecard legal '
            'stale-takeover: bm-a hb 22min>20min both views; dualrun ZERO-DRIFT streak 36; audit CLEAN burning-healthy). S7 4/4 idempotent + '
            'attrition CLEAN. Lane: trio NULLS Q396/V535/D268 of 2000 dup_k=0, finalize window 10-05..10-09 w/ r638 fallback.').replace('"', '')
def set_field(raw, key, val):
    lines = raw.split(seol)
    out = []
    hit = 0
    for ln in lines:
        k = (' "%s":' % key).encode()
        if ln.startswith(k):
            hit += 1
            out.append((' "%s": %s' % (key, val)).encode())
        else:
            out.append(ln)
    assert hit == 1, (key, hit)
    return seol.join(out)
raw = set_field(raw, 'note', '"%s",' % note_new)
for key in ('last_round_at', 'ts', 'updated', 'last_seen', 'clock_read', 'last_decisions_read_at'):
    raw = set_field(raw, key, '"%s",' % ISO)
open(sp, 'wb').write(raw)
print('state fields updated')

# ---------- 4. CODELY.md pit line ----------
cline = ('- [2026-10-04 03:4x r644 bm-b] merge 收口守卫假阳性坑（r440 UU 处置 31 面实弹）：`git diff --cached --check` 对 CRLF JSON 面逐行报 '
         'trailing whitespace=rc≠0，但≠冲突标记残留——以 rc==0 为提交门的守卫会误拦已处置净的 merge commit（本例处置毕被 '
         'MARKER CHECK FAILED 假拦一步）；判别法=--check 输出含 conflict marker 字样才是真拦截面，纯 trailing whitespace=CRLF 噪声放行。'
         'How to apply：merge/收口提交守卫改为检查输出内容或 `git grep -l ^<<<<<<<`，勿单消费 rc。\n')
cp = 'CODELY.md'
craw = open(cp, 'rb').read()
if not craw.endswith(b'\n'):
    craw += b'\n'
open(cp, 'wb').write(craw + cline.encode('utf-8'))
print('CODELY pit line appended; new size =', os.path.getsize(cp))
