"""r465 bm-c final absorb: S7-close supplement line (round report) + merge-resolver
evidence files + treadmilled satengine lane faces, then push_verify. If raced:
push_verify reports NOT-DELIVERED, next cycle is next round's S0 netpath."""
import os
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "round_reports-bm-c.md")

SUPPLEMENT = (
    "｜r465 bm-c S7-close｜本地未达 origin commit 数=0（push_verify DELIVERED·tip d103d9dda"
    "==remote·ahead=0/behind=0·终 absorb commit 随本 push_verify 自证）｜收口实录：round commit "
    "2b2dfd376（53 面）→merge origin/main 撞 17 UU（同日幂等再生态竞写族·bm-b r667 收口波+"
    "bm-a r673 wave·r452/r455/r462 同型）→canon 解 17 面（resolver=results/_r465bmc_merge_"
    "resolve.py·证据 _r465bmc_merge_resolve.json：14 regen 双胞胎 take-ours〔ts 诚实比较 "
    "11:31-11:34 vs 11:25-11:27〕+compute_audit hist-union 203=201+theirs-only 2〔双侧 "
    "containment 断言过〕+token_usage machines per-key max-union〔side_pick=2>0 r456 律兑现〕"
    "+crash_fuse per-key max-merge〔64sigs/47cleared·键集 union 零丢失断言〕）→merge commit "
    "d103d9dda→push_verify DELIVERED 零爪拦零 --no-verify 零强推｜本机 pool_worker 事件照录："
    "THEME-JUDGE-P1 claim 11:32:09→close outcome=fail 11:32:18（O-2210 claim-by-file 自查池面"
    "自主线·fuse 拒绝面 refusals 7@11:30:04=r617 熔丝族健康拦截·修复面归 T-167 bm-a 属主·"
    "bm-b autofill 侧同窗 claim 9d5307fdf 亦在案=池协议自治理零待办）｜零清扫/归档/删除/恢复类"
    "动作轮：登记册零命中断言照实（treasure_guard 零调用面·五收口步零触发→TREASURE_REGISTRY/"
    "METHODOLOGY_ASSETS 零新行照实）｜轮产品计分：5x HANDOVER 条目+S6 管线产出+watch 证据件+"
    "S0 净路证据+resolver 证据件=可跑/能看实物面（等待态声明：finalize 窗 10-05 10:30 开·板空·"
    "N1 关·池全 bm-b 属主=零新面孔可烧·非空转）")

PATHS = [
    "round_reports-bm-c.md",
    "results/_r465bmc_merge_resolve.py",
    "results/_r465bmc_merge_resolve.json",
    "results/_r465bmc_uu_faces.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/_r465bmc_final_absorb.py",
]
MSG = ("absorb r465 bm-c: S7-close receipt (DELIVERED d103d9dda ahead=0/behind=0) + "
       "merge-resolver evidence files + satengine lane faces (treadmill) -- round 465 close")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def main():
    import datetime
    line = datetime.datetime.now().isoformat(timespec="seconds") + SUPPLEMENT
    with open(RR, "ab") as f:
        f.write(("\n" + line).encode("utf-8"))
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
