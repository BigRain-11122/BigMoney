"""r458 bm-c FUND-NULLS watch: nulls burn progress (3 families, K=2000 each)
+ origin pool claim face + r457 surgery adoption-confirmation readout.
Writes JSON evidence to results/_r458bmc_fundnulls_watch.json (file-out form,
r446 probe law). Reuses r457 probe logic verbatim."""
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
OUT = os.path.join(ROOT, "results", "_r458bmc_fundnulls_watch.json")


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
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
          "target_k": 2000, "local_nulls": {}, "origin_pool": {}, "adoption": {}}
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
    rc, blob, err = git_raw(["show", "origin/main:results/runnable_pool.json"])
    if rc != 0:
        ev["origin_pool"] = {"read_fail": err[:160]}
    else:
        ev["origin_pool"] = shard_state(blob)
    q = ev["origin_pool"].get("FUND-QUALITY-P1-NULLS", {})
    ev["adoption"] = {
        "r457_surgery_restore_ts": "2026-10-04 09:11:39",
        "owner": q.get("owner"),
        "owner_since": q.get("owner_since"),
        "confirmed": (q.get("owner") == "bm-b"
                      and str(q.get("owner_since", "")) > "2026-10-04 09:11:39"),
        "note": "owner_since newer than surgery restore ts = bm-b daemon keepalive refresh = r288 gate passed = self-adoption confirmed (r457 pointer (a) closed)",
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("WROTE", OUT)
    print(json.dumps(ev["adoption"], ensure_ascii=False))
    for fam, v in ev["local_nulls"].items():
        print(fam, v if isinstance(v, str) else f"{v['unique_k']}/{v['of']}")


if __name__ == "__main__":
    main()
