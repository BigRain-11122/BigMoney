# -*- coding: utf-8 -*-
# r1103 bm-c: W274 prereg derive FACTS GATHER (zero-transcription law; every face machine-read).
# Frozen W273 template face extracted HERE via python subprocess raw bytes (r1096 PS-pipeline
# corruption precedent: never Out-File). Blob-identity vs the W273 prereg FREEZE commit
# 839441a547 (PRE-backfill face per r1052/r1049 law; HEAD post-backfill twin disclosed NOT used).
import json, os, sys, subprocess, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "git"

def go(args, tolerant=False):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        if tolerant:
            return "ERR:" + r.stderr.decode("utf-8", "replace").strip()[:200]
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")[:400]))
    return r.stdout.decode("utf-8", "replace").strip()

facts = {}

# --- W273 prereg freeze commit (the frozen PRE-backfill template face) ---
facts["w273_prereg_commit"] = "839441a547"
facts["w273_prereg_blob"] = go(["rev-parse", "839441a547:research/PERPETUAL_N1_W273_PREREG.md"])
facts["w273_prereg_ts"] = go(["show", "-s", "--format=%ci", "839441a547"])
facts["w273_prereg_subject"] = go(["show", "-s", "--format=%s", "839441a547"])[:160]
facts["head_tpl_blob"] = go(["rev-parse", "HEAD:research/PERPETUAL_N1_W273_PREREG.md"])
r = subprocess.run([GIT, "show", "839441a547:research/PERPETUAL_N1_W273_PREREG.md"], capture_output=True, cwd=REPO)
assert r.returncode == 0, "git show frozen face failed"
blob = r.stdout
facts["w273_prereg_size"] = len(blob)
facts["w273_prereg_sha256_16"] = hashlib.sha256(blob).hexdigest()[:16]
facts["w273_prereg_sha256_full"] = hashlib.sha256(blob).hexdigest()
src = os.path.join(REPO, "results", "_w274bmc_w273_frozen_face.txt")
with open(src, "wb") as f:
    f.write(blob)
assert hashlib.sha256(open(src, "rb").read()).digest() == hashlib.sha256(blob).digest()
facts["frozen_face_written"] = src

# --- chain commit existence + timestamps (W273 cycle + W274 seat) ---
for k, s in (("w273_splice", "04f2127db"), ("w273_burn1", "fbb4788c49"), ("w273_burn2", "acc7fd02c0"),
             ("w273_finalize_estate", "6659a0e36"), ("w274_seat", "70b21a0264"),
             ("r1102_closeout", "44104391f9")):
    go(["cat-file", "-e", s + "^{commit}"])
    facts["ts_" + k] = go(["show", "-s", "--format=%ci", s])

# --- landed-by verifications ---
facts["n1_w273_landed_by"] = go(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w273_results.json"])
facts["w274_prereg_on_origin"] = go(["ls-tree", "origin/main", "--", "research/PERPETUAL_N1_W274_PREREG.md"], tolerant=True)
facts["w275_prereg_on_origin"] = go(["ls-tree", "origin/main", "--", "research/PERPETUAL_N1_W275_PREREG.md"], tolerant=True)
facts["w274_prereg_worktree_exists"] = os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W274_PREREG.md"))

# --- W274 seat commit files (seat MSG name machine-found, zero guessing) ---
seat_files = [x for x in go(["show", "--name-only", "--format=", "70b21a0264"]).splitlines() if x.strip()]
facts["seat_files"] = seat_files
seat_msgs = [x for x in seat_files if "w274" in x.lower() and "MSG" in x.upper()]
facts["seat_msg_initial_path"] = seat_msgs[0] if seat_msgs else None
if seat_msgs:
    name = os.path.basename(seat_msgs[0])
    facts["seat_msg_name"] = name
    for sub in ("fleet/inbox/processed", "fleet/inbox"):
        p = os.path.join(REPO, sub.replace("/", os.sep), name)
        if os.path.exists(p):
            facts["seat_msg_current_path"] = sub + "/" + name
            facts["seat_msg_landed_by"] = go(["log", "-1", "--format=%h", "--", sub + "/" + name], tolerant=True)
            break

# --- W274 seat receipt (bands/verdict/seed/hops machine-read for in-gate consumption) ---
rcp = json.load(open(os.path.join(REPO, "results", "_w274bmc_20261019_probe_receipt.json"), encoding="utf-8"))
facts["rcp_verdict"] = rcp.get("verdict")
facts["rcp_bands"] = rcp.get("bands")
facts["rcp_seed_admit"] = rcp.get("seed_admit")
facts["rcp_hops"] = {k: v for k, v in rcp.items() if "hop" in str(k).lower()}
facts["rcp_relation_asserts"] = rcp.get("relation_asserts")
facts["rcp_projection_leg4"] = rcp.get("projection_leg4") or rcp.get("leg4") or rcp.get("w275_projection")

# --- W273 fivekeys receipt (FULL-PRECISION machine-read; r1093 pit law) ---
fk = json.load(open(os.path.join(REPO, "results", "_r1102bmc_w273_fivekeys.json"), encoding="utf-8"))
facts["fk_top_keys"] = list(fk.keys())
for k in ("merged", "a_band", "skill_line", "ledger_identity", "checks", "all_pass"):
    facts["fk_" + k] = fk.get(k)
for k, v in fk.items():
    if "only" in str(k).lower():
        facts["fk_only_face_" + str(k)] = v

# --- n1_w273_results.json faces (finalize product, live-read) ---
res = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w273_results.json"), encoding="utf-8"))
facts["res_top_keys"] = list(res.keys())
facts["res_skill_line_v2_k_lift"] = res.get("skill_line_v2_k_lift")
npc = res.get("null_pool_cumulative") or {}
facts["res_null_pool_keys"] = list(npc.keys())
facts["res_se_mu_faces"] = {k: v for k, v in npc.items() if "se_mu" in str(k)}
res1 = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w272_results.json"), encoding="utf-8"))
facts["res_w272_se_mu_at_k596320"] = (res1.get("null_pool_cumulative") or {}).get("se_mu_at_k596320")

# --- sixgate receipt face (W273 pre-finalize correct-phase proof for anchors) ---
sg = json.load(open(os.path.join(REPO, "results", "_r1102bmc_w273_sixgate.json"), encoding="utf-8"))
facts["sg_top_keys"] = list(sg.keys())
facts["sg_all_pass"] = sg.get("all_pass")

# --- engine live-status + RAM live-measure (bm-c instance, THIS window) ---
r = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO)
facts["engine_rc"] = r.returncode
facts["engine_stdout_head"] = r.stdout[:400]
import psutil
facts["ram_available_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 2)

out = os.path.join(REPO, "results", "_w274bmc_facts.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print(json.dumps({k: facts[k] for k in ("w273_prereg_size", "w273_prereg_sha256_16", "head_tpl_blob",
      "w274_prereg_on_origin", "w274_prereg_worktree_exists", "rcp_verdict", "rcp_bands",
      "fk_all_pass", "ram_available_gb")}, ensure_ascii=False, indent=1))
print("FACTS-OK -> %s" % out)
