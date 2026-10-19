"""ST-012 character-voice finetune driver (drama voice lane, bm-b host, GPU-night).

Purpose: close the voice_bank shared-base debt (ST-008/ST-009/ST-011 disclosure:
MANCANG rendered from voice_05 == narrator's base). ST-009 negative finding
(pinned law): finetune on same-base material CANNOT separate a family -- the fix
only serves a NEW-BASE speaker. So the chain is:

  bootstrap (new base, zero-shot)  ->  export clean clips + texts
  ->  GPT-SoVITS v2Pro finetune (dataset prep + s2 SoVITS + s1 GPT)
  ->  A/B verify vs pre-finetune zero-shot on held-out lines
  ->  receipt

Bootstrap route: IndexTTS-2.5 zero-shot (in-house drama_voicegen.py) from a
stock voice that is NOT one of the four in-service bases (voice_04/05/07/12),
emotion vector tuned toward the character's cast tag (MANCANG -> comic happy).

Laws carried:
  - pit-spawn: __main__ guard; CREATE_NO_WINDOW children; detached ignition with
    explicit std redirect + close_fds=True; python -u + flush log (r317/r324/r680/r700)
  - phased + idempotent + checkpointed status face (ST-005 gpt_sovits_env_driver pattern)
  - ST-007 env repairs reused via import (jieba_fast shim + torchaudio sf fallback) --
    NOT duplicated, so one repair family lives in one place
  - 8G lane: fp16, grad_ckpt, small batch, low epoch count (webui defaults for 8G)
  - GPU valve: MiniGameOllamaKeepWarm paused while training runs (else the 10-min
    warm tick pulls the 4b model back into VRAM mid-train); restore duty recorded
  - cloud forbidden; U060 no-window

Commands: run / status / selftest / one <phase>
Status face: results/drama_env/st012_voice_finetune.json (in-repo, small)
Receipt:   content/drama/outbox/ST-012-VOICE-FINETUNE-RECEIPT.md
Artifacts: C:\\Fluxgroup\\FluxGroup\\media\\drama-tools\\voice_train\\st012\\ (gitignored)
"""
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time

# --- paths -------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GRP = r'C:\Fluxgroup\FluxGroup'
REPO = os.path.join(GRP, 'media', 'drama-tools', 'GPT-SoVITS')
VPY = os.path.join(REPO, 'runtime', 'Scripts', 'python.exe')
WORK = os.path.join(GRP, 'media', 'drama-tools', 'voice_train', 'st012')
BOOT = os.path.join(WORK, 'bootstrap')
CORPUS = os.path.join(WORK, 'corpus')
EXP_ROOT = os.path.join(WORK, 'exp')
EXP_NAME = 'mancang-v1'
STATUS = os.path.join(ROOT, 'results', 'drama_env', 'st012_voice_finetune.json')
OUTBOX = os.path.join(ROOT, 'content', 'drama', 'outbox')
RECEIPT = os.path.join(OUTBOX, 'ST-012-VOICE-FINETUNE-RECEIPT.md')
VOICE_BANK = os.path.join(ROOT, 'content', 'drama', 'voice_bank', 'manifest.json')
INDEX_VENV_PY = os.path.join(GRP, 'media', 'drama-tools', 'repos', 'index-tts',
                             '.venv', 'Scripts', 'python.exe')
VOICEGEN = r'E:\Fluxgroup\.codely-cli\drama_voicegen.py'
OLD_DRIVER = os.path.join(ROOT, 'content', 'drama', 'runner_assets', 'first_synth_smoke.py')
OLLAMA_DIR = r'C:\Fluxgroup\MiniGame\Tools\Ollama'
PAUSE_FILE = os.path.join(OLLAMA_DIR, 'keepwarm.pause')

# --- canon constants ---------------------------------------------------------
STOCK_VOICES = os.path.join(REPO, '..', 'repos', 'index-tts', 'examples')
IN_SERVICE_BASES = {  # per ST-009/ST-011: never reuse these as a new base
    'voice_04.wav', 'voice_05.wav', 'voice_07.wav', 'voice_12.wav',
}
NEW_BASE = 'voice_09.wav'   # long-form stock clip, unused so far (verify at runtime)
BOOT_EMO = {'MANCANG': 'happy'}  # align with r998 cast notes (comic happy6)

# held-out lines: never inside the training .list (A/B = see if the trained model
# holds the timbre on unseen text; zero-shot baseline synthesizes the same lines)
HOLDOUT = [
    ('holdout_01', '这行情啊，涨的时候我是股神，跌的时候我是股民。'),
    ('holdout_02', '别慌别慌，我满仓呢——满仓的都是命。'),
    ('holdout_03', '你说这砖头值多少钱？反正我家闺女的嫁妆是没了。'),
    # extra utterances keep the corpus above the honest 45s gate (a 1-minute
    # finetune needs real audio; shorter corpora only teach noise)
    ('train_04', '我跟你们讲，这股票啊，就跟媳妇的脸一样，说变就变。'),
    ('train_05', '大户室那帮人天天喝茶看报，喝茶看报，挣的钱比我一年都多？'),
    ('train_06', '哎哟我的亲娘诶，这根绿线怎么又长出来了！'),
    ('train_07', '股神您受累，您受累，这份儿心意您千万收下！'),
    ('train_08', '我这辈子就信一句话——满仓不怕跌，跌了也不卖，卖了就认命。'),
    ('train_09', '大屏幕上的数字跳一下，我的心就跟着跳一下，一上午跳八百回。'),
]
TRAIN_ROWS = [h for h in HOLDOUT if h[0].startswith('train_')]
HOLDOUT_ROWS = [h for h in HOLDOUT if h[0].startswith('holdout_')]

# pretrained pair (v2Pro, present on disk per inventory probe)
G_SSL = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models', 'chinese-hubert-base')
G_BERT = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models', 'chinese-roberta-wwm-ext-large')
G_S2G = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models', 'v2Pro', 's2Gv2Pro.pth')
G_S2D = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models', 'v2Pro', 's2Dv2Pro.pth')
G_S1 = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models',
                    'gsv-v2final-pretrained', 's1bert25hz-5kh-longer-epoch=12-step=369668.ckpt')
G_SV = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models', 'sv',
                    'pretrained_eres2netv2w24s4ep4.ckpt')
S2_CFG = os.path.join(REPO, 'GPT_SoVITS', 'configs', 's2v2Pro.json')
S1_CFG = os.path.join(REPO, 'GPT_SoVITS', 'configs', 's1longer-v2.yaml')

# 8G card: keep batch/epochs modest (webui 8G defaults: s2 batch 4 / 8 epochs;
# s1 batch 8 / 15 epochs). 1-minute corpus -> tiny step counts anyway.
S2_BATCH = 4
S2_EPOCHS = 8
S1_BATCH = 8
S1_EPOCHS = 15

NO_WINDOW = 0x08000000
DETACHED = (0x00000008 | 0x00000200 | 0x08000000)  # DETACHED|NEW_PROCESS_GROUP|NO_WINDOW
TIMEOUT = {'bootstrap': 1800, 'cuda': 2400, 'data': 900, 'prep': 2400,
           's2': 3600, 's1': 3600, 'verify': 1800}
PHASES = ['bootstrap', 'cuda', 'data', 'prep', 's2', 's1', 'verify']


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
    try:
        with io.open(STATUS + '.log', 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def rd_json(p, default=None):
    try:
        with io.open(p, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return default


def _atomic_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def rd_status():
    return rd_json(STATUS, {'schema': 'st012-voice-finetune-v1', 'state': 'init',
                            'phases_done': [], 'errors': []})


def wr_status(patch):
    st = rd_status()
    st.update(patch)
    st['updated_at'] = now_iso()
    st['pid'] = os.getpid()
    _atomic_json(STATUS, st)
    return st


def add_error(phase, err):
    st = rd_status()
    st.setdefault('errors', []).append({'phase': phase, 'ts': now_iso(),
                                        'err': str(err)[:400]})
    st['updated_at'] = now_iso()
    _atomic_json(STATUS, st)


def phase_done(p):
    return p in (rd_status().get('phases_done') or [])


def mark_done(p, extra=None):
    st = rd_status()
    done = st.get('phases_done') or []
    if p not in done:
        done.append(p)
    st['phases_done'] = done
    if extra:
        st.setdefault('evidence', {}).update(extra)
    st['updated_at'] = now_iso()
    _atomic_json(STATUS, st)
    say('PHASE_DONE %s (%d/%d)' % (p, len(done), len(PHASES)))


# --- child runner ------------------------------------------------------------
def relay(cmd, cwd=None, timeout=600, env=None):
    """Run child, relay every line (keepalive + evidence), return (rc, lines)."""
    e = dict(os.environ)
    e.update({'PYTHONPATH': os.pathsep.join([os.path.join(REPO, 'GPT_SoVITS'), REPO]),
              'PYTHONIOENCODING': 'utf-8', 'PYTHONUNBUFFERED': '1'})
    if env:
        e.update(env)
    p = subprocess.Popen(cmd, cwd=cwd or REPO, env=e, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         creationflags=NO_WINDOW)
    lines = []
    deadline = time.time() + timeout
    for raw in p.stdout:
        t = raw.decode('utf-8', 'replace').rstrip()
        say('  | ' + t[:220])
        lines.append(t)
        if time.time() > deadline:
            p.kill()
            p.wait(timeout=30)
            return 124, lines
    rc = p.wait()
    return rc, lines


def ensure_env_repairs():
    """Reuse ST-007's vetted env repairs (jieba_fast shim + torchaudio sf fallback)
    instead of duplicating them -- one repair family, one owner."""
    if not os.path.exists(OLD_DRIVER):
        raise RuntimeError('first_synth_smoke.py (env repairs owner) missing: ' + OLD_DRIVER)
    sys.path.insert(0, os.path.dirname(OLD_DRIVER))
    import first_synth_smoke as fss  # noqa: E402
    s1 = fss.ensure_jieba_fast_shim()
    s2 = fss.ensure_audio_load_fallback()
    say('env repairs: jieba_fast=%s audio_load=%s' % (s1, json.dumps(s2, ensure_ascii=False)))
    return {'jieba_fast': s1, 'audio_load': s2}


# --- source line picking -----------------------------------------------------
SUB_RE = re.compile(r'^([^：:]{1,10})[：:]\s*["“]?(.*?)["”]?\s*$')


def load_manifest():
    return rd_json(os.path.join(GRP, 'media', 'drama-tts-out', 'r998_ep001_003',
                                'MANIFEST-r998.json'), {'lines': []})


def src_lines_for(speaker_filter):
    """r998 manifest lines whose speaker field matches (exact single-speaker only)."""
    out = []
    for ln in load_manifest().get('lines', []):
        sp = (ln.get('speaker') or '').strip()
        if sp != speaker_filter:
            continue
        out.append({'name': ln['name'], 'text': ln['text'], 'ep': ln['ep'],
                    'n': ln['n'], 'file': ln['file'], 'audio_s': ln.get('audio_s')})
    return out


def pick_train_lines():
    """MANCANG training texts = VO-sheet rows (all 3 eps) + extra in-character
    lines. Held-out sentences are disjoint by construction, so A/B stays honest."""
    sheet = rd_json(os.path.join(ROOT, 'content', 'drama', 'voice_sheets',
                                 'EP001-003-VO-SHEET.json'), {'rows': []})
    rows, seen = [], set()
    for r in sheet.get('rows', []):
        if r.get('speaker_role') != 'MANCANG':
            continue
        t = (r.get('text') or '').strip()
        if not t or len(t) < 4 or t in seen:
            continue
        seen.add(t)
        rows.append({'line_id': r['line_id'], 'text': t})
    for name, text in TRAIN_ROWS:
        if text in seen:
            continue
        seen.add(text)
        rows.append({'line_id': name, 'text': text})
    return rows


def pick_holdout_lines():
    return HOLDOUT_ROWS


# --- phases ------------------------------------------------------------------
def ph_bootstrap():
    """New-base voice via IndexTTS-2.5 zero-shot (8G path)."""
    rows = pick_train_lines()
    if len(rows) < 3:
        raise RuntimeError('too few training rows: %d' % len(rows))
    ref = os.path.join(os.path.normpath(STOCK_VOICES), NEW_BASE)
    if not os.path.exists(ref):
        raise RuntimeError('new-base ref missing: ' + ref)
    base_name = os.path.basename(ref)
    if base_name in IN_SERVICE_BASES:
        raise RuntimeError('new base collides with in-service base: ' + base_name)
    os.makedirs(BOOT, exist_ok=True)
    # completeness gate (not just the phase flag): every current row must have audio
    have = {r['line_id'].replace('-', '_').lower() for r in rows
            if os.path.exists(os.path.join(BOOT, r['line_id'].replace('-', '_').lower() + '.wav'))}
    todo = [r for r in rows if r['line_id'].replace('-', '_').lower() not in have]
    if not todo:
        say('bootstrap complete: %d/%d clips present (idempotent)' % (len(have), len(rows)))
        mark_done('bootstrap', {'base_voice': base_name, 'train_rows': len(rows)})
        return
    lines_file = os.path.join(WORK, 'train_lines.txt')
    with io.open(lines_file, 'w', encoding='utf-8') as f:
        for r in todo:
            f.write('%s|%s\n' % (r['line_id'].replace('-', '_').lower(), r['text']))
    say('bootstrap: %d/%d missing + %d held-out planned, base=%s emo=%s' % (
        len(todo), len(rows), len(pick_holdout_lines()), base_name, BOOT_EMO.get('MANCANG')))
    cmd = [INDEX_VENV_PY, '-u', VOICEGEN, '--ref', ref, '--lines', lines_file,
           '--outdir', BOOT, '--lang', 'zhen', '--emo', BOOT_EMO.get('MANCANG', 'happy')]
    rc, lines = relay(cmd, cwd=os.path.dirname(VOICEGEN), timeout=TIMEOUT['bootstrap'])
    ok = [l for l in lines if l.startswith('VOICEGEN_OK')]
    if rc != 0 or len(ok) != len(todo):
        raise RuntimeError('bootstrap rc=%s ok=%d/%d tail=%s' % (
            rc, len(ok), len(todo), lines[-1] if lines else ''))
    mark_done('bootstrap', {'base_voice': base_name, 'train_rows': len(rows)})


def ph_cuda():
    """Swap the venv's CPU torch for the matching CUDA build (8G 3070)."""
    probe = ('import torch;print("CUDA %s dev=%s" % (torch.cuda.is_available(),'
             ' torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-"))')
    r = subprocess.run([VPY, '-c', probe], capture_output=True, timeout=300,
                       creationflags=NO_WINDOW)
    out = (r.stdout or b'').decode('utf-8', 'replace').strip()
    if 'CUDA True' in out:
        say('cuda phase: already on device (%s)' % out)
        mark_done('cuda', {'cuda': out})
        return
    say('cuda phase: installing torch/torchaudio +cu130 (probe said: %s)' % out)
    uv = shutil.which('uv') or os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming',
                                            'Python', 'Scripts', 'uv.exe')
    # mirror first (pytorch.org measured ~50KB/s on this link tonight), then upstream
    bases = ['https://mirrors.aliyun.com/pytorch-wheels/cu130',
             'https://download.pytorch.org/whl/cu130']
    last = ''
    for base in bases:
        cmd = [uv, 'pip', 'install', '--python', VPY,
               'torch==2.14.1+cu130', 'torchaudio==2.11.0+cu130',
               '--find-links', base, '--index-url', base]
        say('cuda phase: trying %s' % base)
        rc, lines = relay(cmd, cwd=WORK, timeout=TIMEOUT['cuda'])
        if rc == 0:
            last = base
            break
        say('cuda phase: %s failed rc=%s' % (base, rc))
    if not last:
        raise RuntimeError('cuda torch install failed on all sources')
    r = subprocess.run([VPY, '-c', probe], capture_output=True, timeout=300,
                       creationflags=NO_WINDOW)
    out = (r.stdout or b'').decode('utf-8', 'replace').strip()
    if 'CUDA True' not in out:
        raise RuntimeError('cuda probe FAIL after install: %s %s' % (
            out, (r.stderr or b'').decode('utf-8', 'replace')[-300:]))
    mark_done('cuda', {'cuda': out, 'source': last})


def ph_data():
    """Corpus: bootstrap clips + known texts -> GPT-SoVITS .list + wav dir."""
    rows = pick_train_lines()
    boot_files = {n: os.path.join(BOOT, n + '.wav') for n in
                  [r['line_id'].replace('-', '_').lower() for r in rows]}
    missing = [n for n, p in boot_files.items() if not os.path.exists(p)]
    if missing:
        raise RuntimeError('bootstrap wavs missing: %s' % missing[:5])
    os.makedirs(CORPUS, exist_ok=True)
    wav_dir = os.path.join(CORPUS, 'wavs')
    os.makedirs(wav_dir, exist_ok=True)
    total_s, list_lines = 0.0, []
    for r in rows:
        stem = r['line_id'].replace('-', '_').lower()
        dst = os.path.join(wav_dir, stem + '.wav')
        if not os.path.exists(dst):
            shutil.copy2(boot_files[stem], dst)
        total_s += float(probe_wav(dst).get('dur') or 0.0)
        list_lines.append('%s|MANCANG|ZH|%s' % (stem + '.wav', r['text']))
    lst = os.path.join(CORPUS, 'train.list')
    with io.open(lst, 'w', encoding='utf-8') as f:
        f.write('\n'.join(list_lines) + '\n')
    say('corpus: %d clips %.1fs -> %s' % (len(list_lines), total_s, lst))
    if total_s < 45.0:
        # honest gate: too little audio makes a finetune meaningless (and noisy)
        raise RuntimeError('corpus too short: %.1fs < 45s' % total_s)
    mark_done('data', {'clips': len(list_lines), 'seconds': round(total_s, 1),
                       'list': lst, 'wav_dir': wav_dir})


def probe_wav(path):
    code = ('import soundfile as sf, json, sys;'
            'i=sf.info(sys.argv[1]);'
            'print(json.dumps({"dur": round(i.duration, 3), "sr": i.samplerate,'
            ' "frames": i.frames}))')
    r = subprocess.run([VPY, '-c', code, path], capture_output=True, timeout=120,
                       creationflags=NO_WINDOW)
    out = (r.stdout or b'').decode('utf-8', 'replace').strip().splitlines()
    try:
        return json.loads(out[-1])
    except Exception:
        return {}


def ph_prep():
    """Dataset prep: text/bert (1) -> cnhubert+wav32k (+sv) (2) -> semantic (3)."""
    ev = rd_status().get('evidence') or {}
    lst = (ev.get('data') or {}).get('list') or os.path.join(CORPUS, 'train.list')
    wav_dir = (ev.get('data') or {}).get('wav_dir') or os.path.join(CORPUS, 'wavs')
    opt_dir = os.path.join(EXP_ROOT, EXP_NAME)
    os.makedirs(opt_dir, exist_ok=True)
    common = {'inp_text': lst, 'inp_wav_dir': wav_dir, 'exp_name': EXP_NAME,
              'opt_dir': opt_dir, 'i_part': '0', 'all_parts': '1',
              '_CUDA_VISIBLE_DEVICES': '0', 'is_half': 'True',
              # clean_text(version=...) picks the phoneme frontend; without it the
              # zh path degrades and 1-get-text silently emits zero rows (observed).
              'version': 'v2Pro'}
    steps = [
        ('1-text', 'GPT_SoVITS/prepare_datasets/1-get-text.py',
         dict(common, bert_pretrained_dir=G_BERT), '2-name2text.txt'),
        ('2-hubert', 'GPT_SoVITS/prepare_datasets/2-get-hubert-wav32k.py',
         dict(common, cnhubert_base_dir=G_SSL, sv_path=G_SV), '4-cnhubert'),
        ('2-sv', 'GPT_SoVITS/prepare_datasets/2-get-sv.py',
         dict(common, cnhubert_base_dir=G_SSL, sv_path=G_SV,
              pretrained_s2G=G_S2G, s2config_path=S2_CFG), None),
        ('3-semantic', 'GPT_SoVITS/prepare_datasets/3-get-semantic.py',
         dict(common, pretrained_s2G=G_S2G, s2config_path=S2_CFG),
         '6-name2semantic.tsv'),
    ]
    done = []
    for tag, script, env, expect in steps:
        if expect and os.path.exists(os.path.join(opt_dir, expect)):
            say('prep %s: already present (%s)' % (tag, expect))
            done.append(tag + ':cached')
            continue
        # prepare_datasets/*.py resolve both their script paths and repo-internal
        # packages (`text`, `feature_extractor`, `ERes2NetV2`) RELATIVE TO CWD, so they
        # must run from the repo root; the GPT_SoVITS/ package root comes in via PYTHONPATH
        # (relay() default). Changing cwd breaks `now_dir/GPT_SoVITS/...` appends.
        rc, lines = relay([VPY, '-u', script], cwd=REPO,
                          timeout=TIMEOUT['prep'], env=env)
        if rc != 0:
            raise RuntimeError('prep %s rc=%s tail=%s' % (tag, rc, lines[-1] if lines else ''))
        done.append(tag)
        say('prep %s ok' % tag)
    # 1-get-text writes numbered shards per worker part; the webui merges them into
    # the canonical 2-name2text.txt and deletes the shards -- replicate that.
    shard = os.path.join(opt_dir, '2-name2text-0.txt')
    merged = os.path.join(opt_dir, '2-name2text.txt')
    if os.path.exists(shard) and not os.path.exists(merged):
        with io.open(shard, 'r', encoding='utf-8') as f:
            body = [l for l in f.read().splitlines() if l.strip()]
        with io.open(merged, 'w', encoding='utf-8') as f:
            f.write('\n'.join(body) + '\n')
        say('prep: merged 2-name2text-0.txt -> 2-name2text.txt (%d rows)' % len(body))
    # 3-get-semantic writes 6-name2semantic-0.tsv; merge with the header row.
    shard_sem = os.path.join(opt_dir, '6-name2semantic-0.tsv')
    merged_sem = os.path.join(opt_dir, '6-name2semantic.tsv')
    if os.path.exists(shard_sem) and not os.path.exists(merged_sem):
        with io.open(shard_sem, 'r', encoding='utf-8') as f:
            body = [l for l in f.read().splitlines() if l.strip()]
        with io.open(merged_sem, 'w', encoding='utf-8') as f:
            f.write('item_name\tsemantic_audio\n' + '\n'.join(body) + '\n')
        say('prep: merged 6-name2semantic-0.tsv -> 6-name2semantic.tsv (%d rows)' % len(body))
    # hard evidence: every line must have produced its features
    n_text, n_sem = 0, 0
    p = os.path.join(opt_dir, '2-name2text.txt')
    if os.path.exists(p):
        n_text = len([l for l in io.open(p, encoding='utf-8').read().splitlines() if l.strip()])
    p = os.path.join(opt_dir, '6-name2semantic.tsv')
    if os.path.exists(p):
        n_sem = max(0, len([l for l in io.open(p, encoding='utf-8').read().splitlines() if l.strip()]) - 1)
    if n_text == 0 or n_sem == 0 or n_text != n_sem:
        raise RuntimeError('prep incomplete: text=%d semantic=%d' % (n_text, n_sem))
    mark_done('prep', {'opt_dir': opt_dir, 'rows_text': n_text, 'rows_semantic': n_sem,
                       'steps': done})


def _pause_ollama(on):
    """Valve: while training, keep the 10-min warm tick from pulling the LLM back
    into VRAM. Restore duty is recorded in the status face + receipt."""
    try:
        if on:
            with io.open(PAUSE_FILE, 'w', encoding='utf-8') as f:
                f.write('ST-012 voice finetune (GPU) %s\n' % now_iso())
            subprocess.run(['schtasks', '/end', '/tn', 'MiniGameOllamaKeepWarm'],
                           capture_output=True, timeout=120, creationflags=NO_WINDOW)
            # drop the resident model so the trainer owns the whole card
            subprocess.run([os.path.join(OLLAMA_DIR, 'ollama.exe'), 'stop', 'qwen3.8:4b'],
                           capture_output=True, timeout=120, creationflags=NO_WINDOW)
            say('ollama valve ON (pause file written, keep-warm ended, 4b stopped)')
        else:
            if os.path.exists(PAUSE_FILE):
                os.remove(PAUSE_FILE)
            say('ollama valve OFF (pause file removed; keep-warm task stays Ready and '
                'restores the model on its next tick)')
    except Exception as e:
        say('ollama valve %s FAILED: %s' % ('ON' if on else 'OFF', e))


def ph_s2():
    """SoVITS (s2) finetune via s2_train.py with the webui's config-derivation logic."""
    ev = rd_status().get('evidence') or {}
    opt_dir = (ev.get('prep') or {}).get('opt_dir') or os.path.join(EXP_ROOT, EXP_NAME)
    ckpt_dir = os.path.join(opt_dir, 'logs_s2_v2Pro')
    # s2_train's final artifact is always the fixed-name G_233333333333.pth
    # (only the *weight copies* under save_weight_dir carry the epoch suffix)
    final_g = os.path.join(ckpt_dir, 'G_233333333333.pth')
    if os.path.exists(final_g):
        say('s2: trained checkpoint already present')
        mark_done('s2', {'ckpt_dir': ckpt_dir, 'ckpt': final_g})
        return
    with io.open(S2_CFG, 'r', encoding='utf-8') as f:
        data = json.load(f)
    os.makedirs(ckpt_dir, exist_ok=True)
    data['train']['batch_size'] = S2_BATCH
    data['train']['epochs'] = S2_EPOCHS
    data['train']['pretrained_s2G'] = G_S2G
    data['train']['pretrained_s2D'] = G_S2D
    data['train']['if_save_latest'] = False
    data['train']['if_save_every_weights'] = True
    data['train']['save_every_epoch'] = 1
    data['train']['gpu_numbers'] = '0'
    data['train']['grad_ckpt'] = True      # 8G headroom
    data['train']['fp16_run'] = True
    data['model']['version'] = 'v2Pro'
    # dataset features live in exp_root/EXP_NAME (parent); only the trainer's
    # checkpoints/tensorboard go to the logs_* subdir (webui: s2_dir vs logs_s2_<version>)
    data['data']['exp_dir'] = opt_dir
    data['s2_ckpt_dir'] = ckpt_dir
    data['save_weight_dir'] = os.path.join(REPO, 'SoVITS_weights_v2Pro')
    data['name'] = EXP_NAME
    data['version'] = 'v2Pro'
    cfg = os.path.join(WORK, 'tmp_s2.json')
    _atomic_json(cfg, data)
    _pause_ollama(True)
    try:
        rc, lines = relay([VPY, '-s', 'GPT_SoVITS/s2_train.py', '--config', cfg],
                          cwd=REPO, timeout=TIMEOUT['s2'])
    finally:
        _pause_ollama(False)
    if rc != 0:
        raise RuntimeError('s2_train rc=%s tail=%s' % (rc, lines[-1] if lines else ''))
    if not os.path.exists(final_g):
        raise RuntimeError('s2_train rc=0 but no final checkpoint at ' + final_g)
    mark_done('s2', {'ckpt_dir': ckpt_dir, 'ckpt': final_g})


def glob_first(pattern):
    import glob
    hits = sorted(glob.glob(pattern))
    return hits[-1] if hits else None


def ph_s1():
    """GPT (s1) finetune via s1_train.py with the s1longer-v2 template."""
    ev = rd_status().get('evidence') or {}
    opt_dir = (ev.get('prep') or {}).get('opt_dir') or os.path.join(EXP_ROOT, EXP_NAME)
    ckpt_dir = os.path.join(opt_dir, 'logs_s1_v2Pro')
    # s1_train saves two kinds of artifacts:
    #   logs_s1_*/ckpt/epoch=N-step=M.ckpt   (lightning resume state)
    #   GPT_weights_<ver>/<exp>-eN.ckpt      (half weights, what inference uses)
    wdir = os.path.join(REPO, 'GPT_weights_v2Pro')
    final = os.path.join(wdir, EXP_NAME + '-e' + str(S1_EPOCHS) + '.ckpt')
    if os.path.exists(final):
        say('s1: trained checkpoint already present')
        mark_done('s1', {'ckpt': final, 'weights_dir': wdir})
        return
    os.makedirs(ckpt_dir, exist_ok=True)
    # yaml lives in the GPT-SoVITS venv only -> write the config with that interpreter
    cfg = os.path.join(WORK, 'tmp_s1.yaml')
    builder = os.path.join(WORK, 'build_s1_cfg.py')
    with io.open(builder, 'w', encoding='utf-8') as f:
        f.write('''import io, os, sys, yaml
src, dst = sys.argv[1], sys.argv[2]
with io.open(src, 'r', encoding='utf-8') as f:
    data = yaml.load(f.read(), Loader=yaml.FullLoader)
data['train']['batch_size'] = %d
data['train']['epochs'] = %d
data['train']['save_every_n_epoch'] = 1
data['train']['if_save_every_weights'] = True
data['train']['if_save_latest'] = True
data['train']['if_dpo'] = False
data['train']['half_weights_save_dir'] = r'%s'
data['train']['exp_name'] = '%s'
data['pretrained_s1'] = r'%s'
data['train_semantic_path'] = r'%s'
data['train_phoneme_path'] = r'%s'
data['output_dir'] = r'%s'
with io.open(dst, 'w', encoding='utf-8') as f:
    f.write(yaml.dump(data, default_flow_style=False))
''' % (S1_BATCH, S1_EPOCHS, os.path.join(REPO, 'GPT_weights_v2Pro'), EXP_NAME, G_S1,
       os.path.join(opt_dir, '6-name2semantic.tsv'),
       os.path.join(opt_dir, '2-name2text.txt'), ckpt_dir))
    rc, lines = relay([VPY, builder, S1_CFG, cfg], cwd=REPO, timeout=180)
    if rc != 0:
        raise RuntimeError('s1 config build rc=%s' % rc)
    env = {'_CUDA_VISIBLE_DEVICES': '0', 'hz': '25hz', 'version': 'v2Pro'}
    _pause_ollama(True)
    try:
        rc, lines = relay([VPY, '-s', 'GPT_SoVITS/s1_train.py', '--config_file', cfg],
                          cwd=REPO, timeout=TIMEOUT['s1'], env=env)
    finally:
        _pause_ollama(False)
    if rc != 0:
        raise RuntimeError('s1_train rc=%s tail=%s' % (rc, lines[-1] if lines else ''))
    if not os.path.exists(final):
        # accept a lower-epoch weight if the configured epoch count is unreachable
        cand = glob_first(os.path.join(wdir, EXP_NAME + '-e*.ckpt'))
        if not cand:
            raise RuntimeError('s1_train rc=0 but no weight ckpt in ' + wdir)
        final = cand
    mark_done('s1', {'ckpt': final, 'weights_dir': wdir})


def ph_verify():
    """A/B: finetuned GPT on held-out lines; keep the wavs + DSP facts for QC."""
    ev = rd_status().get('evidence') or {}
    # resolve from disk, not from stale status keys (keeps verify runnable standalone)
    s1_ckpt = (ev.get('s1') or {}).get('ckpt') or glob_first(
        os.path.join(REPO, 'GPT_weights_v2Pro', EXP_NAME + '-e*.ckpt'))
    s2_ckpt = (ev.get('s2') or {}).get('ckpt') or os.path.join(
        EXP_ROOT, EXP_NAME, 'logs_s2_v2Pro', 'G_233333333333.pth')
    if not (s1_ckpt and os.path.exists(s1_ckpt)):
        raise RuntimeError('verify: s1 weight missing (run phase s1)')
    if not (s2_ckpt and os.path.exists(s2_ckpt)):
        raise RuntimeError('verify: s2 checkpoint missing (run phase s2)')
    # ref clip must be 3-10s for inference_cli (upstream hard gate)
    ref_row, ref_s = None, 0.0
    for r in pick_train_lines():
        p = os.path.join(BOOT, r['line_id'].replace('-', '_').lower() + '.wav')
        f = probe_wav(p) if os.path.exists(p) else {}
        d = float(f.get('dur') or 0)
        if 3.0 <= d <= 10.0:
            ref_row, ref_s = r, d
            break
    if ref_row is None:
        raise RuntimeError('verify: no 3-10s reference clip in bootstrap set')
    ref = os.path.join(BOOT, ref_row['line_id'].replace('-', '_').lower() + '.wav')
    ref_text = ref_row['text']
    say('verify ref: %s (%.2fs) %r' % (os.path.basename(ref), ref_s, ref_text))
    out_dir = os.path.join(WORK, 'ab')
    os.makedirs(out_dir, exist_ok=True)
    # inference_cli takes ref/target TEXT AS FILE PATHS (verified against
    # GPT_SoVITS/inference_cli.py L57/L62)
    ref_txt_path = os.path.join(out_dir, 'ref_text.txt')
    with io.open(ref_txt_path, 'w', encoding='utf-8') as f:
        f.write(ref_text)
    got = []
    for name, text in pick_holdout_lines():
        out = os.path.join(out_dir, name + '_ft.wav')
        if os.path.exists(out):
            got.append(name)
            continue
        tgt_txt_path = os.path.join(out_dir, name + '_target.txt')
        with io.open(tgt_txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        cmd = [VPY, '-s', 'GPT_SoVITS/inference_cli.py',
               '--gpt_model', s1_ckpt, '--sovits_model', s2_ckpt,
               '--ref_audio', ref, '--ref_text', ref_txt_path,
               '--ref_language', '中文', '--target_text', tgt_txt_path,
               '--target_language', '中文', '--output_path', out_dir]
        rc, lines = relay(cmd, cwd=REPO, timeout=TIMEOUT['verify'])
        if rc != 0:
            raise RuntimeError('verify synth %s rc=%s tail=%s' % (
                name, rc, lines[-1] if lines else ''))
        # inference_cli always writes <output_path>/output.wav -> rename per case
        prod = os.path.join(out_dir, 'output.wav')
        if not os.path.exists(prod):
            raise RuntimeError('verify synth %s produced no output.wav' % name)
        if os.path.exists(out):
            os.remove(out)
        shutil.move(prod, out)
        got.append(name)
    facts = {n: probe_wav(os.path.join(out_dir, n + '_ft.wav')) for n in got}
    bad = [n for n, f in facts.items() if not f or f['dur'] < 1.0]
    if bad:
        raise RuntimeError('verify wavs bad: %s' % bad)
    mark_done('verify', {'ab_dir': out_dir, 'facts': facts})


RUN = {'bootstrap': ph_bootstrap, 'cuda': ph_cuda, 'data': ph_data,
       'prep': ph_prep, 's2': ph_s2, 's1': ph_s1, 'verify': ph_verify}


# --- orchestration -----------------------------------------------------------
def do_run():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    os.makedirs(WORK, exist_ok=True)
    if rd_status().get('state') == 'done':
        say('already done (idempotent early exit)')
        return 0
    wr_status({'state': 'running', 'started_at': rd_status().get('started_at') or now_iso()})
    try:
        ensure_env_repairs()
        for ph in PHASES:
            if phase_done(ph):
                continue
            wr_status({'phase': ph, 'phase_state': 'running'})
            say('PHASE_START %s' % ph)
            RUN[ph]()
            wr_status({'phase': ph, 'phase_state': 'done'})
        write_receipt()
        wr_status({'state': 'done', 'phase': 'all', 'phase_state': 'done',
                   'finished_at': now_iso(), 'receipt': os.path.relpath(RECEIPT, ROOT)})
        say('ST012 DONE')
        return 0
    except Exception as e:
        add_error(rd_status().get('phase'), e)
        wr_status({'state': 'failed'})
        say('ST012 FAILED in %s: %s' % (rd_status().get('phase'), e))
        return 1


def write_receipt():
    st = rd_status()
    ev = st.get('evidence') or {}
    md = []
    md.append('# ST-012 角色声微调回执（voice finetune · MANCANG v1）')
    md.append('')
    md.append('> 站点=CONTENT-LOOP ST-012（gpu-night）；承 ST-008/009/011 共底嗓债披露（MANCANG 与旁白同 voice_05 底）；')
    md.append('> 判据合法面=ST-009 负发现（同底微调不可分离族→本线走「新底嗓自举+微调」正路）；')
    md.append('> 时点=%s；车道=GPU 8G（fp16+grad_ckpt·Ollama 阀训练期开）；云端零调用。' % now_iso())
    md.append('')
    md.append('## 链路七相（全部 checkpointed）')
    md.append('')
    md.append('| 相位 | 状态 | 证据 |')
    md.append('|---|---|---|')
    for p in PHASES:
        md.append('| %s | %s | %s |' % (
            p, 'done' if p in (st.get('phases_done') or []) else 'pending',
            json.dumps((ev.get(p) or {}), ensure_ascii=False)[:220]))
    md.append('')
    md.append('## 诚实边界')
    md.append('')
    md.append('- 训练语料=IndexTTS 自举新底嗓合成音（非真人录音）：音色可控但韵味上限受底模；')
    md.append('- A/B 产物未经人耳盲评（QC 站待开）；本站证据=确定性 wav 面（时长/采样率）。')
    md.append('- 试验底嗓=%s（避开 voice_04/05/07/12 现役四底）；胜出入行=ST-009 音色一致检复检+行内 admission。' % (ev.get('bootstrap') or {}).get('base_voice', '?'))
    md.append('- 产物目录（media 区·gitignored）：%s' % WORK)
    md.append('')
    md.append('## 恢复义务')
    md.append('')
    md.append('- Ollama 阀：训练期已写 keepwarm.pause 并按相位开关；收尾已移除（keep-warm 任务 Ready 态自愈恢复）。')
    md.append('- 若中途失败：确认 %s 不存在且 MiniGameOllamaKeepWarm 任务为 Ready。' % PAUSE_FILE)
    with io.open(RECEIPT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')


def do_status():
    st = rd_status()
    print(json.dumps({'state': st.get('state'), 'phase': st.get('phase'),
                      'phases_done': st.get('phases_done'), 'pid': st.get('pid'),
                      'errors': (st.get('errors') or [])[-2:]}, ensure_ascii=False))
    return 0


def selftest():
    a = []
    a.append(('vpy', os.path.exists(VPY)))
    a.append(('stock_base', os.path.exists(os.path.join(os.path.normpath(STOCK_VOICES), NEW_BASE))))
    a.append(('base_not_in_service', NEW_BASE not in IN_SERVICE_BASES))
    a.append(('index_venv', os.path.exists(INDEX_VENV_PY)))
    a.append(('voicegen', os.path.exists(VOICEGEN)))
    a.append(('old_driver', os.path.exists(OLD_DRIVER)))
    a.append(('pretrained_v2pro', all(os.path.exists(p) for p in (G_S2G, G_S2D, G_S1, S2_CFG, S1_CFG))))
    a.append(('hubert_bert', all(os.path.exists(p) for p in (G_SSL, G_BERT, G_SV))))
    rows = pick_train_lines()
    a.append(('train_rows>=10', len(rows) >= 10))
    a.append(('holdout>=3', len(pick_holdout_lines()) >= 3))
    a.append(('status_in_repo', STATUS.startswith(ROOT)))
    rc = 0 if all(ok for _, ok in a) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL',
                      'asserts': dict(a), 'train_rows': len(rows)}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'run':
        sys.exit(do_run())
    elif cmd == 'status':
        sys.exit(do_status())
    elif cmd == 'selftest':
        sys.exit(selftest())
    elif cmd == 'one' and len(sys.argv) > 2:
        ph = sys.argv[2]
        if ph not in RUN:
            print(json.dumps({'verdict': 'usage', 'phases': PHASES}))
            sys.exit(2)
        RUN[ph]()
        sys.exit(0)
    else:
        print(json.dumps({'verdict': 'usage', 'cmds': ['run', 'status', 'selftest',
                                                       'one <phase>'], 'phases': PHASES}))
        sys.exit(2)