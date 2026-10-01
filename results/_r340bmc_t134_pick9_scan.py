"""r340 bm-c: T-134 s2 NINTH conversion pick -- evidence-order rescan (r304 measurement-first law).

Sources:
  A) results/multicore_census.json verdicts -> remaining single_core list
  B) results/runnable_pool.json -> live registrations + shards (re-burn likelihood face)
  C) results/watermark_red.json -> next_pick queued families (re-burn likelihood face)
Law: rank by (historical burn elapsed evidence) x (re-burn likelihood);
     file-size/reputation intuition forbidden (r304); <100ms-unit families
     deprioritized honestly (r327 law).
Output: results/_r340bmc_t134_pick9.json (pick receipt, pick8 format parity)
"""
import json
import os
import re

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)


def main():
    census = load(r"results/multicore_census.json")
    verdicts = census["verdicts"]
    single = []
    for path, v in verdicts.items():
        cls = v.get("verdict") or v.get("class") if isinstance(v, dict) else v
        if cls == "single_core":
            single.append((path, v if isinstance(v, dict) else {}))
    print("single_core n =", len(single))

    pool = load(r"results/runnable_pool.json")
    entries = pool.get("entries") or pool.get("batches") or []
    if isinstance(entries, dict):
        entries = list(entries.values())
    wm = load(r"results/watermark_red.json")
    next_pick = wm.get("next_pick") or {}
    next_pick_s = json.dumps(next_pick, ensure_ascii=False)

    # cross-reference each single_core runner against pool + WM faces
    rows = []
    for path, v in single:
        name = os.path.basename(path)
        stem = name.replace(".py", "")
        pool_hits = []
        for e in entries:
            blob = json.dumps(e, ensure_ascii=False)
            if stem in blob:
                pool_hits.append(e.get("id") or e.get("batch_id") or "?")
        wm_hit = stem in next_pick_s or name in next_pick_s
        ev = v.get("evidence") or []
        ev_s = " ; ".join(ev)[:300] if isinstance(ev, list) else str(ev)[:300]
        rows.append({
            "runner": path,
            "census_evidence": ev_s,
            "pool_refs": pool_hits,
            "wm_next_pick_hit": wm_hit,
        })
        flag = "  <== POOL" if pool_hits else ""
        flag += " <== WM" if wm_hit else ""
        print(f"{name}{flag}")
        if flag or True:
            print(f"    ev: {ev_s[:200]}")
            if pool_hits:
                print(f"    pool: {pool_hits[:6]}")

    out = {
        "round": "r340 bm-c",
        "ticket": "T-2026-09-30-134 s2 ninth conversion pick (evidence-order rescan per r304 measurement-first law)",
        "generated_at": "2026-10-01T23:5x+08:00",
        "single_core_remaining": [r["runner"] for r in rows],
        "faces": rows,
        "wm_next_pick": next_pick,
    }
    with open(os.path.join(ROOT, r"results/_r340bmc_t134_pick9_scan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("WROTE results/_r340bmc_t134_pick9_scan.json")


if __name__ == "__main__":
    main()
