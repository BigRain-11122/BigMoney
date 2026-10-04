"""r494 bm-c S7-close supplementary: round-report close row (marker gate
count==1) + state did/verify final patch (push-race 3-wave closure) +
daemon lane satengine absorb. Programmatic writes + reparse self-proof.
Laws: r679 marker gate / r694 absolute values / r645 reparse / r489
close-row precedent."""
import datetime
import json
import os
import re
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-c.json")
RR = os.path.join(REPO, "round_reports-bm-c.md")

CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")
MARKER = "｜r494 bm-c S7-close｜"

NOW = datetime.datetime.now().astimezone()
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

CLOSE_ROW = (
    CLOCK + "｜r494 bm-c S7-close｜本地未达 origin commit 数=0（DELIVERED：round commit 6be85160f→首推被拒〔origin 窗内进 4：bm-b r691 N2 gate-fix closeout+bm-a absorb 8503b6ccc+bm-b merge+bm-a r695 generate claim 20:09:42〕→merge 96f92f898 2-UU resolve〔trio 双探针面 per-face ts newer-wins 双 ours：trio_watch deep owner_since 20:02:14 vs 19:46:14+trio_eta generated 20:08:04 vs 19:54:48·receipt _r494bmc_merge_resolve.json·深嵌 ts 扫腿本窗新面〕→push#2 被拒〔bm-b keepalive quad-lane claim-refresh 20:14:19 含 n2-w15-generate owner=bm-b〕→merge wave-2 净〔零 UU·池面 theirs 正典〕→push#3 push_verify DELIVERED tip 750a91ece ahead=0/behind=0·零强推零 --no-verify）｜收口实录：round commit 39 文件（簿记四写+探针族 5 件+S6 log+daemon lane absorb+S6 再生面族+双 MSG 移 processed 100% rename）+close commit（本行+state 终版+satengine daemon 双面 absorb）｜N2 generate 席位观察=池面 claim 摆动中（bm-a 20:09:42 launch-claim vs bm-b 20:14:19 keepalive claim-refresh·双 daemon 轨道=他机 MSG 裁决面·bm-c 零触碰 r474 律）｜在册面行删除类=0（纯 append 轮·无清扫无 quarantine·登记册零命中断言=不适用〔无清扫动作〕）｜轮产品计分：1（S6 38 面再生+看护证据面=实际文件改动·等待态轮如实计）"
)


def main():
    # round report close row (marker gate)
    with open(RR, "rb") as f:
        raw = f.read()
    assert raw.count(MARKER.encode("utf-8")) == 0, "close marker present (r679)"
    eol = b"\r\n" if (raw[-2:] == b"\r\n" or raw.count(b"\r\n") > raw.count(b"\n") // 2) else b"\n"
    if not raw.endswith(eol):
        raw = raw + eol
    with open(RR, "wb") as f:
        f.write(raw + CLOSE_ROW.encode("utf-8") + eol)
    with open(RR, "rb") as f:
        raw2 = f.read()
    assert raw2.count(MARKER.encode("utf-8")) == 1, "close marker != 1 (r679)"
    print("RR_CLOSE_ROW_OK")

    # state final patch
    st = json.load(open(STATE, encoding="utf-8"))
    assert st["round_no"] == 494
    st["did"] = (st["did"] +
                 "; (7) push-race 3-wave window closed: round commit 6be85160f push#1 rejected "
                 "(bm-b r691 + bm-a r695 wave) -> merge 96f92f898 2-UU trio-probe resolve (per-face ts "
                 "newer-wins both ours, receipt _r494bmc_merge_resolve.json) -> push#2 rejected (bm-b "
                 "keepalive quad-lane 20:14:19) -> merge wave-2 clean (zero UU) -> push#3 push_verify "
                 "DELIVERED tip 750a91ece ahead=0/behind=0.")
    st["verify"] = (st["verify"] +
                    "; r494 final: push-race 3-wave closure DELIVERED tip 750a91ece (receipts "
                    "_r494bmc_merge_resolve.json + push_verify json) + close row appended (marker==1)")
    st["last_round_at"] = CLOCK
    st["last_round_ts"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
    st["updated"] = CLOCK
    st["updated_at"] = CLOCK
    st["clock_read"] = CLOCK
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    json.loads(open(STATE, encoding="utf-8").read())
    assert CLOCK_RE.match(CLOCK)
    print("STATE_FINAL_OK clock=", CLOCK)
    print("S7_SUPP_DONE")


if __name__ == "__main__":
    main()
