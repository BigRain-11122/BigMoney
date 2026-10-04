# r668 bm-b burner health probe (watch duty; r667 lineage verbatim + theme-judge face)
# Laws: r659 (no tasklist /FI single-pid filter), r661 (dual-form cross evidence),
#       r660/r645 (probe output to file, ASCII-only console), r446 (probe as file)
import json
import time
from pathlib import Path

OUT = Path(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r668bmb_trio_health.json")
BASE = Path(r"C:\Fluxgroup\FluxGroup\quant\bigmoney")

def cim_full_scan():
    import subprocess
    c = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
         "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
        capture_output=True, timeout=120)
    raw = c.stdout.decode("utf-8", "replace")
    rows = json.loads(raw) if raw.strip() else []
    if isinstance(rows, dict):
        rows = [rows]
    return rows

def main():
    result = {"probe": "r668bmb_trio_health", "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
    procs = cim_full_scan()
    burners = []
    for p in procs:
        cl = (p.get("CommandLine") or "")
        if ("nulls" in cl and "fund_" in cl) or ("burn" in cl and "fund_" in cl) or "theme_judge" in cl:
            burners.append({"pid": p.get("ProcessId"), "created": p.get("CreationDate"),
                            "cmd": cl[:220]})
    result["burner_count"] = len(burners)
    result["burners"] = burners
    # dup_k check on the three nulls faces (r666 pattern)
    dup = {}
    lines_by = {}
    for fam in ("fund_value_p1", "fund_quality_p1", "fund_divlowvol_p1"):
        f = BASE / "results" / fam / "nulls.jsonl"
        ks = set()
        dupk = 0
        n = 0
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                n += 1
                try:
                    k = json.loads(line).get("k")
                except Exception:
                    continue
                if k in ks:
                    dupk += 1
                ks.add(k)
        dup[fam] = {"rows": n, "unique_k": len(ks), "dup_k": dupk}
        lines_by[fam] = n
    result["nulls_faces"] = dup
    # theme-judge burn face: frag census + burn_state marker
    tj = BASE / "results" / "theme_judge_p1"
    frags = sorted((tj / "nulls_frags").glob("*.json")) if (tj / "nulls_frags").is_dir() else []
    bs = tj / "burn_state.json"
    result["theme_judge"] = {
        "frag_count": len(frags),
        "burn_state_present": bs.is_file(),
        "burn_state": (json.loads(bs.read_text(encoding="utf-8", errors="replace"))
                       if bs.is_file() else None),
    }
    result["verdict"] = ("healthy" if len(burners) >= 3 and all(v["dup_k"] == 0 for v in dup.values())
                         else "ATTENTION")
    OUT.write_text(json.dumps(result, ensure_ascii=True, indent=1), encoding="utf-8")
    print("burners:", len(burners), "dup_k:", {k: v["dup_k"] for k, v in dup.items()},
          "rows:", lines_by, "tj_frags:", len(frags), "verdict:", result["verdict"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
