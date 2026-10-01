import subprocess, re
def st(n):
    return subprocess.run(['git', 'show', ':%d:results/crash_fuse.json' % n],
                          capture_output=True).stdout
a, b = st(2), st(3)   # rebase semantics: 2=origin base, 3=our ride commit
def ts(raw):
    m = re.search(rb'"(?:ts|updated[_a-z]*|last_tick[_a-z]*)"\s*:\s*"([^"]+)"', raw)
    return m.group(1).decode() if m else None
ta, tb = ts(a), ts(b)
win = a if (ta or '') > (tb or '') else b
with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\crash_fuse.json", "wb") as fh:
    fh.write(win)
print('crash_fuse ts: origin=%s mine=%s -> %s' % (ta, tb, 'ORIGIN' if win is a else 'MINE'))
