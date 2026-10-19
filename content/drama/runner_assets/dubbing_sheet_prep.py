"""ST-013 dubbing-sheet preprocessing driver (drama voice lane, bm-b host).

Purpose: per-line voice-cast sheets for EP001-003 (一路长虹) built from the
group-repo episode JSONs (fresh origin blobs per the 集团面新鲜读律) mapped
against content/drama/voice_bank/manifest.json. Every spoken shot becomes a
dubbing row: normalized speaker(s) -> voice-bank ref (or honest gap), rule-based
emotion tag v0.1, char-rate est-sec vs the shot window (fit flag). Multi-speaker
lines split per-sentence with a documented in-listed-order heuristic; minors and
the narrator surface as honest gaps (no bank entry) so the casting station knows
exactly what is missing before any synthesis burn.

Deterministic, zero-network (local git objects only after the standard group
fetch), zero cloud (429 economy). Products are the ST-013 station contract:
content/drama/voice_sheets/EP001-003-VO-SHEET.md + machine json twin + outbox
receipt. Commands: run / status / selftest.
Status face: results/drama_env/st013_dubbing_sheet.json (in-repo)
Laws: U060 no-window; CPU lane (13:2x fleet-fill order @bm-b leg);
QUEUE.md never hand-edited (regen = content_loop_step regen_md);
人物一致性律 voice face; DIRECTOR-STEP-GATE-v1 (sheet = pre-production face,
director review happens at the casting/synthesis station, not here).
"""
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GRP = r'C:\Fluxgroup\FluxGroup'
EP_DIR = 'cph4/fleet/drama-001-stockera/episodes'
EPS = ['EP001', 'EP002', 'EP003']
VB_MANIFEST = os.path.join(ROOT, 'content', 'drama', 'voice_bank', 'manifest.json')
SHEET_DIR = os.path.join(ROOT, 'content', 'drama', 'voice_sheets')
SHEET_MD = os.path.join(SHEET_DIR, 'EP001-003-VO-SHEET.md')
SHEET_JSON = os.path.join(SHEET_DIR, 'EP001-003-VO-SHEET.json')
OUTBOX = os.path.join(ROOT, 'content', 'drama', 'outbox')
RECEIPT = os.path.join(OUTBOX, 'ST-013-DUBBING-SHEET-RECEIPT.md')
STATUS = os.path.join(ROOT, 'results', 'drama_env', 'st013_dubbing_sheet.json')
_NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW (U060 zero-desktop-flash law)

# ---- speaker normalization -------------------------------------------------
# raw speaker token -> (bank char id | None, role label)
SPEAKER_MAP = {
    '旁白': (None, 'NARRATOR'),
    '父': ('FATHER', 'FATHER'),
    '长': ('CH', 'CH'),
    '熊': ('XIONG', 'XIONG'),
    '熊伟': ('XIONGWEI', 'XIONGWEI'),
    '满仓': ('MANCANG', 'MANCANG'),
    '红利': ('RED', 'RED'),
    '门卫': (None, 'MINOR:GATEKEEPER'),
    '散户甲': (None, 'MINOR:RETAILER-A'),
    '散户群': (None, 'MINOR:CROWD'),
    '经纪（画外）': (None, 'MINOR:BROKER-VO'),
    '经纪': (None, 'MINOR:BROKER-VO'),
}
# speaker-id emotion baselines (v0.1 delivery hints)
BASE_EMOTION = {
    'NARRATOR': 'narration',
    'FATHER': 'weary',
    'XIONG': 'cold',
    'XIONGWEI': 'cold',
    'RED': 'crisp',
    'MANCANG': 'cheerful',
    'CH': 'calm',
}
# per-id speech rates (chars/sec, v0.1 constants -- disclosed in the sheet)
RATE = {'NARRATOR': 5.0}
RATE_DEFAULT = 4.2
FIT_OK, FIT_TIGHT = 0.85, 1.05


def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def say(msg):
    line = '%s %s' % (now_iso(), msg)
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        try:
            print(line.encode('gbk', errors='replace').decode('gbk'), flush=True)
        except Exception:
            pass


def wr_json(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def rd_json(p, default):
    try:
        with io.open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def git_show_origin(path):
    """Fresh group-origin blob read (新鲜读律). Returns (bytes, blob_sha) or raises."""
    r = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:%s' % path],
                        capture_output=True, timeout=60, creationflags=_NO_WINDOW)
    if r.returncode != 0:
        r2 = subprocess.run(['git', '-C', GRP, 'fetch', 'origin'],
                            capture_output=True, timeout=120, creationflags=_NO_WINDOW)
        if r2.returncode != 0:
            raise RuntimeError('group fetch FAIL: %s' % r2.stderr.decode('utf-8', 'replace')[-160:])
        r = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:%s' % path],
                            capture_output=True, timeout=60, creationflags=_NO_WINDOW)
        if r.returncode != 0:
            raise RuntimeError('git show origin FAIL %s: %s' % (path, r.stderr.decode('utf-8', 'replace')[-160:]))
    s = subprocess.run(['git', '-C', GRP, 'rev-parse', 'origin/main:%s' % path],
                       capture_output=True, timeout=30, creationflags=_NO_WINDOW)
    blob_sha = s.stdout.decode('utf-8', 'replace').strip() if s.returncode == 0 else 'unknown'
    return r.stdout, blob_sha


def split_speakers(raw):
    """raw speaker field -> [(id, role_label, bank_id_or_None)]; multi on 、."""
    out = []
    for tok in [x.strip() for x in raw.split('、') if x.strip()]:
        bank_id, role = SPEAKER_MAP.get(tok, (None, 'UNMAPPED:' + tok))
        out.append({'role': role, 'bank_id': bank_id})
    return out


def split_sentences(text):
    """CJK sentence split keeping delimiters (。！？)."""
    parts = re.findall(r'[^。！？]*[。！？]?', text)
    return [p for p in parts if p.strip()]


def tag_emotion(role, text, fx):
    """Deterministic v0.1 delivery hint. First hit wins; documented rule order.

    panic -> solemn -> sad -> joy -> question -> urgent -> tense(fx/ellipsis)
    -> speaker baseline. NOT a performance spec: the casting/synthesis station
    + director review own final delivery.
    """
    t = text
    if any(k in t for k in ('完了', '救命', '疯了', '不要啊', '跳楼')):
        return 'panic'
    if any(k in t for k in ('记住', '最后一课', '牛市没有眼泪')):
        return 'solemn'
    if any(k in t for k in ('眼泪', '死了', '墓')) and role != 'MANCANG':
        return 'sad'
    if any(k in t for k in ('哈', '笑', '太好了', '成了', '翻倍', '股神')) or \
       (role == 'MANCANG' and '！' in t):
        return 'joy'
    if '？' in t:
        return 'question'
    if '！' in t:
        return 'urgent'
    if '……' in t:
        return 'tense'
    if any(k in fx for k in ('心跳', '警报', '急促', '砸', '切断')):
        return 'tense'
    return BASE_EMOTION.get(role, 'calm')


def est_sec(role, text):
    chars = len(text.strip())
    rate = RATE.get(role, RATE_DEFAULT)
    return round(chars / rate, 1) if chars else 0.0


def fit_flag(est, window):
    if window <= 0:
        return 'NO-WINDOW'
    r = est / window
    if r <= FIT_OK:
        return 'OK'
    if r <= FIT_TIGHT:
        return 'TIGHT'
    return 'OVERFLOW'


def bank_ref(vb, bank_id):
    """voice-bank ref face for a char id; honest gap notes otherwise."""
    if bank_id is None:
        return {'bank_id': None, 'entry_state': None, 'ref_clip': None}
    for c in vb.get('characters', []):
        if c.get('id') == bank_id:
            clips = c.get('ref_clips') or []
            return {'bank_id': bank_id, 'entry_state': c.get('entry_state'),
                    'ref_clip': clips[0]['name'] if clips else None}
    return {'bank_id': bank_id, 'entry_state': 'NOT-IN-BANK', 'ref_clip': None}


def _vo_ref_str(ref, role):
    if ref['bank_id'] is None:
        return 'GAP:%s(no bank entry)' % role
    if ref['entry_state'] not in ('admitted', 'admitted-interim', 'admitted-single-clip'):
        return 'GAP:%s(%s)' % (role, ref['entry_state'])
    return '%s/%s[%s]' % (role, ref['bank_id'], ref['entry_state'])


def build_rows(ep_key, ep_data, vb):
    rows = []
    for shot in ep_data.get('shots', []):
        n = shot.get('n')
        text = (shot.get('sub') or '').strip()
        raw_spk = (shot.get('speaker') or '').strip()
        if not text or not raw_spk:
            continue  # card shots / pure fx shots carry no dubbing line
        fx = shot.get('fx') or ''
        window = shot.get('dur') or 0
        spks = split_speakers(raw_spk)
        if len(spks) > 1:
            sents = split_sentences(text)
            if len(sents) == len(spks):
                for i, (spk, sent) in enumerate(zip(spks, sents)):
                    rows.append(_row(ep_key, n, chr(ord('a') + i), spk, sent, fx, window, vb,
                                     flag='auto-split-heuristic'))
            else:
                rows.append(_row(ep_key, n, '', spks, text, fx, window, vb,
                                 flag='needs-manual-split'))
        else:
            rows.append(_row(ep_key, n, '', spks[0], text, fx, window, vb, flag=None))
    return rows


def _row(ep_key, n, suffix, spk, text, fx, window, vb, flag=None):
    # spk: single-speaker dict, OR the whole list for needs-manual-split rows
    # (sentence count != speaker count -> row kept whole, casting station splits)
    if isinstance(spk, list):
        roles = [s['role'] for s in spk]
        refs = [bank_ref(vb, s['bank_id']) for s in spk]
        role = roles[0]                      # primary-speaker emotion heuristic
        vo_ref = ' / '.join(_vo_ref_str(r, rl) for r, rl in zip(refs, roles))
        bank_id = [s['bank_id'] for s in spk]
        entry_state = '+'.join(sorted({str(r['entry_state']) for r in refs}))
        ref_clip = [r['ref_clip'] for r in refs]
    else:
        role = spk['role']
        ref = bank_ref(vb, spk['bank_id'])
        vo_ref = _vo_ref_str(ref, role)
        bank_id = spk['bank_id']
        entry_state = ref['entry_state']
        ref_clip = ref['ref_clip']
    est = est_sec(role, text)
    r = {
        'line_id': '%s-L%02d%s' % (ep_key, n, suffix),
        'shot_n': n,
        'speaker_role': role if not isinstance(spk, list) else '+'.join(
            s['role'] for s in spk),
        'bank_id': bank_id,
        'bank_entry_state': entry_state,
        'bank_ref_clip': ref_clip,
        'vo_ref': vo_ref,
        'emotion': tag_emotion(role, text, fx),
        'text': text,
        'est_sec': est,
        'shot_window_s': window,
        'fit': fit_flag(est, window),
        'flags': [flag] if flag else [],
    }
    return r


def do_run():
    say('ST-013 dubbing-sheet prep: start')
    vb = rd_json(VB_MANIFEST, None)
    if vb is None:
        raise RuntimeError('voice_bank manifest unreadable')
    os.makedirs(SHEET_DIR, exist_ok=True)
    os.makedirs(OUTBOX, exist_ok=True)
    eps, rows_all, sources = {}, [], []
    for ep in EPS:
        path = '%s/%s.json' % (EP_DIR, ep)
        blob, blob_sha = git_show_origin(path)
        data = json.loads(blob.decode('utf-8'))
        eps[ep] = data
        sources.append({'ep': ep, 'path': path, 'blob_sha': blob_sha,
                        'sha256': hashlib.sha256(blob).hexdigest()})
        rows = build_rows(ep, data, vb)
        rows_all.extend(rows)
        say('%s: %d shots -> %d dubbing rows' % (ep, len(data.get('shots', [])), len(rows)))

    stats = {
        'rows': len(rows_all),
        'by_fit': {},
        'by_role': {},
        'gap_rows': 0,
        'multi_split': 0,
        'manual_split': 0,
    }
    for r in rows_all:
        stats['by_fit'][r['fit']] = stats['by_fit'].get(r['fit'], 0) + 1
        stats['by_role'][r['speaker_role']] = stats['by_role'].get(r['speaker_role'], 0) + 1
        if r['bank_id'] is None:
            stats['gap_rows'] += 1
        for f in r['flags']:
            if f == 'auto-split-heuristic':
                stats['multi_split'] += 1
            if f == 'needs-manual-split':
                stats['manual_split'] += 1

    payload = {
        'schema': 'drama-vo-sheet-v0.1',
        'created': now_iso(),
        'station': 'ST-013',
        'sources': sources,
        'voice_bank_ref': 'content/drama/voice_bank/manifest.json (updated_ts=%s)' % vb.get('updated_ts'),
        'est_rule': 'chars/%.1fs (narrator %.1f) -- v0.1 constant-rate estimate, '
                    'not a synthesis pacing spec' % (RATE_DEFAULT, RATE['NARRATOR']),
        'emotion_rule': 'deterministic v0.1 first-hit-wins: panic->solemn->sad->joy->'
                        'question->urgent->tense(fx/ellipsis)->speaker baseline; '
                        'director review at casting station',
        'rows': rows_all,
        'stats': stats,
    }
    wr_json(SHEET_JSON, payload)
    _write_md(payload, eps, rows_all)
    _write_receipt(payload, eps, rows_all)
    status = {
        'schema': 'st013-dubbing-sheet-status-v0.1',
        'state': 'done',
        'ts': now_iso(),
        'station': 'ST-013',
        'stats': stats,
        'products': [SHEET_MD, SHEET_JSON, RECEIPT],
        'sources': sources,
    }
    wr_json(STATUS, status)
    say('ST-013 done: rows=%d gap=%d overflow=%d tight=%d' % (
        stats['rows'], stats['gap_rows'],
        stats['by_fit'].get('OVERFLOW', 0), stats['by_fit'].get('TIGHT', 0)))
    return 0


def _write_md(payload, eps, rows_all):
    md = []
    md.append('# 《一路长虹》配音台本预处理 EP001-003（ST-013 · v0.1）')
    md.append('')
    md.append('> 生成时点=%s；来源=集团仓 origin/main 剧集 JSON（逐件 blob 溯源见 JSON 孪生）；'
              '声库映射=content/drama/voice_bank/manifest.json。' % payload['created'])
    md.append('> 本件=预产台本面（station contract），非最终表演规格——情绪=规则 v0.1 提示、'
              '配音最终表演归选角/合成站+导演审（DIRECTOR-STEP-GATE-v1）。')
    md.append('')
    md.append('**读法**：预估秒=字数/速率（旁白 5.0、其余 4.2 字/秒·v0.1 常数）；'
              '配速 OK=预估≤85% 镜窗 / TIGHT=85%-105% / OVERFLOW=>105%（超窗=生产站必须'
              '决断：压语速 or 加镜窗）；GAP=声库无此角色条目（缺口如实，禁拿别的角色顶替）。')
    md.append('')
    for ep in EPS:
        data = eps[ep]
        rows = [r for r in rows_all if r['line_id'].startswith(ep + '-L')]
        md.append('## %s 《%s》（%d shots · 台本行 %d）' % (ep, data.get('title', ''), len(data.get('shots', [])), len(rows)))
        md.append('')
        md.append('| # | 说话人 | 声库映射 | 情绪 | 预估秒 | 镜窗 | 配速 | 台词 |')
        md.append('|---|---|---|---|---|---|---|---|')
        for r in rows:
            fl = ('·' + ','.join(r['flags'])) if r['flags'] else ''
            md.append('| %s | %s | %s | %s | %.1f | %s | %s | %s |' % (
                r['line_id'].replace(ep + '-', ''), r['speaker_role'], r['vo_ref'],
                r['emotion'], r['est_sec'], r['shot_window_s'], r['fit'] + fl, r['text']))
        md.append('')
    st = payload['stats']
    md.append('## 汇总与缺口')
    md.append('')
    md.append('- 台本行 %d（EP001/002/003）；配速 OK=%d TIGHT=%d OVERFLOW=%d。' % (
        st['rows'], st['by_fit'].get('OK', 0), st['by_fit'].get('TIGHT', 0), st['by_fit'].get('OVERFLOW', 0)))
    md.append('- 多说话人行：自动句序拆分 %d 行（heuristic·选角站须复核）、待人工拆 %d 行。' % (
        st['multi_split'], st['manual_split']))
    md.append('- **声库缺口（GAP 行 %d）**：旁白 NARRATOR 无声银行条目（voice_05 旁白底嗓·与'
              '满仓共底债=ST-012 根解面）；配角门卫/散户甲/散户群/经纪（画外）无条目=群演车道'
              '（后续站：复用底嗓+分档 or 一次性 extras）；本三集无 BOY 台词（BOY 零素材缺口不触发）。' % st['gap_rows'])
    md.append('- 满仓=admitted-interim（ST-011 去削波过渡面）；FATHER=单条参考音；'
              '情绪/时长=确定性 v0.1 提示面，最终表演与节奏归选角/合成站+导演审。')
    md.append('')
    with io.open(SHEET_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')


def _write_receipt(payload, eps, rows_all):
    st = payload['stats']
    md = []
    md.append('# ST-13 配音台本预处理回执（EP001-003 · ST-013 · r1024 bm-b）')
    md.append('')
    md.append('> 站点=CONTENT-LOOP ST-013；时点=%s；车道=cpu（13:2x 排满令 v2 @bm-b 日间填充腿）；'
              '零网络（本地 git 对象）零云端；纯确定性预处理。' % now_iso())
    md.append('')
    md.append('## 一、结论一览')
    md.append('')
    md.append('- 台本行 %d 行全量落表（MD 人读面 + JSON 机读孪生），逐行带声库映射/情绪提示/预估时长/镜窗配速。' % st['rows'])
    md.append('- 配速风险面：OVERFLOW %d 行 / TIGHT %d 行——生产站烧制前必须逐行决断（压语速或加镜窗），'
              '本表已按行点名。' % (st['by_fit'].get('OVERFLOW', 0), st['by_fit'].get('TIGHT', 0)))
    md.append('- 声库缺口如实：旁白+配角=%d 行 GAP（无银行条目·禁顶替）；多说话人 %d 行自动拆（heuristic 待选角站复核）+ %d 行待人工拆。' % (
        st['gap_rows'], st['multi_split'], st['manual_split']))
    md.append('')
    md.append('## 二、溯源')
    md.append('')
    for s in payload['sources']:
        md.append('- %s = origin/main:%s（blob %s · sha256 %s…）' % (
            s['ep'], s['path'], s['blob_sha'][:12], s['sha256'][:16]))
    md.append('')
    md.append('## 三、诚实边界')
    md.append('')
    md.append('- 情绪=规则 v0.1（首中即停词表+说话人基线），非表演规格；预估时长=常数速率，非合成实测。')
    md.append('- 旁白无银行条目与满仓共 voice_05 底嗓（ST-009 债）——本表只点名不解债，根解=ST-012 夜窗。')
    md.append('- 台本源=集团仓剧集 JSON 当前 origin 面；后续集数台本=同法续站。')
    md.append('')
    md.append('## 四、后续站位')
    md.append('')
    md.append('- 选角/合成站消费本表：GAP 行处置（旁白条目入银行 or 一次性方案）+OVERFLOW 行决断+多说话人复核。')
    md.append('- ST-012 角色声 LoRA 夜窗车道照单（22:0x·GitHub 轮子扫描先行）。')
    md.append('')
    with io.open(RECEIPT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')


def do_status():
    s = rd_json(STATUS, None)
    if s is None:
        print(json.dumps({'state': 'none', 'ts': now_iso()}, ensure_ascii=False))
        return 0
    print(json.dumps({'state': s.get('state'), 'ts': s.get('ts'),
                      'stats': s.get('stats'), 'ts_now': now_iso()}, ensure_ascii=False))
    return 0


def selftest():
    asserts = []
    # speaker map covers every raw speaker token in EP001-003 (frozen inventory
    # from the r1024 probe face; unmapped tokens would surface as UNMAPPED rows)
    inventory = ['旁白', '父', '门卫、长', '散户甲', '长', '满仓', '长、满仓', '散户群', '熊',
                 '经纪（画外）、长', '熊伟', '经纪（画外）', '熊伟、熊', '红利']
    for raw in inventory:
        toks = [x.strip() for x in raw.split('、') if x.strip()]
        asserts.append(('map:' + raw, all(t in SPEAKER_MAP for t in toks)))
    # emotion rules first-hit-wins on frozen cases
    cases = [
        ('MANCANG', '完了！我全仓啊！全部身家！', '', 'panic'),
        ('FATHER', '长虹，记住——牛市没有眼泪。', '', 'solemn'),
        ('XIONG', '他像一个人。一个我以为已经死了的人。', '', 'sad'),
        ('MANCANG', '翻倍了！闺女的嫁妆翻倍了！', '', 'joy'),
        ('RED', '昨天底部全仓的，是不是您？您怎么看联华实业？', '', 'question'),
        ('CH', '不对……这不是跌，是洗盘。', '', 'tense'),
        ('XIONG', '好胆识。可惜——联华，不是你能碰的。', '', 'cold'),
        ('NARRATOR', '十年，我背熟了这座城市的每一根 K 线。', '', 'narration'),
    ]
    for role, text, fx, want in cases:
        asserts.append(('emo:%s:%s' % (role, text[:6]), tag_emotion(role, text, fx) == want))
    # est + fit math
    asserts.append(('est-narrator', abs(est_sec('NARRATOR', '一二三四五六七八九十') - 2.0) < 0.06))
    asserts.append(('fit-overflow', fit_flag(4.0, 3) == 'OVERFLOW'))
    asserts.append(('fit-tight', fit_flag(3.0, 3) == 'TIGHT'))
    asserts.append(('fit-ok', fit_flag(2.0, 3) == 'OK'))
    # sentence split keeps delimiters and counts
    s = split_sentences('扫地的不进大厅。我只要一个能看见大屏的位置。')
    asserts.append(('split-2', len(s) == 2 and s[0].endswith('。')))
    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL',
                     'asserts': {k: ok for k, ok in asserts}}, ensure_ascii=False))
    return rc


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'run':
        try:
            sys.exit(do_run())
        except Exception as e:
            say('ST-013 FAIL: %s' % e)
            wr_json(STATUS, {'schema': 'st013-dubbing-sheet-status-v0.1', 'state': 'failed',
                             'err': str(e)[:300], 'ts': now_iso()})
            sys.exit(2)
    elif cmd == 'status':
        sys.exit(do_status())
    elif cmd == 'selftest':
        sys.exit(selftest())
    else:
        print(json.dumps({'usage': ['run', 'status', 'selftest']}))
        sys.exit(1)


if __name__ == '__main__':
    main()
