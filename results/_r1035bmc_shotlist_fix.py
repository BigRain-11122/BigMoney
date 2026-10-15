# -*- coding: utf-8 -*-
# r1035 bm-c: SHOTLIST S3-20 anchor-tail VAGUE remnant fix (gate-miss disclosure)
#   origin blob -> remove redundant tail ", 2001 Taiwan MV aesthetic" (supplied verbatim
#   by runner official closing block on every frame) -> lint re-scan (expect zero)
#   -> write atomic spec (full mode, blob guard) + orders receipt row
import subprocess, re, sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
G = r"K:\Fluxgroup\FluxGroup"
REL = "cph4/fleet/mv-album-001-jay/星晴-SHOTLIST-v3.md"
subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)
old = subprocess.run(["git", "-C", G, "show", "origin/main:" + REL], capture_output=True).stdout
old_sha_out = subprocess.run(["git", "-C", G, "rev-parse", "origin/main:" + REL], capture_output=True)
old_sha = old_sha_out.stdout.decode("ascii").strip()
assert len(old_sha) == 40, "blob sha fetch failed: %r" % old_sha_out.stdout

txt = old.decode("utf-8")
TAIL = ", 2001 Taiwan MV aesthetic"
n = txt.count(TAIL)
print("tail occurrences:", n)
assert n == 1, "expected exactly 1 tail occurrence, got %d -- ABORT" % n
new_txt = txt.replace(TAIL, "")

# lint re-scan on patched text (same frame-extract path as runner)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
rows = [l for l in new_txt.splitlines() if l.startswith("|") and not l.startswith("|---") and not l.startswith("| 镜位")]
MULTI = re.compile(r"(S2-1[123]|S5-2[678]):\s*")
LIGHT = {"①": "warm 5200K golden daylight", "②": "2800K dusk backlight with warm halo",
         "③": "single 2200K warm lamp light", "④": "indigo night with cool starlight",
         "⑤": "slanted warm window light with dust motes"}
ID_CONST = ("a 20-year-old Taiwanese student with heavy-lidded monolid eyes, a thick lower lip, "
            "softly rounded cheeks and a thick black fringe lying flat over his eyebrows, "
            "natural matte skin with visible pores")
CLOSING = "35mm film grain, telecine texture, 2001 Taiwan music video look"
NEG = re.compile(r"\b(no|not|never|without|avoid|non-)\b|don't|can't|won't|isn't|doesn't", re.I)
VAGUE = re.compile(r"\b(beautiful|stunning|aesthetic|masterpiece|8k|dreamy|ethereal|whimsical|cozy|glass skin|porcelain skin|airbrushed|vibrant|epic|photorealistic|iconic|cinematic)\b", re.I)
CONCEPT = re.compile(r"\b(korean|k-pop|idol|salon|makeup|watermark|typography|logo)\b", re.I)
FR = []
for l in rows:
    c = [x.strip() for x in l.split("|")]
    if len(c) < 10:
        continue
    fid, batch, anchor = c[1], c[8], c[9]
    if batch != "A":
        continue
    if fid in ("S2-11/12/13", "S5-26/27/28"):
        parts = [p for p in MULTI.split(anchor) if p and not MULTI.fullmatch(p)]
        for i in range(0, len(parts) - 1, 2):
            FR.append((parts[i], parts[i + 1].strip(), c[6]))
    else:
        FR.append((fid, anchor, c[6]))
bad = 0
for fid, anchor, light in FR:
    m = re.search(r"[①②③④⑤]", light or "")
    seg = []
    if fid == "S5-30":
        seg.append(ID_CONST)
    if m:
        seg.append("lit by " + LIGHT[m.group(0)] + ",")
    seg.append(anchor if anchor.endswith(".") else anchor + ".")
    seg.append(CLOSING + ".")
    p = " ".join(seg)
    hits = sorted(set((NEG.findall(p) or []) + (VAGUE.findall(p) or []) + (CONCEPT.findall(p) or [])))
    if hits:
        bad += 1
        print("STILL-HIT", fid, hits)
print("frames:", len(FR), "| lint hits after fix:", bad)
assert len(FR) == 33 and bad == 0, "lint re-scan not clean -- ABORT"

fixed_path = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1035bmc_shotlist_fixed.md"
io.open(fixed_path, "wb").write(new_txt.encode("utf-8"))
print("fixed bytes ->", fixed_path, len(new_txt.encode("utf-8")))

ts = "2026-10-15 20:5x"
ord_row = ("| %s | **【@bm-c 回执】星晴 SHOTLIST-v3 S3-20 闸漏一字修（T1 点火前 lint 机核拦截·gate 复扫勘误）** | "
           "闸签发件称复检三名单零命中，机核实锚 S3-20 尾残留 VAGUE 词（“…grass field, 2001 Taiwan MV aesthetic”——aesthetic 命中）；"
           "修法=删该尾短语（零语义损失：runner 官方收尾块逐帧供给 “2001 Taiwan music video look” 正身·尾短语=冗余重复；"
           "同类先例=闸自身对本帧 'iconic' 删除处置）；全 33 帧离线复扫=仅此一处命中、修后 0/33 全净；"
           "SHOTLIST 正身经原子链带 blob 守卫更新（守卫 sha=%s）·烧制侧即行点火 T1 wave-1 | done（bm-c r1035） |"
           % (ts, old_sha[:10]))
spec = {"message": "bm-c r1035: xingqing SHOTLIST S3-20 anchor-tail VAGUE remnant fix (gate-miss, one-phrase deletion redundant with official closing block; lint 0/33 after)",
        "retry": 5, "gate_depth": 10,
        "files": [{"mode": "full", "path": REL, "local": fixed_path, "expect_origin_blob": old_sha},
                  {"mode": "append", "path": "docs/orders.md", "line": ord_row}]}
spec_path = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\logs\atomic_spec_xqT1shotfix.json"
json.dump(spec, io.open(spec_path, "w", encoding="utf-8"), ensure_ascii=False)
print("spec ->", spec_path)
