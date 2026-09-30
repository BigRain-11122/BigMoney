# r491 bm-a: PROSPECT anchor refreeze, same-cutoff (RW-1 aftermath, D-20260930-05
# umbrella, r472 registered-member precedent).
# Root cause: RW-1 (r472) moved exits from same-close fill to T+1-open fill
# UNCONDITIONALLY (audit P0-1 look-ahead fix). The 6 registered members were
# refrozen same-window; the 22 PROSPECT members were only "pinned legacy
# caliber" in r475 -- pinning cannot reproduce pre-RW-1 evidence because the
# exit-timing change is not param-gated. First new-bar window after the flip
# (09-30 bar, 20:42) surfaced 22/22 anchor drift. Fix per r472 precedent:
# recompute every PROSPECT member at its FROZEN evidence_cutoff with the
# CURRENT engine + the member's declared caliber pins, overwrite the
# recorded evidence faces, disclose old->new in the diff table.
# Untouched: g1_pass, paper face, params, status_history, everything else.
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'scripts')
import p3_portfolio as p3
lp = __import__('live.paper', fromlist=['x'])

DIFF_PATH = "results/RW1_PROSPECT_REFREEZE_2026-09-30.md"
STATUS = ("repro-PASS refrozen 2026-09-30 r491 (RW-1 exit-T+1-open, "
          "D-20260930-05 umbrella; diff results/RW1_PROSPECT_REFREEZE_2026-09-30.md)")

PROSPECT_LEVELS = ("PROSPECT",)
traders = []
for f in sorted(os.listdir("firm/traders")):
    if not f.endswith(".json") or f.startswith("_"):
        continue
    with open(os.path.join("firm/traders", f), encoding="utf-8") as fh:
        t = json.load(fh)
    if t.get("level") in PROSPECT_LEVELS:
        traders.append(t)
assert len(traders) == 22, f"expected 22 PROSPECT members, got {len(traders)}"
prices = lp.load_core()

rows, n_flipped_sign = [], 0
for t in traders:
    path = os.path.join("firm/traders", f"{t['id']}.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    old = {k: raw["prospect"][k] for k in (
        "recorded_full_sharpe", "recorded_oos_sharpe",
        "recorded_x2_full_sharpe", "recorded_n_trades",
        "recorded_oos_trades", "recorded_max_dd")}
    r1 = p3.member_run(raw, prices)
    r2 = p3.member_run(raw, prices, cost_mult=2.0)
    new = {
        "recorded_full_sharpe": round(float(r1["full"]["sharpe"]), 4),
        "recorded_oos_sharpe": round(float(r1["oos"]["sharpe"]), 4),
        "recorded_x2_full_sharpe": round(float(r2["full"]["sharpe"]), 4),
        "recorded_n_trades": int(r1["n_trades"]),
        "recorded_oos_trades": int(r1["oos_trades"]),
        "recorded_max_dd": round(float(r1["full"]["max_drawdown"]), 4),
    }
    # replay cutoff must equal the member's frozen evidence_cutoff
    assert r1["cutoff"] == raw["evidence_cutoff"], \
        f"{t['id']}: replay cutoff {r1['cutoff']} != frozen {raw['evidence_cutoff']}"
    raw["prospect"].update(new)
    raw["prospect"]["anchor_status"] = STATUS
    raw["backtest"]["full"] = {"sharpe": new["recorded_full_sharpe"],
                               "max_dd": new["recorded_max_dd"],
                               "trades": new["recorded_n_trades"]}
    raw["backtest"]["out_sample"] = {"sharpe": new["recorded_oos_sharpe"],
                                     "trades": new["recorded_oos_trades"]}
    raw["backtest"]["cost_x2"] = {"full_sharpe":
                                  new["recorded_x2_full_sharpe"]}
    with open(path, "w", encoding="utf-8") as fh:   # CRLF, no trailing NL (house format)
        json.dump(raw, fh, indent=2, ensure_ascii=False)
    sign_flip = (old["recorded_full_sharpe"] > 0
                 and new["recorded_full_sharpe"] <= 0)
    n_flipped_sign += int(sign_flip)
    rows.append({"id": t["id"], "g1_pass": raw["prospect"].get("g1_pass"),
                 "cutoff": r1["cutoff"], "old": old, "new": new,
                 "full_sharpe_sign_flip": sign_flip})

# --- diff table (audit face, r472 RW1_MEMBER_DIFF precedent) ---
def fmt(v):
    return f"{v:+.4f}" if isinstance(v, float) else str(v)

lines = [
    "# RW-1 PROSPECT Anchor Refreeze 2026-09-30 (r491 bm-a)",
    "",
    "Context: r472 RW-1 exit look-ahead fix (audit P0-1, D-20260930-05 umbrella)",
    "made exits decided at close T fill at T+1 open UNCONDITIONALLY. The 6",
    "registered live members were refrozen same-cutoff in r472; the 22 PROSPECT",
    "members kept pre-RW-1 recorded evidence and r475's caliber pinning cannot",
    "reproduce it (exit timing is not param-gated). First new-bar window after",
    "the flip (09-30 bar landed 20:42) surfaced 22/22 anchor drift",
    "(t24_prospect_paper rc=2, member files untouched by contract).",
    "",
    "Action: recompute every PROSPECT member at its FROZEN evidence_cutoff with",
    "the current engine and the member's declared caliber pins; overwrite the",
    "recorded evidence faces only (prospect.recorded_* + backtest mirror +",
    "anchor_status provenance). g1_pass, paper tracking history, params,",
    "status_history untouched. Old values preserved below for audit.",
    "",
    "| member | g1_pass | full_sharpe old->new | oos_sharpe old->new | x2 old->new | trades old->new | oos_trades old->new | max_dd old->new |",
    "|---|---|---|---|---|---|---|---|",
]
for r in rows:
    o, n = r["old"], r["new"]
    lines.append(
        f"| {r['id']} | {r['g1_pass']} "
        f"| {fmt(o['recorded_full_sharpe'])} -> {fmt(n['recorded_full_sharpe'])}{' *SIGN*' if r['full_sharpe_sign_flip'] else ''} "
        f"| {fmt(o['recorded_oos_sharpe'])} -> {fmt(n['recorded_oos_sharpe'])} "
        f"| {fmt(o['recorded_x2_full_sharpe'])} -> {fmt(n['recorded_x2_full_sharpe'])} "
        f"| {o['recorded_n_trades']} -> {n['recorded_n_trades']} "
        f"| {o['recorded_oos_trades']} -> {n['recorded_oos_trades']} "
        f"| {fmt(o['recorded_max_dd'])} -> {fmt(n['recorded_max_dd'])} |")
lines += [
    "",
    f"Sign flips (full_sharpe positive->non-positive): {n_flipped_sign}/22.",
    "Science-owner note: g1 re-evaluation under refrozen evidence (and any",
    "PROSPECT-pool demotion) is a science-face decision, NOT taken here;",
    "promotion path continues to apply frozen criteria (paper months + G2 +",
    "T-22 beat-rate) to forward tracking only.",
    "",
]
with open(DIFF_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

summary = {"round": "r491 bm-a PROSPECT refreeze",
           "n_members": len(rows), "n_sign_flip": n_flipped_sign,
           "diff_table": DIFF_PATH, "cutoffs": sorted({r["cutoff"] for r in rows})}
with open("results/_r491bma_prospect_refreeze.json", "w", encoding="utf-8") as f:
    json.dump(summary | {"rows": rows}, f, ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False))
