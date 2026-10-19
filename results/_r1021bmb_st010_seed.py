"""r1021 bm-b: seed ST-010 (pitch-tier test synthesis, runner-ready) + ST-011
(BOY/MANCANG sourcing, v0.2-pending) into content/drama/queue.json under the
content-loop lock (fresh-read-modify-write, r1006 law). Regenerates QUEUE.md.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'Tools'))
import content_loop_step as cls  # noqa: E402


def main():
    ok, why = cls.acquire_lock()
    if not ok:
        print(json.dumps({'verdict': 'lock-held', 'why': why}))
        return 1
    try:
        q = cls.rd_json(cls.QPATH, None)
        if q is None:
            print(json.dumps({'verdict': 'mechanism-fault'}))
            return 1
        ids = [s['id'] for s in q['stations']]
        added = []
        if 'ST-010' not in ids:
            q['stations'].append({
                'id': 'ST-010',
                'title': ('pitch-tier test-synthesis station: XIONG/XIONGWEI/FATHER 1 line '
                          'each through GPT-SoVITS + tier DSP (0/+3/-1 st machine-read from '
                          'ST-009 face) + RMS re-match -> re-measure F0 separation >=15% gate'),
                'state': 'open',
                'lane': 'cpu',
                'runner': 'st010_pitch_tier_test_synth',
                'require': 'ST-009',
                'product': ('media/drama-tools/voice_smoke/st010/<CID>/tier.wav x3 (media area) '
                            '+ status face results/drama_env/pitch_tier_test_synth.json + '
                            'outbox receipt ST-010-PITCH-TIER-TEST-SYNTH-RECEIPT.md'),
                'source': ('r1020 next-pointer item 1 (r1019 debt, first action); ST-009 '
                           'receipt next-station row; O-20261018-2144-bm-c sec.2.1 voice P1 <=10-22'),
                'claim': None,
            })
            added.append('ST-010')
        if 'ST-011' not in ids:
            q['stations'].append({
                'id': 'ST-011',
                'title': ('BOY/MANCANG sourcing station: child-voice license review FIRST '
                          '(BOY) + MANCANG de-clip re-production or new-source pick (voice_05 '
                          'narrator-shared-base avoidance = root fix per ST-009 sec.3)'),
                'state': 'open',
                'lane': 'cpu',
                'runner': 'v0.2-pending',
                'require': 'none',
                'product': ('sourced+admitted BOY ref clips (license-cleared or in-house) + '
                            'MANCANG clean re-production entries + manifest update + receipt'),
                'source': ('r1020 next-pointer item 2; ST-009 receipt next-station row; '
                           'ST-008 honest gaps (BOY zero material / MANCANG all-CLIPPED)'),
                'claim': None,
            })
            added.append('ST-011')
        if added:
            cls.wr_json(cls.QPATH, q)
        cls.regen_md(cls.rd_json(cls.QPATH, q))
        print(json.dumps({'verdict': 'seeded' if added else 'no-change',
                          'added': added, 'stations': len(q['stations'])},
                         ensure_ascii=False))
        return 0
    finally:
        cls.release_lock()


if __name__ == '__main__':
    sys.exit(main())
