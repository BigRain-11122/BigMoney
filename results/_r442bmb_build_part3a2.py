"""r442 bm-b: stage-3a fixups for the 3 failed anchors."""
SRC = open('results/_r442bmb_stage3a.py', encoding='utf-8').read()
fails = []


def rep(old, new, tag, count=1):
    global SRC
    n = SRC.count(old)
    if n != count:
        fails.append(f'[{tag}] expected {count} got {n}: {old[:60]!r}')
        return
    SRC = SRC.replace(old, new)


# facekey: all 4 (loader + generate + selftest x2)
rep('["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face"]',
    '["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_none_face"]',
    'excl-facekey', count=4)
# disc key (actual quote placement)
rep('''    disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_"
            "amp_mom_none_rows": len(rows)}''',
    '''    disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_"
            "amp_mom_std_none_rows": len(rows)}''', 'excl-disckey')
# screen face string (actual line break)
rep('''                         "face": f"{tag}:stop-gate-vol-yang-vconf-"
                                 "streak-tstate-amp-mom-none",''',
    '''                         "face": f"{tag}:stop-gate-vol-yang-vconf-"
                                 "streak-tstate-amp-mom-std-none",''',
    'excl-facestr1')

open('results/_r442bmb_stage3a.py', 'w', encoding='utf-8').write(SRC)
print('fixups done; fails:', len(fails))
for f in fails:
    print(' FAIL', f)
