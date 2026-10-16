# r1025 bm-a group-side scan: consume D-19 deltas (decisions/orders) + POOL cards + C-20261016-05 dimension list
# Method: python subprocess raw-bytes canonical (r814 lineage). Zero tree-touch on group repo.
import subprocess, json, os, re, sys, datetime

GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_r1025bma_ordscan.json")
res = {"ts": None, "err": None, "dec_rows": [], "ord_rows": [], "pool_cards": {}, "case_c05_excerpt": None, "origin_tip": None}

def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or GROUP, capture_output=True)

try:
    r = run(["git", "fetch", "origin"])
    if r.returncode != 0:
        res["err"] = "fetch rc=%d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:300])
    r = run(["git", "rev-parse", "origin/main"])
    res["origin_tip"] = r.stdout.decode("utf-8", "replace").strip()

    def show(path):
        r = run(["git", "show", "origin/main:" + path])
        if r.returncode != 0:
            return None
        return r.stdout  # raw bytes

    dec = show("docs/decisions.md")
    if dec is not None:
        text = dec.decode("utf-8", "replace")
        lines = text.splitlines()
        seen = set()
        for i, ln in enumerate(lines):
            if re.search(r"D-2026101[67]-\d+", ln):
                res["dec_rows"].append({"i": i, "text": ln[:400]})
                seen.add(ln[:400])
        tail = lines[-120:]
        for j, ln in enumerate(tail):
            if re.search(r"BigMoney|bigmoney|quant", ln, re.I) and ln[:400] not in seen:
                res["dec_rows"].append({"i": len(lines)-120+j, "text": ln[:400], "tail_hit": True})

    ord_ = show("docs/orders.md")
    if ord_ is not None:
        text = ord_.decode("utf-8", "replace")
        lines = text.splitlines()
        tail = lines[-150:]
        for j, ln in enumerate(tail):
            if re.search(r"BigMoney|bigmoney|quant", ln, re.I):
                res["ord_rows"].append({"i": len(lines)-150+j, "text": ln[:400]})

    pool = show("cph4/fleet/dispatcher/POOL.json")
    if pool is not None:
        try:
            pj = json.loads(pool.decode("utf-8", "replace"))
            items = pj if isinstance(pj, list) else pj.get("cards", pj.get("items", []))
            if isinstance(items, dict):
                items = list(items.values())
            for c in items:
                cid = str(c.get("id", c.get("card_id", "")))
                if cid in ("POOL-0003", "POOL-0013", "POOL-0015", "POOL-0016", "POOL-0017"):
                    res["pool_cards"][cid] = c
        except Exception as e:
            res["pool_parse_err"] = repr(e)
            res["pool_raw_head"] = pool.decode("utf-8", "replace")[:2000]

    r = run(["git", "ls-tree", "-r", "--name-only", "origin/main", "cph4/council/"])
    if r.returncode == 0:
        names = r.stdout.decode("utf-8", "replace").splitlines()
        c05 = [n for n in names if "C-20261016-05" in n]
        if c05:
            raw = show(c05[0])
            if raw is not None:
                text = raw.decode("utf-8", "replace")
                keep = [ln for ln in text.splitlines() if re.search(
                    r"维度清单|gpu_mode|gpu_free_vram_mb|互斥|键名|心跳", ln)]
                res["case_c05_excerpt"] = keep[:60]
                res["case_c05_file"] = c05[0]
except Exception as e:
    res["err"] = repr(e)

res["ts"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("ORDSCAN_DONE rows: dec=%d ord=%d cards=%d err=%s" % (
    len(res["dec_rows"]), len(res["ord_rows"]), len(res["pool_cards"]), res["err"]))
