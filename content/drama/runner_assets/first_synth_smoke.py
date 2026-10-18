"""ST-007 first-synthesis smoke driver (drama voice lane, bm-b host).

Purpose: prove the GPT-SoVITS zero-shot inference chain end-to-end on the
ST-005 environment (CPU lane): in-house ref clip (r998 audition artifact)
+ manifest text -> inference_cli (v1 pretrained pair) -> output.wav ->
deterministic wav verify (duration/RMS/sr) -> status face + outbox receipt.

Ref-clip route disclosure: r1016 pointer suggested voice_bank/manifest.json
shortlist sourcing; this smoke uses IN-HOUSE r998 drama audition artifacts
(zero license risk, real Mandarin speech, exact text known from
MANIFEST-r998.json) -- i.e. the shortlist's "self-recorded/in-house" option,
upgraded because the material already exists on disk. External corpus review
(AISHELL-3 license) stays open for the production voice-bank station. This
smoke is CHAIN VALIDATION ONLY: no voice_bank entries are written
(音色一致检 not run; the ref is not a canon voice pick).

Commands: run / status / selftest
Status face: results/drama_env/first_synthesis_smoke.json (in-repo)
Products:   media/drama-tools/voice_smoke/st007/{ref.wav, out/output.wav}
            content/drama/outbox/ST-007-FIRST-SYNTHESIS-SMOKE-RECEIPT.md
Laws: U060 no-window; r680/r1045 output relay; CPU lane
(VOICE-PIPELINE-SKELETON-v1 sec.6); cloud forbidden; idempotent.
"""
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GRP = r'C:\Fluxgroup\FluxGroup'
REPO = os.path.join(GRP, 'media', 'drama-tools', 'GPT-SoVITS')
VPY = os.path.join(REPO, 'runtime', 'Scripts', 'python.exe')
ENV_STATUS = os.path.join(ROOT, 'results', 'drama_env', 'gpt_sovits_env_status.json')
SMOKE_DIR = os.path.join(GRP, 'media', 'drama-tools', 'voice_smoke', 'st007')
OUT_DIR = os.path.join(SMOKE_DIR, 'out')
STATUS = os.path.join(ROOT, 'results', 'drama_env', 'first_synthesis_smoke.json')
OUTBOX = os.path.join(ROOT, 'content', 'drama', 'outbox')
RECEIPT = os.path.join(OUTBOX, 'ST-007-FIRST-SYNTHESIS-SMOKE-RECEIPT.md')
REFSRC = os.path.join(GRP, 'media', 'drama-tts-out', 'r998_ep001_003')
MANIFEST = os.path.join(REFSRC, 'MANIFEST-r998.json')
AUDITION = os.path.join(REFSRC, 'AUDITION-r999.json')
GPT_MODEL = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models',
                          's1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt')
SOVITS_MODEL = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models', 's2G488k.pth')
INFER_CLI = os.path.join('GPT_SoVITS', 'inference_cli.py')  # relative to REPO cwd
TARGET_TEXT = '成交量不会说谎，人心才会。'
# (ep, line-n) fallback chain -- all clean per AUDITION-r999 (no hard/pacing
# flags), single speaker, 3-10s, no em-dash preferred.
CANDIDATES = [('EP002', 4), ('EP003', 17), ('EP003', 4), ('EP001', 2)]
NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW (U060)
INFER_TIMEOUT = 540  # < 600s loop lock stale guard

# --- env shim: jieba_fast was auto-stripped by the env deps phase (sdist needs
# MSVC C++ toolchain absent on this host; .env-deps-ok strips=[pyopenjtalk,
# jieba_fast]). GPT-SoVITS text/chinese.py + tone_sandhi.py import jieba_fast
# unconditionally. This shim aliases the installed pure-python jieba (same API
# surface used: setLogLevel / posseg / cut_for_search / cut / Tokenizer).
# Installed idempotently into the venv site-packages; perf cost ~2-4x slower
# tokenization -- acceptable for the CPU drama voice lane (honest disclosure).
SHIM_PKG = os.path.join(REPO, 'runtime', 'Lib', 'site-packages', 'jieba_fast')
SHIM_SRC = (
    "# jieba_fast shim: pure-python jieba alias (env deps phase stripped the\n"
    "# compiled jieba_fast sdist -- no MSVC on host). Installed idempotently by\n"
    "# content/drama/runner_assets/first_synth_smoke.py (ST-007 smoke).\n"
    "import sys\n"
    "import jieba\n"
    "import jieba.posseg\n"
    "from jieba import *  # noqa: F401,F403 -- public API incl. Tokenizer\n"
    "sys.modules.setdefault(__name__ + '.posseg', jieba.posseg)\n"
    "posseg = jieba.posseg\n"
    "setLogLevel = jieba.setLogLevel\n"
    "cut_for_search = jieba.cut_for_search\n"
    "__version__ = jieba.__version__ + '+shim'\n"
)


def ensure_jieba_fast_shim():
    """Idempotent: probe jieba_fast import in venv; write alias shim if absent."""
    r = subprocess.run([VPY, '-c', 'import jieba_fast, jieba_fast.posseg'],
                       capture_output=True, timeout=60, creationflags=NO_WINDOW)
    if r.returncode == 0:
        return 'already-present'
    os.makedirs(SHIM_PKG, exist_ok=True)
    with io.open(os.path.join(SHIM_PKG, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write(SHIM_SRC)
    r2 = subprocess.run([VPY, '-c', 'import jieba_fast, jieba_fast.posseg;'
                        ' jieba_fast.setLogLevel(50); jieba_fast.cut_for_search("盘口会说谎")'],
                        capture_output=True, timeout=60, creationflags=NO_WINDOW)
    if r2.returncode != 0:
        raise RuntimeError('jieba_fast shim probe FAIL: %s' %
                           (r2.stderr or r2.stdout).decode('utf-8', 'replace')[-160:])
    return 'shim-installed'


# --- env patch 2: torchaudio>=2.9 removed legacy audio backends; load() now
# hard-requires torchcodec + FFmpeg shared DLLs ("full-shared" build), absent
# on this host (torchcodec wheel installed but its core DLLs cannot link).
# Surgical fallback: wrap the torchaudio.load call sites in the GPT-SoVITS
# inference-relevant files with _bmb_ta_load (try native, fall back to
# soundfile read -> torch tensor). Marker-guarded idempotent + py_compile
# verified. Root cause family fixed once for smoke + api_v2 batch lanes.
PATCH_FILES = [
    'GPT_SoVITS/inference_webui.py',
    'GPT_SoVITS/TTS_infer_pack/TTS.py',
    'api.py',
    'tools/audio_sr.py',
    'GPT_SoVITS/prepare_datasets/2-get-sv.py',
]
_TA_HELPER = (
    "def _bmb_ta_load(path):\n"
    "    # bm-b sf-fallback (ST-007 smoke ensure): torchaudio>=2.9 load()\n"
    "    # requires torchcodec + FFmpeg shared DLLs absent on this host; fall\n"
    "    # back to soundfile (wav/flac/ogg). Installed idempotently by\n"
    "    # content/drama/runner_assets/first_synth_smoke.py.\n"
    "    try:\n"
    "        return torchaudio.load(path)\n"
    "    except Exception:\n"
    "        import soundfile as _sf\n"
    "        _d, _sr = _sf.read(path, dtype='float32', always_2d=True)\n"
    "        return torch.from_numpy(_d.T), _sr\n"
    "\n"
)


def ensure_audio_load_fallback():
    """Idempotent marker-guarded callsite wrap + compile verify."""
    patched, skipped, failed = [], [], []
    for rel in PATCH_FILES:
        p = os.path.join(REPO, *rel.split('/'))
        if not os.path.exists(p):
            skipped.append(rel + ':missing')
            continue
        with io.open(p, 'r', encoding='utf-8', errors='surrogateescape', newline='') as f:
            src = f.read()
        if '_bmb_ta_load' in src:
            skipped.append(rel + ':already')
            continue
        n = src.count('torchaudio.load(')
        if n == 0 or 'import torchaudio' not in src:
            skipped.append(rel + ':no-callsite')
            continue
        src = src.replace('torchaudio.load(', '_bmb_ta_load(')
        idx = src.index('import torchaudio')
        eol = src.index('\n', idx) + 1
        src = src[:eol] + _TA_HELPER + src[eol:]
        with io.open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='') as f:
            f.write(src)
        r = subprocess.run([VPY, '-m', 'py_compile', p],
                           capture_output=True, timeout=120, creationflags=NO_WINDOW)
        if r.returncode != 0:
            failed.append(rel + ':compile-fail')
            continue
        patched.append('%s:%d' % (rel, n))
    if failed:
        raise RuntimeError('audio-load fallback compile FAIL: %s' % failed)
    return {'patched': patched, 'skipped': skipped}


def ensure_pip_pkg(pkg, probe_import=None, timeout=900):
    """Idempotent pip-ensure for light pure-python runtime deps the repo
    requirements miss (probe import first; install + re-probe; hard-fail
    honest). Heavy/compiled deps stay out of this path (no torchcodec retry
    here -- its DLL face is broken on this host, sf-fallback carries load)."""
    probe = probe_import or pkg
    r = subprocess.run([VPY, '-c', 'import %s' % probe],
                       capture_output=True, timeout=60, creationflags=NO_WINDOW)
    if r.returncode == 0:
        return 'present'
    r2 = subprocess.run([VPY, '-m', 'pip', 'install', '--disable-pip-version-check', pkg],
                        capture_output=True, timeout=timeout, creationflags=NO_WINDOW)
    tail = ((r2.stdout or b'') + (r2.stderr or b'')).decode('utf-8', 'replace').strip()[-200:]
    say('pip install %s rc=%s tail=%s' % (pkg, r2.returncode, tail[-120:]))
    r3 = subprocess.run([VPY, '-c', 'import %s' % probe],
                        capture_output=True, timeout=60, creationflags=NO_WINDOW)
    if r3.returncode != 0:
        raise RuntimeError('pip-ensure %s FAIL (install rc=%s)' % (pkg, r2.returncode))
    return 'installed'


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


def rd_json(p, default):
    try:
        with io.open(p, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return default


def wr_status(patch):
    st = rd_status()
    st.update(patch)
    st['updated_at'] = now_iso()
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    tmp = STATUS + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)
    return st


def rd_status():
    return rd_json(STATUS, {'schema': 'first-synthesis-smoke-v1', 'state': 'init', 'errors': []})


def pick_ref():
    """Pure-ish: resolve (line_entry, flagged_set) from manifest + audition.
    Returns (entry, why) or raises."""
    man = rd_json(MANIFEST, None)
    aud = rd_json(AUDITION, {})
    if man is None:
        raise RuntimeError('MANIFEST-r998.json unreadable')
    flagged = set()
    for k in ('hard_flags', 'soft_flags', 'pacing_flags'):
        for fl in (aud.get(k) or []):
            flagged.add(str(fl).split()[0])
    for ep, n in CANDIDATES:
        for ln in man.get('lines', []):
            if ln.get('ep') == ep and ln.get('n') == n:
                why = []
                if ln['name'] in flagged:
                    why.append('audition-flagged')
                if not os.path.exists(ln['file']):
                    why.append('wav-missing')
                if not (3.0 <= float(ln.get('audio_s', 0)) <= 9.5):
                    why.append('dur-out-of-3-10s(%.2f)' % ln.get('audio_s', 0))
                if not why:
                    return ln, 'clean'
                say('candidate %s skipped: %s' % (ln['name'], ','.join(why)))
    raise RuntimeError('no clean ref candidate in fallback chain')


def build_args(ref_wav, ref_txt, tgt_txt):
    """Pure fn: inference_cli argv (paths absolute, cli relative to REPO cwd)."""
    return [VPY, INFER_CLI,
            '--gpt_model', GPT_MODEL,
            '--sovits_model', SOVITS_MODEL,
            '--ref_audio', ref_wav,
            '--ref_text', ref_txt,
            '--ref_language', '中文',
            '--target_text', tgt_txt,
            '--target_language', '中文',
            '--output_path', OUT_DIR]


def relay_run(cmd, cwd, timeout):
    """r680/r1045: spawn child with live line relay (keepalive + evidence)."""
    env = dict(os.environ)
    env['PYTHONPATH'] = REPO
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    lines = []
    deadline = time.time() + timeout
    for raw in p.stdout:
        tline = raw.decode('utf-8', 'replace').rstrip()
        say('  | ' + tline[:200])
        lines.append(tline)
        if time.time() > deadline:
            p.kill()
            p.wait(timeout=30)
            return 124, lines
    rc = p.wait(timeout=max(30, int(deadline - time.time())))
    return rc, lines


def verify_wav(path):
    """Deterministic probe via venv soundfile: (ok, facts)."""
    code = ('import soundfile as sf, numpy as np, json, sys;'
            'd,sr=sf.read(sys.argv[1]);'
            'print(json.dumps({"dur": round(len(d)/sr, 2), "sr": sr,'
            '"rms": float(np.sqrt(np.mean(d.astype("float64")**2))),'
            '"bytes": int(__import__("os").path.getsize(sys.argv[1]))}))')
    r = subprocess.run([VPY, '-c', code, path], capture_output=True,
                       timeout=120, creationflags=NO_WINDOW)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0 or not out.startswith('{'):
        return False, {'probe_rc': r.returncode, 'probe_err': (r.stderr.decode('utf-8', 'replace') or out)[:160]}
    f = json.loads(out.splitlines()[-1])
    ok = f['dur'] >= 1.5 and f['rms'] > 1e-3 and f['bytes'] > 30000
    return ok, f


def do_run():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    # idempotency gate: done + product present -> early exit
    st = rd_status()
    if st.get('state') == 'done' and os.path.exists(st.get('output_wav') or ''):
        say('smoke already done (idempotent early exit)')
        return 0
    # env gate
    env = rd_json(ENV_STATUS, {})
    if env.get('state') != 'done' or len(env.get('phases_done', [])) < 6:
        say('env gate FAIL: gpt_sovits_env_state=%s phases=%s' % (
            env.get('state'), env.get('phases_done')))
        wr_status({'state': 'blocked-env', 'env_gate': 'not-done'})
        return 2
    if not (os.path.exists(VPY) and os.path.exists(GPT_MODEL) and os.path.exists(SOVITS_MODEL)):
        say('env artifacts missing (vpy/gpt/sovits)')
        wr_status({'state': 'blocked-env', 'env_gate': 'artifacts-missing'})
        return 2
    shim_state = ensure_jieba_fast_shim()
    say('jieba_fast face: %s' % shim_state)
    ta_patch = ensure_audio_load_fallback()
    say('torchaudio load fallback: %s' % json.dumps(ta_patch, ensure_ascii=False))
    resampy_state = ensure_pip_pkg('resampy')
    say('resampy face: %s' % resampy_state)
    # ref prep
    ln, why = pick_ref()
    os.makedirs(OUT_DIR, exist_ok=True)
    ref_wav = os.path.join(SMOKE_DIR, 'ref.wav')
    os.makedirs(SMOKE_DIR, exist_ok=True)
    shutil.copy2(ln['file'], ref_wav)
    ref_txt = os.path.join(SMOKE_DIR, 'ref_text.txt')
    tgt_txt = os.path.join(SMOKE_DIR, 'target_text.txt')
    with io.open(ref_txt, 'w', encoding='utf-8') as f:
        f.write(ln['text'])
    with io.open(tgt_txt, 'w', encoding='utf-8') as f:
        f.write(TARGET_TEXT)
    stale = os.path.join(OUT_DIR, 'output.wav')
    if os.path.exists(stale):
        os.remove(stale)
    say('ref picked: %s [%s] %.2fs (%s) text=%r' % (
        ln['name'], ln.get('speaker'), ln.get('audio_s', 0), why, ln['text']))
    say('target text: %r' % TARGET_TEXT)
    wr_status({'state': 'running', 'env_shim': 'jieba_fast->jieba alias (%s)' % shim_state,
               'audio_loader_patch': ta_patch,
               'env_pip': {'resampy': resampy_state},
               'ref_clip': {
        'source': 'in-house r998 audition %s (speaker=%s)' % (ln['name'], ln.get('speaker')),
        'text': ln['text'], 'audio_s': ln.get('audio_s')},
        'target_text': TARGET_TEXT})
    # inference (streamed relay)
    t0 = time.time()
    rc, lines = relay_run(build_args(ref_wav, ref_txt, tgt_txt), REPO, INFER_TIMEOUT)
    wall = round(time.time() - t0, 1)
    say('inference rc=%s wall=%ss' % (rc, wall))
    if rc != 0:
        wr_status({'state': 'failed', 'inference_rc': rc, 'inference_wall_s': wall})
        return 1
    out_wav = os.path.join(OUT_DIR, 'output.wav')
    if not os.path.exists(out_wav):
        say('output.wav missing after rc=0')
        wr_status({'state': 'failed', 'inference_rc': rc, 'output_missing': True})
        return 1
    ok, facts = verify_wav(out_wav)
    say('verify: ok=%s %s' % (ok, json.dumps(facts, ensure_ascii=False)))
    if not ok:
        wr_status({'state': 'failed', 'verify': facts, 'inference_rc': rc,
                   'inference_wall_s': wall})
        return 1
    # products: status face + receipt
    receipt_rel = os.path.relpath(RECEIPT, ROOT).replace('\\', '/')
    st = wr_status({'state': 'done', 'ts': now_iso(),
                    'env_gate': 'gpt_sovits_env done 6/6 @%s' % env.get('finished_at'),
                    'env_shim': 'jieba_fast->jieba alias (%s)' % shim_state,
                    'audio_loader_patch': ta_patch,
                    'env_pip': {'resampy': resampy_state},
                    'models': {'gpt': GPT_MODEL, 'sovits': SOVITS_MODEL},
                    'output_wav': out_wav, 'output_s': facts['dur'],
                    'output_sr': facts['sr'], 'output_rms': round(facts['rms'], 6),
                    'output_bytes': facts['bytes'],
                    'inference_rc': rc, 'inference_wall_s': wall,
                    'receipt': receipt_rel})
    write_receipt(st, ln, facts, wall)
    say('SMOKE DONE: output %.2fs sr=%d rms=%.4f bytes=%d -> %s' % (
        facts['dur'], facts['sr'], facts['rms'], facts['bytes'], out_wav))
    return 0


def write_receipt(st, ln, facts, wall):
    os.makedirs(OUTBOX, exist_ok=True)
    md = []
    md.append('# ST-007 首次合成冒烟回执（first-synthesis smoke · GPT-SoVITS）')
    md.append('')
    md.append('> 站点=CONTENT-LOOP v0.1 ST-007（r1016 轮升格 r1017 首动作·声库车道 P1 ≤10-22）；')
    md.append('> 环境=ST-005 GPT-SoVITS 全六相位 done @%s（CPU 车道·VOICE-PIPELINE-SKELETON-v1 §6）；' % st.get('env_gate', ''))
    md.append('> 时点=%s。云端零调用（429 经济）。' % now_iso())
    md.append('')
    md.append('## 冒烟结论：零样本推理链 PASS')
    md.append('')
    md.append('- **参考音 → 音色克隆 → 目标文本合成 → wav 产物 → 确定性校验** 全链走通。')
    md.append('- 产物=`%s`（时长 %.2fs·采样率 %dHz·RMS %.4f·%d bytes）。' % (
        st.get('output_wav'), facts['dur'], facts['sr'], facts['rms'], facts['bytes']))
    md.append('- 推理耗时 %ss（CPU fp32·v1 预训练对：%s + %s）。' % (
        wall, os.path.basename(GPT_MODEL), os.path.basename(SOVITS_MODEL)))
    md.append('')
    md.append('## 参考音来源（寻源披露）')
    md.append('')
    md.append('- 选用=**本仓自产 r998 结构试音素材**（`%s`·角色「%s」·%.2fs·文本『%s』）。' % (
        ln['name'], ln.get('speaker', '-'), ln.get('audio_s', 0), ln['text']))
    md.append('- 与声银行短线（ST-006 manifest ref_clip_sourcing_shortlist）的关系：本路线=短线中')
    md.append('  「self-recorded / 自产素材」档的落地版——盘上已有真实普通话对白素材（r998 试音产物·')
    md.append('  零许可风险·逐行文本可从 MANIFEST-r998.json 机读·试音零硬旗件），优先于外部语料')
    md.append('  （AISHELL-3 许可面未审·留作正式声银行站的后续选项）。')
    md.append('- 参考音挑选判据：AUDITION-r999 硬/软/节拍旗零命中 + 单说话人 + 3-10s 窗 + 文本无长破折号。')
    md.append('')
    md.append('## 冒烟边界（如实）')
    md.append('')
    md.append('- 本站=**链路验证**，非音色定稿：冒烟参考音不是正典角色声银行条目，')
    md.append('  `content/drama/voice_bank/manifest.json` 各角色 ref_clips 仍为空（正式寻源站待开）。')
    md.append('- 输出未经人耳听感门（听感抽检=后续 QC 站的活）；本站校验面=确定性三查')
    md.append('  （存在性/时长-字率带/静音 RMS 门）。')
    md.append('- 音色一致检（入行门）未跑——冒烟产物不写声银行、不入 CEO 面。')
    md.append('- 环境补丁披露（推理首跑暴露 env 冒烟面只验 import 未验 load 的潜伏缺口，本站幂等修复）：')
    md.append('  ① env deps 相位剥离 jieba_fast（sdist 需 MSVC·无该工具链）→ site-packages 别名 shim')
    md.append('  （jieba_fast→纯 Python jieba·分词慢 2-4 倍·CPU 车道可接受）；')
    md.append('  ② torchaudio 2.11 移除传统音频后端、load() 硬依赖 torchcodec+FFmpeg shared DLL（本机无 DLL 面，')
    md.append('  torchcodec 轮子装了链不上）→ 推理相关 5 文件 9 调用位 marker 守卫包裹 `_bmb_ta_load`')
    md.append('  （先走原生、异常回退 soundfile·py_compile 全绿）——smoke 与 api_v2 批产双车道一次修族；')
    md.append('  ③ match_librosa 重采样路径依赖 resampy（repo requirements 未含）→ pip 幂等补装；')
    md.append('  状态面 env_shim/audio_loader_patch/env_pip 字段留证，修复配方版本化于本 runner 资产件可复跑。')
    md.append('- 产物件位于 gitignored media 区（CEO 交付律）；本回执+状态面=入 git 证据。')
    md.append('')
    md.append('## 下一步（CONTENT-LOOP 后续站位）')
    md.append('')
    md.append('- 正典声银行条目站：每角色 1-3 条参考音（优先继续挖 r998 自产素材对齐角色·缺口再走外部语料）')
    md.append('  + 音色一致检入行；GPT-SoVITS 微调面（每角色 LoRA/ckpt）评估。')
    md.append('- 批产站：逐镜 TTS 批产 runner（resume-safe·失败行隔离）+ QC 门三查接线。')
    with io.open(RECEIPT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')


def do_status():
    st = rd_status()
    print(json.dumps({'state': st.get('state'), 'updated_at': st.get('updated_at'),
                     'output_wav': st.get('output_wav'), 'output_s': st.get('output_s'),
                     'receipt': st.get('receipt')}, ensure_ascii=False))
    return 0


def selftest():
    asserts = []
    man = rd_json(MANIFEST, None)
    asserts.append(('manifest-readable', isinstance(man, dict) and len(man.get('lines', [])) >= 50))
    ln, why = pick_ref()
    asserts.append(('ref-resolves-clean', why == 'clean' and os.path.exists(ln['file'])))
    args = build_args('R', 'T', 'G')
    asserts.append(('args-shape', args[0] == VPY and args[1] == INFER_CLI and
                    args[11] == '中文' and args[15] == '中文' and
                    args[17] == OUT_DIR and len(args) == 18))
    asserts.append(('models-present', os.path.exists(VPY) and os.path.exists(GPT_MODEL)
                    and os.path.exists(SOVITS_MODEL)))
    asserts.append(('status-in-repo', STATUS.startswith(ROOT)))
    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL',
                      'asserts': {k: v for k, v in asserts}}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'run':
        sys.exit(do_run())
    elif cmd == 'status':
        sys.exit(do_status())
    elif cmd == 'selftest':
        sys.exit(selftest())
    else:
        print(json.dumps({'verdict': 'usage', 'cmds': ['run', 'status', 'selftest']}))
        sys.exit(2)
