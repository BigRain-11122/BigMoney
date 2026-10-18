# -*- coding: utf-8 -*-
# r1090 bm-c: W268 prereg derive FACTS PROBE (machine-read, zero transcription; r1077 measured-counts law).
# Legs: (1) frozen-face extraction @ df55e3fab9 pre-backfill face + blob identity;
#       (2) chain-fact existence + commit timestamps (splice/finalize/seat);
#       (3) W267 finalize anchors re-read (fivekeys + n1_w267_results + probe receipt);
#       (4) needle baseline MEASURED on T0 (the W267 frozen face);
#       (5) simulated T1 (planned VMAP applied) -> post-leg needle candidates measured + line dumps;
#       (6) live RAM/GPU face (honest window face).
import io, os, subprocess, hashlib, json, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
FREEZE = "df55e3fab9"
SEAT_ORIGIN = "b9ad2f1119"
SEAT_MSG = "fleet/inbox/MSG-20261018-1229-bmc-w268-seat.md"

def git_out(args, as_bytes=False):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout if as_bytes else r.stdout.decode("utf-8", "replace").strip()

out = {}

# (1) frozen face extraction (byte-exact) + identity
blob = git_out(["show", "%s:research/PERPETUAL_N1_W267_PREREG.md" % FREEZE], as_bytes=True)
fc_path = os.path.join(REPO, "results", "_w268bmc_w267_frozen_face.txt")
io.open(fc_path, "wb").write(blob)
sha1 = hashlib.sha1(blob).hexdigest()
sha256_16 = hashlib.sha256(blob).hexdigest()[:16]
rp = git_out(["rev-parse", "%s:research/PERPETUAL_N1_W267_PREREG.md" % FREEZE])
hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W267_PREREG.md"])
T0 = blob.decode("utf-8")
out["frozen_face"] = {"bytes": len(blob), "sha1": sha1, "sha256_16": sha256_16,
                      "rev_parse_blob": rp, "disk_eq_blob": sha1 == rp,
                      "HEAD_twin_post_backfill": hb,
                      "sec78_placeholder_present": ("PLACEHOLDER" in T0 or "\u5360\u4f4d" in T0)}
print("FROZEN FACE bytes=%d sha1=%s sha256_16=%s rev-parse-match=%s HEAD-twin=%s" % (
    len(blob), sha1, sha256_16, sha1 == rp, hb))

# (2) chain facts
facts = {}
for label, sha in (("w267_prereg_freeze", FREEZE), ("w267_splice", "7b9e9377"),
                   ("w268_seat_closeout", SEAT_ORIGIN), ("w267_burn_a", "99166404f2"),
                   ("w267_burn_b", "eb5c74dbf7")):
    try:
        git_out(["cat-file", "-e", sha + "^{commit}"])
        facts[label] = git_out(["show", "-s", "--format=%h %ci", sha])
    except SystemExit:
        facts[label] = "MISSING"
fin_c = git_out(["log", "-1", "--format=%h %ci", "--", "results/perpetual_faces/n1_w267_results.json"])
facts["w267_finalize_commit"] = fin_c
try:
    git_out(["cat-file", "-e", "%s:%s" % (SEAT_ORIGIN, SEAT_MSG)])
    facts["seat_msg_on_origin"] = True
except SystemExit:
    facts["seat_msg_on_origin"] = False
out["chain_facts"] = facts
print("CHAIN FACTS: %s" % json.dumps(facts, ensure_ascii=False))

# (3) W267 finalize anchors (already machine-verified this window; re-read for the derive gates)
with open(os.path.join(REPO, "results", "_r1089bmc_w267_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w267_results.json"), encoding="utf-8") as f:
    res = json.load(f)
with open(os.path.join(REPO, "results", "_w268bmc_20261018_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
out["anchors"] = {
    "fk_all_pass": fk["all_pass"],
    "merged_mu_8dp": round(fk["merged"]["mu"], 8), "merged_sigma_8dp": round(fk["merged"]["sigma"], 8),
    "w267_only_mu_8dp": round(fk["w267_only"]["mu"], 8),
    "se_mu": fk["merged"]["se_mu_k585320"], "p95": fk["a_band"]["full_sharpe_p95"],
    "k_lift": fk["skill_line"]["k_lift_delta"], "n_eff_held": fk["skill_line"]["n_eff_held"],
    "line_pre_w267": fk["skill_line"]["line_pre_w267"], "line_merged": fk["skill_line"]["line_merged_585320"],
    "key1_gap": [c["value"] for c in fk["checks"] if c["name"] == "key1_w267_vs_merged_mu_gap"][0],
    "ledger_total": fk["ledger_identity"]["total"], "merged_k": fk["merged"]["k"],
    "res_n_eff_held_equal": res["skill_line_v2_k_lift"]["n_eff_held_equal"],
    "probe_verdict": pr["verdict"], "probe_bands": pr["bands"],
    "probe_rows_owner_bmc_ordinal": [pr["legs"]["leg0"]["rows"], pr["legs"]["leg0"]["owner_rows"],
                                     pr["legs"]["leg0"]["bmc_rows"], pr["legs"]["leg0"]["ordinal"]],
    "w269p_A": pr["legs"]["leg4"]["W269p_A_naive"], "w269p_B": pr["legs"]["leg4"]["W269p_B_naive"],
}
print("ANCHORS: %s" % json.dumps(out["anchors"], ensure_ascii=False))

# (4) needle baseline MEASURED on T0
NEEDLES_T0 = [
    "A-ext seed=602_701..604_700", "B-ext exit seed=604_701..604_900",
    "entry rng=**602_701+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57",
    "\u5e2d\u4f4d\u516c\u793a=MSG-20261018-1025-bmc-w267-seat \u5df2\u63a8 origin 942ebd5885 r565 \u5f8b\uff08bm-c r1086 \u5e2d\u00b7queue-head seat-first lane\uff09",
    "\u5e2d\u4f4d\u516c\u793a MSG-20261018-1025-bmc-w267-seat \u5148\u63a8 origin 942ebd5885 r565 \u5f8b",
    "\u6ce2\u53f7 267", "r1086 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1\uff1aorigin inbox \u96f6 W267 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d",
    "\u96f6 267 \u884c", "\u96f6 skip-ahead W268/W269 \u5e2d\u4f4d\u58f0\u660e",
    "\u6c60\u7b2c 265 \u679a", "\u7b2c 257 \u6ce2", "bm-c \u7b2c\u516b\u5341\u516d\u679a\u81ea\u6709\u6ce2",
    "probe leg0 bmc_rows=85 attempt-continuity face\uff08r1086 \u7a97\u7b97\u6cd5\u00b7bm-c own seat+bmc live rows 85 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bmc rows 85+\u5019\u9009=\u7b2c 86 \u679a EXACT",
    "engine_owner==bm-c 85 \u884c\u6ce8\u518c",
    "saturation_engine.py status live-read r1087\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\u00b7heartbeat \u65b0\u9c9c",
    "\u672c\u673a bm-c \u5b9e\u4f8b\u00b7heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1087 \u7a97\u00b7\u961f\u5217\u7a7a\u8f6c idle",
    "\u5f15\u64ce\u5b9e\u51b5\u6ce8\u8bb0\uff08\u672c\u673a bm-c \u5b9e\u4f8b heartbeat \u65b0\u9c9c r1087 \u7a97\u5b9e\u8bfb",
    "--wave 267/finalize --wave 267", "\u00a75.5 W268+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1",
    "engine_owner \u884c 256 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e",
    "prev=**\u5c4a\u65f6\u7a7a\u7a97\u6d3b\u94fe\u5934 derive \u7981\u624b\u6284**",
    "\uff08**A \u9762=STAIRCASE-AFFECTS-A", "\uff08\u89c1 \u00a75 item5\uff09\u3002",
    "entry rng seed=**602_701+j**", "\uff1bp=`BASELINE_P",
    "exit rng=**604_701+j**", "\uff1bp_exit=`P_EXIT=0.05`",
    "probe W268+ \u6295\u5f71 A naive 604_701..606_700 CLEAN hops=0", "never transcribe r587**\uff09",
    "5. **W268+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4", "verify at W268 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002",
    "\u672c\u4ef6=\u5e2d\u4f4d\u7a97\u540e\u9996\u7a97\u51bb\u7ed3\u4ef6\uff1b\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c",
    "\uff08gate0.5 \u7eff\u00b7\u7f16\u8f91\u5668 loud abort \u515c\u5e95\uff09**\u3002",
    "n1_w267", "n1_w266", "_w267bmc", "_w266bmc",
    "W267", "W266", "W265", "W264", "W263", "W262", "W261", "W260",
    "W259", "W258", "W257", "W256", "W255", "W254", "W253", "W252", "W251",
    "W268", "W269", "W268p", "W269p",
    "R268", "R269",
    "1,011,735", "585,320", "1,009,535", "583,120", "587,520", "996,335",
    "\u22120.09273858", "0.24507392", "\u22120.09878527", "0.3268", "\u5b9e\u5dee 0.0060",
    "602_701..604_700", "604_701..604_900", "604_701..606_700", "604_901..605_100",
    "602_501..602_700", "602_501..604_500", "602_701..602_900",
    "MSG-20261018-1025", "942ebd5885", "dc71ecc3f9", "007ec5e713", "595433d63c",
    "bc7cab9893", "18f6ffe931", "df55e3fab9", "7b9e9377",
    "10:2x", "07:0x",
    "\u5e2d\u4f4d\u65f6\u5373\u89e3\u9501", "waits-upstream ARMED", "GATED on", "finalize PENDING",
    "\u672c\u7a97 free RAM ~5GB", "3.4G VRAM", "\u8ba9\u8def\u6001",
    "W206/W211..W266", "W136..W266", "W2..W266", "\u5171\u4e8c\u767e\u516d\u5341\u4e94\u9762",
    "\u00a77 \u8303\u5f0f", "\u00a78 \u8303\u5f0f", "bm-c r1086 W266 \u00a77 \u8303\u5f0f", "bm-c r1086 W266 \u00a78 \u8303\u5f0f",
    "\u51bb\u7ed3\u7a97 26G bm-a", "\u51bb\u7ed3\u7a97 7G bm-c", "\u51bb\u7ed3\u7a97 3G bm-c", "\u51bb\u7ed3\u7a97 ~5G bm-c",
    "n_eff_held_equal 996,335", "line_pre_w266", "line_merged@K583,120",
    "\u2192W263 **0.000323**", "\u6295\u5f71 0.000321",
    "\u7b2c\u5341\u516d\u6b21\u8fde\u7eed A-hop", "\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed A-hop",
    "\u7b2c\u5341\u4e03\u6b21\u8fde\u7eed above-own-A", "\u7b2c\u5341\u516d\u6b21\u8fde\u7eed above-own-A",
    "\u8fde\u7eed\u5341\u516d\u6ce2", "SEVENTEENTH", "EIGHTEENTH", "hops=1", "hops=0",
]
counts = {n: T0.count(n) for n in NEEDLES_T0}
out["needle_counts_T0"] = counts
print("NEEDLE COUNTS T0:")
for n, c in counts.items():
    print("  %4d  %r" % (c, n))

# (5) simulated T1 with the PLANNED VMAP (rolled one generation; compound needles first)
P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"
VMAP = [
    ("A-ext seed=602_701..604_700", "A-ext seed=604_901..606_900"),
    ("B-ext exit seed=604_701..604_900", "B-ext exit seed=606_901..607_100"),
    ("entry rng=**602_701+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57", "entry rng=**604_901+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57"),
    ("\u5e2d\u4f4d\u516c\u793a=MSG-20261018-1025-bmc-w267-seat \u5df2\u63a8 origin 942ebd5885 r565 \u5f8b\uff08bm-c r1086 \u5e2d\u00b7queue-head seat-first lane\uff09",
     "\u5e2d\u4f4d\u516c\u793a=MSG-20261018-1229-bmc-w268-seat \u5df2\u63a8 origin b9ad2f1119 r565 \u5f8b\uff08bm-c r1089 \u5e2d\u00b7queue-head seat-first lane\uff09"),
    ("\u5e2d\u4f4d\u516c\u793a MSG-20261018-1025-bmc-w267-seat \u5148\u63a8 origin 942ebd5885 r565 \u5f8b",
     "\u5e2d\u4f4d\u516c\u793a MSG-20261018-1229-bmc-w268-seat \u5148\u63a8 origin b9ad2f1119 r565 \u5f8b"),
    ("\u6ce2\u53f7 267", "\u6ce2\u53f7 268"),
    ("r1086 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1\uff1aorigin inbox \u96f6 W267 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d", "r1089 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1\uff1aorigin inbox \u96f6 W268 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d"),
    ("\u96f6 267 \u884c", "\u96f6 268 \u884c"),
    ("\u96f6 skip-ahead W268/W269 \u5e2d\u4f4d\u58f0\u660e", "\u96f6 skip-ahead W269/W270 \u5e2d\u4f4d\u58f0\u660e"),
    ("\u6c60\u7b2c 265 \u679a", "\u6c60\u7b2c 266 \u679a"),
    ("\u7b2c 257 \u6ce2", "\u7b2c 258 \u6ce2"),
    ("bm-c \u7b2c\u516b\u5341\u516d\u679a\u81ea\u6709\u6ce2", "bm-c \u7b2c\u516b\u5341\u4e03\u679a\u81ea\u6709\u6ce2"),
    ("probe leg0 bmc_rows=85 attempt-continuity face\uff08r1086 \u7a97\u7b97\u6cd5\u00b7bm-c own seat+bmc live rows 85 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bmc rows 85+\u5019\u9009=\u7b2c 86 \u679a EXACT",
     "probe leg0 bmc_rows=86 attempt-continuity face\uff08r1089 \u7a97\u7b97\u6cd5\u00b7bm-c own seat+bmc live rows 86 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bmc rows 86+\u5019\u9009=\u7b2c 87 \u679a EXACT"),
    ("engine_owner==bm-c 85 \u884c\u6ce8\u518c", "engine_owner==bm-c 86 \u884c\u6ce8\u518c"),
    ("saturation_engine.py status live-read r1087\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\u00b7heartbeat \u65b0\u9c9c",
     "saturation_engine.py status live-read r1090\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\u00b7heartbeat \u65b0\u9c9c"),
    ("\u672c\u673a bm-c \u5b9e\u4f8b\u00b7heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1087 \u7a97\u00b7\u961f\u5217\u7a7a\u8f6c idle",
     "\u672c\u673a bm-c \u5b9e\u4f8b\u00b7heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1090 \u7a97\u00b7\u961f\u5217\u7a7a\u8f6c idle"),
    ("\u5f15\u64ce\u5b9e\u51b5\u6ce8\u8bb0\uff08\u672c\u673a bm-c \u5b9e\u4f8b heartbeat \u65b0\u9c9c r1087 \u7a97\u5b9e\u8bfb",
     "\u5f15\u64ce\u5b9e\u51b5\u6ce8\u8bb0\uff08\u672c\u673a bm-c \u5b9e\u4f8b heartbeat \u65b0\u9c9c r1090 \u7a97\u5b9e\u8bfb"),
    ("--wave 267/finalize --wave 267", "--wave 268/finalize --wave 268"),
    ("\u00a75.5 W268+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1", "\u00a75.5 W269+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1"),
    ("n1_w267", P2), ("n1_w266", "n1_w267"), (P2, "n1_w268"),
    ("_w267bmc", P3), ("_w266bmc", "_w267bmc"), (P3, "_w268bmc"),
    ("W267", P1), ("W266", "W267"), ("W265", "W266"), ("W264", "W265"), ("W263", "W264"),
    ("W262", "W263"), ("W261", "W262"), ("W260", "W261"), ("W259", "W260"), ("W258", "W259"),
    ("W257", "W258"), ("W256", "W257"), ("W255", "W256"), (P1, "W268"),
]
def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t
T1 = xf(T0)
out["t1_residuals"] = {
    "W268_plus_count": T1.count("W268+ \u6295\u5f71"),
    "W268p_count": T1.count("W268p"),
    "R268_count": T1.count("R268"),
    "P2_leftover": T1.count(P2), "P3_leftover": T1.count(P3), "P1_leftover": T1.count(P1),
    "W269_preblock_count": T1.count("W269"),
}
print("T1 SIM residuals: %s" % json.dumps(out["t1_residuals"], ensure_ascii=False))

# post-leg needle candidates MEASURED on simulated T1
POST_CAND = [
    "\uff08W267 \u5b9e\u6d4b\u952e **\u22120.09273858**\u00b7K=583,120 \u5408\u5e76\u6c60\u00b7W267-only \u5b9e\u6d4b **\u22120.09878527**\uff09",
    "W2..W267 \u5171\u4e8c\u767e\u516d\u5341\u4e94\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b",
    "W267-only vs merged \u5b9e\u5dee 0.0060 \u5728\u5e26\u5185",
    "\u952e **0.24507392**=W267 \u5408\u5e76\u6c60\u5b9e\u6d4b",
    "\u4e0e W267 A \u6863 p95\uff08**0.3268** \u5b9e\u6d4b\u951a\uff09",
    "\u952e W267 \u5b9e\u6d4b K-lift **0.0001**\u00b7line_merged@K583,120 **1.1958**\u00b7line_pre_w266 1.1957\u00b7n_eff_held_equal 996,335",
    "\u2192W264 **0.000323**\u2192W265 **0.000322**\u2192W266 **0.000321**\u2192W267 **0.000321**\u2192W268 \u6295\u5f71 0.000321\u3011",
    "W1..W267 \u5df2\u843d\u8d26 583,120 \u5b9e\u6d4b",
    "bm-c r1086 W267 \u00a77 \u8303\u5f0f", "bm-c r1086 W267 \u00a78 \u8303\u5f0f",
    "\u672c\u7a97 free RAM ~5GB",
    "\u00b7W244 \u51bb\u7ed3\u7a97 41.9G bm-a \u5b9e\u951a\u00b7W264 \u51bb\u7ed3\u7a97 26G bm-a \u5b9e\u951a\u00b7W265 \u51bb\u7ed3\u7a97 7G bm-c \u5b9e\u951a\u00b7W266 \u51bb\u7ed3\u7a97 3G bm-c \u5b9e\u951a\u00b7W267 \u51bb\u7ed3\u7a97 ~5G bm-c \u5b9e\u951a\uff09",
    "W267 finalize one-pass bm-c r1086",
]
print("POST-LEG CANDIDATES on simulated T1:")
for n in POST_CAND:
    print("  %4d  %r" % (T1.count(n), n[:80]))
out["post_candidates_T1"] = {n: T1.count(n) for n in POST_CAND}

# line dumps: the generation-sensitive lines from T1 (post-roll) for exact post-leg authoring
DUMP_PATS = [
    "\u5b9e\u6d4b\u952e", "\u5171\u4e8c\u767e\u516d\u5341", "\u5b9e\u5dee", "0.2450", "p95\uff08",
    "K-lift", "line_merged@", "line_pre_w", "\u5df2\u843d\u8d26", "\u51bb\u7ed3\u7a97",
    "free RAM", "\u8303\u5f0f", "n_eff_held_equal", "0.00032",
]
print("\n===== T1 LINE DUMPS (post-roll generation-sensitive lines) =====")
seen = set()
for ln in T1.split("\n"):
    if any(p in ln for p in DUMP_PATS) and ln not in seen:
        seen.add(ln)
        print("  | %s" % ln[:400])

# (6) live RAM/GPU face
try:
    import psutil
    ram_free_gb = round(psutil.virtual_memory().available / (1024 ** 3), 2)
except Exception as e:
    ram_free_gb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                        "--format=csv,noheader"], capture_output=True, text=True)
    gpu_face = r.stdout.strip()
except Exception as e:
    gpu_face = "ERR %r" % e
out["live_face"] = {"ram_free_gb": ram_free_gb, "gpu": gpu_face}
print("\nLIVE FACE: ram_free=%sGB gpu=%r" % (ram_free_gb, gpu_face))

io.open(os.path.join(REPO, "results", "_w268bmc_facts_probe.json"), "w", encoding="utf-8").write(
    json.dumps(out, indent=1, ensure_ascii=False))
print("\nFACTS PROBE DONE -> results/_w268bmc_facts_probe.json")
