# -*- coding: utf-8 -*-
"""r768 bm-c CAS direct-drop receipt: append silence-duo rows (b4eb539 popup
root-cure + 21b45d7 mechanism-silence trio) to group-tree docs/orders.md.
Zero worktree touch: temp-index + commit-tree + push <sha>:main (O-1410 canon,
r767 tool bloodline verbatim mechanics). 40-hex hard-asserted; push verdict
greps fatal/rejected/failed/error; tail-newline guard (r843)."""
import os
import re
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
CNO = 0x08000000
TS = "10-08 ~17:2x"

L1 = ("| " + TS + " | 〔弹窗复发根治批回执·承 b4eb539 U060 第五次再提·bm-c〕守卫部署+quark 回执修法面 | "
      "**bm-c 实弹**：①silence-enforce 三件部署=group canonical byte-identical（matchGroup×3 验证）部署至 "
      "bigmoney Tools/（本地 group 树盘面 STALE 实锚〔disk blob 3e5eadb≠origin 6fa5d8e=11:55 System.Object[] "
      "缺陷版〕禁用→lane 固定 bigmoney 部署副本·正本=group origin·drift 面 fleet 轮同步）+16:53 首跑实弹；"
      "②HQ-SilenceGuard-Lane PT1M 装备活（17:15:45 审计实锚：toast/noc 双闸 0/0·task_violations 0·"
      "remediations 0·guard_cadence=lane-1m-ok·15m 旧车道已自动迁移清除）；③quark 回执修法面=canonical @() "
      "修复 live 验证（本机 11:55 旧版 System.Object[] 缺陷实录〔group patrol JSON 在案〕→现版正确计数）+本机 "
      "quark 任务 4 件态=3 件 Disabled+QuarkUpdaterTaskUser1.0.0.21 Disable 拒绝访问=提权物理域如实披露"
      "（Run key QuarkUpdaterTaskUser 已净·S4U/事件日志同类权限边界·CEO 物理件域）——守卫每分钟重试 Disable "
      "自愈在位·弹窗源主程序零触碰照令；④全件随 bigmoney r768 commit 4670869a5 push 机队可见 | "
      "executed（bm-c 面实弹毕·权限边界如实） |")
L2 = ("| " + TS + " | 〔机制级静默三件套回执·承 21b45d7「从机制上就要静默开发」·bm-c〕唯一正门+60 秒车道领受 | "
      "**bm-c 实弹**：①task-register.ps1 唯一正门落地（部署副本随 r768 commit·本机后续新建/改建任务一律走正门；"
      "既有 register_loop_task/watchdog/claws 注册器=InvisibleRunner 隐藏链构造出生即静默·既合律维持用）；"
      "②冷启动法条领受=AI.md 铁律 7 升格版随组仓 pull 生效·本机轮协议链全程隐藏链构造；③60 秒兜底车道="
      "HQ-SilenceGuard-Lane PT1M 活（读回验证 PT1M 触发器+滚动 NextRun 实锚）·最坏弹窗存活 ≤60s 机制达成；"
      "④机制边界如实=S4U 出生级隐身/TaskScheduler 事件日志拦截均需管理员提权=CEO 物理件域（零提权实锚同 "
      "bm-a 面） | executed（三件套 bm-c 面实弹毕） |")
LINES = [L1, L2]


def git(args, cwd=GROUP, env=None, inp=None):
    p = subprocess.run(["git", "-C", cwd] + args, capture_output=True,
                        creationflags=CNO, env=env, input=inp)
    return p.returncode, p.stdout, p.stderr


def hex40(s):
    return bool(re.fullmatch(r"[0-9a-f]{40}", (s or b"").decode("utf-8", "replace").strip()))


def main():
    rc, _, err = git(["fetch", "origin"])
    if rc != 0:
        print("FETCH_FAIL rc=%d" % rc); return 2
    rc, out, err = git(["rev-parse", "origin/main"])
    if rc != 0 or not hex40(out):
        print("TIP_FAIL rc=%d out=%r" % (rc, out[:45], err[:100])); return 2
    tip = out.decode().strip()

    rc, blob, err = git(["show", tip + ":docs/orders.md"])
    if rc != 0:
        print("BLOB_READ_FAIL rc=%d" % rc); return 2
    content = blob.decode("utf-8", "replace")
    if content and not content.endswith("\n"):
        content += "\n"   # r843 tail-terminator splice guard
    for line in LINES:
        content += line + "\n"

    tmp_line = os.path.join(GROUP, ".codely-cli", "_r768bmc_receipt_lines.txt")
    with open(tmp_line, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(LINES) + "\n")

    rc, out, err = git(["hash-object", "-w", "--stdin"], inp=content.encode("utf-8"))
    if rc != 0 or not hex40(out):
        print("HASH_FAIL rc=%d out=%r" % (rc, out[:45], err[:100])); return 2
    new_blob = out.decode().strip()

    tmp_idx = os.path.join(GROUP, ".codely-cli", "_r768bmc_tmp_index")
    if os.path.exists(tmp_idx):
        os.remove(tmp_idx)
    env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
    rc, _, err = git(["read-tree", tip + "^{tree}"], env=env)
    if rc != 0:
        print("READ_TREE_FAIL rc=%d" % rc); return 2
    rc, _, err = git(["update-index", "--cacheinfo",
                      "100644," + new_blob + ",docs/orders.md"], env=env)
    if rc != 0:
        print("UPDATE_INDEX_FAIL rc=%d %s" % (rc, err.decode("utf-8", "replace")[:200])); return 2
    rc, out, err = git(["write-tree"], env=env)
    if rc != 0 or not hex40(out):
        print("WRITE_TREE_FAIL rc=%d out=%r" % (rc, out[:45], err[:100])); return 2
    tree = out.decode().strip()

    msg = ("bm-c silence-duo receipts: popup root-cure (guard deployed + lane PT1M live + "
           "quark 1.0.0.21 Access-Denied physical domain honest) + mechanism-silence trio "
           "(task-register sole door + 60s lane) (承 b4eb539/21b45d7·bm-c r768)")
    rc, out, err = git(["commit-tree", tree, "-p", tip, "-m", msg])
    if rc != 0 or not hex40(out):
        print("COMMIT_TREE_FAIL rc=%d out=%r" % (rc, out[:45], err[:100])); return 2
    commit = out.decode().strip()

    rc, out, err = git(["push", "origin", commit + ":refs/heads/main"])
    push_out = (out + err).decode("utf-8", "replace")
    ok = rc == 0 and not re.search(r"(?i)fatal|rejected|failed|error", push_out)
    if not ok:
        print("PUSH_FAIL rc=%d out=%s" % (rc, push_out[:300])); return 3

    git(["fetch", "origin"])
    rc2, out2, _ = git(["rev-parse", "origin/main"])
    landed = out2.decode().strip() == commit
    os.remove(tmp_idx)
    import json
    print(json.dumps({
        "rc": 0 if landed else 4, "commit": commit[:10], "parent_tip": tip[:10],
        "tree": tree[:10], "new_blob": new_blob[:10], "landed": landed,
        "rows": len(LINES), "receipt_bytes": sum(len(l.encode("utf-8")) for l in LINES),
        "push_tail": push_out.strip().splitlines()[-1][:120] if push_out.strip() else "",
    }, ensure_ascii=False))
    return 0 if landed else 4


if __name__ == "__main__":
    sys.exit(main())
