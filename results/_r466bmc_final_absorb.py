"""r466 bm-c final absorb: S7-close supplement line (round report) + CODELY pit
line (law-landed-mid-lineage gap, one line per four-question gate) + resolver
evidence files + treadmilled satengine lane faces, then push_verify.
Copy of r465 final_absorb form, round-numbered per r461 law."""
import datetime
import os
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "round_reports-bm-c.md")
CODELY = os.path.join(ROOT, "CODELY.md")

SUPPLEMENT = (
    "｜r466 bm-c S7-close｜本地未达 origin commit 数=0（push_verify DELIVERED·tip 351723b2d=="
    "remote·ahead=0/behind=0·终 absorb commit 随本 push_verify 自证）｜收口实录：round commit 42 "
    "面→behind=3→merge origin/main 撞 14 UU（同日幂等再生态竞写族·bm-a r675 wave·r452/r455/"
    "r462/r465 同型）→canon 解 14 面（resolver=results/_r466bmc_merge_resolve.py·证据 "
    "_r466bmc_merge_resolve.json：12 regen 双胞胎 ts 诚实比较 take-ours〔11:47-11:48 vs 11:45-"
    "11:47〕+compute_audit hist-union 202=201+theirs-only 1〔双侧 containment 断言过〕+"
    "token_usage r456 断言实弹〔machines 双侧逐键恒等〔fixed-context delta=0 族〕→side_pick=0"
    "→fail-closed 炸·12 面已写零 add 零部分提交·如设计〕→律定回退腿补齐〔整面新鲜度 ours "
    "11:47:59>theirs 11:47:19 取 ours·r456 显式回退非静默默认〕）→merge commit 351723b2d→"
    "push_verify DELIVERED 零爪拦零 --no-verify 零强推｜更正主行「S4 零新坑律行/CODELY 零行」→"
    "实际 +1 行（resolver 事件发生在 s7close 落笔之后·收口窗内如实更正·记账预算实为 4/5）｜"
    "S4 坑律行：律后于脚本血统落册未回流（resolver 复制链 r462→r465 缺 r456 律定回退腿·r466 "
    "副本已补·三机各系 resolver 血统同窗大概率仍带裸 assert·各机下次复制按 r466 形补）｜零清扫"
    "/归档/删除/恢复类动作轮：登记册零命中断言照实（treasure_guard 零调用面·五收口步零触发→"
    "TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜轮产品计分：S6 管线产出+watch 证据件+"
    "S0 净路证据+resolver 证据件=可跑/能看实物面（等待态声明：finalize 窗 10-05 10:30 开·板空·"
    "N1 关·池全 bm-b 属主=零新面孔可烧·非空转）")

CODELY_LINE = (
    "- [2026-10-04 11:5x r466 bm-c] 律后于脚本血统落册未回流坑（token_usage UU 面 r456 断言实弹·"
    "fail-closed 零部分提交零伤）：r456 律（per-key union 零命中必显式转整面新鲜度键判·禁静默整面"
    "走侧）09:02 落册，而 merge-resolver 脚本复制链（r462→r465 血统）仍只带裸 assert——r466 实弹"
    "撞上（token_usage machines 双侧逐键恒等〔per-round fixed-context 值 delta=0 族·差异仅在顶层 "
    "ts〕→side_pick=0→断言炸·前 12 面已写工作树但零 add 零 commit=fail-closed 如设计）。修="
    "resolver 副本补 r456 律定回退腿（side_pick=0→整面 ts 新鲜度判·本例 ours 11:47:59>theirs "
    "11:47:19 取 ours·results/_r466bmc_merge_resolve.py resolve_token 已内建）。教训=复制链脚本"
    "不自动继承落册在后的律——复制 canon 脚本前必扫「该域在脚本血统起点之后落册的律」核脚本是否"
    "已含律定分支；三机 resolver 血统（bm-a/bm-b 各系）大概率同带裸 assert，撞 token/machines 恒等"
    "面会同炸——各机下次 resolver 复制时按 r466 形补回退腿。"
)

PATHS = [
    "round_reports-bm-c.md",
    "CODELY.md",
    "results/_r466bmc_merge_resolve.py",
    "results/_r466bmc_merge_resolve.json",
    "results/_r466bmc_uu_faces.json",
    "results/_r466bmc_final_absorb.py",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]
MSG = ("absorb r466 bm-c: S7-close receipt (DELIVERED 351723b2d ahead=0/behind=0) + resolver "
       "evidence + CODELY law-drift pit line + satengine lane faces (treadmill) -- round 466 close")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def main():
    import datetime
    line = datetime.datetime.now().isoformat(timespec="seconds") + SUPPLEMENT
    with open(RR, "ab") as f:
        f.write(("\n" + line).encode("utf-8"))
    # CODELY.md: file ends with LF; entries separated by one blank line
    with open(CODELY, "ab") as f:
        f.write(("\n" + CODELY_LINE + "\n").encode("utf-8"))
    # self-verify: appended line present exactly once, parse-safe tail
    with open(CODELY, "rb") as f:
        raw = f.read()
    assert raw.count(CODELY_LINE.encode("utf-8")) == 1, "codely line not unique"
    assert raw.endswith("\n".encode("utf-8")), "codely tail LF fail"
    rc, out, err = git("add", "--", *PATHS)
    assert rc == 0, "add fail " + err[:200]
    rc, out, err = git("commit", "-m", MSG)
    print("COMMIT_RC", rc, (out + err).strip()[:200])
    if rc != 0:
        sys.exit(1)
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                         capture_output=True, creationflags=C, cwd=ROOT)
    txt = (pr.stdout or b"").decode("utf-8", "replace") + " || " + \
        (pr.stderr or b"").decode("utf-8", "replace")
    print("PUSH_VERIFY_RC", pr.returncode)
    print(txt.strip()[-300:])
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
