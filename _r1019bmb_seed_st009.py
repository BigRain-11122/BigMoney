# r1019: seed ST-009 station row into content/drama/queue.json (engine lock held,
# fresh-read-modify-write per r1006 multi-writer law; engine functions reused,
# zero reimplementation). ASCII only.
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'Tools'))
import content_loop_step as eng  # noqa: E402

ok, why = eng.acquire_lock()
if not ok:
    print(json.dumps({'verdict': 'lock-held', 'why': why}))
    sys.exit(2)
try:
    q = eng.rd_json(eng.QPATH, None)
    if q is None:
        print(json.dumps({'verdict': 'mechanism-fault', 'why': 'queue.json unreadable'}))
        sys.exit(2)
    ids = [s['id'] for s in q['stations']]
    if 'ST-009' in ids:
        print(json.dumps({'verdict': 'already-seeded'}))
        sys.exit(0)
    q['stations'].append({
        'id': 'ST-009',
        'title': ('character voice differentiation eval v0.1: voice_07/voice_05 '
                  'shared-base debt measurement + pitch-tier proposal (param tiering '
                  'vs fine-tune feasibility) before full-episode casting'),
        'state': 'open',
        'lane': 'cpu',
        'runner': 'st009_voice_differentiation_eval',
        'require': 'ST-008',
        'product': ('content/drama/outbox/VOICE-DIFFERENTIATION-EVAL-v0.1.md + '
                    'status face results/drama_env/voice_differentiation_eval.json'),
        'source': ('ST-008 receipt next-station row (shared-base debt disclosed: '
                   'XIONG/XIONGWEI/FATHER=voice_07, MANCANG=voice_05); r1018 '
                   'next-pointer item 3; VOICE-PIPELINE-SKELETON-v1 sec.2'),
        'claim': None,
    })
    eng.wr_json(eng.QPATH, q)
    eng.regen_md(q)
    print(json.dumps({'verdict': 'seeded', 'station': 'ST-009',
                      'n_stations': len(q['stations'])}))
finally:
    eng.release_lock()
