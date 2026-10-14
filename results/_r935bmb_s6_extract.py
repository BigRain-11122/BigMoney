# r935 bm-b: extract key S6 chain readings (ASCII-only)
import io, re

txt = io.open(r"results/_r935bmb_s6_log.txt", encoding="utf-8", errors="replace").read()
pats = [
    r"^=== \S+ rc=\d+ \S+",
    r"^\[pool_dualrun\].*",
    r"drift-free streak \d+",
    r'"flags": \[.*\]',
    r'"verdict": "[a-z_]+"',
    r'"load_state": "[a-z\-]+"',
    r"^S6 chain r935 done.*",
]
for pat in pats:
    for m in re.finditer(pat, txt, re.M):
        print(m.group(0)[:170])
