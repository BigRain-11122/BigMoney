# -*- coding: utf-8 -*-
"""r89 bm-c probe: pick-1 (r87 ba823b0f onto 14e18c3b) CODELY+archive face recon before canon resolve.
Origin side = post-18th-batch (bm-a r333 archival) + bm-b r331 merged (f3a01cb5); mine = r87 8994B form.
Goal: mine_new composition vs origin-archive accounting (does filtering mine_new by oa_text
preserve zero-loss while keeping origin's 18th-batch stub-landing intact?)."""
import subprocess, json

def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout

def blobs(path):
    return git("show", f":1:{path}"), git("show", f":2:{path}"), git("show", f":3:{path}")

# ---- CODELY recon
b, o, t = blobs("CODELY.md")
bl, ol, tl = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
bl_l, ol_l, tl_l = bl.splitlines(), ol.splitlines(), tl.splitlines()
print(f"CODELY sizes: base={len(bl.encode('utf-8'))}B origin={len(ol.encode('utf-8'))}B mine={len(tl.encode('utf-8'))}B")
bs, os_, ms = set(bl_l), set(ol_l), set(tl_l)
mine_new = [l for l in tl_l if l not in bs and l not in os_]
orig_new = [l for l in ol_l if l not in bs and l not in ms]
print(f"mine_new x{len(mine_new)} orig_new x{len(orig_new)}")

# archive blobs for accounting
oa = blobs("research/memory-archive/202609.md")[1].decode("utf-8")
ta = blobs("research/memory-archive/202609.md")[2].decode("utf-8")
in_oa = [l for l in mine_new if l in oa]
not_oa = [l for l in mine_new if l not in oa]
print(f"mine_new: in-origin-archive x{len(in_oa)} NOT-in-oa x{len(not_oa)}")
for l in not_oa:
    print("  NEW->", l[:150])
print(f"orig_new x{len(orig_new)} preview (first 6):")
for l in orig_new[:6]:
    print("  ONEW->", l[:150])
canons = [l for l in ol_l if l.startswith("- 坑律正典全量归档")]
print(f"canon lines x{len(canons)}")
for c in canons:
    print("  CANON len=", len(c), c[:100])
r330_in_ol = [l for l in ol_l if l.startswith("- [2026-09-27 14:5x r330 bm-b]")]
print(f"r330 stub in origin CODELY: {len(r330_in_ol)}")
r330_full_in_final_check = ("r330 bm-b] 坑律：**移植" in oa) or ("r330 bm-b] 坑律：**移植" in ta)
print(f"r330 full text in origin-archive or my-archive: {r330_full_in_final_check}")

# ---- archive recon
bb, ob, tb = blobs("research/memory-archive/202609.md")
bd, od, td = bb.decode("utf-8"), ob.decode("utf-8"), tb.decode("utf-8")
print(f"\narchive sizes: base={len(bd)}B origin={len(od)}B mine={len(td)}B")
print(f"prefix: od.startswith(bd)={od.startswith(bd)} td.startswith(bd)={td.startswith(bd)}")
my_suf = td[len(bd):] if td.startswith(bd) else None
if my_suf is not None:
    print(f"my suffix {len(my_suf)}B, 十七批 mentions in it: {my_suf.count('十七批')}")
    print("suffix head:", my_suf[:200].replace(chr(10), ' | '))
final_preview = od + my_suf if my_suf is not None else None
if final_preview:
    print(f"coexist final {len(final_preview)}B, 十七批 count={final_preview.count('十七批')}, r328 dup={final_preview.count('r328 bm-a] 坑律：**腾讯')}")
    print(f"r330 full in final: {'r330 bm-b] 坑律：**移植' in final_preview}")
# zero-loss: my suffix lines present in origin already?
suf_lines = [l for l in my_suf.splitlines() if l.strip()] if my_suf else []
dup_in_od = [l for l in suf_lines if l in od]
uniq_suf = [l for l in suf_lines if l not in od]
print(f"my suffix lines x{len(suf_lines)}: already-in-origin x{len(dup_in_od)} unique x{len(uniq_suf)}")
print("PROBE-R89B-OK")
