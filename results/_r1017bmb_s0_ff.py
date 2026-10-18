"""r1017 bm-b S0 FF resolution: save live shared faces -> discard -> ff-merge -> restore live-wins/union faces.
Law: r982 (daemon live-writer faces stay dirty, never committed by bm-b), r1028 (ts-newer-wins), r1008 (token_usage per-machine union)."""
import sys, os, json, shutil

BASE = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
KEEP = os.path.join(BASE, r"results\_r1017bmb_s0")
LIVE = [r"fleet\machine-health.json", r"results\watermark_red.json", r"results\token_usage.json"]
DISCARD = [r"results\lhb_update_status.json", r"results\futures_update_status.json"]

phase = sys.argv[1]
os.makedirs(KEEP, exist_ok=True)

if phase == "save":
    for f in LIVE:
        src = os.path.join(BASE, f)
        dst = os.path.join(KEEP, os.path.basename(f))
        shutil.copy2(src, dst)
        print("SAVED", f, os.path.getsize(src), "bytes")
elif phase == "restore":
    # live-wins faces: copy saved (newer local daemon) back over worktree -> stays dirty per r982 policy
    for f in LIVE[:2]:
        src = os.path.join(KEEP, os.path.basename(f))
        dst = os.path.join(BASE, f)
        shutil.copy2(src, dst)
        print("RESTORED-LIVE", f)
    # token_usage: union -- base = current (origin-committed) face, overlay bm-b rows + any missing machine keys from saved local
    cur_p = os.path.join(BASE, r"results\token_usage.json")
    loc_p = os.path.join(KEEP, "token_usage.json")
    cur = json.load(open(cur_p, encoding="utf-8"))
    loc = json.load(open(loc_p, encoding="utf-8"))
    changed = 0
    lm, cm = loc.get("machines"), cur.get("machines")
    if isinstance(lm, dict) and isinstance(cm, dict):
        for k, v in lm.items():
            if k == "bm-b" or k not in cm:
                if cm.get(k) != v:
                    cm[k] = v
                    changed += 1
    ll, cl = loc.get("l2_local_llm"), cur.get("l2_local_llm")
    if isinstance(ll, dict) and isinstance(cl, dict):
        for k, v in ll.items():
            if k == "bm-b" and cl.get(k) != v:
                cl[k] = v
                changed += 1
    tmp = cur_p + ".tmp"
    json.dump(cur, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, cur_p)
    print("TOKEN_USAGE union applied, overlaid rows:", changed)
