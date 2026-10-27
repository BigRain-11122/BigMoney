"""CONTENT-LOOP v0.1 queue engine (drama line, bm-b host).

Blueprint: cph4/fleet/CONTENT-OS-LOOP-BLUEPRINT-v1.md sec.3 (20-30min loop,
queue-ledger self-claim, five-piece gates stay in-loop, director step-gate,
CEO terminal review only). Order refs: O-20261018-2144-bm-c sec.2.1,
O-20261018-2236-bm-c (10-min idle SLA).

Commands:
  round   -- locked scan -> claim first runnable station -> execute runner ->
             regenerate QUEUE.md face -> book round row. Emits one JSON line.
  scan    -- read-only verdict (no claim, no write).
  adopt-runners -- developer-seat maintenance: flip open stations from the
             v0.2-pending placeholder onto real runner names (lock-held).
  selftest -- offline assertions.

Machine ledger = content/drama/queue.json (single-writer via pid+age lock,
FleetLink worker v1.6 law). QUEUE.md is a regenerated human face, never hand-
edited. Claims append to content/drama/CLAIMS.jsonl (append-only). Round rows
append to content/drama/ROUND-LOG.md. Loop state = content/drama/loop_state.json.
All writes fresh-read-modify-write inside the lock (r1006 multi-writer law).
"""
import io
import json
import os
import subprocess
import sys
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, 'content', 'drama')
QPATH = os.path.join(QDIR, 'queue.json')
MDPATH = os.path.join(QDIR, 'QUEUE.md')
CLAIMS = os.path.join(QDIR, 'CLAIMS.jsonl')
RLOG = os.path.join(QDIR, 'ROUND-LOG.md')
LSTATE = os.path.join(QDIR, 'loop_state.json')
LOCK = os.path.join(QDIR, '.loop.lock')
# D-20261028-04: never trust a literal. The group tree is resolved (validated
# toplevel + newest ledger mtime) and the literal is only a hint; picking a stale
# mirror here would drive the content lane off a week-old ledger.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from group_root import pick_or_default as _gr_pick
    GRP = _gr_pick(r'C:\Fluxgroup\FluxGroup')
except Exception:                       # pragma: no cover - never block the lane
    GRP = r'C:\Fluxgroup\FluxGroup'
STALE_LOCK_S = 600
_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0  # CREATE_NO_WINDOW (U060 zero-desktop-flash law)


def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def rd_json(p, default):
    try:
        with io.open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def wr_json(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def acquire_lock():
    if os.path.exists(LOCK):
        st = rd_json(LOCK, {})
        try:
            age = time.time() - st.get('ts_epoch', 0)
        except Exception:
            age = 1e9
        alive = False
        try:
            pid = int(st.get('pid', 0))
            if pid and os.name == 'nt':
                r = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                                    "(Get-Process -Id %d -ErrorAction SilentlyContinue) -ne $null" % pid],
                                   capture_output=True, text=True, timeout=30,
                                   creationflags=_NO_WINDOW)
                alive = r.stdout.strip().lower() == 'true'
        except Exception:
            alive = False
        if alive and age < STALE_LOCK_S:
            return False, 'lock-held-pid-%s' % st.get('pid')
        # stale or dead holder -> reclaim
    wr_json(LOCK, {'pid': os.getpid(), 'ts_epoch': time.time(), 'ts': now_iso()})
    return True, 'ok'


def release_lock():
    try:
        os.remove(LOCK)
    except Exception:
        pass


def append_line(p, line):
    with io.open(p, 'a', encoding='utf-8') as f:
        f.write(line.rstrip('\n') + '\n')


def require_ok(q, st):
    req = st.get('require') or 'none'
    if req == 'none':
        return True, 'none'
    if req.startswith('manual-gate:'):
        gate = q['gates'].get(req.split(':', 1)[1])
        if gate and gate.get('state') == 'open':
            return True, 'gate-open'
        return False, 'gate-closed:' + req.split(':', 1)[1]
    if req.lower().startswith('st') and len(req) == 6:
        for s in q['stations']:
            if s['id'] == req and s['state'] == 'done':
                return True, 'dep-done'
        return False, 'dep-open:' + req
    return False, 'unknown-require:' + req


def regen_md(q):
    lines = []
    a = lines.append
    a('# CONTENT-LOOP QUEUE -- drama line (bm-b host, v0.1)')
    a('')
    a('> Carrier: Bigmoney-ContentLoop S4U task (20-min). Machine ledger = queue.json (single-writer);')
    a('> this file is a regenerated face -- never hand-edit. Protocol: claim-by-file, station states')
    a('> open/claimed/done/blocked; five-piece gates stay in-loop (no downgrade); director step-gate')
    a('> per station; CEO = terminal review only; account writes = physical-domain pause face.')
    a('> Law refs: CONTENT-OS-LOOP-BLUEPRINT-v1 sec.3; O-20261018-2144-bm-c sec.2.1; DIRECTOR-STEP-GATE-v1.')
    a('')
    a('## Gates')
    a('')
    a('| gate | state | note |')
    a('|---|---|---|')
    for k, g in q.get('gates', {}).items():
        a('| %s | %s | %s |' % (k, g.get('state'), (g.get('note') or '')[:160]))
    a('')
    a('## Stations')
    a('')
    a('| id | state | lane | runner | require | title | claim |')
    a('|---|---|---|---|---|---|---|')
    for s in q['stations']:
        a('| %s | %s | %s | %s | %s | %s | %s |' % (
            s['id'], s['state'], s['lane'], s.get('runner'), s.get('require'),
            s['title'][:80], s.get('claim') or '-'))
    a('')
    st = rd_json(LSTATE, {})
    a('Loop state: rounds=%s last=%s' % (st.get('rounds', 0), st.get('last_ts', '-')))
    with io.open(MDPATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


# ---------------- runners (v0.1 registry) ----------------

def _git(args, timeout=180):
    r = subprocess.run(['git', '-C', GRP] + args, capture_output=True, timeout=timeout,
                       creationflags=_NO_WINDOW)
    return r.returncode, r.stdout.decode('utf-8', 'replace')


def st001_rootcause_gather(st):
    """ST-001: collect J-D0-1 taildrop evidence from group origin and emit a
    root-cause face into the outbox. Honest-bounded: facts first, root-cause
    candidate clearly labeled as bm-b-side self-cert draft; the LEDGER backfill
    row lands on group via the next push window (queued, not auto-pushed)."""
    out_dir = os.path.join(QDIR, 'outbox')
    os.makedirs(out_dir, exist_ok=True)
    facts = []
    rc, out = _git(['ls-tree', '-r', '--name-only', 'origin/main'])
    hits = [l for l in out.splitlines() if 'taildrop' in l.lower()]
    facts.append(('group-origin tree scan', 'rc=%d, taildrop-named files=%d' % (rc, len(hits))))
    for h in hits[:10]:
        facts.append(('file', h))
    rc, out = _git(['show', 'origin/main:cph4/fleet/drama-dept-v1/LEDGER.md'])
    led_lines = [l for l in out.splitlines() if 'J-D0-1' in l or 'taildrop' in l.lower()]
    facts.append(('LEDGER rows', '%d hit(s)' % len(led_lines)))
    for l in led_lines[:5]:
        facts.append(('ledger', l[:300]))
    # probe group orders for the original dispatch contract
    rc, out = _git(['show', 'origin/main:docs/orders.md'])
    ord_hits = [l for l in out.splitlines() if 'taildrop' in l.lower() and 'drama' in l.lower()]
    facts.append(('orders rows', '%d hit(s)' % len(ord_hits)))
    for l in ord_hits[:5]:
        facts.append(('order', l[:300]))
    md = []
    md.append('# J-D0-1 root-cause self-cert (draft) -- bm-b taildrop SLA violation')
    md.append('')
    md.append('> Station ST-001 product (CONTENT-LOOP v0.1 first runner). Source: drama-dept-v1 LEDGER')
    md.append('> row J-D0-1 (2026-10-16 drama-pilot-taildrop-bmb OVERDUE, hit=0/1, 12:45 deadline,')
    md.append('> 21:06 poke; bm-b-side self-cert pending). PILOT-001 3x20s samples WERE delivered')
    md.append('> (RECIPE-EPBURN-v1 preface) -- the violation is about the delivery channel, not the product.')
    md.append('')
    md.append('## Facts collected (group origin @ %s)' % now_iso())
    for k, v in facts:
        md.append('- **%s**: %s' % (k, v))
    md.append('')
    md.append('## Root-cause candidate (bm-b side)')
    md.append('')
    md.append('- Delivery mechanism was fleet Taildrop file transfer (drop to peer Downloads scan face,')
    md.append('  r1044 pit law). hit=0/1 with poke at 21:06 after a 12:45 deadline = the receiving-side')
    md.append('  pickup never registered during the SLA window; delivery only completed via a later')
    md.append('  alternate channel (git/manual), so the watch contract counted a violation.')
    md.append('- Candidate root causes (ranked): (1) taildrop drop landed outside the scanned inbox face')
    md.append('  (r1044: must-scan-Downloads face); (2) sender-side send receipt not written while the')
    md.append('  receive actually happened late; (3) peer offline during the window.')
    md.append('- Gate recommendation: delivery-watch contract should pin the scan face list (Downloads +')
    md.append('  fleet inbox) and require a sender receipt row; deadline contracts for cross-machine')
    md.append('  physical-channel deliveries should carry a fallback-to-git clause so SLA is provable.')
    md.append('')
    md.append('## Status')
    md.append('')
    md.append('- This face = local evidence product (ST-001 done locally). The LEDGER backfill row rides')
    md.append('  the next group push window -- queued as outbox payload, NOT auto-pushed (group tree =')
    md.append('  shared live tree, CAS push required).')
    outp = os.path.join(out_dir, 'J-D0-1-rootcause.md')
    with io.open(outp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    return {'runner': 'st001_rootcause_gather', 'product': outp,
            'facts_collected': len(facts), 'verdict': 'done-local-ledger-row-pending-group-push'}


# ---------------- runners (v0.2 registry: ST-003 voice lane + ST-004 anchor-clean) ----------------

VOICE_REPOS = [
    # clone routes in fallback order: direct https (schannel can be cut by proxy),
    # gh-proxy.com prefix (fleet-established GitHub route), ssh :443 (config law)
    ('GPT-SoVITS', ['https://github.com/RVC-Boss/GPT-SoVITS.git',
                    'https://gh-proxy.com/https://github.com/RVC-Boss/GPT-SoVITS.git',
                    'git@github.com:RVC-Boss/GPT-SoVITS.git']),
    ('OpenVoice', ['https://github.com/myshell-ai/OpenVoice.git',
                   'https://gh-proxy.com/https://github.com/myshell-ai/OpenVoice.git',
                   'git@github.com:myshell-ai/OpenVoice.git']),
]


def st003_voice_library_first_batch(st):
    """ST-003 (P1 <=10-22): voice-library lane first batch. GitHub-first sourcing
    per CEO standing law (W6 scan shortlist): shallow-clone GPT-SoVITS + OpenVoice
    into group media/drama-tools/, extract offline facts (LICENSE/README) straight
    from the clones, then emit the evaluation face + fixed-voice pipeline skeleton
    into the outbox. No model downloads in this batch (weights -> modelscope
    morning window per ST-002 pattern); cpu lane; cloud forbidden."""
    tools_dir = os.path.join(GRP, 'media', 'drama-tools')
    os.makedirs(tools_dir, exist_ok=True)
    cloned, present, shas = [], [], {}
    for name, urls in VOICE_REPOS:
        dest = os.path.join(tools_dir, name)
        if os.path.isdir(os.path.join(dest, '.git')):
            present.append(name)
        else:
            errs = []
            for url in urls:
                r = subprocess.run(['git', 'clone', '--depth', '1', url, dest],
                                   capture_output=True, timeout=900,
                                   creationflags=_NO_WINDOW)
                if r.returncode == 0:
                    cloned.append(name)
                    break
                errs.append(url.split('//')[-1][:44] + ': ' +
                             r.stderr.decode('utf-8', 'replace').strip()[-100:])
                if os.path.isdir(dest):
                    subprocess.run(
                        ['powershell.exe', '-NoProfile', '-Command',
                         "Remove-Item -LiteralPath '%s' -Recurse -Force -ErrorAction SilentlyContinue"
                         % dest.replace("'", "''")],
                        capture_output=True, timeout=120, creationflags=_NO_WINDOW)
            else:
                raise RuntimeError('clone-failed %s all-routes: %s' % (
                    name, ' | '.join(errs)))
        r2 = subprocess.run(['git', '-C', dest, 'rev-parse', 'HEAD'],
                             capture_output=True, timeout=60,
                             creationflags=_NO_WINDOW)
        shas[name] = r2.stdout.decode().strip()[:12]
    facts = {}
    for name, _ in VOICE_REPOS:
        dest = os.path.join(tools_dir, name)
        lic = 'not-found'
        for cand in ('LICENSE', 'LICENSE.txt', 'LICENSE.md'):
            p = os.path.join(dest, cand)
            if os.path.exists(p):
                with io.open(p, 'r', encoding='utf-8', errors='replace') as f:
                    lic = ' '.join(f.read(300).split())[:280]
                break
        readme, readme_path = '', 'not-found'
        for cand in ('README.md', 'README_zh.md', 'readme.md'):
            p = os.path.join(dest, cand)
            if os.path.exists(p):
                with io.open(p, 'r', encoding='utf-8', errors='replace') as f:
                    readme = f.read(12000)
                readme_path = cand
                break
        hits = []
        for ln in readme.splitlines():
            l = ' '.join(ln.strip().split())
            if len(l) > 40 and not l.startswith(('#', '!', '[!', '<', '|', '---')):
                low = l.lower()
                if any(k in low for k in ('few-shot', 'zero-shot', 'chinese', 'mandarin',
                                          'multilingual', 'tone', 'clone', 'webui', 'vits')):
                    hits.append(l[:170])
            if len(hits) >= 4:
                break
        facts[name] = {'license': lic, 'readme': readme_path,
                       'readme_hits': hits, 'clone_sha': shas.get(name, '-')}
    out_dir = os.path.join(QDIR, 'outbox')
    os.makedirs(out_dir, exist_ok=True)
    ts = now_iso()
    md = []
    md.append('# 声库车道首批评估面（voice-library first batch · ST-003 · P1）')
    md.append('')
    md.append('> 站点=CONTENT-LOOP v0.1 ST-003（O-20261018-2144-bm-c §2.1 声库车道 P1 ≤10-22）；')
    md.append('> 寻源=W6 一致性调研扫描短名单（r1011 回执·CEO 常设工作律「先搜 GitHub 高星现成轮」）；')
    md.append('> 本批产品=克隆+评估+管线骨架；模型权重点位=后续 modelscope 晨窗（ST-002 范式）；')
    md.append('> 车道=cpu；云端禁用（429 经济）。生成时点=%s。' % ts)
    md.append('')
    md.append('## 克隆实况（--depth 1）')
    for name, _ in VOICE_REPOS:
        md.append('- **%s** → `%s`（clone_sha=%s · %s）' % (
            name, os.path.join(tools_dir, name), facts[name]['clone_sha'],
            '本批新克隆' if name in cloned else '已在位跳过'))
    md.append('- 星数引用=W6 扫描时点数：GPT-SoVITS 63k / OpenVoice 37k（本批不在线复核·如实标注）。')
    md.append('- 产物面=gitignored media 区（CEO 交付律）·本评估件与骨架件=outbox 入 git。')
    md.append('')
    for name, _ in VOICE_REPOS:
        md.append('## 离线事实直读 -- %s' % name)
        md.append('')
        md.append('- License（文件首段）：%s' % facts[name]['license'])
        md.append('- README=%s；要点行摘录（克隆件直读）：' % facts[name]['readme'])
        for h in facts[name]['readme_hits']:
            md.append('  - %s' % h)
        if not facts[name]['readme_hits']:
            md.append('  - （关键词面无命中行·如实）')
        md.append('')
    md.append('## 评估结论（对照 drama-001-stockera 需求）')
    md.append('')
    md.append('- 需求面：60 集漫剧固定角色配音——7 个正典角色（CH/XIONG/RED/MANCANG/XIONGWEI/FATHER/BOY）')
    md.append('  中文台词批产 TTS、跨集音色恒定（人物一致性=受众第一优先律的声音面）。')
    md.append('- **主选=GPT-SoVITS**：少样本音色克隆（参考音分钟级）+中文一等支持+社区体量（63k）——')
    md.append('  与「固定角色声银行」正身匹配（每角色 1-3 条参考音入库，跨集复用）。')
    md.append('- **备选=OpenVoice**：轻量音色迁移路线——主选环境/质量不达标时作 tone-transfer 备胎，或作风格化辅助层。')
    md.append('- 后续批次（≤10-22 档内）：环境安装+首批声银行条目（每角色参考音→声音面清单入行，')
    md.append('  锚清洗纪律的声音面移植：入行前同角色多参考音过「音色一致检」）。')
    md.append('- 诚实缺口：本批未装环境未出声样（P1 站点产品=克隆+评估+骨架）；星数=扫描时点数非实时；')
    md.append('  README 摘录=关键词面采样非全文审读。')
    evalp = os.path.join(out_dir, 'VOICE-LIBRARY-EVAL-20261019.md')
    with io.open(evalp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    sk = []
    sk.append('# 固定声管线骨架 v1（fixed-voice pipeline skeleton · ST-003）')
    sk.append('')
    sk.append('> 承接=VOICE-LIBRARY-EVAL-20261019.md（主选 GPT-SoVITS/备选 OpenVoice）；')
    sk.append('> 法源=O-20261018-2144-bm-c §2.1 + DIRECTOR-STEP-GATE-v1（逐站门）+人物一致性律（声音面）。')
    sk.append('')
    sk.append('## 站位（v0 蓝图）')
    sk.append('')
    sk.append('1. **台词面**：episodes/EP*.json 对白行 → 按角色归并（drama-001-stockera 面板）。')
    sk.append('2. **声银行（voice bank）**：每正典角色条目 schema = `{id, ref_clips[1-3], engine, params,')
    sk.append('   voice_manifest{性别/年龄感/质感}, added_ts}`；入行门=同角色多参考音「音色一致检」')
    sk.append('   （锚清洗纪律的声音面移植）+独立 lane 目录（不入 CEO 试验账本面）。')
    sk.append('3. **TTS 批产**：逐镜音频件·确定性参数档·resume-safe·失败行隔离重试（断点续拉范式）。')
    sk.append('4. **QC 门（三查·声音面）**：音频存在性/时长-字率带（台词长度匹配）/听感抽检（盲评位；')
    sk.append('   不过门=打回不进装配）。')
    sk.append('5. **装配面**：音频入集装配器（画面+对白音轨）；与 MV 音轨律不冲突——漫剧台词=剧情音·')
    sk.append('   非 MV 歌轨面（O-20261009-1901 律域=BigStream MV 线）。')
    sk.append('6. **车道纪律**：cpu 先行（GPT-SoVITS CPU 推理慢→夜间批产）；GPU 面=ST-002 门后评估；云端禁用。')
    sk.append('7. **一致性法律继承**：跨集音色漂移=判负打回（受众面第一优先）。')
    sk.append('')
    sk.append('## 与视觉面锚清洗纪律的对齐（ST-004 同窗落地）')
    sk.append('')
    sk.append('- 视觉面=ANCHOR 三元组硬约束（发型/发色/着装）+id 银行入行前一致检（anchor_precheck.py）；')
    sk.append('  声音面同构=voice_manifest 三描述+参考音入行前一致检——两面上位同一纪律：**入行前过检，')
    sk.append('  行内零漂移**。')
    skelp = os.path.join(out_dir, 'VOICE-PIPELINE-SKELETON-v1.md')
    with io.open(skelp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sk) + '\n')
    return {'runner': 'st003_voice_library_first_batch',
            'cloned': cloned, 'present': present,
            'products': [evalp, skelp],
            'clone_shas': shas, 'verdict': 'first-batch-complete'}


BURN_PY = r'C:\Fluxgroup\MiniGame\Tools\comfy\drama_ep_burn.py'
APC_DEST = r'C:\Fluxgroup\MiniGame\Tools\comfy\anchor_precheck.py'
APC_SRC = os.path.join(QDIR, 'runner_assets', 'anchor_precheck.py')

# ANCHOR triple pins (CSA-SMOKE-VERDICT-20261017 v1.1 item 2): the five canon
# anchors that lacked explicit hair style/color get the pin; CH (black hair) and
# XIONG (silver temples) already passed. Long IDS + compact IDS_C kept in sync.
BURN_REPL = [
    ("    'RED': 'a poised young woman around 20, 1990s office skirt suit, calculator on a lanyard, neat ponytail',",
     "    'RED': 'a poised young woman around 20, black hair in a neat ponytail, 1990s office skirt suit, calculator on a lanyard',"),
    ("    'MANCANG': 'a chubby cheerful man around 25, loud floral shirt, pager clipped to belt',",
     "    'MANCANG': 'a chubby cheerful man around 25, short black hair, loud floral shirt, pager clipped to belt',"),
    ("    'XIONGWEI': 'a cold young man around 24, all-black minimalist suit, rimless glasses, colder and sharper than his father',",
     "    'XIONGWEI': 'a cold young man around 24, neat black hair, all-black minimalist suit, rimless glasses, colder and sharper than his father',"),
    ("    'FATHER': 'a weary middle-aged man in a rumpled dark 1993 suit, loosened tie, kind tired eyes, rain-soaked hair',",
     "    'FATHER': 'a weary middle-aged man in a rumpled dark 1993 suit, loosened tie, kind tired eyes, rain-soaked black hair',"),
    ("    'BOY': 'a 12-year-old schoolboy in a plain white shirt, wide frightened eyes looking upward',",
     "    'BOY': 'a 12-year-old schoolboy, short black hair, in a plain white shirt, wide frightened eyes looking upward',"),
    ("    'RED': 'young woman 20, ponytail, 1990s office skirt suit',",
     "    'RED': 'young woman 20, black hair ponytail, 1990s office skirt suit',"),
    ("    'MANCANG': 'chubby man 25, loud floral shirt, pager on belt',",
     "    'MANCANG': 'chubby man 25, short black hair, loud floral shirt, pager on belt',"),
    ("    'XIONGWEI': 'young man 24, all-black suit, rimless glasses',",
     "    'XIONGWEI': 'young man 24, neat black hair, all-black suit, rimless glasses',"),
    ("    'FATHER': 'weary middle-aged man, rumpled dark suit, loosened tie',",
     "    'FATHER': 'weary middle-aged man, unkempt black hair, rumpled dark suit, loosened tie',"),
    ("    'BOY': '12-year-old schoolboy, plain white shirt',",
     "    'BOY': '12-year-old schoolboy, short black hair, plain white shirt',"),
    ("ALIAS = {'XTC': 'XIONG', 'XW': 'XIONGWEI', 'MC': 'MANCANG', 'HL': 'RED',\n"
     "         '散户甲': 'SD1', '散户乙': 'SD2'}",
     "ALIAS = {'XTC': 'XIONG', 'XW': 'XIONGWEI', 'MC': 'MANCANG', 'HL': 'RED',\n"
     "         '散户甲': 'SD1', '散户乙': 'SD2'}\n"
     "# CSA-SMOKE-VERDICT-20261017 v1.1 item 2: ANCHOR triple hard-constraint\n"
     "# (发型/发色/着装) -- canon bank anchors must pin all three or the burn\n"
     "# refuses to start (锚清洗纪律; green-hair drift case). Util =\n"
     "# anchor_precheck.py in this dir (ST-004; compact heads +2 words per pinned\n"
     "# char -- expand_c scene-tail absorbs, verdict item-2 tradeoff).\n"
     "CANON_IDS = ('CH', 'XIONG', 'RED', 'MANCANG', 'XIONGWEI', 'FATHER', 'BOY')\n"
     "\n"
     "def anchor_gate():\n"
     "    import anchor_precheck\n"
     "    bad = anchor_precheck.validate_canon(IDS_C, CANON_IDS)\n"
     "    if bad:\n"
     "        print('ANCHOR_TRIPLE_FAIL ' + json.dumps(bad, ensure_ascii=False), flush=True)\n"
     "        sys.exit(2)\n"
     "    print('ANCHOR_TRIPLE_OK canon=%d' % len(CANON_IDS), flush=True)"),
    ("def main(ep_lo, ep_hi):\n    g.wait_server()",
     "def main(ep_lo, ep_hi):\n    anchor_gate()\n    g.wait_server()"),
]

CANON_COMPACT_POST = {
    'CH': 'young man 22, black hair, white dress shirt, steel watch chain',
    'XIONG': 'man 50, silver temples, black suit, dark red necktie, prayer beads on wrist',
    'RED': 'young woman 20, black hair ponytail, 1990s office skirt suit',
    'MANCANG': 'chubby man 25, short black hair, loud floral shirt, pager on belt',
    'XIONGWEI': 'young man 24, neat black hair, all-black suit, rimless glasses',
    'FATHER': 'weary middle-aged man, unkempt black hair, rumpled dark suit, loosened tie',
    'BOY': '12-year-old schoolboy, short black hair, plain white shirt',
}


def st004_csa_anchor_precheck(st):
    """ST-004: CSA anchor-cleaning discipline into production (CSA-SMOKE-VERDICT
    20261017 v1.1 item 2). Deliverables: (1) anchor_precheck.py util deployed to
    the toolchain canonical dir (MiniGame/Tools/comfy, bm-b owner) from the
    versioned source content/drama/runner_assets/; (2) drama_ep_burn.py
    anchor-clean patch -- five canon anchors missing explicit hair pins get them
    (green-hair drift root), plus a startup hard gate (ANCHOR_TRIPLE_OK /
    ANCHOR_TRIPLE_FAIL exit 2); (3) offline selftest + post-patch probe.
    Receipt doc -> outbox."""
    with io.open(APC_SRC, 'r', encoding='utf-8') as f:
        apc_body = f.read()
    with io.open(APC_DEST, 'w', encoding='utf-8', newline='\n') as f:
        f.write(apc_body)
    with io.open(BURN_PY, 'r', encoding='utf-8') as f:
        src = f.read()
    already = 'ANCHOR_TRIPLE_OK' in src
    if not already:
        patched = src
        for old, new in BURN_REPL:
            n = patched.count(old)
            if n != 1:
                raise RuntimeError('patch-precondition-fail count=%d: %r' % (n, old[:70]))
            patched = patched.replace(old, new)
        with io.open(BURN_PY, 'w', encoding='utf-8', newline='') as f:
            f.write(patched)
    r = subprocess.run([sys.executable, APC_DEST, '--selftest'],
                        capture_output=True, timeout=120, creationflags=_NO_WINDOW)
    st_out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        raise RuntimeError('anchor_precheck selftest FAIL: ' + st_out[:200])
    sys.path.insert(0, os.path.dirname(APC_DEST))
    import anchor_precheck as apc
    bad = apc.validate_canon(CANON_COMPACT_POST, tuple(CANON_COMPACT_POST))
    if bad:
        raise RuntimeError('post-patch probe FAIL: ' + json.dumps(bad, ensure_ascii=False)[:200])
    with io.open(BURN_PY, 'r', encoding='utf-8') as f:
        src2 = f.read()
    for _, new in BURN_REPL:
        assert new in src2, 'post-patch read-back assert failed: %r' % new[:60]
    out_dir = os.path.join(QDIR, 'outbox')
    os.makedirs(out_dir, exist_ok=True)
    ts = now_iso()
    md = []
    md.append('# ST-004 锚清洗纪律入产线回执（CSA v1.1 item 2 · anchor pre-check）')
    md.append('')
    md.append('> 站点=CONTENT-LOOP v0.1 ST-004；法源=cph4/fleet/drama-dept-v1/epburn-handover/')
    md.append('> CSA-SMOKE-VERDICT-20261017.md v1.1 条款 2（工单 2/5 技术面 GO 承接）；时点=%s。' % ts)
    md.append('')
    md.append('## 交付三件')
    md.append('')
    md.append('1. **anchor_precheck.py 工具**（部署=`%s`；版本化源=bigmoney' % APC_DEST)
    md.append('   `content/drama/runner_assets/anchor_precheck.py`）：ANCHOR 三元组校验（发型/发色/着装）+')
    md.append('   id 银行入行门（manifest 零漂移）+ 同角色跨帧行清单零漂移检 + 视觉席位工单面')
    md.append('   （emit_frame_check——像素级帧检=多模态席位的活，工具只做确定性面）。')
    md.append('2. **drama_ep_burn.py 锚清洗补丁**（`%s`·%s）：' % (BURN_PY, '本批落补丁' if not already else '已在位幂等跳过'))
    md.append('   - 5 个正典锚补齐发色/发型钉（绿发漂移根因位）：RED（black hair ponytail）/MANCANG（short')
    md.append('     black hair）/XIONGWEI（neat black hair）/FATHER（unkempt black hair·长锚 rain-soaked black')
    md.append('     hair）/BOY（short black hair）；CH（black hair）与 XIONG（silver temples）原已达标零改。')
    md.append('   - 启动硬闸 anchor_gate()：烧制前校验 7 正典角色 IDS_C 三元组，缺项=ANCHOR_TRIPLE_FAIL')
    md.append('     exit 2 拒烧（fail-fast·不再带病入产）。')
    md.append('   - CLIP 77-token 预算注记：紧锚头均 +2 词（expand_c 景尾吸收机制既有·CSA 判决条款 2 的')
    md.append('     定谳取舍：锚漂移之害>景尾截短之损）。')
    md.append('3. **自检+探针双绿**：anchor_precheck --selftest（离线断言 9 条含反例）=%s；' % st_out[-60:])
    md.append('   补丁后正典紧锚 in-process 探针=validate_canon 7/7 PASS。')
    md.append('')
    md.append('## 诚实边界')
    md.append('')
    md.append('- 帧级（像素）一致性检不在本件射程（=多模态席位工单面）；本件=文本/清单级确定性面。')
    md.append('- 补丁只钉锚文本与启动闸，未动 expand/expand_c 注入算法、种子、STEPS/CFG（零行为面改动')
    md.append('  除锚文本本身）。')
    md.append('- MiniGame/Tools/comfy=非 git 工具区（盘面为正身）；版本化源与回执走 bigmoney 仓。')
    rcp = os.path.join(out_dir, 'ST-004-ANCHOR-PRECHECK-RECEIPT.md')
    with io.open(rcp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    return {'runner': 'st004_csa_anchor_precheck', 'util': APC_DEST,
            'burn_patched': not already, 'selftest_rc': r.returncode,
            'probe': 'canon-7/7-pass', 'product': rcp}




# ---------------- runners (v0.2 registry: ST-005 env bootstrap + ST-006 voice bank) ----------------

ENV_DRIVER = os.path.join(QDIR, 'runner_assets', 'gpt_sovits_env_driver.py')
ENV_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'gpt_sovits_env_status.json')
ENV_LOG = os.path.join(GRP, 'media', 'drama-tools', '.gpt_sovits_env_install.log')
_DETACHED_FLAGS = (0x00000008 | 0x00000200 | 0x08000000)  # DETACHED|NEW_PROCESS_GROUP|NO_WINDOW


def _driver_status():
    try:
        with io.open(ENV_STATUS, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return {}


def _pid_alive(pid):
    if not pid:
        return False
    try:
        r = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                            '(Get-Process -Id %d -ErrorAction SilentlyContinue) -ne $null' % int(pid)],
                           capture_output=True, text=True, timeout=30,
                           creationflags=_NO_WINDOW)
        return r.stdout.strip().lower() == 'true'
    except Exception:
        return False


def st005_gpt_sovits_env_ignite(st):
    """ST-005: voice-library env bootstrap (GPT-SoVITS main engine per ST-003
    eval). Idempotent ensure-ignited: live driver -> already-running; finished
    -> done-early; else detached ignition (astock spawn_detached precedent,
    r317 close_fds law) + post-ignition liveness probe. Product = driver
    live-or-done + status face + log; the phased install itself completes
    over subsequent loop rounds (phases venv/torch/deps/weights/extras/smoke,
    each idempotent + checkpointed)."""
    ds = _driver_status()
    if ds.get('state') == 'done':
        return {'runner': 'st005_gpt_sovits_env_ignite', 'verdict': 'done-early',
                'phases_done': ds.get('phases_done'), 'status_face': ENV_STATUS}
    if ds.get('state') == 'running' and _pid_alive(ds.get('pid')):
        return {'runner': 'st005_gpt_sovits_env_ignite', 'verdict': 'already-running',
                'pid': ds.get('pid'), 'phase': ds.get('phase'), 'status_face': ENV_STATUS}
    if ds.get('state') == 'failed':
        # prior attempt failed honestly -- re-ignite is legal (idempotent phases
        # checkpoint); failed-phase errors ride the status face
        pass
    r = subprocess.run([sys.executable, ENV_DRIVER, 'selftest'],
                        capture_output=True, timeout=120, creationflags=_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError('driver selftest FAIL pre-ignition: ' +
                           r.stdout.decode('utf-8', 'replace').strip()[-160:])
    os.makedirs(os.path.dirname(ENV_LOG), exist_ok=True)
    with io.open(ENV_LOG, 'a', encoding='utf-8') as lf:
        subprocess.Popen([sys.executable, ENV_DRIVER, 'run'],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=_DETACHED_FLAGS,
                         close_fds=True)  # r317 law: explicit std redirect => close_fds=True
    time.sleep(4)
    ds = _driver_status()
    if ds.get('state') != 'running' or not _pid_alive(ds.get('pid')):
        raise RuntimeError('post-ignition probe FAIL: state=%s live=%s (log: %s)' % (
            ds.get('state'), _pid_alive(ds.get('pid')), ENV_LOG))
    return {'runner': 'st005_gpt_sovits_env_ignite', 'verdict': 'ignited',
            'pid': ds.get('pid'), 'phase': ds.get('phase'),
            'status_face': ENV_STATUS, 'log': ENV_LOG}


CANON_VOICE_META = {
    'CH':       {'gender': 'male', 'age_feel': 'early-20s', 'texture': 'calm, restrained, quietly intense young man'},
    'XIONG':    {'gender': 'male', 'age_feel': '50s', 'texture': 'deep, unhurried, authoritative magnate'},
    'RED':      {'gender': 'female', 'age_feel': 'early-20s', 'texture': 'bright, crisp, professional office voice'},
    'MANCANG':  {'gender': 'male', 'age_feel': 'mid-20s', 'texture': 'loud, cheerful, plump-market-vendor warmth'},
    'XIONGWEI': {'gender': 'male', 'age_feel': 'mid-20s', 'texture': 'cold, sharp, clipped, minimal words'},
    'FATHER':   {'gender': 'male', 'age_feel': '50s', 'texture': 'weary, kind, low and worn'},
    'BOY':      {'gender': 'male', 'age_feel': 'child ~12', 'texture': 'thin, frightened, high-pitched'},
}


def st006_voice_bank_manifest(st):
    """ST-006: voice-bank manifest v0.1 (VOICE-PIPELINE-SKELETON-v1 sec.2 first
    entries). 7 canon character entries per drama-001-stockera id bank; entry
    schema carries voice_manifest descriptors + empty ref_clips (honest: clip
    sourcing is the NEXT station, gated on env ready) + consistency-gate spec
    (声音面移植 of the ST-004 anchor discipline: entry admission requires the
    音色一致检). Sourcing shortlist = offline facts only, license caveat honest.
    Products: content/drama/voice_bank/manifest.json + outbox receipt."""
    vb_dir = os.path.join(QDIR, 'voice_bank')
    os.makedirs(vb_dir, exist_ok=True)
    entries = []
    for cid, meta in CANON_VOICE_META.items():
        entries.append({
            'id': cid,
            'voice_manifest': meta,
            'engine': 'gpt-sovits',
            'ref_clips': [],
            'params': {},
            'entry_state': 'awaiting-ref-clips',
            'added_ts': None,
        })
    manifest = {
        'schema': 'drama-voice-bank-v0.1',
        'created': now_iso(),
        'characters': entries,
        'consistency_gate': {
            'name': '音色一致检 (voice-face analog of ST-004 anchor precheck)',
            'rule': 'entry admission requires 1-3 ref clips passing cross-clip '
                    'consistency check; intra-bank drift across episodes = reject',
            'pinned_by': 'VOICE-PIPELINE-SKELETON-v1 sec.2 + 人物一致性律 (voice face)',
        },
        'ref_clip_sourcing_shortlist': [
            {'corpus': 'AISHELL-3 (SLR93)', 'face': 'multi-speaker Mandarin, ~8k speakers; '
             'license = research-use caveats -- commercial drama use needs license review (honest gap)'},
            {'corpus': 'aidatatang_200zh (SLR29)', 'face': 'Mandarin, license review needed'},
            {'corpus': 'self-recorded / CEO-provided clips', 'face': 'zero license risk, '
             'physical-domain action; highest tone-fit ceiling'},
            {'corpus': 'zero-shot bootstrap from a stock base voice + cross-check',
             'face': 'possible after env ready; consistency gate still applies'},
        ],
        'honest_gaps': [
            'no ref clips yet (clip acquisition = next station, gated on ST-005 env)',
            'corpus licenses not yet reviewed for commercial use',
            'engine params pinned at the first synthesis station, not here',
        ],
        'law_refs': ['O-20261018-2144-bm-c sec.2.1', 'VOICE-PIPELINE-SKELETON-v1 sec.2/7',
                     'DIRECTOR-STEP-GATE-v1'],
    }
    mpath = os.path.join(vb_dir, 'manifest.json')
    with io.open(mpath, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    out_dir = os.path.join(QDIR, 'outbox')
    os.makedirs(out_dir, exist_ok=True)
    md = []
    md.append('# 声银行清单 v0.1（voice-bank manifest · ST-006）')
    md.append('')
    md.append('> 站点=CONTENT-LOOP v0.1 ST-006；承=ST-003 评估件「后续批次：环境安装+首批声银行条目」；')
    md.append('> 正身=content/drama/voice_bank/manifest.json（本件=回执面）。生成时点=%s。' % now_iso())
    md.append('')
    md.append('## 7 正典角色声音条目（voice_manifest 描述档）')
    md.append('')
    md.append('| id | 性别 | 年龄感 | 质感 | 状态 |')
    md.append('|---|---|---|---|---|')
    for e in entries:
        m = e['voice_manifest']
        md.append('| %s | %s | %s | %s | %s |' % (e['id'], m['gender'], m['age_feel'],
                                                 m['texture'], e['entry_state']))
    md.append('')
    md.append('## 入行门（锚清洗纪律的声音面移植）')
    md.append('')
    md.append('- 每角色 1-3 条参考音入行前过「音色一致检」；跨集音色漂移=判负打回（行内零漂移）。')
    md.append('- 与视觉面 ANCHOR 三元组硬约束（ST-004）同构：入行前过检，行内零漂移。')
    md.append('')
    md.append('## 参考音寻源短线（离线事实·未复核许可面）')
    md.append('')
    for s in manifest['ref_clip_sourcing_shortlist']:
        md.append('- **%s**：%s' % (s['corpus'], s['face']))
    md.append('')
    md.append('## 诚实缺口')
    md.append('')
    for g in manifest['honest_gaps']:
        md.append('- %s' % g)
    rcp = os.path.join(out_dir, 'VOICE-BANK-MANIFEST-v0.1.md')
    with io.open(rcp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    return {'runner': 'st006_voice_bank_manifest', 'manifest': mpath,
            'receipt': rcp, 'characters': len(entries), 'verdict': 'manifest-v0.1-drafted'}




# ---------------- runners (v0.2 registry: ST-007 first-synthesis smoke) ----------------

FIRST_SYNTH_DRIVER = os.path.join(QDIR, 'runner_assets', 'first_synth_smoke.py')
FIRST_SYNTH_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'first_synthesis_smoke.json')


def _first_synth_status():
    try:
        with io.open(FIRST_SYNTH_STATUS, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return {}


def st007_first_synthesis_smoke(st):
    """ST-007: first-synthesis smoke (GPT-SoVITS zero-shot chain validation,
    r1016-promoted r1017 FIRST ACTION). Idempotent ensure-done: completed smoke
    (status face state=done + product wav present) -> done-early with evidence;
    else execute the versioned driver synchronously (bounded 540s < 600s lock
    stale guard, CREATE_NO_WINDOW). Driver chain: in-house r998 audition ref
    clip + MANIFEST text -> inference_cli v1 pretrained pair -> output.wav ->
    duration/RMS/sr verify -> status face + outbox receipt. No voice_bank
    writes (chain validation only)."""
    ds = _first_synth_status()
    if ds.get('state') == 'done' and os.path.exists(ds.get('output_wav') or ''):
        return {'runner': 'st007_first_synthesis_smoke', 'verdict': 'done-early',
                'output_wav': ds.get('output_wav'), 'output_s': ds.get('output_s'),
                'ref_clip': (ds.get('ref_clip') or {}).get('source'),
                'status_face': FIRST_SYNTH_STATUS, 'receipt': ds.get('receipt')}
    r = subprocess.run([sys.executable, FIRST_SYNTH_DRIVER, 'run'],
                       capture_output=True, timeout=540, creationflags=_NO_WINDOW)
    tail = ((r.stdout or b'').decode('utf-8', 'replace') +
            (r.stderr or b'').decode('utf-8', 'replace')).strip()[-300:]
    ds = _first_synth_status()
    if r.returncode != 0 or ds.get('state') != 'done':
        raise RuntimeError('first-synthesis smoke FAIL rc=%s state=%s tail=%s' % (
            r.returncode, ds.get('state'), tail))
    return {'runner': 'st007_first_synthesis_smoke', 'verdict': 'smoke-done',
            'output_wav': ds.get('output_wav'), 'output_s': ds.get('output_s'),
            'ref_clip': (ds.get('ref_clip') or {}).get('source'),
            'status_face': FIRST_SYNTH_STATUS, 'receipt': ds.get('receipt')}


# ---------------- runners (v0.2 registry: ST-008 voice-bank entries) ----------------

VB_DRIVER = os.path.join(QDIR, 'runner_assets', 'voice_bank_entries.py')
VB_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'voice_bank_entries.json')


def _vb_status():
    try:
        with io.open(VB_STATUS, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return {}


def st008_voice_bank_entries(st):
    """ST-008: canon voice-bank entries v0.1 (r1017 next-pointer item 2, voice
    P1 <=10-22). Idempotent ensure-done: completed admission (status face
    state=done + admitted_n>=1) -> done-early with evidence; else execute the
    versioned driver synchronously (bounded 420s < 600s lock stale guard,
    CREATE_NO_WINDOW). Driver: role-aligned 1-3 ref clips per canon character
    from in-house r998 audition assets + 音色一致检 v0.1 deterministic proxy
    gate -> manifest ref_clips admitted + status face + outbox receipt."""
    ds = _vb_status()
    if ds.get('state') == 'done' and int(ds.get('admitted_n', 0)) >= 1:
        return {'runner': 'st008_voice_bank_entries', 'verdict': 'done-early',
                'admitted_n': ds.get('admitted_n'),
                'no_material': ds.get('no_material'),
                'status_face': VB_STATUS, 'receipt': ds.get('receipt')}
    r = subprocess.run([sys.executable, VB_DRIVER, 'run'],
                       capture_output=True, timeout=420, creationflags=_NO_WINDOW)
    tail = ((r.stdout or b'').decode('utf-8', 'replace') +
            (r.stderr or b'').decode('utf-8', 'replace')).strip()[-300:]
    ds = _vb_status()
    if r.returncode != 0 or ds.get('state') != 'done':
        raise RuntimeError('voice-bank entries FAIL rc=%s state=%s tail=%s' % (
            r.returncode, ds.get('state'), tail))
    return {'runner': 'st008_voice_bank_entries', 'verdict': 'entries-admitted',
            'admitted_n': ds.get('admitted_n'), 'admitted': ds.get('admitted'),
            'single_clip': ds.get('single_clip'),
            'no_material': ds.get('no_material'),
            'status_face': VB_STATUS, 'receipt': ds.get('receipt')}


# ---------------- runners (v0.2 registry: ST-009 voice differentiation eval) ----------------

VD_DRIVER = os.path.join(QDIR, 'runner_assets', 'voice_differentiation_eval.py')
VD_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'voice_differentiation_eval.json')


def _vd_status():
    try:
        with io.open(VD_STATUS, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return {}


def st009_voice_differentiation_eval(st):
    """ST-009: character voice differentiation eval v0.1 (ST-008 receipt
    shared-base-debt face; r1018 next-pointer item 3). Idempotent ensure-done:
    completed eval (status face state=done + same_voice_band_pairs list +
    receipt on disk) -> done-early with evidence; else execute the versioned
    driver synchronously (bounded 300s < 600s lock stale guard,
    CREATE_NO_WINDOW). Driver: manifest ref-clip F0/RMS/centroid medians ->
    cross-character same-voice-band matrix + deterministic pitch-tier search
    (semantic direction constraints, min total shift, family pairs F0 rel
    >= 0.15) + method-feasibility receipt. Eval only: no voice_bank writes."""
    ds = _vd_status()
    if (ds.get('state') == 'done'
            and isinstance(ds.get('same_voice_band_pairs'), list)
            and os.path.exists(os.path.join(ROOT, ds.get('receipt') or '_'))):
        return {'runner': 'st009_voice_differentiation_eval', 'verdict': 'done-early',
                'same_voice_band_pairs': len(ds.get('same_voice_band_pairs') or []),
                'pitch_tier': ds.get('pitch_tier'),
                'status_face': VD_STATUS, 'receipt': ds.get('receipt')}
    r = subprocess.run([sys.executable, VD_DRIVER, 'run'],
                       capture_output=True, timeout=300, creationflags=_NO_WINDOW)
    tail = ((r.stdout or b'').decode('utf-8', 'replace') +
            (r.stderr or b'').decode('utf-8', 'replace')).strip()[-300:]
    ds = _vd_status()
    if r.returncode != 0 or ds.get('state') != 'done':
        raise RuntimeError('voice differentiation eval FAIL rc=%s state=%s tail=%s' % (
            r.returncode, ds.get('state'), tail))
    return {'runner': 'st009_voice_differentiation_eval', 'verdict': 'eval-done',
            'same_voice_band_pairs': len(ds.get('same_voice_band_pairs') or []),
            'pitch_tier': ds.get('pitch_tier'),
            'status_face': VD_STATUS, 'receipt': ds.get('receipt')}


# ---------------- runners (v0.2 registry: ST-010 pitch-tier test synthesis) ----------------

PTT_DRIVER = os.path.join(QDIR, 'runner_assets', 'pitch_tier_test_synth.py')
PTT_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'pitch_tier_test_synth.json')


def _ptt_status():
    try:
        with io.open(PTT_STATUS, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return {}


def st010_pitch_tier_test_synth(st):
    """ST-010: pitch-tier test-synthesis station (r1020 next-pointer item 1 /
    r1019 debt; ST-009 receipt next-station row). Idempotent ensure-done:
    completed run (status face state=done + all three tier wavs on disk) ->
    done-early with evidence; else execute the versioned driver synchronously
    (bounded 480s < 600s lock stale guard, CREATE_NO_WINDOW). Driver chain:
    XIONG/XIONGWEI/FATHER 1 line each through GPT-SoVITS zero-shot (admitted
    manifest ref clips, same fixed target text) + tier DSP (offsets
    machine-read from the ST-009 face) + RMS re-match + deterministic F0
    separation re-measure + gate (every family pair F0 rel >= 0.15).
    Products: st010 wavs (media area) + status face + outbox receipt."""
    ds = _ptt_status()
    if ds.get('state') == 'done':
        missing = [c for c in ('XIONG', 'XIONGWEI', 'FATHER')
                   if not os.path.exists(os.path.join(
                       GRP, 'media', 'drama-tools', 'voice_smoke', 'st010', c, 'tier.wav'))]
        if not missing:
            return {'runner': 'st010_pitch_tier_test_synth', 'verdict': 'done-early',
                    'gate': ds.get('gate'), 'pairs_after': ds.get('pairs_after_tier'),
                    'status_face': PTT_STATUS, 'receipt': ds.get('receipt')}
    r = subprocess.run([sys.executable, PTT_DRIVER, 'run'],
                       capture_output=True, timeout=480, creationflags=_NO_WINDOW)
    tail = ((r.stdout or b'').decode('utf-8', 'replace') +
            (r.stderr or b'').decode('utf-8', 'replace')).strip()[-300:]
    ds = _ptt_status()
    if ds.get('state') != 'done':
        raise RuntimeError('pitch-tier test-synth FAIL rc=%s state=%s tail=%s' % (
            r.returncode, ds.get('state'), tail))
    return {'runner': 'st010_pitch_tier_test_synth',
            'verdict': 'tier-synth-done gate=%s' % ds.get('gate'),
            'gate': ds.get('gate'), 'pairs_after': ds.get('pairs_after_tier'),
            'status_face': PTT_STATUS, 'receipt': ds.get('receipt')}


# ---------------- runners (v0.2 registry: ST-012 character-voice finetune) ----------------

ST012_DRIVER = os.path.join(QDIR, 'runner_assets', 'st012_character_lora_train.py')
ST012_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'st012_voice_finetune.json')
ST012_LOG = ST012_STATUS + '.log'


def _st012_status():
    try:
        with io.open(ST012_STATUS, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return {}


def st012_character_lora_train(st):
    """ST-012: character-voice finetune lane (gpu-night). Closes the shared-base
    debt per ST-009 negative finding (same-base finetune cannot separate a
    family -> bootstrap a NEW base first, then finetune). Phases:
    bootstrap(IndexTTS zero-shot) / cuda(torch cu130) / data(.list) /
    prep(bert+cnhubert+sv+semantic) / s2(SoVITS) / s1(GPT) / verify(A/B).
    Each phase is checkpointed and idempotent; training ~minutes for a 49s
    corpus. Detached ignition (multi-phase, may outlive one 20-min round --
    ST-005 carrier precedent), status face polled each round; loop closes the
    station when the face reports done."""
    ds = _st012_status()
    if ds.get('state') == 'done':
        return {'runner': 'st012_character_lora_train', 'verdict': 'done-early',
                'phases_done': ds.get('phases_done'), 'status_face': ST012_STATUS,
                'receipt': ds.get('receipt')}
    if ds.get('state') == 'running':
        pid = ds.get('pid')
        if pid and _pid_alive(pid):
            return {'runner': 'st012_character_lora_train', 'verdict': 'already-running',
                    'pid': pid, 'phase': ds.get('phase'),
                    'phases_done': ds.get('phases_done'), 'status_face': ST012_STATUS}
        # stale running face -> re-ignite (phases are idempotent)
    r = subprocess.run([sys.executable, ST012_DRIVER, 'selftest'],
                       capture_output=True, timeout=180, creationflags=_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError('ST-012 driver selftest FAIL: ' +
                           (r.stdout or b'').decode('utf-8', 'replace').strip()[-200:])
    with io.open(ST012_LOG, 'a', encoding='utf-8') as lf:
        subprocess.Popen([sys.executable, ST012_DRIVER, 'run'],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=_DETACHED_FLAGS,
                         close_fds=True)
    time.sleep(5)
    ds = _st012_status()
    return {'runner': 'st012_character_lora_train',
            'verdict': 'ignited' if ds.get('state') in ('running', 'done') else 'ignite-probe-warn',
            'state': ds.get('state'), 'phase': ds.get('phase'),
            'status_face': ST012_STATUS, 'log': ST012_LOG}


ST013_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'st013_dubbing_sheet.json')
DUBBING_SHEET_PREP = os.path.join(QDIR, 'runner_assets', 'dubbing_sheet_prep.py')


def st013_dubbing_sheet_prep(st):
    """ST-013 (13:2x fleet-fill order @bm-b): dubbing sheet preprocessing
    EP001-003 -- per-line speaker->voice-bank mapping / rule-based emotion
    v0.1 / est-sec vs shot-window fit flags from group-origin episode JSONs
    (fresh-blob law). CPU lane, zero cloud. Products: voice_sheets
    EP001-003-VO-SHEET.md + json twin + outbox receipt."""
    r = subprocess.run([sys.executable, DUBBING_SHEET_PREP, 'selftest'],
                       capture_output=True, timeout=120, creationflags=_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError('dubbing-sheet selftest FAIL: ' +
                           r.stdout.decode('utf-8', 'replace').strip()[-200:])
    r = subprocess.run([sys.executable, DUBBING_SHEET_PREP, 'run'],
                       capture_output=True, timeout=300, creationflags=_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError('dubbing-sheet prep FAIL rc=%s tail=%s' % (
            r.returncode, r.stdout.decode('utf-8', 'replace').strip()[-200:] +
            r.stderr.decode('utf-8', 'replace').strip()[-200:]))
    ds = rd_json(ST013_STATUS, None) or {}
    if ds.get('state') != 'done':
        raise RuntimeError('dubbing-sheet prep FAIL rc=%s state=%s' % (
            r.returncode, ds.get('state')))
    return {'runner': 'st013_dubbing_sheet_prep',
            'verdict': 'sheet-done rows=%s gap=%s overflow=%s' % (
                (ds.get('stats') or {}).get('rows'),
                (ds.get('stats') or {}).get('gap_rows'),
                ((ds.get('stats') or {}).get('by_fit') or {}).get('OVERFLOW', 0)),
            'status_face': ST013_STATUS, 'receipt':
            os.path.join(QDIR, 'outbox', 'ST-013-DUBBING-SHEET-RECEIPT.md')}


RUNNERS = {
    'st001_rootcause_gather': st001_rootcause_gather,
    'st003_voice_library_first_batch': st003_voice_library_first_batch,
    'st004_csa_anchor_precheck': st004_csa_anchor_precheck,
    'st005_gpt_sovits_env_ignite': st005_gpt_sovits_env_ignite,
    'st006_voice_bank_manifest': st006_voice_bank_manifest,
    'st007_first_synthesis_smoke': st007_first_synthesis_smoke,
    'st008_voice_bank_entries': st008_voice_bank_entries,
    'st009_voice_differentiation_eval': st009_voice_differentiation_eval,
    'st010_pitch_tier_test_synth': st010_pitch_tier_test_synth,
    'st012_character_lora_train': st012_character_lora_train,
    'st013_dubbing_sheet_prep': st013_dubbing_sheet_prep,
}

# developer-seat maintenance map: station -> runner for stations still on the
# v0.2-pending placeholder (adopt-runners flips them only via the lock).
RUNNER_ADOPT = {
    'ST-003': 'st003_voice_library_first_batch',
    'ST-004': 'st004_csa_anchor_precheck',
    'ST-012': 'st012_character_lora_train',
    'ST-013': 'st013_dubbing_sheet_prep',
}


def do_adopt_runners(mapping=None):
    """Maintenance op (developer seat): flip open stations from the
    'v0.2-pending' placeholder onto real runner names. Lock-held
    fresh-read-modify-write; touches ONLY the runner field."""
    ok, why = acquire_lock()
    if not ok:
        return {'verdict': 'lock-held', 'why': why, 'ts': now_iso()}
    try:
        q = rd_json(QPATH, None)
        if q is None:
            return {'verdict': 'mechanism-fault', 'why': 'queue.json unreadable',
                    'ts': now_iso()}
        mapping = mapping or RUNNER_ADOPT
        changed = []
        for st in q['stations']:
            if st.get('state') != 'open' or st.get('runner') != 'v0.2-pending':
                continue
            new = mapping.get(st['id'])
            if new and new in RUNNERS:
                st['runner'] = new
                changed.append(st['id'])
        if changed:
            wr_json(QPATH, q)
            regen_md(q)
        return {'verdict': 'adopted' if changed else 'no-change',
                'stations': changed, 'ts': now_iso()}
    finally:
        release_lock()


def station_plan(q):
    """Returns (verdict, station, why) for the first actionable station."""
    for st in q['stations']:
        if st['state'] == 'claimed':
            # crashed-claim reclaim after 30min not implemented in v0.1; honest hold
            return 'held', st, 'claim-in-place (v0.1 has no reclaim yet)'
        if st['state'] != 'open':
            continue
        ok, why = require_ok(q, st)
        if not ok:
            continue  # gate/dep closed -> try next station
        runner = st.get('runner') or 'none'
        if runner in RUNNERS:
            return 'claimable', st, 'runner-ready'
        return 'held', st, 'runner-pending:' + runner
    return 'no-station', None, 'all stations blocked/pending/done'


def do_round():
    ok, why = acquire_lock()
    if not ok:
        return {'verdict': 'lock-held', 'why': why, 'ts': now_iso()}
    try:
        q = rd_json(QPATH, None)
        if q is None:
            return {'verdict': 'mechanism-fault', 'why': 'queue.json unreadable', 'ts': now_iso()}
        verdict, st, why = station_plan(q)
        action = None
        if verdict == 'claimable':
            st['state'] = 'claimed'
            st['claim'] = 'claimed@bm-b@' + now_iso()
            wr_json(QPATH, q)
            append_line(CLAIMS, json.dumps({'ts': now_iso(), 'station': st['id'],
                                           'action': 'claimed', 'by': 'bm-b'}, ensure_ascii=False))
            try:
                action = RUNNERS[st['runner']](st)
                st['state'] = 'done'
                st['done_at'] = now_iso()
            except Exception as e:
                st['state'] = 'open'   # honest rollback; station stays queued
                action = {'runner': st['runner'], 'verdict': 'runner-error', 'err': str(e)[:200]}
            q = rd_json(QPATH, q)
            for s2 in q['stations']:
                if s2['id'] == st['id']:
                    s2['state'] = st['state']
                    s2['claim'] = st.get('claim')
                    if 'done_at' in st:
                        s2['done_at'] = st['done_at']
            wr_json(QPATH, q)
            append_line(CLAIMS, json.dumps({'ts': now_iso(), 'station': st['id'],
                                            'action': st['state'], 'detail': action},
                                           ensure_ascii=False))
        regen_md(q)
        ls = rd_json(LSTATE, {'rounds': 0})
        ls['rounds'] = int(ls.get('rounds', 0)) + 1
        ls['last_ts'] = now_iso()
        wr_json(LSTATE, ls)
        append_line(RLOG, '%s | round %s | %s | %s | %s' % (
            now_iso(), ls['rounds'], verdict, (st or {}).get('id', '-'),
            json.dumps(action or why, ensure_ascii=False)[:220]))
        return {'verdict': verdict, 'station': (st or {}).get('id'), 'why': why,
                'action': action, 'ts': now_iso(), 'loop_rounds': ls['rounds']}
    finally:
        release_lock()


def do_scan():
    q = rd_json(QPATH, None)
    if q is None:
        return {'verdict': 'mechanism-fault', 'why': 'queue.json unreadable'}
    verdict, st, why = station_plan(q)
    return {'verdict': verdict, 'station': (st or {}).get('id'), 'why': why, 'ts': now_iso()}


def selftest():
    asserts = []
    q = rd_json(QPATH, {})
    asserts.append(('queue-readable', isinstance(q.get('stations'), list) and len(q['stations']) >= 1))
    ids = [s['id'] for s in q.get('stations', [])]
    asserts.append(('ids-unique', len(ids) == len(set(ids))))
    v, st, why = station_plan(q)
    asserts.append(('plan-verdict-valid', v in ('claimable', 'held', 'no-station')))
    # done stations' runner names are historical labels (r1022 ST-011 was
    # direct-executed with an ad-hoc script, no registry wrapper) -- the
    # known-runner assert targets future-executable stations only
    known = all((s.get('runner') or 'none') in list(RUNNERS) + ['none', 'v0.2-pending']
                for s in q.get('stations', []) if s.get('state') != 'done')
    asserts.append(('runners-known-or-pending', known))
    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL', 'asserts':
                      {k: ok for k, ok in asserts}}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'round'
    if cmd == 'round':
        print(json.dumps(do_round(), ensure_ascii=False))
    elif cmd == 'scan':
        print(json.dumps(do_scan(), ensure_ascii=False))
    elif cmd == 'adopt-runners':
        print(json.dumps(do_adopt_runners(RUNNER_ADOPT), ensure_ascii=False))
    elif cmd == 'selftest':
        sys.exit(selftest())
    else:
        print(json.dumps({'verdict': 'usage', 'cmds': ['round', 'scan', 'adopt-runners', 'selftest']}))
