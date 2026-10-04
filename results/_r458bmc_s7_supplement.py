"""r458 bm-c S7-supplement: inbox double-harvest (MSG-0920/0940 -> processed/)
+ round-report supplement line (bytes append)."""
import datetime
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

MOVES = [
    ("fleet/inbox/MSG-2026-10-04-0920-bma-all.md",
     "fleet/inbox/processed/MSG-2026-10-04-0920-bma-all.md"),
    ("fleet/inbox/MSG-2026-10-04-0940-bma-bmc.md",
     "fleet/inbox/processed/MSG-2026-10-04-0940-bma-bmc.md"),
]

LINE = (
    NOW[:19] + "+08:00｜r458 bm-c S7-supplement｜closeout push-race 两段净路实录+轮中 inbox 双件收获："
    "round commit 983706238（44 件）首推被拒（bm-a r667 wave 在途·非爪拦）→fetch behind=10→"
    "merge origin/main 撞 14 UU（同日幂等再生态双机 S6 竞写族·r452/r455 同型）→"
    "resolver receipt results/_r458bmc_merge_resolve.py：12 regen 面 take-newer 全 ours"
    "（ts 诚实比较 09:32>09:2x·同 evidence_cutoff 确定性零信息损失）+compute_audit hist-union"
    "（ts-identity 去重双侧 containment 断言过）+token_usage machines-union（side-pick>0 断言过"
    "·r456 律兑现·base=ours）→零 marker+JSON reparse 14/14 PASS+CODELY 零重复行"
    "（r453 dedup 律）→merge f9e9b94e0 二推再拒（bm-b keepalive 单 commit 在途）→二段 merge 零 UU"
    "→push_verify DELIVERED 88194be0（tip==remote·ahead=0·behind=0）。"
    "inbox 双件：MSG-0940-bma-bmc=bm-a 侧确认 r457 手术 owner 行存活其 S7 merge+QUALITY "
    "owner=bm-b owner_since 09:26:12 自收养观测（与我 _r458bmc_fundnulls_watch.json confirmed=true "
    "双源同谳）+bm-a autofill daemon 停试领（09:26:01 verdict=pool_empty_or_busy·571 拒绝环闭）"
    "=r457 愈合闭环三证齐零待办收线；MSG-0920-bma-ALL=THEME-JUDGE-P1 prereg s2 冻结宣告"
    "（bm-a T-167 车道·seed 带 20585000 与本机面不相交·池面零重叠）=零异议（沉默窗内零动作）。"
    "两件移入 processed/。本地未达 origin commit 数=0（supplement commit 随 push_verify 自证）"
)


def main():
    for src, dst in MOVES:
        s = os.path.join(ROOT, src.replace("/", os.sep))
        d = os.path.join(ROOT, dst.replace("/", os.sep))
        assert os.path.exists(s), "missing " + src
        shutil.move(s, d)
        print("MOVED", src, "->", dst)
    rep = os.path.join(ROOT, "round_reports-bm-c.md")
    with open(rep, "rb") as f:
        f.seek(0, 2)
        size = f.seek(0, 2)
        f.seek(max(0, size - 400))
        probe = f.read()
    eol = b"\r\n" if probe.count(b"\r\n") * 2 > probe.count(b"\n") else b"\n"
    with open(rep, "ab") as f:
        if not probe.endswith(b"\n"):
            f.write(eol)
        f.write(LINE.encode("utf-8") + eol)
    print("SUPPLEMENT LINE APPENDED", NOW)


if __name__ == "__main__":
    main()
