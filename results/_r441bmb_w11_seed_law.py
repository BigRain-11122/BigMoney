# W11 freeze-step seed three-step law (draft clause-5 collision re-take):
# draft berth 20316000/20316500/20317000 collides with bm-a r445 A12
# (t101_v4_a12_predcond_scrnull/unc = 20316000/20316500). Per W9 double-
# collision precedent: re-take = +500 ladder -> 20317000/20317500/20318000.
# Three steps: (1) registry full-keyed exact zero-collision, (2) Sobol/NPCG
# first-element mutual distinctness vs all existing int bases, (3) derive-band
# overlap check + repo-wide rg classification for the bare numbers.
import io, json, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NEW = [20317000, 20317500, 20318000]
KEYS = ["trial_labor_w11_gen", "trial_labor_w11_scrnull", "trial_labor_w11_unc"]

src = io.open("scripts/science_gates.py", encoding="utf-8").read()
# registry block = SEED_REGISTRY dict literal; extract key -> int pairs
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
# new-basis mutual distinctness
fe_new = [facts["first_els"][str(n)] for n in NEW]
facts["new_first_els_mutual_distinct"] = len(set(fe_new)) == len(fe_new)

# Step 3a: derive-band overlap (null band 20317500..20317699, unc band 20318000..20318200)
bands = [(20317500, 20317699), (20318000, 20318200)]
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

io.open("results/_r441bmb_w11_seed_law_facts.json", "w", encoding="utf-8").write(
    json.dumps(facts, ensure_ascii=False, indent=1))
print("step1 zero-collision:", facts["verdict_step1_zero_collision"])
print("step2 first-el distinct:", facts["verdict_step2_distinct"], facts["first_els"])
print("step3 bands clean:", facts["verdict_step3_bands_clean"])
for n in NEW:
    print(f"rg {n} hits: {len(facts['rg_hits'][str(n)])}")
    for l in facts["rg_hits"][str(n)][:6]:
        print("   ", l[:160])
