# r112 bm-c rebase storm resolver (16 UU, same-window S6 double-run family)
# canon: r106 classify+side-assert / r109 tick single-line take-new / r110 rc0+nonempty probe gate /
#        r344 pool ID-set carry (pool not conflicted this window, verified post-fold)
import json, subprocess, sys, io

def gs(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError("probe gate FAIL stage=%d path=%s rc=%d out_len=%d" % (stage, path, r.returncode, len(r.stdout)))
    return r.stdout.decode("utf-8", "replace")

UU = [
 "docs/daily_report/REPORT-2026-09-27.json",
 "docs/daily_report/REPORT-2026-09-27.md",
 "results/autofill_state.json",
 "results/compute_audit.json",
 "results/dashboard_status.js",
 "results/dashboard_status.json",
 "results/fundamental_b_layer_filter.json",
 "results/futures_update_status.json",
 "results/heat_update_status.json",
 "results/lhb_update_status.json",
 "results/prospect_promotion/_summary.json",
 "results/regime_state.json",
 "results/scorecard_v1.json",
 "results/strategy_scorecard.json",
 "results/token_usage.json",
 "results/update_status.json",
]

def _ts_of(j, keys):
    for k in keys:
        if isinstance(j, dict) and k in j:
            return str(j[k])
    return ""

def union_audit(s2, s3):
    a2, a3 = json.loads(s2), json.loads(s3)
    h2, h3 = a2.get("history", []), a3.get("history", [])
    keyed, diverge = {}, 0
    for row in h2 + h3:
        k = (str(row.get("ts")), str(row.get("machine")))
        if k in keyed and keyed[k] != row:
            diverge += 1
        keyed[k] = row
    merged = sorted(keyed.values(), key=lambda r: str(r.get("ts")))
    out = dict(a3)  # latest face = my fresher side
    out["history"] = merged
    return out, len(h2), len(h3), len(merged), diverge

def resolve():
    report = {}
    for p in UU:
        s2, s3 = gs(2, p), gs(3, p)
        if p == "results/compute_audit.json":
            out, n2, n3, nm, dv = union_audit(s2, s3)
            assert dv == 0, "same-ts-diverge on audit: %d" % dv
            txt = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
            json.loads(txt)
            report[p] = "union hist %d+%d->%d diverge=0" % (n2, n3, nm)
        elif p == "results/regime_state.json":
            a2, a3 = json.loads(s2), json.loads(s3)
            if a2.get("history") == a3.get("history"):
                txt = s3
                report[p] = "identical-ledgers take-new (updated %s)" % _ts_of(a3, ["updated"])
            else:
                keyed = {}
                for row in a2.get("history", []) + a3.get("history", []):
                    keyed[str(row.get("ts") or row.get("asof") or row.get("date"))] = row
                a3["history"] = sorted(keyed.values(), key=lambda r: str(r.get("ts") or r.get("asof")))
                txt = json.dumps(a3, ensure_ascii=False, indent=1) + "\n"
                report[p] = "ledger-union -> %d" % len(a3["history"])
        elif p.endswith(".json"):
            j2, j3 = json.loads(s2), json.loads(s3)
            t2 = _ts_of(j2, ["updated", "generated", "generated_at", "ts"])
            t3 = _ts_of(j3, ["updated", "generated", "generated_at", "ts"])
            assert t3 >= t2, "side-assert FAIL %s: s3=%s < s2=%s" % (p, t3, t2)
            txt = s3
            json.loads(txt)
            report[p] = "take-new s3 (ts %s > %s)" % (t3 or "none", t2 or "none")
        elif p.endswith(".js"):
            assert s3.startswith("window.DASH_DATA = "), "js format-assert FAIL"
            json.loads(s3[len("window.DASH_DATA = "):].rstrip().rstrip(";"))
            assert "<<<<<<<" not in s3 and ">>>>>>>" not in s3
            txt = s3
            report[p] = "take-new s3 (js wrapper format-assert ok)"
        else:  # .md twin
            assert s3.startswith("# ") and "<<<<<<<" not in s3 and ">>>>>>>" not in s3 and len(s3) > 1000
            txt = s3
            report[p] = "take-new s3 (md twin, same-side as json)"
        with io.open(p.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
            f.write(txt)
        r = subprocess.run(["git", "add", p], capture_output=True)
        assert r.returncode == 0, "git add FAIL %s: %s" % (p, r.stderr.decode("utf-8", "replace"))
    with io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r112bmc_resolve.json", "w", encoding="utf-8", newline="") as f:
        json.dump({"resolved": report, "n_uu": len(UU)}, f, ensure_ascii=False, indent=1)
    print("RESOLVED %d files:" % len(UU))
    for k, v in report.items():
        print("  %s -> %s" % (k, v))

if __name__ == "__main__" and sys.argv[1:] == ["resolve"]:
    resolve()

if __name__ == "__main__" and sys.argv[1:] == ["probe"]:
    for p in UU:
        s2, s3 = gs(2, p), gs(3, p)
        j2 = json.loads(s2) if p.endswith(".json") else None
        j3 = json.loads(s3) if p.endswith(".json") else None
        info = []
        if j2 is not None:
            for tag, j in (("s2", j2), ("s3", j3)):
                ks = sorted(j.keys()) if isinstance(j, dict) else "?"
                info.append("%s keys=%s" % (tag, ks[:9]))
                for k in ("ts", "generated", "generated_at", "updated_at", "updated", "last_tick", "last_fetch", "asof", "date"):
                    if isinstance(j, dict) and k in j:
                        info[-1] += " %s=%s" % (k, j[k])
                if isinstance(j, dict) and "history" in j:
                    info[-1] += " hist=%d last_ts=%s" % (len(j["history"]), j["history"][-1].get("ts") if j["history"] else None)
        else:
            for tag, s in (("s2", s2), ("s3", s3)):
                info.append("%s head=%r len=%d" % (tag, s[:80], len(s)))
        print("## %s" % p)
        print("   " + " | ".join(info))
