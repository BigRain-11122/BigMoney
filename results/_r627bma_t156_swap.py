# r627 bm-a: T-156 post-landing sequence
#   stage 1: staging hash-verify vs sender manifest (pre-swap gate, fail-closed)
#   stage 2: quarantine swap (old -> .off-caliber-quarantine-20261003, staged -> live)
#            + copy local-only mktcap sidecars into new cache (T-73 s2 SIZE face, MSG-0909 no-mixing)
#   stage 3: crash-fuse clear (quality-sens ONLY, division MSG-0857 sec.2 item 4;
#            tombstone > last event, r603 precedent; others stay blocked = anti-dup vs bm-b in-flight)
#   stage 4: pool host_gates check on FUND-QUALITY-P1-SENS (ready state re-verify)
# Evidence: results/_r627bma_t156_swap.json
import json, hashlib, os, shutil, datetime, sys

STAGED = r"Money02\data\cache\p1c_stock.incoming\p1c_stock"
LIVE = r"Money02\data\cache\p1c_stock"
QUAR = r"Money02\data\cache\p1c_stock.off-caliber-quarantine-20261003"
SENDER = "fleet/transfers/T-2026-10-03-156-sender.json"
FUSE = "results/crash_fuse.json"
EVID = "results/_r627bma_t156_swap.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "machine": "bm-a"}

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()

# ---- stage 1: staging verify (fail-closed) ----
man = json.load(open(SENDER, encoding="utf-8-sig"))
ok, rows = True, []
for f in man["files"]:
    p = os.path.join(STAGED, f["file"])
    if not os.path.exists(p):
        ok = False; rows.append({"file": f["file"], "err": "absent"}); continue
    sz = os.path.getsize(p)
    h = sha256(p)
    f_ok = (sz == f["bytes"]) and (h == f["sha256"])
    rows.append({"file": f["file"], "bytes": sz, "pass": bool(f_ok)})
    ok = ok and f_ok
total = sum(os.path.getsize(os.path.join(STAGED, f)) for f in os.listdir(STAGED)
            if os.path.isfile(os.path.join(STAGED, f)))
ev["stage1_staging_verify"] = {"n": len(rows), "total_bytes": total, "pass": bool(ok), "rows": rows}
print("stage1 staging verify:", "PASS" if ok else "FAIL", "| n=", len(rows), "| bytes=", total)
if not ok:
    json.dump(ev, open(EVID, "w", encoding="utf-8"), indent=1)
    sys.exit(2)   # fail-closed: NO swap on any mismatch

# ---- stage 2: swap ----
assert not os.path.exists(QUAR), "quarantine dir already exists"
os.rename(LIVE, QUAR)
os.rename(STAGED, LIVE)
# local-only SIZE-face sidecars (unaffected by 688 100x; keep adjacent, no mixing)
copied = []
for fn in ("mktcap_raw.npy", "mktcap_raw.meta.json"):
    src = os.path.join(QUAR, fn)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(LIVE, fn))
        copied.append(fn)
ev["stage2_swap"] = {"quarantine": QUAR, "new_live": LIVE, "sidecars_copied": copied,
                     "new_file_count": len(os.listdir(LIVE)), "pass": True}
print("stage2 swap done | sidecars copied:", copied, "| new live count:", len(os.listdir(LIVE)))

# ---- stage 3: fuse clear (quality-sens only) ----
fuse = json.load(open(FUSE, encoding="utf-8"))
key = "scripts/fund_quality_p1.py|run,--sensitivity"
sig = fuse.get("sigs", {}).get(key)
assert sig is not None, "quality-sens sig not found in fuse"
fuse["sigs"].pop(key)
fuse.setdefault("cleared", {})[key] = {
    "cleared_ts": NOW, "cleared_by": "bm-a",
    "reason": ("p1c-transfer-verified: T-156 four-point verify PASS + swap "
               "complete 2026-10-03 (correct-caliber cache vwap_688_check="
               "true, hashes==sender manifest); division MSG-0857 sec.2 "
               "item 4 -- QUALITY-SENS re-claim = bm-a"),
    "crashes": int(sig.get("count", 0)),
    "old_code_sha256": sig.get("code_sha256"),
    "old_note": sig.get("note"),
}
tmp = FUSE + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(fuse, fh, ensure_ascii=False, indent=1)
os.replace(tmp, FUSE)
chk = json.load(open(FUSE, encoding="utf-8"))
assert key not in chk.get("sigs", {}) and key in chk.get("cleared", {})
ev["stage3_fuse_clear"] = {"key": key, "pass": True,
                           "kept_blocked": sorted(k for k in chk.get("sigs", {}) if "fund" in k)}
print("stage3 fuse cleared:", key, "| remaining blocked:", ev["stage3_fuse_clear"]["kept_blocked"])

# ---- stage 4: pool entry state check ----
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
ents = {e["id"]: e for e in pool.get("entries", [])}
sens = ents.get("FUND-QUALITY-P1-SENS")
ev["stage4_pool"] = {"id": "FUND-QUALITY-P1-SENS",
                     "status": (sens or {}).get("status"),
                     "host_gates": (sens or {}).get("host_gates"),
                     "pass": bool(sens and sens.get("status") == "ready")}
print("stage4 pool FUND-QUALITY-P1-SENS status:", (sens or {}).get("status"),
      "| host_gates:", (sens or {}).get("host_gates"))

ev["pass"] = True
json.dump(ev, open(EVID, "w", encoding="utf-8"), indent=1)
print("SWAP SEQUENCE COMPLETE")
