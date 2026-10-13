# -*- coding: utf-8 -*-
# W235 per-wave prereg derivation -- bm-a takeover freeze, same-label
# continuation of the r967 takeover freeze-prep (R35 authored r967, subgen
# emitted the SUB block r967 window; derive applies now in the r968
# continuation window per the W234 r976-continuation same-label precedent).
# Method: machine transform of the freeze-time W234 prereg blob
# (git show 252d5cc95:research/PERPETUAL_N1_W234_PREREG.md -- the exact
# pre-backfill commit face; the sec.7/8 machine-read backfill landed later
# in e830a2632) with the ordered replacement table emitted by
# results/_w235bma_subgen.py into results/_w235bma_sub_block.py
# (find sides machine-generated from the committed _w234bmc_prereg_derive.py
# SUB34 new-sides, m32 materialization, zero transcription; repl sides are
# the authored R35 takeover faces, machine-asserted here against live JSON).
# Takeover evidence: bm-c seat-published W235 (MSG-20261013-2149-bmc @ origin
# e830a2632, r976 absorb window) then hb-stalled (last seen 2026-10-13 23:59,
# >158min stalled at takeover decision, re-verified >180min at derive time)
# with r977/r978 crash-loop dead windows (facts landed 23:33, prereg derive
# died twice, no prereg file); bm-a per CEO fill-order standing takes over
# the freeze (r885/r898 precedent, mirror case). Bands UNCHANGED
# (R250 no re-pick): seat ADMIT receipt
# results/_w235bmc_20261013_probe_receipt.json verbatim.
import ast, datetime, hashlib, json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def blob(rev, path):
    b = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b.decode("utf-8")

# ---------- machine facts (never hand-copied) ----------
FACTS = json.load(open(REPO + r"\results\_w235bmc_facts.json", encoding="utf-8"))
rec = json.load(open(REPO + r"\results\_w235bmc_20261013_probe_receipt.json", encoding="utf-8"))

# ---------- gate0.5: W234 row registered + finalize file in place ----------
pf_now = blob("origin/main", "scripts/perpetual_faces.py")
assert re.search(r"W234[^\n]*529_?604", pf_now) or "W234" in pf_now, "gate0.5: W234 row missing in law file"
w234 = json.load(open(REPO + r"\results\perpetual_faces\n1_w234_results.json", encoding="utf-8"))
print("gate0.5 OK: W234 row in law file + n1_w234_results.json in place")

# ---------- live hygiene (R35[2] prose assertions, re-run live) ----------
# (1) origin law file has NO W235 row yet
assert not re.search(r"W235[^\n]*531_?804", pf_now), "hygiene: W235 already registered in law file"
# (2) origin n1 runner has no W235 WAVE_CONFIGS
pfn1 = blob("origin/main", "scripts/perpetual_faces_n1.py")
assert "PERPETUAL-N1-W235" not in pfn1, "hygiene: W235 WAVE_CONFIGS already in runner"
# (3) origin has no W235 prereg
_chk = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", REPO,
                       "cat-file", "-e", "origin/main:research/PERPETUAL_N1_W235_PREREG.md"],
                      capture_output=True)
assert _chk.returncode != 0, "hygiene: W235 prereg already on origin"
# (4) no foreign W235 seat in inbox/processed (own seat MSG-20261013-2149-bmc ok)
_ip = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", REPO,
                     "ls-tree", "--name-only", "origin/main", "fleet/inbox/processed/"],
                    capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
foreign = [l for l in _ip.splitlines() if "W235" in l and "2149" not in l]
assert not foreign, f"hygiene: foreign W235 seat files {foreign}"
# seat publish verified on origin (r565 seat-first law)
assert "MSG-20261013-2149-bmc" in _ip, "seat publish MSG-20261013-2149-bmc not on origin processed/"
print("live hygiene OK: origin vacancy 4-checks + seat publish on origin")

# ---------- base blob (freeze-time W234 face, pre-backfill) ----------
bb = FACTS["base_blob"]
assert bb["rev"] == "252d5cc95" and bb["bytes"] == 25813 and bb["sha16"] == "4c28f0c92e6c9a10"
t = blob(bb["rev"], bb["path"])
_tb = t.encode("utf-8")
assert len(_tb) == bb["bytes"], f"base blob bytes {len(_tb)} != {bb['bytes']}"
assert hashlib.sha256(_tb).hexdigest()[:16] == bb["sha16"], "base blob sha16 drift"
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"
print("base blob OK:", bb["rev"], bb["bytes"], "bytes sha16", bb["sha16"])

# ---------- probe receipt machine anchors ----------
leg0, leg1, leg4 = rec["legs"]["leg0"], rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg0["rows"] == 232 and leg0["tail"] == "W234-registered"
assert leg0["owner_rows"] == 224 and leg0["bmc_rows"] == 64 and leg0["bma_rows"] == 119
assert leg0["ordinal"] == 225
assert leg1["A"] == [531804, 533803] and leg1["B"] == [533804, 534003]
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
assert leg1["ARITH_A"] == [531604, 533603] and leg1["ARITH_B"] == [531804, 532003]
assert leg1["B_naive_first_clean"] == [531804, 532003]
assert leg4["W235p_A"] == "533804..535803" and leg4["W235p_B"] == "534004..534203"
assert leg4["W235p_B_lands_inside_W235p_A"] is True
assert rec["bands"] == {"A": "531804_533803", "B": "533804_534003"}
for line in rec["legs"]["leg2"]["seed_admit_gate"]:
    assert "verdict=FREE" in line, f"seed gate not FREE: {line}"
print("probe receipt anchors OK: bands/hops/legs/seed gates all machine-verified")

# ---------- live W234 finalize JSON guards (facts mirror re-verified) ----------
led = w234["science_gates"]["ledger"]
assert led["total"] == 938589 and led["prev_total"] == 936389 and led["batch_trials"] == 2200
merged = w234["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 512720
w234only = w234["null_pool_cumulative"]["w234_only"]
A_p95 = w234["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w234["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0002 and kl["n_eff_held_equal"] == 936389
assert kl["line_pre_w234"] == 1.1923 and kl["line_merged_512720"] == 1.1925
se_mu = w234["null_pool_cumulative"]["se_mu_at_k512720"]
assert se_mu == 0.000342

def fmt8(x):
    return ("\u2212" if x < 0 else "") + f"{abs(x):.8f}"
w234f = FACTS["w234"]
assert fmt8(merged["mu"]) == w234f["merged_mu_8f"] == "\u22120.09277778", fmt8(merged["mu"])
assert fmt8(w234only["mu"]) == w234f["w234_only_mu_8f"] == "\u22120.09468659", fmt8(w234only["mu"])
assert f"{merged['sigma']:.8f}" == w234f["merged_sigma_8f"] == "0.24508604"
assert f"{abs(w234only['mu'] - merged['mu']):.4f}" == "0.0019"
assert f"{A_p95:.4f}" == "0.3097"
assert f"{kl['line_delta_k_lift']:+.4f}" == "+0.0002"
assert FACTS["w234"]["se_mu"] == se_mu
# bands mirror
bw = FACTS["w235_bands"]
assert bw["A"] == "531804_533803" and bw["B"] == "533804_534003"
assert bw["leg1_A"] == leg1["A"] and bw["leg1_B"] == leg1["B"]
assert bw["leg0_rows"] == 232 and bw["leg0_owner_rows"] == 224
print("live JSON guards OK: W234 finalize keys re-verified against facts mirror")

# ---------- takeover premise re-verified (hb-stale, not recovered) ----------
_bmchb = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8-sig"))
_ep = _bmchb.get("heartbeat_epoch_utc")
assert isinstance(_ep, int), "bm-c heartbeat epoch not int"
_age_min = (datetime.datetime.now().timestamp() - _ep) / 60
assert _age_min > 158, f"takeover premise broken: bm-c hb only {_age_min:.0f}min old (revived?)"
print(f"takeover premise OK: bm-c hb-stall {_age_min:.0f}min (>158min bar)")

# ---------- live RAM read (honesty for the RAM note) ----------
import psutil
_avail_gb = psutil.virtual_memory().available / 1e9
assert 0.03 <= _avail_gb <= 60.0, f"unexpected RAM face: {_avail_gb}"
RAM_GB = f"~{_avail_gb:.1f}"
print(f"live free RAM: {_avail_gb:.2f} GB -> note '{RAM_GB}GB'")

# ---------- engine live status (honesty for the block-1 carried face) ----------
_st = subprocess.run([sys.executable, "scripts/saturation_engine.py", "status"],
                     cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert _st.returncode == 0, f"engine status FAIL: {(_st.stdout or '')[-300:]}"
_so = _st.stdout or ""
# bm-a runner schema: active_burns/queue_depth (bm-c Tools schema names differ)
assert '"active_burns": []' in _so, "engine active_burns not empty at derive time"
assert '"queue_depth": 0' in _so, "engine queue_depth not zero at derive time"
assert '"last_verdict": "idle"' in _so, "engine not idle at derive time"
print("engine live status: active_burns=[] queue_depth=0 idle verified")

# ---------- freeze-window label (live honesty; same-label r967 takeover) ----------
_now = datetime.datetime.now()
assert (_now.year, _now.month, _now.day) == (2026, 10, 14), f"unexpected clock: {_now}"
WIN_LABEL = f"2026-10-14 {_now.hour}:{_now.minute // 10}x·"
print(f"freeze-window label: r967 takeover same-label continuation {WIN_LABEL}")

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

SUB = extract_lit(r"results\_w235bma_sub_block.py", "SUB", 46,
                  vars={"WIN_LABEL_234": FACTS["w234_win_label"],
                        "WIN_LABEL": WIN_LABEL,
                        "RAM_FACE_234": FACTS["w234_ram_face"],
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

# ---------- generic wave-token aging shifts (W234 derive tail, verbatim law) ----------
t = t.replace("n1_w234_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W234", "PERPETUAL-N1-W235")
t = t.replace("PERPETUAL_N1_W234", "PERPETUAL_N1_W235")
t = t.replace("n1_w234", "n1_w235")
t = t.replace("_w234bmc", "_w235bmc")
t = t.replace("W234", "@U_W@")
t = t.replace("W233", "W234")
t = t.replace("n1_w233", "n1_w234")
t = t.replace("PERPETUAL_N1_W233", "PERPETUAL_N1_W234")
t = t.replace("_w233bmc", "_w234bmc")
t = t.replace("@u_w@", "w234")
t = t.replace("@U_W@", "W234")
# heritage tokens materialized at derive end (R35 header law):
# @L33@ -> 233 (one-wave-older refs immune to aging shift)
# @T33@ -> 34 (_w234bmc template face)
t = t.replace("@L33@", "233")
t = t.replace("@T33@", "34")
for _tok in ("@L33@", "@T33@", "@L32@", "@T32@", "@u_w@", "@U_W@"):
    assert t.count(_tok) == 0, f"unmaterialized token survives: {_tok}"
print("aging shifts OK: tokens materialized, zero placeholders survive")

# ---------- STALE (W234-face self tokens that must be gone) ----------
STALE = [
    "PERPETUAL-N1-W234 预注册", "泵第 232 枚", "NINETY-FOURTH", "第九十四例", "第六十四枚",
    "bmc_ordinal=64", "第 64 枚 EXACT", "prose 64th", "63rd owned 承袭",
    "r976 freeze 窗·2026-10-13 20:5x", "第 224 波", "engine_owner==bm-c 63 行",
    "净账本锚头 **936,389**", "=**512,720 投影**", "K=510,520 合并池",
    "n1_w234/ 分片计数增长", 'batch_name="PERPETUAL-N1-W234"',
    "line_merged@K510,520", "实差 0.0062 在带内", "parity 92 行",
    "共二百三十一面", "机证 231 行", "pre-W234 宇宙",
    "W235 freezer 承接面",  # consumed by pair 38
    "（529_603+1）", "波号 234=", "A base=529604", "B base=531604",
    "第 63 枚 EXACT", "63rd owned",
    "\u2212" + "0.09276956", "\u2212" + "0.09893318", "0.24506207", "0.3027",
    "n_eff_held_equal 934,189",
    "W234 B 带 531_604..531_803 注册后将拒 naive W235 A 窗",
    "verify at W235 prereg",  # consumed by pair 38 repl (verify at W236)
    "净账本锚头 936,389",
]
for s in STALE:
    c = t.count(s)
    if c:
        for m in re.finditer(re.escape(s), t):
            print(f"--- STALE[{s}] ctx ---")
            print(t[max(0, m.start()-140):m.end()+60].replace("\n", " | "))
    assert c == 0, f"STALE token survives x{c}: {s}"
print(f"STALE all-zero OK: {len(STALE)} checks")

# ---------- NEW (W235-face tokens that must be present) ----------
NEW = [
    "PERPETUAL-N1-W235 预注册 · N1 nulls-deepening 泵第 233 枚",
    "**A-ext seed=531_804..533_803**", "**B-ext exit seed=533_804..534_003**",
    "NINETY-FIFTH", "第九十五例", "第九十六例",
    "938,589", "512,720", "**514,920 投影**",
    "MSG-20261013-2149-bmc", "e830a2632",
    "n1_w235_results.json", "n1_w234_results.json",
    "0.3097", "\u2212" + "0.09277778", "\u2212" + "0.09468659", "0.24508604",
    "n_eff_held_equal 936,389", "0.000342",
    "第 225 波", "第 120 枚 EXACT", "bma rows 119",
    "A base=531804 span=2000 checked=2000 verdict=FREE / B base=533804 span=200 checked=200 verdict=FREE",
    "全二百三十二行", "共二百三十二面", "机证 232 行",
    "bm-a takeover", "takeover freeze 窗",
    "engine_owner==bm-a 119 行", "K-lift **+0.0002**",
    "实差 0.0019 在带内", "parity 93 行",
    "533_804..535_803", "534_004..534_203",
    "verify at W236 prereg", "W236 freezer 承接面强制注记",
    "n1_w235/shard-<k>-of-12.json", "PERPETUAL_N1_W235_PREREG.md",
]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A/B bands appear as the ADMIT face (>=4)
assert t.count("531_804..533_803") >= 4 and t.count("533_804..534_003") >= 4
# upstream W234 refusing band appears in A-face prose (>=2)
assert t.count("531_604..531_803") >= 2
# chain-history legs present exactly once each (pair-written verbatim)
assert t.count("+W233=bm-c r973 死窗五面冻结（0ca920362）") == 1
assert t.count("+W234=bm-c r976 死窗 prereg derive（252d5cc95）") == 1
assert t.count("n1_w233_results.json·19:5x") == 1
assert t.count("n1_w232_results.json·15:2x") == 1
# estate parity listing carries the aged one-wave-older legs verbatim
assert t.count("W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234") == 1
assert t.count("W233 **0.000343**\u2192W234 **0.000342**】") == 1 or t.count("W233 **0.000343**→W234 **0.000342**】") == 1
assert t.count("按 _w234bmc_freeze_edits.py 模板派生") == 1
assert t.count("W@L32@") == 0 and t.count("@T32@") == 0
print(f"NEW all-present OK: {len(NEW)} checks + band/leg/parity sanity")

# ---------- write ----------
out = r"research\PERPETUAL_N1_W235_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W235 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W234(upper) refs (upstream, expected 40+):", t.count("W234"), "| W235 self:", t.count("W235"))
print("W233 heritage refs (chain legs + estate face):", t.count("W233"))
