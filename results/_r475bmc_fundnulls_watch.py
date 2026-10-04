"""r475 bm-c FUND-NULLS watch: burn progress (3 families, K=2000 each) + origin
pool claim face + keepalive freshness + delta vs r474 watch.
Writes JSON evidence to results/_r475bmc_fundnulls_watch.json (file-out, r446 law)."""
import datetime
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FAMS = {
    "VALUE": "results/fund_value_p1/nulls.jsonl",
    "QUALITY": "results/fund_quality_p1/nulls.jsonl",
    "DIVLOWVOL": "results/fund_divlowvol_p1/nulls.jsonl",
}
R474 = os.path.join(ROOT, "results", "_r474bmc_fundnulls_watch.json")
OUT = os.path.join(ROOT, "results", "_r475bmc_fundnulls_watch.json")


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def shard_state(blob):
    out = {}
    try:
        d = json.loads(blob.decode("utf-8-sig"))
    except Exception as e:
        return {"parse_error": str(e)}
    for e in d.get("entries", []):
        if e.get("id", "").startswith("FUND-") and e.get("id", "").endswith("-NULLS"):
            sh = e.get("shards", [{}])[0]
            out[e["id"]] = {"entry_status": e.get("status"),
                            "shard_status": sh.get("status"),
                            "owner": sh.get("owner"),
                            "owner_since": sh.get("owner_since")}
    return out


def main():
    now = datetime.datetime.now()
    ev = {"ts": now.isoformat(timespec="seconds"),
          "target_k": 2000, "local_nulls": {}, "origin_pool": {},
          "delta_vs_r474": {}, "keepalive_freshness": {}}
    r474_counts = {}
    if os.path.exists(R474):
        try:
            with open(R474, encoding="utf-8") as fh:
                prev = json.load(fh)
            for fam, v in (prev.get("local_nulls") or {}).items():
                if isinstance(v, dict):
                    r474_counts[fam] = v.get("unique_k")
        except Exception:
            pass
    for fam, rel in FAMS.items():
        p = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.exists(p):
            ev["local_nulls"][fam] = "FILE-MISSING"
            continue
        ks = set()
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    j = json.loads(line)
                    k = j.get("k", j.get("key"))
                    if k is not None:
                        ks.add(k)
                except ValueError:
                    pass
        n = len(ks)
        ev["local_nulls"][fam] = {"unique_k": n, "of": 2000}
        if fam in r474_counts:
            ev["delta_vs_r474"][fam] = n - r474_counts[fam]
    rc, blob, err = git_raw(["show", "origin/main:results/runnable_pool.json"])
    if rc != 0:
        ev["origin_pool"] = {"read_fail": err[:160]}
    else:
        ev["origin_pool"] = shard_state(blob)
    for sid, face in ev["origin_pool"].items():
        if not isinstance(face, dict) or "owner_since" not in face:
            continue
        try:
            os_time = datetime.datetime.strptime(face["owner_since"],
                                                 "%Y-%m-%d %H:%M:%S")
            age_min = round((now - os_time).total_seconds() / 60.0, 1)
        except Exception:
            age_min = None
        ev["keepalive_freshness"][sid] = {
            "owner": face.get("owner"),
            "owner_since": face.get("owner_since"),
            "age_min": age_min,
            "healthy": (face.get("owner") == "bm-b" and age_min is not None
                        and age_min <= 30),
        }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("WROTE", OUT)
    for fam, v in ev["local_nulls"].items():
        if isinstance(v, dict):
            d = ev["delta_vs_r474"].get(fam, "n/a")
            print(f"{fam}: {v['unique_k']}/{v['of']} delta_r474={d}")
    for sid, fr in ev["keepalive_freshness"].items():
        print(f"{sid}: owner={fr['owner']} age_min={fr['age_min']} healthy={fr['healthy']}")


if __name__ == "__main__":
    main()
