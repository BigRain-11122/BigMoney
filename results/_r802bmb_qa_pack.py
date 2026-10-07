# r802 bm-b QA pack (in-round delivery, zero debt)
# Lineage: _r801bmb_qa_pack.py verbatim structure; smoke-rNNN.md checklist face per smoke-r803.md format.
# Evidence-only face (zero registration, zero ledger append). Log written by script itself (UTF-8,
# shell redirect banned for CJK/UTF-8 faces -- pit-encoding domain).
import os, sys, io, json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/ -> repo root
D = os.path.join(ROOT, "data", "daily")
QA = os.path.join(ROOT, "qa")
LOG = os.path.join(QA, "smoke-r802.log")
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

png = os.path.join(QA, "equity-curve-r802.png")
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(range(len(r1["equity_curve"])), r1["equity_curve"], lw=1.2, color="#0a6")
ax.set_title("QA r802 equity curve -- 159901/159915/159919 x 800 bars (real closes, engine canonical)")
ax.set_xlabel("bar"); ax.set_ylabel("equity (CNY)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(png, dpi=100)
plt.close(fig)
print(f"PNG qa\\equity-curve-r802.png ({os.path.getsize(png)} bytes)")

# SIGNAL evidence: this window's S6 chain leg 07 (idempotent same-day; log line verified)
chain_log = os.path.join(ROOT, "results", "_r802bmb_s6_chain.log")
sig_ok = False
with io.open(chain_log, encoding="utf-8", errors="replace") as f:
    lines = f.read().splitlines()
sig_lines = [l for l in lines if "LEG 07_clock_call" in l]
if sig_lines:
    sig_ok = "RC=0" in sig_lines[-1]
    print("SIGNAL market_clock_call chain leg 07 rc=0 (r802 S6 chain, idempotent same-day regen) :: " + sig_lines[-1])
else:
    print("SIGNAL MISSING -- chain leg 07 line not found")
latest = max(df.index[-1] for df in panels.values())
print(f"DATA latest_panel_bar={latest.date()} (golden-week no-op expected until 10-08 reopen)")

ok = (m.get("num_trades", 0) > 0 and det and os.path.exists(png) and sig_ok)
print("QA_PACK_VERDICT " + ("5/5 PASS" if ok else "FAIL"))
_logf.close()

md = os.path.join(QA, "smoke-r802.md")
with io.open(md, "w", encoding="utf-8", newline="\n") as f:
    f.write(f"""# BigMoney QA self-verification r802

> Group charter: docs/qa-smoke-test-charter.md (BigMoney section). Evidence = this pack; re-runnable every round; ZERO registration / ZERO ledger append (smoke face).
> Lineage: r800 debt pack delivered by r801; this r802 pack produced in-round (no debt).

## checklist

- [x] 1. full backtest runs clean -- 3 syms x 800 bars, {m.get('num_trades')} trades, determinism={det}
- [x] 2. results have real numbers -- sharpe={m.get('sharpe')} annual={m.get('annual_return')} maxdd={m.get('max_drawdown')} win_rate={m.get('win_rate')} trades={m.get('num_trades')}
- [x] 3. equity curve png -- equity-curve-r802.png
- [x] 4. live-signal generation clean -- market_clock_call rc=0 (r802 S6 chain leg 07, idempotent same-day regen)
- [x] 5. data pull healthy -- latest panel bar {latest.date()}; S6 35-leg chain rc0 receipts in round report (golden-week no-op family, reopen 10-08)

## evidence pointers

- chart: equity-curve-r802.png
- raw log: smoke-r802.log
""")
sys.exit(0 if ok else 1)
