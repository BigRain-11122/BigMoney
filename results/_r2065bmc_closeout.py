"""r2065 (bm-c) closeout: bump state, write the heartbeat through the merge-only door,
append the round report. Contention window -> only this machine's own faces are touched.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "Tools"))
import heartbeat_write as HW  # noqa: E402

STATE = os.path.join(BASE, "state-bm-c.json")
REPORT = os.path.join(BASE, "round_reports-bm-c.md")

VERDICT = (
    "CONTENTION（rc=3）只落新增文件面：把 r2061 分类里的两条 EXCEPTION 腿做成一行补丁+13/13 证明"
    "（permission_persistence --check 与 cash_roll_today --selftest 同为『上游合法沉默』，"
    "一个读 key 一个读活盘）·补丁未落地待静窗"
)
DID = (
    "r2065: results/_r2065bmc_reader_silent_upstream.py（13/13·含两条负控：未打补丁仍抛两个 KeyError）"
    " + patches/r2065-reader-silent-upstream.patch（4 段/3 文件·git apply --check rc0）"
    " + results/reader_silent_upstream.json + research/READER-SILENT-UPSTREAM.md"
)
CURRENT = ("r2065 两条 EXCEPTION 冒烟腿的根因与修法：上游合法沉默时读者不许崩，selftest 不许读活盘")


def main():
    ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    ts = ts[:-2] + ":" + ts[-2:]

    # --- state round_no -------------------------------------------------------------
    with io.open(STATE, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    before = st.get("round_no")
    st["round_no"] = 2065
    st["note_r2065"] = ("reader-silent-upstream patch proven (13/13); not applied -- contention "
                        "window, new files only")
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    print("state round_no %r -> 2065 (keys=%d)" % (before, len(st)))

    # --- heartbeat through the merge-only writer ------------------------------------
    fields = {
        "last_seen": ts, "clock_read": ts, "ts": ts,
        "heartbeat_epoch_utc": int(time.time()),
        "round": 2065, "round_no": 2065,
        "current_task": CURRENT, "did": DID, "verdict": VERDICT,
        "ram_free_gb": round(__import__("psutil").virtual_memory().available / 1e9, 1),
        "idle_rounds": 0, "agenda_starved": False,
    }
    hb = os.path.join(BASE, "fleet", "machines", "bm-c.json")
    with io.open(hb, encoding="utf-8") as fh:
        n_before = len(json.load(fh))
    v, rc = HW.write(BASE, fields)
    print("heartbeat rc=%s keys %d -> %d gpu_replaced=%s warnings=%s"
          % (rc, n_before, len(json.load(io.open(hb, encoding="utf-8"))),
             len(v.get("gpu_replaced") or []), v.get("warnings") or []))
    if rc != 0:
        print(json.dumps(v, ensure_ascii=False)[:400])
        return 1
    with io.open(hb, encoding="utf-8") as fh:
        h2 = json.load(fh)
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert h2["round_no"] == 2065 and isinstance(h2["round_no"], int)

    # --- distance from origin -------------------------------------------------------
    r = subprocess.run(["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
                       cwd=BASE, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    behind_ahead = (r.stdout or "").strip() or "?"

    line = (
        "%s | r2065 | bm-c | **PRODUCT（产品优先律·watermark 绿（red=false·lane=healthy·next_pick 已被"
        "他机 claimed）·孤儿面=0（py_faces=6 / orphans=0 / resident_servers=2）·竞争窗 rc=3 CONTENTION"
        "〔对端 interactive pid 79608 自 2026-11-24T22:39 起 201min、16 张共享面在轮首前被动过、重叠窗内"
        "不可归因 0 张，证据 results/_repo_write_contention.bm-c.json〕→ 按 r1907/r1927 只落新增文件面："
        "未改共享面、未重跑 S6 链、未跑全量冒烟）**：r2061 分类里那 2 条 EXCEPTION 腿不是两个新缺陷，"
        "是 r2062..r2064 那条链的第三种长相——**上游合法沉默，读者却当成不可能**。①"
        "`etf_book_permission_persistence --check` 直接读 `gap['gap_k']`，而缺口票据今天合法地答 "
        "UNREADABLE（permitted_k=null），于是 `KeyError: 'gap_k'`——检查器拿到的是 traceback，它要的是"
        "一句话；②`etf_book_cash_roll_today --selftest` 更糟：selftest 去读**活盘**权限面并在 "
        "`live['cash_cny']` 上取值，而沉默面上 `build()` 正确地返回 NO_INSTRUCTION（没有 cash 可索引）"
        "→ `KeyError: 'cash_cny'`——**市场替这个文件决定它自己的自检过不过**，今天根本没代码错。"
        "| 补丁 4 段/3 文件（`patches/r2065-reader-silent-upstream.patch`·`git apply --check` rc0）："
        "checker 改成印 `UPSTREAM_SILENT` 并 exit 3（第三态，harness 收 UNVERIFIED 不收红：r1861/r1943；"
        "红一个谁也动不了的腿＝教读者放宽规则 r1789/r1135），且该句**不含 STALE**（链只在那个词上付重建，"
        "r1850）；run() 改为在不可读的 trim 上拒发而非崩；cash_roll_today 的盘上两腿换成**夹具**"
        "（可读面：cash=nav−ordered 到分；沉默面：NO_INSTRUCTION 且无 cash 可索引），活盘对照留给 --check"
        "（它本来就在逐字段做）；harness 加一条 rc==3+UPSTREAM_SILENT → UNVERIFIED 分支。"
        "| 证明 `results/_r2065bmc_reader_silent_upstream.py` **13/13**：补丁确定性两跑逐字节相同、"
        "hunk 计数 4/3、git apply --check 过、三份补丁后源码 ast 通过、harness 分支位置断言、"
        "沉默票据→rc3 且句含 UPSTREAM_SILENT 且不含 STALE、可读票据→**穿过守卫真的走到 rebuild**（守卫不是哑巴）、"
        "打补丁后 selftest 在**read_inputs 被下毒**的情况下仍 0（它真的离线了）；**两条负控**＝未打补丁的源码"
        "在同一批夹具上仍抛 `KeyError 'gap_k'` / `KeyError 'cash_cny'`（绿腿不可能是夹具变了）。"
        "| 未做（如实）：**补丁未落地**（竞争窗只准新增文件面）；未跑全量冒烟（连续第 11 轮，红腿读数仍是 "
        "2026-11-24T20:12:28 那份）；S6 链连续第 11 轮未跑；r2063 那条一行补丁（k 腿锚 base_bar）仍未落。"
        "| S0.5 双扫：fleet/orders 117 件、本机回执 331 条、**未回执 0 件**；集团 origin/main:docs/decisions.md "
        "原生字节 250,586B sha256 79e3083b85c130b8… **== 自持水位**（零新决策零动作）；fleet/inbox 空。"
        "| S7：attrition tripwire **CLEAN**（4 件·三条历史缩行 healed 照录）；审阅 schtasks 本轮未触碰"
        "（对端在飞，重注册会打断在飞轮）。| **本地未达 origin commit 数**：commit 前实测 "
        "origin/main...HEAD = %s（本条 commit 后再 +1）。| 下轮指针：(a) 静窗后先 `git apply` 本补丁再跑"
        "`smoke_test --only` 书族看那两条腿是否变 UNVERIFIED（≤48h）；(b) r2063 的 k 腿一行补丁同窗落地；"
        "(c) 全量冒烟 + S6 收口（≤48h）。| **CEO 三行**：当前活＝把剩下 2 条『异常』红腿查清——不是代码坏，"
        "是上游今天说不出话而读者不会听｜最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\patches\\"
        "r2065-reader-silent-upstream.patch（可一键 git apply·13/13 证据在 results\\reader_silent_upstream.json）"
        "｜下个里程碑＝静窗落地本补丁+书族冒烟复验（≤48h）。| 记账：轮报告 1 处 + state 1 + 心跳 1 = 3。"
        % (ts, behind_ahead)
    )
    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n" + line + "\n")
    print("report appended (%d chars)" % len(line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
