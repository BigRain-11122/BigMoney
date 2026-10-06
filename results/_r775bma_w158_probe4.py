# -*- coding: utf-8 -*-
import io, json, subprocess, re

# 1) W157 freeze commit sha (the commit that landed the W157 row in pf.py)
r = subprocess.run(["git", "log", "--oneline", "-S", '157: {"a": (360_204, 362_203',
                   "--", "scripts/perpetual_faces.py"], capture_output=True, text=True,
                  encoding="utf-8", errors="replace")
print("=== W157 freeze commits ===")
print(r.stdout.strip()[:400])

# 2) W157 entry full text (n1.py)
src = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8", newline="").read()
k = src.find('157: {"batch"')
m = src.find('"engine_owner": "bm-a"},', k)
entry = src[k:m + len('"engine_owner": "bm-a"},')]
print("=== W157 entry len ===", len(entry))
io.open(r"results\_r775bma_w158_entry_template.txt", "w", encoding="utf-8", newline="").write(entry)

# stats block inside the entry (K-lift / mu / se_mu region)
i = entry.find("W156 finalize")
print(entry[i - 100:i + 900] if i > 0 else "NO W156 finalize cite")

# 3) materializer pre/post
w = src.find("# --- W157 materializer face")
t2 = src.find("# --- T-141 s2 lane face", w)
block = src[w:t2]
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
print("=== pre len", len(pre), "=== post len", len(post))
io.open(r"results\_r775bma_w158_mat_pre.txt", "w", encoding="utf-8", newline="").write(pre)
io.open(r"results\_r775bma_w158_mat_post.txt", "w", encoding="utf-8", newline="").write(post)
print("--- PRE ---")
print(pre[:1200])
print("--- POST ---")
print(post[:600])

# 4) W157 finalize stats from results json
d = json.load(open(r"results\perpetual_faces\n1_w157_results.json", encoding="utf-8"))
print("=== n1_w157_results.json keys ===")
print(sorted(d.keys())[:40])
for key in ("ledger_head", "k_merged", "mu", "mu_merged", "sigma", "a_p95", "k_lift",
            "se_mu", "mu_delta", "merged_pool_k", "pool_k", "k_total"):
    if key in d:
        print(key, "=", d[key])
