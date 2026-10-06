# _r769bmb_nulls_repair.py -- frankenline repair (split multi-object line, enforce trailing newline)
# + three-way account HEAD/stash/current for fund trio nulls ledgers (r769 surgery incident audit)
import subprocess, json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = json.JSONDecoder()

def split_objects(line):
    """Split a line that may contain multiple concatenated JSON objects."""
    objs, idx, s = [], 0, line.strip()
    while idx < len(s):
        while idx < len(s) and s[idx] in " \t\r":
            idx += 1
        if idx >= len(s):
            break
        obj, end = DEC.raw_decode(s, idx)
        objs.append(json.dumps(obj, sort_keys=True, ensure_ascii=False))
        idx = end
    return objs

def repair_file(path):
    b = open(path, "rb").read()
    text = b.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    raw_lines = text.split("\n")
    out_lines, multi_fixed = [], 0
    for ln in raw_lines:
        if not ln.strip() or ln.strip() == "":
            continue
        if "\r" in ln:
            ln = ln.replace("\r", "")
        try:
            json.loads(ln)
            out_lines.append(ln)
        except json.JSONDecodeError:
            parts = split_objects(ln)
            if len(parts) >= 2:
                out_lines.extend(parts)
                multi_fixed += 1
            else:
                out_lines.append(ln)  # unparseable for other reason: keep verbatim (crash-tail law)
    if out_lines and not b.endswith(b"\n"):
        pass  # we always write with trailing newline below
    data = ("\n".join(out_lines) + "\n").encode("utf-8")
    open(path, "wb").write(data)
    return len(out_lines), multi_fixed

def blob(ref, p):
    r = subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True, cwd=REPO)
    return r.stdout if r.returncode == 0 else None

def keys_of(b):
    d = {}
    for l in b.decode("utf-8").splitlines():
        if not l.strip():
            continue
        try:
            o = json.loads(l)
            d[o["key"]] = o
        except Exception:
            pass
    return d

report = {}
for fam in ["fund_divlowvol_p1", "fund_quality_p1", "fund_value_p1"]:
    p = f"results/{fam}/nulls.jsonl"
    n, fixed = repair_file(os.path.join(REPO, p))
    hk = keys_of(blob("HEAD", p) or b"")
    sk = keys_of(blob("stash@{0}", p) or b"")
    ck = keys_of(open(os.path.join(REPO, p), "rb").read())
    var = [k for k in (set(hk) & set(ck)) if json.dumps(hk[k], sort_keys=True) != json.dumps(ck[k], sort_keys=True)]
    head_missing = sorted(set(hk) - set(ck))
    cur_new_vs_head = sorted(set(ck) - set(hk))
    stash_missing_vs_cur = sorted(set(sk) - set(ck))
    report[fam] = {
        "rows_after_repair": n, "frankenlines_fixed": fixed,
        "head_rows": len(hk), "stash_rows": len(sk), "cur_rows": len(ck),
        "keys_in_HEAD_missing_from_current": head_missing[:15],
        "keys_in_current_not_in_HEAD": cur_new_vs_head[:15],
        "keys_in_stash_missing_from_current": stash_missing_vs_cur[:15],
        "same_key_content_variants_HEAD_vs_current": var[:8],
    }

with open(os.path.join(REPO, "results/_r769bmb_nulls_audit.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
    f.write("\n")
print(json.dumps(report, ensure_ascii=False, indent=1)[:3200])
