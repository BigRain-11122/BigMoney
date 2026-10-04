"""r464 bm-c cumulative-face containment check: token_usage/compute_audit/
attrition histories both sides -- union vs newer-wins decision evidence."""
import json
import subprocess

C = 0x08000000


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       creationflags=C, cwd=".")
    return json.loads(r.stdout.decode("utf-8", "replace"))


def main():
    tu_h = show("HEAD", "results/token_usage.json")
    tu_o = show("origin/main", "results/token_usage.json")
    print("token_usage HEAD keys:", list(tu_h.keys())[:10])
    print("token_usage ORIGIN keys:", list(tu_o.keys())[:10])
    for label, d in (("HEAD", tu_h), ("ORIGIN", tu_o)):
        for k, v in d.items():
            if isinstance(v, dict):
                print(f"  {label}.{k}: dict keys={list(v.keys())[:8]}")
            elif isinstance(v, list):
                print(f"  {label}.{k}: list len={len(v)}")
            else:
                print(f"  {label}.{k}: {str(v)[:60]}")
    # containment: does HEAD contain all ORIGIN sub-keys/rows?
    def flat(x, prefix=""):
        out = set()
        if isinstance(x, dict):
            for k, v in x.items():
                out |= flat(v, prefix + "/" + str(k))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                out |= flat(v, prefix + f"[{i}]")
        else:
            out.add(prefix + "=" + str(x))
        return out
    fh, fo = flat(tu_h), flat(tu_o)
    print("TU: origin-only leaves:", len(fo - fh), "| head-only leaves:", len(fh - fo))
    for x in sorted(fo - fh)[:10]:
        print("   O-ONLY", x[:120])

    ca_h = show("HEAD", "results/compute_audit.json")
    ca_o = show("origin/main", "results/compute_audit.json")
    hh, ho = ca_h.get("history", []), ca_o.get("history", [])
    print("compute_audit history len HEAD/ORIGIN:", len(hh), len(ho))
    keys_h = [h.get("ts") for h in hh][-5:]
    keys_o = [h.get("ts") for h in ho][-5:]
    print("  HEAD tail ts:", keys_h)
    print("  ORIGIN tail ts:", keys_o)
    print("  latest ts HEAD:", ca_h.get("latest", {}).get("ts"),
          "| ORIGIN:", ca_o.get("latest", {}).get("ts"))
    o_only = [h.get("ts") for h in ho if h.get("ts") not in {x.get("ts") for x in hh}]
    print("  ORIGIN-only history rows:", len(o_only), o_only[:5])

    ag_h = show("HEAD", "results/_attrition_guard_scan.json")
    ag_o = show("origin/main", "results/_attrition_guard_scan.json")
    print("attrition HEAD keys:", list(ag_h.keys()))
    print("attrition ORIGIN keys:", list(ag_o.keys()))
    for label, d in (("HEAD", ag_h), ("ORIGIN", ag_o)):
        for k, v in d.items():
            if isinstance(v, list):
                print(f"  {label}.{k}: list len={len(v)} tail={str(v[-1])[:100] if v else ''}")


if __name__ == "__main__":
    main()
