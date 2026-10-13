# -*- coding: utf-8 -*-
# W235 prereg derive PREP r977: facts machine-freeze (r975 precedent verbatim范式).
# Sources (zero transcription): _r976bmc_w234_fivekey_receipt.json (W234 finalize
# five-key product), n1_w234_results.json (K cross-check), _w235bmc_20261013_probe
# _receipt.json (seat ADMIT), committed W234 prereg blob 252d5cc95 (base_blob +
# win/RAM faces). Hygiene scans W235-variant per _w234bmc_hygiene_r976.py.
import glob, hashlib, json, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def gshow(rev, path):
    b = subprocess.run([GIT, "-C", REPO, "show", f"{rev}:{path}"], capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b

# ---- 1) W234 finalize numbers (five-key receipt = machine product) ----
fk = json.load(open(REPO + r"\results\_r976bmc_w234_fivekey_receipt.json", encoding="utf-8"))
led = fk["ledger"]
assert led["prev"] == 936389 and led["batch"] == 2200
assert led["prev"] + led["batch"] == led["total"] == 938589, "ledger identity"
merged_mu = fk["merged_mu"]; merged_sigma = fk["merged_sigma"]
w_only_mu = fk["w_only_mu"]
sl = fk["skill_line"]; semu = fk["se_mu"]
K = 510520 + 2200  # W234 facts merged_n_values + batch
assert "k512720" in str(semu) or semu["se_mu_at_k512720"] is not None, "K face drift"
assert abs(sl["merged"] - sl["pre"] - sl["delta"]) < 1e-9, "skill line identity"
# cross-check vs n1_w234_results.json (science_gates.ledger + null_pool_cumulative.merged)
res = json.load(open(REPO + r"\results\perpetual_faces\n1_w234_results.json", encoding="utf-8"))
res_led = res["science_gates"]["ledger"]
assert res_led["total"] == 938589 and res_led["prev_total"] == 936389 and res_led["batch_trials"] == 2200
merged_face = res["null_pool_cumulative"]["merged"]
assert merged_face["n_values"] == K == 512720, f"merged K face {merged_face['n_values']} != 512720"
assert abs(merged_face["mu"] - merged_mu) < 1e-12 and abs(merged_face["sigma"] - merged_sigma) < 1e-12
assert abs(res["null_pool_cumulative"]["w234_only"]["mu"] - w_only_mu) < 1e-12
print("ledger identity EXACT: 936,389+2,200=938,589; K=", K)

def f8(x):
    return ("−" if x < 0 else "") + ("%.8f" % abs(x)).rstrip("0").rstrip(".")
def f4(x):
    return ("−" if x < 0 else "") + ("%.4f" % abs(x)).rstrip("0").rstrip(".")

w234 = {
    "ledger_total": led["total"],
    "ledger_prev_total": led["prev"],
    "batch_trials": led["batch"],
    "merged_n_values": K,
    "merged_mu_8f": f8(merged_mu),
    "merged_sigma_8f": ("%.8f" % merged_sigma).rstrip("0"),
    "w234_only_mu_8f": f8(w_only_mu),
    "w234_only_vs_merged_absdiff_4f": f4(abs(w_only_mu - merged_mu)),
    "A_p95_4f": ("%.4f" % fk["A_p95"]).rstrip("0"),
    "kl_line_delta": "%+.4f" % sl["delta"],
    "kl_n_eff_held_equal": sl["n_eff"],
    "kl_line_pre_w234_4f": "%.4f" % sl["pre"],
    "kl_line_merged_4f": "%.4f" % sl["merged"],
    "se_mu": semu["se_mu_at_k512720"],
}
print("w234 faces:", json.dumps(w234, ensure_ascii=False))

# ---- 2) W235 seat probe receipt (bands + leg0 + leg4) ----
pr = json.load(open(REPO + r"\results\_w235bmc_20261013_probe_receipt.json", encoding="utf-8"))
assert pr["verdict"] == "ADMIT"
l0, l1, l4 = pr["legs"]["leg0"], pr["legs"]["leg1"], pr["legs"]["leg4"]
assert l1["A"] == [531804, 533803] and l1["hops_A"] == 1
assert l1["B"] == [533804, 534003] and l1["hops_B"] == 1
w235_bands = {
    "A": "531804_533803", "B": "533804_534003",
    "leg1_A": l1["A"], "leg1_B": l1["B"],
    "leg1_hops_A": l1["hops_A"], "leg1_hops_B": l1["hops_B"],
    "leg1_ARITH_A": l1["ARITH_A"], "leg1_ARITH_B": l1["ARITH_B"],
    "leg1_B_naive_first_clean": l1["B_naive_first_clean"],
    "leg4_W236p_A": l4["W235p_A"], "leg4_W236p_B": l4["W235p_B"],
    "leg0_rows": l0["rows"], "leg0_owner_rows": l0["owner_rows"],
    "leg0_bmc_rows": l0["bmc_rows"], "leg0_bmc_ordinal": l0["bmc_ordinal"],
    "leg0_ordinal": l0["ordinal"], "leg0_note_64th_owned": True,
}

# ---- 3) base blob: committed W234 prereg (freeze-time face) ----
rev = "252d5cc95"
path = "research/PERPETUAL_N1_W234_PREREG.md"
b = gshow(rev, path)
m = re.search(r"freeze 窗·(2026-10-1[23] \d+:\d+)x·", b.decode("utf-8"))
assert m, "W234 win label face not found"
win_label = m.group(1) + "x·"
mr = re.search(r"本窗 free RAM ~(\d+\.\d)GB", b.decode("utf-8"))
assert mr, "W234 RAM face not found"
ram_face = "~" + mr.group(1)
sha16 = hashlib.sha256(b).hexdigest()[:16]
assert sha16 == "4c28f0c92e6c9a10", f"sha16 drift {sha16} (r976 commit claim 4c28f0c92e6c9a10)"
print(f"base_blob: rev={rev} bytes={len(b)} sha16={sha16} win={win_label!r} ram={ram_face!r}")

# ---- 4) hygiene scans (W235 variant, r976 hygiene clone) ----
mentions, foreign = 0, 0
for d in ("fleet/inbox", "fleet/inbox/processed"):
    for f in glob.glob(REPO.replace("\\", "/") + "/" + d + "/*.md"):
        txt = open(f, encoding="utf-8", errors="replace").read()
        if "W235" in txt:
            mentions += 1
            if re.search(r"bm-a|bm-b", txt) and "bm-c" not in txt:
                foreign += 1
pf = gshow("origin/main", "scripts/perpetual_faces.py").decode("utf-8", "replace")
pf_235_rows = len(re.findall(r"^\s*\[?235[,\]]", pf, re.M))
pf_n1_235 = len(re.findall(r"PERPETUAL-N1-W235", pf))
pfn1 = open(REPO + r"\scripts\perpetual_faces_n1.py", encoding="utf-8").read()
pfn1_235 = len(re.findall(r"PERPETUAL-N1-W235", pfn1))
ls = subprocess.run([GIT, "-C", REPO, "ls-tree", "--name-only", "origin/main", "research/"],
                    capture_output=True).stdout.decode("utf-8", "replace")
prereg_on_origin = 1 if "PERPETUAL_N1_W235_PREREG.md" in ls else 0
hygiene = {"window": "r977", "ts": "2026-10-13 22:3x",
           "inbox_processed_W235_mentions": mentions,
           "inbox_processed_W235_foreign_mentions": foreign,
           "perpetual_faces_W235_rows": pf_235_rows,
           "perpetual_faces_n1_W235_wave_configs": pfn1_235 + pf_n1_235,
           "prereg_W235_on_origin": prereg_on_origin}
assert foreign == 0, "FOREIGN W235 seat hit -- do not proceed"
assert pf_235_rows == 0 and (pfn1_235 + pf_n1_235) == 0, "registry not vacant"
assert prereg_on_origin == 0, "prereg already on origin"
print("HYGIENE GREEN:", json.dumps(hygiene, ensure_ascii=False))

# ---- 5) write facts ----
facts = {
    "w234": w234,
    "w235_bands": w235_bands,
    "w234_freeze_receipt": {"bmc_own_ordinal": l0["bmc_ordinal"] - 1, "commit_hint": None},
    "base_blob": {"rev": rev, "path": path, "bytes": len(b), "sha16": sha16},
    "w234_ram_face": ram_face,
    "w234_win_label": win_label,
    "w234_freeze_round": "976",
    "hygiene": hygiene,
    "chain_leg_w234": {"splice_commit": "de342250c", "splice_round": "r976-continuation",
                       "absorb_round": "r976", "k": K, "ledger": led["total"],
                       "results_file": "n1_w234_results.json", "finalize_window": "21:5x"},
    "seat_publish": {"msg": "MSG-20261013-2149-bmc", "origin": "e830a2632", "window": "r976"},
}
open(REPO + r"\results\_w235bmc_facts.json", "w", encoding="utf-8").write(
    json.dumps(facts, ensure_ascii=False, indent=1))
print("FACTS FROZEN: results/_w235bmc_facts.json")
