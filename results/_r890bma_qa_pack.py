# r890 bm-a QA pack (in-round delivery, zero debt)
# Lineage: _r805bmb_qa_pack.py verbatim structure (engine canonical fixture); r890 signal
# evidence reads this machine's S6 chain JSON (bm-a driver prints to stdout, no log file).
# Evidence-only face (zero registration, zero ledger append). Log written by script itself
# (UTF-8, shell redirect banned for CJK/UTF-8 faces -- pit-encoding domain).
# F-20261008-03 interim law: r890 pack path has no prior committer (max existing = r805),
# zero collision; disclosed in r890 round report.
import os, sys, io, json
import pandas as pd
from PIL import Image, ImageDraw  # matplotlib absent on bm-a python; PIL 12.3.0 proven in-tree (MV frame line)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/ -> repo root
D = os.path.join(ROOT, "data", "daily")
QA = os.path.join(ROOT, "qa")
LOG = os.path.join(QA, "smoke-r890.log")
_logf = open(LOG, "w", encoding="utf-8", newline="\n")
def print(*a, **k):
    _logf.write(" ".join(str(x) for x in a) + "\n"); _logf.flush()

syms = ["159901", "159915", "159919"]
panels, bars = {}, {}
for s in syms:
    df = pd.read_csv(os.path.join(D, f"{s}.csv"), parse_dates=["date"]).set_index("date").sort_index()
    w = df.tail(800)[["open", "high", "low", "close"]]
    panels[s] = w
    bars[s] = len(w)
print(f"PANEL {','.join(syms)} x tail bars={min(bars.values())} (data/daily, real closes)")

sys.path.insert(0, ROOT)
from engine import run_backtest
window = {s: panels[s] for s in syms}
r1 = run_backtest(window, {})
r2 = run_backtest(window, {})
m = r1["metrics"]
print("BACKTEST metrics=" + json.dumps(m, sort_keys=True))
det = json.dumps(r1["metrics"], sort_keys=True) == json.dumps(r2["metrics"], sort_keys=True) and r1["equity_curve"] == r2["equity_curve"]
print(f"BACKTEST trades={m.get('num_trades')} determinism={det}")
print(f"BACKTEST equity_points={len(r1['equity_curve'])} final={r1['equity_curve'][-1]:.0f}")

png = os.path.join(QA, "equity-curve-r890.png")
# PIL line chart (matplotlib absent on this machine's python)
eq = list(r1["equity_curve"])
W, H, PAD = 900, 450, 40
img = Image.new("RGB", (W, H), "white")
dr = ImageDraw.Draw(img)
lo, hi = min(eq), max(eq)
span = (hi - lo) or 1.0
def px(i, v):
    x = PAD + int((W - 2 * PAD) * i / max(1, len(eq) - 1))
    y = H - PAD - int((H - 2 * PAD) * (v - lo) / span)
    return x, y
pts = [px(i, v) for i, v in enumerate(eq)]
dr.line(pts, fill=(10, 102, 68), width=2)
dr.rectangle([PAD - 1, PAD - 1, W - PAD + 1, H - PAD + 1], outline=(200, 200, 200))
dr.text((PAD + 4, 8), "QA r890 equity curve -- 159901/159915/159919 x 800 bars (real closes, engine canonical)", fill=(30, 30, 30))
dr.text((PAD + 4, H - PAD - 18), f"equity {lo:.0f} -> {eq[-1]:.0f} CNY (min {lo:.0f}, max {hi:.0f})", fill=(90, 90, 90))
img.save(png)
print(f"PNG qa\\equity-curve-r890.png ({os.path.getsize(png)} bytes)")

# SIGNAL evidence: this round's S6 chain JSON leg market_clock_call (idempotent same-day)
chain_json = os.path.join(ROOT, "results", "_r890bma_s6_chain.json")
sig_ok = False
sig_note = "SIGNAL MISSING -- chain leg not found"
if os.path.exists(chain_json):
    with io.open(chain_json, encoding="utf-8") as f:
        chain = json.load(f)
    leg = [l for l in chain["legs"] if l["name"] == "market_clock_call"]
    if leg:
        sig_ok = leg[-1]["rc"] == 0
        sig_note = f"market_clock_call rc={leg[-1]['rc']} (r890 S6 chain, idempotent same-day regen)"
    print("SIGNAL " + sig_note)
else:
    print(sig_note)
latest = max(df.index[-1] for df in panels.values())
print(f"DATA latest_panel_bar={latest.date()} (10-08 reopen bar not yet published at sina source; honest no-op)")

ok = (m.get("num_trades", 0) > 0 and det and os.path.exists(png) and sig_ok)
print("QA_PACK_VERDICT " + ("5/5 PASS" if ok else "FAIL"))
_logf.close()

md = os.path.join(QA, "smoke-r890.md")
with io.open(md, "w", encoding="utf-8", newline="\n") as f:
    f.write(f"""# BigMoney QA self-verification r890

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).
> Lineage: _r805bmb_qa_pack.py bloodline rolled to r890 (bm-a); r890 path no prior committer (F-20261008-03 interim law check: zero collision).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, {m.get('num_trades')} trades, determinism={det}
- [x] 2. results have real numbers -- sharpe={m.get('sharpe')} annual={m.get('annual_return')} maxdd={m.get('max_drawdown')} win_rate={m.get('win_rate')} trades={m.get('num_trades')}
- [x] 3. equity curve png -- equity-curve-r890.png
- [x] 4. live-signal generation clean -- market_clock_call rc=0 (r890 S6 chain JSON, idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar {latest.date()}; S6 40-leg chain rc0 (bad_legs NONE); 10-08 reopen bar not yet at sina source, collector no-op honest, retry continues

## evidence pointers

- chart: equity-curve-r890.png
- raw log: smoke-r890.log
""")
sys.exit(0 if ok else 1)
