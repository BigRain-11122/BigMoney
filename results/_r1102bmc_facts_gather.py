# -*- coding: utf-8 -*-
# r1102 bm-c: W273 prereg derive FACTS GATHER (zero-transcription law; every face machine-read).
# Frozen W272 template face extracted HERE via python subprocess raw bytes (r1096 PS-pipeline
# corruption precedent: never Out-File). Blob-identity vs the W272 prereg FREEZE commit
# c049a57623 (PRE-backfill face per r1052/r1049 law; HEAD post-backfill twin disclosed NOT used).
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

# --- W272 prereg freeze commit (the frozen PRE-backfill template face) ---
facts["w272_prereg_commit"] = "c049a57623"
facts["w272_prereg_blob"] = go(["rev-parse", "c049a57623:research/PERPETUAL_N1_W272_PREREG.md"])
facts["w272_prereg_ts"] = go(["show", "-s", "--format=%ci", "c049a57623"])
facts["w272_prereg_subject"] = go(["show", "-s", "--format=%s", "c049a57623"])[:160]
facts["head_tpl_blob"] = go(["rev-parse", "HEAD:research/PERPETUAL_N1_W272_PREREG.md"])
r = subprocess.run([GIT, "show", "c049a57623:research/PERPETUAL_N1_W272_PREREG.md"], capture_output=True, cwd=REPO)
assert r.returncode == 0, "git show frozen face failed"
blob = r.stdout
facts["w272_prereg_size"] = len(blob)
facts["w272_prereg_sha256_16"] = hashlib.sha256(blob).hexdigest()[:16]
src = os.path.join(REPO, "results", "_w273bmc_w272_frozen_face.txt")
with open(src, "wb") as f:
    f.write(blob)
assert hashlib.sha256(open(src, "rb").read()).digest() == hashlib.sha256(blob).digest()
facts["frozen_face_written"] = src

# --- chain commit existence + timestamps (W272 cycle + W273 seat) ---
for k, s in (("w272_splice", "c99ee20a4"), ("w272_burn1", "434983cb65"), ("w272_burn2", "42549d6df1"),
             ("w272_finalize_estate", "d914e1a3db"), ("w273_seat", "39e1bb32f1"),
             ("r1101_closeout", "f10ecc00e8")):
    go(["cat-file", "-e", s + "^{commit}"])
    facts["ts_" + k] = go(["show", "-s", "--format=%ci", s])

# --- landed-by verifications ---
facts["n1_w272_landed_by"] = go(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w272_results.json"])
facts["w273_prereg_on_origin"] = go(["ls-tree", "origin/main", "--", "research/PERPETUAL_N1_W273_PREREG.md"], tolerant=True)

# --- W273 seat commit files (seat MSG name machine-found, zero guessing) ---
seat_files = [x for x in go(["show", "--name-only", "--format=", "39e1bb32f1"]).splitlines() if x.strip()]
facts["seat_files"] = seat_files
seat_msgs = [x for x in seat_files if "w273" in x.lower() and "MSG" in x.upper()]
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

# --- W272 fivekeys receipt (FULL-PRECISION machine-read; r1093 pit law) ---
fk = json.load(open(os.path.join(REPO, "results", "_r1100bmc_w272_fivekeys.json"), encoding="utf-8"))
facts["fk_top_keys"] = list(fk.keys())
for k in ("merged", "a_band", "skill_line", "ledger_identity", "checks", "all_pass"):
    facts["fk_" + k] = fk.get(k)
for k, v in fk.items():
    if "only" in str(k).lower():
        facts["fk_only_face_" + str(k)] = v

# --- n1_w272_results.json faces (finalize product, live-read) ---
res = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w272_results.json"), encoding="utf-8"))
facts["res_top_keys"] = list(res.keys())
facts["res_skill_line_v2_k_lift"] = res.get("skill_line_v2_k_lift")
npc = res.get("null_pool_cumulative") or {}
facts["res_null_pool_keys"] = list(npc.keys())
facts["res_se_mu_faces"] = {k: v for k, v in npc.items() if "se_mu" in str(k)}
res1 = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w271_results.json"), encoding="utf-8"))
facts["res_w271_se_mu_at_k594120"] = (res1.get("null_pool_cumulative") or {}).get("se_mu_at_k594120")

# --- engine live-status + RAM live-measure (bm-c instance, THIS window) ---
r = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO)
facts["engine_rc"] = r.returncode
facts["engine_stdout_head"] = r.stdout[:400]
import psutil
facts["ram_available_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 2)

out = os.path.join(REPO, "results", "_w273bmc_facts.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print(json.dumps(facts, ensure_ascii=False, indent=1))
print("FACTS-OK -> %s" % out)
