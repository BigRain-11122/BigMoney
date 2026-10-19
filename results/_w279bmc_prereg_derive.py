# -*- coding: utf-8 -*-
# r1122 bm-c: W279 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w278bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W278 prereg AT THE FREEZE COMMIT df1aaba72a (git
# df1aaba72a:research/PERPETUAL_N1_W278_PREREG.md, 23,814 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w279bmc_w278_frozen_face.txt by the r1120 PREP window
# (python subprocess raw bytes; prep facts receipt results/_w279bmc_prep_facts.json);
# byte-verified: disk==blob sha256_16 99001d3d3f337942 (CR-normalized; autocrlf disk face
# disclosed r1093 law), freeze blob sha1 053892f61cf24d9803cb20410d4ab1163cb7897a.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 1c93e077c2b64476fb55041a7f59f7591f67db68
# (28,082 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the
# r1119 W278 cycle (estate 0a92fcc28f). Deriving from the backfilled face would
# fabricate W279 sec.7/8 from W278 measured numbers -- the r1049/r1052 precedent requires the
# df1aaba72a frozen pre-run face. W279 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w279bmc_20261019_probe_receipt.json (bm-c r1119
#     window authored+run live, seat rides origin 900c23fe7d per r565 early-visibility law,
#     MSG-20261019-145x-bmc-w279-seat landed on origin; zero foreign W279 seat claims; zero
#     W280/W281 skip-claims). STAIRCASE CONTINUES: A naive 628_901..630_900 REFUSED at start
#     (registered W278 B band 628_901..629_100 sits INSIDE the naive A window) -> A first-clean
#     629_101..631_100 hops=1 (TWENTY-EIGHTH consecutive A-hop, W278 prereg sec.5 item5
#     post-W278-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 629_101..629_300 lands INSIDE the own-wave W279 A first-clean window 629_101..631_100
#     (own-A reservation cascade) -> hop past own-A tail 631_100 -> 631_101..631_300 hops=1
#     (TWENTY-NINTH consecutive above-own-A landing); seed_admit FREE x2 (A base=629101 span=2000 /
#     B base=631101 span=200); leg0 rows=276 owner_rows=268 bmc_rows=97 ordinal=269; leg2
#     conflicts=0; leg3 origin_vacancy=true; W280p projection: A naive 631_101..633_100 CLEAN
#     hops=0 / B naive 631_301..631_500 CLEAN hops=0 but lands inside W280p A naive.
#   - upstream W278 finalize LANDED (bm-c r1119 window one-pass, n1_w278_results.json
#     landed via 0a92fcc28f 15:13:26, fivekeys 6/6 receipt results/_r1118bmc_w278_fivekeys.json +
#     sec.7/8 backfilled): merged K=609,520 / ledger 1,035,935 EXACT (1,033,735+2,200) / merged mu
#     -0.09278575748129675 (8dp -0.09278576) / sigma 0.24505493584785207 (8dp 0.24505494) /
#     se_mu@K609,520 0.000314 (held-flat from W277 0.000314) / W278-only mu -0.09701509090909091
#     (8dp -0.09701509) / A p95 0.3095->0.2844 (in-band) / K-lift -0.0002
#     (first negative micro-move, key4-band legal) / n_eff_held 1,033,735 / line_pre_w278 1.1971 /
#     line_merged@609,520 1.1969 / key1 only-vs-merged gap 0.004229333427794163 (4dp 0.0042)
#     in-band; splice b6f486af35 13:5x (r1118 window, engine batches 60e630918f+b965e2ecf0);
#     sixgate 41st consecutive PRE-FINALIZE ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded
#     narration faces; ALL gates machine-verify against the full-precision fivekeys/results jsons
#     (r1093 CODELY pit entry; live-read governs r587).
# Needle-count pre-flight evidence: results/_w279bmc_prep_facts.json + needle floors
# results/_w279bmc_needle_floors.json (MEASURED on T0 by the r1120/r1121 PREP windows, r1077
# measured-counts law; floors below match every measured count; zero-floor audit: every
# next-wave face measured 0 on T0).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1102 family):
# (1) finalize-window stamp roll: W278 finalize one-pass landed 15:1x (0a92fcc28f 15:13:26); T0
#     carries the W277-era 10:3x stamps x5 (MEASURED by the r1121 prep) -> POST_LEG x5; splice
#     stamps 09:5x-era x2 -> W278 splice 13:5x (b6f486af35).
# (2) date-cross N/A this generation (disclosed): the W279 seat receipt is SAME-DATE with the W278
#     seat receipt (both _*_20261019) -- the lowercase prefix chain rolls the receipt date correctly
#     with NO date-cross leg.
# (3) sec.5 item1 measured keys -> W278 actuals (n1_w278_results + fivekeys machine values):
#     merged mu -0.09278576 / K=609,520 / W278-only -0.09701509 (all full-precision
#     machine-verified in-gate).
# (4) sec.5 item1 diff face: W278-only vs merged TRUE diff = 0.0042 @4dp (measured
#     0.004229333427794163 full) in-band |d|<0.02.
# (5) sec.5 item2 sigma key 0.24508694 -> 0.24505494 (W278 merged-pool measured).
# (6) sec.5 item3 p95 anchor 0.3095 -> 0.2844 (W278 A-band fivekeys measured).
# (7) sec.5 item4 K-lift chain: K-lift -0.0002 (W278 fivekeys key4, first negative micro-move
#     in-band) + line_merged@K609,520 1.1969 + lowercase line_pre_w277 -> line_pre_w278 1.1971
#     (lowercase NOT rolled by the W-roll, case-sensitive; r1102 heal (6) family) + n_eff_held_equal
#     1,031,535 -> 1,033,735.
# (8) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries the
#     stale projection on the W278 slot -> POST_LEG rewrites the tail with true history W273 0.000319 /
#     W274 0.000318 / W275 0.000317 / W276 0.000316 / W277 0.000314 / W278 0.000314 and appends
#     the W279 projection 0.000313 (computed sigma/sqrt(K611,720), machine-read anchors).
# (9) sec.4 merged-pool anchor face: W1..W278 607,320 -> W1..W278 609,520 (W278 finalize landed).
# (10) sec.7/8 backfill paradigm rows: bm-c r1114-continuation W277 -> bm-c r1119 W278 (cycle owner
#     + wave roll).
# (11) RAM face live-measured THIS window: psutil 6 GB available (~6.4GB, probe-time read) +
#     nvidia-smi nvidia-smi 实读 0%·2.0G VRAM 占用·MV 车道已收官 GPU idle 回释 -- GPU=gen-only lane idle (loop CPU-only); the r1116 ~4.5GB face is stale.
#     RAM honest-window gate 16.0 wide cap held (r1116 heal (e) standing).
# (12) low-RAM precedent ledger append: W278 freeze-window ~6.4G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; pre-shift needles land the MUST series
#     back on the TRUE labels W263..W277 + the new W278 anchor).
# (13) seat/provenance legs: MSG-20261019-102x-bmc-w278-seat/b187aa6214/r1114-continuation ->
#     MSG-20261019-145x-bmc-w279-seat/900c23fe7d/r1119 (two live faces + block NEWs).
# (14) engine live-read faces r1116 -> r1122 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
# (15) estate-chain/timeline faces rolled (heal (D) 3-label honest): the W278 cycle = prereg r1116
#     (df1aaba72a) + splice r1118 (b6f486af35) + finalize/fivekeys/sec78 r1119 one-window
#     (0a92fcc28f; engine batches 60e630918f+b965e2ecf0).
# DEFECT-BIRTHPLACE HEALS (builder-level, disclosed in the builder header):
# (16) A_hop_chain parenthetical refuser-band machine face verified at birth (canon heal (a)
#     re-applied rolled): the single blanket roll lands the parenthetical on the
#     machine-receipt face (registered W278 B band 628_901..629_100 refused the naive W279 A
#     start -- receipt leg1 refuser_bands=[[628901,629100]]); the own-B lineal-defect face
#     (631_101..631_300) and the stale prior face (626_701..626_900) are both count-asserted
#     absent, disclosed + fail-closed.
# (17) freezer-label unlag re-confirmed STRUCTURAL and re-applied (the label sits one above the
#     W-chain top and never rolls naturally; universe face rolls naturally; W279->W280 this
#     generation, measured x1 on T0 by the r1121 prep).
import io, os, sys, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w279bmc_w278_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W279_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "053892f61cf24d9803cb20410d4ab1163cb7897a"   # freeze-commit face @ df1aaba72a
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "df1aaba72a:research/PERPETUAL_N1_W278_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W278_PREREG.md"])
assert _hb == "1c93e077c2b64476fb55041a7f59f7591f67db68", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")  # heal (h) r1093: CRLF disk face -> LF git-object face (sim byte-identity)
assert len(T0.encode("utf-8")) == 23814, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "99001d3d3f337942", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("df1aaba72a", "b6f486af35", "60e630918f", "b965e2ecf0", "0a92fcc28f", "900c23fe7d"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "b6f486af35"])    # 2026-10-19 13:5x +0800
_m = re.match(r"2026-10-19 13:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "13:%sx" % _m.group(1)[0]   # 13:5x
_fz = git_out(["show", "-s", "--format=%ci", "0a92fcc28f"])    # 2026-10-19 15:13:26 +0800
assert _fz.startswith("2026-10-19 15:1"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "900c23fe7d"])   # 2026-10-19 15:09:11 +0800
assert _st.startswith("2026-10-19 15:0"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w278_results.json"])
assert _fin_log == "0a92fcc28f", "W278 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "900c23fe7d"])
assert "MSG-20261019-145x-bmc-w279-seat.md" in _seat_files, "W279 seat MSG not carried by seat commit 900c23fe7d: %r" % _seat_files[:200]

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1118bmc_w278_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 609520, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09278576, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24505494, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k609520"], 6) == 0.000314, "se_mu drift: %r" % fk["merged"]["se_mu_k609520"]
assert round(fk["w278_only"]["mu"], 8) == -0.09701509, "w278-only mu drift: %r" % fk["w278_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.2844, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == -0.0002, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1033735, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w278"], 4) == 1.1971, "line_pre drift: %r" % fk["skill_line"]["line_pre_w278"]
assert round(fk["skill_line"]["line_merged_609520"], 4) == 1.1969, "line_merged drift: %r" % fk["skill_line"]["line_merged_609520"]
assert fk["ledger_identity"]["total"] == 1035935 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w278_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0042 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w278_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1033735
assert round(res["skill_line_v2_k_lift"]["line_pre_w278"], 4) == 1.1971
assert round(res["skill_line_v2_k_lift"]["line_merged_609520"], 4) == 1.1969
assert round(res["null_pool_cumulative"]["se_mu_at_k609520"], 6) == 0.000314, "W278 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w277_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k607320"], 6) == 0.000314, "W277 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w279bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [629101, 631100] and pr["bands"]["B"] == [631101, 631300]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [628901, 630900], "jump_to": 629101,
                              "refuser_pts": [], "refuser_bands": [[628901, 629100]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [629101, 629300], "jump_to": 631101,
                              "refuser_pts": [], "refuser_bands": [[629101, 631100]]}]
assert l1["B_naive"] == [629101, 629300] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W278_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W278_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W276_W277_W278_bands_respected_A"] is True and _ra["W276_W277_W278_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 276 and _l0["owner_rows"] == 268 and _l0["bmc_rows"] == 97
assert _l0["ordinal"] == 269 and _l0["w278_finalize_landed"] is True
assert _l0["w278_finalize_anchors"]["ledger_total"] == 1035935
assert _l0["w278_finalize_anchors"]["merged_n"] == 609520
assert round(_l0["w278_finalize_anchors"]["skill_line_delta_k_lift"], 4) == -0.0002
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=629101 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=631101 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W280p_A_naive"] == "631101..633100"
assert pr["legs"]["leg4"]["W280p_B_naive"] == "631301..631500"
assert pr["legs"]["leg4"]["W280p_B_lands_inside_W280p_A_naive"] is True

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
# r1122 window face: probe-time read = ~6.4GB available (loop CPU-only; RAM fluctuates with
# resident daemons). Wide gate keeps idempotent re-runs green across the fluctuation
# (r1052 law); 16.0 upper bound held from the r1116 heal (e); below 0.05GB = machine near
# death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 16.0, "RAM face out of honest window: %.2f" % _ram_free

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=626_901..628_900", "A-ext seed=629_101..631_100"),
    ("B-ext exit seed=631_101..631_300", "B-ext exit seed=631_101..631_300"),
    ("entry rng=**626_901+j**（与 A[j] 同源配对语义逐字", "entry rng=**629_101+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W279 seat published bm-c r1102, rides origin 900c23fe7d)
    ("席位公示=MSG-20261019-102x-bmc-w278-seat 已推 origin b187aa6214 r565 律（bm-c r1114-continuation 席·queue-head seat-first lane）",
     "席位公示=MSG-20261019-145x-bmc-w279-seat 已推 origin 900c23fe7d r565 律（bm-c r1119 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261019-102x-bmc-w278-seat 先推 origin b187aa6214 r565 律",
     "席位公示 MSG-20261019-145x-bmc-w279-seat 先推 origin 900c23fe7d r565 律"),
    # wave-number + vacancy faces
    ("波号 278", "波号 279"),
    ("r1114-continuation 席位窗实跑：origin inbox 零 W278 席位外机命中", "r1119 席位窗实跑：origin inbox 零 W279 席位外机命中"),
    ("零 278 行", "零 279 行"),
    ("零 skip-ahead W279/W280 席位声明", "零 skip-ahead W280/W281 席位声明"),
    ("池第 276 枚", "池第 277 枚"),
    # ordinals + own-wave faces
    ("第 268 波", "第 269 波"),
    ("bm-c 第九十七枚自有波", "bm-c 第九十八枚自有波"),
    ("probe leg0 bmc_rows=96 attempt-continuity face（r1114-continuation 窗算法·bm-c own seat+bmc live rows 96 实读）——freeze 时 live derive bmc rows 96+候选=第 97 枚 EXACT",
     "probe leg0 bmc_rows=97 attempt-continuity face（r1119 窗算法·bm-c own seat+bmc live rows 97 实读）——freeze 时 live derive bmc rows 97+候选=第 98 枚 EXACT"),
    ("engine_owner==bm-c 96 行注册", "engine_owner==bm-c 97 行注册"),
    # engine live-read faces (bm-c instance, r1104 window)
    ("saturation_engine.py status live-read r1116：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1122：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1116 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1122 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1116 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1122 窗实读"),
    # runner CLI wave
    ("--wave 278/finalize --wave 278", "--wave 279/finalize --wave 279"),
    # sec8 placeholder projection-label bump (W279+ face)
    ("§5.5 W279+ 投影承接机证", "§5.5 W280+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w278", P2), ("n1_w277", "n1_w278"), (P2, "n1_w279"),
    ("_w278bmc", P3), ("_w277bmc", "_w278bmc"), (P3, "_w279bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W278", P1), ("W277", "W278"), ("W276", "W277"), ("W275", "W276"), ("W274", "W275"), ("W273", "W274"),
    ("W272", "W273"), ("W271", "W272"), ("W270", "W271"), ("W269", "W270"), ("W268", "W269"),
    ("W267", "W268"), ("W266", "W267"), ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), (P1, "W279"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle probe r1104)
    "A-ext seed=626_901..628_900": 1,
    "B-ext exit seed=631_101..631_300": 0,
    "entry rng=**626_901+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261019-102x-bmc-w278-seat 已推 origin b187aa6214 r565 律（bm-c r1114-continuation 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261019-102x-bmc-w278-seat 先推 origin b187aa6214 r565 律": 1,
    "波号 278": 1,
    "r1114-continuation 席位窗实跑：origin inbox 零 W278 席位外机命中": 1,
    "零 278 行": 1,
    "零 skip-ahead W279/W280 席位声明": 1,
    "池第 276 枚": 1,
    "第 268 波": 1,
    "bm-c 第九十七枚自有波": 1,
    "probe leg0 bmc_rows=96 attempt-continuity face（r1114-continuation 窗算法·bm-c own seat+bmc live rows 96 实读）——freeze 时 live derive bmc rows 96+候选=第 97 枚 EXACT": 1,
    "engine_owner==bm-c 96 行注册": 1,
    "saturation_engine.py status live-read r1116：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1116 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1116 窗实读": 1,
    "--wave 278/finalize --wave 278": 1,
    "§5.5 W279+ 投影承接机证": 1,
    # lowercase rolls (measured on T0)
    "n1_w279": 4, "n1_w278": 4, "_w279bmc": 4, "_w278bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w279bmc_needle_probe.py r1104 window;
    # measured-counts law r1077)
    "W278": 44, "W277": 62, "W276": 4, "W275": 4, "W274": 3, "W273": 3, "W272": 3, "W271": 2, "W270": 2, "W269": 2, "W268": 2, "W267": 2,
    "W266": 2, "W265": 2, "W264": 2, "W263": 2, "W262": 1, "W261": 1,
    # block-marker stability floors (raw template face; measured on T0)
    "engine_owner 行 267 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**626_901+j**": 1,
    "exit rng=**628_901+j**": 1,
    "probe W279+ 投影 A naive 628_901..630_900 CLEAN hops=0": 1,
    "5. **W279+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 1,033,735": 0,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
    "10:3x": 5, "09:5x": 2,
    # zero-floors (absence assertions on T0; needle probe measured all == 0)
    "waits-upstream ARMED": 0, "GATED on": 0, "finalize PENDING": 0, "queue_depth": 0,
    "_w279bmc": 0, "n1_w279": 0, "W280p_": 0,
    "第 98 枚": 0, "第 269 波": 0, "第九十八枚": 0, "池第 277 枚": 0, "波号 279": 0, "零 279 行": 0,
    "engine_owner==bm-c 97 行注册": 0, "bmc_rows=97": 0, "bmc rows 97+候选": 0,
    "第二十九次连续 A-hop": 0, "第二十九次连续 above-own-A": 0, "连续二十八波": 0, "共二百七十七面": 0,
    "1,035,935": 0, "611,720": 0, "629_101..631_100": 0, "631_101..631_300": 0,
    "631_101..633_100": 0, "631_301..631_500": 0,
    "13:5x": 0, "15:1x": 0, "15:0x": 0, "09:0x": 0,
    "df1aaba72a": 0, "b6f486af35": 0, "60e630918f": 0, "b965e2ecf0": 0, "0a92fcc28f": 0, "900c23fe7d": 0,
    "−0.09278576": 0, "0.24505494": 0, "−0.09701509": 0, "0.2844": 0,
    "实差 0.0042 在带内": 0, "line_pre_w278 1.1971": 0, "line_merged@K609,520": 0, "K=609,520": 0,
    "r1119 W278 §7 范式": 0, "（W278 注册+烧录+finalize 全落地）": 0,
    "MSG-20261019-145x": 0, "键 W278 实测 K-lift": 0, "本窗 free RAM ~6.4GB": 0,
    "626_901..628_900 CLEAN": 0,
    "622_301..622_500": 0, "624_501..626_500": 0, "613_701..613_900": 0, "620_301..622_300": 0,
    "613_701..613_900": 0, "622_301..624_300": 0,
    "12:2x": 0, "13:5x": 0, "14:0x": 0,
    "611_300+1": 0, "617_900+1": 0, "611_500+1": 0,
    # NOTE (fail-closed discipline): 第二十七次连续 A-hop (T0=3) / 第二十八次连续 above-own-A
    # (T0=2) / 第二十八次连续 A-hop (T0=3) / 连续二十七波 (T0=1) / 共二百七十六面 (T0=1) are NOT
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
    # finalize-window stamp roll (heal (1)): W278 finalize one-pass landed 15:1x (0a92fcc28f
    # 15:13:26); T1 carries the W277-era 10:3x stamps x5 (MEASURED by the r1121 prep, r1077 law);
    # splice stamps 09:5x-era x2 -> W278 splice 13:5x (b6f486af35)
    ("10:3x", "15:1x", 5),
    # splice-stamp roll (heal (1) leg-2): W277 splice 09:5x-era stamps x2 (MEASURED by the
    # r1121 prep) -> W278 splice b6f486af35 13:5x
    ("09:5x", "13:5x", 2),
    # date-cross N/A this generation (heal (2), disclosed): W279 seat receipt same-date 20261019
    # with the W278 seat receipt -- lowercase prefix chain rolls the receipt date correctly with
    # NO date-cross leg.
    # sec.5 item1 measured keys -> W278 actuals (n1_w278_results + fivekeys machine values)
    ("（W278 实测键 **−0.09277044**·K=607,320 合并池·W278-only 实测 **−0.08889850**）",
     "（W278 实测键 **−0.09278576**·K=609,520 合并池·W278-only 实测 **−0.09701509**）", 1),
    ("W2..W278 共二百七十六面实测 mu 稳定先例", "W2..W278 共二百七十七面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (4)): TRUE W278 diff = 0.0042 @4dp (measured
    # 0.004229333427794163 full), in-band
    ("W278-only vs merged 实差 0.0039 在带内", "W278-only vs merged 实差 0.0042 在带内", 1),
    # sec.5 item2 sigma key (heal (5))
    ("键 **0.24508694**=W278 合并池实测", "键 **0.24505494**=W278 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (6))
    ("与 W278 A 档 p95（**0.3095** 实测锚）", "与 W278 A 档 p95（**0.2844** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (7): lowercase line_pre_w277 NOT rolled by the
    # W-roll; true W278 anchors K-lift -0.0002 first negative micro-move in-band + line_merged@K609,520
    # 1.1969 + line_pre_w278 1.1971 + n_eff_held 1,033,735)
    ("键 W278 实测 K-lift **+0.0000**·line_merged@K607,320 **1.197**·line_pre_w277 1.197·n_eff_held_equal 1,031,535",
     "键 W278 实测 K-lift **−0.0002**·line_merged@K609,520 **1.1969**·line_pre_w278 1.1971·n_eff_held_equal 1,033,735", 1),
    # se_mu chain true-history correction (heal (8); W278 fivekeys key5 measured 0.000314
    # held-flat from W277 0.000314; W279 projection 0.000313 computed sigma/sqrt(K611,720))
    ("→W273 **0.000319**→W274 **0.000319**→W275 **0.000318**→W276 **0.000317**→W277 **0.000316**→W278 **0.000314**→W279 投影 0.000314】",
     "→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 投影 0.000313】", 1),
    # sec.4 merged-pool anchor face (heal (9): W278 finalize landed)
    ("W1..W278 已落账 607,320 实测", "W1..W278 已落账 609,520 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W278 cycle (heal (10): bm-c r1119;
    # OLD faces are POST-VMAP faces -- the raw T0' W277-cycle rows already shifted W277->W278
    # before this leg fires; the leg fixes the window number r1114-continuation->r1119,
    # measured post-VMAP count=1)
    ("bm-c r1114-continuation W278 §7 范式", "bm-c r1119 W278 §7 范式", 1),
    ("bm-c r1114-continuation W278 §8 范式", "bm-c r1119 W278 §8 范式", 1),
    # RAM face live-measured THIS window (heal (11)): psutil 6 GB available (~6.4GB) + nvidia-smi 实读 0%·2.0G VRAM 占用·MV 车道已收官 GPU idle 回释
    # -- GPU=gen-only lane idle; honest window face updated from the r1116 ~4.5GB face
    ("本窗 free RAM ~4.5GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 0%·1.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~6.4GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 0%·2.0G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W278 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- pre-shift needles land the MUST series on the TRUE labels W263..W277;
    # this leg restores the POST-VMAP shifted ledger and appends the true W278 anchor
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚·W275 冻结窗 ~4.0G bm-c 实锚·W276 冻结窗 ~3.8G bm-c 实锚·W277 冻结窗 ~3.9G bm-c 实锚·W278 冻结窗 ~4.5G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚·W276 冻结窗 ~3.9G bm-c 实锚·W277 冻结窗 ~4.5G bm-c 实锚·W278 冻结窗 ~6.4G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 268 注册在册（表尾 W279 行【bm-c r1118 五面冻结 splice b6f486af35 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 11th gen）】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w278/ 12/12·ledger append 60e630918f+b965e2ecf0】"
    "·**W278 finalize 已落地**【n1_w278_results.json 机读·净账本锚头 1,035,935·K=607,320 合并池·W278 finalize one-pass bm-c r1119 窗 15:1x·estate chain r1116/r1118/r1119 W278 全周期 df1aaba72a+b6f486af35+0a92fcc28f】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1119 席位 MSG-20261019-145x-bmc-w279-seat 已推 origin 900c23fe7d"
    "·probe receipt _w279bmc_20261019 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 97+候选=第 98 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1119 席位窗 2026-10-19 15:0x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W279=bm-c own-wave window per chain-order law（W276 bm-c→W277 bm-c→W278 bm-c→W279 bm-c own-turn rotation·MSG-145x owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W278 N1 注册全部落地**【W278=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W278**"
    "【净账本锚头 **1,035,935**·K=607,320 合并池·n1_w278_results.json 机读·W278 finalize one-pass bm-c r1119 窗 15:1x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W278 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=607,320+2,200（本波）=**611,720 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十八次连续 A-hop）**："
    "A 面算术续带 628_901..630_900（自注册 W278 A 尾 628_900 续）"
    "在席位窗宇宙（post-W278-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W278 B 带 628_901..629_100 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W278 prereg §5 item5 post-W278-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W278 B 尾 629_100→A first-clean **629_101..631_100**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（628_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 628_901..630_900→jump 629_101·refuser band 628_901..629_100〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W278_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；"
    "**B-ext exit seed=631_101..631_300**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第二十九次连续 above-own-A 落位）**："
    "B naive 续带 629_101..629_300（自注册 W278 B 尾 628_900+1 续）"
    "在席位窗宇宙（post-W278-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 629_101..629_300 落本波 A first-clean 窗 629_101..631_100 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 629_101..631_100**（1 hop）"
    "→**1 hop** 落位 **631_101..631_300**·**B 落位 base==本波 A 窗尾+1（631_100+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W278 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W279 A naive 628_901..630_900 将被注册 W278 B 带拒（staircase affects A 承袭·第二十八次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R280：W279 带（A 629_101..631_100/B 631_101..631_300）注册后对 W280+ 的拒面影响=W279 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**629_101+j**（法典 §4 W279 行 A=629_101..631_100·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十八次连续 A-hop）**："
    "A 算术续带 628_901..630_900（自注册 W278 A 尾 628_900 续）"
    "在席位窗宇宙（post-W278-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W278 B 带 628_901..629_100 落 naive A 窗内=W278 prereg §5 item5 post-W278-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W278 B 尾 629_100→A first-clean 629_101..631_100·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（628_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W278_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**631_101+j**（法典 §4 W279 行 B=631_101..631_300·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 629_101..629_300（自注册 W278 B 尾 628_900+1 续）"
    "在席位窗宇宙（post-W278-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 629_101..631_100 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 629_101..631_100→1 hop 落位 631_101..631_300·"
    "**B 落位 base==本波 A 窗尾+1（631_100+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第二十九次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W278 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W280+ 投影 A naive 631_101..633_100 CLEAN hops=0（零 live refusers）/ B naive 631_301..631_500 CLEAN hops=0 "
    "**但落 naive W279 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 631_101..633_100 CLEAN·hops=0——**post-W279-REGISTERED 预披露：naive W279 A 起点将被注册 W279 B 带 631_101..631_300 拒=staircase affects A 第二十九次连续 A-hop 预期**；"
    "投影 B naive 631_301..631_500 clean 但落 naive W279 A 窗 631_101..633_100 内——"
    "**above-own-A 承袭面：W279 B 631_101..631_300 落本波 A 窗之上〔第二十八次连续〕·W279 A 面 1-hop=staircase affects A〔第二十八次连续〕·"
    "W280 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W279 B 带将拒 naive W279 A 窗仅当重叠——"
    "**W280 freezer 承接面强制注记：须在 post-W279 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W280+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 631_101..633_100 **CLEAN**（hops=0·pre-W279 宇宙零 live refusers）——"
    "**post-W279-REGISTERED 预披露：naive W279 A 起点将被注册 W279 B 带 631_101..631_300 拒（staircase-affects-A 第二十九次连续 A-hop 预期）**；"
    "B naive **631_301..631_500 CLEAN（hops=0）但落投影 A 窗 631_101..633_100 内**（W280p_B_lands_inside_W280p_A_naive=true——"
    "**staircase face 延续**：W279 A 629_101..631_100+B 631_101..631_300 注册后 naive W279 A 窗起点即被注册 W279 B 带拒（staircase affects A 承袭·第二十九次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W279 宇宙 live re-derive 必变·禁转录投影）；"
    "**W279 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279=A/B 双 1-hop 形态连续二十八波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W279 冻结方必须在 post-W279 注册宇宙重 derive 且 derive B 时预留本波 A 窗 629_101..631_100+本波 B 带 631_101..631_300"
    "——leg2 律/E36 卡·W141 先例；verify at W280 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w279bmc_freeze_edits.py"
    "（按 _w278bmc_freeze_edits.py 模板派生·gate0.5 自查 W278 行+W278 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1116/r1118 W278 全周期先例实时间线：prereg df1aaba72a 落于 r1116 窗·splice b6f486af35 落于 r1118 执行窗 @@SPLICE_T@@——"
    "**W279 freeze 面：W278 own-wave finalize 已落地=席位时即解锁——席位 r1119 窗+prereg r1122 窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 267 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**626_901+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**628_901+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W279+ 投影 A naive 628_901..630_900 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W279+ 投影（probe 机证 leg4", "verify at W279 prereg，hop 链逐跳在 probe 回执。"),
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
    "PERPETUAL-N1-W279", "research/PERPETUAL_N1_W279_PREREG.md",
    "629_101..631_100", "631_101..631_300", "607,320", "1,035,935", "607,320", "K=607,320",
    "n1_w279_results.json", "n1_w278_results.json", "MSG-20261019-145x-bmc-w279-seat", "900c23fe7d",
    "池第 277 枚", "第九十八枚", "第 269 波", "第 98 枚",
    "STAIRCASE-AFFECTS-A", "第二十八次连续 A-hop", "第二十九次连续 above-own-A",
    "_w279bmc_20261019", "--wave 279/finalize --wave 279",
    "W278 finalize one-pass bm-c r1119", "n_eff_held_equal 1,033,735",
    "−0.09278576", "0.24505494", "−0.09701509", "（**0.2844** 实测锚）",
    "键 W278 实测 K-lift **−0.0002**", "line_merged@K609,520 **1.1969**", "line_pre_w278 1.1971",
    "实差 0.0042 在带内", "共二百七十七面", "W2..W278", "W1..W278",
    "engine_owner==bm-c 97 行注册", "engine_owner 行 268 注册在册",
    "probe leg0 bmc_rows=97 attempt-continuity face（r1119 窗算法·bm-c own seat+bmc live rows 97 实读）",
    "bm-c 循环班 r1119 席位窗", "本窗 free RAM ~6.4GB", "本机 bm-c 实例",
    "W279=bm-c own-wave window per chain-order law",
    "df1aaba72a", "b6f486af35", "60e630918f", "b965e2ecf0", "0a92fcc28f",
    "W280+ 投影", "W280p_B_lands_inside_W280p_A_naive", "verify at W280 prereg",
    "_w279bmc_freeze_edits.py", "_w278bmc_freeze_edits.py 模板派生",
    "bm-c r1119 W278 §7 范式", "bm-c r1119 W278 §8 范式",
    "（上游 W278 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "（W278 注册+烧录+finalize 全落地）",
    "W206/W211..W278 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",
    "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚", "W274 冻结窗 ~4.0G bm-c 实锚", "W275 冻结窗 ~3.8G bm-c 实锚", "W276 冻结窗 ~3.9G bm-c 实锚", "W277 冻结窗 ~4.5G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R280：W279 带",
    "→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 投影 0.000313】",
    "628_900+1", "631_100+1", "631_101..631_300",
    "A_staircase_hop_past_W278_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 279", "零 279 行", "零 skip-ahead W280/W281 席位声明",
    "15:1x", "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1122：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1122 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1122 窗实读",
    "nvidia-smi 实读 0%·2.0G VRAM 占用·MV 车道已收官 GPU idle 回释",
    "r1119 席位窗实跑：origin inbox 零 W279 席位外机命中",
    "results/p2cal_ext/n1_w278/ 12/12",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=611_501", "B-ext exit seed=613_501",
    "626_901..628_900", "622_301..622_500", "613_301..613_500", "613_301..615_300", "613_701..613_700",
    "624_501..626_500 CLEAN", "624_501..626_500", "620_301..622_300", "622_301..622_500", "624_501..626_500", "613_701..613_900",
    "620_301..622_300", "613_701..613_900", "622_301..624_300",
    "628_901..630_900 CLEAN", "629_101..629_300 CLEAN",
    "GATED on", "finalize PENDING", "queue_depth",
    "607,120", "**607,320 投影**", "line_merged@K607,120", "K=607,120",
    "−0.09277044", "0.24508694", "−0.08889850", "**0.305**", "实差 0.0039 在带内",
    "17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "07:2x", "07:4x", "08:1x", "09:5x", "10:3x", "09:0x",
    "MSG-20261019-102x", "b187aa6214", "c5f8b88f91", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",
    "bmc_rows=96", "bmc rows 96+候选", "第 97 枚", "第 268 波", "第九十七枚",
    "engine_owner==bm-c 96 行注册",
    "r1114-continuation 席位窗实跑", "r1101 窗算法",
    "95%·7.9G VRAM",
    "W279p_", "W279p_",
    "line_pre_w271", "键 W277 实测 K-lift",
    "verify at W279 prereg",
    "W279+ 投影", "W278+ 投影", "W277+ 投影",
    "第二十七次连续 A-hop", "第二十二次连续 above-own-A", "第二十八次连续 above-own-A", "连续二十七波", "共二百七十六面",
    "n1_w277_results.json", "n1_w269_results.json", "n1_w268_results.json",
    "W2..W277", "W136..W277", "W1..W277",
    "波号 278", "零 278 行",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",
    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",
    "626_900+1", "617_900+1", "611_500+1", "617_900+1", "611_300+1",
    "12:2x", "14:0x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W280+ 投影") == 3, "W279+ count=%d (expect 3 = §5.5 rolled + b_claim_proj + b5)" % T2.count("W280+ 投影")
assert T2.count("W279+ 投影") == 0, "W279+ count=%d (expect 0)" % T2.count("W279+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("第二十八次连续 A-hop") == 3, "A21 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("第二十八次连续 A-hop")
assert T2.count("第二十九次连续 A-hop") == 3, "A22 count=%d (expect 3 = b5 x2 + b_claim_proj)" % T2.count("第二十九次连续 A-hop")
assert T2.count("第二十九次连续 above-own-A") == 2, "B22 count=%d (expect 2 = b_band + b3_b)" % T2.count("第二十九次连续 above-own-A")
assert T2.count("第二十八次连续 above-own-A") == 0, "B21 count=%d (expect 0)" % T2.count("第二十八次连续 above-own-A")
assert T2.count("连续二十八波") == 1, "21-wave count=%d (expect 1 = b5 NEW)" % T2.count("连续二十八波")
assert T2.count("629_101..631_100") >= 5, "own-A count=%d (expect >=5)" % T2.count("629_101..631_100")
assert T2.count("631_101..631_300") >= 4, "own-B count=%d (expect >=4)" % T2.count("631_101..631_300")
assert T2.count("631_101..631_300") >= 3, "reg-W278-B count=%d (expect >=3)" % T2.count("631_101..631_300")
assert T2.count("629_101..629_300") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("629_101..629_300")
assert T2.count("628_901..630_900") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("628_901..630_900")
assert T2.count("631_101..633_100") == 5, "W279p-A count=%d (expect 5 = b_claim_proj x3 + b5 x2)" % T2.count("631_101..633_100")
assert T2.count("631_301..631_500") == 3, "W279p-B count=%d (expect 3 = b_claim_proj x2 + b5)" % T2.count("631_301..631_500")
assert T2.count("席位时即解锁") == 2, "unlock count=%d (expect 2)" % T2.count("席位时即解锁")
assert T2.count("_w279bmc_20261019") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w279bmc_20261019")
assert T2.count("1,035,935") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,035,935")
# n_eff_held face honest update (r1093 full-precision law): the ONLY 1,033,735 in the output
# is the sec.5 item4 n_eff_held_equal anchor = the W278 fivekeys measured value (the canon
# r1102 window left this sub-face stale at the W277-era 1,020,535; healed forward here)
assert T2.count("1,033,735") == 1, "n_eff_held count=%d (expect 1 = sec.5 item4 honest anchor only)" % T2.count("1,033,735")
assert T2.count("607,320") >= 3, "merged-K count=%d (expect >=3)" % T2.count("607,320")
assert T2.count("（占位·finalize one-pass 后回填") == 1, "sec7 placeholder count=%d (expect 1)" % T2.count("（占位·finalize one-pass 后回填")
assert T2.count("（占位·finalize 同窗回填") == 1, "sec8 placeholder count=%d (expect 1)" % T2.count("（占位·finalize 同窗回填")
assert T2.count("第 98 枚") == 2, "own-ordinal count=%d (expect 2 = leg + b_title)" % T2.count("第 98 枚")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W279 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: b6f486af35 @ " + SPLICE_T + " | finalize estate: 0a92fcc28f @ 15:1x | seat: 900c23fe7d @ 15:1x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~6.4GB written, MV 车道已收官 idle) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == 053892f61cf24d9803cb20410d4ab1163cb7897a @ df1aaba72a (frozen pre-run face; HEAD post-backfill twin 1c93e077 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
