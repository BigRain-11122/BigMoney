# r973 rebase conflict resolver: update_status.json (newer-wins whole) + compute_audit.json (union history + newer top)
import json, re, sys

# --- update_status.json: whole-file newer-wins by ts ---
p = r"results/update_status.json"
raw = open(p, encoding="utf-8-sig").read()
if "<<<<<<<" in raw:
    # extract ours/theirs blocks
    blocks = re.findall(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n?", raw, re.S)
    print("update_status conflict blocks:", len(blocks))
    # side-level ts: parse the two full candidate documents instead of per-block
    # strategy: reconstruct ours-doc = raw with theirs-blocks replaced by ours, and vice versa
    ours_raw = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n?", lambda m: m.group(1) + "\n", raw, flags=re.S)
    theirs_raw = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n?", lambda m: m.group(2) + "\n", raw, flags=re.S)
    def get_ts(s):
        m = re.search(r'"ts":\s*"([^"]+)"', s)
        return m.group(1) if m else ""
    o_ts, t_ts = get_ts(ours_raw), get_ts(theirs_raw)
    print("ours ts:", o_ts, "| theirs ts:", t_ts)
    try:
        ours_doc = json.loads(ours_raw)
        pick_raw = ours_raw
        pick = "OURS"
    except Exception as e:
        ours_doc = None
    try:
        theirs_doc = json.loads(theirs_raw)
    except Exception as e:
        theirs_doc = None
    if ours_doc and theirs_doc:
        pick_raw = ours_raw if o_ts >= t_ts else theirs_raw
        pick = "OURS" if o_ts >= t_ts else "THEIRS"
    elif ours_doc:
        pick_raw, pick = ours_raw, "OURS-ONLY-VALID"
    elif theirs_doc:
        pick_raw, pick = theirs_raw, "THEIRS-ONLY-VALID"
    else:
        print("FATAL: neither side parses"); sys.exit(2)
    open(p, "w", encoding="utf-8", newline="").write(pick_raw)
    json.loads(open(p, encoding="utf-8").read())  # parse-verify
    print("update_status resolved:", pick)
else:
    print("update_status: no conflict markers (already clean)")

# --- compute_audit.json: union history + newer top-level ---
p2 = r"results/compute_audit.json"
raw2 = open(p2, encoding="utf-8-sig").read()
if "<<<<<<<" not in raw2:
    print("compute_audit: no conflict markers (already clean)")
else:
    ours_raw = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n?", lambda m: m.group(1) + "\n", raw2, flags=re.S)
    theirs_raw = re.sub(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n?", lambda m: m.group(2) + "\n", raw2, flags=re.S)
    A = json.loads(ours_raw)
    B = json.loads(theirs_raw)
    # top-level newer-wins by ts
    base = A if str(A.get("ts", "")) >= str(B.get("ts", "")) else B
    other = B if base is A else A
    ha = base.get("history") or []
    hb = other.get("history") or []
    # union by (ts, machine) key, preserve order: base first, then other's unseen
    seen = set()
    for h in ha:
        seen.add((str(h.get("ts")), str(h.get("machine", h.get("machine_id", "")))))
    merged = list(ha)
    added = 0
    for h in hb:
        k = (str(h.get("ts")), str(h.get("machine", h.get("machine_id", ""))))
        if k not in seen:
            seen.add(k)
            merged.append(h)
            added += 1
    base["history"] = merged
    print("compute_audit: top ts", base.get("ts"), "| history merged", len(ha), "+", added, "=", len(merged))
    open(p2, "w", encoding="utf-8", newline="").write(json.dumps(base, ensure_ascii=False, indent=1))
    json.loads(open(p2, encoding="utf-8").read())
    print("compute_audit resolved: union history + newer top")
print("RESOLVER DONE rc0")
