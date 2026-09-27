# r91 bm-c: CODELY.md <=10KB in-window archival (22nd batch) + new r91 pitlaw append
# Law chain: O-20260927-0230 (10KB hard line) + r331 entry-union bidirectional verification
# + r338bma writer-format law (byte-exact EOL/indent replication — applied to both files here)
import io, sys

MARK_R338 = '- [2026-09-27 16:5x r338 bm-a] \u5751\u5f8b\uff1a**'
POINTER_R338 = ('- [2026-09-27 16:5x r338 bm-a] \u5751\u5f8b\uff08\u4e8c\u5341\u4e8c\u6279\u5916\u8fc1\u00b7\u6307\u9488\uff09\uff1a'
                '\u5171\u4eab JSON \u9762 python \u7f16\u8f91\u5fc5\u5148\u63a2\u539f\u5199\u8005\u683c\u5f0f\u9010\u5b57\u8282\u590d\u523b'
                '\uff08EOL/indent/\u5c3e\u6362\u884c\u00b7\u9ed8\u8ba4 json.dump \u6574\u4ef6\u91cd\u5199=churn \u653e\u5927\uff09\u3002'
                '\u5168\u6587 verbatim=research/memory-archive/202609.md\u300e\u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e8c\u5341\u4e8c\u6279\u300f\u8282\u3002')
NEW_R91 = ('- [2026-09-27 17:2x r91 bm-c] \u5751\u5f8b\uff1a**S0 pull \u5bf9\u5171\u4eab\u6eda\u52a8\u53f0\u8d26 stash\u2192pop \u5fc5 UU'
           '\u2014\u2014resolver \u5b9a\u4fa7\u6e90=git show HEAD:<path>+stash@{N}:<path>\uff08:2:/:3: \u7ecf\u4efb\u4f55 git add \u5373\u706d\u00b7r90 \u8868\u4eb2\uff09\uff1b'
           '\u89e3\u5b8c\u624d add \u4e14\u987b\u8d76 :X0:02 tick \u524d\uff08tick add \u541e\u6807\u8bb0\u4ef6\u5165 commit\u00b7r331 \u5f8b\uff09\uff1b'
           'PS \u5f15 stash@{0} \u5fc5\u5355\u5f15\u53f7\uff08@{0} \u54c8\u5e0c\u8868\u8bed\u6cd5\u9759\u9ed8\u541e\u53c2\uff09**\u3002'
           '\u6b63\u5178=stash push <file>\u2192pull --rebase\u2192pop UU\u2192HEAD/stash \u53cc\u4fa7\u6574\u6761 canonical-json dedup'
           '+ts \u6392\u5e8f+\u7a97\u53e3 cap+last_tick \u53d6\u65b0\u2192JSON \u6821\u9a8c\u2192add\u2192drop\u3002'
           'r91 \u5b9e\u5f39 48+48\u219250\u2192cap48 \u5168\u843d\u76d8\uff08v1 \u76f2 add \u706d stage blob=v2 \u53cc\u6e90\u5168\u6551\uff09\u3002'
           '\u6307\u9488=results/_r91bmc_resolve_autofill.py+commit r91\u3002')

def read_exact(p):
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        return f.read()

def write_exact(p, t):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)

codely = read_exact('CODELY.md')
lines = codely.split('\r\n') if '\r\n' in codely else codely.split('\n')
eol = '\r\n' if '\r\n' in codely else '\n'
hits = [i for i, ln in enumerate(lines) if ln.startswith(MARK_R338)]
assert len(hits) == 1, f'r338 full entry hits={len(hits)} (expect 1)'
i = hits[0]
r338_full = lines[i]
print(f'r338 full entry: {len(r338_full.encode("utf-8"))}B')
assert 'runnable_pool' in r338_full and '_r338bma_fmt_check.py' in r338_full, 'r338 entry identity check'

lines[i] = POINTER_R338
while lines and lines[-1] == '':
    lines.pop()
lines.append(NEW_R91)
new_codely = eol.join(lines) + eol
write_exact('CODELY.md', new_codely)

archive = read_exact('research/memory-archive/202609.md')
section = (eol + '## \u5751\u5f8b\u5f52\u6863 2026-09-27 \u4e8c\u5341\u4e8c\u6279\uff08r91 bm-c\u00b7\u6c34\u4f4d\u5f8b\u5f53\u7a97\u6574\u7f16\uff1a'
           'r91 \u65b0\u5751\u5f8b append \u540e\u8d85 \u226410KB \u786c\u7ebf\u00b7r338bma \u5171\u4eab JSON \u5199\u8005\u683c\u5f0f\u5f8b\u5168\u6587\u5916\u8fc1\u00b7\u884c\u7ea7\u96f6\u4e22\u5931\uff09' + eol + eol
           + r338_full + eol)
write_exact('research/memory-archive/202609.md', archive + section)

# bidirectional zero-loss verification (r331 law)
chk_c = read_exact('CODELY.md')
chk_a = read_exact('research/memory-archive/202609.md')
assert r338_full in chk_a, 'verbatim lost in archive'
assert r338_full not in chk_c, 'full entry still in CODELY (pointer replace failed)'
assert POINTER_R338 in chk_c and NEW_R91 in chk_c, 'pointer/new entry missing'
sz = len(chk_c.encode('utf-8'))
print(f'CODELY.md now {sz}B (limit 10000B) archive +{len(section.encode("utf-8"))}B')
sys.exit(0 if sz <= 10000 else 3)
