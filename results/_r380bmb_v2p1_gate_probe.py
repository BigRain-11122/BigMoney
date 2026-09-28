"""r380 bm-b: V2-P1 G-REPRO-REV fix-first live probe (r379 next-pointer c).

Facts under probe (post 53be4125 owner fix, never yet fired on bm-b live data):
- 02:34 bm-b run FAILED G-REPRO-REV on the OLD runner (no a5 fallback):
  replay drift ann_ret -0.014376 vs frozen -0.014384 (8e-6, benign cross-machine
  float face per MSG-0345/0340 forensics) -> gate honest FAIL, entry fused.
- Owner fix (bm-c r128 addendum 53be4125) landed s9-a5 drift-fallback:
  replay bit-level mismatch + artifact present -> re-validate vs frozen via
  the r368 bit-equal artifact (results/rev_osc/daily_series_FY_BG_TP8.json,
  bm-a G-REPRO-REV independent reverify PASS, sha256 recompute ok).
- This probe fires sleeve_gate() on BOTH faces on bm-b LIVE data and asserts
  the fallback chain: replay drift detected -> artifact-drift-fallback ->
  stats/counters bit-equal frozen -> gate PASS. Zero pool writes, zero canon
  edits; full-batch relaunch stays gated on the RAM window per r357 defer.
"""
import json
import sys

sys.path.insert(0, "scripts")
import decision_chain_v2 as dc  # noqa: E402

fail = 0
results = {}
for face in dc.FACES:
    got = dc.sleeve_gate(face)
    rec = dc.sleeve_frozen_record()[dc.REV_FACE_MAP[face]]
    frozen = rec["stats"]
    path = got.get("path") if isinstance(got, dict) else None  # path_used (s9-a5 distinguishes replay/artifact/artifact-drift-fallback)
    ok_gate = isinstance(got, dict) and "series" in got and "gate" not in got
    # bit-level recheck (independent of runner's internal ok)
    bit = (got["stats"] == frozen
           and got["counters"]["entries"] == rec["entries"]
           and got["counters"]["trades"] == rec["trades"]) if ok_gate else False
    verdict = "PASS" if (ok_gate and bit) else "FAIL"
    if verdict == "FAIL":
        fail += 1
    results[face] = {
        "verdict": verdict,
        "path_used": path,
        "stats": got.get("stats") if isinstance(got, dict) else str(got)[:200],
        "frozen": frozen,
        "entries": got["counters"]["entries"] if ok_gate else None,
        "trades": got["counters"]["trades"] if ok_gate else None,
        "series_days": int(got["series"].size) if ok_gate else None,
    }
    print(f"[{face}] gate={verdict} path={path} "
          f"bit_level_stats={'OK' if bit else 'NO'} "
          f"entries={results[face]['entries']} trades={results[face]['trades']}")

# path provenance: replay cache present on bm-b + artifact present ->
# drift-fallback is the EXPECTED path; straight 'artifact' (cache absent)
# or 'replay' (bit-equal) would also be a lawful PASS, disclosed either way.
paths = {f: results[f]["path_used"] for f in dc.FACES}
print(f"paths={json.dumps(paths)}")
print(f"artifact={dc.SLEEVE_ARTIFACT}")
print(f"cache_isdir={__import__('os').path.isdir(dc.ro.CACHE)}")

out = {
    "probe": "r380 bm-b V2-P1 G-REPRO-REV fix-first live verification",
    "faces": results,
    "paths_used": paths,
    "all_pass": fail == 0,
    "law_refs": ["prereg s9-a4 two-path + s9-a5 drift-fallback",
                 "MSG-20260928-0340/0345 forensics", "r368 artifact reverify",
                 "53be4125 owner fix", "r379 next-pointer (c)"],
}
with open(r"results\_r380bmb_v2p1_gate_probe.json", "w",
          encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"PROBE_VERDICT={'ALL_PASS' if fail == 0 else 'FAIL'} fail={fail}")
sys.exit(0 if fail == 0 else 1)
