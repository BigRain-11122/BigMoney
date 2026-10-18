"""r1018 bm-b: seed ST-008 (canon voice-bank entries) into content/drama/queue.json
under the engine lock (r1015 lock-held seeding pattern). Idempotent: station id
already present -> zero-action exit 0. Lock held -> exit 3 (retry later round).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'Tools'))
import content_loop_step as cls  # noqa: E402

ok, why = cls.acquire_lock()
if not ok:
    print(json.dumps({'verdict': 'lock-held', 'why': why}))
    sys.exit(3)
try:
    q = cls.rd_json(cls.QPATH, None)
    if q is None:
        print(json.dumps({'verdict': 'mechanism-fault', 'why': 'queue.json unreadable'}))
        sys.exit(2)
    if any(s.get('id') == 'ST-008' for s in q.get('stations', [])):
        print(json.dumps({'verdict': 'already-seeded', 'station': 'ST-008'}))
        sys.exit(0)
    q['stations'].append({
        'id': 'ST-008',
        'title': 'canon voice-bank entries v0.1: role-aligned ref clips 1-3/char from r998 in-house assets + 音色一致检 admission gate (6 chars admitted expected + BOY honest gap)',
        'state': 'open',
        'lane': 'cpu',
        'runner': 'st008_voice_bank_entries',
        'require': 'ST-007',
        'product': 'content/drama/voice_bank/manifest.json ref_clips admitted + status face results/drama_env/voice_bank_entries.json + outbox receipt VOICE-BANK-ENTRIES-v0.1.md',
        'source': 'r1017 next-pointer item 2 (voice P1 <=10-22); VOICE-PIPELINE-SKELETON-v1 sec.2; ST-007 receipt next-station row; ST-006 manifest gate spec',
        'claim': None,
    })
    cls.wr_json(cls.QPATH, q)
    cls.regen_md(q)
    print(json.dumps({'verdict': 'seeded', 'station': 'ST-008',
                      'n_stations': len(q['stations'])}))
finally:
    cls.release_lock()
