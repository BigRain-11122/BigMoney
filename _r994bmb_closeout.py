# -*- coding: utf-8 -*-
# r994 bm-b closeout: O-20261017-1751 P0 leg-1 (IndexTTS-2.5 detached deploy in flight)
# + E1 leg-5 taildrop re-queue + MSG-2203 + S6 41rc0 + S7 registers green.
import subprocess, json, os, sys, glob, time, datetime

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
NOWC = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
EPOCH = int(time.time())

def git(*a, timeout=180, cwd=BM):
    r = subprocess.run(['git', '-C', cwd] + list(a), capture_output=True, timeout=timeout)
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()

# ---------- 1. heartbeat ----------
ack_list = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BM, 'fleet', 'orders', 'O-*.md')))
print('ORDERS_ACK_LIST=%d' % len(ack_list))

did = ("r994: 当前活=O-20261017-1751 P0 执行腿一：IndexTTS-2.5 分离部署驱动器在飞（clone+uv+sync 三段已毕·ModelScope 权重 5.11G 下载中）；"
       "最近实物=media/drama-tools/repos/index-tts 克隆+.venv 189 包（21:52 stage3 OK）+deploy_indextts_r994.py 驱动器（pid 26764·分离存活）+drama 试点五件 Taildrop 重推 bm-a+MSG-2203 取件请求（22:03）；"
       "下个里程碑=《一路长虹》前三集对白配音样件上链（O-20261017-1751 窗·≤10-18 17:5x·r995 收部署+首产）。孤儿面=12/0；watermark=insufficient_history（red=false·周末池空板空合法 idle 白名单·P0 在飞 --worked）")
heart = {
    "machine_id": "bm-b",
    "last_seen": NOW,
    "task": "r994: closeout",
    "did": did,
    "cpu_cores": 16,
    "free_ram_gb": 13.8,
    "gpu_free_vram_mb": 7549,
    "cpu_load_pct": 9,
    "verdict": ("GREEN: O-20261017-1751 P0 dispatched leg-1 — IndexTTS-2.5 detached deployment driver alive (stages 1-3 OK: gh-proxy clone, uv bootstrap, "
                "uv sync webui extra 189 pkgs; stage 4 ModelScope weights 5.11G downloading at closeout); next round harvests + drama_voicegen pilot per runbook B.4-III; "
                "E1 leg-5: drama pilot 5 files (15.7MB) taildrop re-queued to bm-a, peer file-layer not replying, MSG-2203 pickup request sent; "
                "O-2110 CDN leg honest-deferred (needs TJ-MCP interactive window); "
                "D-19 zero new delta since r993 consumption (orders e0dcbd80 holds, decisions 1d4741e4 holds; watermark-file advance pending); "
                "S6 chain 41/41 rc0; S7 registers green (loop pin=2, watchdog re-registered S4U, both claws installed, attrition 4 CLEAN); "
                "BigHouse T-3 honest-deferred to next rounds (P0 deploy window priority)"),
    "idle_rounds": 0,
    "agenda_starved": False,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "ts": NOW,
    "orders_ack": ack_list,
    "note": ("r994: deploy driver = DETACHED_PROCESS pattern (astock machine-proven); log=media/drama-tools/deploy_indextts_r994.log; "
             "DONE marker=deploy_indextts_r994.DONE.json; taildrop bg task may outlive round (tailscaled holds queue)"),
    "latest_artifact": "media/drama-tools/repos/index-tts clone + .venv (189 pkgs, 21:52) + deploy driver log (stages 1-3 OK) + MSG-20261017-2203 taildrop pickup request",
    "codely_live_count": 2,
    "round_no": 994,
    "round": 994,
    "current_task": "r995: harvest IndexTTS-2.5 deploy (DONE marker + aux models first-gen) + drama_voicegen EP001-003 pilot (O-20261017-1751) + BigHouse T-3 + MSG-2203 pickup verify",
    "next": ("r995: 1) read deploy_indextts_r994.DONE.json / log tail; if DONE -> write drama_voicegen.py per runbook B.4-III (use_qwen_emo=False, API batch), "
             "first-gen triggers aux model auto-download (~5.3G w2v-bert+BigVGAN+MaskGCT+CAMPPlus), generate EP001-003 dialogue samples -> receipt to results/ "
             "2) verify MSG-2203 pickup by bm-a (taildrop) 3) BigHouse T-3 安家流程 4) d19 watermark-file advance (scripts/d19_watermark.py) "
             "5) O-2110 CDN leg still awaits TJ-MCP window"),
}
with open(os.path.join(BM, 'fleet', 'machines', 'bm-b.json'), 'w', encoding='utf-8') as fh:
    json.dump(heart, fh, ensure_ascii=False, indent=1)

# ---------- 2. state.json surgical update ----------
sp = os.path.join(BM, 'state.json')
with open(sp, encoding='utf-8') as fh:
    st = json.load(fh)
st['round'] = 994
st['round_no'] = 994
st['round_no_label'] = 'r994'
st['clock_read'] = NOW
st['ts'] = NOW
st['updated'] = NOW
st['updated_at'] = NOW
st['last_seen'] = NOW
st['last_round_at'] = NOW
st['last_round_ts'] = NOW
st['current_task'] = heart['current_task']
st['did'] = ("r994: (a) P0 O-20261017-1751 leg-1 executed: IndexTTS-2.5 detached deployment driver spawned (pid 26764, DETACHED_PROCESS astock-proven pattern), "
             "stages 1-3 OK by 21:52 (gh-proxy clone -> media/drama-tools/repos/index-tts; uv bootstrap via aliyun; uv sync --extra webui 189 pkgs), "
             "stage 4 ModelScope weights 5.11G (IndexTeam/IndexTTS-2.5) downloading at closeout; driver idempotent-resumable, log+DONE marker in "
             "media/drama-tools/. (b) E1 leg-5: drama pilot 5 files (PILOT 7.8MB + seg1-3 + sea-review md, 15.7MB total) taildrop re-queued to bm-a at 21:47; "
             "peer file-layer 'not replying' (tailscaled up, relay sin); MSG-20261017-2203 pickup request written to fleet/inbox/; O-2110 CDN leg "
             "honest-deferred (needs TJ-MCP interactive window, not available in headless loop). (c) D-19 probe 21:44: decisions zero-delta (1d4741e4), "
             "orders origin == e0dcbd80 (r993-consumed delta, no new rows); watermark FILE not yet advanced (r993 gap, r995 todo via scripts/d19_watermark.py). "
             "(d) S6 chain 41/41 rc0 (orphan 12 faces/0, smoke green, dualrun streak, 4 shared faces stale-takeover derive per O-2100 s2.4 as bm-a hb stale 246min). "
             "(e) S7: loop task pin=2 no-op, watchdog re-registered (S4U SWA=false), pre-commit+pre-push claws reinstalled, attrition scan 4 ledgers CLEAN. "
             "(f) BigHouse T-3 honest-deferred (P0 deploy window priority). (g) r992-numbered work files were r993's; this round's work files carry r994 names.")
st['last_action'] = "r994: P0 deploy driver in flight (stages 1-3 OK) + taildrop re-queue + MSG-2203 + S6 41rc0 + S7 green"
st['last_action_at'] = NOW
st['next'] = heart['next']
st['next_milestone'] = "IndexTTS-2.5 deploy DONE + EP001-003 voiceover samples receipt on chain before 10-18 17:5x (O-20261017-1751 window)"
st['verdict'] = heart['verdict']
st['current'] = "r994: P0 dispatch leg-1 + closeout"
st['latest_artifact'] = heart['latest_artifact']
st['last_artifact'] = heart['latest_artifact']
st['now_active'] = "r994 closed; deploy driver detached-alive into next rounds (DONE marker awaited)"
st['orphan_face'] = 12
st['orphan_faces'] = 12
st['orphan_face_note'] = "r994 round-start probe (21:44): 11 py faces / 0 orphans; S6 chain re-probe 21:55: 12 faces / 0 orphans"
st['sat_engine'] = {"status": "alive (r994 S6 status rc=0, last_verdict idle)", "checked_at": NOW}
st['last_orders_probe_at'] = NOW
st['last_orders_at'] = NOW
st['orders_delta_pending'] = False
st['last_decisions_probe_at'] = NOW
st['last_decisions_at'] = NOW
st['decisions_delta_pending'] = False
st['d19_probe_due_note'] = "r994 21:44 probe: origin orders == e0dcbd80 (r993-consumed), decisions == 1d4741e4; watermark-file advance pending r995"
st.setdefault('sync', {})['r994_main_push'] = {
    "status": "PENDING (this commit)", "pushed_sha": "pending", "consumed_at": "pending r995",
    "behind_origin_main": 0,
    "note": "r994 payload = own faces (state/heartbeat/round report + S6 log + MSG-2203 + closeout/s6chain work files); surgery on fresh origin tip; docs regen faces per r982 policy",
}
with open(sp, 'w', encoding='utf-8') as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# ---------- 3. round report row ----------
rr = os.path.join(BM, 'logs', 'iteration-loop', 'round_reports.md')
row = ("{t} | r994 | watermark=insufficient_history（red=false·周末池空板空合法 idle 白名单·P0 在飞 --worked 清零）"
       "｜P0 O-20261017-1751 腿一执行：IndexTTS-2.5 分离部署驱动器点火（pid 26764·astock 分离范式）·三段 21:52 前 OK（gh-proxy 克隆/uv 引导/uv sync webui 189 包）·第四段 ModelScope 权重 5.11G 下载在飞收轮（幂等可续·DONE 验收件候 r995）；"
       "E1 腿五：drama 试点五件 15.7MB Taildrop 21:47 重推 bm-a（对端文件层 not replying·MSG-20261017-2203 取件请求已发）·O-2110 CDN 腿诚实缓办（需 TJ-MCP 活窗）；"
       "D-19 探针 21:44=零新增量（orders e0dcbd80=r993 已消费·decisions 1d4741e4 不变·水位文件推进欠账记 r995）；"
       "S6 链 41/41 rc0（孤儿 12/0·smoke 绿·四共享面 stale-takeover 合法接管·bm-a hb 陈旧 246min）；"
       "S7 四件绿（loop pin=2·watchdog 重注册 S4U·双爪重装·attrition 4 CLEAN）；BigHouse T-3 诚实缓办（P0 部署窗优先）；"
       "本地未达 origin commit 数=23（外科净路·折叠设计态·S0 自拉平）"
       "｜证据=media/drama-tools/deploy_indextts_r994.log（stages 1-3 OK）/_r994bmb_s6_log.txt 41rc0/D19 双探 21:44/attrition _attrition_guard_scan.json/MSG-20261017-2203"
       "｜r995: 收部署 DONE 件+辅模首产+drama_voicegen EP001-003 试产样件（O-20261017-1751 窗 ≤10-18 17:5x）+BigHouse T-3+d19 水位文件推进+MSG-2203 取件验证\n").format(t=NOWC)
with open(rr, 'a', encoding='utf-8') as fh:
    fh.write(row)

# ---------- 4. BM-repo own-face surgery push on fresh origin tip ----------
rcf, _ = git('fetch', 'origin')
rc, tip = git('rev-parse', 'origin/main')
print('FETCH rc=%d ORIGIN=%s' % (rcf, tip[:12]))
tmpidx = os.path.join(BM, '.git', 'surgery_idx_r994')
msgfile = os.path.join(BM, '.git', 'surgery_msg_r994.txt')
env = dict(os.environ, GIT_INDEX_FILE=tmpidx)

def genv(*a, timeout=240):
    r = subprocess.run(['git', '-C', BM] + list(a), capture_output=True, env=env, timeout=timeout)
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()

rc, _ = genv('read-tree', tip)
print('READ_TREE rc=%d' % rc)

EXPLICIT = [
    'state.json', 'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md',
    'results/_r994bmb_s6_log.txt',
    'fleet/inbox/MSG-20261017-2203-bm-b-drama-taildrop-pickup.md',
    '_r994bmb_s6chain.ps1', '_r994bmb_closeout.py',
]
rcs, status_out = git('status', '--porcelain')
faces = list(EXPLICIT)
for line in status_out.splitlines():
    if not line.strip():
        continue
    path = line[3:].strip().strip('"')
    if path.startswith('results/_quarantine'):
        continue
    if path in faces:
        continue
    if (path.startswith('results/') or path.startswith('docs/live_usage/') or path.startswith('docs/daily_report/')
            or path == 'fleet/machine-health.json'):
        fp = os.path.join(BM, path.replace('/', os.sep))
        try:
            if os.path.getsize(fp) > 2 * 1024 * 1024:
                print('SKIP-BIG %s' % path)
                continue
        except OSError:
            continue
        faces.append(path)

added = []
for rel in faces:
    fp = os.path.join(BM, rel.replace('/', os.sep))
    if not os.path.isfile(fp):
        print('MISSING %s' % rel)
        continue
    r = subprocess.run(['git', '-C', BM, 'hash-object', '-w', '--no-filters', fp],
                       capture_output=True, timeout=60)
    sha = r.stdout.decode('utf-8', 'replace').strip()
    if len(sha) != 40:
        print('HASH_FAIL %s' % rel)
        continue
    rcu, _ = genv('update-index', '--add', '--cacheinfo', '100644', sha, rel)
    if rcu == 0:
        added.append((rel, sha))
    else:
        print('UPDATE_INDEX_FAIL %s rc=%d' % (rel, rcu))
print('FACES=%d' % len(added))

rc, tree = genv('write-tree')
print('TREE=%s rc=%d' % (tree[:12], rc))
msg = ('round 994: O-20261017-1751 P0 leg-1 dispatched (IndexTTS-2.5 detached deploy in flight: '
       'clone+uv+sync OK, 5.11G weights DL) + drama pilot taildrop re-queued to bm-a (MSG-2203 pickup request) '
       '+ S6 41rc0 + S7 registers/attrition green + D-19 zero-new-delta (e0dcbd80 consumed r993)')
with open(msgfile, 'w', encoding='utf-8') as fh:
    fh.write(msg)

def mkcommit(parent):
    r = subprocess.run(['git', '-C', BM, 'commit-tree', tree, '-p', parent, '-F', msgfile],
                       capture_output=True, env=env, timeout=60)
    return r.stdout.decode('utf-8', 'replace').strip()

newc = mkcommit(tip)
print('COMMIT=%s' % newc)
r = subprocess.run(['git', '-C', BM, 'push', 'origin', newc + ':refs/heads/main'],
                   capture_output=True, timeout=180)
out = (r.stdout + r.stderr).decode('utf-8', 'replace')
print('PUSH rc=%d %s' % (r.returncode, out[:200].replace('\n', ' | ')))
if r.returncode != 0:
    print('race retry on fresh tip...')
    git('fetch', 'origin')
    rc, tip2 = git('rev-parse', 'origin/main')
    newc = mkcommit(tip2)
    r = subprocess.run(['git', '-C', BM, 'push', 'origin', newc + ':refs/heads/main'],
                       capture_output=True, timeout=180)
    print('PUSH_RETRY rc=%d commit=%s' % (r.returncode, newc))
print('CLOSEOUT_DONE')
