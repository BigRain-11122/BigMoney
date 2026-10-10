# -*- coding: utf-8 -*-
"""r868 wave-counts heal: patch the two corrupted derived faces of the
landed MP1 artifacts (verdict_counts_by_wave in the JSON + the MD wave
table) with true values recomputed from the intact per-gate results.
Runner function bug fixed separately (generator single-use pit, disclosed
in prereg sec.7). Deterministic: recompute from landed data, verify sums,
patch only the corrupted field, raw-text CRLF-safe JSON face preserved."""
import json
import subprocess

JP = "results/mp1_tsgate_p1.json"
MP = "research/MP1_TSGATE.md"

p = json.load(open(JP, encoding="utf-8"))
true_wave = {"W19": {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "N/A": 0},
             "W20": {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "N/A": 0}}
for g, a in p["results"].items():
    true_wave[a["wave"]][a["verdict"]] += 1
tot = {v: sum(true_wave[w][v] for w in true_wave)
       for v in ("PASS", "PARTIAL", "FAIL", "N/A")}
assert tot == p["verdict_counts"], (tot, p["verdict_counts"])
assert p["verdict_counts_by_wave"] != true_wave  # only patch if corrupted
assert sum(true_wave["W19"].values()) == 96 and sum(true_wave["W20"].values()) == 82

# byte face probe before rewrite (r500 law)
b = open(JP, "rb").read()
crlf = b.count(b"\r\n") == b.count(b"\n") and b.count(b"\r\n") > 0
eol = "\r\n" if crlf else "\n"

p["verdict_counts_by_wave"] = true_wave
text = json.dumps(p, ensure_ascii=False, indent=1)
if crlf:
    text = text.replace("\n", "\r\n")
json.loads(text)  # parse gate before write
with open(JP, "w", encoding="utf-8", newline="") as fh:
    fh.write(text)
rp = json.load(open(JP, encoding="utf-8"))
assert rp["verdict_counts_by_wave"] == true_wave
st = subprocess.run(["git", "diff", "--numstat", JP], capture_output=True, text=True)
print(JP, "->", st.stdout.strip())

# MD wave table rows
md = open(MP, encoding="utf-8").read()
if crlf:
    md = md.replace("\r\n", "\n")  # normalize for surgical work, restore after
old_w19 = "| W19 | 8 | 0 | 0 | 0 |"
old_w20 = "| W20 | 17 | 0 | 0 | 0 |"
new_w19 = "| W19 | 8 | 32 | 56 | 0 |"
new_w20 = "| W20 | 17 | 11 | 54 | 0 |"
assert old_w19 in md and old_w20 in md, "MD wave rows not in corrupted form"
md = md.replace(old_w19, new_w19).replace(old_w20, new_w20)
if crlf:
    md = md.replace("\n", "\r\n")
with open(MP, "w", encoding="utf-8", newline="") as fh:
    fh.write(md)
st = subprocess.run(["git", "diff", "--numstat", MP], capture_output=True, text=True)
print(MP, "->", st.stdout.strip())
print("heal OK: wave table W19 8/32/56 + W20 17/11/54 (sum 178 == verdict_counts)")
