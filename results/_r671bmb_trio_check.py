import json, io, os, time, datetime

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_trio_check.txt"
lines = []

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

pool = json.load(open(r"results\runnable_pool.json", encoding="utf-8"))
entries = pool.get("entries") or pool.get("shards") or {}
if isinstance(entries, list):
    entries = {e.get("id", str(i)): e for i, e in enumerate(entries)}
lines.append("pool type ok, entries=%d" % len(entries))
for k, e in entries.items():
    if "nulls" in str(k).lower() or "fund" in str(k).lower():
        lines.append("POOL: %s status=%s owner=%s owner_since=%s progress=%s" % (
            k, e.get("status"), e.get("owner"), e.get("owner_since"),
            (e.get("progress") or e.get("done") or "")))

for fam in ["fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"]:
    p = r"results\%s\nulls.jsonl" % fam
    if os.path.exists(p):
        with io.open(p, "rb") as f:
            data = f.read()
        n = data.count(b"\n")
        lines.append("%s: bytes=%d lines=%d mtime=%s" % (
            fam, len(data), n,
            datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M:%S")))
        # last line ts if parseable
        last = data.rstrip(b"\n").split(b"\n")[-1] if n else b""
        try:
            j = json.loads(last)
            lines.append("  last: round=%s ts=%s shard=%s" % (j.get("round"), j.get("ts") or j.get("wall"), str(j.get("shard_id") or j.get("id"))[:40]))
        except Exception as ex:
            lines.append("  last parse: %r" % (ex,))

# crash fuse
cf = r"results\crash_fuse.json"
if os.path.exists(cf):
    j = json.load(io.open(cf, encoding="utf-8"))
    keep = {k: v for k, v in j.items() if "nulls" in k.lower() or "fund" in k.lower()}
    lines.append("fuse trio-related keys: " + json.dumps(keep, ensure_ascii=False)[:600])

# autofill state
af = r"results\autofill_state.bm-b.json"
if os.path.exists(af):
    j = json.load(io.open(af, encoding="utf-8"))
    lines.append("autofill_state: " + json.dumps(j, ensure_ascii=False)[:900])

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")
