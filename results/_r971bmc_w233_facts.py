# -*- coding: utf-8 -*-
# r971 W233 prereg FACTS FREEZE -- machine-extracted, zero transcription (r587/r787 laws).
# Emits results/_w233bmc_facts.json for the next-window R33 authoring + derive run.
import json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
G = r"C:\Program Files\Git\cmd\git.exe"

facts = {}

# ---- 1. W232 finalize results (upstream anchor) ----
w232 = json.load(open(REPO + r"\results\perpetual_faces\n1_w232_results.json", encoding="utf-8"))
led = w232["science_gates"]["ledger"]
merged = w232["null_pool_cumulative"]["merged"]
w232only = w232["null_pool_cumulative"]["w232_only"]
A_p95 = w232["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w232["skill_line_v2_k_lift"]
se_mu = w232["null_pool_cumulative"]["se_mu_at_k508320"]
facts["w232"] = {
    "ledger_total": led["total"], "ledger_prev_total": led["prev_total"], "batch_trials": led["batch_trials"],
    "merged_n_values": merged["n_values"], "merged_mu_8f": ("%.8f" % merged["mu"]).replace("-", "\u2212"),
    "merged_sigma_8f": "%.8f" % merged["sigma"],
    "w232_only_mu_8f": ("%.8f" % w232only["mu"]).replace("-", "\u2212"),
    "w232_only_vs_merged_absdiff_4f": "%.4f" % abs(w232only["mu"] - merged["mu"]),
    "A_p95_4f": "%.4f" % A_p95,
    "kl_line_delta": "%+.4f" % kl["line_delta_k_lift"],
    "kl_n_eff_held_equal": kl["n_eff_held_equal"],
    "kl_line_pre_w232_4f": "%.4f" % kl["line_pre_w232"],
    "kl_line_merged_4f": "%.4f" % kl["line_merged_508320"],
    "se_mu": se_mu,
}
# structural parity vs W231-window anchor pattern (state note): 934,189 / K 508,320
assert led["total"] == 934189 and led["prev_total"] == 931989 and led["batch_trials"] == 2200
assert merged["n_values"] == 508320
assert facts["w232"]["merged_mu_8f"].startswith("\u22120.09274") or facts["w232"]["merged_mu_8f"].startswith("\u22120.0927"), facts["w232"]["merged_mu_8f"]
assert "%.5f" % merged["sigma"] == "0.24508", merged["sigma"]
assert "%.4f" % A_p95 == "0.3063", A_p95
assert kl["line_delta_k_lift"] <= 0.0001 and kl["line_pre_w232"] is not None
assert se_mu == 0.000344, se_mu

# ---- 2. W233 seat probe receipt (bands authority) ----
rec = json.load(open(REPO + r"\results\_w233bmc_20261013_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "527404_529403", "B": "529404_529603"}
leg0, leg1, leg4 = rec["legs"]["leg0"], rec["legs"]["leg1"], rec["legs"]["leg4"]
facts["w233_bands"] = {
    "A": rec["bands"]["A"], "B": rec["bands"]["B"],
    "leg1_A": leg1["A"], "leg1_B": leg1["B"], "leg1_hops_A": leg1["hops_A"], "leg1_hops_B": leg1["hops_B"],
    "leg1_ARITH_A": leg1["ARITH_A"], "leg1_B_naive_first_clean": leg1["B_naive_first_clean"],
    "leg4_W234p_A": leg4["W233p_A"], "leg4_W234p_B": leg4["W233p_B"],
    "leg0_rows": leg0["rows"], "leg0_owner_rows": leg0["owner_rows"], "leg0_bmc_rows": leg0["bmc_rows"],
    "leg0_bmc_ordinal": leg0["bmc_ordinal"], "leg0_ordinal": leg0["ordinal"],
    "leg0_note_62nd_owned": "62nd owned" in leg0["bmc_ordinal_note"],
}

# ---- 3. W232 freeze receipt (ordinal prose anchor) ----
fr = json.load(open(REPO + r"\results\_w232bmc_freeze_receipt.json", encoding="utf-8"))
facts["w232_freeze_receipt"] = {"bmc_own_ordinal": fr["ordinal_faces"]["bmc_own_ordinal"],
                                 "commit_hint": fr.get("commit", fr.get("splice_commit", None))}
assert fr["ordinal_faces"]["bmc_own_ordinal"] == 62, fr["ordinal_faces"]

# ---- 4. freeze-time blob base: W232 prereg @ a3a7aa632 (pre-sec.7/8-backfill face) ----
b = subprocess.run([G, "-C", REPO, "show", "a3a7aa632:research/PERPETUAL_N1_W232_PREREG.md"], capture_output=True).stdout
assert b and b"## \xc2\xa77" in b and "占位".encode("utf-8") in b, "freeze-time W232 face verify failed"
facts["base_blob"] = {"rev": "a3a7aa632", "path": "research/PERPETUAL_N1_W232_PREREG.md",
                       "bytes": len(b), "sha16": __import__("hashlib").sha256(b).hexdigest()[:16]}
# RAM + win-label faces from the W232 freeze-time blob
txt = b.decode("utf-8")
m = re.search(r"本窗 free RAM ~(\d+\.\d)GB", txt); facts["w232_ram_face"] = "~" + m.group(1)
m = re.search(r"freeze 窗·(2026-10-1[23] \d+:\d+)x·", txt); facts["w232_win_label"] = m.group(1) + "x·"
m = re.search(r"循环班 r(\d+) freeze 窗", txt); facts["w232_freeze_round"] = m.group(1)

# ---- 5. origin hygiene probes (W233 prose claims, live-verified) ----
def origin_count(pattern, path_glob, exclude_substr=None):
    out = subprocess.run([G, "-C", REPO, "grep", "-c", "-E", pattern, "origin/main", "--", path_glob],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    total = 0
    for ln in (out.stdout or "").splitlines():
        if ":" in ln:
            fname = ln.split(":", 1)[1].rsplit(":", 1)[0]
            if exclude_substr and exclude_substr in fname:
                continue
            try: total += int(ln.rsplit(":", 1)[1])
            except ValueError: pass
    return total
facts["hygiene"] = {
    # prose claim = zero FOREIGN machine W233 seat hits; own -bmc seat/relay MSGs excluded
    "inbox_processed_W233_mentions": origin_count(r"W233", "fleet/inbox/"),
    "inbox_processed_W233_foreign_mentions": origin_count(r"W233", "fleet/inbox/", exclude_substr="-bmc"),
    "perpetual_faces_W233_rows": origin_count(r"WAVE_CONFIGS.*W233|W233.*WAVE_CONFIGS|PERPETUAL-N1-W233", "scripts/perpetual_faces_n1.py"),
    "prereg_W233_on_origin": origin_count(r"PERPETUAL_N1_W233_PREREG", "research/"),
}
assert facts["hygiene"]["inbox_processed_W233_foreign_mentions"] == 0, facts["hygiene"]
assert facts["hygiene"]["prereg_W233_on_origin"] == 0, facts["hygiene"]

# ---- 6. upstream chain leg append text (G3) facts ----
facts["chain_leg_w232"] = {"splice_commit": "e58dbcda3", "k": 508320, "ledger": 934189,
                            "results_file": "n1_w232_results.json", "finalize_window": "15:2x",
                            "derive_round": "r968"}

out = REPO + r"\results\_w233bmc_facts.json"
json.dump(facts, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("FACTS FROZEN OK:", out)
print(json.dumps({k: facts[k] for k in ("w232", "w233_bands", "w232_freeze_receipt", "base_blob", "w232_ram_face", "w232_win_label", "w232_freeze_round", "hygiene")}, ensure_ascii=False, indent=1))
