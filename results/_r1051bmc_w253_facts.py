# -*- coding: utf-8 -*-
# _r1051bmc_w253_facts.py — W253 prereg derive PREP: facts machine-freeze (r971 honest-split precedent)
# All values machine-derived from on-disk artifacts, ZERO transcription.
import io, os, sys, json, subprocess, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"

def rp(*p):
    return os.path.join(REPO, *p)

facts = {"tool": "_r1051bmc_w253_facts", "ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"), "machine": "bm-c"}

# 1) W252 finalize actuals (n1_w252_results.json)
res = json.load(open(rp("results", "perpetual_faces", "n1_w252_results.json"), encoding="utf-8"))
keys = ["ledger", "K", "mu", "sigma", "se_mu", "skill_line", "line_pre", "line_merged",
        "a_p95", "k_lift", "mu_w252_only", "w252_only_mu", "n_eff", "n_eff_held_equal"]
w252 = {}
for k in keys:
    if k in res:
        w252[k] = res[k]
# fallback: dump top-level scalar faces
for k, v in res.items():
    if isinstance(v, (int, float, str)) and k not in w252:
        w252[k] = v
facts["w252_results_scalars"] = {k: w252[k] for k in sorted(w252)} if w252 else res

# 2) W252 frozen tpl blob identity (committed research/PERPETUAL_N1_W252_PREREG.md)
tpl_path = rp("research", "PERPETUAL_N1_W252_PREREG.md")
ho = subprocess.run(["git", "hash-object", tpl_path], capture_output=True, text=True, cwd=REPO).stdout.strip()
sha256_16 = hashlib.sha256(open(tpl_path, "rb").read()).hexdigest()[:16]
sz = os.path.getsize(tpl_path)
facts["w252_tpl"] = {"path": "research/PERPETUAL_N1_W252_PREREG.md", "blob_sha1": ho,
                     "sha256_16": sha256_16, "bytes": sz}

# 3) worktree tpl == committed blob assert (HEAD state; derive window re-verifies)
show = subprocess.run(["git", "show", "HEAD:research/PERPETUAL_N1_W252_PREREG.md"],
                      capture_output=True, cwd=REPO)
facts["w252_tpl_head_blob_match"] = (subprocess.run(
    ["git", "hash-object", "--stdin"], input=show.stdout, capture_output=True, cwd=REPO
).stdout.decode().strip() == ho) if show.returncode == 0 else False

# 4) W252 registered bands — from the freeze receipt (dual-sha16 receipt in r1050 estate)
fr = None
for cand in ("results/_w252bmc_freeze_receipt.json", "results/_r1050bmc_w252_freeze_receipt.json"):
    if os.path.isfile(rp(cand)):
        fr = cand; break
if fr is None:
    hits = [f for f in os.listdir(rp("results")) if "w252" in f and "freeze" in f and f.endswith(".json")]
    fr = ("results/" + hits[0]) if hits else None
facts["w252_freeze_receipt_file"] = fr
if fr and os.path.isfile(rp(fr)):
    j = json.load(open(rp(fr), encoding="utf-8"))
    facts["w252_freeze_receipt"] = j if isinstance(j, dict) and len(str(j)) < 6000 else {"keys": list(j)[:40] if isinstance(j, dict) else "list"}

# 5) W252 fivekeys receipt
fk = None
for f in sorted(os.listdir(rp("results"))):
    if "w252" in f and "fivekey" in f and f.endswith(".json"):
        fk = f; break
facts["w252_fivekeys_file"] = ("results/" + fk) if fk else None

# 6) band arithmetic — live re-derive from registered faces (state next pointer: A 571_701..573_700 REFUSED at B 571_701..571_900)
#    registered bands extracted from the n1 face file (perpetual registry), never assumed
pf = rp("scripts", "perpetual_faces.py")
reg = {}
if os.path.isfile(pf):
    src = open(pf, encoding="utf-8").read()
    import re
    # find W252-registered band rows like A=569_701..571_700 / B=571_701..571_900
    for m in re.finditer(r"W252[^\n]{0,120}?(A|B)[^\n]{0,10}?(\d{3}_\d{3})\.\.(\d{3}_\d{3})", src):
        reg.setdefault("W252_" + m.group(1), []).append([m.group(2), m.group(3)])
facts["w252_registered_bands_regex_scan"] = reg

# 7) gate0.5 W252 row + finalize presence (prereg §8 anchors)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("sg", rp("scripts", "science_gates.py"))
    sg = importlib.util.module_from_spec(spec); spec.loader.exec_module(sg)
    facts["seed_registry_path"] = getattr(sg, "SEED_REGISTRY", None) or "see-scripts"
except Exception as e:
    facts["seed_registry_path"] = "import-fail: %r" % e

out = rp("results", "_w253bmc_facts.json")
json.dump(facts, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("facts ->", out)
print(json.dumps({k: facts[k] for k in ("w252_tpl", "w252_tpl_head_blob_match", "w252_freeze_receipt_file",
                                        "w252_fivekeys_file", "w252_registered_bands_regex_scan")}, ensure_ascii=False, indent=1))
print("w252 scalars:", json.dumps(facts["w252_results_scalars"], ensure_ascii=False)[:1200])
