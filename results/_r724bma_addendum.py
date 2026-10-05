"""r724 bm-a ledger addendum line with MEASURED push values (r532/r533 law:
tail line consumes only measured values, never pre-written)."""
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

line = (
    f"{ts} | r724 (bm-a) addendum | 收口窗三跳 merge 实录（r524 两跳正典+第三窗干净收口）: "
    "首推被拒=behind 5（bm-c r538 S6 波 12:2x 同窗再生成族+churn face）-> merge 窗1: 14-UU 正典 resolver "
    "（r538 bm-c 血统 verbatim-adapted·stage :2:/:3: 源 r515 律·readback 断言 r704 律·twin-lock r708/r510）= "
    "10 take-ours 全 OURS-NEW ts 探针定向（我 12:35-38 再生 > bm-c 12:28-29）+compute_audit/regime_state "
    "rolling union 零丢失+token per-key max-union（picked_theirs=0）+3 md 孪生随 json 同侧 -> 二次 fetch "
    "复核又 behind 3（bm-c r539 S6 波 12:39-40 更新面）-> merge 窗2: 同 14 面=10 take-theirs 全 THEIRS-NEW "
    "（ts 律双向诚实：他们更新=他们赢）+双 union 二跑零丢失 -> 窗2 commit 消息首版误复用窗1 文案=push 前 amend "
    "修正（未推送=合法·r532 律防预写假值同源）-> 三次 fetch 复核再 behind 1（bm-c r539 close scaffolding）-> "
    "merge 窗3 干净零 UU（1 file 新增）-> PUSH DELIVERED b226404b4..fdc32e0e2 -> fetch 后 ahead=0/behind=0 "
    "双向+六件 ls-tree origin 在位（round_reports/state/s6_log/s6_chain/merge_resolve receipt/heartbeat）"
    "| receipt=两窗 union results/_r724bma_merge_resolve.json（r516-3 律：多窗 receipt 必 union 禁覆写·"
    "窗1 独立件 _r724bma_merge_resolve_w1.json 留档）| 本地未达 origin commit 数=0（实测：fetch 后 rev-list "
    "双向 0/0+ls-tree 6/6）| 登记册零命中断言: 本窗零清扫/归档/删除/恢复类动作（treasure_guard 未触发）| "
    "坑例捕获: 无新坑（三窗 merge 全走既有正典血统；resolver 血统复用=反重复铁律执法·零重写）| "
    "下轮指针: r725=5x HANDOVER 块+W16 烧链观察+10-08 复市窗执行面 [via bm-a]"
)

path = os.path.join(ROOT, "round_reports-bm-a.md")
with open(path, "a", encoding="utf-8") as f:
    f.write("\n" + line + "\n")
print("addendum appended,", len(line), "chars |", ts)
