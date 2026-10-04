"""r671 T-166 closure evidence: read parquet faces, verify coverage/shape/TTM helper."""
import json, sys, io
import pandas as pd

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
D = REPO + r"\data\fund_statement_export"
w = io.open(r"C:\Users\sjs20\AppData\Local\Temp\r671_close.txt", "w", encoding="utf-8")

expect_periods = 86
summary = {}
for face in ("cashflow", "balance", "income"):
    df = pd.read_parquet(D + f"\\{face}_faces.parquet")
    periods = df["report_date"].nunique() if "report_date" in df.columns else df.iloc[:, 1].nunique()
    cols = list(df.columns)
    summary[face] = {"rows": len(df), "periods": int(periods), "cols": cols}
    w.write(f"{face}: rows={len(df)} periods={periods}\n  cols={cols}\n")
    # null share on key value col
    for c in cols:
        if c.lower() in ("value", "amount", "total"):
            nn = df[c].notna().mean()
            w.write(f"  {c} nonnull share: {nn:.4f}\n")

# TTM helper import check
sys.path.insert(0, REPO + r"\scripts")
import update_fund_statements as ufs
w.write(f"\nttm_from_cumulative present: {hasattr(ufs, 'ttm_from_cumulative')}\n")
w.write(f"norm_avail_date present: {hasattr(ufs, 'norm_avail_date')}\n")

ok = all(v["periods"] == expect_periods for v in summary.values()) and hasattr(ufs, "ttm_from_cumulative")
w.write(f"\nCLOSURE GATE: {'PASS' if ok else 'FAIL'} (all faces 86 periods + TTM helper importable)\n")
w.close()
print("PASS" if ok else "FAIL")
