import subprocess, json, os, sys
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

def blob(ref, p):
    r = subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"blob {ref}:{p} rc={r.returncode} len={len(r.stdout)}")
    return r.stdout

receipt = {"window": "rebase2-pick1-r789-onto-a4699768d", "faces": {}, "guard": "CODELY.md=rc3-registry(line-level only) pit-git-resolver=rc3-registry(line-level only) attrition=rc0-restorable"}

def load(p):
    raw = open(p, "rb").read()
    txt = raw.decode("utf-8")
    nl = "\r\n" if "\r\n" in txt else "\n"
    return txt, nl

def save(p, lines, nl):
    open(p, "wb").write(nl.join(lines).encode("utf-8"))

# ---- 1) CODELY.md: line-level conflict-block resolution (idempotent: 0 hunks = already resolved, verify only) ----
p = "CODELY.md"
txt, nl = load(p)
lines = txt.split(nl)
if any(l.startswith("<<<<<<<") for l in lines):
    out, i, hunks = [], 0, 0
    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            j = i
            while not lines[j].startswith(">>>>>>>"):
                j += 1
            block_o, sep, block_m, k = [], None, [], i + 1
            while k < j:
                if lines[k].startswith("======="):
                    sep = k
                elif sep is None:
                    block_o.append(lines[k])
                else:
                    block_m.append(lines[k])
                k += 1
            hunks += 1
            if hunks == 1:
                # origin(HEAD/onto) block = [r644-QA, blank]; ours block = [] -> take origin block
                assert any("r644 bm-c" in l for l in block_o) and block_m == [], f"hunk1 shape: o={block_o} m={block_m}"
                out.extend(block_o); receipt["faces"][p] = {"hunk1": "take-origin-block(r644-QA kept, ours-empty=r640-deletion honored)"}
            else:
                # hunk2: union ours-block(blank,r789) + origin-block(r644) in chronological order
                assert any("r789 bm-b" in l for l in block_m) and any("r644 bm-c" in l for l in block_o), f"hunk2 shape: o={block_o} m={block_m}"
                out.extend(block_m); out.extend(block_o)
                receipt["faces"][p]["hunk2"] = "union ours(r789)+origin(r644) chronological"
            i = j + 1
        else:
            out.append(lines[i]); i += 1
    assert hunks == 2, f"expected 2 hunks, saw {hunks}"
else:
    out = lines
    receipt["faces"][p] = {"hunks": "already-resolved (idempotent rerun)"}
# surgical line removal: r640/r642 entries (ours' migration intent), r787 absent (both deleted)
removed = []
final = []
for l in out:
    if l.startswith("- [2026-10-06 21:3x r640 bm-c]") or l.startswith("- [2026-10-06 23:4x r642 bm-c]") or l.startswith("- [2026-10-06 23:5x r787 bm-b]"):
        removed.append(l[:60]); continue
    final.append(l)
save(p, final, nl)
receipt["faces"][p]["removed_lines"] = removed
# assertions (line-start anchored per r637: content-embedded marker quotes are legal)
for l in final:
    assert not l.startswith(("<<<<<<< ", ">>>>>>> ", "||||||| ", "=======")), f"marker line-start left: {l[:60]}"
for pref, n in (("- 域指针·r789 bm-b", 1), ("- [2026-10-07 00:3x r644 bm-c]", 1), ("- 域指针·r644 bm-c", 1),
                ("- 冷层指针（r800 合并", 1), ("- [2026-10-06 21:3x r640 bm-c]", 0), ("- [2026-10-06 23:4x r642 bm-c]", 0),
                ("- [2026-10-06 23:5x r787 bm-b]", 0)):
    c = sum(1 for l in final if l.startswith(pref))
    assert c == n, f"CODELY {pref!r} count={c} expected={n}"
moji = [l[:50] for l in final if l.startswith(("å", "¸", "¥", "¨", "¿", "æ"))]
assert not moji, f"mojibake fragments remain: {moji}"
sz = os.path.getsize(p)
assert sz <= 30720, f"CODELY.md {sz}B > 30KB gate"
receipt["faces"][p]["final_lines"] = len(final); receipt["faces"][p]["bytes"] = sz

# ---- 2) pit-git-resolver.md: line-level, keep ours-insertion (r642), drop markers ----
p = "research/pit-git-resolver.md"
txt, nl = load(p)
lines = txt.split(nl)
out, i, hunks = [], 0, 0
while i < len(lines):
    if lines[i].startswith("<<<<<<<"):
        j = i
        while not lines[j].startswith(">>>>>>>"):
            j += 1
        block_o, sep, block_m, k = [], None, [], i + 1
        while k < j:
            if lines[k].startswith("======="):
                sep = k
            elif sep is None:
                block_o.append(lines[k])
            else:
                block_m.append(lines[k])
            k += 1
        hunks += 1
        # origin block empty (deleted region), ours block = r642 insertion -> keep ours block
        assert block_o == [] and any("r642 bm-c" in l for l in block_m), f"pit hunk shape: o={block_o} m={block_m}"
        out.extend(block_m)
        i = j + 1
    else:
        out.append(lines[i]); i += 1
assert hunks == 1, f"expected 1 pit hunk, saw {hunks}"
save(p, out, nl)
full = nl.join(out)
assert "<<<<<<<" not in full and ">>>>>>>" not in full
r642 = sum(1 for l in out if l.startswith("- [2026-10-06 23:4x r642 bm-c]"))
r787 = sum(1 for l in out if l.startswith("- [2026-10-06 23:5x r787 bm-b]"))
assert r642 == 1 and r787 == 1, f"r642={r642} r787={r787}"
s3 = blob(":3", p).decode("utf-8")
s3lines = [l for l in s3.splitlines() if l.strip()]
merged = [l for l in out if l.strip()]
assert set(s3lines) == set(merged), "pit merged != stage3 content (superset check)"
receipt["faces"][p] = {"recipe": "line-level keep-ours-insertion r642; content==stage3 superset verified", "lines": len(out)}

# ---- 3) _attrition_guard_scan.json: rc0 restorable, take stage2 (origin newer ts) ----
p = "results/_attrition_guard_scan.json"
b2 = blob(":2", p)
d = json.loads(b2.decode("utf-8"))
assert d["ts"] == "2026-10-07T00:59:54+08:00" and d["active_loss"] is False, f"unexpected origin face: {d.get('ts')}"
open(p, "wb").write(b2)
back = json.loads(open(p, "rb").read().decode("utf-8"))
assert back == d, "attrition write-back mismatch"
receipt["faces"][p] = {"recipe": "take-stage2-origin-newer (rc0 restorable, r773 precedent)", "ts": d["ts"]}

with open("results/_r790bmb_rebase2_resolve.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
sys.stdout.write("PICK1-RESOLVE-OK hunks: CODELY=2(line-union) pit=1(keep-r642) attrition=take-new\n")
