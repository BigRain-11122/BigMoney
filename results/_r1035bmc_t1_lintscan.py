# -*- coding: utf-8 -*-
# r1035 bm-c: offline lint dry-run over all 33 A-frame prompts (same build path as xq_t1_r1035.py)
import subprocess, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
md = subprocess.run(["git", "-C", r"K:\Fluxgroup\FluxGroup", "show",
                     "origin/main:cph4/fleet/mv-album-001-jay/星晴-SHOTLIST-v3.md"],
                    capture_output=True).stdout.decode("utf-8", "replace")
rows = [l for l in md.splitlines() if l.startswith("|") and not l.startswith("|---") and not l.startswith("| 镜位")]
MULTI = re.compile(r"(S2-1[123]|S5-2[678]):\s*")
LIGHT = {"①": "warm 5200K golden daylight", "②": "2800K dusk backlight with warm halo",
         "③": "single 2200K warm lamp light", "④": "indigo night with cool starlight",
         "⑤": "slanted warm window light with dust motes"}
ID_CONST = ("a 20-year-old Taiwanese student with heavy-lidded monolid eyes, a thick lower lip, "
            "softly rounded cheeks and a thick black fringe lying flat over his eyebrows, "
            "natural matte skin with visible pores")
ID_FRAMES = {"S5-30"}
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
print("frames:", len(FR))
hits_total = 0
for fid, anchor, light in FR:
    m = re.search(r"[①②③④⑤]", light or "")
    seg = []
    if fid in ID_FRAMES:
        seg.append(ID_CONST)
    if m:
        seg.append("lit by " + LIGHT[m.group(0)] + ",")
    seg.append(anchor if anchor.endswith(".") else anchor + ".")
    seg.append(CLOSING + ".")
    p = " ".join(seg)
    hits = sorted(set((NEG.findall(p) or []) + (VAGUE.findall(p) or []) + (CONCEPT.findall(p) or [])))
    if hits:
        hits_total += 1
        print("HIT", fid, hits)
        print("   anchor:", anchor)
print("total frames with hits:", hits_total)
