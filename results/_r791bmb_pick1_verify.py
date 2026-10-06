import subprocess, json, os, sys
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
receipt = {"window": "pick1-r789-onto-a4699768d verify+finish (r790 session died mid-resolve, this round completes)", "faces": {}}

def load(p):
    raw = open(p, "rb").read()
    return raw, raw.decode("utf-8")

# ---- 1) CODELY.md: verify prior session's line-level resolution in worktree ----
p = "CODELY.md"
raw, txt = load(p)
lines = txt.splitlines()
markers = [l for l in lines if l.startswith(("<<<<<<< ", ">>>>>>> ", "||||||| ", "======="))]
assert not markers, f"CODELY markers remain: {markers[:3]}"
for pref, n in (("- 域指针·r789 bm-b", 1), ("- [2026-10-07 00:3x r644 bm-c]", 1), ("- 域指针·r644 bm-c", 1),
                ("- 冷层指针（r800 合并", 1), ("- [2026-10-06 21:3x r640 bm-c]", 0), ("- [2026-10-06 23:4x r642 bm-c]", 0),
                ("- [2026-10-06 23:5x r787 bm-b]", 0)):
    c = sum(1 for l in lines if l.startswith(pref))
    assert c == n, f"CODELY {pref!r} count={c} expected={n}"
moji = [l[:50] for l in lines if l.startswith(("å", "¸", "¥", "¨", "¿", "æ"))]
assert not moji, f"mojibake fragments remain: {moji}"
sz = os.path.getsize(p)
assert sz <= 30720, f"CODELY.md {sz}B > 30KB gate"
receipt["faces"][p] = {"recipe": "prior-session line-union verified", "bytes": sz, "lines": len(lines)}

# ---- 2) pit-git-resolver.md: verify prior session's keep-ours-insertion ----
p = "research/pit-git-resolver.md"
raw, txt = load(p)
out = txt.splitlines()
# r637: line-start anchored only; content-embedded marker quotes are legal registry prose
bad = [l[:60] for l in out if l.startswith(("<<<<<<< ", ">>>>>>> ", "||||||| ", "======="))]
assert not bad, f"pit line-start markers remain: {bad}"
r642 = sum(1 for l in out if l.startswith("- [2026-10-06 23:4x r642 bm-c]"))
r787 = sum(1 for l in out if l.startswith("- [2026-10-06 23:5x r787 bm-b]"))
assert r642 == 1 and r787 == 1, f"r642={r642} r787={r787}"
r = subprocess.run(["git", "show", ":3:research/pit-git-resolver.md"], capture_output=True)
assert r.returncode == 0 and r.stdout, "stage3 read failed"
s3lines = [l for l in r.stdout.decode("utf-8").splitlines() if l.strip()]
merged = [l for l in out if l.strip()]
assert set(s3lines) <= set(merged), "pit merged != stage3 superset (line-level union must contain ours/HEAD face)"
receipt["faces"][p] = {"recipe": "prior-session keep-ours-r642 verified; stage3-superset ok", "lines": len(out)}

# ---- 3) attrition: take stage2 (origin newer ts), rc0 confirmed by guard ----
p = "results/_attrition_guard_scan.json"
r = subprocess.run(["git", "show", ":2:" + p], capture_output=True)
assert r.returncode == 0 and r.stdout, "stage2 read failed"
b2 = r.stdout
d = json.loads(b2.decode("utf-8"))
assert d["ts"] == "2026-10-07T00:59:54+08:00", f"unexpected stage2 face: {d.get('ts')}"
assert d["active_loss"] is False, f"stage2 active_loss={d['active_loss']}"
# check stage3 ts is the older ours face (confirming newer-wins direction)
r3 = subprocess.run(["git", "show", ":3:" + p], capture_output=True)
d3 = json.loads(r3.stdout.decode("utf-8"))
assert d3["ts"] == "2026-10-07T00:49:52+08:00", f"unexpected stage3 face: {d3.get('ts')}"
open(p, "wb").write(b2)
back = json.loads(open(p, "rb").read().decode("utf-8"))
assert back == d, "attrition write-back mismatch"
receipt["faces"][p] = {"recipe": "take-stage2-origin-newer (rc0, r773 precedent)", "ts": d["ts"], "stage3_ts": d3["ts"]}

with open("results/_r791bmb_pick1_verify.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
sys.stdout.write("PICK1-VERIFY-OK CODELY=%dB pit=r642+r787 attrition=stage2(00:59:54)\n" % receipt["faces"]["CODELY.md"]["bytes"])
