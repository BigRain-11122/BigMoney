import io

d = io.open(r'research\PERPETUAL_N1_W276_PREREG.md', encoding='utf-8').read()
for i, ln in enumerate(d.splitlines(), 1):
    if '622501' in ln or '624501' in ln or 'base=' in ln:
        print('L%d: %s' % (i, ln.strip()[:220]))
