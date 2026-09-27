# -*- coding: utf-8 -*-
# r310 bm-b ticket surgery: (1) T-89 claim-collision resolution per fleet/README sec.4
# commit-time order (bm-b c422fa6b 07:55:54 < bm-a 54ae013c 08:01:09 -> later bm-a yields;
# slice-2 delivery credited zero-rework); (2) T-90 same-round claim-and-start per
# O-20260924-1730 immediate-law (start deliverable = four-arm prereg this round).
import json, datetime, sys

def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def dump(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")

ts = now_iso()
print("surgery ts:", ts)

# ---- T-89: bm-b owns per sec.4; keep bm-a slice-2 progress verbatim (credited) ----
p89 = "fleet/tasks/T-2026-09-26-89-P1.json"
t89 = load(p89)
assert t89["id"] == "T-2026-09-26-89", t89["id"]
assert "bm-a" in t89.get("claimed_by", ""), "expected bm-a collision state on disk, got: %r" % t89.get("claimed_by")
keep_bma = t89.get("progress_r303_bma")  # historical credit, preserved verbatim
t89["status"] = "claimed"
t89["claimed_by"] = ("bm-b (OS iteration loop, round 309 claim commit c422fa6b @ 2026-09-27 07:55:54 +0800; "
    "R310 collision resolution per fleet/README sec.4 commit-time order: bm-a later claim (54ae013c @ 08:01:09) yields; "
    "bm-a slice-2 MARKET_STAGE_TABLE.md v1.0 delivery credited zero-rework; "
    "slice-1 prereg frozen by bm-b e33984e4 = research/PROS_REGIME_SEGMENTS_P1.md)")
t89["claimed_at"] = "2026-09-27T07:55:54+08:00"
t89["collision_r310"] = ("same-window dual claim (both rounds pulled pre-push trees): bm-b r309 c422fa6b 07:55:54 "
    "vs bm-a r303 54ae013c 08:01:09; sec.4 later-arriver-yields -> bm-a yields; slices complementary zero-dup: "
    "bm-b slice-1 prereg (frozen) + bm-a slice-2 standing table (delivered); "
    "anti-dup guard: slice-1 prereg ALREADY FROZEN -- bm-a do not re-draft, do not work this ticket")
t89["progress_r310_bmb"] = ("r310 surgery commit: bm-b owns; slice-1b exact continuation = scripts/prospect_regime_segments.py "
    "(t22 import-face reuse, level=PROSPECT injection, hermetic selftest incl. r297 B7b contract leg) -> "
    "runnable_pool entry ~63.5k cells -> autofill per S3; slice-3 attack-corps supply memo after slice-1b")
if keep_bma:
    t89["progress_r303_bma"] = keep_bma
dump(p89, t89)
print("T-89 resolved: claimed_by=bm-b, bm-a progress preserved:", bool(keep_bma))

# ---- T-90: open -> claimed by bm-b, same-round start per immediate-law ----
p90 = "fleet/tasks/T-2026-09-27-90-P1.json"
t90 = load(p90)
assert t90["id"] == "T-2026-09-27-90", t90["id"]
assert t90.get("status") == "open", "expected T-90 open, got: %r" % t90.get("status")
t90["status"] = "claimed"
t90["claimed_by"] = ("bm-b (OS iteration loop, round 310 same-round claim-and-start per O-20260924-1730 immediate-law; "
    "start deliverable = four-arm chain E2E prereg draft+freeze this round; runner -> runnable_pool next per R99; "
    "zero new strategy search inside ticket)")
t90["claimed_at"] = ts
t90["progress_r310_bmb"] = ("r310 claim + start: prereg research/DECISION_CHAIN_E2E_P1.md draft+freeze "
    "(four arms A full-chain regime-routed replay / B CE-01 no-switch / C passive EW / D six-member EW; "
    "T-22 harness lineage; frozen judgments: beat rates, worst-start dd, switch friction ledger, "
    "per-regime segments, half-ladder A/B face, broken-ring localization) -- this round commit")
dump(p90, t90)
print("T-90 claimed by bm-b at", ts)

# self-verify: reload + key asserts
for p, owner_check in ((p89, "bm-b"), (p90, "bm-b")):
    d = load(p)
    assert owner_check in d["claimed_by"], d["claimed_by"]
    assert d["status"] == "claimed", d["status"]
print("SURGERY OK: T-89 bm-b-owned (bm-a yields, slice-2 credited), T-90 claimed bm-b same-round start")
