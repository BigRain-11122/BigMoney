# r1024 bm-b ST-013 direct station execution (r1022/ST-011 precedent, lock-held).
# The generic loop plan holds at ST-012 (gpu-night lane, runner pending on
# purpose -- night-window discipline), so this round targets ST-013 through the
# SAME lock/CLAIMS/regen machinery via module import (single-writer law kept).
import io
import json
import os
import sys

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
sys.path.insert(0, os.path.join(ROOT, 'Tools'))
import content_loop_step as cls  # noqa: E402


def main():
    ok, why = cls.acquire_lock()
    if not ok:
        print(json.dumps({'verdict': 'lock-held', 'why': why}, ensure_ascii=False))
        return 1
    try:
        q = cls.rd_json(cls.QPATH, None)
        if q is None:
            print(json.dumps({'verdict': 'mechanism-fault', 'why': 'queue unreadable'}, ensure_ascii=False))
            return 2
        st = None
        for s in q['stations']:
            if s['id'] == 'ST-013':
                st = s
                break
        if st is None:
            print(json.dumps({'verdict': 'station-missing'}, ensure_ascii=False))
            return 2
        if st.get('state') != 'open':
            print(json.dumps({'verdict': 'not-open', 'state': st.get('state')}, ensure_ascii=False))
            return 0
        # developer-seat runner adoption (same op adopt-runners performs)
        st['runner'] = 'st013_dubbing_sheet_prep'
        st['state'] = 'claimed'
        st['claim'] = 'claimed@bm-b@' + cls.now_iso()
        cls.wr_json(cls.QPATH, q)
        cls.append_line(cls.CLAIMS, json.dumps(
            {'ts': cls.now_iso(), 'station': 'ST-013', 'action': 'claimed', 'by': 'bm-b'},
            ensure_ascii=False))
        action = None
        try:
            action = cls.RUNNERS['st013_dubbing_sheet_prep'](st)
            st['state'] = 'done'
            st['done_at'] = cls.now_iso()
        except Exception as e:
            st['state'] = 'open'   # honest rollback; station stays queued
            action = {'runner': st.get('runner'), 'verdict': 'runner-error', 'err': str(e)[:240]}
        q = cls.rd_json(cls.QPATH, q)
        for s2 in q['stations']:
            if s2['id'] == 'ST-013':
                s2['runner'] = st.get('runner')
                s2['state'] = st['state']
                s2['claim'] = st.get('claim')
                if 'done_at' in st:
                    s2['done_at'] = st['done_at']
        cls.wr_json(cls.QPATH, q)
        cls.append_line(cls.CLAIMS, json.dumps(
            {'ts': cls.now_iso(), 'station': 'ST-013', 'action': st['state'], 'detail': action},
            ensure_ascii=False))
        cls.regen_md(q)
        print(json.dumps({'verdict': st['state'], 'station': 'ST-013', 'action': action},
                         ensure_ascii=False))
        return 0 if st['state'] == 'done' else 3
    finally:
        cls.release_lock()


if __name__ == '__main__':
    sys.exit(main())
