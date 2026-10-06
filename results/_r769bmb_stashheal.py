# _r769bmb_stashheal.py -- bm-b r769: zero-loss heal of dead-session autostash (stash@{0})
# Law basis: r758 x2_watch_log union law (append-only jsonl union + stable ts sort; naive concat violates ts order),
#            r620 daemon live law (dict faces live-wins), mixed-dict recipe (last_tick ts-newer whole-dict take),
#            r756 ts normalization (space->T before parse; never lexicographic compare).
import subprocess, json, os, sys, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def stash_blob(path):
    r = subprocess.run(["git", "show", "stash@{0}:" + path], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f"stash blob {path}: rc={r.returncode}")
    return r.stdout

def norm_ts(v):
    if not isinstance(v, str) or len(v) < 16:
        return None
    s = v.strip()
    if s[10] == " ":
        s = s[:10] + "T" + s[11:]
    try:
        from datetime import datetime
        return datetime.fromisoformat(s).timestamp()
    except Exception:
        return None

receipt = {"round": "r769", "machine": "bm-b", "heal": "autostash zero-loss union", "faces": [], "asserts": [], "superseded_variants": []}

# ---- 1. satengine history_bm-b.jsonl: union + stable ts sort (r758 x2 law) ----
p = "results/saturation_engine/history_bm-b.jsonl"
disk_b = open(os.path.join(REPO, p), "rb").read()
stash_b = stash_blob(p)
crlf = b"\r\n" in disk_b
nl = b"\r\n" if crlf else b"\n"
disk_lines = [l for l in disk_b.decode("utf-8").split(nl.decode()) if l.strip()]
stash_lines = [l for l in stash_b.decode("utf-8").split("\n") if l.strip()]
disk_set = set(disk_lines)
stash_only = [l for l in stash_lines if l not in disk_set]
union = disk_lines + stash_only
def row_ts(l):
    try:
        return norm_ts(json.loads(l).get("ts"))
    except Exception:
        return None
union.sort(key=lambda l: (row_ts(l) is None, row_ts(l) or 0))  # stable: None-tail, ts-asc
with open(os.path.join(REPO, p), "wb") as f:
    f.write(nl.decode().join(union).encode("utf-8") + nl)
verify = [l for l in open(os.path.join(REPO, p), "rb").read().decode("utf-8").split("\n") if l.strip()]
receipt["faces"].append({"path": p, "recipe": "union+ts-stable-sort", "disk_rows": len(disk_lines),
                        "stash_rows": len(stash_lines), "recovered": len(stash_only), "after": len(verify)})
receipt["asserts"].append({"face": p, "assert": "post-write rows == disk+recovered (or more if daemon raced in)",
                           "ok": len(verify) >= len(disk_lines) + len(stash_only)})
if len(verify) < len(disk_lines) + len(stash_only):
    print("HEAL FAIL: rows lost on write:", p); sys.exit(2)

# ---- 2. fund nulls x2: key-indexed heal (append-only by 'key'/'k'; same-key variant = live disk wins, stash logged) ----
for p in ["results/fund_divlowvol_p1/nulls.jsonl", "results/fund_quality_p1/nulls.jsonl"]:
    disk_b = open(os.path.join(REPO, p), "rb").read()
    crlf = b"\r\n" in disk_b
    nl_s = "\r\n" if crlf else "\n"
    disk_lines = [l for l in disk_b.decode("utf-8").split(nl_s) if l.strip()]
    stash_lines = [l for l in stash_blob(p).decode("utf-8").split("\n") if l.strip()]
    disk_keys = {}
    for l in disk_lines:
        try:
            disk_keys[json.loads(l)["key"]] = l
        except Exception:
            disk_keys[None] = l
    recovered, variants = [], []
    for l in stash_lines:
        try:
            k = json.loads(l)["key"]
        except Exception:
            continue
        if k not in disk_keys:
            recovered.append(l)
        elif disk_keys[k] != l:
            variants.append({"key": k, "stash_row": l, "disk_row": disk_keys[k]})
    merged = disk_lines + recovered
    merged.sort(key=lambda l: (json.loads(l).get("k", 0) if not isinstance(l, str) else 0) if False else (lambda ll: json.loads(ll).get("k", 0))(l))
    with open(os.path.join(REPO, p), "wb") as f:
        f.write(nl_s.join(merged).encode("utf-8") + ((nl_s if disk_b.endswith(b"\n") else "").encode("utf-8")))
    keys_final = [json.loads(l).get("key") for l in merged]
    receipt["faces"].append({"path": p, "recipe": "key-indexed-union", "disk_rows": len(disk_lines),
                             "recovered_new_keys": len(recovered), "superseded_variants": len(variants), "after": len(merged)})
    receipt["superseded_variants"] += [{"path": p, **v} for v in variants]
    if len(keys_final) != len(set(keys_final)):
        print("HEAL FAIL: duplicate keys in", p); sys.exit(2)

# ---- 3. autofill_state.bm-b.json: launches identical (probed 50/50); last_tick ts-newer whole-dict take (recipe) ----
p = "results/autofill_state.bm-b.json"
head_b = subprocess.run(["git", "show", "HEAD:" + p], capture_output=True, cwd=REPO).stdout
head_j = json.loads(head_b)
stash_j = json.loads(stash_blob(p))
lt_head = (head_j.get("last_tick") or {}).get("ts")
lt_stash = (stash_j.get("last_tick") or {}).get("ts")
diff_keys = [k for k in set(list(head_j) + list(stash_j)) if head_j.get(k) != stash_j.get(k)]
take_stash_tick = norm_ts(lt_stash) is not None and (norm_ts(lt_head) is None or norm_ts(lt_stash) > norm_ts(lt_head))
merged = dict(head_j)
if take_stash_tick:
    merged["last_tick"] = stash_j["last_tick"]
# detect format from HEAD blob
fmt = None
for ind in (1, 2, 3, 4):
    for sep in ((",", ": "), (",", ":")):
        for ea in (False, True):
            s = json.dumps(head_j, indent=ind, separators=sep, ensure_ascii=ea)
            if s.encode("utf-8") == head_b or (s + "\n").encode("utf-8") == head_b:
                fmt = (ind, sep, ea, head_b.endswith(b"\n"))
                break
ind, sep, ea, tnl = fmt if fmt else (2, (",", ": "), False, True)
out = json.dumps(merged, indent=ind, separators=sep, ensure_ascii=ea) + ("\n" if tnl else "")
open(os.path.join(REPO, p), "wb").write(out.encode("utf-8"))
json.loads(open(os.path.join(REPO, p), "rb").read())  # parse gate
receipt["faces"].append({"path": p, "recipe": "mixed-dict: last_tick ts-newer whole-dict, rest live-wins",
                         "diff_keys_vs_HEAD": diff_keys, "took_stash_last_tick": bool(take_stash_tick),
                         "lt_head": lt_head, "lt_stash": lt_stash})
receipt["asserts"].append({"face": p, "assert": "isinstance(last_tick, dict) after write",
                           "ok": isinstance(json.loads(open(os.path.join(REPO, p), "rb").read()).get("last_tick"), dict)})

with open(os.path.join(REPO, "results/_r769bmb_stashheal_receipt.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(json.dumps(receipt, ensure_ascii=False, indent=1)[:2000])
