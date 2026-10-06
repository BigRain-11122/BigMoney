# -*- coding: utf-8 -*-
"""r771 bm-a: capture W155 editor runtime strings (full, with edit() stubbed)
and dump exact delivery-window + sec8 + tail segments for needle building."""
import io

src = io.open(r"results/_r768bma_w155_freeze_edits.py", "r", encoding="utf-8", newline="").read()
lines = src.splitlines(keepends=True)
i_pf = next(i for i, l in enumerate(lines) if l.startswith("edit(PF"))
i_n1 = next(i for i, l in enumerate(lines) if l.startswith("edit(N1"))
i_tail = next(i for i, l in enumerate(lines) if l.startswith("# --- post-edit"))

ns = {"RECORDED": {}}
head = "".join(lines[:i_pf]) + "RECORDED['pf'] = [(a1, r1)]\n" + \
       "".join(lines[i_pf + 1:i_n1]) + \
       "RECORDED['n1'] = [(a2, r2), (a3, r3), (a4, r4)]\n"
exec(compile(head, "w155_head", "exec"), ns)

import json
out = {k: ns[k] for k in ("a1", "r1", "a2", "r2", "a3", "r3", "a4", "r4")}
json.dump(out, open(r"results/_r771bma_w155_runtime_strings.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("captured:", {k: len(v) for k, v in out.items()})

for k in ("r1", "r2", "r3"):
    s = out[k]
    for j, tag in enumerate(("delivery window", "gate leg3", "finalize window")):
        i = s.find(tag)
        if i >= 0:
            print(f"--- {k} [{tag}] @{i}")
            print(repr(s[max(0, i - 120):i + 420]))
            print()
# also: full post-edit tail of template editor (for manual rewrite reference)
print("=== template tail (post-edit asserts) ===")
print("".join(lines[i_tail:i_tail + 20]))
