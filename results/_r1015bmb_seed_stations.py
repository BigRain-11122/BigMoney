"""r1015 one-shot: seed ST-005/ST-006 into the drama content queue (lock-held,
fresh-read-modify-write per content_loop_step lock law), then engine selftest."""
import io
import json
import os
import sys

sys.path.insert(0, r'C:\Fluxgroup\FluxGroup\quant\bigmoney\Tools')
import content_loop_step as cls

NEW = [
    {
        'id': 'ST-005',
        'title': 'voice-library env bootstrap: GPT-SoVITS phased install driver (venv+torch-cpu+deps+modelscope weights+smoke, detached carrier, idempotent phases)',
        'state': 'open',
        'lane': 'cpu-code',
        'runner': 'st005_gpt_sovits_env_ignite',
        'require': 'none',
        'product': 'detached driver live-or-done + status face results/drama_env/gpt_sovits_env_status.json + install log (media area)',
        'source': 'ST-003 eval next-batch item (env install, <=10-22 window); O-20261018-2144-bm-c sec.2.1 voice-library lane',
        'claim': None,
    },
    {
        'id': 'ST-006',
        'title': 'voice-bank manifest v0.1: 7 canon character voice entries (schema+descriptors+ref-clip sourcing shortlist+consistency gate spec)',
        'state': 'open',
        'lane': 'cpu-code',
        'runner': 'st006_voice_bank_manifest',
        'require': 'none',
        'product': 'content/drama/voice_bank/manifest.json + outbox receipt VOICE-BANK-MANIFEST-v0.1.md',
        'source': 'VOICE-PIPELINE-SKELETON-v1 sec.2 (voice bank schema); ST-003 eval next-batch item (first voice-bank entries)',
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

r = os.system('')  # noop keep py happy
import subprocess
p = subprocess.run([sys.executable, r'C:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\content_loop_step.py', 'selftest'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('engine selftest rc=', p.returncode)
print(p.stdout.strip()[-400:])
p = subprocess.run([sys.executable, r'C:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\content_loop_step.py', 'scan'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('scan:', p.stdout.strip()[-300:])
