"""r681 bm-a schema check: lhb_detail + lhb_seat columns, UTF-8 dump (r680 law: no GBK console guessing)."""
import os, json
import pandas as pd

OUT = {}

# detail face (full history, r680 census used it)
dd = pd.read_parquet(r"Money02/data/lhb/lhb_detail.parquet")
OUT["detail_cols"] = list(dd.columns)
OUT["detail_rows"] = int(len(dd))
OUT["detail_day_range"] = [str(dd["上榜日"].min()) if "上榜日" in dd.columns else "?", str(dd["上榜日"].max()) if "上榜日" in dd.columns else "?"]
OUT["detail_sample"] = dd.head(2).to_dict("records")

# seat face (sampled windows)
fs = [f for f in sorted(os.listdir(r"Money02/data/lhb_seat")) if f.endswith(".parquet")]
frames = [pd.read_parquet(os.path.join(r"Money02/data/lhb_seat", f)) for f in fs[:6]]
sd = pd.concat(frames, ignore_index=True)
OUT["seat_cols"] = list(sd.columns)
OUT["seat_n_files"] = len(fs)
OUT["seat_sample_rows"] = int(len(sd))
# code-day key coverage: how many seat (code,day) pairs are joinable to detail
if "SECURITY_CODE" in sd.columns and "TRADE_DATE" in sd.columns:
    sd["code"] = sd["SECURITY_CODE"].astype(str).str.zfill(6)
    sd["day"] = sd["TRADE_DATE"].astype(str).str.slice(0, 10)
    OUT["seat_unique_code_day"] = int(sd.groupby(["code", "day"]).ngroups)
    OUT["seat_unique_seats"] = int(sd["OPERATEDEPT_CODE"].nunique()) if "OPERATEDEPT_CODE" in sd.columns else -1

with open(r"results/_r681bma_lhb_seat_schema.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1, default=str)
print("SCHEMA_DUMP_DONE detail_rows=%d seat_files=%d" % (OUT["detail_rows"], OUT["seat_n_files"]))
