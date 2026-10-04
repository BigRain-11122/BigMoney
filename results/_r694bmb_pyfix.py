"""r694 bm-b: heartbeat py_cpu_pct caliber realign (my closeout probe wrote
the raw per-proc SUM 900.0; the historical series caliber is share-of-
machine = sum/cores, sub-100. One-key surgical fix, roundtrip-identity
file so a programmatic dump is byte-safe.)"""
import io
import json

HB = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-b.json"
raw = io.open(HB, "rb").read()
trailing_nl = raw.endswith(b"\n")
doc = json.loads(raw.decode("utf-8"))
old = doc["py_cpu_pct"]
assert old == 900.0, "unexpected py_cpu_pct %r (already fixed?)" % old
doc["py_cpu_pct"] = round(old / 16.0, 1)      # 16 cores, share-of-machine
out = json.dumps(doc, indent=1).encode("utf-8")
if trailing_nl:
    out += b"\n"
io.open(HB, "wb").write(out)
chk = json.load(io.open(HB, encoding="utf-8"))
assert chk["py_cpu_pct"] == 56.3, "reparse mismatch"
print("py_cpu_pct caliber fixed: 900.0 -> 56.3 (share-of-machine)")
