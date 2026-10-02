# -*- coding: utf-8 -*-
# r581 bm-b: anchor-surface probe for the W97 freeze edits tool
import subprocess


def show(path):
    return subprocess.run(["git", "show", "HEAD:" + path],
                          capture_output=True).stdout.decode("utf-8", "replace")


pf = show("scripts/perpetual_faces.py")
i = pf.rfind('96: {"a"')
print("--- pf W96 entry (rfind):")
print(pf[i - 100:i + 720])
print("=== close-line after 96 entry:",
      repr(pf[i:i + 900].split('engine_owner": "bm-a"},')[0][-80:]), "...")

n1 = show("scripts/perpetual_faces_n1.py")
j = n1.find('"shard_subdir": "n1_w96"')
print("--- n1 W96 cfg entry:")
print(n1[j - 120:j + 700])

canon = show("research/PERPETUAL_FACES.md")
k = canon.rfind("- N1 " + chr(27874) + "96")
print("--- canon W96 row (head 500):")
print(canon[k:k + 500])
print("--- canon W96 row (tail 400):")
m = canon.find("\n- ", k + 10)
print(canon[m - 400:m + 60] if m > 0 else "(W96 is the last row; tail =)")
print(canon[-500:] if m < 0 else "")
