import io

d = io.open(r'research\PERPETUAL_N1_W276_PREREG.md', encoding='utf-8').read()
checks = [
    ('A band 622_501..624_500', '622_501..624_500'),
    ('B band 624_501..624_700', '624_501..624_700'),
    ('naive refused 622_301..624_300', '622_301..624_300'),
    ('registered W275 B 622_301..622_500', '622_301..622_500'),
    ('heal-16 refuser face', '注册 W275 B 带 622_301..622_500 落 naive A 窗内'),
    ('heal-17 freezer face', 'W277 freezer 承接面强制注记'),
    ('live RAM face ~3.8GB', '本窗 free RAM ~3.8GB'),
    ('wave 276', '波号 276'),
    ('W277p projection A', '624_501..626_500'),
    ('W277p projection B', '624_701..624_900'),
    ('merged mu 8dp', '−0.09280541'),
    ('sigma 8dp', '0.24507989'),
    ('W275-only mu', '−0.09398255'),
    ('A p95 0.3088', '0.3088'),
    ('ledger 1,029,335', '1,029,335'),
    ('merged K 602,920', '602,920'),
    ('se_mu 0.000316', '0.000316'),
    ('n_eff 1,027,135', '1,027,135'),
    ('key1 gap 0.0012', '0.0012'),
    ('seat MSG-20261019-055x', 'MSG-20261019-055x'),
    ('seat origin 21b51a102', '21b51a102'),
    ('freezer doubled-tail absent', '回释·MV 车道已收官 GPU idle 回释）'),
    ('stale bare 4.4GB absent', '本窗 free RAM ~4.4GB'),
    ('r1109 seat window', 'bm-c 循环班 r1109 席位窗'),
    ('A_ext base=622501', 'base=622501 span=2000'),
    ('B_ext base=624501', 'base=624501 span=200'),
]
bad = 0
for name, face in checks:
    n = d.count(face)
    expect_absent = face in ('回释·MV 车道已收官 GPU idle 回释）', '本窗 free RAM ~4.4GB')
    ok = (n == 0) if expect_absent else (n >= 1)
    if not ok:
        bad += 1
    print('%s %-36s count=%d' % ('OK ' if ok else 'BAD', name, n))
print('RESULT:', 'ALL PASS' if bad == 0 else '%d BAD' % bad)
