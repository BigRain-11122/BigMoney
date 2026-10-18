# -*- coding: utf-8 -*-
"""r1102 closeout: append the saturation_engine dual-entry pit row to CODELY.md
(single-file fresh-read-modify-write per the r1006 multi-writer law; EOL-native;
10KB hard-line assert per the O-20260927-0230 budget law)."""
import io

p = "CODELY.md"
raw = io.open(p, encoding="utf-8", newline="").read()
crlf = raw.count("\r\n")
lf = raw.count("\n") - crlf
eol = "\r\n" if crlf >= lf else "\n"
assert raw.endswith(eol), "file must end with EOL"
assert "saturation_engine.py dual-entry" not in raw, "idempotent guard: row already present"
row = ("- [2026-10-19 00:5x r1102 bm-c] **saturation_engine.py 双入口路径分歧坑**："
       "scripts/ 副本 STATE_PATH=results/saturation_engine/state_bm-c.json（子目录形态·盘上恒不存在）"
       "→误跑 python scripts/saturation_engine.py status 必报 engine_alive=false "
       "'no state file (engine never ticked)' 假死（r1102 W273 六门前实弹·与冻结件注记 heartbeat 新鲜矛盾·"
       "险致误诊引擎死走 P0 修复歧路）；正身=Tools/saturation_engine.py"
       "（状态件 results/saturation_engine_state.bm-c.json 平铺形态·prereg facts 脚本引用面）。"
       "How to apply：引擎 status 实读一律 Tools/ 入口；scripts/ 副本为历史形态勿作判活依据。")
t2 = raw + row + eol
nb = len(t2.encode("utf-8"))
assert nb <= 10240, "would exceed 10KB hard line: %d" % nb
io.open(p, "w", encoding="utf-8", newline="").write(t2)
print("appended, new bytes:", nb, "eol:", repr(eol))
