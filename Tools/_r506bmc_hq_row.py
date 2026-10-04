"""r506 bm-c: HQ-FEEDBACK mechanism-gap row append (pool_worker claim path
lacks data_deps locality gate -- shard-6 fast-fail evidence). Encoding-aware
binary append per r485 EOL law (same pattern as close script)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "HQ-FEEDBACK.md")

row = ("- F-20261005-02 [bm-c r506 2026-10-05 01:4x·池机制缺口呈报·JUDGE-SHARD-6 快败实证] "
       "**pool_worker 认领路径缺数据本地性门（D-20261004-02① autofill 侧 data_deps 门未覆盖 pool_worker 面）**"
       "--本机 pool_worker 于 origin 池面 fetch 实核后认领 PERPETUAL-N2-W15-JUDGE-SHARD-6（01:32:17 claim·lane commit）"
       "→runner 13.3s rc=2 快败：judge 状态件 results/n2_w15/n2_w15_judge_state.json（bm-a r705 judge-prep 产物）"
       "在未合入的 origin 波内、本地树缺席=runner 依赖面不全即开烧。证据="
       "results/pool_claims/PERPETUAL-N2-W15-JUDGE-SHARD-6/n2w15judge-6of12.bm-c.json（outcome=fail·exit_code=2·13.3s）"
       "+results/pool_worker_ledger.jsonl 尾行+bm-b r670 data_deps 门实现（Tools/autofill.py _data_deps_missing L1307"
       "+认领前接线 L1826）=同律仅 autofill 面。建议方向：①pool_worker.py 认领前接同律 data_deps 本地在场断言"
       "（复用 autofill._data_deps_missing）；②或池条目 enroll 侧（r497 pattern）强制 data_deps 字段声明；"
       "③过渡律：认领机先核本地树与 origin 同步（behind=0）才领池条目。状态=open\n")

raw = open(P, "rb").read()
enc = "utf-8"
try:
    raw.decode("utf-8")
except UnicodeDecodeError:
    enc = "gbk"
with open(P, "ab") as fh:
    if raw and not raw.endswith(b"\n"):
        fh.write(b"\n")
    fh.write(row.encode(enc, errors="replace"))
print("HQ row appended, enc", enc, "len", len(row))
