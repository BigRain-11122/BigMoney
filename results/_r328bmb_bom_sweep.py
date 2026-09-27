# -*- coding: utf-8 -*-
"""r328 bm-b BOM sweep + strict-load assertion (r323 gbk_sweep lineage, byte-face family).

Lesson: PS 5.x `>` redirection / Out-File default encoding = UTF-8 WITH BOM.
18 fleet JSON files (3 tasks + 15 transfers) were BOM-polluted by an early PS
writer; strict `json.load(io.open(..., encoding='utf-8'))` readers crash on
them (hit live in r328 S2 board scan). Fix in r328 = byte-faithful 3-byte BOM
strip + content-identity assertion + full-repo rescan (18/18, rescan=0).

This artifact re-runs the assertion so any future BOM regression is caught:
  1. no repo *.json starts with EF BB BF
  2. every fleet/ JSON strict-loads under encoding='utf-8'
Exit 0 = clean; nonzero = pollution found (paths printed).
"""
import io, json, os, sys

EXCLUDE_DIRS = {'.git', '__pycache__', 'Money02', 'legacy', '.codely-cli', 'node_modules'}


def scan_bom(root='.'):
    hits = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if fn.endswith('.json'):
                p = os.path.join(dirpath, fn)
                with open(p, 'rb') as fh:
                    if fh.read(3) == b'\xef\xbb\xbf':
                        hits.append(p)
    return hits


def strict_load_fleet():
    bad = []
    for sub in ('tasks', 'transfers', 'machines'):
        d = os.path.join('fleet', sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith('.json'):
                continue
            p = os.path.join(d, fn)
            try:
                json.load(io.open(p, encoding='utf-8'))
            except Exception as e:
                bad.append((p, repr(e)))
    return bad


if __name__ == '__main__':
    bom = scan_bom()
    bad = strict_load_fleet()
    for p in bom:
        print('BOM:', p)
    for p, e in bad:
        print('STRICT-LOAD-FAIL:', p, e)
    print('bom_files=%d strict_load_fail=%d' % (len(bom), len(bad)))
    sys.exit(0 if (not bom and not bad) else 1)
