# -*- coding: utf-8 -*-
# r993 bm-b closeout (renumbered from r992 per collision-yield law: the 17:52
# timeout-killed orphan round already delivered anchors as "r992" 1bd21af).
# One shot: state.json + heartbeat (orders_ack fixed to LIST per scanner
# contract) + HQ-FEEDBACK line + round report line, then BM-repo own-face
# tree-surgery push on fresh origin tip (promisor-safe, worktree-untouched).
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

# ---------- 1. heartbeat (orders_ack back to LIST per orders_ack_scan.py contract) ----------
ack_list = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BM, 'fleet', 'orders', 'O-*.md')))
print('ORDERS_ACK_LIST=%d' % len(ack_list))

did = ("r993: 当前活=r993 收口（无头轮 21:12 tick 本体：POOL-0018 首批回执核验+S6 链 41 步 rc0+D-19 orders 水位增量消费完毕）；"
       "最近实物=cph4/fleet/mv-album-001-jay/anchors/*-words.json 10/10 上链核验（commit 1bd21af·whisperX 词级锚点+端到端校准 PASS exact=34-51/曲·由 18:17 被击杀孤儿轮交付、本轮外科复核字节恒等 10/10）"
       "+HQ-FEEDBACK F-20261017-01（cloud-cap 超预算无头面饿死车道病灶定谳）；"
       "下个里程碑=漫剧 IndexTTS-2 部署+《一路长虹》前三集对白配音试产（O-20261017-1751 @bm-b 派单·回执窗 24h·r994 P0 执行·窗 ≤10-18 17:5x）。孤儿面=9/0；watermark=绿（red=false·py 低但池空+板空=周末合法 idle 白名单·本轮有实产 --worked 清零）")
heart = {
    "machine_id": "bm-b",
    "last_seen": NOW,
    "task": "r993: closeout",
    "did": did,
    "cpu_cores": 16,
    "free_ram_gb": 12.1,
    "gpu_free_vram_mb": 3450,
    "cpu_load_pct": 14,
    "verdict": ("GREEN: POOL-0018 first-batch receipt verified on origin (1bd21af, 10/10 byte-identical + calibration PASS by delivering round); "
                "S6 chain 41/41 rc0 (smoke green, orphan 9/0, dualrun streak 44, 4 shared faces stale-takeover per O-2100 s2.4 as bm-a hb stale 216min); "
                "D-19 orders delta consumed (e0dcbd80: new @bm-b dispatch IndexTTS-2 voiceover -> r994 P0, 24h window); "
                "cloud-cap lane starvation root-caused + F-20261017-01 filed; orders_ack heartbeat format fixed back to scanner contract (list); "
                "honest defers: BigHouse T-3 / MSG-1249 pickup verify / O-2110 CDN leg -> r994; r992 number yielded to orphan delivering round"),
    "idle_rounds": 0,
    "agenda_starved": False,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "ts": NOW,
    "orders_ack": ack_list,
    "note": ("r993: renumbered from r992 per collision-yield law (17:52-18:17 timeout-killed orphan round delivered anchors as r992, no closeout); "
             "idle --worked declared post-anchors-verify + S6 (idle_rounds 19->0); "
             "orders_ack restored to LIST format (r991 prose string broke orders_ack_scan - 'orders_ack is not a list' since 17:25)"),
    "latest_artifact": "POOL-0018 words anchors 10/10 verified on group origin (1bd21af) + results/_r992bmb_s6_log.txt (41 steps rc0) + HQ-FEEDBACK F-20261017-01",
    "codely_live_count": 2,
    "round_no": 993,
    "round": 993,
    "current_task": "r994: IndexTTS-2 deploy + EP001-003 voiceover pilot (O-20261017-1751) + O-2110 CDN leg verify + BigHouse T-3",
    "next": ("r994: 1) IndexTTS-2 deployment per R-20261016-drama-sfx-tts-deploy-01 runbook + 3-episode voiceover pilot (O-20261017-1751 dispatch, 24h window) "
             "2) O-2110 bm-b CDN leg verify (needs TJ-MCP window) 3) BigHouse T-3 安家流程 4) MSG-1249 bm-a pickup watch "
             "5) orders_ack_scan green verify (list format fixed r993) 6) astock detached refresh progress read"),
}
with open(os.path.join(BM, 'fleet', 'machines', 'bm-b.json'), 'w', encoding='utf-8') as fh:
    json.dump(heart, fh, ensure_ascii=False, indent=1)

# ---------- 2. state.json surgical update ----------
sp = os.path.join(BM, 'state.json')
with open(sp, encoding='utf-8') as fh:
    st = json.load(fh)
st['round'] = 993
st['round_no'] = 993
st['round_no_label'] = 'r993'
st['clock_read'] = NOW
st['ts'] = NOW
st['updated'] = NOW
st['updated_at'] = NOW
st['last_seen'] = NOW
st['last_round_at'] = NOW
st['last_round_ts'] = NOW
st['current_task'] = heart['current_task']
st['did'] = ("r993: (a) headless round = 21:12 tick spawn (pid 27800); cloud-cap starvation incident diagnosed: 18:22-21:02 16+ ticks CLOUD_CAP_DEFER live=2 "
             "(over-budget headless faces from 14:17/15:37/18:17 timeout kills surviving the one-level kill, and/or other-lane hung -p faces) starved the "
             "bigmoney lane ~3h; faces self-resolved by 21:12 (live=1, spawn GO); root-cause + fix proposal filed as HQ-FEEDBACK F-20261017-01. "
             "(b) POOL-0018 first-batch receipt: words anchors 10/10 verified byte-identical on origin (commit 1bd21af by the 17:52-18:17 timeout-killed "
             "orphan round self-labeled r992, incl. end-to-end lyric_calibration PASS exact=34-51/song; my temp-index surgery confirmed IDENTICAL_SKIP=10, "
             "no push needed, no foreign face touched). Structure face POOL-0019 honestly fused-out (madmom 3 attempts, marker present). In-production songs "
             "(anjing/jiandanan/kaibuliaokou/qingtian) await audio Taildrop per card note. (c) D-19: decisions zero-delta (1d4741e4 holds); orders DELTA "
             "consumed (e0dcbd80): new @bm-b dispatch = IndexTTS-2 deploy + 3-episode voiceover pilot (O-20261017-1751, 24h window) -> r994 P0. "
             "(d) S6 chain 41/41 rc0 incl smoke green, orphan probe 9 py faces / 0 orphans, pool_dualrun streak 44, 4 shared faces stale-takeover derive "
             "(strategy_scorecard / t35_paper_export / daily_scorecard / dashboard_status) per O-2100 s2.4 (bm-a heartbeat stale 216min), astock refresh "
             "spawned detached (panel empty/first-pull mode), idle_trigger --worked (idle_rounds 19->0). (e) heartbeat orders_ack fixed back to LIST format "
             "(scanner had errored since r991 prose string). (f) round number yielded: r992 taken by orphan delivering round; this round = r993. "
             "(g) MSG-1249 bm-a pickup still unverified in their state face (their hb stale). (h) S0 pull skipped (promisor evening risk + 25min headless "
             "budget); own faces landed via temp-index surgery on fresh origin tip instead.")
st['last_action'] = "r993: POOL-0018 receipt verify (1bd21af 10/10) + D-19 orders delta consumed + S6 41rc0 + cloud-cap starvation finding filed"
st['last_action_at'] = NOW
st['next'] = heart['next']
st['next_milestone'] = "IndexTTS-2 deploy + EP001-003 voiceover samples on chain before 10-18 17:5x (O-20261017-1751 window)"
st['verdict'] = heart['verdict']
st['current'] = "r993: receipt-verify + D-19 consumption + closeout"
st['latest_artifact'] = heart['latest_artifact']
st['last_artifact'] = heart['latest_artifact']
st['now_active'] = "r993 closed; next tick resumes normal cadence (zombie faces self-resolved)"
st['orphan_face'] = 9
st['orphan_faces'] = 9
st['orphan_face_note'] = "r993 round-zero probe (21:24): 9 py faces, 0 orphans"
st['sat_engine'] = {"status": "alive (r993 S6 status rc=0, last_verdict idle)", "checked_at": NOW}
st['last_orders_sha_probe'] = "e0dcbd8070f16c503cf99d710269580769293f60591c2e150bf9de73f2ac0cea"
st['last_orders_probe_at'] = NOW
st['last_orders_at'] = NOW
st['orders_delta_pending'] = False
st['last_decisions_probe_at'] = NOW
st['last_decisions_at'] = NOW
st['decisions_delta_pending'] = False
st['last_decisions_sha_probe'] = "1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1"
st['r992_collision_note'] = "r992 number taken by the 17:52-18:17 timeout-killed orphan round (delivered anchors 1bd21af, zero closeout); this session renumbered to r993 per collision-yield law"
st.setdefault('sync', {})['r993_main_push'] = {
    "status": "PENDING (this commit)", "pushed_sha": "pending", "consumed_at": "pending r994",
    "behind_origin_main": 0,
    "note": "r993 payload = own faces (state/heartbeat/round report + HQ-FEEDBACK + S6 log + d19 delta face + closeout work files + S6 regen faces); surgery on fresh origin tip; docs faces excluded (anti-regression, r982 policy)",
}
with open(sp, 'w', encoding='utf-8') as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# ---------- 3. HQ-FEEDBACK line ----------
hq = os.path.join(BM, 'HQ-FEEDBACK.md')
fb = ("- F-20261017-01 [bm-b r993 2026-10-17 21:3x·无头轮当窗实弹] **spawn-gate cloud-cap 探针把「超预算存活的无头 -p 面」计入并发帽=车道级饿死**："
      "现象=18:22-21:02 连续 16+ 拍 CLOUD_CAP_DEFER live=2（Bigmoney 车道断供约 3h·期间三轮 25min 超时击杀 [14:17/15:37/18:17] 的幸存面与他车道挂死面持续计入帽位；"
      "iteration_loop.ps1 超时击杀只杀直接子进程一层，深树幸存体不受 Job Object 约束），21:12 一面自然消亡后才恢复（live=1·spawn GO·即本行回执轮本体）。"
      "证据=logs/probe-heartbeat.txt defer 连击 16+ 行+21:12 run log（cloud-cap preflight OK live=1）+击杀行×3。"
      "建议方向：①iteration_loop.ps1 超时击杀升格树级连坐（taskkill /T 或 Job Object）；②cloud-cap 探针（Tools/iteration_loop.ps1 spawn-gate 段）加年龄过滤——超该车道轮预算×2 的 -p 面不入帽计数、改记僵尸告警行（结构上把「挂死面」与「在帽活面」分开，帽位永远留给真活轮）；"
      "③各车道 wrapper 击杀后自检子体清零（Stop 后 CIM 复扫 ParentProcessId 链）。状态 open\n")
with open(hq, 'a', encoding='utf-8') as fh:
    fh.write(fb)

# ---------- 4. round report line ----------
rr = os.path.join(BM, 'logs', 'iteration-loop', 'round_reports.md')
row = ("{t} | r993 | watermark=绿（red=false·周末池空+板空合法 idle 白名单·本轮实产 --worked 已清零）"
       "｜无头轮 21:12 tick 本体（25min 预算内收口）：POOL-0018 首批回执核验=锚点 10/10 origin 字节恒等（1bd21af·由 18:17 击杀孤儿轮 r992 面交付+校准 PASS exact=34-51/曲·撞号让路本轮取 993）；"
       "S6 链 41 步 rc0（smoke 绿/孤儿面 9/0/dualrun 连绿 44/四共享面 stale-takeover 合法接管·bm-a hb 陈旧 216min/astock 首拉后台刷新 spawn）；"
       "D-19 双水位=decisions 零增量+orders 增量已消费（e0dcbd80：新 @bm-b 派单=漫剧 IndexTTS-2+前三集配音试产→r994 P0）；"
       "cloud-cap 饿死病灶定谳+HQ-FEEDBACK F-20261017-01（超预算无头面计入帽位 3h 断供）；"
       "心跳 orders_ack 修回 list 格式（r991 散文串致扫描器 17:25 起报错）；MSG-1249 取件仍未证（bm-a 心跳陈旧）；"
       "本地未达 origin commit 数=0（外科净路·本地 main 落后属设计态·S0 自拉平）"
       "｜证据=probe-heartbeat 230 行/1bd21af git log/_r992bmb_s6_log.txt 41rc0/D19 sha 双探/_r992bmb_d19_orders_delta.txt"
       "｜r994: IndexTTS-2 部署+《一路长虹》前三集配音试产（O-20261017-1751·24h 窗）+O-2110 CDN 腿核验（候 TJ-MCP 窗）+BigHouse T-3+orders_ack_scan 绿面复验\n").format(t=NOWC)
with open(rr, 'a', encoding='utf-8') as fh:
    fh.write(row)

# ---------- 5. BM-repo own-face surgery push on fresh origin tip ----------
rcf, _ = git('fetch', 'origin')
rc, tip = git('rev-parse', 'origin/main')
print('FETCH rc=%d ORIGIN=%s' % (rcf, tip[:12]))
tmpidx = os.path.join(BM, '.git', 'surgery_idx_r993')
msgfile = os.path.join(BM, '.git', 'surgery_msg_r993.txt')
env = dict(os.environ, GIT_INDEX_FILE=tmpidx)

def genv(*a, timeout=240):
    r = subprocess.run(['git', '-C', BM] + list(a), capture_output=True, env=env, timeout=timeout)
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()

rc, _ = genv('read-tree', tip)
print('READ_TREE rc=%d' % rc)

EXPLICIT = [
    'state.json', 'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md', 'HQ-FEEDBACK.md',
    'results/_r992bmb_s6_log.txt', 'results/_r992bmb_d19_orders_delta.txt',
    '_r992bmb_anchor_surgery.py', '_r992bmb_s6chain.ps1', '_r992bmb_d19_orders.py',
    '_r992bmb_closeout.py',
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
msg = ('round 993: POOL-0018 first-batch receipt verified (1bd21af 10/10 byte-identical) '
       '+ D-19 orders delta consumed (IndexTTS-2 dispatch -> r994 P0) + S6 chain 41rc0 '
       '+ cloud-cap lane starvation root cause filed (HQ-FEEDBACK F-20261017-01) '
       '+ heartbeat orders_ack fixed to list (scanner contract) '
       '+ r992 number yielded to orphan delivering round (collision-yield law)')
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
    if r.returncode != 0:
        print('PUSH_FAILED - faces stay on disk (staged-carry next round); report honestly')

# delivery verification on origin
git('fetch', 'origin')
rc, otip = git('rev-parse', 'origin/main')
ok = 0
probe_faces = [f for f, _ in added][:6]
for rel, sha in added:
    rcv, osha = git('rev-parse', otip + ':' + rel)
    if osha == sha:
        ok += 1
    elif rel in probe_faces:
        print('MISMATCH %s origin=%s mine=%s' % (rel, osha[:12], sha[:12]))
print('CONTENT_CHECK %d/%d on origin tip %s' % (ok, len(added), otip[:12]))
print('BEHIND_AFTER=%s' % git('rev-list', '--count', 'main..origin/main')[1])
print('CLOSEOUT_DONE')
