# W12 freeze-step seed three-step law (W11 _r441bmb_w11_seed_law.py verbatim
# lineage, keys swapped): draft berth 20320500/20321000/20321500 (+500 natural
# ladder from W11 20317000/20317500/20318000; draft-time registry tail read
# max=20320000, freeze-time live re-read tail includes innovation_quota_w4_
# volregime 20322000 -- different value, no exact berth collision; berths
# declared by bm-a r447 draft comment line, zero registered keys on them).
# Three steps: (1) registry full-keyed exact zero-collision, (2) Sobol/NPCG
# first-element mutual distinctness vs all existing int bases, (3) derive-band
# overlap check + repo-wide rg classification for the bare numbers.
import io, json, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NEW = [20320500, 20321000, 20321500]
KEYS = ["trial_labor_w12_gen", "trial_labor_w12_scrnull", "trial_labor_w12_unc"]

src = io.open("scripts/science_gates.py", encoding="utf-8").read()
pairs = re.findall(r'"([A-Za-z0-9_]+)":\s*(\d{6,})', src)
reg = {}
for k, v in pairs:
    reg[k] = int(v)

facts = {"new": NEW, "new_keys": KEYS, "collision_values": [], "collision_keys": [],
         "first_els": {}, "first_el_clash": [], "band_overlap": [], "rg_hits": {}}

# Step 1: exact zero-collision (values + key names)
for n in NEW:
    hits = [k for k, v in reg.items() if v == n]
    if hits:
        facts["collision_values"].append({"value": n, "keys": hits})
for k in KEYS:
    if k in reg:
        facts["collision_keys"].append(k)

# Step 2: first-element distinctness (canonical = int(default_rng(s).integers(0, 2**31)))
import numpy as np
def first_el(s):
    return int(np.random.default_rng(s).integers(0, 2 ** 31))
all_bases = sorted(set(v for v in reg.values() if isinstance(v, int)))
existing_els = {}
for b in all_bases:
    existing_els[b] = first_el(b)
for n in NEW:
    facts["first_els"][str(n)] = first_el(n)
for n in NEW:
    fe = facts["first_els"][str(n)]
    for b, be in existing_els.items():
        if fe == be:
            facts["first_el_clash"].append({"new": n, "first_el": fe, "clashes_base": b})
fe_new = [facts["first_els"][str(n)] for n in NEW]
facts["new_first_els_mutual_distinct"] = len(set(fe_new)) == len(fe_new)

# Step 3a: derive-band overlap (null band 20321000..20321199, unc band 20321500..20321700)
bands = [(20321000, 20321199), (20321500, 20321700)]
for lo, hi in bands:
    ov = [k for k, v in reg.items() if lo <= v <= hi]
    if ov:
        facts["band_overlap"].append({"band": [lo, hi], "keys": ov})

# Step 3b: repo-wide rg for bare numbers
for n in NEW:
    r = subprocess.run(["git", "grep", "-n", "-F", str(n), "--", "."],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    facts["rg_hits"][str(n)] = lines

facts["verdict_step1_zero_collision"] = (not facts["collision_values"]) and (not facts["collision_keys"])
facts["verdict_step2_distinct"] = (not facts["first_el_clash"]) and facts["new_first_els_mutual_distinct"]
facts["verdict_step3_bands_clean"] = not facts["band_overlap"]
facts["n_registry_keys"] = len(reg)
facts["n_int_bases"] = len(all_bases)

io.open("results/_r444bmb_w12_seed_law_facts.json", "w", encoding="utf-8").write(
    json.dumps(facts, ensure_ascii=False, indent=1))
print("step1 zero-collision:", facts["verdict_step1_zero_collision"])
print("step2 first-el distinct:", facts["verdict_step2_distinct"], facts["first_els"])
print("step3 bands clean:", facts["verdict_step3_bands_clean"])
for n in NEW:
    print(f"rg {n} hits: {len(facts['rg_hits'][str(n)])}")
    for l in facts["rg_hits"][str(n)][:6]:
        print("   ", l[:160])
