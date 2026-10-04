import io, json, datetime

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_trio_schema.txt"
lines = []
p = r"results\fund_value_p1\nulls.jsonl"
with io.open(p, "rb") as f:
    data = f.read()
rows = [ln for ln in data.split(b"\n") if ln.strip()]
lines.append("rows=%d" % len(rows))
j = json.loads(rows[-1])
lines.append("last row keys: %s" % sorted(j.keys()))
lines.append("last row sample: %s" % json.dumps(j, ensure_ascii=False)[:600])
j0 = json.loads(rows[0])
lines.append("first row sample: %s" % json.dumps(j0, ensure_ascii=False)[:400])

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")
