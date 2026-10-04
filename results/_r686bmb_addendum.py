"""r686 bm-b round-report addendum append (bytes mode, EOL-preserving):
closeout three-wave race record + delivery self-proof per O-1108 law."""
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clock = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
raw = open(rp, "rb").read()
last_nl = raw.rfind(b"\n")
eol = b"\r\n" if raw[:last_nl].endswith(b"\r") else b"\n"
marker = f"{clock} | round 686 addendum"
assert raw.count(marker.encode("utf-8")) == 0
line = (
    f"{clock} | round 686 addendum (bm-b) | S7 收口三波竞速实录（r681/r690 同型·O-1108 如实登记）: "
    f"closeout 首推被 non-FF 拒（origin 前进=bm-a autofill tick claim contest-ytd-rc-0of1 owner=bm-a）→"
    f"merge #1 单 UU results/crash_fuse.json 双区按属主语义取 theirs（bm-a 18:40:04 code_changed 清闸=新正主+更新时点·"
    f"保留我侧陈旧 sig 块将反向阻塞其 claim=错向·r626d-② 属主判读先查 pin note）→"
    f"复推被 pre-push 爪正确拦（删除集 6 件 _r489bmc_*=陈旧基座假阳性面 r370/r392 族·正解=先集成勿走逃生口）→"
    f"fetch 见 bm-c r489 收口波再进 2 笔→merge #2 14 UU 全 S6 共享再生面正典解 "
    f"（ts 归一 newer-wins：REPORT/LIVE/fundamental/futures/lhb/regime/update_status 取 ours=18:40:45 族 vs theirs 18:40:30 族真 newer·"
    f"attrition scan theirs 18:41:29 真 newer·compute_audit 双侧无顶层 ts=origin 缺省=r681 正典同款·"
    f"token_usage per-key union 5 键保全 picks ours=5/theirs=0·双侧原字节 git show 直取 r657-②·"
    f"resolver results/_r686bmb_merge_resolve.py+回执 _r686bmb_merge_resolve.json·md 孪生同侧 r681）→"
    f"三推送达 DELIVERED 7d1e83663（fe0ae782b..7d1e83663·爪过零删除集·fetch+rev-list 0/0 自证）"
    f"｜本地未达 origin commit 数=0（收口全量 push 后 fetch+rev-list 0/0+tip==origin 自证回填）"
)
open(rp, "wb").write(raw + line.encode("utf-8") + eol)
after = open(rp, "rb").read()
assert after.count(marker.encode("utf-8")) == 1
print("ADDENDUM_APPENDED", clock, "eol=", eol)
