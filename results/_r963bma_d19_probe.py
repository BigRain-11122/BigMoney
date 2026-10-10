import subprocess, hashlib, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def run(*a, cwd=GRP):
    r = subprocess.run([GIT] + list(a), capture_output=True, cwd=cwd)
    return r.stdout

run('fetch', 'origin')
dec = run('show', 'origin/main:docs/decisions.md')
ord_ = run('show', 'origin/main:docs/orders.md')
dec_sha = hashlib.sha1(dec).hexdigest()
ord_sha = hashlib.sha1(ord_).hexdigest()
print("dec sha1:", dec_sha[:12], "| bm-a watermark: a20664ec0852")
print("ord sha1:", ord_sha[:12], "| bm-a watermark: 3af479f138")

if dec_sha != 'a20664ec0852a5ada8cea3f3fb93ea35254d0023':
    print("\n=== DEC DELTA (new rows since a20664ec) ===")
    old = run('show', 'a20664ec0852a5ada8cea3f3fb93ea35254d0023^{commit}', cwd=GRP)  # fallback: not blob; use stored local
    # get previous content from bm-a state known-good: fetch blob by short sha won't work; diff via log
    log = run('log', '--format=%h %s', '-5', '--', 'docs/decisions.md').decode('utf-8', 'replace')
    print("recent decisions.md commits:")
    print(log)
    txt = dec.decode('utf-8', 'replace')
    # print lines mentioning D-20261011 and BigMoney
    for ln in txt.splitlines():
        if 'D-20261011' in ln or ('D-20261010' in ln and 'BigMoney' in ln):
            print("  DEC-ROW:", ln[:400])
    for ln in txt.splitlines():
        if 'BigMoney' in ln and ('2026-10-10' in ln or '2026-10-11' in ln):
            print("  BM-DISPATCH?:", ln[:400])

if ord_sha != '3af479f1383537596cd0937a8d64e056879c27e8':
    print("\n=== ORD DELTA (new rows since 3af479f1) ===")
    txt = ord_.decode('utf-8', 'replace')
    for ln in txt.splitlines():
        if '2026-10-11' in ln or ('2026-10-10' in ln and ('BigMoney' in ln or '2350' in ln or '0012' in ln)):
            print("  ORD-ROW:", ln[:400])
