# -*- coding: utf-8 -*-
"""N1 freeze-face adjudicator (r1188 bm-c).

Why this exists: a per-wave freeze receipt records the *_pre-commit* face it wrote
(under core.autocrlf=true that face is CRLF on disk), while the landed blob in git is
LF-normalized.  A post-commit gate that compares the worktree/landed bytes straight
against `n1_sha16_post` therefore fails on EOL alone (W304 first live-fire, r1188).

This tool reproduces the freeze face mechanically instead of trusting either side:
  1. clone the repo (--shared, no worktree cost) at the receipt's origin_base,
  2. pin refs/remotes/origin/main to that base so the editor's freshness assert holds,
  3. run the wave's freeze editor inside the clone (must reproduce pre AND post faces),
  4. diff the reproduced post face (LF-normalized) against the landed blob and classify
     every delta, allowing ONLY the documented in-window heal pattern
     ("freeze-time commit n/a" -> "freeze-time commit <sha>"),
  5. emit an evidence JSON the six-gate can consume.

Verdict PASS means: landed content == freeze content modulo EOL normalization plus the
declared heal lines; no silent content drift.

Usage:
  python Tools/n1_freeze_face_adjudicate.py --wave 304 \
      --editor results/_w304bmc_freeze_edits.py \
      --receipt results/_w304bmc_freeze_receipt.json \
      --probe-receipt results/_w304bmc_20261024_probe_receipt.json \
      --prereg research/PERPETUAL_N1_W304_PREREG.md \
      --splice <splice-commit> --out results/_r1188bmc_w304_face_adjudication.json
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lines the freeze editor could not know at write time: it stamps the prereg commit
# sha into the n1 registry AFTER the prereg lands (documented as "prereg_commit_heal"
# in the receipt).  Byte-for-byte the only admissible replay-vs-landed delta.
HEAL_RULES = [
    # (old_re, new_re, needs_parity_count)
    (re.compile(r'^(\s*"[^"]*?)freeze-time commit n/a( @ probe receipt [0-9a-f]+;[^"]*")$'),
     re.compile(r'^(\s*"[^"]*?)freeze-time commit [0-9a-f]{7,40}( @ probe receipt [0-9a-f]+;[^"]*")$'),
     False),
    # r1189: the same stamp also appears in prose comments as "freeze-time gate n/a".
    (re.compile(r'^(.*?)freeze-time gate n/a(;.*)$'),
     re.compile(r'^(.*?)freeze-time gate [0-9a-f]{7,40}(;.*)$'),
     False),
    # r1189: a comment-only parity-count correction is admissible ONLY against the
    # receipt's own machine-recorded count (receipt parity.total_parity_rows) -- the
    # decision never trusts the landed text on its own.
    (re.compile(r'^(\s*#\s+registry at freeze time -> )(\d+)( parity rows\.)$'),
     re.compile(r'^(\s*#\s+registry at freeze time -> )(\d+)( parity rows\.)$'),
     True),
]

STAMP_RE = re.compile(rb'freeze-time (?:commit|gate) n/a')


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd or REPO, capture_output=True)


def blob(commit, path):
    r = git('show', f'{commit}:{path}')
    if r.returncode != 0:
        raise SystemExit(f'git show {commit}:{path} failed: {r.stderr[:400]!r}')
    return r.stdout


def heal_pair_ok(old, new, parity_count=None):
    """True when old/new are the same line apart from the documented heal."""
    for old_re, new_re, needs_parity in HEAL_RULES:
        mo, mn = old_re.match(old), new_re.match(new)
        if not (mo and mn):
            continue
        if needs_parity:
            # prefix+suffix must match and the landed number must equal the
            # receipt's own machine-recorded count
            if mo.group(1) != mn.group(1) or mo.group(3) != mn.group(3):
                continue
            if parity_count is None or int(mn.group(2)) != int(parity_count):
                continue
            return True
        if mo.group(1) == mn.group(1) and mo.group(2) == mn.group(2):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--wave', type=int, required=True)
    ap.add_argument('--editor', required=True)
    ap.add_argument('--receipt', required=True)
    ap.add_argument('--probe-receipt', required=True)
    ap.add_argument('--prereg', required=True)
    ap.add_argument('--splice', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--materialize', nargs='*', default=[],
                    help=('repo-relative inputs the replay editor asserts on but which '
                          'postdate origin_base (e.g. a seat MSG committed after the freeze '
                          'captured its base); copied from the worktree and hashed into the '
                          'evidence (r1192 bm-c W307 first live-fire)'))
    a = ap.parse_args()

    wave, splice = a.wave, a.splice
    rec = json.load(io.open(os.path.join(REPO, a.receipt), encoding='utf-8'))
    base = rec['origin_base']

    landed_n1 = blob(splice, 'scripts/perpetual_faces_n1.py')
    landed_pf = blob(splice, 'scripts/perpetual_faces.py')
    editor_src = blob(splice, a.editor)
    probe_src = blob(splice, a.probe_receipt)
    prereg_src = io.open(os.path.join(REPO, a.prereg), 'rb').read()

    tmp = tempfile.mkdtemp(prefix=f'n1w{wave}face_')
    ev = {'wave': wave, 'splice': splice, 'origin_base': base, 'tmp': tmp,
          'landed_n1_sha16': sha16(landed_n1), 'landed_pf_sha16': sha16(landed_pf),
          'receipt_n1_sha16_post': rec['n1_sha16_post'],
          'receipt_n1_sha16_pre': rec['n1_sha16_pre'],
          'receipt_pf_sha16_post': rec['pf_sha16_post'],
          'receipt_pf_sha16_pre': rec['pf_sha16_pre'],
          'prereg_sha16': sha16(prereg_src)}
    try:
        clone = os.path.join(tmp, 'r')
        c = git('clone', '--shared', '--no-checkout', REPO, clone)
        if c.returncode != 0:
            raise SystemExit(f'clone failed: {c.stderr[:400]!r}')
        git('config', 'core.autocrlf', 'true', cwd=clone)
        git('checkout', '--detach', base, cwd=clone)
        # pin the freshness face: the editor asserts origin/main is an ancestor of HEAD
        git('remote', 'remove', 'origin', cwd=clone)
        git('update-ref', 'refs/remotes/origin/main', base, cwd=clone)

        def put(rel, data):
            p = os.path.join(clone, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            io.open(p, 'wb').write(data)
            return p

        n1_pre = io.open(os.path.join(clone, 'scripts/perpetual_faces_n1.py'), 'rb').read()
        pf_pre = io.open(os.path.join(clone, 'scripts/perpetual_faces.py'), 'rb').read()

        # r1236 bm-c: the receipt DECLARES its own EOL basis (`eol.n1_crlf` / `eol.pf_crlf`,
        # r838 law). The replay clone is always checked out under core.autocrlf=true, i.e.
        # its raw bytes are CRLF even when the freeze window ran on an LF worktree, so a raw
        # comparison silently compares two different bases (W327 first live-fire: receipt
        # faces LF, replay faces CRLF, content identical). Compare on the DECLARED basis,
        # record which basis was used, and keep the hash the judge (nothing is smoothed:
        # the chosen candidate must still match the receipt face byte-exactly).
        def _lf(b):
            return b.replace(b'\r\n', b'\n')

        def declared_is_crlf(key):
            e = rec.get('eol') or {}
            v = e.get(key)
            return True if v is None else bool(v)

        def on_basis(b, want_crlf):
            return b if want_crlf else _lf(b)

        n1_pre_cmp = on_basis(n1_pre, declared_is_crlf('n1_crlf'))
        pf_pre_cmp = on_basis(pf_pre, declared_is_crlf('pf_crlf'))
        ev['pre_match_basis'] = {'n1': 'crlf' if declared_is_crlf('n1_crlf') else 'lf',
                                 'pf': 'crlf' if declared_is_crlf('pf_crlf') else 'lf',
                                 'source': 'receipt eol flags (r838 law), never assumed'}
        ev['replay_n1_sha16_pre'] = sha16(n1_pre_cmp)
        ev['replay_pf_sha16_pre'] = sha16(pf_pre_cmp)
        ev['replay_n1_sha16_pre_raw'] = sha16(n1_pre)
        ev['replay_pf_sha16_pre_raw'] = sha16(pf_pre)
        ev['pre_faces_match_receipt'] = (ev['replay_n1_sha16_pre'] == rec['n1_sha16_pre']
                                         and ev['replay_pf_sha16_pre'] == rec['pf_sha16_pre'])

        put(a.editor, editor_src)
        put(a.probe_receipt, probe_src)
        put(a.prereg, prereg_src)
        if a.materialize:
            mat = {}
            for rel in a.materialize:
                data = io.open(os.path.join(REPO, rel), 'rb').read()
                put(rel, data)
                mat[rel] = sha16(data)
            ev['materialized_inputs'] = mat
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        r = subprocess.run([sys.executable, os.path.join(clone, a.editor)],
                           cwd=clone, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', env=env)
        ev['editor_rc'] = r.returncode
        ev['editor_stdout_tail'] = (r.stdout or '').strip().splitlines()[-3:]
        ev['editor_stderr_tail'] = (r.stderr or '').strip().splitlines()[-3:]
        if r.returncode != 0:
            raise SystemExit('freeze editor replay failed (see evidence)')

        rep_n1 = io.open(os.path.join(clone, 'scripts/perpetual_faces_n1.py'), 'rb').read()
        rep_pf = io.open(os.path.join(clone, 'scripts/perpetual_faces.py'), 'rb').read()
        # r1236: replay post faces are compared on the receipt's DECLARED EOL basis too
        # (same law as the pre faces above); raw faces kept in the evidence for audit.
        ev['post_match_basis'] = {'n1': 'crlf' if declared_is_crlf('n1_crlf') else 'lf',
                                  'pf': 'crlf' if declared_is_crlf('pf_crlf') else 'lf',
                                  'source': 'receipt eol flags (r838 law), never assumed'}
        ev['replay_n1_sha16_post_raw'] = sha16(rep_n1)
        ev['replay_pf_sha16_post_raw'] = sha16(rep_pf)
        rep_n1 = on_basis(rep_n1, declared_is_crlf('n1_crlf'))
        rep_pf = on_basis(rep_pf, declared_is_crlf('pf_crlf'))
        rep_n1_raw, rep_pf_raw = rep_n1, rep_pf
        ev['replay_n1_sha16_post'] = sha16(rep_n1)
        ev['replay_pf_sha16_post'] = sha16(rep_pf)
        ev['post_faces_match_receipt'] = (ev['replay_n1_sha16_post'] == rec['n1_sha16_post']
                                          and ev['replay_pf_sha16_post'] == rec['pf_sha16_post'])
        def stamp_candidates(b, sha10):
            """Yield (index, candidate) with exactly ONE n/a stamp replaced: the receipt
            face records the stamp only for its own wave block; blanket replacement would
            also stamp older blocks (r1189 W305 live-fire)."""
            needle = b'freeze-time commit n/a'
            gate = b'freeze-time gate n/a'
            hits = [(m.start(), needle, b'freeze-time commit ' + sha10.encode())
                    for m in re.finditer(re.escape(needle), b)]
            hits += [(m.start(), gate, b'freeze-time gate ' + sha10.encode())
                     for m in re.finditer(re.escape(gate), b)]
            for i, (pos, old, new) in enumerate(sorted(hits)):
                yield i, b[:pos] + new + b[pos + len(old):]

        def stamped_match(b, target_sha16, sha10):
            for i, cand in stamp_candidates(b, sha10):
                if sha16(cand) == target_sha16:
                    return i, sha16(cand)
            return None, None

        ev['post_match_mode'] = 'direct'
        if not ev['post_faces_match_receipt']:
            # r1189: the receipt may record a post face that already carries the prereg
            # commit stamp while the replay (clone pinned before that commit) writes n/a.
            # Reconcile mechanically with the RECEIPT's own prereg sha, one stamp at a time.
            sha10 = ((rec.get('own_seat_face') or {}).get('prereg_commit') or '')[:10]
            if sha10:
                i_n1, s_n1 = stamped_match(rep_n1, rec['n1_sha16_post'], sha10)
                i_pf, s_pf = stamped_match(rep_pf, rec['pf_sha16_post'], sha10)
                ev['post_match_mode'] = 'single-stamp-replay(receipt prereg sha)'
                ev['replay_n1_sha16_post_stamped'] = s_n1
                ev['replay_pf_sha16_post_stamped'] = s_pf
                ev['stamped_index'] = {'n1': i_n1, 'pf': i_pf}
                ev['post_faces_match_receipt'] = (s_n1 == rec['n1_sha16_post']
                                                  and s_pf == rec['pf_sha16_post'])

        if not ev['post_faces_match_receipt']:
            # r1192 W307: the wave block stamps the prereg commit AND the seat/probe receipt
            # commit; the replay can reproduce neither (both postdate origin_base). The stamps
            # appear in two shapes -- '"freeze-time commit n/a @ probe receipt n/a"' (registry
            # row) and 'freeze-time gate n/a; probe receipt <path> @ n/a)' (prose comment).
            # Fill both from the RECEIPT's own_seat_face; the resulting byte face must equal
            # the receipt face, so the hash (not the fill) is the judge.
            seat10 = ((rec.get('own_seat_face') or {}).get('seat_origin') or '')[:10]
            receipt_name = os.path.basename(a.probe_receipt).encode()
            if sha10 and seat10:
                pair_pat = b'freeze-time commit n/a @ probe receipt n/a'
                pair_fill = (b'freeze-time commit ' + sha10.encode()
                             + b' @ probe receipt ' + seat10.encode())

                def wave_fill(b):
                    c = b.replace(pair_pat, pair_fill)
                    lines = c.split(b'\n')
                    for k, ln in enumerate(lines):
                        if receipt_name in ln and b'@ n/a' in ln:
                            lines[k] = ln.replace(b'@ n/a', b'@ ' + seat10.encode())
                            if k and b'freeze-time gate n/a' in lines[k - 1]:
                                lines[k - 1] = lines[k - 1].replace(
                                    b'freeze-time gate n/a',
                                    b'freeze-time gate ' + sha10.encode())
                    return b'\n'.join(lines)

                cand_n1 = wave_fill(rep_n1_raw)
                cand_pf = wave_fill(rep_pf_raw)
                if (sha16(cand_n1) == rec['n1_sha16_post']
                        and sha16(cand_pf) == rec['pf_sha16_post']):
                    rep_n1, rep_pf = cand_n1, cand_pf
                    ev['post_match_mode'] = 'wave-block-stamp-fill(receipt own_seat_face)'
                    ev['stamp_fill'] = {'prereg_commit10': sha10,
                                        'seat_origin10': seat10,
                                        'probe_receipt_name': receipt_name.decode()}
                    ev['post_faces_match_receipt'] = True

        # ---- content face: replay (LF) vs landed (LF) ----
        def lf(b):
            return b.replace(b'\r\n', b'\n')

        rep_lf, ld_lf = lf(rep_n1), lf(landed_n1)
        ev['replay_lf_sha16'] = sha16(rep_lf)
        ev['landed_lf_sha16'] = sha16(ld_lf)
        ev['replay_lf_eq_landed'] = rep_lf == ld_lf
        deltas, heals = [], []
        if not ev['replay_lf_eq_landed']:
            import difflib
            A = rep_lf.decode('utf-8').split('\n')
            B = ld_lf.decode('utf-8').split('\n')
            sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == 'equal':
                    continue
                old, new = A[i1:i2], B[j1:j2]
                parity_count = (rec.get('parity') or {}).get('total_parity_rows')
                ok = len(old) == len(new) and all(
                    heal_pair_ok(o, n, parity_count) for o, n in zip(old, new))
                (heals if ok else deltas).append(
                    {'tag': tag, 'replay_lines': old[:4], 'landed_lines': new[:4],
                     'replay_lineno': i1 + 1, 'landed_lineno': j1 + 1})
        ev['heal_deltas'] = heals
        ev['unexplained_deltas'] = deltas

        clean = (ev['pre_faces_match_receipt'] and ev['post_faces_match_receipt']
                 and not deltas)
        ev['verdict'] = 'PASS' if clean else 'FAIL'
        ev['law'] = ('worktree==landed is compared CR-normalized (autocrlf smudge face); '
                     'receipt post faces are pre-commit CRLF faces -> reconciled by mechanical replay, '
                     'never by trusting either side (r1188 bm-c)')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        ev.pop('tmp', None)

    out = os.path.join(REPO, a.out)
    io.open(out, 'w', encoding='utf-8', newline='\n').write(json.dumps(ev, indent=1))
    print(json.dumps({k: ev[k] for k in ('wave', 'verdict', 'pre_faces_match_receipt',
                                         'post_faces_match_receipt', 'replay_lf_eq_landed',
                                         'heal_deltas', 'unexplained_deltas')}, indent=1))
    print('WROTE', a.out)
    raise SystemExit(0 if ev['verdict'] == 'PASS' else 1)


if __name__ == '__main__':
    main()