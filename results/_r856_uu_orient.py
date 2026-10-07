import re

for path in ("results/token_usage.json", "results/compute_audit.json",
             "results/regime_state.json"):
    s = open(path, encoding="utf-8", errors="replace").read()
    ours = re.search(r'<<<<<<<.*?\n(.*?)\n=======', s, re.S)
    theirs = re.search(r'=======\n(.*?)\n>>>>>>>', s, re.S)
    for name, blk in [("OURS(HEAD=origin/bm-c)", ours),
                      ("THEIRS(my r856)", theirs)]:
        if not blk:
            print(path, name, "NO BLOCK")
            continue
        txt = blk.group(1)
        m = re.search(r'"(?:ts|updated)"\s*:\s*"([^"]{10,25})"', txt)
        print(path, name, "ts=", m.group(1) if m else "?")
