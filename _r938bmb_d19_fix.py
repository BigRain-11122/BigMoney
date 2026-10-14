# r938 fix: D-19 verdict correction -- raw-bytes hash EQUAL (PS-pipe c1a8c7fc = mojibake false positive)
import hashlib
import json
import subprocess

def group_sha(path, algo):
    blob = subprocess.check_output(["git", "-C", r"C:\Fluxgroup\FluxGroup", "show", "origin/main:" + path])
    return hashlib.sha256(blob).hexdigest() if algo == "sha256" else hashlib.sha1(blob).hexdigest()

DEC = group_sha("docs/decisions.md", "sha256")
ORD = group_sha("docs/orders.md", "sha1")
assert DEC == "d9d8aa72d4d346e809f81d0d6e0ab6343bff2ebb002b254852917ce0c34e02f4", DEC
assert ORD == "a7bb50eaf0abfeb6d219e4c7a7b8f644e58d030a", ORD
print("verified EQUAL: dec", DEC[:16], "ord", ORD[:12])

did_fix = (
    "r938 bm-b S0-estate-absorb round (watchdog-killed r937 rebase healed): "
    "(1) S0: found rebase-merge in progress 1/3 (pick 05f1a00e9 UU fleet/machine-health.json) -- "
    "union heal 13->9 rows dual-tail 14:36+15:11 verified (r996/r998 precedent, treasure_guard rc0 "
    "reproducible-artifact class, resolver _r938bmb_resolver.py committed as evidence); picks 2-3 conflicts "
    "= 5+3 bm-b own SatEngine/live daemon faces resolved live-wins (history 120-row window rotated-by-design, "
    "20 old rows out = daemon trim, not loss); rebase completed clean; owner-content audit PASS (state "
    "round 937 clock 15:33:23 verdict W20 = bm-b own, r936 law); r937 stranded estate DELIVERED "
    "(push 1a1161be3..1ae3f0f15: W20 census 0/45 + S6 37/37 + state r937); (2) S0.5 orders scan + S7 "
    "double-scan both NONE unacked; D-19 decisions/orders dual hash EQUAL zero-action (raw-bytes "
    "subprocess verify dec=d9d8aa72 ord=a7bb50ea vs r936-advanced watermark; D-20261014-02..07 rows "
    "already consumed by r936 14:56:29 advance=true; dispatch-board re-read confirmed all executors "
    "FluxVerse/HQ/group = zero rows involve this repo; CAUGHT PRE-COMMIT: earlier PS-pipe hash probe "
    "returned c1a8c7fc fake-CHANGED verdict = PowerShell pipe re-encoding mangles CJK bytes -- "
    "watermark probes must hash raw subprocess bytes, never PS-piped stdin); group fetch moved "
    "2fb6677..5df53b1..0cac24f = hardware/bili non-decisions commits; (3) S1 smoke 49/49 PASS; "
    "SatEngine alive; watermark red=false; idle verdict None (no GREEN-IDLE); (4) S6 full chain rc0: "
    "dualrun streak 23 ZERO-DRIFT, compute_audit FLAG pool_starvation+supply_floor (verdict stands: "
    "tick-stock-panel route closed, refill = P1 stock-universe ticket or sec.5 sources), "
    "py_watermark=py_low_board_clear (legal idle white-list), market_clock ORANGE_COOL, thermo rebuild, "
    "dualarm DUALARM-2026-09-30 honest asof, prospect 22/22 + promotion gate 0/22 eligible, "
    "daily_report REPORT-2026-10-14 + LIVE-2026-10-14 (state=ORANGE cap 50%) written; TODAY=trading "
    "day confirmed (marks 19 rows to 15:05 settle + minute feed 15:00 bars) but sina DAILY bar not yet "
    "published -> panel cutoff stays 10-13, live.paper/t35/t24 gated legs honest skip, self-heal next "
    "rounds; (5) S7: attrition CLEAN (1 healed shrink note), loop pin=2 no-op next 16:02, watchdog "
    "alive 15:59, both claws OK; observation: strategy_scorecard+daily_scorecard ran full derive on "
    "bm-b (no r378 host-guard found in code face; deterministic-idempotent zero-drift; flag for "
    "guard-face governance audit); inbox 1 unread = MSG-2026-10-14-1547-bmc addressed to bm-a (not "
    "this machine, not ALL) -> zero action, left in place"
)

verdict_fix = (
    "GREEN: r938 S0 estate absorb landed whole-package (interrupted r937 rebase healed via union "
    "dual-tail + live-wins chain, stranded W20 census estate delivered to origin); S6 full chain rc0; "
    "smoke 49/49; attrition CLEAN; orders 0 unacked; D-19 dual hash EQUAL zero-action (PS-pipe fake-hash "
    "false positive caught pre-commit); flags = supply_floor/pool_starvation standing WITH VERDICT "
    "(route closed; refill = P1 stock-universe ticket or sec.5 sources) + GPU PSU-deferred standing "
    "(MODE=pause) + sina 10-14 daily-bar catch pending (self-heal) + scorecard guard-face observation "
    "(governance audit pointer)"
)

s = json.load(open("state.json", encoding="utf-8"))
s["did"] = did_fix
s["verdict"] = verdict_fix
s["last_decisions_sha_method"] = (
    "r938: fresh git -C C:/Fluxgroup/FluxGroup fetch (2fb6677..5df53b1..0cac24f hardware/bili non-decisions "
    "commits) + raw-bytes subprocess show hash EQUAL vs r936-advanced watermark -> zero-action; "
    "PS-pipe probe c1a8c7fc = mojibake false positive (caught pre-commit)"
)
s["last_orders_sha_note"] = (
    "r938: orders.md sha1 EQUAL vs stored (raw-bytes verify; tail re-read = bm-a/bm-c video/bili rows "
    "only, zero BigMoney rows); zero scan delta"
)
s["note"] = (
    "r938: S0 fork round; rebase heal chain per r996/r998 precedents; ONE new pit face learned: "
    "PS-piped hash probes corrupt CJK blobs (fake CHANGED verdicts) -- watermark probes must hash "
    "raw subprocess bytes (memory append queued per four-gate)"
)
json.dump(s, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# fix round report last line (raw bytes, no pipes)
p = r"logs\iteration-loop\round_reports.md"
raw = open(p, "rb").read().decode("utf-8")
lines = raw.rstrip("\n").split("\n")
assert "r938 bm-b" in lines[-1], lines[-1][:80]
lines[-1] = lines[-1].replace(
    "D-19 decisions hash changed -> dispatch board + 6 new D-rows consumed, ALL "
    "executor=FluxVerse/HQ/group zero rows involve this repo (watermark updated)",
    "D-19 decisions/orders dual hash EQUAL zero-action (raw-bytes subprocess verify d9d8aa72/a7bb50ea vs "
    "r936 watermark; D-20261014-02..07 already consumed by r936; CAUGHT PRE-COMMIT: PS-pipe hash probe "
    "c1a8c7fc = mojibake fake-CHANGED -- watermark probes must hash raw subprocess bytes, PS pipe "
    "re-encodes CJK)",
)
with open(p, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("state + report line fixed")
