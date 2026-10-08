# -*- coding: utf-8 -*-
"""r774 bm-c: A-direction pre-start outbound delivery (ORD 10-08 19:25 item-4:
过门即推合同路径). Gate-passed assets this round: st3_goddess_c (white-robe
7/8/7), st1_library_z3_composite (8/8/9 first-ever library PASS), st2_carve_i
(quick-cut silhouette 8/8/7). Converts to jpg q88 (r770 outbound law), writes
A-DIRECTION-v1.md delivery note (CEO plain-language menu + honest 3-PASS/
4-FAIL ledger), CAS direct-invest to group repo fleet/mv0001-handover/
outbound/ (temp-index + commit-tree + push sha:main, r814/r770 precedent;
40-hex hard asserts + fatal/rejected/failed/error scan + post-push fetch
ls-tree self-proof)."""
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
RECEIPT = os.path.join(R, "results", "_r774bmc_outbound_cas.json")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
NAMES = ["st3_goddess_c", "st1_library_z3_composite", "st2_carve_i"]

NOTE = """# MV0001 A 向预开工交付单 v1（本轮新增 3 张过门图）

- **交付时间**: 2026-10-08 19:5x（bm-c 产线·承您 19:25「全面开工」令+O-1715 自决授权·您勾选前先动·产出可复用）
- **一句话总结**: A 向（本地合成法再修）今晚再出一轮已兑现——3 张新图全过三律门，其中书库双影是这条线三代失败后**首次过门**；您原来的 A/B/C 三选项不变，A 向的弹药现已备齐。

## 一、本轮新增过门资产（3 张·判词=真实感/构图/考据 三律各 10 分制）

| # | 场 | 文件 | 真实感 | 构图 | 考据 | 判 | 一句话 |
|---|---|---|---|---|---|---|---|
| 1 | 女神显影·**白裙版** | st3_goddess_c.jpg | 7 | 8 | 7 | **PASS** | 白袍确认（象牙白·非青）·与已过门的 b 版烟青构成**裙色双版菜单**——您只需勾裙色（原版记忆点=白裙 vs 本地生成自然偏烟青） |
| 2 | 书库双影·合成法 v3 | st1_library_z3_composite.jpg | 8 | 8 | 9 | **PASS** | **三代失败后首次过门**：两个时代同框拍子成立——左下现代读碑人+中右古代书吏软鬼影双影分离、陶碗明火零错置、无圣书体混入；考据 9 分为本包最高 |
| 3 | 刻字仪式·**快切剪影备选** | st2_carve_i.jpg | 8 | 8 | 7 | **PASS** | 纯手+芦苇笔逆光剪影·**文字弱化=刻意设计**（本地模型画不清楔形字的能力边界用「不画字」绕开）·适配分镜 S5/S6 的 0.5-2 秒快切 |

## 二、诚实台账（本轮 7 次生成+2 次合成迭代·3 过 4 败·全留档 results/mv_work/kf/）

1. **4 张败作如实报**：goddess_d 种子漂移（5/8/2·婚纱+罗马桥错置）·glass_c 青色收窄失败（7/8/5·青窗吃掉半幅+铅条窗错置）·carve_j 俯拍缺手（5/4/3·泥板读作巧克力）·z 首版合成面板硬边（5/7/7·已由 z3 亮度掩码修法取代）。
2. **玻璃场无新交付**：glass_c 收窄尝试失败后，该场维持原评审包 a 版（7/7/7·已过门）为最佳、b 版（6/8/7）备选——您在原菜单勾即可。
3. **合成法两次迭代**：z 面板瑕疵根因=「纯黑背景」负词失效（实测全图 71% 像素为 205 亮度浅面板）→z3 改暗剪影乘法鬼影（面板零贡献）一次过门。

## 三、菜单状态（不变·弹药已备齐）

- **勾 A（本地再修·推荐）**：书库用 z3（8/8/9）+刻字用 carve_i 或原 f 版（7/8/5·氛围最佳）进视频施工·女神裙色二选一——**今晚即可全速开工**。
- **勾 B（云端通道）**：仍可把书库/刻字关键帧换云端出图再过门（两场景的云端可达性判例在册）。
- **勾 C（您改构图）**：本轮 3 张新图亦可作构图参考底。
- **视频段维持冻结**等您点头（照令执行）；解冻后按分镜表+调色链正典施工。

---
*本包样图全部本地 SDXL 生成（RTX 3070 16GB·ComfyUI），云端多模态盲评 7 次过门（token 用量入账）；生成台账+逐张判词留档 bigmoney results/mv_work/kf/（v6 批 7 张+合成 z/z2/z3 全留）。*
"""

MSG = ("mv0001 A-direction pre-start delivery v1 (bm-c r774, ORD 19:25 item-4, "
       "O-1715 self-decision): 3 gate-passed assets -- goddess WHITE-ROBE c "
       "7/8/7 (dress-color dual menu with smoke-cyan b), library "
       "double-shadow composite z3 8/8/9 (first PASS after 3 generations of "
       "FAILs, two-era-in-one-frame beat landed, zero anachronism), carve "
       "quick-cut silhouette i 8/8/7 (text-weak by design, sidesteps local "
       "SDXL cuneiform ceiling); honest ledger 3-PASS/4-FAIL (d seed drift / "
       "glass_c cyan window overrun -- glass lane keeps a 7/7/7 / carve_j "
       "hands absent / z panel edge superseded by z3 luminance-mask); A/B/C "
       "menu unchanged, A-option ammo stocked; video lane stays frozen "
       "until CEO OK")


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
    note_p = os.path.join(OUTJ, "A-DIRECTION-v1.md")
    with open(note_p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(NOTE)
    shutil.copy2(note_p, os.path.join(DEST, "A-DIRECTION-v1.md"))
    files.append("fleet/mv0001-handover/outbound/A-DIRECTION-v1.md")
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
