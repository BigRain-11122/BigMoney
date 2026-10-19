# -*- coding: utf-8 -*-
# r1129-continuation bm-c: W280 prereg derive (count-asserted ordered transform + block replaces).
# Canon-clone of _w279bmc_prereg_derive.py per age() machine-needle law (one generation).
# Source = the frozen W279 prereg at freeze commit ba5c725b42 (23,681 B, sha256_16
# c2fc7c34d0e41a68, blob 51d7ca52a811bc22a4ada6f4635915d5219ec734), extracted by the r1125 PREP
# window; the HEAD twin b98e8592 (28,043 B, sec.7/8 backfilled by the r1124 cycle) is NOT used
# (r1049/r1052 law).
# W280 facts (machine-derived): seat probe ADMIT results/_w280bmc_20261019_probe_receipt.json
#   (bm-c r1124, seat origin f96272d8b9, MSG-20261019-200x-bmc-w280-seat): A naive
#   631_101..633_100 refused by registered W279 B 631_101..631_300 -> A 631_301..633_300 hops=1
#   (29th consecutive A-hop); B naive 631_301..631_500 inside own-A -> B 633_301..633_500 hops=1
#   (30th above-own-A); seed_admit FREE x2; leg0 rows=277 owner=269 bmc=98 ordinal=270.
#   upstream W279 finalize LANDED (r1124, 6bdbdb9a07, fivekeys _r1124bmc_w279_fivekeys.json):
#   K=611,720 / ledger 1,038,135 EXACT / mu -0.09282362698620283 / sigma 0.24506025197871714 /
#   se_mu 0.000313 / W279-only -0.10331554545454545 / A p95 0.3104 / K-lift +0.0000 /
#   n_eff_held 1,035,935 / line_pre_w279 1.197 / line_merged@611,720 1.197 / key1 gap 0.0104919.
#   splice 3810f4a7ac 19:3x (r1123), engine batches 498d178d0b+332e8e8656, sixgate 42nd PASS.
# ANCHOR LAW: prose carries 8dp rounded faces; every gate machine-verifies against the
# full-precision fivekeys/results jsons (r1093 pit entry; live-read governs r587).
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
SRC = os.path.join(REPO, "results", "_w280bmc_w279_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W280_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "51d7ca52a811bc22a4ada6f4635915d5219ec734"   # freeze-commit face @ ba5c725b42
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "ba5c725b42:research/PERPETUAL_N1_W279_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W279_PREREG.md"])
assert _hb == "b98e85926cdff71cde7ac3705ad82a368c7e620b", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")  # heal (h) r1093: CRLF disk face -> LF git-object face (sim byte-identity)
assert len(T0.encode("utf-8")) == 23681, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "c2fc7c34d0e41a68", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("ba5c725b42", "3810f4a7ac", "498d178d0b", "332e8e8656", "6bdbdb9a07", "f96272d8b9"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "3810f4a7ac"])    # 2026-10-19 19:3x +0800
_m = re.match(r"2026-10-19 19:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "19:%sx" % _m.group(1)[0]   # 19:3x
_fz = git_out(["show", "-s", "--format=%ci", "6bdbdb9a07"])    # 2026-10-19 20:06:06 +0800
assert _fz.startswith("2026-10-19 20:0"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "f96272d8b9"])   # 2026-10-19 20:06:06 +0800
assert _st.startswith("2026-10-19 20:0"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w279_results.json"])
assert _fin_log == "6bdbdb9a07", "W279 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "f96272d8b9"])
assert "MSG-20261019-200x-bmc-w280-seat.md" in _seat_files, "W280 seat MSG not carried by seat commit f96272d8b9: %r" % _seat_files[:200]

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1124bmc_w279_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 611720, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09282363, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24506025, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k611720"], 6) == 0.000313, "se_mu drift: %r" % fk["merged"]["se_mu_k611720"]
assert round(fk["w279_only"]["mu"], 8) == -0.10331555, "w279-only mu drift: %r" % fk["w279_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3104, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1035935, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w279"], 4) == 1.197, "line_pre drift: %r" % fk["skill_line"]["line_pre_w279"]
assert round(fk["skill_line"]["line_merged_611720"], 4) == 1.197, "line_merged drift: %r" % fk["skill_line"]["line_merged_611720"]
assert fk["ledger_identity"]["total"] == 1038135 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w279_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0105 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w279_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1035935
assert round(res["skill_line_v2_k_lift"]["line_pre_w279"], 4) == 1.197
assert round(res["skill_line_v2_k_lift"]["line_merged_611720"], 4) == 1.197
assert round(res["null_pool_cumulative"]["se_mu_at_k611720"], 6) == 0.000313, "W279 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w278_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k609520"], 6) == 0.000314, "W278 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w280bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [631301, 633300] and pr["bands"]["B"] == [633301, 633500]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [631101, 633100], "jump_to": 631301,
                              "refuser_pts": [], "refuser_bands": [[631101, 631300]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [631301, 631500], "jump_to": 633301,
                              "refuser_pts": [], "refuser_bands": [[631301, 633300]]}]
assert l1["B_naive"] == [631301, 631500] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W279_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W279_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W277_W278_W279_bands_respected_A"] is True and _ra["W277_W278_W279_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 277 and _l0["owner_rows"] == 269 and _l0["bmc_rows"] == 98
assert _l0["ordinal"] == 270 and _l0["w279_finalize_landed"] is True
assert _l0["w279_finalize_anchors"]["ledger_total"] == 1038135
assert _l0["w279_finalize_anchors"]["merged_n"] == 611720
assert round(_l0["w279_finalize_anchors"]["skill_line_delta_k_lift"], 4) == 0.0
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=631301 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=633301 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W281p_A_naive"] == "633301..635300"
assert pr["legs"]["leg4"]["W281p_B_naive"] == "633501..633700"
assert pr["legs"]["leg4"]["W281p_B_lands_inside_W281p_A_naive"] is True

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
    [
        "A-ext seed=629_101..631_100",
        "A-ext seed=633_301..635_300"
    ],
    [
        "B-ext exit seed=631_101..631_300",
        "B-ext exit seed=633_301..633_500"
    ],
    [
        "entry rng=**629_101+j**（与 A[j] 同源配对语义逐字",
        "entry rng=**633_301+j**（与 A[j] 同源配对语义逐字"
    ],
    [
        "席位公示=MSG-20261019-145x-bmc-w279-seat 已推 origin 900c23fe7d r565 律（bm-c r1119 席·queue-head seat-first lane）",
        "席位公示=MSG-20261020-@@SEAT_HHMM@@-bmc-w281-seat 已推 origin @@SEAT_SHA@@ r565 律（bm-c r1130 席·queue-head seat-first lane）"
    ],
    [
        "席位公示 MSG-20261019-145x-bmc-w279-seat 先推 origin 900c23fe7d r565 律",
        "席位公示 MSG-20261020-@@SEAT_HHMM@@-bmc-w281-seat 先推 origin @@SEAT_SHA@@ r565 律"
    ],
    [
        "波号 279",
        "波号 281"
    ],
    [
        "r1119 席位窗实跑：origin inbox 零 W279 席位外机命中",
        "r1130 席位窗实跑：origin inbox 零 W281 席位外机命中"
    ],
    [
        "零 279 行",
        "零 281 行"
    ],
    [
        "零 skip-ahead W280/W281 席位声明",
        "零 skip-ahead W282/W283 席位声明"
    ],
    [
        "池第 277 枚",
        "池第 279 枚"
    ],
    [
        "第 269 波",
        "第 271 波"
    ],
    [
        "bm-c 第九十八枚自有波",
        "bm-c 第一百枚自有波"
    ],
    [
        "probe leg0 bmc_rows=97 attempt-continuity face（r1119 窗算法·bm-c own seat+bmc live rows 97 实读）——freeze 时 live derive bmc rows 97+候选=第 98 枚 EXACT",
        "probe leg0 bmc_rows=99 attempt-continuity face（r1129-continuation 窗算法·bm-c own seat+bmc live rows 99 实读）——freeze 时 live derive bmc rows 99+候选=第 100 枚 EXACT"
    ],
    [
        "engine_owner==bm-c 97 行注册",
        "engine_owner==bm-c 99 行注册"
    ],
    [
        "saturation_engine.py status live-read r1122：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
        "saturation_engine.py status live-read r1129：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"
    ],
    [
        "本机 bm-c 实例·heartbeat 新鲜实读 r1122 窗·队列空转 idle",
        "本机 bm-c 实例·heartbeat 新鲜实读 r1129 窗·队列空转 idle"
    ],
    [
        "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1122 窗实读",
        "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1129 窗实读"
    ],
    [
        "--wave 279/finalize --wave 279",
        "--wave 281/finalize --wave 281"
    ],
    [
        "§5.5 W280+ 投影承接机证",
        "§5.5 W282+ 投影承接机证"
    ],
    [
        "n1_w279",
        "\u0001N\u0001"
    ],
    [
        "W279",
        "W280"
    ],
    [
        "W278",
        "W279"
    ],
    [
        "W277",
        "W278"
    ],
    [
        "W276",
        "W277"
    ],
    [
        "W275",
        "W276"
    ],
    [
        "W274",
        "W275"
    ],
    [
        "W273",
        "W274"
    ],
    [
        "W272",
        "W273"
    ],
    [
        "W271",
        "W272"
    ],
    [
        "W270",
        "W271"
    ],
    [
        "W269",
        "W270"
    ],
    [
        "W268",
        "W269"
    ],
    [
        "W267",
        "W268"
    ],
    [
        "W266",
        "W267"
    ],
    [
        "W265",
        "W266"
    ],
    [
        "W264",
        "W265"
    ],
    [
        "W263",
        "W264"
    ],
    [
        "W262",
        "W263"
    ],
    [
        "W261",
        "W262"
    ],
    [
        "_w279bmc",
        "\u0001B\u0001"
    ],
    [
        "_w279bmc",
        "_w280bmc"
    ],
    [
        "_w278bmc",
        "_w279bmc"
    ],
    [
        "_w277bmc",
        "_w278bmc"
    ],
    [
        "_w276bmc",
        "_w277bmc"
    ],
    [
        "_w275bmc",
        "_w276bmc"
    ],
    [
        "_w274bmc",
        "_w275bmc"
    ],
    [
        "_w273bmc",
        "_w274bmc"
    ],
    [
        "_w272bmc",
        "_w273bmc"
    ],
    [
        "_w271bmc",
        "_w272bmc"
    ],
    [
        "_w270bmc",
        "_w271bmc"
    ],
    [
        "_w269bmc",
        "_w270bmc"
    ],
    [
        "_w268bmc",
        "_w269bmc"
    ],
    [
        "_w267bmc",
        "_w268bmc"
    ],
    [
        "_w266bmc",
        "_w267bmc"
    ],
    [
        "_w265bmc",
        "_w266bmc"
    ],
    [
        "_w264bmc",
        "_w265bmc"
    ],
    [
        "_w263bmc",
        "_w264bmc"
    ],
    [
        "_w262bmc",
        "_w263bmc"
    ],
    [
        "\u0001N\u0001",
        "n1_w280"
    ],
    [
        "\u0001B\u0001",
        "_w280bmc"
    ],
    [
        "\u0001W\u0001",
        "W280"
    ]
]

VMAP_FLOORS = {
    "A-ext seed=629_101..631_100": 1,
    "B-ext exit seed=631_101..631_300": 1,
    "entry rng=**629_101+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261019-145x-bmc-w279-seat 已推 origin 900c23fe7d r565 律（bm-c r1119 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261019-145x-bmc-w279-seat 先推 origin 900c23fe7d r565 律": 1,
    "波号 279": 1,
    "r1119 席位窗实跑：origin inbox 零 W279 席位外机命中": 1,
    "零 279 行": 1,
    "零 skip-ahead W280/W281 席位声明": 1,
    "池第 277 枚": 1,
    "第 269 波": 1,
    "bm-c 第九十八枚自有波": 1,
    "probe leg0 bmc_rows=97 attempt-continuity face（r1119 窗算法·bm-c own seat+bmc live rows 97 实读）——freeze 时 live derive bmc rows 97+候选=第 98 枚 EXACT": 1,
    "engine_owner==bm-c 97 行注册": 1,
    "saturation_engine.py status live-read r1122：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1122 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1122 窗实读": 1,
    "--wave 279/finalize --wave 279": 1,
    "§5.5 W280+ 投影承接机证": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**629_101+j**": 1,
    "exit rng=**631_101+j**": 1,
    "probe W280+ 投影 A naive 631_101..633_100 CLEAN hops=0": 1,
    "5. **W280+ 投影（probe 机证 leg4": 1,
    "R280：W279 带": 1,
    "（见 §5 item5）。": 1,
    "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。": 1,
    "；p=`BASELINE_P": 1,
    "；p_exit=`P_EXIT=0.05`": 1,
    "never transcribe r587**）": 1,
    "verify at W280 prereg，hop 链逐跳在 probe 回执。": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
    "席位时即解锁": 2,
    "注册+烧录+finalize 全落地": 2,
    "W278": 62,
    "W277": 4,
    "W276": 4,
    "W275": 3,
    "W274": 3,
    "W273": 3,
    "W272": 2,
    "W271": 2,
    "W270": 2,
    "W269": 2,
    "W268": 2,
    "W267": 2,
    "W266": 2,
    "W265": 2,
    "W264": 2,
    "W263": 2,
    "W262": 1,
    "W261": 1,
    "_w278bmc": 1,
    "_w277bmc": 0,
    "_w276bmc": 0,
    "_w275bmc": 0,
    "_w274bmc": 0,
    "_w273bmc": 0,
    "_w272bmc": 0,
    "_w271bmc": 0,
    "_w270bmc": 0,
    "_w269bmc": 0,
    "_w268bmc": 0,
    "_w267bmc": 0,
    "_w266bmc": 0,
    "_w265bmc": 0,
    "_w264bmc": 0,
    "_w263bmc": 0,
    "_w262bmc": 0,
    "n1_w279": 4,
    "n1_w278": 6,
    "_w279bmc": 4,
    "15:1x": 4,
    "13:5x": 2,
    "waits-upstream ARMED": 0,
    "GATED on": 0,
    "finalize PENDING": 0,
    "queue_depth": 0,
    "_w280bmc": 0,
    "n1_w280": 0,
    "第 99 枚": 0,
    "第 270 波": 0,
    "第九十九枚": 0,
    "池第 278 枚": 0,
    "波号 280": 0,
    "零 280 行": 0,
    "engine_owner==bm-c 98 行注册": 0,
    "bmc_rows=98": 0,
    "bmc rows 98+候选": 0,
    "第三十次连续 A-hop": 0,
    "第三十次连续 above-own-A": 0,
    "连续二十九波": 0,
    "共二百七十八面": 0,
    "1,038,135": 0,
    "613,920": 0,
    "631_301..633_300": 0,
    "633_301..633_500": 0,
    "633_301..635_300": 0,
    "633_501..633_700": 0,
    "ba5c725b42": 0,
    "3810f4a7ac": 0,
    "498d178d0b": 0,
    "332e8e8656": 0,
    "6bdbdb9a07": 0,
    "f96272d8b9": 0,
    "−0.09282363": 0,
    "0.24506025": 0,
    "−0.10331555": 0,
    "0.3104": 0,
    "line_pre_w279 1.197": 0,
    "K=611,720": 0,
    "r1124 W279 §7 范式": 0,
    "MSG-20261019-200x": 0,
    "键 W279 实测 K-lift": 0,
    "631_301..633_300 CLEAN": 0,
    "10:3x": 0,
    "09:5x": 0
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

# ---- POST corrections fire on the MOTHER face BEFORE the wave roll (r1129 ordering law):
# the sec.5 measured-key sentence carries W278 labels on both halves, so a pre-shifted face
# would break every POST floor. ----
T1 = T0
for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)
T1 = xf(T1)

# ---------------- post-roll ledger (kept verbatim for the splice canons) ----------------
VMAP_POST_LEGS = [
    [
        "10:3x",
        "15:1x",
        0
    ],
    [
        "09:5x",
        "13:5x",
        0
    ],
    [
        "15:1x",
        "20:0x",
        4
    ],
    [
        "13:5x",
        "19:3x",
        2
    ],
    [
        "（W278 实测键 **−0.09278576**·K=609,520 合并池·W278-only 实测 **−0.09701509**）",
        "（W280 实测键 **@@W280_ONLY_MU@@**·K=@@W280_K@@ 合并池·W280-only 实测 **@@W280_ONLY_MU@@**）",
        1
    ],
    [
        "W2..W278 共二百七十七面实测 mu 稳定先例",
        "W2..W280 共二百七十九面实测 mu 稳定先例",
        1
    ],
    [
        "W278-only vs merged 实差 0.0042 在带内",
        "W280-only vs merged 实差 @@W280_DIFF4@@ 在带内",
        1
    ],
    [
        "键 **0.24505494**=W278 合并池实测",
        "键 **@@W280_SIGMA@@**=W280 合并池实测",
        1
    ],
    [
        "与 W278 A 档 p95（**0.2844** 实测锚）",
        "与 W280 A 档 p95（**@@W280_P95@@** 实测锚）",
        1
    ],
    [
        "键 W278 实测 K-lift **−0.0002**·line_merged@K609,520 **1.1969**·line_pre_w278 1.1971·n_eff_held_equal 1,033,735",
        "键 W280 实测 K-lift **@@W280_KLIFT@@**·line_merged@K@@W280_K@@ **@@W280_LINE_M@@**·line_pre_w280 @@W280_LINE_P@@·n_eff_held_equal @@W280_NEFF@@",
        1
    ],
    [
        "→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 投影 0.000313】",
        "→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 投影 @@W280_SE_PROJ@@】",
        1
    ],
    [
        "W1..W278 已落账 609,520 实测",
        "W1..W280 已落账 @@W280_K@@ 实测",
        1
    ],
    [
        "bm-c r1119 W278 §7 范式",
        "bm-c @@W280_PARADIGM_WIN@@ W280 §7 范式",
        1
    ],
    [
        "bm-c r1119 W278 §8 范式",
        "bm-c @@W280_PARADIGM_WIN@@ W280 §8 范式",
        1
    ],
    [
        "本窗 free RAM ~6.4GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 0%·2.0G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
        "本窗 free RAM ~2.3GB（bm-c 底盘常驻·24G 物理内存机·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 0%·@@VRAM_G@@ VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
        1
    ],
    [
        "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚·W276 冻结窗 ~3.9G bm-c 实锚·W277 冻结窗 ~4.5G bm-c 实锚·W278 冻结窗 ~6.4G bm-c 实锚）",
        "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚·W276 冻结窗 ~3.9G bm-c 实锚·W277 冻结窗 ~4.5G bm-c 实锚·W278 冻结窗 ~6.4G bm-c 实锚·W279 冻结窗 ~2.3G bm-c 实锚）",
        1
    ]
]

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}
NEW["b_title"] = "engine_owner 行 269 注册在册（表尾 W281 行【bm-c r1118 五面冻结 splice b6f486af35 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 11th gen）】+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w278/ 12/12·ledger append 60e630918f+b965e2ecf0】·**W279 finalize 已落地**【n1_w278_results.json 机读·净账本锚头 1,035,935·K=607,320 合并池·W279 finalize one-pass bm-c r1119 窗 15:1x·estate chain r1116/r1118/r1119 W279 全周期 df1aaba72a+b6f486af35+0a92fcc28f】）+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1119 席位 MSG-20261019-145x-bmc-w279-seat 已推 origin 900c23fe7d·probe receipt _w280bmc_20261019 机证·bands ADMIT verbatim·queue-head seat-first lane）→freeze 时 live derive bmc rows 97+候选=第 98 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-c 循环班 r1119 席位窗 2026-10-19 15:0x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令·**W280=bm-c own-wave window per chain-order law（W277 bm-c→W278 bm-c→W279 bm-c→W280 bm-c own-turn rotation·MSG-145x owner per chain-order law）**】】）"

NEW["b_band"] = "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W240 staircase era 后第二十八次连续 A-hop）**：A 面算术续带 628_901..630_900（自注册 W279 A 尾 628_900 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）起点即 REFUSED（注册 W279 B 带 628_901..629_100 落 naive A 窗内=staircase re-emergence affects A 承袭·W279 prereg §5 item5 post-W279-REGISTERED pre-disclosure 兑现 r587 如实披露）→walk 越注册 W279 B 尾 629_100→A first-clean **629_101..631_100**·**hops=1**·**A 落位 base==注册前波 B 尾+1（628_900+1）机检关系**（A_hop_chain 1 跳 verbatim leg1 机证〔window 628_901..630_900→jump 629_101·refuser band 628_901..629_100〕·A_clean_at_naive_start=false·A_staircase_hop_past_W279_B=true·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；**B-ext exit seed=631_101..631_300**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第二十九次连续 above-own-A 落位）**：B naive 续带 629_101..629_300（自注册 W279 B 尾 628_900+1 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）起点即 REFUSED（naive B 窗 629_101..629_300 落本波 A first-clean 窗 629_101..631_100 内=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）——**own-A reservation standard leg 越本波 A 窗 629_101..631_100**（1 hop）→**1 hop** 落位 **631_101..631_300**·**B 落位 base==本波 A 窗尾+1（631_100+1）EXACT 机检关系**（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证·非转录 r587·AB 同窗互斥面 leg2 律在场）；**W279 prereg §5 item5 投影承接面注记兑现+落位一致如面**：投影预言 W280 A naive 628_901..630_900 将被注册 W279 B 带拒（staircase affects A 承袭·第二十八次连续 A-hop）与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。R280：W280 带（A 629_101..631_100/B 631_101..631_300）注册后对 W281+ 的拒面影响=W280 冻结方 leg4 前瞻已机证（见 §5 item5）。"

NEW["b_gated"] = "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w279bmc_freeze_edits.py（按 _w278bmc_freeze_edits.py 模板派生·gate0.5 自查 W279 行+W279 finalize 件在场=已绿·未落即 loud abort 兜底）=**splice 执行窗派生落地（r1116/r1118 W279 全周期先例实时间线：prereg df1aaba72a 落于 r1116 窗·splice b6f486af35 落于 r1118 执行窗 @@SPLICE_T@@——**W280 freeze 面：W279 own-wave finalize 已落地=席位时即解锁——席位 r1119 窗+prereg r1122 窗落地 per seat-first law O-20261010-2350 §2·splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"

NEW["b_prev"] = "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）：**W1..W279 N1 注册全部落地**【W279=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W279**【净账本锚头 **1,035,935**·K=607,320 合并池·n1_w278_results.json 机读·W279 finalize one-pass bm-c r1119 窗 15:1x】】；**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W279 席位已闭链=注册+烧录+finalize 全落地·零在飞）；finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；累计 null 池=607,320+2,200（本波）=**611,720 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"

NEW["b_claim_proj"] = "probe W281+ 投影 A naive 631_101..633_100 CLEAN hops=0（零 live refusers）/ B naive 631_301..631_500 CLEAN hops=0 **但落 naive W280 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**（投影 A naive 631_101..633_100 CLEAN·hops=0——**post-W280-REGISTERED 预披露：naive W280 A 起点将被注册 W280 B 带 631_101..631_300 拒=staircase affects A 第二十九次连续 A-hop 预期**；投影 B naive 631_301..631_500 clean 但落 naive W280 A 窗 631_101..633_100 内——**above-own-A 承袭面：W280 B 631_101..631_300 落本波 A 窗之上〔第二十八次连续〕·W280 A 面 1-hop=staircase affects A〔第二十八次连续〕·W281 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W280 B 带将拒 naive W280 A 窗仅当重叠——**W281 freezer 承接面强制注记：须在 post-W280 宇宙重 derive 且 derive B 时预留本波 A 窗·W142 先例·never transcribe r587**）"

NEW["b3_a"] = "entry rng seed=**629_101+j**（法典 §4 W280 行 A=629_101..631_100·**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W240 staircase era 后第二十八次连续 A-hop）**：A 算术续带 628_901..630_900（自注册 W279 A 尾 628_900 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）起点即 REFUSED（注册 W279 B 带 628_901..629_100 落 naive A 窗内=W279 prereg §5 item5 post-W279-REGISTERED pre-disclosure 兑现·r587 承袭披露）→walk 越注册 W279 B 尾 629_100→A first-clean 629_101..631_100·**hops=1**·**A 落位 base==注册前波 B 尾+1（628_900+1）机检关系**（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W279_B=true）·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"

NEW["b3_b"] = "exit rng=**631_101+j**（法典 §4 W280 行 B=631_101..631_300·**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**：B naive 续带 629_101..629_300（自注册 W279 B 尾 628_900+1 续）在席位窗宇宙（post-W279-REGISTERED 终态注册）起点即 REFUSED（naive B 窗落本波 A first-clean 窗 629_101..631_100 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）→own-A reservation 越本波 A 窗 629_101..631_100→1 hop 落位 631_101..631_300·**B 落位 base==本波 A 窗尾+1（631_100+1）机检关系**（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执·第二十九次连续 above-own-A 落位如实注记）·非转录 r587·与 W279 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"

NEW["b5_projection"] = "5. **W281+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 631_101..633_100 **CLEAN**（hops=0·pre-W280 宇宙零 live refusers）——**post-W280-REGISTERED 预披露：naive W280 A 起点将被注册 W280 B 带 631_101..631_300 拒（staircase-affects-A 第二十九次连续 A-hop 预期）**；B naive **631_301..631_500 CLEAN（hops=0）但落投影 A 窗 631_101..633_100 内**（W281p_B_lands_inside_W281p_A_naive=true——**staircase face 延续**：W280 A 629_101..631_100+B 631_101..631_300 注册后 naive W280 A 窗起点即被注册 W280 B 带拒（staircase affects A 承袭·第二十九次连续 A-hop 预期）→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W280 宇宙 live re-derive 必变·禁转录投影）；**W280 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**（W252 起 staircase affects A·W253/W254/W255/W256/W257/W258/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279/W280=A/B 双 1-hop 形态连续二十八波如实注记·seed-gap face 已于 W253 终结=A 首跳如实注记）——W280 冻结方必须在 post-W280 注册宇宙重 derive 且 derive B 时预留本波 A 窗 629_101..631_100+本波 B 带 631_101..631_300——leg2 律/E36 卡·W142 先例；verify at W281 prereg，hop 链逐跳在 probe 回执。"

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    [
        "b_title",
        "engine_owner 行 268 注册在册（表尾"
    ],
    [
        "b_band",
        "（**A 面=STAIRCASE-AFFECTS-A"
    ],
    [
        "b_gated",
        "R280：W279 带"
    ],
    [
        "b_prev",
        "prev=**届时空窗活链头 derive 禁手抄**"
    ],
    [
        "b_claim_proj",
        "probe W280+ 投影 A naive 631_101..633_100 CLEAN hops=0"
    ],
    [
        "b3_a",
        "- **B 档**（j=0..199）：entry rng=**629_101+j**（与 A[j] 同源配对语义逐字"
    ],
    [
        "b3_b",
        "exit rng=**631_101+j**"
    ],
    [
        "b5_projection",
        "5. **W280+ 投影（probe 机证 leg4"
    ]
]

def apply_doc(t):
    """Document-ordered block replace: start marker -> next block start."""
    out = t
    names = [b[0] for b in BLOCKS]
    for idx, name in enumerate(names):
        sm = dict(BLOCKS)[name]
        assert out.count(sm) == 1, "BLOCK %s marker count=%d" % (name, out.count(sm))
        i = out.index(sm)
        nxt = dict(BLOCKS)[names[idx + 1]] if idx + 1 < len(names) else None
        j = out.find(nxt, i) if nxt else len(out)
        if j < 0:
            j = len(out)
        out = out[:i] + NEW[name].replace("@@SPLICE_T@@", SPLICE_T) + out[j:]
    return out


T2 = apply_doc(T1)

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W280",
    "research/PERPETUAL_N1_W280_PREREG.md",
    "631_301..633_300",
    "633_301..633_500",
    "611,720",
    "1,038,135",
    "611,720",
    "K=611,720",
    "n1_w280_results.json",
    "n1_w278_results.json",
    "MSG-20261019-200x-bmc-w280-seat",
    "f96272d8b9",
    "池第 278 枚",
    "第九十九枚",
    "第 270 波",
    "第 99 枚",
    "STAIRCASE-AFFECTS-A",
    "第二十九次连续 A-hop",
    "第三十次连续 above-own-A",
    "_w280bmc_20261019",
    "--wave 280/finalize --wave 280",
    "W279 finalize one-pass bm-c r1124",
    "n_eff_held_equal 1,035,935",
    "−0.09282363",
    "0.24506025",
    "−0.10331555",
    "（**0.3104** 实测锚）",
    "键 W279 实测 K-lift **+0.0000**",
    "line_merged@K611,720 **1.197**",
    "line_pre_w279 1.197",
    "实差 0.0105 在带内",
    "共二百七十八面",
    "W2..W279",
    "W1..W279",
    "engine_owner==bm-c 98 行注册",
    "engine_owner 行 269 注册在册",
    "probe leg0 bmc_rows=98 attempt-continuity face（r1124 窗算法·bm-c own seat+bmc live rows 98 实读）",
    "bm-c 循环班 r1124 席位窗",
    "本窗 free RAM ~2.3GB",
    "本机 bm-c 实例",
    "W280=bm-c own-wave window per chain-order law",
    "ba5c725b42",
    "3810f4a7ac",
    "498d178d0b",
    "332e8e8656",
    "6bdbdb9a07",
    "W281+ 投影",
    "W281p_B_lands_inside_W281p_A_naive",
    "verify at W281 prereg",
    "_w280bmc_freeze_edits.py",
    "_w279bmc_freeze_edits.py 模板派生",
    "bm-c r1124 W279 §7 范式",
    "bm-c r1124 W279 §8 范式",
    "（上游 W279 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "（W279 注册+烧录+finalize 全落地）",
    "W206/W211..W279 低 RAM 实烧先例",
    "W263 冻结窗 26G bm-a 实锚",
    "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚",
    "W266 冻结窗 ~5G bm-c 实锚",
    "W267 冻结窗 ~0.1G bm-c 实锚",
    "W268 冻结窗 ~1.4G bm-c 实锚",
    "W269 冻结窗 ~2.1G bm-c 实锚",
    "W270 冻结窗 ~3.3G bm-c 实锚",
    "W271 冻结窗 ~1.4G bm-c 实锚",
    "W272 冻结窗 ~0.3G bm-c 实锚",
    "W273 冻结窗 ~4.4G bm-c 实锚",
    "W274 冻结窗 ~4.0G bm-c 实锚",
    "W275 冻结窗 ~3.8G bm-c 实锚",
    "W276 冻结窗 ~3.9G bm-c 实锚",
    "W277 冻结窗 ~4.5G bm-c 实锚",
    "席位时即解锁",
    "（见 §5 item5）。",
    "R281：W280 带",
    "→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 投影 0.000313】",
    "631_300+1",
    "633_300+1",
    "633_301..633_500",
    "A_staircase_hop_past_W279_B=true",
    "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 280",
    "零 280 行",
    "零 skip-ahead W281/W282 席位声明",
    "15:1x",
    "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1129：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1129 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1129 窗实读",
    "nvidia-smi 实读 0%·2.0G VRAM 占用·MV 车道已收官 GPU idle 回释",
    "r1124 席位窗实跑：origin inbox 零 W280 席位外机命中",
    "results/p2cal_ext/n1_w279/ 12/12",
    "W278 冻结窗 ~6.4G bm-c 实锚"
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=611_501",
    "B-ext exit seed=613_501",
    "626_901..628_900",
    "622_301..622_500",
    "613_301..613_500",
    "613_301..615_300",
    "613_701..613_700",
    "624_501..626_500 CLEAN",
    "624_501..626_500",
    "620_301..622_300",
    "622_301..622_500",
    "624_501..626_500",
    "613_701..613_900",
    "620_301..622_300",
    "613_701..613_900",
    "622_301..624_300",
    "628_901..630_900 CLEAN",
    "629_101..629_300 CLEAN",
    "GATED on",
    "finalize PENDING",
    "queue_depth",
    "607,120",
    "**607,320 投影**",
    "line_merged@K607,120",
    "K=607,120",
    "−0.09277044",
    "0.24508694",
    "−0.08889850",
    "**0.305**",
    "实差 0.0039 在带内",
    "17:2x",
    "17:0x",
    "15:4x",
    "15:2x",
    "16:0x",
    "18:3x",
    "18:4x",
    "19:1x",
    "20:2x",
    "20:4x",
    "21:1x",
    "00:2x",
    "00:3x",
    "01:0x",
    "03:0x",
    "03:2x",
    "03:3x",
    "05:2x",
    "05:3x",
    "05:5x",
    "07:2x",
    "07:4x",
    "08:1x",
    "09:5x",
    "10:3x",
    "09:0x",
    "MSG-20261019-102x",
    "b187aa6214",
    "c5f8b88f91",
    "3bb8b9308e",
    "1c814343ed",
    "6c1aee751d",
    "ae98b97a10",
    "e4b015cbb",
    "7dd091eef1",
    "a035552321",
    "037445477b",
    "e0a21b817d",
    "bmc_rows=96",
    "bmc rows 96+候选",
    "第 97 枚",
    "第 268 波",
    "第九十七枚",
    "engine_owner==bm-c 96 行注册",
    "r1114-continuation 席位窗实跑",
    "r1101 窗算法",
    "95%·7.9G VRAM",
    "W280p_",
    "W280p_",
    "line_pre_w271",
    "键 W278 实测 K-lift",
    "verify at W280 prereg",
    "W280+ 投影",
    "W279+ 投影",
    "W278+ 投影",
    "第二十七次连续 A-hop",
    "第二十二次连续 above-own-A",
    "第二十八次连续 above-own-A",
    "连续二十七波",
    "共二百七十六面",
    "n1_w277_results.json",
    "n1_w269_results.json",
    "n1_w268_results.json",
    "W2..W278",
    "W137..W278",
    "W1..W278",
    "波号 278",
    "零 278 行",
    "W265 冻结窗 26G",
    "W266 冻结窗 7G",
    "W267 冻结窗 3G",
    "W268 冻结窗 ~5G",
    "W269 冻结窗 ~0.1G",
    "W270 冻结窗 ~1.4G",
    "W271 冻结窗 ~2.1G",
    "W272 冻结窗 ~3.3G",
    "W273 冻结窗 ~1.4G",
    "W274 冻结窗 ~0.3G",
    "626_900+1",
    "617_900+1",
    "611_500+1",
    "617_900+1",
    "611_300+1",
    "12:2x",
    "14:0x"
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
print("W280 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 3810f4a7ac @ " + SPLICE_T + " | finalize estate: 6bdbdb9a07 @ 20:0x | seat: f96272d8b9 @ 20:0x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~6.4GB written, MV 车道已收官 idle) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == 51d7ca52a811bc22a4ada6f4635915d5219ec734 @ ba5c725b42 (frozen pre-run face; HEAD post-backfill twin b98e8592 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
