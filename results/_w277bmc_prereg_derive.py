# -*- coding: utf-8 -*-
# r1113 bm-c: W277 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w276bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W276 prereg AT THE FREEZE COMMIT 770a47fa1f (git
# 770a47fa1f:research/PERPETUAL_N1_W276_PREREG.md, 23,554 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w277bmc_w276_frozen_face.txt by the r1113 derive window
# prep leg (python subprocess raw bytes; prep facts receipt results/_w277bmc_prep_facts.json);
# byte-verified: disk==blob sha256_16 5352c7cf343fc5e5, freeze blob sha1 daa87d01f7a9deb0238b5ddd3112498f64409c0d.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 46f0b537a01a8cb12e2bfeff5547431c23492341
# (27745 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1111
# W276 cycle (estate e781164e41). Deriving from the backfilled face would fabricate W277 sec.7/8
# from W276 measured numbers -- the r1049/r1052 precedent requires the 770a47fa1f frozen pre-run
# face. W277 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w277bmc_20261019_probe_receipt.json (bm-c r1112 window
#     authored+run live, seat rides origin c5f8b88f91 per r565 early-visibility law,
#     MSG-20261019-080x-bmc-w277-seat landed on origin; zero foreign W277 seat claims; zero
#     W278/W279 skip-claims). STAIRCASE CONTINUES: A naive 624_501..626_500 REFUSED at start
#     (registered W276 B band 624_501..624_700 sits INSIDE the naive A window) -> A first-clean
#     624_701..626_700 hops=1 (TWENTY-SIXTH consecutive A-hop, W276 prereg sec.5 item5
#     post-W276-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 624_701..624_900 lands INSIDE the own-wave W277 A first-clean window 624_701..626_700
#     (own-A reservation cascade) -> hop past own-A tail 626_700 -> 626_701..626_900 hops=1
#     (TWENTY-SEVENTH consecutive above-own-A landing); seed_admit FREE x2 (A base=624701 span=2000 /
#     B base=626701 span=200); leg0 rows=274 owner_rows=266 bmc_rows=95 ordinal=267; leg2
#     conflicts=0; leg3 origin_vacancy=true; W278p projection: A naive 626_701..628_700 CLEAN
#     hops=0 / B naive 626_901..627_100 CLEAN hops=0 but lands inside W278p A naive.
#   - upstream W276 finalize LANDED (bm-c r1111 window one-pass, n1_w276_results.json landed via
#     e781164e41 07:47:43, fivekeys 6/6 receipt results/_r1111bmc_w276_fivekeys.json + sec.7/8
#     backfilled): merged K=605,120 / ledger 1,031,535 EXACT (1,029,335+2,200) / merged mu
#     -0.09278451381544156 (8dp -0.09278451) / sigma 0.2450856226849218 (8dp 0.24508562) /
#     se_mu@K605,120 0.000315 (narrowing-held from W275 0.000316) / W276-only mu -0.08705886363636364
#     (8dp -0.08705886) / A p95 0.3088->0.305 (in-band) / K-lift +0.0001
#     (sign-flip positive) / n_eff_held 1,029,335 / line_pre_w276 1.1968 / line_merged@605,120
#     1.1969 / key1 only-vs-merged gap 0.005725650179077918 (4dp 0.0057) in-band; splice
#     354a645155 07:28:56 (r1111 window, engine batches df7dedfd07+627c4e10f2 tail-shard carried);
#     sixgate 39th consecutive PRE-FINALIZE ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded
#     narration faces; ALL gates machine-verify against the full-precision fivekeys/results jsons
#     (r1093 CODELY pit entry; live-read governs r587).
# Needle-count pre-flight evidence: results/_w277bmc_prep_facts.json (MEASURED live on T0 THIS
# window, r1077 measured-counts law; floors below match every measured count; zero-floor audit:
# every next-wave face measured 0 on T0).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1102 family):
# (1) finalize-window stamp roll: W276 finalize one-pass landed 07:4x (e781164e41 07:47:43); T0
#     carries the W275-era 05:3x stamps x4 (MEASURED live THIS build, r1077 law) -> POST_LEG x4.
# (2) date-cross N/A this generation (disclosed): the W277 seat receipt is SAME-DATE with the W276
#     seat receipt (both _*_20261019) -- the lowercase prefix chain rolls the receipt date correctly
#     with NO date-cross leg.
# (3) sec.5 item1 measured keys -> W276 actuals (n1_w276_results + fivekeys machine values):
#     merged mu -0.09278451 / K=605,120 / W276-only -0.08705886 (all full-precision
#     machine-verified in-gate).
# (4) sec.5 item1 diff face: W276-only vs merged TRUE diff = 0.0057 @4dp (measured
#     0.005725650179077918 full) in-band |d|<0.02.
# (5) sec.5 item2 sigma key 0.24507989 -> 0.24508562 (W276 merged-pool measured).
# (6) sec.5 item3 p95 anchor 0.3088 -> 0.305 (W276 A-band fivekeys measured).
# (7) sec.5 item4 K-lift chain: K-lift +0.0001 (W276 fivekeys key4, sign-flip positive) +
#     line_merged@K605,120 1.1969 + lowercase line_pre_w275 -> line_pre_w276 1.1968 (lowercase
#     NOT rolled by the W-roll, case-sensitive; r1102 heal (6) family) + n_eff_held_equal
#     1,027,135 -> 1,029,335.
# (8) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries the
#     stale projection on the W276 slot -> POST_LEG rewrites the tail with true history W271 0.000319 /
#     W272 0.000319 / W273 0.000318 / W274 0.000317 / W275 0.000316 / W276 0.000315 and appends
#     the W277 projection 0.000315.
# (9) sec.4 merged-pool anchor face: W1..W276 602,920 -> W1..W276 605,120 (W276 finalize landed).
# (10) sec.7/8 backfill paradigm rows: bm-c r1108 W275 -> bm-c r1111 W276 (cycle owner + wave roll).
# (11) RAM face live-measured THIS window: psutil 3 GB available (~3.9GB, probe-time read) +
#     nvidia-smi nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释 -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); the r1110
#     ~3.8GB face is stale.
# (12) low-RAM precedent ledger append: W276 freeze-window ~3.9G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; pre-shift needles land the MUST series
#     back on the TRUE labels W263..W275 + the new W276 anchor).
# (13) seat/provenance legs: MSG-20261019-055x-bmc-w276-seat/21b51a102/r1109 ->
#     MSG-20261019-080x-bmc-w277-seat/c5f8b88f91/r1112 (two live faces + block NEWs).
# (14) engine live-read faces r1110 -> r1113 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
# (15) estate-chain/timeline faces rolled two-window: the W276 cycle = prereg r1110 (770a47fa1f)
#     + splice/burn/sixgate/finalize/fivekeys/sec78 r1111 one-window (354a645155+e781164e41).
# DEFECT-BIRTHPLACE HEALS (builder-level, disclosed in the builder header):
# (16) A_hop_chain parenthetical refuser-band lineal defect fixed at birth (see builder heal (a)):
#     post-W-chain pass restores the parenthetical to the machine-receipt face (registered W276 B
#     band 624_501..624_700 refused the naive W277 A start -- receipt leg1
#     refuser_bands=[[624501,624700]]); the band needles had rolled it to the own-B value
#     (r1107-family lineal residue, disclosed + count-asserted).
# (17) r1110 heal (17) freezer-label unlag re-confirmed STRUCTURAL and re-applied (the label
#     sits one above the W-chain top and never rolls naturally; universe face rolls naturally).
import io, os, sys, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w277bmc_w276_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W277_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "daa87d01f7a9deb0238b5ddd3112498f64409c0d"   # freeze-commit face @ 770a47fa1f
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "770a47fa1f:research/PERPETUAL_N1_W276_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W276_PREREG.md"])
assert _hb == "46f0b537a01a8cb12e2bfeff5547431c23492341", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23554, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "5352c7cf343fc5e5", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("770a47fa1f", "354a645155", "df7dedfd07", "627c4e10f2", "e781164e41", "c5f8b88f91"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "354a645155"])    # 2026-10-19 07:28:56 +0800
_m = re.match(r"2026-10-19 07:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "07:%sx" % _m.group(1)[0]   # 07:2x
_fz = git_out(["show", "-s", "--format=%ci", "e781164e41"])    # 2026-10-19 07:47:43 +0800
assert _fz.startswith("2026-10-19 07:4"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "c5f8b88f91"])   # 2026-10-19 08:13:22 +0800
assert _st.startswith("2026-10-19 08:1"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w276_results.json"])
assert _fin_log == "e781164e41", "W276 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "c5f8b88f91"])
assert "MSG-20261019-080x-bmc-w277-seat.md" in _seat_files, "W277 seat MSG not carried by seat commit c5f8b88f91: %r" % _seat_files[:200]

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1111bmc_w276_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 605120, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09278451, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24508562, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k605120"], 6) == 0.000315, "se_mu drift: %r" % fk["merged"]["se_mu_k605120"]
assert round(fk["w276_only"]["mu"], 8) == -0.08705886, "w276-only mu drift: %r" % fk["w276_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.305, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1029335, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w276"], 4) == 1.1968, "line_pre drift: %r" % fk["skill_line"]["line_pre_w276"]
assert round(fk["skill_line"]["line_merged_605120"], 4) == 1.1969, "line_merged drift: %r" % fk["skill_line"]["line_merged_605120"]
assert fk["ledger_identity"]["total"] == 1031535 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w276_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0057 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w276_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1029335
assert round(res["skill_line_v2_k_lift"]["line_pre_w276"], 4) == 1.1968
assert round(res["skill_line_v2_k_lift"]["line_merged_605120"], 4) == 1.1969
assert round(res["null_pool_cumulative"]["se_mu_at_k605120"], 6) == 0.000315, "W276 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k602920"], 6) == 0.000316, "W275 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w277bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [624701, 626700] and pr["bands"]["B"] == [626701, 626900]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [624501, 626500], "jump_to": 624701,
                              "refuser_pts": [], "refuser_bands": [[624501, 624700]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [624701, 624900], "jump_to": 626701,
                              "refuser_pts": [], "refuser_bands": [[624701, 626700]]}]
assert l1["B_naive"] == [624701, 624900] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W276_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W276_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W274_W275_W276_bands_respected_A"] is True and _ra["W274_W275_W276_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 274 and _l0["owner_rows"] == 266 and _l0["bmc_rows"] == 95
assert _l0["ordinal"] == 267 and _l0["w276_finalize_landed"] is True
assert _l0["w276_finalize_anchors"]["ledger_total"] == 1031535
assert _l0["w276_finalize_anchors"]["merged_n"] == 605120
assert round(_l0["w276_finalize_anchors"]["skill_line_delta_k_lift"], 4) == 0.0001
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=624701 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=626701 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W278p_A_naive"] == "626701..628700"
assert pr["legs"]["leg4"]["W278p_B_naive"] == "626901..627100"
assert pr["legs"]["leg4"]["W278p_B_lands_inside_W278p_A_naive"] is True

# --- engine live-status gate (bm-c instance, THIS window; prereg engine-face honesty) ---
_r = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO)
assert _r.returncode == 0, "saturation_engine status rc=%d (engine face gate)" % _r.returncode
try:
    _eng = json.loads(_r.stdout)
    assert _eng.get("machine_id") == "bm-c" and _eng.get("alive_flag") is True
    assert _eng.get("burns_active") == [] and _eng.get("queue_next") == []
except Exception:
    assert '"alive_flag": true' in _r.stdout and '"burns_active": []' in _r.stdout \
        and '"queue_next": []' in _r.stdout, "engine face parse failed"

# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---
# r1113 window face: probe-time read = ~3.9GB available (MV lane drained, loop CPU-only; RAM
# fluctuates with resident daemons). Wide gate keeps idempotent re-runs green across the
# fluctuation (r1052 law); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %.2f" % _ram_free

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=622_501..624_500", "A-ext seed=624_701..626_700"),
    ("B-ext exit seed=626_701..626_900", "B-ext exit seed=626_701..626_900"),
    ("entry rng=**622_501+j**（与 A[j] 同源配对语义逐字", "entry rng=**624_701+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W277 seat published bm-c r1102, rides origin c5f8b88f91)
    ("席位公示=MSG-20261019-055x-bmc-w276-seat 已推 origin 21b51a102 r565 律（bm-c r1109 席·queue-head seat-first lane）",
     "席位公示=MSG-20261019-080x-bmc-w277-seat 已推 origin c5f8b88f91 r565 律（bm-c r1112 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261019-055x-bmc-w276-seat 先推 origin 21b51a102 r565 律",
     "席位公示 MSG-20261019-080x-bmc-w277-seat 先推 origin c5f8b88f91 r565 律"),
    # wave-number + vacancy faces
    ("波号 276", "波号 277"),
    ("r1109 席位窗实跑：origin inbox 零 W276 席位外机命中", "r1112 席位窗实跑：origin inbox 零 W277 席位外机命中"),
    ("零 276 行", "零 277 行"),
    ("零 skip-ahead W277/W278 席位声明", "零 skip-ahead W278/W279 席位声明"),
    ("池第 274 枚", "池第 275 枚"),
    # ordinals + own-wave faces
    ("第 266 波", "第 267 波"),
    ("bm-c 第九十五枚自有波", "bm-c 第九十六枚自有波"),
    ("probe leg0 bmc_rows=94 attempt-continuity face（r1109 窗算法·bm-c own seat+bmc live rows 94 实读）——freeze 时 live derive bmc rows 94+候选=第 95 枚 EXACT",
     "probe leg0 bmc_rows=95 attempt-continuity face（r1112 窗算法·bm-c own seat+bmc live rows 95 实读）——freeze 时 live derive bmc rows 95+候选=第 96 枚 EXACT"),
    ("engine_owner==bm-c 94 行注册", "engine_owner==bm-c 95 行注册"),
    # engine live-read faces (bm-c instance, r1104 window)
    ("saturation_engine.py status live-read r1110：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1113：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1110 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1113 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1110 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1113 窗实读"),
    # runner CLI wave
    ("--wave 276/finalize --wave 276", "--wave 277/finalize --wave 277"),
    # sec8 placeholder projection-label bump (W277+ face)
    ("§5.5 W277+ 投影承接机证", "§5.5 W278+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w276", P2), ("n1_w275", "n1_w276"), (P2, "n1_w277"),
    ("_w276bmc", P3), ("_w275bmc", "_w276bmc"), (P3, "_w277bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W276", P1), ("W275", "W276"), ("W274", "W275"), ("W273", "W274"), ("W272", "W273"), ("W271", "W272"),
    ("W270", "W271"), ("W269", "W270"), ("W268", "W269"), ("W267", "W268"), ("W266", "W267"),
    ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), (P1, "W277"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle probe r1104)
    "A-ext seed=622_501..624_500": 1,
    "B-ext exit seed=626_701..626_900": 0,
    "entry rng=**622_501+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261019-055x-bmc-w276-seat 已推 origin 21b51a102 r565 律（bm-c r1109 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261019-055x-bmc-w276-seat 先推 origin 21b51a102 r565 律": 1,
    "波号 276": 1,
    "r1109 席位窗实跑：origin inbox 零 W276 席位外机命中": 1,
    "零 276 行": 1,
    "零 skip-ahead W277/W278 席位声明": 1,
    "池第 274 枚": 1,
    "第 266 波": 1,
    "bm-c 第九十五枚自有波": 1,
    "probe leg0 bmc_rows=94 attempt-continuity face（r1109 窗算法·bm-c own seat+bmc live rows 94 实读）——freeze 时 live derive bmc rows 94+候选=第 95 枚 EXACT": 1,
    "engine_owner==bm-c 94 行注册": 1,
    "saturation_engine.py status live-read r1110：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1110 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1110 窗实读": 1,
    "--wave 276/finalize --wave 276": 1,
    "§5.5 W277+ 投影承接机证": 1,
    # lowercase rolls (measured on T0)
    "n1_w276": 4, "n1_w275": 6, "_w276bmc": 4, "_w275bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w277bmc_needle_probe.py r1104 window;
    # measured-counts law r1077)
    "W276": 44, "W275": 62, "W274": 4, "W273": 4, "W272": 3, "W271": 3, "W270": 3, "W269": 2, "W268": 2,
    "W265": 2, "W264": 2, "W263": 2, "W262": 1, "W260": 1, "W259": 1,
    # block-marker stability floors (raw template face; measured on T0)
    "engine_owner 行 265 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**622_501+j**": 1,
    "exit rng=**624_501+j**": 1,
    "probe W277+ 投影 A naive 624_501..626_500 CLEAN hops=0": 1,
    "5. **W277+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 1,020,535": 0,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
    "05:3x": 4, "05:2x": 2, "05:5x": 1,
    # zero-floors (absence assertions on T0; needle probe measured all == 0)
    "waits-upstream ARMED": 0, "GATED on": 0, "finalize PENDING": 0, "queue_depth": 0,
    "_w277bmc": 0, "n1_w277": 0, "W278p_": 0,
    "第 96 枚": 0, "第 267 波": 0, "第九十六枚": 0, "池第 275 枚": 0, "波号 277": 0, "零 277 行": 0,
    "engine_owner==bm-c 95 行注册": 0, "bmc_rows=95": 0, "bmc rows 95+候选": 0,
    "第二十七次连续 A-hop": 0, "第二十七次连续 above-own-A": 0, "连续二十六波": 0, "共二百七十五面": 0,
    "1,031,535": 0, "607,320": 0, "624_701..626_700": 0, "626_701..626_900": 0,
    "626_701..628_700": 0, "626_901..627_100": 0,
    "07:2x": 0, "07:4x": 0, "08:1x": 0,
    "770a47fa1f": 0, "354a645155": 0, "df7dedfd07": 0, "627c4e10f2": 0, "e781164e41": 0, "c5f8b88f91": 0,
    "−0.09278451": 0, "0.24508562": 0, "−0.08705886": 0, "0.305": 0,
    "实差 0.0057 在带内": 0, "line_pre_w276 1.1968": 0, "line_merged@K605,120": 0, "K=605,120": 0,
    "r1111 W276 §7 范式": 0, "（W276 注册+烧录+finalize 全落地）": 0,
    "MSG-20261019-080x": 0, "键 W276 实测 K-lift": 0, "本窗 free RAM ~4.0GB": 0,
    "622_501..624_500 CLEAN": 0,
    "617_901..618_100": 0, "620_101..622_100": 0, "611_501..611_700": 0, "618_101..620_100": 0,
    "611_501..611_700": 0, "617_901..619_900": 0,
    "12:2x": 0, "13:5x": 0, "14:0x": 0,
    "611_300+1": 0, "617_900+1": 0, "611_500+1": 0,
    # NOTE (fail-closed discipline): 第二十五次连续 A-hop (T0=3) / 第二十六次连续 above-own-A
    # (T0=2) / 第二十六次连续 A-hop (T0=3) / 连续二十五波 (T0=1) / 共二百七十四面 (T0=1) are NOT
    # zero-floors on this T0 -- they are block-interior current-wave faces (probe: outside=0
    # for the band/ordinal set) + POST_LEG faces, handled by block replace + POST_LEG;
    # banned on T2 via MUST_NOT instead.
}

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

for o, f in VMAP_FLOORS.items():
    c = T0.count(o)
    if f == 0:
        if c:
            raise SystemExit("VMAP FLOOR(0) FAIL: %r count=%d (expect 0)" % (o, c))
        continue
    if c < f:
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))

T1 = xf(T0)

# ---------------- post-roll correction legs (needles exist only in T1 after the rolls) ----------------
VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (1)): W276 finalize one-pass landed 07:4x (e781164e41
    # 07:47:43); T1 carries the W275-era 05:3x stamps x4 (MEASURED live THIS build, r1077 law)
    ("05:3x", "07:4x", 4),
    # date-cross N/A this generation (heal (2), disclosed): W277 seat receipt same-date 20261019
    # with the W276 seat receipt -- lowercase prefix chain rolls the receipt date correctly with
    # NO date-cross leg.
    # sec.5 item1 measured keys -> W276 actuals (n1_w276_results + fivekeys machine values)
    ("（W276 实测键 **−0.09280541**·K=602,920 合并池·W276-only 实测 **−0.09398255**）",
     "（W276 实测键 **−0.09278451**·K=605,120 合并池·W276-only 实测 **−0.08705886**）", 1),
    ("W2..W276 共二百七十四面实测 mu 稳定先例", "W2..W276 共二百七十五面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (4)): TRUE W276 diff = 0.0057 @4dp (measured
    # 0.005725650179077918 full), in-band
    ("W276-only vs merged 实差 0.0012 在带内", "W276-only vs merged 实差 0.0057 在带内", 1),
    # sec.5 item2 sigma key (heal (5))
    ("键 **0.24507989**=W276 合并池实测", "键 **0.24508562**=W276 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (6))
    ("与 W276 A 档 p95（**0.3088** 实测锚）", "与 W276 A 档 p95（**0.305** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (7): lowercase line_pre_w275 NOT rolled by the
    # W-roll; true W276 anchors K-lift +0.0001 sign-flip + line_merged@K605,120 1.1969 +
    # line_pre_w276 1.1968 + n_eff_held 1,029,335)
    ("键 W276 实测 K-lift **−0.0001**·line_merged@K602,920 **1.1967**·line_pre_w275 1.1968·n_eff_held_equal 1,027,135",
     "键 W276 实测 K-lift **+0.0001**·line_merged@K605,120 **1.1969**·line_pre_w276 1.1968·n_eff_held_equal 1,029,335", 1),
    # se_mu chain true-history correction (heal (8); W276 fivekeys key5 measured 0.000315
    # narrowing-held from W275 0.000316)
    ("→W271 **0.000319**→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000316**→W277 投影 0.000316】",
     "→W271 **0.000319**→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000315**→W277 投影 0.000315】", 1),
    # sec.4 merged-pool anchor face (heal (9): W276 finalize landed)
    ("W1..W276 已落账 602,920 实测", "W1..W276 已落账 605,120 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W276 cycle (heal (10): bm-c r1111; OLD faces are
    # POST-VMAP faces -- the raw T0' W275-cycle rows already shifted W275->W276 before this leg
    # fires; the leg fixes the window number r1108->r1111, measured post-VMAP count=1)
    ("bm-c r1108 W276 §7 范式", "bm-c r1111 W276 §7 范式", 1),
    ("bm-c r1108 W276 §8 范式", "bm-c r1111 W276 §8 范式", 1),
    # RAM face live-measured THIS window (heal (11)): psutil 3.9 available (~3.9GB) + nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释
    # -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); honest window face
    # updated from the r1110 ~3.8GB face
    ("本窗 free RAM ~3.8GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~3.9GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W276 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- pre-shift needles land the MUST series on the TRUE labels W263..W275;
    # this leg restores the POST-VMAP shifted ledger and appends the true W276 anchor
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚·W275 冻结窗 ~4.0G bm-c 实锚·W276 冻结窗 ~3.8G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚·W276 冻结窗 ~3.9G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 266 注册在册（表尾 W277 行【bm-c r1111 五面冻结 splice 354a645155 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 9th gen）】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w276/ 12/12·ledger append df7dedfd07+627c4e10f2】"
    "·**W276 finalize 已落地**【n1_w276_results.json 机读·净账本锚头 1,031,535·K=605,120 合并池·W276 finalize one-pass bm-c r1111 窗 07:4x·estate chain r1110/r1111 W276 全周期 770a47fa1f+354a645155+e781164e41】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1112 席位 MSG-20261019-080x-bmc-w277-seat 已推 origin c5f8b88f91"
    "·probe receipt _w277bmc_20261019 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 95+候选=第 96 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1112 席位窗 2026-10-19 08:1x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W277=bm-c own-wave window per chain-order law（W274 bm-c→W275 bm-c→W276 bm-c→W277 bm-c own-turn rotation·MSG-080x owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W276 N1 注册全部落地**【W276=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W276**"
    "【净账本锚头 **1,031,535**·K=605,120 合并池·n1_w276_results.json 机读·W276 finalize one-pass bm-c r1111 窗 07:4x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W276 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=605,120+2,200（本波）=**607,320 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十六次连续 A-hop）**："
    "A 面算术续带 624_501..626_500（自注册 W276 A 尾 624_500 续）"
    "在席位窗宇宙（post-W276-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W276 B 带 624_501..624_700 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W276 prereg §5 item5 post-W276-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W276 B 尾 624_700→A first-clean **624_701..626_700**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（624_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 624_501..626_500→jump 624_701·refuser band 624_501..624_700〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W276_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；"
    "**B-ext exit seed=626_701..626_900**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第二十七次连续 above-own-A 落位）**："
    "B naive 续带 624_701..624_900（自注册 W276 B 尾 624_700+1 续）"
    "在席位窗宇宙（post-W276-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 624_701..624_900 落本波 A first-clean 窗 624_701..626_700 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 624_701..626_700**（1 hop）"
    "→**1 hop** 落位 **626_701..626_900**·**B 落位 base==本波 A 窗尾+1（626_700+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W276 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W277 A naive 624_501..626_500 将被注册 W276 B 带拒（staircase affects A 承袭·第二十六次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R278：W277 带（A 624_701..626_700/B 626_701..626_900）注册后对 W278+ 的拒面影响=W277 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**624_701+j**（法典 §4 W277 行 A=624_701..626_700·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十六次连续 A-hop）**："
    "A 算术续带 624_501..626_500（自注册 W276 A 尾 624_500 续）"
    "在席位窗宇宙（post-W276-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W276 B 带 624_501..624_700 落 naive A 窗内=W276 prereg §5 item5 post-W276-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W276 B 尾 624_700→A first-clean 624_701..626_700·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（624_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W276_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**626_701+j**（法典 §4 W277 行 B=626_701..626_900·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 624_701..624_900（自注册 W276 B 尾 624_700+1 续）"
    "在席位窗宇宙（post-W276-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 624_701..626_700 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 624_701..626_700→1 hop 落位 626_701..626_900·"
    "**B 落位 base==本波 A 窗尾+1（626_700+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第二十七次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W276 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W278+ 投影 A naive 626_701..628_700 CLEAN hops=0（零 live refusers）/ B naive 626_901..627_100 CLEAN hops=0 "
    "**但落 naive W277 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 626_701..628_700 CLEAN·hops=0——**post-W277-REGISTERED 预披露：naive W277 A 起点将被注册 W277 B 带 626_701..626_900 拒=staircase affects A 第二十七次连续 A-hop 预期**；"
    "投影 B naive 626_901..627_100 clean 但落 naive W277 A 窗 626_701..628_700 内——"
    "**above-own-A 承袭面：W277 B 626_701..626_900 落本波 A 窗之上〔第二十六次连续〕·W277 A 面 1-hop=staircase affects A〔第二十六次连续〕·"
    "W279 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W277 B 带将拒 naive W277 A 窗仅当重叠——"
    "**W278 freezer 承接面强制注记：须在 post-W277 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W278+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 626_701..628_700 **CLEAN**（hops=0·pre-W277 宇宙零 live refusers）——"
    "**post-W277-REGISTERED 预披露：naive W277 A 起点将被注册 W277 B 带 626_701..626_900 拒（staircase-affects-A 第二十七次连续 A-hop 预期）**；"
    "B naive **626_901..627_100 CLEAN（hops=0）但落投影 A 窗 626_701..628_700 内**（W278p_B_lands_inside_W278p_A_naive=true——"
    "**staircase face 延续**：W277 A 624_701..626_700+B 626_701..626_900 注册后 naive W277 A 窗起点即被注册 W277 B 带拒（staircase affects A 承袭·第二十七次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W277 宇宙 live re-derive 必变·禁转录投影）；"
    "**W277 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277=A/B 双 1-hop 形态连续二十六波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W277 冻结方必须在 post-W277 注册宇宙重 derive 且 derive B 时预留本波 A 窗 624_701..626_700+本波 B 带 626_701..626_900"
    "——leg2 律/E36 卡·W141 先例；verify at W278 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w277bmc_freeze_edits.py"
    "（按 _w276bmc_freeze_edits.py 模板派生·gate0.5 自查 W276 行+W276 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1110/r1111 W276 全周期先例实时间线：prereg 770a47fa1f 落于 r1110 窗·splice 354a645155 落于 r1111 执行窗 @@SPLICE_T@@——"
    "**W277 freeze 面：W276 own-wave finalize 已落地=席位时即解锁——席位 r1112 窗+prereg r1113 窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 265 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**622_501+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**624_501+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W277+ 投影 A naive 624_501..626_500 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W277+ 投影（probe 机证 leg4", "verify at W277 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
]

T2 = T1
for name, sm, em in BLOCKS:
    c = T2.count(sm)
    assert c == 1, "BLOCK %s start-marker count=%d (expect 1)" % (name, c)
    i = T2.index(sm)
    j = T2.find(em, i)
    assert j > i, "BLOCK %s end-marker not found after start" % name
    j += len(em)
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", SPLICE_T)
    T2 = T2[:i] + NEWTXT + T2[j:]
    assert NEWTXT in T2, "BLOCK %s NEW not inserted" % name

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W277", "research/PERPETUAL_N1_W277_PREREG.md",
    "624_701..626_700", "626_701..626_900", "605,120", "1,031,535", "605,120", "K=605,120",
    "n1_w277_results.json", "n1_w276_results.json", "MSG-20261019-080x-bmc-w277-seat", "c5f8b88f91",
    "池第 275 枚", "第九十六枚", "第 267 波", "第 96 枚",
    "STAIRCASE-AFFECTS-A", "第二十六次连续 A-hop", "第二十七次连续 above-own-A",
    "_w277bmc_20261019", "--wave 277/finalize --wave 277",
    "W276 finalize one-pass bm-c r1111", "n_eff_held_equal 1,029,335",
    "−0.09278451", "0.24508562", "−0.08705886", "（**0.305** 实测锚）",
    "键 W276 实测 K-lift **+0.0001**", "line_merged@K605,120 **1.1969**", "line_pre_w276 1.1968",
    "实差 0.0057 在带内", "共二百七十五面", "W2..W276", "W1..W276",
    "engine_owner==bm-c 95 行注册", "engine_owner 行 266 注册在册",
    "probe leg0 bmc_rows=95 attempt-continuity face（r1112 窗算法·bm-c own seat+bmc live rows 95 实读）",
    "bm-c 循环班 r1112 席位窗", "本窗 free RAM ~3.9GB", "本机 bm-c 实例",
    "W277=bm-c own-wave window per chain-order law",
    "770a47fa1f", "354a645155", "df7dedfd07", "627c4e10f2", "e781164e41",
    "W278+ 投影", "W278p_B_lands_inside_W278p_A_naive", "verify at W278 prereg",
    "_w277bmc_freeze_edits.py", "_w276bmc_freeze_edits.py 模板派生",
    "bm-c r1111 W276 §7 范式", "bm-c r1111 W276 §8 范式",
    "（上游 W276 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "（W276 注册+烧录+finalize 全落地）",
    "W206/W211..W276 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",
    "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚", "W274 冻结窗 ~4.0G bm-c 实锚", "W275 冻结窗 ~3.8G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R278：W277 带",
    "→W271 **0.000319**→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000315**→W277 投影 0.000315】",
    "624_700+1", "626_700+1", "626_701..626_900",
    "A_staircase_hop_past_W276_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 277", "零 277 行", "零 skip-ahead W278/W279 席位声明",
    "07:4x", "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1113：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1113 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1113 窗实读",
    "nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释",
    "r1112 席位窗实跑：origin inbox 零 W277 席位外机命中",
    "results/p2cal_ext/n1_w276/ 12/12",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=611_501", "B-ext exit seed=613_501",
    "622_501..624_500", "617_901..618_100", "613_301..613_500", "613_301..615_300", "613_701..613_700",
    "620_101..622_100 CLEAN", "620_101..622_100", "618_101..620_100", "617_901..618_100", "620_101..622_100", "611_501..611_700",
    "618_101..620_100", "611_501..611_700", "617_901..619_900",
    "624_501..626_500 CLEAN", "624_701..624_900 CLEAN",
    "GATED on", "finalize PENDING", "queue_depth",
    "602,920", "**605,120 投影**", "line_merged@K602,920", "K=602,920",
    "−0.09280541", "0.24507989", "−0.09398255", "**0.3088**", "实差 0.0012 在带内",
    "17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x",
    "MSG-20261019-055x", "21b51a102", "bf4bbbde1e", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",
    "bmc_rows=94", "bmc rows 94+候选", "第 95 枚", "第 266 波", "第九十五枚",
    "engine_owner==bm-c 94 行注册",
    "r1109 席位窗实跑", "r1101 窗算法",
    "95%·7.9G VRAM",
    "W277p_", "W277p_",
    "line_pre_w271", "键 W275 实测 K-lift",
    "verify at W277 prereg",
    "W277+ 投影", "W276+ 投影", "W275+ 投影",
    "第二十五次连续 A-hop", "第二十二次连续 above-own-A", "第二十六次连续 above-own-A", "连续二十五波", "共二百七十四面",
    "n1_w275_results.json", "n1_w269_results.json", "n1_w268_results.json",
    "W2..W275", "W136..W275", "W1..W275",
    "波号 276", "零 276 行",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",
    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",
    "622_500+1", "617_900+1", "611_500+1", "617_900+1", "611_300+1",
    "12:2x", "13:5x", "14:0x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W278+ 投影") == 3, "W277+ count=%d (expect 3 = §5.5 rolled + b_claim_proj + b5)" % T2.count("W278+ 投影")
assert T2.count("W277+ 投影") == 0, "W277+ count=%d (expect 0)" % T2.count("W277+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("第二十六次连续 A-hop") == 3, "A21 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("第二十六次连续 A-hop")
assert T2.count("第二十七次连续 A-hop") == 3, "A22 count=%d (expect 3 = b5 x2 + b_claim_proj)" % T2.count("第二十七次连续 A-hop")
assert T2.count("第二十七次连续 above-own-A") == 2, "B22 count=%d (expect 2 = b_band + b3_b)" % T2.count("第二十七次连续 above-own-A")
assert T2.count("第二十六次连续 above-own-A") == 0, "B21 count=%d (expect 0)" % T2.count("第二十六次连续 above-own-A")
assert T2.count("连续二十六波") == 1, "21-wave count=%d (expect 1 = b5 NEW)" % T2.count("连续二十六波")
assert T2.count("624_701..626_700") >= 5, "own-A count=%d (expect >=5)" % T2.count("624_701..626_700")
assert T2.count("626_701..626_900") >= 4, "own-B count=%d (expect >=4)" % T2.count("626_701..626_900")
assert T2.count("626_701..626_900") >= 3, "reg-W276-B count=%d (expect >=3)" % T2.count("626_701..626_900")
assert T2.count("624_701..624_900") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("624_701..624_900")
assert T2.count("624_501..626_500") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("624_501..626_500")
assert T2.count("626_701..628_700") == 5, "W277p-A count=%d (expect 5 = b_claim_proj x3 + b5 x2)" % T2.count("626_701..628_700")
assert T2.count("626_901..627_100") == 3, "W277p-B count=%d (expect 3 = b_claim_proj x2 + b5)" % T2.count("626_901..627_100")
assert T2.count("席位时即解锁") == 2, "unlock count=%d (expect 2)" % T2.count("席位时即解锁")
assert T2.count("_w277bmc_20261019") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w277bmc_20261019")
assert T2.count("1,031,535") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,031,535")
# n_eff_held face honest update (r1093 full-precision law): the ONLY 1,029,335 in the output
# is the sec.5 item4 n_eff_held_equal anchor = the W276 fivekeys measured value (the canon
# r1102 window left this sub-face stale at the W275-era 1,020,535; healed forward here)
assert T2.count("1,029,335") == 1, "n_eff_held count=%d (expect 1 = sec.5 item4 honest anchor only)" % T2.count("1,029,335")
assert T2.count("605,120") >= 3, "merged-K count=%d (expect >=3)" % T2.count("605,120")
assert T2.count("（占位·finalize one-pass 后回填") == 1, "sec7 placeholder count=%d (expect 1)" % T2.count("（占位·finalize one-pass 后回填")
assert T2.count("（占位·finalize 同窗回填") == 1, "sec8 placeholder count=%d (expect 1)" % T2.count("（占位·finalize 同窗回填")
assert T2.count("第 96 枚") == 2, "own-ordinal count=%d (expect 2 = leg + b_title)" % T2.count("第 96 枚")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W277 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 354a645155 @ " + SPLICE_T + " | finalize estate: e781164e41 @ 07:4x | seat: c5f8b88f91 @ 08:1x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~3.9GB written, MV 车道已收官 idle) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == daa87d01f7a9deb0238b5ddd3112498f64409c0d @ 770a47fa1f (frozen pre-run face; HEAD post-backfill twin 46f0b537 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
