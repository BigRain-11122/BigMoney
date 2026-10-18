"""r1017 one-shot: seed ST-007 into the drama content queue (lock-held,
fresh-read-modify-write per content_loop_step lock law), then engine selftest."""
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, r'C:\Fluxgroup\FluxGroup\quant\bigmoney\Tools')
import content_loop_step as cls

NEW = [
    {
        'id': 'ST-007',
        'title': 'first-synthesis smoke: GPT-SoVITS v1 zero-shot chain validation (in-house r998 audition ref + manifest text -> clone -> synth -> wav verify)',
        'state': 'open',
        'lane': 'cpu',
        'runner': 'st007_first_synthesis_smoke',
        'require': 'ST-005',
        'product': 'media/drama-tools/voice_smoke/st007/out/output.wav (smoke, media area) + status face results/drama_env/first_synthesis_smoke.json + outbox receipt ST-007-FIRST-SYNTHESIS-SMOKE-RECEIPT.md',
        'source': 'r1016 next-pointer FIRST ACTION (env all-phases DONE 04:11:25); VOICE-PIPELINE-SKELETON-v1 sec.3 TTS lane; O-20261018-2144-bm-c sec.2.1 voice-library P1 <=10-22',
        'claim': None,
    },
]

ok, why = cls.acquire_lock()
print('lock:', ok, why)
assert ok, 'lock-held, abort seeding'
try:
    q = cls.rd_json(cls.QPATH, None)
    assert q is not None, 'queue.json unreadable'
    ids = [s['id'] for s in q['stations']]
    added = []
    for st in NEW:
        if st['id'] not in ids:
            q['stations'].append(st)
            added.append(st['id'])
    cls.wr_json(cls.QPATH, q)
    cls.regen_md(q)
    print('seeded:', added)
finally:
    cls.release_lock()

for cmd in ('selftest', 'scan'):
    p = subprocess.run([sys.executable, r'C:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\content_loop_step.py', cmd],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(cmd, 'rc=', p.returncode, p.stdout.strip()[-300:])
