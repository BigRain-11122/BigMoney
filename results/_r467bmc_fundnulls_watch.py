"""r467 bm-c FUND-NULLS watch: nulls burn progress (3 families, K=2000 each)
+ origin pool claim face + keepalive freshness + delta vs r466 baseline.
Schema = r466 watch json. Round-numbered copy per r461 law.
File-out per r446 probe law."""
import datetime
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMS = {
    "VALUE": "results/fund_value_p1/nulls.jsonl",
    "QUALITY": "results/fund_quality_p1/nulls.jsonl",
    "DIVLOWVOL": "results/fund_divlowvol_p1/nulls.jsonl",
}
R466_BASE = {"VALUE": 726, "QUALITY": 560, "DIVLOWVOL": 412}
OUT = os.path.join(ROOT, "results", "_r467bmc_fundnulls_watch.json")


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def shard_state(blob):
    out = {}
    try:
        d = json.loads(blob.decode("utf-8-sig"))
    except Exception as e:  # noqa: BLE001
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
          "delta_vs_r466": {}, "keepalive_freshness": {}}
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
        ev["local_nulls"][fam] = {"unique_k": len(ks), "of": 2000}
        base = ev["local_nulls"][fam]
        if isinstance(base, dict):
            ev["delta_vs_r466"][fam] = base["unique_k"] - R466_BASE.get(fam, 0)
    rc, blob, err = git_raw(["show", "origin/main:results/runnable_pool.json"])
    if rc != 0:
        ev["origin_pool"] = {"read_fail": err[:160]}
    else:
        ev["origin_pool"] = shard_state(blob)
    for eid, st in ev["origin_pool"].items():
        if not isinstance(st, dict) or "owner_since" not in st:
            continue
        age_min = None
        healthy = False
        try:
            os_dt = datetime.datetime.strptime(st["owner_since"], "%Y-%m-%d %H:%M:%S")
            age_min = round((now - os_dt).total_seconds() / 60.0, 1)
            healthy = 0 <= age_min <= 15
        except Exception:  # noqa: BLE001
            pass
        ev["keepalive_freshness"][eid] = {"owner": st.get("owner"),
                                          "owner_since": st.get("owner_since"),
                                          "age_min": age_min, "healthy": healthy}
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("WROTE", OUT)
    for fam, v in ev["local_nulls"].items():
        print(fam, v if isinstance(v, str) else f"{v['unique_k']}/{v['of']}",
              "delta", ev["delta_vs_r466"].get(fam))
    for eid, kf in ev["keepalive_freshness"].items():
        print(eid, "age_min", kf.get("age_min"), "healthy", kf.get("healthy"))


if __name__ == "__main__":
    main()
