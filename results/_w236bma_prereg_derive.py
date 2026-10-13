# -*- coding: utf-8 -*-
# W236 per-wave prereg derivation -- bm-a own-seat freeze window r972 (upstream
# W1..W235 ALL LANDED at this window: W235 full cycle = prereg derive 89bd6962c
# (r968 takeover) + five-face splice ff438aeaf (r969) + engine self-burn 12/12
# 03:45-03:56 + PRE-FINALIZE six-gate tenth consecutive + finalize one-pass
# r970 ccf10ee3d + five-key ALL PASS + sec78 backfill; zero in-flight upstream
# seats, clean chain-order window, twenty-fifth consecutive fully-clean freeze
# window). Method: machine transform of the freeze-time W235 prereg blob
# (git show 89bd6962c:research/PERPETUAL_N1_W235_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later in
# ccf10ee3d) with the ordered replacement table emitted by
# results/_w236bma_subgen.py into results/_w236bma_sub_block.py
# (find sides machine-generated from the committed _w235bma_sub_block.py
# W235 new-sides, m33 materialization, zero transcription; repl sides are
# the authored R36 own-seat faces, machine-asserted here against live JSON).
# OWN-SEAT: bm-a r971 published seat MSG-20261014-0446-bma-w236-seat @ origin
# 5c25db795 with probe _w236bma_20261014 ADMIT receipt; bands UNCHANGED
# (R250 no re-pick): A 534_004..536_003 / B 536_004..536_203 per receipt
# verbatim. CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10
# ~23:1x + O-20261013-22:1x CPU standing-open + O-20260911-0012 sec.ii
# queue-deepen seat-chain mandate.
import ast, datetime, hashlib, json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def blob(rev, path):
    b = subprocess.run([GIT, "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b.decode("utf-8")

# ---------- machine facts (never hand-copied) ----------
FACTS = json.load(open(REPO + r"\results\_w236bma_facts.json", encoding="utf-8"))
rec = json.load(open(REPO + r"\results\_w236bma_20261014_probe_receipt.json", encoding="utf-8"))

# ---------- gate0.5: W235 row registered + finalize file in place ----------
pf_now = blob("origin/main", "scripts/perpetual_faces.py")
assert re.search(r"W235[^\n]*531_?804", pf_now) or "W235" in pf_now, "gate0.5: W235 row missing in law file"
w235 = json.load(open(REPO + r"\results\perpetual_faces\n1_w235_results.json", encoding="utf-8"))
print("gate0.5 OK: W235 row in law file + n1_w235_results.json in place")

# ---------- live hygiene (own-seat vacancy 4-checks, re-run live) ----------
# (1) origin law file has NO W236 row yet
assert not re.search(r"W236[^\n]*534_?004", pf_now), "hygiene: W236 already registered in law file"
# (2) origin n1 runner has no W236 WAVE_CONFIGS
pfn1 = blob("origin/main", "scripts/perpetual_faces_n1.py")
assert "PERPETUAL-N1-W236" not in pfn1, "hygiene: W236 WAVE_CONFIGS already in runner"
# (3) origin has no W236 prereg
_chk = subprocess.run([GIT, "-C", REPO,
                       "cat-file", "-e", "origin/main:research/PERPETUAL_N1_W236_PREREG.md"],
                      capture_output=True)
assert _chk.returncode != 0, "hygiene: W236 prereg already on origin"
# (4) no foreign W236 seat anywhere in inbox/processed (own seat MSG-20261014-0446 ok)
_ip = subprocess.run([GIT, "-C", REPO,
                      "ls-tree", "--name-only", "-r", "origin/main", "fleet/inbox/", "fleet/inbox/processed/"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
foreign = [l for l in _ip.splitlines() if "W236" in l and "0446" not in l]
assert not foreign, f"hygiene: foreign W236 seat files {foreign}"
# seat publish verified on origin (r565 seat-first law)
assert "MSG-20261014-0446-bma-w236-seat.md" in _ip, "seat publish MSG not on origin inbox"
print("live hygiene OK: origin vacancy 4-checks + seat publish on origin")

# ---------- base blob (freeze-time W235 face, pre-backfill) ----------
bb = FACTS["base_blob"]
assert bb["rev"] == "89bd6962c" and bb["bytes"] == 26354 and bb["sha16"] == "91d568af162efbc1"
t = blob(bb["rev"], bb["path"])
_tb = t.encode("utf-8")
assert len(_tb) == bb["bytes"], f"base blob bytes {len(_tb)} != {bb['bytes']}"
assert hashlib.sha256(_tb).hexdigest()[:16] == bb["sha16"], "base blob sha16 drift"
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"
print("base blob OK:", bb["rev"], bb["bytes"], "bytes sha16", bb["sha16"])

# ---------- probe receipt machine anchors ----------
leg0, leg1, leg4 = rec["legs"]["leg0"], rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg0["rows"] == 233 and leg0["tail"] == "W235-registered"
assert leg0["owner_rows"] == 225 and leg0["bmc_rows"] == 64 and leg0["bma_rows"] == 120
assert leg0["ordinal"] == 226 and leg0["bma_ordinal"] == 121
assert leg1["A"] == [534004, 536003] and leg1["B"] == [536004, 536203]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [533804, 535803] and leg1["ARITH_B"] == [534004, 534203]
assert leg1["B_naive_first_clean"] == [534004, 534203]
assert leg4["W237p_A"] == "536004..538003" and leg4["W237p_B"] == "536204..536403"
assert leg4["W237p_B_lands_inside_W237p_A"] is True
assert rec["bands"]["A"] == [534004, 536003] and rec["bands"]["B"] == [536004, 536203]
for line in rec["legs"]["leg2"]["seed_admit_gate"]:
    assert "verdict=FREE" in line, f"seed gate not FREE: {line}"
print("probe receipt anchors OK: bands/hops/legs/seed gates all machine-verified")

# ---------- live W235 finalize JSON guards (facts mirror re-verified) ----------
led = w235["science_gates"]["ledger"]
assert led["total"] == 940789 and led["prev_total"] == 938589 and led["batch_trials"] == 2200
merged = w235["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 514920
w235only = w235["null_pool_cumulative"]["w235_only"]
A_p95 = w235["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w235["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 938589
assert kl["line_pre_w235"] == 1.1926 and kl["line_merged_514920"] == 1.1926
se_mu = w235["null_pool_cumulative"]["se_mu_at_k514920"]
assert se_mu == 0.000342

def fmt8(x):
    return ("\u2212" if x < 0 else "") + f"{abs(x):.8f}"
w235f = FACTS["w235"]
assert fmt8(merged["mu"]) == w235f["merged_mu_8f"] == "\u22120.09279197", fmt8(merged["mu"])
assert fmt8(w235only["mu"]) == w235f["w235_only_mu_8f"] == "\u22120.09609841", fmt8(w235only["mu"])
assert f"{merged['sigma']:.8f}" == w235f["merged_sigma_8f"] == "0.24509683"
assert f"{abs(w235only['mu'] - merged['mu']):.4f}" == "0.0033"
assert f"{A_p95:.4f}" == "0.3058"
assert f"{kl['line_delta_k_lift']:+.4f}" == "+0.0000"
assert FACTS["w235"]["se_mu"] == se_mu
# bands mirror
bw = FACTS["w236_bands"]
assert bw["A"] == "534004_536003" and bw["B"] == "536004_536203"
assert bw["leg1_A"] == leg1["A"] and bw["leg1_B"] == leg1["B"]
assert bw["leg0_rows"] == 233 and bw["leg0_owner_rows"] == 225
print("live JSON guards OK: W235 finalize keys re-verified against facts mirror")

# ---------- own-seat premise verification (zero takeover) ----------
_seat = subprocess.run([GIT, "-C", REPO,
                        "show", "5c25db795:fleet/inbox/MSG-20261014-0446-bma-w236-seat.md"],
                       capture_output=True)
assert _seat.returncode == 0 and _seat.stdout.startswith(b"# W236 seat published"), \
    "own-seat premise broken: seat MSG not on origin at declared commit 5c25db795"
print("own-seat premise OK: MSG-20261014-0446-bma-w236-seat on origin 5c25db795 (own seat, zero takeover)")

# ---------- live RAM read (honesty for the RAM note) ----------
import psutil
_avail_gb = psutil.virtual_memory().available / 1e9
assert 0.03 <= _avail_gb <= 94.0, f"unexpected RAM face: {_avail_gb}"
RAM_GB = f"~{_avail_gb:.1f}"
print(f"live free RAM: {_avail_gb:.2f} GB -> note '{RAM_GB}GB'")

# ---------- engine live status (honesty for the block-1 carried face) ----------
_st = subprocess.run([sys.executable, "scripts/saturation_engine.py", "status"],
                     cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert _st.returncode == 0, f"engine status FAIL: {(_st.stdout or '')[-300:]}"
_so = _st.stdout or ""
assert '"active_burns": []' in _so, "engine active_burns not empty at derive time"
assert '"queue_depth": 0' in _so, "engine queue_depth not zero at derive time"
assert '"last_verdict": "idle"' in _so, "engine not idle at derive time"
print("engine live status: active_burns=[] queue_depth=0 idle verified")

# ---------- freeze-window label (live honesty) ----------
_now = datetime.datetime.now()
assert (_now.year, _now.month, _now.day) == (2026, 10, 14), f"unexpected clock: {_now}"
WIN_LABEL = f"2026-10-14 {_now.hour}:{_now.minute // 10}x·"
print(f"freeze-window label: r972 own-seat freeze {WIN_LABEL}")

# ---------- SUB extraction (literal from subgen output, BinOp vars live) ----------
def resolve_node(node, vars):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [resolve_node(x, vars) for x in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(resolve_node(x, vars) for x in node.elts)
    if isinstance(node, ast.Dict):
        return {resolve_node(k, vars): resolve_node(v, vars) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return resolve_node(node.left, vars) + resolve_node(node.right, vars)
    if isinstance(node, ast.Name) and node.id in vars:
        return node.id and vars[node.id]
    raise AssertionError(f"unresolvable AST node: {ast.dump(node)[:100]}")

def extract_lit(path, varname, expect, vars=None):
    vars = vars or {}
    src = open(path, encoding="utf-8").read()
    val = None
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == varname:
            try:
                cand = resolve_node(node.value, vars)
            except Exception:
                cand = None
            if cand:
                val = cand
                break
    assert val and len(val) == expect, f"{varname} extract failed: {len(val) if val else 0}"
    return val

SUB = extract_lit(r"results\_w236bma_sub_block.py", "SUB", 46,
                  vars={"WIN_LABEL_235": FACTS["w235_win_label"],
                        "WIN_LABEL": WIN_LABEL,
                        "RAM_FACE_235": FACTS["w235_ram_face"],
                        "RAM_GB": RAM_GB})
print(f"SUB extracted: 46 groups | special (0,3) repl head: {SUB[0][3][1][:42]!r}")

# ---------- preflight + apply (r787: every find count==1, then replace) ----------
_n_pairs = 0
for i in range(46):
    for find, repl in SUB[i]:
        c = t.count(find)
        assert c == 1, f"pair[{i}][k] count {c} != 1 for: {find[:70]}..."
        t = t.replace(find, repl, 1)
        _n_pairs += 1
print(f"preflight+apply OK: 46/46 groups, {_n_pairs} pairs all count==1")

# ---------- generic wave-token aging shifts (W235 derive tail, verbatim law) ----------
t = t.replace("n1_w235_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W235", "PERPETUAL-N1-W236")
t = t.replace("PERPETUAL_N1_W235", "PERPETUAL_N1_W236")
t = t.replace("n1_w235", "n1_w236")
t = t.replace("_w235bma", "_w236bma")
t = t.replace("W235", "@U_W@")
t = t.replace("W234", "W235")
t = t.replace("n1_w234", "n1_w235")
t = t.replace("PERPETUAL_N1_W234", "PERPETUAL_N1_W235")
t = t.replace("_w234bmc", "_w235bma")
t = t.replace("@u_w@", "w235")
t = t.replace("@U_W@", "W235")
# heritage tokens materialized at derive end (R36 header law):
# @L34@ -> 234 (one-wave-older refs immune to aging shift)
# @T34@ -> 35 (_w235bma template face)
t = t.replace("@L34@", "234")
t = t.replace("@T34@", "35")
for _tok in ("@L34@", "@T34@", "@L33@", "@T33@", "@u_w@", "@U_W@"):
    assert t.count(_tok) == 0, f"unmaterialized token survives: {_tok}"
print("aging shifts OK: tokens materialized, zero placeholders survive")

# ---------- STALE (W235-face self tokens that must be gone) ----------
STALE = [
    "PERPETUAL-N1-W235 预注册", "泵第 233 枚", "NINETY-FIFTH", "第九十五例",
    "第 120 枚 EXACT", "第一百二十枚自有波", "bma rows 119",
    "r967 takeover freeze 窗·2026-10-14 3:1x", "第 225 波", "engine_owner==bm-a 119 行",
    "净账本锚头 **938,589**", "=**514,920 投影**", "K=512,720 合并池",
    "n1_w235/ 分片计数增长", 'batch_name="PERPETUAL-N1-W235"',
    "line_merged@K512,720", "实差 0.0019 在带内", "parity 93 行",
    "共二百三十二面", "机证 232 行", "全二百三十二行",
    "pre-W235 宇宙",
    "W236 freezer 承接面",
    "（531_803+1）", "（533_803+1）", "波号 235=", "A base=531804", "B base=533804",
    "\u2212" + "0.09277778", "\u2212" + "0.09468659", "0.24508604", "0.3097",
    "n_eff_held_equal 936,389",
    "W235 B 带 533_804..534_003 注册后将拒 naive W236 A 窗",
    "verify at W236 prereg",
    "净账本锚头 938,589",
    "K-lift **+0.0002**",
]
for s in STALE:
    c = t.count(s)
    if c:
        for m in re.finditer(re.escape(s), t):
            print(f"--- STALE[{s}] ctx ---")
            print(t[max(0, m.start()-140):m.end()+60].replace("\n", " | "))
    assert c == 0, f"STALE token survives x{c}: {s}"
print(f"STALE all-zero OK: {len(STALE)} checks")

# ---------- NEW (W236-face tokens that must be present) ----------
NEW = [
    "PERPETUAL-N1-W236 预注册 · N1 nulls-deepening 泵第 234 枚",
    "**A-ext seed=534_004..536_003**", "**B-ext exit seed=536_004..536_203**",
    "NINETY-SIXTH", "第九十六例", "第九十七例",
    "940,789", "514,920", "**517,120 投影**",
    "MSG-20261014-0446-bma-w236-seat", "5c25db795",
    "n1_w236_results.json", "n1_w235_results.json",
    "0.3058", "\u2212" + "0.09279197", "\u2212" + "0.09609841", "0.24509683",
    "n_eff_held_equal 938,589", "0.000342",
    "第 226 波", "第 121 枚 EXACT", "bma rows 120",
    "A base=534004 span=2000 checked=2000 verdict=FREE / B base=536004 span=200 checked=200 verdict=FREE",
    "全二百三十三行", "共二百三十三面", "机证 233 行",
    "bm-a 自有席自有波", "freeze 窗",
    "engine_owner==bm-a 120 行", "K-lift **+0.0000**",
    "实差 0.0033 在带内", "parity 94 行",
    "536_004..538_003", "536_204..536_403",
    "verify at W237 prereg", "W237 freezer 承接面强制注记",
    "n1_w236/shard-<k>-of-12.json", "PERPETUAL_N1_W236_PREREG.md",
]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A/B bands appear as the ADMIT face (>=4)
assert t.count("534_004..536_003") >= 4 and t.count("536_004..536_203") >= 4
# upstream W235 refusing band appears in A-face prose (>=2)
assert t.count("533_804..534_003") >= 2
# chain-history legs present exactly once each (pair-written verbatim)
assert t.count("+W234=bm-c r976 死窗 prereg derive（252d5cc95）") == 1
assert t.count("+W235=bm-a r968 takeover 窗 prereg derive（89bd6962c）") == 1
assert t.count("n1_w234_results.json·21:5x") == 1
assert t.count("n1_w235_results.json·04:3x") == 1
# estate parity listing carries the aged one-wave-older legs verbatim
assert t.count("W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235") == 1
assert t.count("W234 **0.000342**→W235 **0.000342**】") == 1
assert t.count("按 _w235bma_freeze_edits.py 模板派生") == 1
assert t.count("W@L34@") == 0 and t.count("@T34@") == 0
print(f"NEW all-present OK: {len(NEW)} checks + band/leg/parity sanity")

# ---------- write ----------
out = r"research\PERPETUAL_N1_W236_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W236 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W235(upper) refs (upstream, expected 40+):", t.count("W235"), "| W236 self:", t.count("W236"))
print("W234 heritage refs (chain legs + estate face):", t.count("W234"))
