# -*- coding: utf-8 -*-
# r976 W234 hygiene re-scan (derive-window honesty re-verification, r971->r972
# precedent: stamps claim the window the derive runs in, so re-verify live).
import glob, json, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

# 1) inbox (pending + processed) W234 mentions, foreign classification
mentions, foreign = 0, 0
for d in ("fleet/inbox", "fleet/inbox/processed"):
    for f in glob.glob(d + "/*.md"):
        txt = open(f, encoding="utf-8", errors="replace").read()
        if "W234" in txt:
            mentions += 1
            if re.search(r"bm-a|bm-b", txt) and "bm-c" not in txt:
                foreign += 1
# 2) origin perpetual_faces.py 234 band rows (registry vacancy)
pf = subprocess.run([GIT, "-C", REPO, "show", "origin/main:scripts/perpetual_faces.py"],
                   capture_output=True).stdout.decode("utf-8", "replace")
pf_234_rows = len(re.findall(r"^\s*\[?234[,\]]", pf, re.M))
pf_n1_234 = len(re.findall(r"PERPETUAL-N1-W234", pf))
# 3) perpetual_faces_n1.py WAVE_CONFIGS 234
pfn1 = open(REPO + r"\scripts\perpetual_faces_n1.py", encoding="utf-8").read()
pfn1_234 = len(re.findall(r"PERPETUAL-N1-W234", pfn1))
# 4) origin PERPETUAL_N1_W234_PREREG.md vacancy
ls = subprocess.run([GIT, "-C", REPO, "ls-tree", "--name-only", "origin/main", "research/"],
                    capture_output=True).stdout.decode("utf-8", "replace")
prereg_on_origin = 1 if "PERPETUAL_N1_W234_PREREG.md" in ls else 0

out = {"window": "r976", "ts": "2026-10-13 20:5x",
       "inbox_processed_W234_mentions": mentions,
       "inbox_processed_W234_foreign_mentions": foreign,
       "perpetual_faces_W234_rows": pf_234_rows,
       "perpetual_faces_n1_W234_wave_configs": pfn1_234 + pf_n1_234,
       "prereg_W234_on_origin": prereg_on_origin}
print(json.dumps(out, ensure_ascii=False, indent=1))
assert foreign == 0, "FOREIGN W234 seat hit -- do not proceed"
assert pf_234_rows == 0 and (pfn1_234 + pf_n1_234) == 0, "registry not vacant"
assert prereg_on_origin == 0, "prereg already on origin"
# merge into facts.json hygiene face (r975 frozen block -> r976 live block)
fp = REPO + r"\results\_w234bmc_facts.json"
facts = json.load(open(fp, encoding="utf-8"))
old_h = dict(facts["hygiene"])
facts["hygiene"] = out
json.dump(facts, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("facts hygiene updated: r975", json.dumps(old_h, ensure_ascii=False), "-> r976 live")
print("HYGIENE-RESCAN-GREEN: foreign=0 / registry-vacant / origin-vacant")
