"""r671 diagnose: parquet period_end values vs expected compact format."""
import pandas as pd
D = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\data\fund_statement_export"
import sys
sys.path.insert(0, r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\scripts")
import update_fund_statements as ufs

w = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_diag.txt", "w", encoding="utf-8")
for face in ("cashflow", "balance", "income"):
    df = pd.read_parquet(D + f"\\{face}_faces.parquet", columns=["period_end"])
    vals = df["period_end"].astype(str).unique()[:3]
    w.write(f"{face}: dtype={df['period_end'].dtype} sample={list(vals)} n_unique={df['period_end'].nunique()}\n")
exp = ufs.expected_period_set(ufs.dt.datetime.now())
w.write(f"expected n={len(exp)} sample={sorted(exp)[:3]}\n")
cov, rows = ufs.panel_coverage()
for k, v in cov.items():
    inter = len(v & exp)
    w.write(f"gate-face {k}: cov_n={len(v)} intersection_with_expected={inter} sample={sorted(v)[:2]}\n")
w.close()
print("diag written")
