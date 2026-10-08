# -*- coding: utf-8 -*-
"""r767 bm-c CAS direct-drop receipt: append mv0001 acceptance line to
group-tree docs/orders.md (per O-20261008-1715/1755-bm-c receipt channel:
'回执落 docs/orders.md 承 P-2026-10-08-05 行 append', acceptance <=1h SLA).
Shared-tree discipline: group worktree is DIRTY with other machines'
half-done faces -> ZERO worktree/main-ref touch: temp-index + commit-tree +
push <sha>:main (CAS object-space drop, O-1410-era canon). All 40-hex
fields hard-asserted (CAS batch law); push verdict greps fatal/rejected/
failed/error (wrapper merged-output trap). Tail-newline guard before
append (r843 no-terminator splice family). Receipt line content written to
temp file first (registry-line SOP: line file before append, never empty)."""
import os
import re
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
CNO = 0x08000000
RECEIPT_TS = "10-08 ~15:5x"

RECEIPT_LINE = (
    "| " + RECEIPT_TS + " | 〔mv0001 承接确认回执·承 O-20261008-1715/1755-bm-c·≤1h SLA 内·bm-c〕"
    "产线承接+腾资源两件已执行 | "
    "**D-BS-20261008-11 承接确认（bm-c）**：①移交包 23 件已读（HANDOVER.md 正本+六波 R 件清单在案·"
    "建议窗副歌 77-97s 领受·bm-c 科学修正权保留）；②**腾资源两件已执行**=qwen3.6-coder:35b"
    "（13GB·100%GPU·Forever 常驻）15:5x ollama stop 卸载〔ollama ps 空自证·VRAM ~13GB 腾出〕"
    "+gaming draft-queue 图像批暂停=MiniGameComfyDraftTick OS 任务 15:56 禁用〔draft-queue.jsonl "
    "工单行零触碰保全·完工后 enable 恢复并回执注明〕；③GPU 排产=MV 样片优先已就位（ComfyUI SDXL "
    "关键帧通道在位·Wan2.2-5B GGUF Q4 视频段通道按模型下载三闸令自检中）；④20 秒完成片级样片全链"
    "开工（SDXL 关键帧→本地视频段→帧闸→插帧律〔24fps 直用·仅慢动作段 RIFE〕→调色全链〔分频三带实测"
    "校准+halation gblur sigma14+screen+灰基 softlight 颗粒 0.45〕→窗内歌词字幕→2.35:1 遮幅→AIGC "
    "显著标识→乐句切点对轴〔77.0=bar35 实测〕→三律人眼门自检〔高级/去烂俗/去AI感+三病清零〕·"
    "十二项执行清单完工回执逐项打勾）；⑤样片出口=cph4/fleet/mv0001-handover/outbound/"
    "MV0001_爱在西元前_20s样片_v1.mp4（commit+push 传回）·bm-a=查看位只看结果照领受 | "
    "承接确认已落·样片在途 |"
)


def git(args, cwd=GROUP, env=None, inp=None):
    p = subprocess.run(["git", "-C", cwd] + args, capture_output=True,
                       creationflags=CNO, env=env, input=inp)
    return p.returncode, p.stdout, p.stderr


def hex40(s):
    return bool(re.fullmatch(r"[0-9a-f]{40}", (s or "").decode("utf-8", "replace").strip()))


def main():
    rc, _, err = git(["fetch", "origin"])
    if rc != 0:
        print("FETCH_FAIL rc=%d %s" % (rc, err.decode("utf-8", "replace")[:200]))
        return 2
    rc, out, err = git(["rev-parse", "origin/main"])
    if rc != 0 or not hex40(out):
        print("TIP_FAIL rc=%d out=%r err=%r" % (rc, out[:45], err[:100]))
        return 2
    tip = out.decode().strip()

    rc, blob, err = git(["show", tip + ":docs/orders.md"])
    if rc != 0:
        print("BLOB_READ_FAIL rc=%d" % rc)
        return 2
    content = blob.decode("utf-8", "replace")
    if content and not content.endswith("\n"):
        content += "\n"   # r843 tail-terminator splice guard
    content += RECEIPT_LINE + "\n"

    tmp_line = os.path.join(GROUP, ".codely-cli", "_r767bmc_receipt_line.txt")
    with open(tmp_line, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(RECEIPT_LINE + "\n")

    rc, out, err = git(["hash-object", "-w", "--stdin"], inp=content.encode("utf-8"))
    if rc != 0 or not hex40(out):
        print("HASH_FAIL rc=%d out=%r" % (rc, out[:45]))
        return 2
    new_blob = out.decode().strip()

    tmp_idx = os.path.join(GROUP, ".codely-cli", "_r767bmc_tmp_index")
    if os.path.exists(tmp_idx):
        os.remove(tmp_idx)
    env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
    rc, _, err = git(["read-tree", tip + "^{tree}"], env=env)
    if rc != 0:
        print("READ_TREE_FAIL rc=%d" % rc)
        return 2
    rc, _, err = git(["update-index", "--cacheinfo",
                      "100644," + new_blob + ",docs/orders.md"], env=env)
    if rc != 0:
        print("UPDATE_INDEX_FAIL rc=%d %s" % (rc, err.decode("utf-8", "replace")[:200]))
        return 2
    rc, out, err = git(["write-tree"], env=env)
    if rc != 0 or not hex40(out):
        print("WRITE_TREE_FAIL rc=%d out=%r" % (rc, out[:45]))
        return 2
    tree = out.decode().strip()

    msg = ("mv0001 承接确认回执 bm-c：腾资源两件执行（qwen 常驻卸载+DraftTick 禁用）+产线开工 "
           "(承 O-20261008-1715/1755-bm-c·bm-c)")
    rc, out, err = git(["commit-tree", tree, "-p", tip, "-m", msg])
    if rc != 0 or not hex40(out):
        print("COMMIT_TREE_FAIL rc=%d out=%r" % (rc, out[:45]))
        return 2
    commit = out.decode().strip()

    rc, out, err = git(["push", "origin", commit + ":refs/heads/main"])
    push_out = (out + err).decode("utf-8", "replace")
    ok = rc == 0 and not re.search(r"(?i)fatal|rejected|failed|error", push_out)
    if not ok:
        print("PUSH_FAIL rc=%d out=%s" % (rc, push_out[:300]))
        return 3

    rc, _, _ = git(["fetch", "origin"])
    rc2, out2, _ = git(["rev-parse", "origin/main"])
    landed = out2.decode().strip() == commit
    os.remove(tmp_idx)
    print(json_ok(commit, tip, tree, new_blob, landed, push_out))


def json_ok(commit, tip, tree, new_blob, landed, push_out):
    import json
    print(json.dumps({
        "rc": 0 if landed else 4,
        "commit": commit[:10], "parent_tip": tip[:10], "tree": tree[:10],
        "new_blob": new_blob[:10], "landed": landed,
        "receipt_line_bytes": len(RECEIPT_LINE.encode("utf-8")),
        "push_tail": push_out.strip().splitlines()[-1][:120] if push_out.strip() else "",
    }, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
