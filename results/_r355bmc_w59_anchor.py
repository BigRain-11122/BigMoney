def _main():
    import subprocess, json
    REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
    out = subprocess.check_output(["git", "-C", REPO, "show",
        "origin/main:results/perpetual_faces/n1_w59_results.json"])
    j = json.loads(out.decode("utf-8"))
    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                p = path + "/" + str(k)
                if "p95" in str(k).lower() or "p9" in str(k).lower():
                    print("P95FACE", p, "=", v if not isinstance(v, (dict, list)) else type(v).__name__)
                walk(v, p)
        elif isinstance(o, list):
            for i, v in enumerate(o[:2]):
                walk(v, path + "/%d" % i)
    walk(j)
    print("TOP_KEYS", sorted(j.keys()))
    npc = j.get("null_pool_cumulative", {})
    print("NPC_KEYS", sorted(npc.keys()) if isinstance(npc, dict) else type(npc).__name__)
    # find the A-family p95 anchor: look in a-family summary blocks
    for key in j:
        v = j[key]
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, (int, float)) and ("p95" in k2 or "p9" in k2):
                    print("NUM", key, "/", k2, "=", v2)
                if isinstance(v2, dict):
                    for k3, v3 in v2.items():
                        if isinstance(v3, (int, float)) and ("p95" in k3 or "p9" in k3):
                            print("NUM", key, "/", k2, "/", k3, "=", v3)
if __name__ == "__main__":
    _main()
