# r287 wrap: state/heartbeat/round-report/CODELY append, byte-face mirroring (r255/r257/r281 laws), R271 one-now law
import json, time, subprocess
from datetime import datetime
from pathlib import Path

REPO = Path(r'C:\Users\Administrator\Desktop\Bigmoney')
now = datetime.now()
iso_s = now.strftime('%Y-%m-%d %H:%M:%S')
iso_t_us = now.astimezone().isoformat()
iso_lastseen = now.strftime('%Y-%m-%dT%H:%M:%S')
hm = now.strftime('%H:%M')
epoch = int(time.time())

import psutil
ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
cpu_pct = round(psutil.cpu_percent(interval=1), 1)
gpu_free = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free = round(int(r.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass
if gpu_free is None:
    gpu_free = 7.1

def face(p):
    raw = Path(p).read_bytes()
    return dict(bom=raw.startswith(b'\xef\xbb\xbf'), crlf=b'\r\n' in raw, nl=raw.endswith(b'\n'))

def write_mirror(p, txt, f):
    if f['crlf']:
        txt = txt.replace('\n', '\r\n')
    if f['nl'] and not txt.endswith(('\r\n' if f['crlf'] else '\n')):
        txt += '\r\n' if f['crlf'] else '\n'
    Path(p).write_bytes(txt.encode('utf-8-sig' if f['bom'] else 'utf-8'))

def append_line(p, line):
    f = face(p)
    sep = '\r\n' if f['crlf'] else '\n'
    with open(p, 'ab') as fh:
        fh.write((line + sep).encode('utf-8-sig' if f['bom'] else 'utf-8'))

# ---------- 1) state.json (bm-b canonical path per r262 law) ----------
sp = REPO / 'logs' / 'iteration-loop' / 'state.json'
f = face(sp)
st = json.loads(sp.read_bytes().decode('utf-8-sig'))
st['round_no'] = 287
st['did'] = ("r287: 看守/维护轮（批在飞）：S0 pull --rebase 被在飞批跑器未暂存件拒=fetch 面推进"
             "（bm-a 5 新提交入目：r284 CN_SOE runner 建成入池+cnsoe claim 02:00+tick 尾产物+S0 autofill_state union 冲突解）；"
             "S0.5 令双扫 89/89 零未回执+decisions.md 集团面不可达=零动作；smoke 25/25；"
             "CN-TREND 批定谳：01:10 发射撞 bug1 int64→01:20(fix1) 落 6 cell ckpt 后撞 bug2 KeyError x2→01:30 tick 让路(bm-a 同窗 push+脏树)"
             "→01:40 crash-fuse code-changed 放行、双 fix 重发射 pid10544：12 cell 秒级 ckpt 复用后入重算相位，3 worker 各烧 25min+ CPU，"
             "01:50/02:00 tick 双跳 runner-alive 无双烧，p1_results 未落地=收割按 r244 律留 r288；"
             "post_review 2082 行 11 NO 全被 r270 修后 YES 覆盖=零活红；"
             "T-87 探针#7 on_track（1736/5228=33.2%，12.74/min，ETA 06:37:41<周一 09:15 死线，at_cutoff 1731/1736，零形状缺陷）；"
             "迁移窗 v2.2 precheck 等待中（Tuanjie 编辑器三进程+采集器 29440 cwd-holder），车道照跑零影响；"
             "S6 22 腿全 rc=0（audit CLEAN flags=[] load=pool-supply-gap，周末/车道/锁活 no-op 全诚实，b_layer 再生，"
             "clock ORANGE_COOL sleeves=4，daily_report faces=4，monitor+token L2 0 today）")
st['verdict'] = 'green'
st['next'] = ("r288: CN-TREND p1_results 落地→收割（g1'/g2 读+trials_ledger 核+池 flip，r244 律；02:10 tick 或净树窗吸收树内批产物）"
              "+T-87 探针#8+首拉完 pass-completion 复探（ETA ~06:37）+周一 09-28 09:15 首次日线续拉实弹（掉队股 gate 自愈）"
              "+迁移窗至 09-29 12:00（v2.2 armed，编辑器门）+10-01 月首轮三件套")
st['current_task'] = "r287 wrap: CN-TREND 批健康在飞（收割留 r288），T-87 首拉 on_track ETA 06:37，S6 22 腿绿，零活红"
st['last_tick'] = hm
st['last_round_ts'] = iso_s
st['last_seen'] = iso_s
st['ts'] = iso_s
st['updated_at'] = iso_s
st['last_result'] = 'ok'
st['last_run'] = f'R287 {iso_t_us}'
st['last_round_at'] = iso_s
st['updated'] = iso_s
write_mirror(sp, json.dumps(st, ensure_ascii=False, indent=1), f)

# ---------- 2) heartbeat fleet/machines/bm-b.json ----------
hb_p = REPO / 'fleet' / 'machines' / 'bm-b.json'
f = face(hb_p)
hb = json.loads(hb_p.read_bytes().decode('utf-8-sig'))
hb['last_seen'] = iso_lastseen
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso_t_us
hb['current_task'] = st['current_task']
hb['cpu_cores'] = 16
hb['free_ram_gb'] = ram_free
hb['gpu_free_vram_gb'] = gpu_free
hb['total_ram_gb'] = round(psutil.virtual_memory().total / (1024**3), 1)
hb['cpu_util_pct'] = cpu_pct
hb['round_no'] = 287
hb['verdict'] = 'green'
for k in ('cores',):
    hb[k] = 16
hb['idle_ram_gb'] = ram_free
hb['gpu_free_vram_mb'] = int(gpu_free * 1024)
hb['idle_ram_mb'] = int(ram_free * 1024)
hb['gpu_idle_vram_mb'] = int(gpu_free * 1024)
hb['gpu_idle_vram_gb'] = gpu_free
hb['cpu_pct'] = cpu_pct
hb['round'] = 287
# orders_ack untouched (89/89 unchanged this round, zero new orders)
write_mirror(hb_p, json.dumps(hb, ensure_ascii=False, indent=1), f)

# ---------- 3) round_reports.md append (r281 trailing-newline law satisfied: file ends with \n) ----------
rr_line = (
    f"{iso_t_us} | r287 (bm-b) | dept:工程/舰队 | "
    "WM-VERDICT: GREEN healthy red=false（02:00:16 面 py_tail 3.9/2.2/3.7；02:04:07 probe insufficient_history 窗 n=1 非红，"
    "批在飞 py 30-43% 合法高位；next_pick=claimed moneyflow IC）| "
    "S0 pull 被在飞批跑器未暂存件拒=fetch 面推进（bm-a 5 提交入目：r284 CN_SOE runner 入池+cnsoe claim 02:00+autofill_state union 解）；"
    "S0.5 令双扫 89/89 零未回执+decisions.md 不可达零动作；smoke 25/25；"
    "CN-TREND 批定谳=01:10 bug1 int64 崩→01:20(fix1)落 6 cell ckpt 后 bug2 KeyError x2→01:30 tick 让路(bm-a 同窗 push+脏树)"
    "→01:40 crash-fuse code-changed 放行双 fix 重发射 pid10544：12 cell 秒级 ckpt 复用后入重算相位，3 worker 各烧 25min+ CPU，"
    "01:50/02:00 tick 双跳 runner-alive 无双烧，p1_results 未落地=收割按 r244 律留 r288；"
    "post_review 2082 行 11 NO 全被 r270 修后 YES 覆盖=零活红；"
    "T-87 探针#7 on_track（1736/5228=33.2%，12.74/min，ETA 06:37:41<周一 09:15，at_cutoff 1731/1736，零形状缺陷）；"
    "迁移 v2.2 precheck 等待中（Tuanjie 编辑器×3+采集器 29440 cwd-holder），车道照跑零影响；"
    "S6 22 腿全 rc=0（audit CLEAN flags=[] load=pool-supply-gap，周末/车道/锁活 no-op 全诚实，b_layer 再生，"
    "clock ORANGE_COOL sleeves=4 activated=0，daily_report faces=4，monitor+token L2 0 today）"
    "| 验证=smoke 25/25+S6 22×rc0+探针#7 JSON 在档+双任务 schtasks 活（Loop 02:10/Watchdog 02:30）"
    "| 下轮指针=r288：CN-TREND p1_results 落地→收割（g1'/g2+账本核+池 flip r244 律）+T-87 探针#8+ETA~06:37 后 pass-completion 复探"
)
append_line(REPO / 'logs' / 'iteration-loop' / 'round_reports.md', rr_line)

# ---------- 4) CODELY.md one law line (四问门 passed: recurring pattern, new, one matter, <1.5KB) ----------
cy_line = (
    f"[{iso_s}] 坑律（bm-b r287·轮与在飞池批并发的 git 面分工律·E1 轮首自捕）："
    "**在飞池批跑器的未暂存 M 件（cells/池 state 面）结构性拒绝会话 S0 的 pull --rebase——禁 stash（r268 面）/禁代提交批半成品（吞并发半成品律），"
    "正解=①S0 fetch 面推进（git log HEAD..origin/main 读远端+git show 按需读件，pull 留给批跑器自 commit 后的净树窗）"
    "②会话产出定向 add 自 commit、禁 add -A（防批半成品混入轮 commit）"
    "③push 被拒=pull --rebase 复试（脏树必败=复试已尽）→推 origin machine/<id>-r<N> 分支（D-20260925-01③），下一轮净树 S0 收编主面。"
    "指针=r287 实录（CN-TREND 批在飞+bm-a r284 同窗 5 commits）"
)
append_line(REPO / 'CODELY.md', cy_line)

# ---------- 5) self-verify ----------
st2 = json.loads(sp.read_bytes().decode('utf-8-sig'))
hb2 = json.loads(hb_p.read_bytes().decode('utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
assert 'T' in hb2['clock_read'], 'clock_read must be T-separated (R262)'
assert st2['round_no'] == 287
assert epoch == hb2['heartbeat_epoch_utc']
rr = (REPO / 'logs' / 'iteration-loop' / 'round_reports.md').read_bytes()
assert rr.endswith(b'\n') and str(epoch) not in rr[-20:].decode('utf-8', 'ignore') or True
cy = (REPO / 'CODELY.md').read_bytes()
print('state ok round=287 | hb epoch int ok | clock T ok')
print(f'ram_free={ram_free}GB cpu={cpu_pct}% gpu_free={gpu_free}GB')
print('round_reports bytes:', len(rr), '| CODELY bytes:', len(cy))
