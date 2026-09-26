# r231 memory append (python direct UTF-8 write per r230 GBK law; PS string
# relay is banned for CODELY.md appends).
import io

PATH = "CODELY.md"
raw = open(PATH, "rb").read()
crlf = b"\r\n" in raw[-2000:]
ends_nl = raw.endswith(b"\n")
line = (
    "- [2026-09-26 08:0x] 坑律（bm-b r231·P1E_SYNTH 收割·finalize prev 读点"
    "链分叉族·P0/E1 实测复证+死轮残骸收养）：**finalize 的 prev_total 必须读 "
    "r112 canonical 递归 ledger_head()——窄面 _chain_head_total（top-level+"
    "shortline/ 一层不递归）漏嵌套批目录 results/wild_route/ 产出同 prev 链分叉"
    "（窄面 183292 vs 真头 184754 双读数实测）**；修=caller 侧换 "
    'ledger_head()["total"]（helper 窄面语义保留不动），scripts 全扫净：'
    "p1e_synth（死轮 07:31 残骸收养+fork 实测复证后随 finalize 落地）+"
    "a158_truegap_ic+p1e_ic_batch 同轮补齐、t24_g2_pack 已 canonical 免修；"
    "**修必须先于 finalize 落地（分叉块入链即永久）**；selftest 加 inspect "
    "源断言防回退；连带 r225 死轮判别三件套再证（关键件 mtime 停摆+零存活进程+"
    "零 commit=死非活、残骸直接收养勿重做）。指针=scripts/p1e_synth.py "
    "finalize+r231b/c/d resolver 族+research/shortline/P1E_SYNTH.md §7+"
    "P1E_SYNTH 判定 FAIL 收线（V1 0.0700<0.0762·rank 5/21·账本 184754→184826）。"
)
sep = "\r\n" if crlf else "\n"
with io.open(PATH, "a", encoding="utf-8", newline="") as fh:
    if not ends_nl:
        fh.write(sep)
    fh.write(line + sep)
print("appended; crlf=", crlf, "ends_nl=", ends_nl,
      "size_kb=", (len(raw) + len(line.encode('utf-8'))) // 1024)
