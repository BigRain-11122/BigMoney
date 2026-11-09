"""r1490: the 'reinstated bar whose inputs later CHANGED' path, exercised on the REAL ledger.

r1489 taught the sheet to re-derive a withdrawn bar that came back. Its REWRITTEN_FROM_PANEL
branch -- the one that actually moves a published number -- had only ever run on a fixture,
so the question "does the disclosure survive when the inputs move" had no answer built from
this book's own history.

This face answers it without inventing a number. It copies the real
results/etf_book_order/ledger.jsonl, picks the second-to-last bar, recovers the book return
that bar's own row implies (rp = (ret + k_cost - (1-k)*rf) / k), and then moves that ONE
input by --shift (a restated close: the panel reprints the bar 0.5% higher, the default).
Nothing else is fabricated: the ledger nav/ret, k and rf are the real printed values.

Two runs, in this order:
  * CONTROL  -- same panel. Must print RECOMPUTED_IDENTICAL with nav_delta 0.0, or this face
                refuses to draw any conclusion (an identity that does not hold means the
                reconstruction is wrong, not the book).
  * SHADOW   -- the moved input. The row is rewritten from the panel, nav_published keeps the
                number that was actually published, the single later row is rescaled, and the
                chain is re-checked with the rounding-aware gate.

Output: results/etf_book_order/restatement_shadow.json (mode SHADOW_ON_REAL_PRODUCTS).
Writes nothing to the real ledger -- the copy lives in a temp dir.

  python scripts/etf_book_restatement_shadow.py run [--shift=0.005]
"""

import json
import os
import shutil
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etf_book_order as BO  # noqa: E402

REAL = os.path.join("results", "etf_book_order", "ledger.jsonl")
OUT = os.path.join("results", "etf_book_order", "restatement_shadow.json")


def _rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def run(shift=0.005):
    rows = _rows(REAL)
    if len(rows) < 3:
        print("ledger too short to shadow (%d rows)" % len(rows))
        return 2
    cut = rows[-2]
    nxt = rows[-1]
    k = float(cut["k"])
    rf = float(cut["rf"])
    cost = float(cut.get("k_cost") or 0.0)
    rp_implied = (float(cut["ret"]) + cost - (1.0 - k) * rf) / k

    def fixture():
        d = tempfile.mkdtemp()
        shutil.copy(REAL, os.path.join(d, "ledger.jsonl"))
        with open(os.path.join(d, "withdrawals.json"), "w", encoding="utf-8") as f:
            json.dump([{"withdrawn": [{"date": cut["date"], "nav": cut["nav"],
                                       "ret": cut["ret"], "k": k}],
                        "reason": "panel ended",
                        "panel_last": rows[-3]["date"],
                        "state_rewound_to": rows[-3]["date"],
                        "at": "%sT23:54:02" % cut["date"]}], f)
        idx = pd.DatetimeIndex([cut["date"], nxt["date"]])
        return d, idx

    d0, idx0 = fixture()
    ctrl = BO.reinstatement_check(
        pd.Series([rp_implied, 0.0], index=idx0),
        pd.Series([rf, float(nxt["rf"])], index=idx0),
        pd.Series([k, float(nxt["k"])], index=idx0), out_dir=d0, now="control")
    c_rec = (ctrl or {}).get("records", [{}])[0]
    if c_rec.get("status") != "RECOMPUTED_IDENTICAL" or (c_rec.get("nav_delta") or 0.0) != 0.0:
        print("REFUSED: the reconstructed panel does not reproduce the published row "
              "(status=%s nav_delta=%s) -- no conclusion can be drawn from the shadow"
              % (c_rec.get("status"), c_rec.get("nav_delta")))
        return 3

    d1, idx1 = fixture()
    sh = BO.reinstatement_check(
        pd.Series([rp_implied + float(shift), 0.0], index=idx1),
        pd.Series([rf, float(nxt["rf"])], index=idx1),
        pd.Series([k, float(nxt["k"])], index=idx1), out_dir=d1, now="shadow")
    rec = sh["records"][0]
    after = _rows(os.path.join(d1, "ledger.jsonl"))
    row_on_disk = [r for r in after if r["date"] == cut["date"]][0]
    downstream = [r for r in after if r["date"] == nxt["date"]][0]
    hist = BO.reinstated_history(os.path.join(d1, "ledger.jsonl"))

    payload = {
        "at": pd.Timestamp.now().floor("s").isoformat(),
        "mode": "SHADOW_ON_REAL_PRODUCTS",
        "note": ("real ledger rows from %s; the book return that the bar's own row implies, "
                 "moved by %+.4f for that one bar (a restated close). Every nav/ret/k/rf "
                 "below is the ledger's own printed value. The real ledger is untouched."
                 % (REAL, shift)),
        "real_ledger": {"path": REAL, "rows": len(rows), "shadowed_bar": cut["date"],
                        "next_bar": nxt["date"]},
        "control_same_panel": {"status": c_rec.get("status"),
                               "nav_delta": c_rec.get("nav_delta"),
                               "rewritten": (ctrl or {}).get("rewritten")},
        "changed_panel": {
            "status": rec.get("status"), "bar": rec.get("date"),
            "nav_published": rec.get("nav_published"),
            "nav_settled": rec.get("recomputed_nav"),
            "ret_published": rec.get("ret_published"),
            "ret_settled": rec.get("recomputed_ret"),
            "nav_delta": rec.get("nav_delta"), "restated_at": rec.get("restated_at"),
            "nav_factor": rec.get("nav_factor"),
            "later_rows_rescaled": rec.get("later_rows_rescaled"),
            "chain_intact": rec.get("chain_intact"),
            "chain_breaks": rec.get("chain_breaks")},
        "row_on_disk": {kk: row_on_disk.get(kk) for kk in
                        ("date", "nav", "ret", "nav_published", "ret_published",
                         "restated_at", "nav_factor_applied", "later_rows_rescaled")},
        "downstream_row": {"date": downstream["date"], "nav_published": nxt["nav"],
                           "nav_after": downstream["nav"],
                           "ret_unchanged": downstream["ret"] == nxt["ret"]},
        "ledger_history_face": {"bars": hist["bars"], "chain_broken": hist["chain_broken"],
                                "published_nav": (hist["records"][0]["nav_published"]
                                                  if hist["records"] else None),
                                "settled_nav": (hist["records"][0]["nav"]
                                                if hist["records"] else None)},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("shadow on real products: bar %s published nav=%s ret=%s -> settled nav=%.8f "
          "ret=%+.8f | factor %.12f | later rows rescaled=%d | chain_intact=%s"
          % (cut["date"], rec.get("nav_published"), rec.get("ret_published"),
             rec["recomputed_nav"], rec["recomputed_ret"], rec.get("nav_factor") or 1.0,
             rec.get("later_rows_rescaled") or 0, rec.get("chain_intact")))
    print("downstream %s: nav %s -> %s (ret unchanged=%s)"
          % (nxt["date"], nxt["nav"], downstream["nav"], payload["downstream_row"]["ret_unchanged"]))
    print("wrote", OUT)
    return 0


def main():
    if "--selftest" in sys.argv:
        print("selftest: this face runs the real ledger; --selftest is a no-op stub "
              "(the identity gate is the control run: it refuses to conclude without it)")
        return 0
    shift = 0.005
    for a in sys.argv:
        if a.startswith("--shift="):
            shift = float(a.split("=", 1)[1])
    return run(shift)


if __name__ == "__main__":
    sys.exit(main())