# _r339bma_resolve_autofill.py -- rebase UU resolver for results/autofill_state.json (r339 bm-a)
# canon: r91 dual-source union (launches union-dedup + cap48 + last_tick take-new)
#        + r338 byte-format law (LF / indent=1 / no trailing newline = origin blob 215bde8b)
# law refs: r87 union-dedup key probe-fields-first; r91 v2 (read stages BEFORE any add)
import json, subprocess, sys

PATH = 'results/autofill_state.json'

def read_stage(n):
    r = subprocess.run(['git', 'show', f':{n}:{PATH}'], capture_output=True)
    if r.returncode != 0:
        print(f'FATAL: stage :{n}: missing ({r.stderr[:200]})')
        sys.exit(2)
    b = r.stdout
    return b, json.loads(b.decode('utf-8'))

def main():
    # guard: path must be UU
    st = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout
    line = [l for l in st.splitlines() if PATH in l]
    if not line or not line[0].startswith('UU'):
        print('FATAL: %s not in UU state; abort (line=%r)' % (PATH, line))
        sys.exit(2)

    b2, d2 = read_stage(2)   # ours = upstream (origin/main, bm-c r91 union result)
    b3, d3 = read_stage(3)   # theirs = my tick-state commit
    b1, d1 = read_stage(1)   # base

    def lkey(e):
        # probe-fields-first (r87): ts+machine+entry+shard identity
        return (e.get('ts'), e.get('machine'), e.get('entry'), e.get('shard'))

    l2 = d2.get('launches', [])
    l3 = d3.get('launches', [])
    seen = {lkey(e) for e in l2}
    missing = [e for e in l3 if lkey(e) not in seen]
    merged = l2 + missing
    merged.sort(key=lambda e: e.get('ts', ''))
    merged = merged[-48:]                      # cap48 (r91)
    d2['launches'] = merged

    lt2 = d2.get('last_tick') or {}
    lt3 = d3.get('last_tick') or {}
    d2['last_tick'] = lt3 if lt3.get('ts', '') > lt2.get('ts', '') else lt2

    out = json.dumps(d2, ensure_ascii=False, indent=1)
    if b2.endswith(b'\n'):                    # match origin blob trailing-newline state
        out += '\n'
    open(PATH, 'wb').write(out.encode('utf-8'))
    print('resolved: launches=%d restored-from-mine=%d last_tick=%s'
          % (len(merged), len(missing), json.dumps(d2['last_tick'], ensure_ascii=False)))
    print('origin fmt: crlf=%s trailing_nl=%s' % (b'\r\n' in b2, b2.endswith(b'\n')))

if __name__ == '__main__':
    main()
