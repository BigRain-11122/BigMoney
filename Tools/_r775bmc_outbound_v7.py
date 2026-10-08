# -*- coding: utf-8 -*-
"""r775 bm-c: A-direction rolling continuation outbound delivery (ORD 10-08
19:25 item-4 standing rule: 过门即推合同路径). Gate-passed asset this round:
st4_glass_d 9/8/7 (glass lane NEW BEST -- photorealism 9 = project-highest,
beats glass_a 7/7/7; honest spec-deviation disclosure: cyan sliver actually
runs the full left edge ~1/4 frame, judged 7 pass). Two honest FAILs stay
local: goddess_e 6/7/6 (dual-seed pick-of-two -> c 7/8/7 wins), library z4
alpha-0.45 4/4/5 (one-notch-down hypothesis falsified, z3 8/8/9 stays canon).
Writes A-DIRECTION-v1.1.md addendum (CEO plain-language menu upgrade), CAS
direct-invest to group repo fleet/mv0001-handover/outbound/ (temp-index +
commit-tree + push sha:main, r814/r770/r774 precedent; 40-hex hard asserts +
fatal/rejected/failed/error scan + post-push fetch ls-tree self-proof)."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

from PIL import Image

G = r"K:\Fluxgroup\FluxGroup"
R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
KF = os.path.join(R, "results", "mv_work", "kf")
OUTJ = os.path.join(R, "results", "mv_work", "outbound_jpg")
DEST = os.path.join(G, "fleet", "mv0001-handover", "outbound")
RECEIPT = os.path.join(R, "results", "_r775bmc_outbound_cas.json")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
NAMES = ["st4_glass_d"]

NOTE = """# MV0001 A 向滚动续产交付单 v1.1（玻璃场升级 1 张）

- **交付时间**: 2026-10-08 20:1x（bm-c 产线·承 19:25「全面开工」令滚动续产线·O-1715 自决授权）
- **一句话总结**: 玻璃双曝光场今晚出新最佳——**真实感 9 分为全项目最高**，玻璃场主推荐从 a 版（7/7/7）换为 d 版；女神裙色择优与书库鬼影微调两项尝试诚实判负，原已过门版本维持。A/B/C 菜单不变，A 向弹药再加固。

## 一、本轮新增过门资产（1 张·三律各 10 分制）

| # | 场 | 文件 | 真实感 | 构图 | 考据 | 判 | 一句话 |
|---|---|---|---|---|---|---|---|
| 1 | 玻璃双曝光·**青缝收窄版 d** | st4_glass_d.jpg | **9** | 8 | 7 | **PASS** | 玻璃熔融纹理+胶片颗粒高度接近实拍·双曝光拍子成立·**玻璃场新主推荐**（替代 a 版 7/7/7） |

**诚实披露（考据 7 分扣分点）**：设计限定是「青色仅左下角一小条」，实际成片青色沿整条左缘自上而下约 1/4 幅面——比 c 版（青窗吃半幅·考据 5 判负）大幅收敛但未达规格；评审判 7 分过线。您若要更严的收窄版可再迭代。

## 二、诚实台账（本轮 2 张生成+1 次合成·3 次云端盲评·1 过 2 败·全留档 results/mv_work/kf/）

1. **女神白裙第二 seed 择优：e 版诚实败**（6/7/6）——精修海报感/石拱属罗马式砌法而非两河泥砖拱/白纱为现代礼服剪裁三处扣分；**择优结论=c 版（7/8/7）胜出**，裙色双版菜单维持 c（白）+b（烟青）不变。
2. **书库鬼影「透明度降一档」假设证伪**：z4（合成强度 0.45）反而被读作生硬贴图面板（4/4/5 诚实败·残留扫描线纹理穿帮）；**z3（8/8/9）维持正典**——较强鬼影（0.6）才读作摄影机内双重曝光，弱化反而露馅。
3. 玻璃 d 版青缝规格偏离如实披露（见上）。

## 三、菜单状态（不变·A 向弹药已三重加固）

- **勾 A（本地再修）**：书库用 z3（8/8/9）+刻字用 carve_i（8/8/7）+玻璃用 **d 版（9/8/7 新最佳）**+女神裙色 c/b 二选一——今晚即可全速开工。
- **勾 B（云端通道）/勾 C（您改构图）**：同前；本轮新图亦可作参考底。
- **视频段维持冻结**等您点头；解冻后按分镜表+调色链正典施工。

---
*本包样图本地 SDXL 生成（RTX 3070 16GB·ComfyUI），云端多模态盲评 3 次过门（token 用量入账）；生成台账+逐张判词留档 bigmoney results/mv_work/kf/（v7 批 2 张+合成 z4 全留）。*
"""

MSG = ("mv0001 A-direction rolling-cont delivery v1.1 (bm-c r775, ORD 19:25 "
       "item-4 standing rule): glass lane NEW BEST st4_glass_d 9/8/7 "
       "(photorealism 9 = project-highest, replaces glass_a 7/7/7 as primary "
       "rec; cyan-sliver spec deviation honestly disclosed: runs full left "
       "edge ~1/4 frame, judged 7 pass); two honest FAILs stay local: "
       "goddess_e 6/7/6 (dual-seed pick-of-two, c 7/8/7 wins, dress-color "
       "menu unchanged) + library z4 alpha-0.45 4/4/5 (one-notch-down "
       "hypothesis falsified, z3 8/8/9 stays canon -- weaker ghost reads as "
       "sticker, stronger reads as in-camera double exposure); A/B/C menu "
       "unchanged; video lane stays frozen until CEO OK")


def run(cwd, args, env=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def main():
    facts = {"legs": []}
    os.makedirs(OUTJ, exist_ok=True)
    os.makedirs(DEST, exist_ok=True)
    files = []
    for n in NAMES:
        img = Image.open(os.path.join(KF, n + ".png")).convert("RGB")
        jp = os.path.join(OUTJ, n + ".jpg")
        img.save(jp, "JPEG", quality=88)
        shutil.copy2(jp, os.path.join(DEST, n + ".jpg"))
        files.append("fleet/mv0001-handover/outbound/" + n + ".jpg")
        facts["jpg_" + n] = os.path.getsize(jp)
    note_p = os.path.join(OUTJ, "A-DIRECTION-v1.1.md")
    with open(note_p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(NOTE)
    shutil.copy2(note_p, os.path.join(DEST, "A-DIRECTION-v1.1.md"))
    files.append("fleet/mv0001-handover/outbound/A-DIRECTION-v1.1.md")
    facts["files"] = files

    idx = tempfile.mktemp(suffix=".idx")
    ok_push = False
    for attempt in range(1, 4):
        rc, _, err = run(G, ["git", "fetch", "origin"])
        if rc != 0:
            facts["legs"].append("fetch-fail-%d: %s" % (attempt, err[:200]))
            continue
        rc, base, err = run(G, ["git", "rev-parse", "origin/main"])
        base = base.strip()
        if rc != 0 or not HEX40.match(base):
            facts["legs"].append("base-bad-%d: %r %s" % (attempt, base, err[:120]))
            continue
        env = dict(os.environ, GIT_INDEX_FILE=idx)
        rc, _, err = run(G, ["git", "read-tree", base], env=env)
        if rc != 0:
            facts["legs"].append("read-tree-fail-%d: %s" % (attempt, err[:120]))
            continue
        rc, _, err = run(G, ["git", "add", "--"] + files, env=env)
        if rc != 0:
            facts["legs"].append("add-fail-%d: %s" % (attempt, err[:120]))
            continue
        rc, tree, err = run(G, ["git", "write-tree"], env=env)
        tree = tree.strip()
        if rc != 0 or not HEX40.match(tree):
            facts["legs"].append("tree-bad-%d: %r %s" % (attempt, tree, err[:120]))
            continue
        rc, newc, err = run(G, ["git", "commit-tree", tree, "-p", base, "-m", MSG])
        newc = newc.strip()
        if rc != 0 or not HEX40.match(newc):
            facts["legs"].append("commit-bad-%d: %r %s" % (attempt, newc, err[:120]))
            continue
        rc, out, err = run(G, ["git", "push", "origin", newc + ":refs/heads/main"])
        blob = (out + err)
        bad = re.search(r"fatal|rejected|failed|error", blob, re.I)
        if rc == 0 and not bad:
            facts["legs"].append("push-ok-%d base=%s newc=%s" % (attempt, base, newc))
            facts["base"] = base
            facts["newc"] = newc
            ok_push = True
            break
        facts["legs"].append("push-race-%d rc=%d: %s" % (attempt, rc, blob[:200]))
    facts["push_ok"] = ok_push

    if ok_push:
        run(G, ["git", "fetch", "origin"])
        rc, tip, _ = run(G, ["git", "rev-parse", "origin/main"])
        facts["origin_tip_after"] = tip.strip()
        rc, ls, _ = run(G, ["git", "ls-tree", "origin/main",
                            "fleet/mv0001-handover/outbound/"])
        facts["ls_tree_outbound"] = ls.strip().splitlines()
        facts["delivered"] = (tip.strip() == facts.get("newc"))
    try:
        os.remove(idx)
    except OSError:
        pass
    facts["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("OUTBOUND push_ok=%s delivered=%s newc=%s files=%d"
          % (facts["push_ok"], facts.get("delivered"), facts.get("newc"), len(files)))
    for leg in facts["legs"]:
        print(leg)
    return 0 if facts["push_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
