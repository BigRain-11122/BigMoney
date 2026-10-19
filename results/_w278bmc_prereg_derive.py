# -*- coding: utf-8 -*-
# r1116 bm-c: W278 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w277bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W277 prereg AT THE FREEZE COMMIT e0bc4a0ddd (git
# e0bc4a0ddd:research/PERPETUAL_N1_W277_PREREG.md, 23,593 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w278bmc_w277_frozen_face.txt by the r1115 PREP window
# (python subprocess raw bytes; prep facts receipt results/_w278bmc_prep_facts.json);
# byte-verified: disk==blob sha256_16 45ee1de94c7d36fd, freeze blob sha1 e5d12b12da03a799a88bd980cf8566b2b1eff5ba.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 78571eb16e279d7b6f316b04aef0960fac37283f
# (27,848 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the
# r1114-continuation W277 cycle (estate 0502c722ac). Deriving from the backfilled face would
# fabricate W278 sec.7/8 from W277 measured numbers -- the r1049/r1052 precedent requires the
# e0bc4a0ddd frozen pre-run face. W278 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w278bmc_20261019_probe_receipt.json (bm-c r1114-continuation
#     window authored+run live, seat rides origin b187aa6214 per r565 early-visibility law,
#     MSG-20261019-102x-bmc-w278-seat landed on origin; zero foreign W278 seat claims; zero
#     W279/W280 skip-claims). STAIRCASE CONTINUES: A naive 626_701..628_700 REFUSED at start
#     (registered W277 B band 626_701..626_900 sits INSIDE the naive A window) -> A first-clean
#     626_901..628_900 hops=1 (TWENTY-SEVENTH consecutive A-hop, W277 prereg sec.5 item5
#     post-W277-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 626_901..627_100 lands INSIDE the own-wave W278 A first-clean window 626_901..628_900
#     (own-A reservation cascade) -> hop past own-A tail 628_900 -> 628_901..629_100 hops=1
#     (TWENTY-EIGHTH consecutive above-own-A landing); seed_admit FREE x2 (A base=626901 span=2000 /
#     B base=628901 span=200); leg0 rows=275 owner_rows=267 bmc_rows=96 ordinal=268; leg2
#     conflicts=0; leg3 origin_vacancy=true; W279p projection: A naive 628_901..630_900 CLEAN
#     hops=0 / B naive 629_101..629_300 CLEAN hops=0 but lands inside W279p A naive.
#   - upstream W277 finalize LANDED (bm-c r1114-continuation window one-pass, n1_w277_results.json
#     landed via 0502c722ac 10:35:34, fivekeys 6/6 receipt results/_r1114bmc_w277_fivekeys.json +
#     sec.7/8 backfilled): merged K=607,320 / ledger 1,033,735 EXACT (1,031,535+2,200) / merged mu
#     -0.09277043683725218 (8dp -0.09277044) / sigma 0.24508693698115214 (8dp 0.24508694) /
#     se_mu@K607,320 0.000314 (narrowing-held from W276 0.000315) / W277-only mu -0.08889849999999999
#     (8dp -0.08889850) / A p95 0.305->0.3095 (in-band) / K-lift +0.0000
#     (held-flat-at-zero) / n_eff_held 1,031,535 / line_pre_w277 1.197 / line_merged@607,320
#     1.197 / key1 only-vs-merged gap 0.0038719368372521906 (4dp 0.0039) in-band; splice
#     9e53371814 09:57:42 (r1114-continuation window, engine batches 0df07c846b+644b4f8459);
#     sixgate 40th consecutive PRE-FINALIZE ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded
#     narration faces; ALL gates machine-verify against the full-precision fivekeys/results jsons
#     (r1093 CODELY pit entry; live-read governs r587).
# Needle-count pre-flight evidence: results/_w278bmc_prep_facts.json (MEASURED on T0 by the r1115
# PREP window, r1077 measured-counts law; floors below match every measured count; zero-floor
# audit: every next-wave face measured 0 on T0).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1102 family):
# (1) finalize-window stamp roll: W277 finalize one-pass landed 10:3x (0502c722ac 10:35:34); T0
#     carries the W276-era 07:4x stamps x4 (MEASURED by the r1115 prep) -> POST_LEG x4.
# (2) date-cross N/A this generation (disclosed): the W278 seat receipt is SAME-DATE with the W277
#     seat receipt (both _*_20261019) -- the lowercase prefix chain rolls the receipt date correctly
#     with NO date-cross leg.
# (3) sec.5 item1 measured keys -> W277 actuals (n1_w277_results + fivekeys machine values):
#     merged mu -0.09277044 / K=607,320 / W277-only -0.08889850 (all full-precision
#     machine-verified in-gate).
# (4) sec.5 item1 diff face: W277-only vs merged TRUE diff = 0.0039 @4dp (measured
#     0.0038719368372521906 full) in-band |d|<0.02.
# (5) sec.5 item2 sigma key 0.24508562 -> 0.24508694 (W277 merged-pool measured).
# (6) sec.5 item3 p95 anchor 0.305 -> 0.3095 (W277 A-band fivekeys measured).
# (7) sec.5 item4 K-lift chain: K-lift +0.0000 (W277 fivekeys key4, held-flat-at-zero) +
#     line_merged@K607,320 1.197 + lowercase line_pre_w276 -> line_pre_w277 1.197 (lowercase
#     NOT rolled by the W-roll, case-sensitive; r1102 heal (6) family) + n_eff_held_equal
#     1,029,335 -> 1,031,535.
# (8) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries the
#     stale projection on the W277 slot -> POST_LEG rewrites the tail with true history W272 0.000319 /
#     W273 0.000319 / W274 0.000318 / W275 0.000317 / W276 0.000316 / W277 0.000314 and appends
#     the W278 projection 0.000314.
# (9) sec.4 merged-pool anchor face: W1..W277 605,120 -> W1..W277 607,320 (W277 finalize landed).
# (10) sec.7/8 backfill paradigm rows: bm-c r1111 W276 -> bm-c r1114-continuation W277 (cycle owner
#     + wave roll).
# (11) RAM face live-measured THIS window: psutil 4 GB available (~4.5GB, probe-time read) +
#     nvidia-smi nvidia-smi 实读 0%·1.8G VRAM 占用·MV 车道已收官 GPU idle 回释 -- GPU=gen-only lane idle (MV lane drained, loop CPU-only; jman/female-lead
#     LoRA dataset lines = night-priority standing queue); the r1113 ~3.9GB face is stale. RAM
#     honest-window gate widened 6.0->16.0 (disclosed heal: Monday-morning live face above the
#     r1113-era cap; idempotence law r1052 preserved).
# (12) low-RAM precedent ledger append: W277 freeze-window ~4.5G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; pre-shift needles land the MUST series
#     back on the TRUE labels W263..W276 + the new W277 anchor).
# (13) seat/provenance legs: MSG-20261019-080x-bmc-w277-seat/c5f8b88f91/r1112 ->
#     MSG-20261019-102x-bmc-w278-seat/b187aa6214/r1114-continuation (two live faces + block NEWs).
# (14) engine live-read faces r1113 -> r1116 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
# (15) estate-chain/timeline faces rolled: the W277 cycle = prereg r1113 (e0bc4a0ddd)
#     + splice/burn/sixgate/finalize/fivekeys/sec78 r1114-continuation one-window
#     (9e53371814+0502c722ac; engine batches 0df07c846b+644b4f8459).
# DEFECT-BIRTHPLACE HEALS (builder-level, disclosed in the builder header):
# (16) A_hop_chain parenthetical refuser-band machine face verified at birth (see builder heal
#     (a), probe-verified): the single blanket roll lands the parenthetical on the
#     machine-receipt face (registered W277 B band 626_701..626_900 refused the naive W278 A
#     start -- receipt leg1 refuser_bands=[[626701,626900]]); the own-B lineal-defect face
#     (628_901..629_100) and the stale prior face (624_501..624_700) are both count-asserted
#     absent, disclosed + fail-closed.
# (17) freezer-label unlag re-confirmed STRUCTURAL and re-applied (the label sits one above the
#     W-chain top and never rolls naturally; universe face rolls naturally).
import io, os, sys, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w278bmc_w277_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W278_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "e5d12b12da03a799a88bd980cf8566b2b1eff5ba"   # freeze-commit face @ e0bc4a0ddd
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "e0bc4a0ddd:research/PERPETUAL_N1_W277_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W277_PREREG.md"])
assert _hb == "78571eb16e279d7b6f316b04aef0960fac37283f", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")  # heal (h) r1093: CRLF disk face -> LF git-object face (sim byte-identity)
assert len(T0.encode("utf-8")) == 23593, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "45ee1de94c7d36fd", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("e0bc4a0ddd", "9e53371814", "0df07c846b", "644b4f8459", "0502c722ac", "b187aa6214"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "9e53371814"])    # 2026-10-19 09:57:42 +0800
_m = re.match(r"2026-10-19 09:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "09:%sx" % _m.group(1)[0]   # 09:5x
_fz = git_out(["show", "-s", "--format=%ci", "0502c722ac"])    # 2026-10-19 10:35:34 +0800
assert _fz.startswith("2026-10-19 10:3"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "b187aa6214"])   # 2026-10-19 10:35:34 +0800
assert _st.startswith("2026-10-19 10:3"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w277_results.json"])
assert _fin_log == "0502c722ac", "W277 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "b187aa6214"])
assert "MSG-20261019-102x-bmc-w278-seat.md" in _seat_files, "W278 seat MSG not carried by seat commit b187aa6214: %r" % _seat_files[:200]

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1114bmc_w277_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 607320, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09277044, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24508694, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k607320"], 6) == 0.000314, "se_mu drift: %r" % fk["merged"]["se_mu_k607320"]
assert round(fk["w277_only"]["mu"], 8) == -0.0888985, "w277-only mu drift: %r" % fk["w277_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3095, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1031535, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w277"], 4) == 1.197, "line_pre drift: %r" % fk["skill_line"]["line_pre_w277"]
assert round(fk["skill_line"]["line_merged_607320"], 4) == 1.197, "line_merged drift: %r" % fk["skill_line"]["line_merged_607320"]
assert fk["ledger_identity"]["total"] == 1033735 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w277_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0039 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w277_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1031535
assert round(res["skill_line_v2_k_lift"]["line_pre_w277"], 4) == 1.197
assert round(res["skill_line_v2_k_lift"]["line_merged_607320"], 4) == 1.197
assert round(res["null_pool_cumulative"]["se_mu_at_k607320"], 6) == 0.000314, "W277 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w276_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k605120"], 6) == 0.000315, "W276 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w278bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [626901, 628900] and pr["bands"]["B"] == [628901, 629100]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [626701, 628700], "jump_to": 626901,
                              "refuser_pts": [], "refuser_bands": [[626701, 626900]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [626901, 627100], "jump_to": 628901,
                              "refuser_pts": [], "refuser_bands": [[626901, 628900]]}]
assert l1["B_naive"] == [626901, 627100] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W277_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W277_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W275_W276_W277_bands_respected_A"] is True and _ra["W275_W276_W277_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 275 and _l0["owner_rows"] == 267 and _l0["bmc_rows"] == 96
assert _l0["ordinal"] == 268 and _l0["w277_finalize_landed"] is True
assert _l0["w277_finalize_anchors"]["ledger_total"] == 1033735
assert _l0["w277_finalize_anchors"]["merged_n"] == 607320
assert round(_l0["w277_finalize_anchors"]["skill_line_delta_k_lift"], 4) == 0.0
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=626901 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=628901 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W279p_A_naive"] == "628901..630900"
assert pr["legs"]["leg4"]["W279p_B_naive"] == "629101..629300"
assert pr["legs"]["leg4"]["W279p_B_lands_inside_W279p_A_naive"] is True

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
# r1116 window face: probe-time read = ~4.5GB available (Monday-morning state, loop CPU-only; RAM
# fluctuates with resident daemons). Wide gate keeps idempotent re-runs green across the
# fluctuation (r1052 law); upper bound widened 6.0->16.0 THIS window (disclosed heal, live face
# above the r1113-era cap); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 16.0, "RAM face out of honest window: %.2f" % _ram_free

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=624_701..626_700", "A-ext seed=626_901..628_900"),
    ("B-ext exit seed=628_901..629_100", "B-ext exit seed=628_901..629_100"),
    ("entry rng=**624_701+j**（与 A[j] 同源配对语义逐字", "entry rng=**626_901+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W278 seat published bm-c r1102, rides origin b187aa6214)
    ("席位公示=MSG-20261019-080x-bmc-w277-seat 已推 origin c5f8b88f91 r565 律（bm-c r1112 席·queue-head seat-first lane）",
     "席位公示=MSG-20261019-102x-bmc-w278-seat 已推 origin b187aa6214 r565 律（bm-c r1114-continuation 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261019-080x-bmc-w277-seat 先推 origin c5f8b88f91 r565 律",
     "席位公示 MSG-20261019-102x-bmc-w278-seat 先推 origin b187aa6214 r565 律"),
    # wave-number + vacancy faces
    ("波号 277", "波号 278"),
    ("r1112 席位窗实跑：origin inbox 零 W277 席位外机命中", "r1114-continuation 席位窗实跑：origin inbox 零 W278 席位外机命中"),
    ("零 277 行", "零 278 行"),
    ("零 skip-ahead W278/W279 席位声明", "零 skip-ahead W279/W280 席位声明"),
    ("池第 275 枚", "池第 276 枚"),
    # ordinals + own-wave faces
    ("第 267 波", "第 268 波"),
    ("bm-c 第九十六枚自有波", "bm-c 第九十七枚自有波"),
    ("probe leg0 bmc_rows=95 attempt-continuity face（r1112 窗算法·bm-c own seat+bmc live rows 95 实读）——freeze 时 live derive bmc rows 95+候选=第 96 枚 EXACT",
     "probe leg0 bmc_rows=96 attempt-continuity face（r1114-continuation 窗算法·bm-c own seat+bmc live rows 96 实读）——freeze 时 live derive bmc rows 96+候选=第 97 枚 EXACT"),
    ("engine_owner==bm-c 95 行注册", "engine_owner==bm-c 96 行注册"),
    # engine live-read faces (bm-c instance, r1104 window)
    ("saturation_engine.py status live-read r1113：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1116：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1113 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1116 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1113 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1116 窗实读"),
    # runner CLI wave
    ("--wave 277/finalize --wave 277", "--wave 278/finalize --wave 278"),
    # sec8 placeholder projection-label bump (W278+ face)
    ("§5.5 W278+ 投影承接机证", "§5.5 W279+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w277", P2), ("n1_w276", "n1_w277"), (P2, "n1_w278"),
    ("_w277bmc", P3), ("_w276bmc", "_w277bmc"), (P3, "_w278bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W277", P1), ("W276", "W277"), ("W275", "W276"), ("W274", "W275"), ("W273", "W274"), ("W272", "W273"),
    ("W271", "W272"), ("W270", "W271"), ("W269", "W270"), ("W268", "W269"), ("W267", "W268"),
    ("W266", "W267"), ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), (P1, "W278"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle probe r1104)
    "A-ext seed=624_701..626_700": 1,
    "B-ext exit seed=628_901..629_100": 0,
    "entry rng=**624_701+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261019-080x-bmc-w277-seat 已推 origin c5f8b88f91 r565 律（bm-c r1112 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261019-080x-bmc-w277-seat 先推 origin c5f8b88f91 r565 律": 1,
    "波号 277": 1,
    "r1112 席位窗实跑：origin inbox 零 W277 席位外机命中": 1,
    "零 277 行": 1,
    "零 skip-ahead W278/W279 席位声明": 1,
    "池第 275 枚": 1,
    "第 267 波": 1,
    "bm-c 第九十六枚自有波": 1,
    "probe leg0 bmc_rows=95 attempt-continuity face（r1112 窗算法·bm-c own seat+bmc live rows 95 实读）——freeze 时 live derive bmc rows 95+候选=第 96 枚 EXACT": 1,
    "engine_owner==bm-c 95 行注册": 1,
    "saturation_engine.py status live-read r1113：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1113 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1113 窗实读": 1,
    "--wave 277/finalize --wave 277": 1,
    "§5.5 W278+ 投影承接机证": 1,
    # lowercase rolls (measured on T0)
    "n1_w278": 4, "n1_w277": 4, "_w278bmc": 4, "_w277bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w278bmc_needle_probe.py r1104 window;
    # measured-counts law r1077)
    "W277": 44, "W276": 62, "W275": 4, "W274": 4, "W273": 3, "W272": 3, "W271": 3, "W270": 2, "W269": 2, "W268": 2, "W267": 2, "W266": 2,
    "W265": 2, "W264": 2, "W263": 2, "W262": 1, "W261": 1,
    # block-marker stability floors (raw template face; measured on T0)
    "engine_owner 行 266 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**624_701+j**": 1,
    "exit rng=**626_701+j**": 1,
    "probe W278+ 投影 A naive 626_701..628_700 CLEAN hops=0": 1,
    "5. **W278+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 1,031,535": 0,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
    "07:4x": 4, "07:2x": 2, "08:1x": 1,
    # zero-floors (absence assertions on T0; needle probe measured all == 0)
    "waits-upstream ARMED": 0, "GATED on": 0, "finalize PENDING": 0, "queue_depth": 0,
    "_w278bmc": 0, "n1_w278": 0, "W279p_": 0,
    "第 97 枚": 0, "第 268 波": 0, "第九十七枚": 0, "池第 276 枚": 0, "波号 278": 0, "零 278 行": 0,
    "engine_owner==bm-c 96 行注册": 0, "bmc_rows=96": 0, "bmc rows 96+候选": 0,
    "第二十八次连续 A-hop": 0, "第二十八次连续 above-own-A": 0, "连续二十七波": 0, "共二百七十六面": 0,
    "1,033,735": 0, "609,520": 0, "626_901..628_900": 0, "628_901..629_100": 0,
    "628_901..630_900": 0, "629_101..629_300": 0,
    "09:5x": 0, "10:3x": 0, "09:0x": 0,
    "e0bc4a0ddd": 0, "9e53371814": 0, "0df07c846b": 0, "644b4f8459": 0, "0502c722ac": 0, "b187aa6214": 0,
    "−0.09277044": 0, "0.24508694": 0, "−0.08889850": 0, "0.3095": 0,
    "实差 0.0039 在带内": 0, "line_pre_w277 1.197": 0, "line_merged@K607,320": 0, "K=607,320": 0,
    "r1114-continuation W277 §7 范式": 0, "（W277 注册+烧录+finalize 全落地）": 0,
    "MSG-20261019-102x": 0, "键 W277 实测 K-lift": 0, "本窗 free RAM ~4.5GB": 0,
    "624_701..626_700 CLEAN": 0,
    "620_101..620_300": 0, "622_301..624_300": 0, "613_701..613_900": 0, "620_301..622_300": 0,
    "613_701..613_900": 0, "620_101..622_100": 0,
    "12:2x": 0, "13:5x": 0, "14:0x": 0,
    "611_300+1": 0, "617_900+1": 0, "611_500+1": 0,
    # NOTE (fail-closed discipline): 第二十六次连续 A-hop (T0=3) / 第二十七次连续 above-own-A
    # (T0=2) / 第二十七次连续 A-hop (T0=3) / 连续二十六波 (T0=1) / 共二百七十五面 (T0=1) are NOT
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
    # finalize-window stamp roll (heal (1)): W277 finalize one-pass landed 10:3x (0502c722ac
    # 10:35:34); T1 carries the W276-era 07:4x stamps x4 (MEASURED by the r1115 prep, r1077 law)
    ("07:4x", "10:3x", 4),
    # date-cross N/A this generation (heal (2), disclosed): W278 seat receipt same-date 20261019
    # with the W277 seat receipt -- lowercase prefix chain rolls the receipt date correctly with
    # NO date-cross leg.
    # sec.5 item1 measured keys -> W277 actuals (n1_w277_results + fivekeys machine values)
    ("（W277 实测键 **−0.09278451**·K=605,120 合并池·W277-only 实测 **−0.08705886**）",
     "（W277 实测键 **−0.09277044**·K=607,320 合并池·W277-only 实测 **−0.08889850**）", 1),
    ("W2..W277 共二百七十五面实测 mu 稳定先例", "W2..W277 共二百七十六面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (4)): TRUE W277 diff = 0.0039 @4dp (measured
    # 0.0038719368372521906 full), in-band
    ("W277-only vs merged 实差 0.0057 在带内", "W277-only vs merged 实差 0.0039 在带内", 1),
    # sec.5 item2 sigma key (heal (5))
    ("键 **0.24508562**=W277 合并池实测", "键 **0.24508694**=W277 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (6))
    ("与 W277 A 档 p95（**0.305** 实测锚）", "与 W277 A 档 p95（**0.3095** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (7): lowercase line_pre_w276 NOT rolled by the
    # W-roll; true W277 anchors K-lift +0.0000 held-flat-at-zero + line_merged@K607,320 1.197 +
    # line_pre_w277 1.197 + n_eff_held 1,031,535)
    ("键 W277 实测 K-lift **+0.0001**·line_merged@K605,120 **1.1969**·line_pre_w276 1.1968·n_eff_held_equal 1,029,335",
     "键 W277 实测 K-lift **+0.0000**·line_merged@K607,320 **1.197**·line_pre_w277 1.197·n_eff_held_equal 1,031,535", 1),
    # se_mu chain true-history correction (heal (8); W277 fivekeys key5 measured 0.000314
    # narrowing-held from W276 0.000315)
    ("→W272 **0.000319**→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000315**→W278 投影 0.000315】",
     "→W272 **0.000319**→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 投影 0.000314】", 1),
    # sec.4 merged-pool anchor face (heal (9): W277 finalize landed)
    ("W1..W277 已落账 605,120 实测", "W1..W277 已落账 607,320 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W277 cycle (heal (10): bm-c r1114-continuation;
    # OLD faces are POST-VMAP faces -- the raw T0' W276-cycle rows already shifted W276->W277
    # before this leg fires; the leg fixes the window number r1111->r1114-continuation,
    # measured post-VMAP count=1)
    ("bm-c r1111 W277 §7 范式", "bm-c r1114-continuation W277 §7 范式", 1),
    ("bm-c r1111 W277 §8 范式", "bm-c r1114-continuation W277 §8 范式", 1),
    # RAM face live-measured THIS window (heal (11)): psutil 4 GB available (~4.5GB) + nvidia-smi 实读 0%·1.8G VRAM 占用·MV 车道已收官 GPU idle 回释
    # -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); honest window face
    # updated from the r1113 ~3.9GB face
    ("本窗 free RAM ~3.9GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~4.5GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 0%·1.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W277 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- pre-shift needles land the MUST series on the TRUE labels W263..W276;
    # this leg restores the POST-VMAP shifted ledger and appends the true W277 anchor
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚·W275 冻结窗 ~4.0G bm-c 实锚·W276 冻结窗 ~3.8G bm-c 实锚·W277 冻结窗 ~3.9G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚·W276 冻结窗 ~3.9G bm-c 实锚·W277 冻结窗 ~4.5G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 267 注册在册（表尾 W278 行【bm-c r1114-continuation 五面冻结 splice 9e53371814 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 10th gen）】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w277/ 12/12·ledger append 0df07c846b+644b4f8459】"
    "·**W277 finalize 已落地**【n1_w277_results.json 机读·净账本锚头 1,033,735·K=607,320 合并池·W277 finalize one-pass bm-c r1114-continuation 窗 10:3x·estate chain r1113/r1114-continuation W277 全周期 e0bc4a0ddd+9e53371814+0502c722ac】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1114-continuation 席位 MSG-20261019-102x-bmc-w278-seat 已推 origin b187aa6214"
    "·probe receipt _w278bmc_20261019 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 96+候选=第 97 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1114-continuation 席位窗 2026-10-19 10:3x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W278=bm-c own-wave window per chain-order law（W275 bm-c→W276 bm-c→W277 bm-c→W278 bm-c own-turn rotation·MSG-102x owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W277 N1 注册全部落地**【W277=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W277**"
    "【净账本锚头 **1,033,735**·K=607,320 合并池·n1_w277_results.json 机读·W277 finalize one-pass bm-c r1114-continuation 窗 10:3x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W277 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=607,320+2,200（本波）=**609,520 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十七次连续 A-hop）**："
    "A 面算术续带 626_701..628_700（自注册 W277 A 尾 626_700 续）"
    "在席位窗宇宙（post-W277-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W277 B 带 626_701..626_900 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W277 prereg §5 item5 post-W277-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W277 B 尾 626_900→A first-clean **626_901..628_900**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（626_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 626_701..628_700→jump 626_901·refuser band 626_701..626_900〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W277_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；"
    "**B-ext exit seed=628_901..629_100**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第二十八次连续 above-own-A 落位）**："
    "B naive 续带 626_901..627_100（自注册 W277 B 尾 626_900+1 续）"
    "在席位窗宇宙（post-W277-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 626_901..627_100 落本波 A first-clean 窗 626_901..628_900 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 626_901..628_900**（1 hop）"
    "→**1 hop** 落位 **628_901..629_100**·**B 落位 base==本波 A 窗尾+1（628_900+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W277 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W278 A naive 626_701..628_700 将被注册 W277 B 带拒（staircase affects A 承袭·第二十七次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R279：W278 带（A 626_901..628_900/B 628_901..629_100）注册后对 W279+ 的拒面影响=W278 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**626_901+j**（法典 §4 W278 行 A=626_901..628_900·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十七次连续 A-hop）**："
    "A 算术续带 626_701..628_700（自注册 W277 A 尾 626_700 续）"
    "在席位窗宇宙（post-W277-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W277 B 带 626_701..626_900 落 naive A 窗内=W277 prereg §5 item5 post-W277-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W277 B 尾 626_900→A first-clean 626_901..628_900·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（626_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W277_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**628_901+j**（法典 §4 W278 行 B=628_901..629_100·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 626_901..627_100（自注册 W277 B 尾 626_900+1 续）"
    "在席位窗宇宙（post-W277-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 626_901..628_900 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 626_901..628_900→1 hop 落位 628_901..629_100·"
    "**B 落位 base==本波 A 窗尾+1（628_900+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第二十八次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W277 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W279+ 投影 A naive 628_901..630_900 CLEAN hops=0（零 live refusers）/ B naive 629_101..629_300 CLEAN hops=0 "
    "**但落 naive W278 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 628_901..630_900 CLEAN·hops=0——**post-W278-REGISTERED 预披露：naive W278 A 起点将被注册 W278 B 带 628_901..629_100 拒=staircase affects A 第二十八次连续 A-hop 预期**；"
    "投影 B naive 629_101..629_300 clean 但落 naive W278 A 窗 628_901..630_900 内——"
    "**above-own-A 承袭面：W278 B 628_901..629_100 落本波 A 窗之上〔第二十七次连续〕·W278 A 面 1-hop=staircase affects A〔第二十七次连续〕·"
    "W279 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W278 B 带将拒 naive W278 A 窗仅当重叠——"
    "**W279 freezer 承接面强制注记：须在 post-W278 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W279+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 628_901..630_900 **CLEAN**（hops=0·pre-W278 宇宙零 live refusers）——"
    "**post-W278-REGISTERED 预披露：naive W278 A 起点将被注册 W278 B 带 628_901..629_100 拒（staircase-affects-A 第二十八次连续 A-hop 预期）**；"
    "B naive **629_101..629_300 CLEAN（hops=0）但落投影 A 窗 628_901..630_900 内**（W279p_B_lands_inside_W279p_A_naive=true——"
    "**staircase face 延续**：W278 A 626_901..628_900+B 628_901..629_100 注册后 naive W278 A 窗起点即被注册 W278 B 带拒（staircase affects A 承袭·第二十八次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W278 宇宙 live re-derive 必变·禁转录投影）；"
    "**W278 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278=A/B 双 1-hop 形态连续二十七波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W278 冻结方必须在 post-W278 注册宇宙重 derive 且 derive B 时预留本波 A 窗 626_901..628_900+本波 B 带 628_901..629_100"
    "——leg2 律/E36 卡·W141 先例；verify at W279 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w278bmc_freeze_edits.py"
    "（按 _w277bmc_freeze_edits.py 模板派生·gate0.5 自查 W277 行+W277 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1113/r1114-continuation W277 全周期先例实时间线：prereg e0bc4a0ddd 落于 r1113 窗·splice 9e53371814 落于 r1114-continuation 执行窗 @@SPLICE_T@@——"
    "**W278 freeze 面：W277 own-wave finalize 已落地=席位时即解锁——席位 r1114-continuation 窗+prereg r1116 窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 266 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**624_701+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**626_701+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W278+ 投影 A naive 626_701..628_700 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W278+ 投影（probe 机证 leg4", "verify at W278 prereg，hop 链逐跳在 probe 回执。"),
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
    "PERPETUAL-N1-W278", "research/PERPETUAL_N1_W278_PREREG.md",
    "626_901..628_900", "628_901..629_100", "607,320", "1,033,735", "607,320", "K=607,320",
    "n1_w278_results.json", "n1_w277_results.json", "MSG-20261019-102x-bmc-w278-seat", "b187aa6214",
    "池第 276 枚", "第九十七枚", "第 268 波", "第 97 枚",
    "STAIRCASE-AFFECTS-A", "第二十七次连续 A-hop", "第二十八次连续 above-own-A",
    "_w278bmc_20261019", "--wave 278/finalize --wave 278",
    "W277 finalize one-pass bm-c r1114-continuation", "n_eff_held_equal 1,031,535",
    "−0.09277044", "0.24508694", "−0.08889850", "（**0.3095** 实测锚）",
    "键 W277 实测 K-lift **+0.0000**", "line_merged@K607,320 **1.197**", "line_pre_w277 1.197",
    "实差 0.0039 在带内", "共二百七十六面", "W2..W277", "W1..W277",
    "engine_owner==bm-c 96 行注册", "engine_owner 行 267 注册在册",
    "probe leg0 bmc_rows=96 attempt-continuity face（r1114-continuation 窗算法·bm-c own seat+bmc live rows 96 实读）",
    "bm-c 循环班 r1114-continuation 席位窗", "本窗 free RAM ~4.5GB", "本机 bm-c 实例",
    "W278=bm-c own-wave window per chain-order law",
    "e0bc4a0ddd", "9e53371814", "0df07c846b", "644b4f8459", "0502c722ac",
    "W279+ 投影", "W279p_B_lands_inside_W279p_A_naive", "verify at W279 prereg",
    "_w278bmc_freeze_edits.py", "_w277bmc_freeze_edits.py 模板派生",
    "bm-c r1114-continuation W277 §7 范式", "bm-c r1114-continuation W277 §8 范式",
    "（上游 W277 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "（W277 注册+烧录+finalize 全落地）",
    "W206/W211..W277 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",
    "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚", "W274 冻结窗 ~4.0G bm-c 实锚", "W275 冻结窗 ~3.8G bm-c 实锚", "W276 冻结窗 ~3.9G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R279：W278 带",
    "→W272 **0.000319**→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 投影 0.000314】",
    "626_900+1", "628_900+1", "628_901..629_100",
    "A_staircase_hop_past_W277_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 278", "零 278 行", "零 skip-ahead W279/W280 席位声明",
    "10:3x", "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1116：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1116 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1116 窗实读",
    "nvidia-smi 实读 0%·1.8G VRAM 占用·MV 车道已收官 GPU idle 回释",
    "r1114-continuation 席位窗实跑：origin inbox 零 W278 席位外机命中",
    "results/p2cal_ext/n1_w277/ 12/12",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=611_501", "B-ext exit seed=613_501",
    "624_701..626_700", "620_101..620_300", "613_301..613_500", "613_301..615_300", "613_701..613_700",
    "622_301..624_300 CLEAN", "622_301..624_300", "620_301..622_300", "620_101..620_300", "622_301..624_300", "613_701..613_900",
    "620_301..622_300", "613_701..613_900", "620_101..622_100",
    "626_701..628_700 CLEAN", "626_901..627_100 CLEAN",
    "GATED on", "finalize PENDING", "queue_depth",
    "605,120", "**607,320 投影**", "line_merged@K605,120", "K=605,120",
    "−0.09278451", "0.24508562", "−0.08705886", "**0.305**", "实差 0.0057 在带内",
    "17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "07:2x", "07:4x", "08:1x",
    "MSG-20261019-080x", "c5f8b88f91", "21b51a102", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",
    "bmc_rows=95", "bmc rows 95+候选", "第 96 枚", "第 267 波", "第九十六枚",
    "engine_owner==bm-c 95 行注册",
    "r1112 席位窗实跑", "r1101 窗算法",
    "95%·7.9G VRAM",
    "W278p_", "W278p_",
    "line_pre_w271", "键 W276 实测 K-lift",
    "verify at W278 prereg",
    "W278+ 投影", "W277+ 投影", "W276+ 投影",
    "第二十六次连续 A-hop", "第二十二次连续 above-own-A", "第二十七次连续 above-own-A", "连续二十六波", "共二百七十五面",
    "n1_w276_results.json", "n1_w269_results.json", "n1_w268_results.json",
    "W2..W276", "W136..W276", "W1..W276",
    "波号 277", "零 277 行",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",
    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",
    "624_700+1", "617_900+1", "611_500+1", "617_900+1", "611_300+1",
    "12:2x", "13:5x", "14:0x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W279+ 投影") == 3, "W278+ count=%d (expect 3 = §5.5 rolled + b_claim_proj + b5)" % T2.count("W279+ 投影")
assert T2.count("W278+ 投影") == 0, "W278+ count=%d (expect 0)" % T2.count("W278+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("第二十七次连续 A-hop") == 3, "A21 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("第二十七次连续 A-hop")
assert T2.count("第二十八次连续 A-hop") == 3, "A22 count=%d (expect 3 = b5 x2 + b_claim_proj)" % T2.count("第二十八次连续 A-hop")
assert T2.count("第二十八次连续 above-own-A") == 2, "B22 count=%d (expect 2 = b_band + b3_b)" % T2.count("第二十八次连续 above-own-A")
assert T2.count("第二十七次连续 above-own-A") == 0, "B21 count=%d (expect 0)" % T2.count("第二十七次连续 above-own-A")
assert T2.count("连续二十七波") == 1, "21-wave count=%d (expect 1 = b5 NEW)" % T2.count("连续二十七波")
assert T2.count("626_901..628_900") >= 5, "own-A count=%d (expect >=5)" % T2.count("626_901..628_900")
assert T2.count("628_901..629_100") >= 4, "own-B count=%d (expect >=4)" % T2.count("628_901..629_100")
assert T2.count("628_901..629_100") >= 3, "reg-W277-B count=%d (expect >=3)" % T2.count("628_901..629_100")
assert T2.count("626_901..627_100") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("626_901..627_100")
assert T2.count("626_701..628_700") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("626_701..628_700")
assert T2.count("628_901..630_900") == 5, "W278p-A count=%d (expect 5 = b_claim_proj x3 + b5 x2)" % T2.count("628_901..630_900")
assert T2.count("629_101..629_300") == 3, "W278p-B count=%d (expect 3 = b_claim_proj x2 + b5)" % T2.count("629_101..629_300")
assert T2.count("席位时即解锁") == 2, "unlock count=%d (expect 2)" % T2.count("席位时即解锁")
assert T2.count("_w278bmc_20261019") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w278bmc_20261019")
assert T2.count("1,033,735") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,033,735")
# n_eff_held face honest update (r1093 full-precision law): the ONLY 1,031,535 in the output
# is the sec.5 item4 n_eff_held_equal anchor = the W277 fivekeys measured value (the canon
# r1102 window left this sub-face stale at the W276-era 1,020,535; healed forward here)
assert T2.count("1,031,535") == 1, "n_eff_held count=%d (expect 1 = sec.5 item4 honest anchor only)" % T2.count("1,031,535")
assert T2.count("607,320") >= 3, "merged-K count=%d (expect >=3)" % T2.count("607,320")
assert T2.count("（占位·finalize one-pass 后回填") == 1, "sec7 placeholder count=%d (expect 1)" % T2.count("（占位·finalize one-pass 后回填")
assert T2.count("（占位·finalize 同窗回填") == 1, "sec8 placeholder count=%d (expect 1)" % T2.count("（占位·finalize 同窗回填")
assert T2.count("第 97 枚") == 2, "own-ordinal count=%d (expect 2 = leg + b_title)" % T2.count("第 97 枚")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W278 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 9e53371814 @ " + SPLICE_T + " | finalize estate: 0502c722ac @ 10:3x | seat: b187aa6214 @ 10:3x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~4.5GB written, MV 车道已收官 idle) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == e5d12b12da03a799a88bd980cf8566b2b1eff5ba @ e0bc4a0ddd (frozen pre-run face; HEAD post-backfill twin 78571eb1 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
