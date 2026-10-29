"""bm-b S6 chain runner (reusable).

Same shape and same reason as Tools/s6_chain_bmc.py: the per-round S6 chain used
to be an ad-hoc script rebuilt every window, which spent the round's wall time
on generation instead of measurement. This copy carries the legs bm-b actually
owns (R31 lane law: astock daily + ETF five-member panel are bm-b lanes) plus the
shared data/panel and guard legs, and leaves the bm-c-hosted ETF production-book
family to bm-c's own runner so the two machines do not refresh one book twice.

Usage: python Tools\\s6_chain_bmb.py <round_no>
Exit 0 always (legs are recorded; a non-zero leg is reported, not fatal) -- the
round report must surface any rc!=0 leg verbatim.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

LEGS = [
    ("dualrun", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    # E217: run before anything that reads "pool ready N" -- four cards sat open with
    # their declared deliverable already on disk, so the watermark counted work that
    # was finished. apply is evidence-gated (face written after the card entered) and
    # idempotent, so a clean pool costs one glob pass and writes nothing.
    ("pool_deliverable", ["python", os.path.join("Tools", "pool_deliverable_audit.py"),
                          "apply"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    # the official exchange calendar, so "no new bar" is not ambiguous
    ("cal_audit", ["python", "scripts/exchange_calendar_audit.py", "run"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("market_clock", ["python", "scripts/market_clock_call.py", "run"]),
    # bm-b lanes (R31): the A-share daily panel and the five-member ETF panel
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"]),
    # bm-b faces that read those panels
    ("regime_thermo", ["python", "scripts/regime_thermo_build.py"]),
    ("regime_gate_dualarm", ["python", "scripts/regime_gate_dualarm.py", "run"]),
    ("rev_osc_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("etf_book_forward", ["python", "scripts/etf_book_forward.py"]),
    # E214: the E60 off-book liquidity split carried across every era the panel
    # covers, so a two-era sign disagreement is not read as a flip on a sample of 2
    ("offbookera", ["python", "scripts/e39_panel_census.py", "offbookera"]),
    # E61: the mid-month calendar gap split into a timing part and a selection
    # part, with the month-end book's holdings as the per-session candidate pool
    ("sharedbook", ["python", "scripts/e39_panel_census.py", "sharedbook"]),
    # E218: E61's "selection" part also carried a width change (the shared arm
    # chose from <=10 names, both full arms from ~1,274), so the split is re-read
    # with both matched arms on one seeded draw of the same size -- and read as a
    # distribution, because a single ten-name draw is noisier than the gap
    ("sharedbookwidth", ["python", "scripts/e39_panel_census.py",
                         "sharedbookwidth"]),
    # E219: the same matched-width control on a width ladder. Idempotent on the
    # cutoff (a face for this cutoff is a no-op), so the chain does not re-pay four
    # burns per round for identical numbers.
    ("sharedbookwidthladder", ["python", "scripts/e39_panel_census.py",
                               "sharedbookwidthladder"]),
    # E220: the ladder's rungs disagree, so this reads them through the E61 identity
    # and names the part that carries the movement. Pure arithmetic over the face
    # above -- no burn -- so it re-derives every round instead of caching to a cutoff.
    ("sharedbookwidthsplit", ["python", "scripts/e39_panel_census.py",
                              "sharedbookwidthsplit"]),
    # E221: the same calendar question asked where the sample is wide enough to
    # matter -- the whole ETF universe instead of one ten-name book. Deterministic,
    # zero network, ~10s on the full panel, so it re-derives every round rather than
    # caching to a cutoff.
    ("dom_profile", ["python", "scripts/e221_dom_profile.py", "run"]),
    # E222: E221 left the turn-of-month shape as a post-hoc candidate; this leg asks
    # whether it survives as a tradable rule with costs, a frozen IS/OOS split and a
    # decision rule in code. Same panel, deterministic, ~2s, so it re-derives each round.
    ("tom_overlay", ["python", "scripts/e222_tom_overlay.py", "run"]),
    # E223: E222's power block said the calendar question needs ~110 years because the
    # rule is observed once a month. This leg runs the same accounting on a frequency
    # ladder (the monthly anchor against three weekly ones) and publishes the resolution
    # each reaches, so "observe more often" is measured rather than assumed.
    ("obs_rate_ladder", ["python", "scripts/e223_obs_rate_ladder.py", "run"]),
    # CEO-facing pages
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    # E210: the pages above are the ones the CEO opens, so the leg that asks whether
    # their numbers can be traced to a face cell has to run after them, not before.
    ("docquotes", ["python", "scripts/e97_routing.py", "docquotes", "--publish"]),
    # E211: the same sweep as a ratchet -- a page family that starts printing a number
    # no face produces turns this leg red instead of waiting for the next audit.
    ("pagegate", ["python", "scripts/e97_routing.py", "pagegate", "--publish"]),
    # fleet / bookkeeping guards
    ("machine_health", ["python", "Tools/machine_health_face.py", "check"]),
    ("gpu_face", ["python", "Tools/gpu_face.py", "audit"]),
    ("attrition_guard", ["python", "scripts/attrition_ledger_guard.py", "scan"]),
    ("pool_audit", ["python", os.path.join("scripts", "pool_audit.py")]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
]


def main(argv):
    if not argv:
        print("usage: s6_chain_bmb.py <round_no>")
        return 2
    rnd = str(argv[0])
    out = os.path.join("results", "_r%sbmb_s6_chain.json" % rnd)
    rows = []
    t0 = time.time()
    for leg, cmd in LEGS:
        s = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                               errors="replace", timeout=900)
            rc, tail = p.returncode, (p.stdout or "").strip().splitlines()[-1:] or [""]
        except Exception as exc:      # a leg that cannot even start is a leg, not a crash
            rc, tail = 99, [str(exc)[:200]]
        rows.append({"leg": leg, "rc": rc,
                     "elapsed_sec": round(time.time() - s, 2),
                     "tail": (tail[0][:300] if tail else "")})
        print("%-22s rc=%-3s %6.2fs  %s" % (leg, rc, time.time() - s,
                                            rows[-1]["tail"][:110]))
    bad = [r for r in rows if r["rc"] != 0]
    payload = {"round": rnd, "machine": "bm-b",
               "ts": datetime.now().isoformat(timespec="seconds"),
               "elapsed_sec": round(time.time() - t0, 2),
               "legs_total": len(rows), "legs_rc0": len(rows) - len(bad),
               "legs": rows}
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("\nS6 %d/%d rc=0  (%.1fs)  receipt=%s"
          % (payload["legs_rc0"], payload["legs_total"], payload["elapsed_sec"], out))
    for r in bad:
        print("NONZERO %s rc=%s %s" % (r["leg"], r["rc"], r["tail"][:200]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))