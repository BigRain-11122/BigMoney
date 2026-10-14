# -*- coding: utf-8 -*-
# _r1012bmc_gap7_atpush_run.py -- POOL-0012 gap7 harvest estate atomic push (group tree)
# Patches ROOT in Tools/git-atomic-push.py for bm-c (K:\Fluxgroup\FluxGroup), builds spec,
# runs tool with CWD=group root. Zero local-tree touch (Data API atomic chain).
import json, os, subprocess, sys

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP = r"K:\Fluxgroup\FluxGroup"
TOOL_SRC = os.path.join(GRP, "Tools", "git-atomic-push.py")
TOOL_RUN = os.path.join(BM, "results", "_r1012bmc_atpush_tool.py")
SPEC = os.path.join(BM, "results", "_r1012bmc_atpush_spec.json")

# 1) patch ROOT (bm-a hardcoded path -> bm-c group root)
src = open(TOOL_SRC, encoding="utf-8").read()
old_root = 'ROOT = r"C:\\Users\\sjs20\\Desktop\\FluxGroup"'
new_root = 'ROOT = r"K:\\Fluxgroup\\FluxGroup"'
assert old_root in src, "ROOT anchor not found in tool source"
if old_root not in src:
    print("ABORT: ROOT anchor missing"); sys.exit(1)
open(TOOL_RUN, "w", encoding="utf-8", newline="\n").write(src.replace(old_root, new_root))
print("tool patched ->", TOOL_RUN)

BASE = "cph4/fleet/mv0001-handover/outbound/krea2/kf-demo-20261012"
BMC_LOCAL = os.path.join(GRP, BASE.replace("/", os.sep), "bmc")

mp4s = ["INT1_desk_breath", "INT2_paper_fight", "INT3_photo_stare",
        "INT4_rubbing_glow", "INT5_head_bow", "D03b_direct_gaze", "E01c_first_line"]
files = []
for m in mp4s:
    files.append({"mode": "full", "path": "%s/bmc/i2v/%s.mp4" % (BASE, m),
                  "local": os.path.join(BMC_LOCAL, "i2v", m + ".mp4"),
                  "expect_origin_blob": "NEW"})
for f in ["v3gap7_r1011_progress.json", "v3gap7_r1011_receipt.json", "v3gap7_qc_sheet_r1012.jpg"]:
    files.append({"mode": "full", "path": "%s/bmc/%s" % (BASE, f),
                  "local": os.path.join(BMC_LOCAL, f),
                  "expect_origin_blob": "NEW"})
files.append({"mode": "full", "path": "%s/bmc/I2V-URL-INDEX.md" % BASE,
              "local": os.path.join(BMC_LOCAL, "I2V-URL-INDEX.md"),
              "expect_origin_blob": "9ddc907dcc65d9c8dfa9ef2dc607ca29ed601129"})

orders_line = ("| 10-15 03:1x | **MV V3 gap7 七镜补产收割交付回执（POOL-0012 done·O-20261013-2200 全本地令执行件·bm-c r1012 死窗遗产收口）** "
    "| ①7/7 DELIVERED（gap7 runner 02:53:28 自然收工·v3gap7_r1011_receipt.json）：INT1_desk_breath 821469B/INT2_paper_fight 905283B/INT3_photo_stare 755567B/INT4_rubbing_glow 748653B/INT5_head_bow 897269B/D03b_direct_gaze 751856B/E01c_first_line 605510B——七 CDN URL 全行见 bmc/I2V-URL-INDEX.md 七新行；"
    "②字节终验（INDEX-SKIP 律合规收割）=_r1012bmc_gap7_byteverify.json **7/7 ALL-MATCH**（本地 mp4=CDN HEAD Content-Length=declared 三方恒等）；"
    "③q88 看板 v3gap7_qc_sheet_r1012.jpg 板检 PASS：7/7 有画零破格零 HUD 零浮空·六格琥珀暖调统一·INT2_paper_fight 单格冷蓝调=装配站 fin 统一调色单镜修法面（非重烧面·导演席裁定）；"
    "④7 mp4+progress+receipt+board+INDEX 七新行全上链（本 commit 原子推）；"
    "⑤**@bm-a 装配站**：七槽落位即 asm_preflight 66 槽全解析·云引用=0 过闸律达成→V3.5 预览剪→768P 全本地终剪→成片闸（10-15 晨 CEO 成品死线·O-20261014-1855）；"
    "⑥POOL-0012 done 三元组=POOL-0012+done+证据指针（本行+byteverify json+board）·五态迁移归 CEO-PROXY 收卡 | done（bm-c 收口·poke bm-a 装配站） |")
files.append({"mode": "append", "path": "docs/orders.md", "line": orders_line})

spec = {"message": "bm-c r1012: POOL-0012 gap7 7/7 harvest delivery (7 mp4 INT8 768P + byte-verify ALL-MATCH + q88 board + INDEX 7 rows + receipt/progress; assembly station unblocked, CEO 1855 night-order chain)",
        "retry": 5, "gate_depth": 10, "files": files}
json.dump(spec, open(SPEC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("spec written:", SPEC, "files:", len(files))

# 2) run patched tool with CWD=group root
env = dict(os.environ)
env["PYTHONIOENCODING"] = "utf-8"
r = subprocess.run([sys.executable, TOOL_RUN, SPEC], cwd=GRP, env=env,
                   capture_output=True)
sys.stdout.write(r.stdout.decode("utf-8", "replace"))
sys.stderr.write(r.stderr.decode("utf-8", "replace"))
print("EXIT", r.returncode)
sys.exit(r.returncode)
