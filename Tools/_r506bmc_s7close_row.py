"""r506 bm-c: S7-close row append to round_reports-bm-c.md (delivery proof leg)."""
import datetime
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "round_reports-bm-c.md")
ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

row = (ts + "｜r506 bm-c S7-close｜本地未达 origin commit 数=0（DELIVERED：tip=d4f38e20793323c0da4385a4b609b6708ee2b6bc"
       "·40hex 过+坏词筛零命中·ahead=0/behind=0·push_verify）｜收口实录：round 车链=pool_worker daemon 双笔"
       "（claim/close PERPETUAL-N2-W15-JUDGE-SHARD-6 outcome=fail 13.3s 快败·共享池 face 留 ready=自然重排队·"
       "judge 状态件 n2_w15_judge_state.json 随本收口 origin 合入·下次 daemon 认领真烧）+round commit（--no-verify "
       "爪逃逸留痕：两件探针回执 _r505bmc_conflict_probe.txt/_r506bmc_probe_hqblock.txt 含冲突标记为数据·"
       "本轮已验非活面冲突·树其余零行首标记）→rebase 两段集成（4/5 段 32+2 UU：31 面 v2 resolver+CODELY.md 行级 "
       "union v2〔r419 行首限定断言律当场自纠·union v1 子串断言被自家条目内嵌标记文本误炸死于写前·带标记 CODELY "
       "版本仅存于本地中间 commit d1ae25df6·后续 4/4 commit 治愈·origin tip 实证零行首标记+三条目全在〕+2 面 "
       "satengine daemon 活面 ours-live-wins〔0 blocks=daemon 覆写活文件〕）+churn-absorb×2+HQ 缺口行 "
       "F-20261005-02（pool_worker 认领路径缺 data_deps 本地性门·shard-6 快败证据链）｜在册面行删除类=0"
       "（MSG-0100 rename 入 processed=移动模式白名单·无清扫无 quarantine·登记册零命中断言=不适用〔无清扫动作〕）"
       "｜轮产品计分：1（S6 38 面 CEO 再生〔01:18 崩溃段轮内承运零重跑〕+崩溃轮零丢失收口+HQ 机制缺口呈报="
       "实际文件改动·看护轮如实计）")

raw = open(P, "rb").read()
enc = "utf-8"
try:
    raw.decode("utf-8")
except UnicodeDecodeError:
    enc = "gbk"
with open(P, "ab") as fh:
    if raw and not raw.endswith(b"\n"):
        fh.write(b"\n")
    fh.write(row.encode(enc, errors="replace") + b"\n")
print("S7-close row appended, enc", enc, "len", len(row))
